from agent import GoalAgent
from agent.action import Action


def say_hi():
    print("Hi!")


if __name__ == "__main__":
    actions = [
        Action(name="say_hi", description="Say hi to the user.", function=say_hi)
    ]
    agent = GoalAgent("Say hello to the user!", actions_available=actions)
    agent.run()
