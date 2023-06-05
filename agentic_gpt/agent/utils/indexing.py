"""Helper functions for Llama Index."""
from llama_index import GPTVectorStoreIndex, GPTListIndex
from llama_index import ServiceContext, LLMPredictor
from langchain.chat_models import ChatOpenAI
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
