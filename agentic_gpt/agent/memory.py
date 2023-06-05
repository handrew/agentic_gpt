"""Context class abstraction.

The Context class abstracts the details of the context from the agent. It
takes care of embedding the documents, indexing them, and retrieving
them, as well as the bookkeeping of the documents.
"""
from llama_index import Document
from typing import Dict
from .utils.indexing import init_index, summarize_documents, retrieve_segment_of_text


class Memory:
    """Initialize the memory with `documents`, a list of strings."""

    def __init__(
        self,
        documents: Dict[str, str] = {},
        model="gpt-3.5-turbo",
        embedding_model=None,
    ):
        """A Memory object is initialized with a list of documents.
        It keeps track of a few things about the documents:
        - `self.documents`: The documents themselves, stored in `name`: `text` pairs.
        - `self.document_store`: A dict of `name`: to {"text": `text`, "summary": `summary`, "index": `index`}
        - `self.vector_index`: A vector index over all of the texts.
        """
        self.model = model
        self.embedding_model = embedding_model
        self.documents = documents
        if documents:
            name_and_text = [(name, text) for name, text in documents.items()]

            llama_docs = [Document(text) for name, text in name_and_text]
            summary_obj = summarize_documents(
                llama_docs, model=self.model, embedding_model=self.embedding_model
            )

            self.document_store = {
                name: {"text": text, "summary": summary, "index": index}
                for (name, text), summary, index in zip(
                    name_and_text, summary_obj["summaries"], summary_obj["indexes"]
                )
            }
            self.router_index = init_index(
                [Document(text) for text in documents.values()],
                model=self.model,
                embedding_model=self.embedding_model,
            )
        else:
            self.document_store = {}
            self.router_index = None

    def is_empty(self):
        """Returns True if the memory is empty."""
        return not self.documents

    def to_prompt_string(self):
        """Print the memory as a string which can be injected into a prompt.

        The format is:
        - <document 1 name>:
            Summary: <document 1 summary>
        - <document 2 name>:
            Summary: <document 2 summary>
        ...
        """
        prompt = ""
        summaries = [
            (name, self.document_store[name]["summary"])
            for name in self.documents.keys()
        ]
        for name, summary in summaries:
            prompt += f"- {name}:\n"
            prompt += f"    Summary: {summary}\n"
        return prompt

    def get_document(self, name, query="Return the text verbatim.", max_length=5000):
        """Return a document's text verbatim."""
        text = self.documents[name]
        if len(text) > max_length:
            return retrieve_segment_of_text(
                query, text, model=self.model, embedding_model=self.embedding_model
            )
        return text

    def add_document(self, name: str, document: str):
        """Add a document to the memory."""
        self.documents[name] = document
        llama_doc = Document(document)
        summary_obj = summarize_documents([llama_doc])
        summary = summary_obj["summaries"][0]
        index = summary_obj["indexes"][0]
        self.document_store[name] = {
            "text": document,
            "summary": summary,
            "index": index,
        }
        self.router_index.insert(Document(document))

    def query_all(self, query):
        """Query and get a response synthesized from all of the docs."""
        doc_responses = []
        indexes = [self.document_store[name]["index"] for name in self.documents.keys()]
        for index in indexes:
            query_engine = index.as_query_engine(response_mode="tree_summarize")
            response = query_engine.query(query)
            text_response = response.response
            doc_responses.append(text_response)

        list_index = init_index(doc_responses, index_type="list")
        query_engine = list_index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query(query)
        context = f"The answer returned from memory is: {response.response}"
        return {"answer": response.response, "context": context}

    def query_one(self, query):
        """Query and get a response synthesized from one of the docs."""
        query_engine = self.router_index.as_query_engine()
        response = query_engine.query(query)
        context = f"The answer returned from memory is: {response.response}"
        return {"answer": response.response, "context": context}
