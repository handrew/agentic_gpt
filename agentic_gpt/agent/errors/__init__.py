"""Custom error classes for the agent."""


class AgentError(Exception):
    """General class of exceptions which denote an error in the agent, rather
    than an error in the code. This means that the agent should retry its last
    decision."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)
