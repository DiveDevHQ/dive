from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
import importlib
from langchain.schema import Document
from dive.types import EmbeddingModel
from dive.indices.index_context import IndexContext


def index_example_data(chunk_size, chunk_overlap, summarize, embeddings, llm):
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
    embedding_model.summarize = summarize
    service_context = ServiceContext.from_defaults(embed_config=embedding_model, embeddings=embeddings, llm=llm)
    IndexContext.from_documents(documents=_documents, ids=_ids, service_context=service_context)


def query_example_data(question, chunk_size, embeddings, llm, instruction):
    service_context = ServiceContext.from_defaults(embeddings=embeddings, llm=llm, instruction=instruction)
    query_context = QueryContext.from_defaults(service_context=service_context)
    data = query_context.query(query=question, k=chunk_size)
    print('------------top K chunks -----------------')
    for d in data:
        print(d.page_content)
        print('')
    short_answer=query_context.question_answer(query=question,documents=data)
    print('------------short answer -----------------')
    print(short_answer)
    summary = query_context.summarization(documents=data)
    print('------------summary -----------------')
    print(summary)


def clear_example_data():
    index_context = IndexContext.from_defaults()
    index_context.delete(delete_all=True)
