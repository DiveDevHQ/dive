from dive.util.configAPIKey import set_openai_api_key
from examples.base import index_example_data,query_example_data,clear_example_data, index_example_yc_safe_user_guide_data
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import OpenAI
import time

#Use chromadb and OpenAI embeddings and llm


set_openai_api_key()
index_example_yc_safe_user_guide_data(256, 20, False, OpenAIEmbeddings(), OpenAI())
print('------------Finish Indexing Data-----------------')
time.sleep(30)
print('------------Start Querying Data-----------------')
question = 'What is my post-money valuation when I raise 10 million for 15% ownership?'
instruction = None # 'summarise your response in no more than 5 lines' or 'answer this question in Indonesian'
query_example_data(question, 4, OpenAIEmbeddings(), OpenAI(temperature=0), instruction)
#clear_example_data()