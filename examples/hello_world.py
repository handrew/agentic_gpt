"""Simplest example of how to use the AgentGPT class. Exposes a single action
to the agent, which is to say hi to the user."""

from agent_gpt.agent import AgentGPT
from agent_gpt.agent.action import Action


def say_hi():
    print("Hi!")


if __name__ == "__main__":
    actions = [
        Action(name="say_hi", description="Say hi to the user.", function=say_hi)
    ]
    agent = AgentGPT("Say hello to the user!", actions_available=actions)
    agent.run()
