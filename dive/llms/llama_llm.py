from langchain.llms.base import BaseLLM
from langchain.schema.messages import BaseMessage, get_buffer_string
from langchain.schema.output import LLMResult
from langchain.schema.prompt import PromptValue
from abc import abstractmethod
from typing import List, Any, Optional,Sequence
from langchain.callbacks.manager import Callbacks

class LlamaLLM(BaseLLM):

    @abstractmethod
    def predict_messages(
            self,
            messages: List[BaseMessage],
            *,
            stop: Optional[Sequence[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        return None



    @abstractmethod
    async def apredict(
            self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any
    ) -> str:
        return None


    @abstractmethod
    async def apredict_messages(
            self,
            messages: List[BaseMessage],
            *,
            stop: Optional[Sequence[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:

        return None

    @abstractmethod
    def generate_prompt(
            self,
            prompts: List[PromptValue],
            stop: Optional[List[str]] = None,
            callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> LLMResult:

        return None

    @abstractmethod
    def predict(
            self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any
    ) -> str:
        return None