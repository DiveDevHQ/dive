import pytest
from dive.langchain.agents.vectorStoreRetrieverAgent import VectorStoreRetrieverAgent

def test_agent_prompt():
    prompt = "What did george washington say?"
    answer = "4"
    agent = VectorStoreRetrieverAgent()
    assert answer == agent.retrieve(prompt)
