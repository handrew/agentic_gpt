"""Example of using AgenticGPT to make a folder on the filesystem.
Also demonstrates how to ask the user for input and use it in the agent's
thoughts."""
from agentic_gpt import AgenticGPT
from agentic_gpt import Action
from agentic_gpt.actions.requests import get as http_get
from agentic_gpt.actions.filesystem import write as file_write


if __name__ == "__main__":
    actions = [
        Action(
            name="get_request",
            description="Make a get request to the url.",
            function=http_get,
        ),
        Action(
            name="file_write",
            description="Write to file on file system.",
            function=file_write,
        ),
    ]
    agent = AgenticGPT(
        "Make a get request to https://www.example.com/ and save the response to a file called example.txt.",
        actions_available=actions,
        verbose=True,
    )
    agent.run()
