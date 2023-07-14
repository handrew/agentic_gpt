from ..agent.utils.llm_providers import SUPPORTED_LANGUAGE_MODELS, get_completion


def ask_llm(prompt: str) -> str:
    """Ask the language model a question and return its answer.
    Wrapper around `get_completion`."""
    return get_completion(prompt)


CLARIFY_FUNCTION = "ask_user_to_clarify"


def ask_user_to_clarify(question: str) -> str:
    """Ask the user a question and return their answer."""
    user_response = input(question + " ")
    context = (
        f'- Asked the question: "{question}"... Received response: "{user_response}"'
    )
    return {"context": context}
