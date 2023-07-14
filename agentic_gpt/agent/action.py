"""Action class abstraction."""
from inspect import signature
from typing import Callable
from .errors import AgentError


class Action:
    """Action class takes a name, a description, a function that it executes.

    A well-defined action will return a textual description of the state
    of the world so that the agent can understand what to do next."""

    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function

    def to_string(self):
        """Return a string representation of the action, including the
        function signature."""
        func_signature = ", ".join(
            [str(param) for param in signature(self.function).parameters.values()]
        )
        return (
            f"`{self.name}`, called with params ({func_signature}): {self.description}"
        )

    def execute(self, *args):
        """Execute the action with the given arguments."""
        try:
            return self.function(*args)
        except Exception as e:
            raise AgentError("Error executing action. Error message: " + str(e))
