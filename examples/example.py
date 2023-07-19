from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
from dive.indices.index_context import IndexContext
from dive.types import EmbeddingModel
from langchain.schema import Document
import importlib
import time
import nltk
nltk.download('punkt')
from langchain.embeddings.openai import OpenAIEmbeddings
from dive.util.openAIAPIKey import set_openai_api_key
from langchain import OpenAI

def index_example_data(chunk_size, chunk_overlap, embeddings):
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
    IndexContext.from_documents(documents=_documents, ids=_ids, service_context=service_context,
                                                embeddings=embeddings)


def query_example_data(chunk_size, llm):
    query_text = "What did the author do growing up?"
    query_context = QueryContext.from_defaults()
    data = query_context.query(query=query_text, k=chunk_size, filter={'connector_id': "example"})
    summary = query_context.summarization(documents=data,llm=llm)
    print('------------top K chunks -----------------')
    for d in data:
        print(d.page_content)
    print('------------summary -----------------')
    print(summary)


#Default free model

index_example_data(256, 20, None)
#wait 1 min to run query method
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
query_example_data(4, None)


#Open AI model
'''
set_openai_api_key()
index_example_data(256, 20, OpenAIEmbeddings())
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
query_example_data(4, OpenAI())
'''