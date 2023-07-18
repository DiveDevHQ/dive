from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
from dive.indices.index_context import IndexContext
from dive.types import EmbeddingModel
from langchain.schema import Document
import importlib
import time

def index_example_data(chunk_size, chunk_overlap):
    package_name = "integrations.connectors.example.filestorage.request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(None, None, "paul_graham_essay", None, None, None)

    metadata = {'account_id': 'self', 'connector_id': 'example',
                'obj_type': 'paul_graham_essay'}
    _ids = []
    _documents = []
    for d in data['results']:
        _metadata = metadata
        if 'metadata' in d:
            _metadata.update(d['metadata'])
        document = Document(page_content=str(d['data']), metadata=_metadata)
        _documents.append(document)
        _ids.append(d['id'])
    embedding_model = EmbeddingModel()
    embedding_model.chunking_type = "custom"
    embedding_model.chunk_size = chunk_size
    embedding_model.chunk_overlap = chunk_overlap
    service_context = ServiceContext.from_defaults(embed_model=embedding_model)
    index_context = IndexContext.from_documents(documents=_documents, ids=_ids, service_context=service_context)
    index_context.upsert()


def query_example_data(chunk_size):
    query_text = "What did the author do growing up?"
    query_context = QueryContext.from_documents()
    print(query_context)
    data = query_context.query(query=query_text,k=chunk_size,filter={'connector_id': "example"})
    summary=query_context.summarization(documents=data)
    print('------------top documents -----------------')
    for d in data:
        print(d.page_content)
    print('------------top summary -----------------')
    for s in summary:
        print(s)


index_example_data(256,20)
'''wait 1 min to run query method'''
time.sleep(60)
query_example_data(4)
