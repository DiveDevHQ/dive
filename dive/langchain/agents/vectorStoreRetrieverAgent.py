from dive.langchain.agents.agent import Agent
from langchain.vectorstores import Chroma
from dive.util.chromaDBClient import ChromaDBClient
from langchain.chains.summarize import load_summarize_chain
from dive.util.openAIAPIKey import set_openai_api_key
from langchain import OpenAI

class VectorStoreRetrieverAgent(Agent):

    def __init__(self):
        set_openai_api_key()

    def retrieve(self, prompt) -> str:
        similarity_search = "similarity"
        refine_chain_type = "refine"
        llm = OpenAI()
        db_client = ChromaDBClient()
        chromadb = Chroma(client = db_client)
        relevant_docs = chromadb.search(query = prompt, search_type = similarity_search)
        chain = load_summarize_chain(llm = llm, chain_type= refine_chain_type, prompt = prompt)
        return chain.run()









