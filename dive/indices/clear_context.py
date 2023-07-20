from dive.storages.storage_context import StorageContext
from typing import Optional, Any, Dict
from dataclasses import dataclass


@dataclass
class ClearContext:

    storage_context: StorageContext

    @classmethod
    def from_defaults(
            cls,
            storage_context: Optional[StorageContext] = None
    ):

        if not storage_context:
            storage_context = StorageContext.from_defaults()

        return cls(storage_context=storage_context)


    def delete_from(self, where: Dict):

        result = self.storage_context.vector_store.get(where=where)

        if len(result['ids']) > 0:
            try:
                self.storage_context.vector_store.delete(ids=result['ids'])
            except KeyError:
                return

