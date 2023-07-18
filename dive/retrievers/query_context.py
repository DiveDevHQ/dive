
from dive.storages.storage_context import StorageContext
from dive.types import VectorStoreQuery, VectorQueryResult
from typing import Optional, List, Any, Dict
from dataclasses import dataclass


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

    def query(self, query: VectorStoreQuery) -> VectorQueryResult:
        return self.storage_context.vector_store.query(query=query)
