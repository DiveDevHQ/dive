import chromadb
from chromadb.config import Settings


class ChromaDBClient:
    db_directory = "db"

    def db_connection(self):
        db_connection = chromadb.Client(
            Settings(
                persist_directory=self.db_directory,
                chroma_db_impl="duckdb+parquet",
            )
        )







