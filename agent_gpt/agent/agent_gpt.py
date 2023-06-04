"""AgentGPT class."""
import json
import logging
from typing import Dict
from .action import Action
from .memory import Memory
from .utils.openai import get_completion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""Define default actions for the agent."""

def ask_user_to_clarify(question: str) -> str:
    """Ask the user a question and return their answer."""
    user_response = input(question + " ")
    context = f"- Asked the question: {question}... Received response: {user_response}"
    return {"context": context}


def declare_done():
    """Declare that you are done with your objective."""


DONE_FUNCTION = "declare_done"

DEFAULT_ACTIONS = [
    Action(
        name="ask_user_to_clarify",
        description="Ask the user to clarify their instructions. Used when the information in the context is not enough to proceed to the next step.",
        function=ask_user_to_clarify,
    ),
    Action(
        name=DONE_FUNCTION,
        description="Declare that you are done with your objective.",
        function=declare_done,
    ),
]

"""Prompt to be called at every time step for the agent."""

AGENT_PROMPT = """You are an agent given the following objective: "{objective}"

=============================================================
You can take the following actions:
{actions}

=============================================================
These files are available to you in your memory:
{files}

=============================================================
You have taken the following actions so far:
{actions_taken}

=============================================================
Here is some potentially helpful context about your environment:
{context}

=============================================================
What is your next action? Answer with a JSON with the below form which can be loaded with Python `json.loads`. Example:
{example_response_format}

"""

EXAMPLE_RESPONSE_FORMAT = """
{
    "thoughts": {
        "text": "<your thought>",
        "reasoning": "<your reasoning>"
    },
    command: {
        "action": "selected_action_name",
        "args": ["arg1", "arg2"],
        "kwargs": {
            "kwarg1": "kwarg1_value",
            "kwarg2": "kwarg2_value"
        }
    }
}
"""


class AgentGPT:
    def __init__(
        self, objective, actions_available=[], memory_dict={}, max_steps=100, verbose=True,
    ):
        """Initialize the agent. An agent is given the following args:
        @param objective: The objective of the agent.
        @param actions_available: a list of `Action`s which it can use to achieve the objective
        @param memory_dir: a directory of documents which it loads into its `Memory`
        @param max_steps: an integer that specifies the maximum number of steps the agent can take
        @param verbose: a boolean that specifies whether to print out the prompt at every step

        The agent then maintains:
        - a list of actions that it has taken so far
        - a `memory_dict` which it uses to keep track of the files it has in its memory
        """
        # Set the variables given to the agent.
        self.objective = objective
        self.max_steps = max_steps
        self.verbose = verbose
        self.memory = Memory(memory_dict)
        self.actions_available = self.__init_actions_available(actions_available)

        self.actions_taken = []
        self.context = None

    def __init_actions_available(self, given_actions):
        """Initialize the actions available to the agent."""
        # Add the Memory actions to the agent.
        memory_actions = [
            Action(
                name="add_document_to_memory",
                description="Add document to the agent's memory.",
                function=self.memory.add_document,
            ),
            Action(
                name="query_all_documents_in_memory",
                description="Query the Memory to synthesize an answer from all documents.",
                function=self.memory.query_all,
            ),
            Action(
                name="query_one_document_in_memory",
                description="Query the Memory to synthesize an answer from one document.",
                function=self.memory.query_one,
            ),
        ]

        default_actions = DEFAULT_ACTIONS + memory_actions
        self.actions_available = given_actions + default_actions

        # Check that the actions_available don't have name collisions with the
        # default actions.
        for action in given_actions:
            assert (
                action.name not in [action.name for action in default_actions]
            ), f"Action {action.name} collides with a default action."
        
        return self.actions_available

    def __get_available_actions(self) -> str:
        """Get a string to inject into the prompt telling the agent what
        actions it can take."""
        actions = "\n".join(
            ["- " + action.to_string() for action in self.actions_available]
        )
        return actions

    def __get_actions_taken(self) -> str:
        """Get a string to inject into the prompt telling the agent what
        actions it has taken so far."""
        actions = "\n".join(
            [
                "- "
                + action["command"]["action"]
                + " with args "
                + str(action["command"]["args"])
                + " and kwargs "
                + str(action["command"]["kwargs"])
                for action in self.actions_taken
            ]
        )
        if actions.strip():
            return actions
        else:
            return "None."

    def __get_memory_string(self) -> str:
        """Get a string to inject into the prompt telling the agent what
        files it has in its memory."""
        return self.memory.to_prompt_string()

    def __get_context(self) -> str:
        """Get a string to inject into the prompt telling the agent what
        the state of the world is."""
        return self.context

    def process_response(self, response: str) -> Dict:
        try:
            response_obj = json.loads(response)
        except json.decoder.JSONDecodeError:
            raise ValueError("Response is not valid JSON.")

        chosen_action = response_obj["command"]["action"]
        action_args = response_obj["command"]["args"]
        action_kwargs = response_obj["command"]["kwargs"]

        logger.info("Chosen action: %s", chosen_action)
        logger.info("Action args: %s", action_args)
        logger.info("Action kwargs: %s", action_kwargs)

        action_result = None
        for action in self.actions_available:
            if action.name == chosen_action:
                action_result = action.execute(*action_args, **action_kwargs)
                if isinstance(action_result, dict) and "context" in action_result:
                    self.context = action_result["context"]
                break

        self.actions_taken.append(response_obj)
        return {"agent_response": response_obj, "action_result": action_result}

    def run(self):
        """Runs the agent."""

        action = None
        while action is not DONE_FUNCTION and len(self.actions_taken) < self.max_steps:
            prompt = AGENT_PROMPT.format(
                objective=self.objective,
                actions=self.__get_available_actions(),
                actions_taken=self.__get_actions_taken(),
                files=self.__get_memory_string(),
                context=self.__get_context(),
                example_response_format=EXAMPLE_RESPONSE_FORMAT,
            )
            if self.verbose:
                print("\n" + "=" * 80)
                print("AGENT PROMPT:")
                print(prompt)

            completion = get_completion(prompt)

            try:
                processed = self.process_response(completion)
            except:
                new_context = f"\nThere was an error running the action {action.name}. Your thoughts and answer were: "
                new_context += completion
                self.context += new_context
                print(new_context)
                continue

            response_obj = processed["agent_response"]
            action_result = processed["action_result"]
            action = response_obj["command"]["action"]

            if action == DONE_FUNCTION:
                print("You have completed your objective!")
                return
