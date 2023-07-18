

from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
from dive.indices.index_context import IndexContext
from dive.types import VectorStoreQuery,EmbeddingResult,EmbeddingModel
import importlib

def index_example_data(chunk_size, chunk_overlap):
    package_name = "integrations.connectors.example.filestorage.request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(None, None, "paul_graham_essay", None, None, None)
    print(data)
    metadata = {'account_id': 'self', 'connector_id': 'example',
                'obj_type': 'paul_graham_essay'}
    documents=[]
    for d in data['results']:
        embedding_document=EmbeddingResult(id=d['id'],text=d['data'],metadata=d['metadata'])
        embedding_document.metadata.update(metadata)
        documents.append(embedding_document)

    embedding_model = EmbeddingModel()
    embedding_model.chunking_type = "custom"
    embedding_model.chunk_size = chunk_size
    embedding_model.chunk_overlap = chunk_overlap
    service_context = ServiceContext.from_defaults(embed_model=embedding_model)
    index_context = IndexContext.from_documents(documents=documents, service_context=service_context)
    ids = index_context.upsert()


def query_example_data(chunk_size):
    query_text="What did the author do growing up?"
    query_context = QueryContext.from_documents()
    vector_store_query = VectorStoreQuery()
    vector_store_query.text = query_text
    vector_store_query.llm = None
    vector_store_query.chunk_size = chunk_size
    vector_store_query.where = {'connector_id': "example"}
    data = query_context.query(query=vector_store_query)
    print('------------top documents -----------------')
    for d in data.query_documents:
        print(d.document)
    print('------------top summary -----------------')
    for s in data.summary:
        print(s)


index_example_data(256,20)
'''wait 1 min to run query method'''
#query_example_data(4)


