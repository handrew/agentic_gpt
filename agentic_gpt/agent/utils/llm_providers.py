"""OpenAI utils."""
import time
import openai

OPENAI_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
]

SUPPORTED_LANGUAGE_MODELS = OPENAI_MODELS


def get_completion(
    prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=1024, stop=["```"]    
):
    assert model in SUPPORTED_LANGUAGE_MODELS, f"Model {model} not supported. Supported models: {SUPPORTED_LANGUAGE_MODELS}"

    if model in OPENAI_MODELS:
        try:
            return openai_call(
                prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
        except openai.error.InvalidRequestError as exc:
            return {"error": str(exc)}


def openai_call(
    prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=1024, stop=["```"]
):
    """Wrapper over OpenAI's completion API."""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            temperature=temperature,
            stop=stop,
        )
        text = response["choices"][0]["message"]["content"]
    except (
        openai.error.RateLimitError,
        openai.error.APIError,
        openai.error.Timeout,
        openai.error.APIConnectionError,
    ) as exc:
        print(exc)
        print("Error from OpenAI's API. Sleeping for a few seconds.")
        time.sleep(5)
        text = get_completion(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )

    return text
