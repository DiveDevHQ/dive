# from dive.vector_db.vector_store import VectorStore
from typing import Optional, List
# from dive.vector_db.chroma.vector_data import ChromaVectorStore
import chromadb
from chromadb.config import Settings
from dataclasses import dataclass
from dive.constants import DEFAULT_COLLECTION_NAME
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores import Chroma
from chromadb.utils import embedding_functions
from langchain.embeddings.base import Embeddings
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
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = Chroma(persist_directory=persist_dir or "db", embedding_function=embedding_function)

        return cls(
            vector_store=vector_store,
            persist_dir=persist_dir or "db"
        )
