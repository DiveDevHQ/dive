from dive.storages.storage_context import StorageContext
from typing import Optional, List, Any, Dict
from dataclasses import dataclass
from langchain.schema import Document
from dive.constants import DEFAULT_QUERY_CHUNK_SIZE
from dive.util.power_method import degree_centrality_scores
from sentence_transformers import SentenceTransformer, util
import nltk
import numpy as np

@dataclass
class QueryContext:
    storage_context: StorageContext

    @classmethod
    def from_documents(
            cls,
            storage_context: Optional[StorageContext] = None,
            **kwargs: Any,
    ):
        if not storage_context:
            storage_context = StorageContext.from_defaults()

        return cls(storage_context=storage_context,
                   **kwargs, )

    def query(self, query: str, k: int = DEFAULT_QUERY_CHUNK_SIZE, filter: Optional[Dict[str, str]] = None) -> List[
        Document]:
        return self.storage_context.vector_store.similarity_search(query=query, k=k, filter=filter)

    def summarization(self, documents:[Document])->[]:
        chunks_text=''
        for d in documents:
            chunks_text += d.page_content + '\n'

        model = SentenceTransformer('all-MiniLM-L6-v2')

        sentences = nltk.sent_tokenize(chunks_text)
        sentences = [sentence.strip() for sentence in sentences]

        embeddings = model.encode(sentences, convert_to_tensor=True)

        cos_scores = util.cos_sim(embeddings, embeddings).numpy()

        centrality_scores = degree_centrality_scores(cos_scores, threshold=None)

        most_central_sentence_indices = np.argsort(-centrality_scores)
        summary_list = []
        for idx in most_central_sentence_indices[0:5]:
            summary_list.append(sentences[idx].strip())
        return summary_list