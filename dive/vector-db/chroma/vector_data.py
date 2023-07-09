import chromadb
from chromadb.config import Settings

db_directory = "db"
vector_collection_name="peristed_collection"


def index_documents(documents, connector_id, obj_type):
    if len(documents) == 0:
        return
    persist_directory = db_directory
    client = chromadb.Client(
        Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )

    collection = client.get_or_create_collection(name=vector_collection_name)

    _documents = []
    _document_ids = []
    _metadatas = []
    for document in documents:
        _documents.append(document['text'])
        _document_ids.append(document['id'])
        _metadatas.append({'connector_id': connector_id, 'obj_type': obj_type})

    collection.upsert(
        documents=_documents,
        # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
        metadatas=_metadatas,  # filter on these!
        ids=_document_ids,  # unique for each doc
    )

    client.persist()


def delete_documents_by_connector_id(connector_id):
    persist_directory = db_directory
    collection_name = vector_collection_name
    client = chromadb.Client(
        Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )
    try:
        collection = client.get_collection(collection_name)
    except ValueError:
        return
    collection.delete(where={"connector_id": connector_id})


def query_documents(query, connector_id):

    client = chromadb.Client(
        Settings(
            persist_directory=db_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )
    # Load the collection
    try:
        collection = client.get_collection(vector_collection_name)
    except ValueError:
        error_data = {'error': {}}
        error_data['error']['id'] = 'Resources Gone'
        error_data['error']['message'] = 'Requested vector collection does not exist'
        error_data['error']['status_code'] = 410
        return error_data

    try:
        results = collection.query(
            query_texts=query,
            where={"connector_id": connector_id},
            n_results=2,
            # where={"metadata_field": "is_equal_to_this"}, # optional filter
            # where_document={"$contains":"search_string"}  # optional filter
        )
        return results
    except Exception as e:
        error_data = {'error': {}}
        error_data['error']['id'] = 'Bad request'
        error_data['error']['status_code'] = 400
        error_data['error']['message'] = str(e)
        return error_data

    return None
