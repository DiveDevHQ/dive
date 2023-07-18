import chromadb
from chromadb.config import Settings
from dive.vector_db import query_utils
from dive.vector_db.vector_store import VectorStore
from typing import Optional, List, Any, Dict
from dive.types import EmbeddingResult, VectorStoreQuery, VectorQueryResult, QueryDocument
from dive.constants import DEFAULT_COLLECTION_NAME


class ChromaVectorStore(VectorStore):
    storage_path: str = "db"
    collection: Any

    def __init__(self, chroma_collection: Any, persist_dir: Optional[str]) -> None:
        self.collection = chroma_collection
        if persist_dir:
            self.storage_path = persist_dir

    def add(self, embedding_results: List[EmbeddingResult]) -> List[str]:
        if not self.collection:
            raise ValueError("Collection not initialized")
        _embeddings = []
        _embeddings_ids = []
        _embeddings_metadatas = []

        _documents = []
        _documents_ids = []
        _documents_metadatas = []

        for result in embedding_results:
            if result.embedding:
                _embeddings.append(result.embedding)
                _embeddings_metadatas.append(result.metadata)
                _embeddings_ids.append(result.id)
            else:
                _documents.append(result.text)
                _documents_metadatas.append(result.metadata)
                _documents_ids.append(result.id)

        if len(_embeddings) > 0:
            self.collection.add(
                embeddings=_embeddings,
                metadatas=_embeddings_metadatas,  # filter on these!
                ids=_embeddings_ids,  # unique for each doc
            )
        else:
            self.collection.add(
                documents=_documents,
                # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
                metadatas=_documents_metadatas,  # filter on these!
                ids=_documents_ids,  # unique for each doc
            )
        self.client.persist()
        return _embeddings_ids + _documents_ids

    def upsert(self, embedding_results: List[EmbeddingResult]) -> List[str]:

        if not self.collection:
            raise ValueError("Collection not initialized")

        _embeddings = []
        _embeddings_ids = []
        _embeddings_metadatas = []

        _documents = []
        _documents_ids = []
        _documents_metadatas = []

        for result in embedding_results:
            if result.embedding and len(result.embedding > 0):
                _embeddings.append(result.embedding)
                _embeddings_metadatas.append(result.metadata)
                _embeddings_ids.append(result.id)
            else:
                _documents.append(result.text)
                _documents_metadatas.append(result.metadata)
                _documents_ids.append(result.id)

        if len(_embeddings) > 0:
            self.collection.upsert(
                embeddings=_embeddings,
                metadatas=_embeddings_metadatas,  # filter on these!
                ids=_embeddings_ids,  # unique for each doc
            )

        if len(_documents) > 0:
            self.collection.upsert(
                documents=_documents,
                # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
                metadatas=_documents_metadatas,  # filter on these!
                ids=_documents_ids,  # unique for each doc
            )
        self.client.persist()
        return _embeddings_ids + _documents_ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        self.collection.delete(where={"document_id": ref_doc_id})

    def delete_query(self, where: Dict, **delete_kwargs: Any) -> None:
        self.collection.delete(where=where)

    @property
    def client(self) -> Any:
        client = chromadb.Client(
            Settings(
                persist_directory=self.storage_path,
                chroma_db_impl="duckdb+parquet",
            )
        )

        return client

    def persist(
            self, persist_path: str
    ) -> None:
        self.storage_path = persist_path
        return None

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorQueryResult:
        if not self.collection:
            raise ValueError("Collection not initialized")
        try:
            results = self.collection.query(
                query_texts=query.text,
                where=query.where,
                n_results=query.chunk_size,
                # where={"metadata_field": "is_equal_to_this"}, # optional filter
                # where_document={"$contains":"search_string"}  # optional filter
            )

            document_list = []
            item_list = []

            for result in results['ids']:
                for i, id in enumerate(result):
                    if len(item_list) < i + 1:
                        item_list.append(QueryDocument())
                    item_list[i].id = id

            for result in results['documents']:
                for i, sentence in enumerate(result):
                    if len(item_list) < i + 1:
                        item_list.append(QueryDocument())
                    item_list[i].document = sentence
                    document_list.append(sentence)

            for result in results['metadatas']:
                for i, metadata in enumerate(result):
                    if len(item_list) < i + 1:
                        item_list.append(QueryDocument())
                    item_list[i].metadata = metadata

            for result in results['distances']:
                for i, distance in enumerate(result):
                    if len(item_list) < i + 1:
                        item_list.append(QueryDocument())
                    item_list[i].distance = distance

            summary_list = query_utils.get_text_summarization(document_list, query.llm)
            return VectorQueryResult(query_documents=item_list, summary=summary_list)
        except Exception as e:
            print(str(e))
            return None
