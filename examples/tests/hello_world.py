"""Simplest example of how to use the AgenticGPT class. Exposes a single action
to the agent, which is to say hi to the user."""

from agentic_gpt.agent import AgenticGPT
from agentic_gpt.agent.action import Action


def say_hi():
    print("Hi!")


if __name__ == "__main__":
    actions = [
        Action(name="say_hi", description="Say hi to the user.", function=say_hi)
    ]
    agent = AgenticGPT("Say hello to the user, then exit!", actions_available=actions)
    agent.run()
