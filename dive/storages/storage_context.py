from typing import Optional, List
from dataclasses import dataclass
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from dive.constants import DEFAULT_COLLECTION_NAME
from langchain.embeddings.base import Embeddings
import environ
env = environ.Env()
environ.Env.read_env()  # reading .env file

@dataclass
class StorageContext:
    vector_store: VectorStore
    persist_dir: str = "db"

    @classmethod
    def from_defaults(cls,
                      vector_store: Optional[VectorStore] = None,
                      embedding_function: Optional[Embeddings] = None,
                      persist_dir: Optional[str] = None):
        if not vector_store:
            if env.str('PINECONE_API_KEY', default=''):
                import_err_msg = (
                    "`pinecone` package not found, please run `pip install pinecone`"
                )
                try:
                    import pinecone
                    pinecone.init(
                        api_key=env.str('PINECONE_API_KEY', default=''),  # find at app.pinecone.io
                        environment=env.str('PINECONE_ENV', default=''),  # next to api key in console
                    )
                except ImportError:
                    raise ImportError(import_err_msg)
            else:
                import_err_msg = (
                    "`chromadb` package not found, please run `pip install chromadb`"
                )
                try:
                    import chromadb
                    client_settings = chromadb.config.Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=persist_dir or "db"
                    )
                    client = chromadb.Client(
                        client_settings
                    )
                    client.get_or_create_collection(DEFAULT_COLLECTION_NAME)
                    if not embedding_function:
                        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
                    vector_store = Chroma(client=client, client_settings=client_settings,
                                          collection_name=DEFAULT_COLLECTION_NAME, persist_directory=persist_dir or "db",
                                          embedding_function=embedding_function)
                except ImportError:
                    raise ImportError(import_err_msg)

        return cls(
            vector_store=vector_store,
            persist_dir=persist_dir or "db"
        )
