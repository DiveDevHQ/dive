from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from dive.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNKING_TYPE, DEFAULT_QUERY_CHUNK_SIZE


class EmbeddingModel(BaseModel):
    chunking_type: str = DEFAULT_CHUNKING_TYPE
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    tokenizer: Any



class QueryDocument:
    id: str
    document: str
    metadata: Dict
    distance: float


class VectorQueryResult:
    query_documents: List[QueryDocument]
    summary: List[str]

    def __init__(self, query_documents: List[QueryDocument], summary:List[str]):
        self.query_documents=query_documents
        self.summary=summary