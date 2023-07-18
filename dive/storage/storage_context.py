from dive.vector_db.vector_store import VectorStore
from typing import Optional, List
from dive.vector_db.chroma.vector_data import ChromaVectorStore
import chromadb
from chromadb.config import Settings
from dataclasses import dataclass
from dive.constants import DEFAULT_COLLECTION_NAME


@dataclass
class StorageContext:
    vector_store: VectorStore

    @classmethod
    def from_defaults(cls,
                      vector_store: Optional[VectorStore] = None,
                      persist_dir: Optional[str] = None):
        if not vector_store:
            chroma_client = chromadb.Client(
                Settings(
                    persist_directory=persist_dir or "db",
                    chroma_db_impl="duckdb+parquet",
                )
            )
            collection = chroma_client.get_or_create_collection(DEFAULT_COLLECTION_NAME)

            vector_store = ChromaVectorStore(chroma_collection=collection, persist_dir=persist_dir or "db")

        return cls(
            vector_store=vector_store
        )
