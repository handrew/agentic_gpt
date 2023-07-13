from ..agent.utils.llm_providers import SUPPORTED_LANGUAGE_MODELS, get_completion


def ask_llm(prompt: str) -> str:
    """Ask the language model a question and return its answer.
    Wrapper around `get_completion`."""
    return get_completion(prompt)
