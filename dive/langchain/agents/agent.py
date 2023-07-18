from langchain import OpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType

import os

from dive.util.openAIAPIKey import set_openai_api_key


class Agent:

    def __init__(self, tools):
        set_openai_api_key()
        self.tools = tools

    def agent(self, prompt):
        llm = OpenAI(temperature=0)
        agent = initialize_agent(self.tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
        return agent.run(prompt)












