import pytest
from dive.langchain.agents import vectorStoreRetrieverAgent

def test_agent_prompt():
    prompt = "What did george washington say?"
    answer = "4"
    agent = vectorStoreRetrieverAgent()
    assert answer == agent.retrieve()
