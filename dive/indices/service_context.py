from dive.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNKING_TYPE
from pydantic import BaseModel
from typing import Optional, List
import tiktoken
from dataclasses import dataclass
from langchain.embeddings.base import Embeddings
from langchain.chains.llm import BaseLanguageModel
from langchain.embeddings import SentenceTransformerEmbeddings

@dataclass
class ServiceContext:
    embed_config: BaseModel
    embeddings:Embeddings
    llm: BaseModel

    @classmethod
    def from_defaults(cls, embed_config: Optional[BaseModel] = None,
                      embeddings: Optional[Embeddings]=None,
                      llm: Optional[BaseLanguageModel] = None
                      ):
        if not embed_config:
            embed_config = DefaultEmbeddingConfig()

        if not embeddings:
            embeddings=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        return cls(
            embed_config=embed_config,
            embeddings=embeddings,
            llm=llm
        )


class DefaultEmbeddingConfig(BaseModel):
    chunking_type = DEFAULT_CHUNKING_TYPE
    chunk_size = DEFAULT_CHUNK_SIZE
    chunk_overlap = DEFAULT_CHUNK_OVERLAP
    tokenizer = lambda text: tiktoken.get_encoding("gpt2").encode(text, allowed_special={"<|endoftext|>"})

