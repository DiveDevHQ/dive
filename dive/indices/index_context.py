from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from typing import Optional, Any, Dict
from dive.constants import DEFAULT_CHUNKING_TYPE, DEFAULT_COLLECTION_NAME
from dive.util.text_splitter import SentenceSplitter
from dataclasses import dataclass
from langchain.schema import Document
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
import chromadb
import tiktoken


@dataclass
class IndexContext:
    service_context: ServiceContext
    storage_context: StorageContext
    documents: [Document]
    ids: [str]

    @classmethod
    def from_defaults(
            cls,
            service_context: Optional[ServiceContext] = None,
            storage_context: Optional[StorageContext] = None
    ):

        if not service_context:
            service_context = ServiceContext.from_defaults()

        if not storage_context:
            storage_context = StorageContext.from_defaults(embedding_function=service_context.embeddings)

        if not service_context:
            service_context = ServiceContext.from_defaults()

        return cls(
            documents=[],
            ids=[],
            service_context=service_context,
            storage_context=storage_context)

    @classmethod
    def from_documents(
            cls,
            documents: [Document],
            ids: [str],
            service_context: Optional[ServiceContext] = None,
            storage_context: Optional[StorageContext] = None,
            persist_dir: Optional[str] = None,
            **kwargs: Any,
    ):

        if not service_context:
            service_context = ServiceContext.from_defaults()

        return cls.upsert(
            documents=documents,
            ids=ids,
            service_context=service_context,
            storage_context=storage_context,
            persist_dir=persist_dir,
            **kwargs)

    @classmethod
    def upsert(cls, documents: [Document],
               ids: [str],
               service_context: ServiceContext,
               storage_context: Optional[StorageContext] = None,
               persist_dir: Optional[str] = None,
               **kwargs: Any):
        _documents = []
        _ids = []
        if not service_context.embed_config.chunking_type or service_context.embed_config.chunking_type == DEFAULT_CHUNKING_TYPE:
            _documents = documents
            _ids = ids
        else:
            _tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})
            sentence_splitter_default = SentenceSplitter(chunk_size=service_context.embed_config.chunk_size,
                                                         chunk_overlap=service_context.embed_config.chunk_overlap,
                                                         tokenizer=service_context.embed_config.tokenizer or _tokenizer)

            _documents = []
            _ids = []
            for i, document in enumerate(documents):
                sentence_chunks = sentence_splitter_default.split_text(document.page_content)
                for j, d in enumerate(sentence_chunks):
                    _document = Document(metadata=document.metadata,
                                         page_content=d)
                    _documents.append(_document)
                    _ids.append(ids[i] + "_chunk_" + str(j))

        if storage_context is None:
            client_settings = chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir or "db"
            )
            client = chromadb.Client(
                client_settings
            )
            client.get_or_create_collection(DEFAULT_COLLECTION_NAME)
            db = Chroma.from_documents(client=client, client_settings=client_settings,
                                       collection_name=DEFAULT_COLLECTION_NAME,
                                       documents=_documents, ids=_ids,
                                       persist_directory=persist_dir or "db",
                                       embedding=service_context.embeddings)
            db.persist()
        else:
            storage_context.vector_store.from_documents(documents=_documents, ids=_ids,
                                                        embedding=service_context.embeddings)

        return cls(storage_context=storage_context,
                   service_context=service_context,
                   documents=documents,
                   ids=ids,
                   **kwargs, )



    def delete_from(self, where: Dict):

        result = self.storage_context.vector_store.get(where=where)

        if len(result['ids']) > 0:
            try:
                self.storage_context.vector_store.delete(ids=result['ids'])
            except KeyError:
                return

