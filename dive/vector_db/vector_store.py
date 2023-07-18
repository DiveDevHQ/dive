from typing import Any, List, Optional, Protocol, Dict
from dive.types import VectorQueryResult


class VectorStore(Protocol):
    """Abstract vector store protocol."""

    stores_text: bool
    is_embedding_query: bool = True

    @property
    def client(self) -> Any:
        """Get client."""
        ...

    def add(
            self,
            embedding_results: List[Any],
    ) -> List[str]:
        """Add embedding results to vector store."""
        ...

    def upsert(
            self,
            embedding_results: List[Any],
    ) -> List[str]:
        """Add embedding results to vector store."""
        ...

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""
        ...

    def delete_query(self, where: Dict, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""
        ...

    def query(self, query: Dict, **kwargs: Any) -> VectorQueryResult:
        """Query vector store."""
        ...

    def persist(
            self, persist_path: str
    ) -> None:
        return None

