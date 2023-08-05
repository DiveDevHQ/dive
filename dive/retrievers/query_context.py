from dive.storages.storage_context import StorageContext
from dive.indices.service_context import ServiceContext
from typing import Optional, List, Any, Dict
from dataclasses import dataclass
from langchain.schema import Document
from dive.constants import DEFAULT_QUERY_CHUNK_SIZE
from dive.util.power_method import sentence_transformer_summarize,sentence_transformer_question_answer
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate


@dataclass
class QueryContext:
    storage_context: StorageContext
    service_context: ServiceContext

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

    def get(self, filter: Dict[str, str]):
        try:
            return self.storage_context.vector_store.get_data(filter=filter)
        except KeyError:
            raise ValueError(
                "Could not find the index"
            )


    def summarization(self, documents: [Document]) -> str:

        chunks_text = ''
        for d in documents:
            chunks_text += d.page_content + '\n'

        if self.service_context.instruction:
            map_prompt = f'{self.service_context.instruction}' """
            "{text}"
            CONCISE SUMMARY:
            """
            map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

        if not self.service_context.llm:
            return sentence_transformer_summarize(chunks_text)
        else:
            if self.service_context.instruction:
                chain = load_summarize_chain(llm=self.service_context.llm, chain_type="map_reduce", verbose=True,
                                             map_prompt=map_prompt_template)
            else:
                chain = load_summarize_chain(llm=self.service_context.llm, chain_type="map_reduce")

        return chain.run(documents)

    def question_answer(self, query: str, documents: [Document]):
        if self.service_context.instruction:
            prompt = f'{self.service_context.instruction}' """
            "{context}"
            Question: {question}:
            """
            prompt_template = PromptTemplate(template=prompt, input_variables=["context", "question"])

        if not self.service_context.llm:
            chunks_text = ''
            for d in documents:
                chunks_text += d.page_content + '\n'
            return sentence_transformer_question_answer(query,chunks_text)
        else:
            if self.service_context.instruction:
                chain = load_qa_chain(llm=self.service_context.llm, chain_type="stuff", verbose=True,
                                      prompt=prompt_template)
            else:
                chain = load_qa_chain(llm=self.service_context.llm, chain_type="stuff")

            return chain.run(input_documents=documents, question=query)
