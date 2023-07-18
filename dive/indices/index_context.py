from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from typing import Optional, List, Any, Dict
from dive.constants import DEFAULT_CHUNKING_TYPE
from dive.vector_db.text_splitter import SentenceSplitter
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
            documents: [Document] = None,
            ids: [str] = None,
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
        return cls(storage_context=storage_context,
                   service_context=service_context,
                   documents=documents,
                   ids=ids,
                   embeddings=embeddings,
                   **kwargs, )

    def upsert(self):

        if not self.service_context.embed_model.chunking_type or self.service_context.embed_model.chunking_type == DEFAULT_CHUNKING_TYPE:
            db = self.storage_context.vector_store.from_documents(documents=self.documents, ids=self.ids,
                                                                  embedding=self.embeddings,
                                                                  persist_directory=self.storage_context.persist_dir
                                                                  )
            db.persist()

        else:
            _tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})
            sentence_splitter_default = SentenceSplitter(chunk_size=self.service_context.embed_model.chunk_size,
                                                         chunk_overlap=self.service_context.embed_model.chunk_overlap,
                                                         tokenizer=self.service_context.embed_model.tokenizer or _tokenizer)

            _documents = []
            _ids = []
            for i, document in enumerate(self.documents):
                sentence_chunks = sentence_splitter_default.split_text(document.page_content)
                for j, d in enumerate(sentence_chunks):
                    _document = Document(metadata=document.metadata,
                                         page_content=d)
                    _documents.append(_document)
                    _ids.append(self.ids[i] + "_chunk_" + str(j))

            db = self.storage_context.vector_store.from_documents(documents=_documents, ids=_ids,
                                                                  persist_directory=self.storage_context.persist_dir,
                                                                  embedding=self.embeddings)
            db.persist()
            data = db.similarity_search(query="What did the author do growing up?",k=4,filter={'connector_id': "example"})
            print(data)

    def delete(self, where: Dict):
        result=self.storage_context.vector_store.get(where=where)
        self.storage_context.vector_store.delete(ids=result['ids'])
