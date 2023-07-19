from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from typing import Optional, Any, Dict
from dive.constants import DEFAULT_CHUNKING_TYPE
from dive.util.text_splitter import SentenceSplitter
from dataclasses import dataclass
from langchain.schema import Document
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.embeddings.base import Embeddings
import tiktoken


@dataclass
class IndexContext:
    service_context: ServiceContext
    storage_context: StorageContext
    documents: [Document]
    embeddings: Optional[Embeddings]
    ids: [str]

    @classmethod
    def from_documents(
            cls,
            documents: [Document],
            ids: [str],
            embeddings: Optional[Embeddings] = None,
            storage_context: Optional[StorageContext] = None,
            service_context: Optional[ServiceContext] = None,
            **kwargs: Any,
    ):

        if not storage_context:
            storage_context = StorageContext.from_defaults()
        if not service_context:
            service_context = ServiceContext.from_defaults()
        if not embeddings:
            embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        return cls.upsert(storage_context=storage_context,
                          service_context=service_context,
                          documents=documents,
                          ids=ids,
                          embeddings=embeddings,
                          **kwargs)

    @classmethod
    def upsert(cls, documents: [Document],
               ids: [str],
               embeddings: Embeddings,
               storage_context: StorageContext,
               service_context: ServiceContext,
               **kwargs: Any):


        if not service_context.embed_model.chunking_type or service_context.embed_model.chunking_type == DEFAULT_CHUNKING_TYPE:
            db = storage_context.vector_store.from_documents( documents=documents, ids=ids,
                                                             embedding=embeddings,
                                                             persist_directory=storage_context.persist_dir
                                                             )
            db.persist()
        else:
            _tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})
            sentence_splitter_default = SentenceSplitter(chunk_size=service_context.embed_model.chunk_size,
                                                         chunk_overlap=service_context.embed_model.chunk_overlap,
                                                         tokenizer=service_context.embed_model.tokenizer or _tokenizer)

            _documents = []
            _ids = []
            for i, document in enumerate(documents):
                sentence_chunks = sentence_splitter_default.split_text(document.page_content)
                for j, d in enumerate(sentence_chunks):
                    _document = Document(metadata=document.metadata,
                                         page_content=d)
                    _documents.append(_document)
                    _ids.append(ids[i] + "_chunk_" + str(j))

            db = storage_context.vector_store.from_documents(documents=_documents, ids=_ids,
                                                             persist_directory=storage_context.persist_dir,
                                                             embedding=embeddings)
            db.persist()

            return cls(storage_context=storage_context,
                       service_context=service_context,
                       documents=documents,
                       ids=ids,
                       embeddings=embeddings,
                       **kwargs, )


