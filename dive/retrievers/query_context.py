from dive.storages.storage_context import StorageContext
from typing import Optional, List, Any, Dict
from dataclasses import dataclass
from langchain.schema import Document
from dive.constants import DEFAULT_QUERY_CHUNK_SIZE


@dataclass
class QueryContext:
    storage_context: StorageContext

    @classmethod
    def from_documents(
            cls,
            storage_context: Optional[StorageContext] = None,
            **kwargs: Any,
    ):
        if not storage_context:
            storage_context = StorageContext.from_defaults()

        return cls(storage_context=storage_context,
                   **kwargs, )

    def query(self, query: str, k: int = DEFAULT_QUERY_CHUNK_SIZE, filter: Optional[Dict[str, str]] = None) -> List[
        Document]:
        return self.storage_context.vector_store.similarity_search(query=query, k=k, filter=filter)
