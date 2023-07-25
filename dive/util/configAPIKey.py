import os


def set_openai_api_key():
    os.environ["OPENAI_API_KEY"] = ""

def set_pinecone_api_key():
    os.environ["PINECONE_API_KEY"] = ""

def set_pinecone_env():
    os.environ["PINECONE_ENV"] = ""

def set_pinecone_index_dimentions():
    os.environ["PINECONE_INDEX_DIMENSIONS"] = ""

def set_chromadb_persist():
    os.environ["CHROMA_PERSIST_DIR"] = ""