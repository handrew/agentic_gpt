import os
from agent import GoalAgent
from agent.action import Action


def mkdir(folder):
    os.mkdir(folder)


if __name__ == "__main__":
    actions = [
        Action(
            name="mkdir", description="Make a folder on the filesystem.", function=mkdir
        )
    ]
    agent = GoalAgent(
        "Ask the user what folder they want to make and make it for them.",
        actions_available=actions,
    )
    agent.run()
