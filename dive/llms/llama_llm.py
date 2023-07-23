from langchain.llms.base import BaseLLM
from langchain.schema.messages import BaseMessage, get_buffer_string
from langchain.schema.output import LLMResult
from langchain.schema.prompt import PromptValue
from abc import abstractmethod
from typing import List, Any, Optional,Sequence
from langchain.callbacks.manager import Callbacks
from langchain.callbacks.manager import (
    AsyncCallbackManager,
    AsyncCallbackManagerForLLMRun,
    CallbackManager,
    CallbackManagerForLLMRun,
    Callbacks,
)

class LlamaLLM(BaseLLM):


    def predict_messages(
            self,
            messages: List[BaseMessage],
            *,
            stop: Optional[Sequence[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        return None




    async def apredict(
            self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any
    ) -> str:
        return None



    async def apredict_messages(
            self,
            messages: List[BaseMessage],
            *,
            stop: Optional[Sequence[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:

        return None


    def generate_prompt(
            self,
            prompts: List[PromptValue],
            stop: Optional[List[str]] = None,
            callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> LLMResult:

        return None


    def predict(
            self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any
    ) -> str:
        return None

    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        return None

    async def _agenerate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        return None


    @property
    def _llm_type(self) -> str:
        return None