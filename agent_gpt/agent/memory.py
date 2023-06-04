"""Context class abstraction.

The Context class abstracts the details of the context from the agent. It
takes care of embedding the documents, indexing them, and retrieving
them, as well as the bookkeeping of the documents.
"""
from llama_index import Document
from llama_index import GPTVectorStoreIndex, GPTListIndex
from llama_index import ServiceContext, LLMPredictor
from langchain.chat_models import ChatOpenAI
from typing import Dict
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
    for doc in docs:
        index = init_index([doc], index_type="vector")
        query_engine = index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query("Summarize in a few sentences: ")
        summaries.append(response.response)
        indexes.append(index)
    return {"summaries": summaries, "indexes": indexes}


class Memory:
    """Initialize the memory with `documents`, a list of strings."""

    def __init__(self, documents: Dict[str, str] = {}):
        """A Memory object is initialized with a list of documents.
        It keeps track of a few things about the documents:
        - `self.documents`: The documents themselves, stored in `name`: `text` pairs.
        - `self.summaries`: The summaries of the documents.
        - `self.doc_indexes`: The indexes of the documents.
        - `self.router_index`: A router index over the summaries.
        """
        self.documents = documents
        if documents:
            llama_docs = [Document(text) for name, text in documents.items()]
            summary_obj = summarize_documents(llama_docs)
            self.summaries = summary_obj["summaries"]
            self.doc_indexes = summary_obj["indexes"]
            self.router_index = init_index([Document(summary) for summary in self.summaries])
        else:
            self.summaries = []
            self.doc_indexes = []
            self.router_index = None

    def is_empty(self):
        """Returns True if the memory is empty."""
        return not self.documents

    def to_prompt_string(self):
        """Print the memory as a string which can be injected into a prompt.
        
        The format is:
        <document 1 name>: <document 1 summary>
        <document 2 name>: <document 2 summary>
        ...
        """
        prompt = ""
        for name, summary in zip(self.documents.keys(), self.summaries):
            prompt += f"{name}: {summary}\n"
        return prompt

    def add_document(self, document: str):
        """Add a document to the memory."""
        self.documents.append(document)
        llama_doc = Document(document)
        summary_obj = summarize_documents([llama_doc])
        self.summaries.append(summary_obj["summaries"][0])
        self.doc_indexes.append(summary_obj["indexes"][0])
        self.router_index.insert(Document(self.summaries[-1]))

    def query_all(self, query: str):
        """Query and get a response synthesized from all of the docs."""
        doc_responses = []
        for index in self.doc_indexes:
            query_engine = index.as_query_engine(response_mode="tree_summarize")
            response = query_engine.query(query)
            text_response = response.response
            doc_responses.append(text_response)
        
        list_index = init_index(doc_responses, index_type="list")
        query_engine = list_index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query(query)
        context = f"The answer returned from memory is: {response.response}"
        return {"answer": response.response, "context": context}
    
    def query_one(self, query: str):
        """Query and get a response synthesized from one of the docs."""
        query_engine = self.router_index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query(query)
        context = f"The answer returned from memory is: {response.response}"
        return {"answer": response.response, "context": context}