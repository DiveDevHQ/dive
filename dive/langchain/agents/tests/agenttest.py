import pytest
from dive.langchain.agents.agent import Agent




def test_agent_prompt():
    prompt = "print out the result for 2+2"
    answer = "4"
    agent = Agent()
    assert agent.agent(prompt) == answer
