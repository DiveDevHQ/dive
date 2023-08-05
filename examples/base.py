from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
import importlib
from langchain.schema import Document
from dive.types import EmbeddingConfig
from dive.indices.index_context import IndexContext


def index_example_data(chunk_size, chunk_overlap, summarize, embeddings, llm):
    package_name = "integrations.connectors.example.filestorage.request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(None, None, "pg_essay_paging", None, None, None)
    metadata = {'account_id': 'self', 'connector_id': 'example',
                'obj_type': 'pg_essay_paging'}
    _ids = []
    _documents = []

    for d in data['results']:
        _metadata = metadata
        if 'metadata' in d:
            _metadata.update(d['metadata'])
        document = Document(page_content=str(d['data']), metadata=_metadata)
        _documents.append(document)
        _ids.append(d['id'])

    embedding_config = EmbeddingConfig()
    embedding_config.chunking_type = "custom"
    embedding_config.chunk_size = chunk_size
    embedding_config.chunk_overlap = chunk_overlap
    embedding_config.summarize = summarize
    service_context = ServiceContext.from_defaults(embed_config=embedding_config, embeddings=embeddings, llm=llm)
    IndexContext.from_documents(documents=_documents, ids=_ids, service_context=service_context)


def index_example_yc_safe_user_guide_data(chunk_size, chunk_overlap, summarize, embeddings, llm):
    package_name = "integrations.connectors.example.filestorage.request_data"
    mod = importlib.import_module(package_name)
    data = mod.load_objects(None, None, "yc_safe_user_guide", None, None, None)

    metadata = {'account_id': 'self', 'connector_id': 'example',
                'obj_type': 'yc_safe_user_guide'}
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

    top_chunks=[]

    summary_ids = []
    for d in data:
        top_chunks.append(d.page_content)
        _metadata = d.metadata
        if 'summary_id' in _metadata:
            summary_ids.append(_metadata['summary_id'])

    _documents = data
    if len(summary_ids) > 0:
        _documents = []
        for id in summary_ids:
            chunks = query_context.get(filter={'summary_id': id})
            _documents += chunks
        print('------------top summary chunks -----------------')
        for _document in _documents:
            print(_document.page_content)
            print('-> next chunk')
    else:
        print('------------top K chunks -----------------')
        for tc in top_chunks:
            print(tc)
            print('-> next chunk')

    short_answer = query_context.question_answer(query=question, documents=_documents)
    print('------------short answer -----------------')
    print(short_answer)
    summary = query_context.summarization(documents=_documents)
    print('------------summary -----------------')
    print(summary)


def clear_example_data():
    index_context = IndexContext.from_defaults()
    index_context.delete(delete_all=True)
