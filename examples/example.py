from dive.retrievers.query_context import QueryContext
from dive.indices.service_context import ServiceContext
from dive.storages.storage_context import StorageContext
from dive.indices.index_context import IndexContext
from dive.constants import DEFAULT_COLLECTION_NAME
from dive.types import EmbeddingModel
from langchain.embeddings import LlamaCppEmbeddings
from langchain.schema import Document
import importlib
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from huggingface_hub import  hf_hub_download
import os
import time
import nltk
import os
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager

nltk.download('punkt')
from langchain.embeddings.openai import OpenAIEmbeddings
from dive.util.configAPIKey import set_openai_api_key, set_pinecone_api_key, set_pinecone_env, \
    set_pinecone_index_dimentions,set_hugging_face_auth
from langchain import OpenAI
from langchain.schema import Document
import importlib



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
    summary = query_context.summarization(documents=data)
    print('------------summary -----------------')
    print(summary)


def clear_example_data():
    index_context = IndexContext.from_defaults()
    index_context.delete(delete_all=True)


# Use pinecone vector db

#set_pinecone_api_key()
#set_pinecone_env()
#set_pinecone_index_dimentions()


# Default free model
'''
index_example_data(256, 20, False, None,None)
# wait 1 min to run query method
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
question='What did the author do growing up?'
query_example_data(question, 4, None, None, None)
#clear_example_data()
'''

 
# Open AI model
'''
set_openai_api_key()
#index_example_data(256, 20, False, OpenAIEmbeddings(), OpenAI())
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
question = 'What did the author do growing up?'
instruction = None  # 'summarise your response in no more than 5 lines'
#query_example_data(question, 4, OpenAIEmbeddings(), OpenAI(temperature=0), instruction)
#clear_example_data()
'''


# Llama v2 7B model
#os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
#os.environ["COMMANDLINE_ARGS"] = "--skip-torch-cuda-test --upcast-sampling --no-half-vae --no-half --opt-sub-quad-attention --use-cpu interrogate"

set_hugging_face_auth()
hf_auth = os.environ.get('use_auth_token', '')
model_path = hf_hub_download(repo_id='TheBloke/Llama-2-7B-GGML', filename='llama-2-7b.ggmlv3.q5_1.bin', use_auth_token=hf_auth)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llama_embeddings = LlamaCppEmbeddings(model_path=model_path)
llm = LlamaCpp(
    model_path=model_path,
    input={"temperature": 0.75, "max_length": 2000, "top_p": 1},
    callback_manager=callback_manager,
    verbose=True,
)
 
index_example_data(256, 20, False, llama_embeddings,llm)
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
question='What did the author do growing up?'
instruction='summarise your response in no more than 5 lines'
query_example_data(question,4, llama_embeddings,llm,instruction)

