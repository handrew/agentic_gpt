"""Context class abstraction.

The Context class abstracts the details of the context from the agent. It
takes care of embedding the documents, indexing them, and retrieving
them, as well as the bookkeeping of the documents.
"""
from llama_index import Document
from llama_index import GPTVectorStoreIndex, GPTListIndex
from llama_index import ServiceContext, LLMPredictor
from langchain.chat_models import ChatOpenAI
from typing import List
from tqdm import tqdm

CHATGPT_KWARGS = {"temperature": 0, "model_name": "gpt-3.5-turbo"}


def init_index(docs, index_type="vector"):
    """Initialize each index with a different service context."""
    assert index_type in ("vector", "list")
    llm = LLMPredictor(llm=ChatOpenAI(**CHATGPT_KWARGS))
    service_context = ServiceContext.from_defaults(llm_predictor=llm)
    if index_type == "vector":
        index = GPTVectorStoreIndex.from_documents(
            docs, service_context=service_context
        )
    elif index_type == "list":
        index = GPTListIndex.from_documents(docs, service_context=service_context)

    return index


def summarize_documents(docs):
    """Given a list of documents, create a list of their summaries."""
    summaries = []
    indexes = []
    for doc in tqdm(docs, desc="Summarizing documents..."):
        index = init_index([doc], index_type="vector")
        query_engine = index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query("Summarize: ")
        summaries.append(response.response)
        indexes.append(index)
    return {"summaries": summaries, "indexes": indexes}


class Memory:
    """Initialize the memory with `documents`, a list of strings."""

    def __init__(self, documents: List[str]):
        self.documents = documents
        if documents:
            llama_docs = [Document(doc) for doc in documents]
            self.index = init_index(llama_docs)

    def add_document(self, document: str):
        """Add a document to the memory."""
        self.documents.append(document)
        raise NotImplemented("Figure out how to add a document to the index.")