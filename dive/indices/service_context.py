from dive.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNKING_TYPE
from pydantic import BaseModel
from typing import Optional, List
import tiktoken
from dataclasses import dataclass


@dataclass
class ServiceContext:
    embed_model: BaseModel
    llm: BaseModel

    @classmethod
    def from_defaults(cls, embed_model: Optional[BaseModel] = None, llm: Optional[BaseModel] = None
                      ):
        if not embed_model:
            embed_model = DefaultEmbeddingModel()
        if not llm:
            llm = DefaultLLMModel()

        return cls(
            embed_model=embed_model,
            llm=llm
        )


class DefaultEmbeddingModel(BaseModel):
    chunking_type = DEFAULT_CHUNKING_TYPE
    chunk_size = DEFAULT_CHUNK_SIZE
    chunk_overlap = DEFAULT_CHUNK_OVERLAP
    tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})


class DefaultLLMModel(BaseModel):
    prompts: Optional[List[str]]
    model = "all-MiniLM-L6-v2"
