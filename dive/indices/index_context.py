from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from typing import Optional, Any, Dict, List
from dive.constants import DEFAULT_CHUNKING_TYPE, DEFAULT_COLLECTION_NAME
from dive.util.text_splitter import SentenceSplitter, TokenTextSplitter, ParagraphSplitter
from dataclasses import dataclass
from langchain.schema import Document

import tiktoken
import environ

env = environ.Env()
environ.Env.read_env()  # reading .env file
import os


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
            **kwargs: Any,
    ):

        if not service_context:
            service_context = ServiceContext.from_defaults()

        if not storage_context:
            storage_context = StorageContext.from_defaults(embedding_function=service_context.embeddings)

        return cls.upsert(
            documents=documents,
            ids=ids,
            service_context=service_context,
            storage_context=storage_context,
            **kwargs)

    @classmethod
    def upsert(cls, documents: [Document],
               ids: [str],
               service_context: ServiceContext,
               storage_context: Optional[StorageContext] = None,
               **kwargs: Any):

        _documents = []
        _ids = []

        if not service_context.embed_config.chunking_type or service_context.embed_config.chunking_type == DEFAULT_CHUNKING_TYPE:
            _documents = documents
            _ids = ids
        elif service_context.embed_config.chunking_type == 'paragraph':
            paragraph_splitter_default = ParagraphSplitter()
            for i, document in enumerate(documents):
                sentence_chunks = paragraph_splitter_default.split_text(document.page_content)
                for j, d in enumerate(sentence_chunks):
                    if not d:
                        continue
                    _document = Document(metadata=document.metadata,
                                         page_content=d)
                    _documents.append(_document)
                    _ids.append(ids[i] + "_chunk_" + str(j))

        else:
            _tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})
            sentence_splitter_default = TokenTextSplitter(chunk_size=service_context.embed_config.chunk_size,
                                                          chunk_overlap=service_context.embed_config.chunk_overlap,
                                                          tokenizer=service_context.embed_config.tokenizer or _tokenizer)

            for i, document in enumerate(documents):
                sentence_chunks = sentence_splitter_default.split_text(document.page_content)
                for j, d in enumerate(sentence_chunks):
                    _document = Document(metadata=document.metadata,
                                         page_content=d)
                    _documents.append(_document)
                    _ids.append(ids[i] + "_chunk_" + str(j))

        PINECONE_API_KEY = env.str('PINECONE_API_KEY', default='') or os.environ.get('PINECONE_API_KEY', '')

        if PINECONE_API_KEY:
            storage_context.vector_store.from_documents(
                index_name=DEFAULT_COLLECTION_NAME,
                documents=_documents, ids=_ids, batch_size=100,
                embedding=service_context.embeddings)

        else:
            CHROMA_PERSIST_DIR = env.str('CHROMA_PERSIST_DIR', default='db') or os.environ.get('CHROMA_PERSIST_DIR',
                                                                                               'db')
            storage_context.vector_store.from_documents(
                collection_name=DEFAULT_COLLECTION_NAME,
                documents=_documents, ids=_ids,
                persist_directory=CHROMA_PERSIST_DIR,
                embedding=service_context.embeddings)

        return cls(storage_context=storage_context,
                   service_context=service_context,
                   documents=documents,
                   ids=ids,
                   **kwargs, )

    def delete(self, ids: Optional[List[str]] = None,
               delete_all: Optional[bool] = None,
               filter: Optional[dict] = None):

        self.storage_context.vector_store.delete(ids=ids, delete_all=delete_all, filter=filter)
