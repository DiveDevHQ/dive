
from typing import Optional, List
import chromadb
from chromadb.config import Settings
from dataclasses import dataclass
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings


@dataclass
class StorageContext:
    vector_store: VectorStore
    persist_dir: str = "db"

    @classmethod
    def from_defaults(cls,
                      vector_store: Optional[VectorStore] = None,
                      persist_dir: Optional[str] = None):
        if not vector_store:
            client_settings = chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir or "db"
            )
            client = chromadb.Client(
                client_settings
            )
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = Chroma(client=client,client_settings=client_settings, persist_directory=persist_dir or "db", embedding_function=embedding_function)

        return cls(
            vector_store=vector_store,
            persist_dir=persist_dir or "db"
        )
