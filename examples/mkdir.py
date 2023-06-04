"""Example of using AgenticGPT to make a folder on the filesystem.
Also demonstrates how to ask the user for input and use it in the agent's
thoughts."""
import os
from agentic_gpt.agent import AgenticGPT
from agentic_gpt.agent.action import Action


def mkdir(folder):
    os.mkdir(folder)


if __name__ == "__main__":
    actions = [
        Action(
            name="mkdir", description="Make a folder on the filesystem.", function=mkdir
        )
    ]
    agent = AgenticGPT(
        "Ask the user what folder they want to make and make it for them.",
        actions_available=actions,
    )
    agent.run()
    agent.save_actions_taken("mkdir.json")