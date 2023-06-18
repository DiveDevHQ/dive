import chromadb
from chromadb.config import Settings


def index_documents(documents, instance_id, obj_type):
    persist_directory = "db"
    client = chromadb.Client(
        Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )
    client.reset()
    collection_name = "peristed_collection"
    collection = client.create_collection(name=collection_name)
    _documents = []
    _document_ids = []
    _object_types = []
    for document in documents:
        _documents.append(document['text'])
        _document_ids.append(document['id'])
        _object_types.append({'instance_id':instance_id,'obj_type': obj_type})
    collection.add(
        documents=_documents,
        # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
        metadatas=_object_types,  # filter on these!
        ids=_document_ids,  # unique for each doc
    )

    client.persist()


def query_documents(query, instance_id):
    persist_directory = "db"
    client = chromadb.Client(
        Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )
    collection_name = "peristed_collection"
# Load the collection
    collection = client.get_collection(collection_name)
    results = collection.query(
        query_texts=query,
        where={"instance_id": instance_id},
        n_results=2,
        # where={"metadata_field": "is_equal_to_this"}, # optional filter
        # where_document={"$contains":"search_string"}  # optional filter
    )
    return results