from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from dive.types import EmbeddingResult
from typing import Optional, List, Any, Dict
from dive.constants import DEFAULT_CHUNKING_TYPE
from dive.vector_db.text_splitter import SentenceSplitter
from dataclasses import dataclass
import tiktoken


@dataclass
class IndexContext:
    service_context: ServiceContext
    storage_context: StorageContext
    documents: [EmbeddingResult]

    @classmethod
    def from_documents(
            cls,
            documents: List[EmbeddingResult],
            storage_context: Optional[StorageContext] = None,
            service_context: Optional[ServiceContext] = None,
            **kwargs: Any,
    ):

        if not storage_context:
            storage_context = StorageContext.from_defaults()
        if not service_context:
            service_context = ServiceContext.from_defaults()

        return cls(storage_context=storage_context,
                   service_context=service_context,
                   documents=documents,
                   **kwargs, )

    def insert(self)->[]:
        if not self.service_context.embed_model.chunking_type or self.service_context.embed_model.chunking_type == DEFAULT_CHUNKING_TYPE:
            return self.storage_context.vector_store.add(embedding_results=self.documents)

        else:
            sentence_splitter_default = SentenceSplitter(chunk_size=self.service_context.embed_model.chunk_size,
                                                         chunk_overlap=self.service_context.embed_model.chunk_overlap,
                                                         tokenizer=self.service_context.embed_model.tokenizer)

            _documents = [EmbeddingResult]
            for document in self.documents:
                sentence_chunks = sentence_splitter_default.split_text(document.text)
                for i, d in enumerate(sentence_chunks):
                    _document = EmbeddingResult(id=document.id + "_chunk_" + str(i), metadata=document.metadata,
                                                text=document.text)
                    _documents.append(d)
            return self.storage_context.vector_store.add(embedding_results=_documents)



    def upsert(self)->[]:

        if not self.service_context.embed_model.chunking_type or self.service_context.embed_model.chunking_type == DEFAULT_CHUNKING_TYPE:
            return self.storage_context.vector_store.upsert(embedding_results=self.documents)

        else:
            _tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})
            sentence_splitter_default = SentenceSplitter(chunk_size=self.service_context.embed_model.chunk_size,
                                                             chunk_overlap=self.service_context.embed_model.chunk_overlap,
                                                             tokenizer=self.service_context.embed_model.tokenizer or _tokenizer)

            _documents = []

            for document in self.documents:
                sentence_chunks = sentence_splitter_default.split_text(document.text)
                for i, d in enumerate(sentence_chunks):
                    _document = EmbeddingResult(id=document.id + "_chunk_" + str(i), metadata=document.metadata,
                                                    text=d)
                    _documents.append(_document)
            return self.storage_context.vector_store.upsert(embedding_results=_documents)


    def delete(self, where: Dict):
        self.storage_context.vector_store.delete_query(where)
