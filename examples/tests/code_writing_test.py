"""Example of using AgenticGPT to write some code."""
from agentic_gpt import AgenticGPT
from agentic_gpt import Action
from agentic_gpt.actions.requests import get as http_get
from agentic_gpt.actions.filesystem import write as file_write


if __name__ == "__main__":
    actions = [
        Action(
            name="file_write", description="Write to file on file system.", function=file_write
        )
    ]
    agent = AgenticGPT(
        "Write a Python function to print out the first 100 numbers in the Fibonacci sequence.",
        actions_available=actions,
    )
    agent.run()
