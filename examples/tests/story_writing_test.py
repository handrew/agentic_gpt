"""Example of using AgenticGPT to write a story."""
from agentic_gpt import AgenticGPT
from agentic_gpt import Action
from agentic_gpt.actions.requests import get as http_get
from agentic_gpt.actions.filesystem import write as file_write


if __name__ == "__main__":
    actions = [
        Action(
            name="file_write",
            description="Write to file on file system.",
            function=file_write,
        )
    ]
    agent = AgenticGPT(
        "Come up with a Hero's Journey story plotline, flesh it out, and write it to a text file called story.txt",
        actions_available=actions,
    )
    agent.run()
