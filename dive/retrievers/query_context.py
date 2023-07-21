from dive.storages.storage_context import StorageContext
from dive.indices.service_context import ServiceContext
from typing import Optional, List, Any, Dict
from dataclasses import dataclass
from langchain.schema import Document
from dive.constants import DEFAULT_QUERY_CHUNK_SIZE
from dive.util.power_method import degree_centrality_scores
from sentence_transformers import SentenceTransformer, util
import nltk
nltk.download('punkt')
import numpy as np
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings.base import Embeddings

@dataclass
class QueryContext:
    storage_context: StorageContext
    service_context:ServiceContext

    @classmethod
    def from_defaults(
            cls,
            storage_context: Optional[StorageContext] = None,
            service_context: Optional[ServiceContext] = None,
            **kwargs: Any,
    ):

        if not service_context:
            service_context = ServiceContext.from_defaults()

        if not storage_context:
            storage_context = StorageContext.from_defaults(embedding_function=service_context.embeddings)

        return cls(storage_context=storage_context,
                   service_context=service_context,
                   **kwargs, )

    def query(self, query: str, k: int = DEFAULT_QUERY_CHUNK_SIZE, filter: Optional[Dict[str, str]] = None) -> List[
        Document]:

        try:
            return self.storage_context.vector_store.similarity_search(query=query, k=k, filter=filter)
        except KeyError:
            raise ValueError(
                "Could not find the index"
            )


    def summarization(self, documents: [Document]) -> str:
        chunks_text = ''
        for d in documents:
            chunks_text += d.page_content + '\n'

        if not self.service_context.llm:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            sentences = nltk.sent_tokenize(chunks_text)
            sentences = [sentence.strip() for sentence in sentences]
            embeddings = model.encode(sentences, convert_to_tensor=True)
            cos_scores = util.cos_sim(embeddings, embeddings).numpy()
            centrality_scores = degree_centrality_scores(cos_scores, threshold=None)
            most_central_sentence_indices = np.argsort(-centrality_scores)
            summary_text = ""
            for idx in most_central_sentence_indices[0:5]:
                summary_text += sentences[idx].strip() + '\n'
            return summary_text

        else:
            chain = load_summarize_chain(llm=self.service_context.llm, chain_type="map_reduce")
            return chain.run(documents)
