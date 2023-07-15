"""AgenticGPT class."""
import sys
import json
import logging
import jinja2
from typing import Dict
from .action import Action
from .memory import Memory
from .errors import AgentError
from .utils.llm_providers import SUPPORTED_LANGUAGE_MODELS, get_completion
from .utils.indexing import retrieve_segment_of_text
from ..actions.ai_functions import ask_llm, CLARIFY_FUNCTION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SUPPORTED_EMBEDDING_MODELS = ["text-embedding-ada-002", "sentencetransformers"]

"""Define default actions for the agent."""

DONE_FUNCTION = "declare_done"


def declare_done():
    """Declare that you are done with your objective."""


ASK_LLM_FUNCTION = "ask_ai"


"""Prompt to be called at every time step for the agent."""

AGENT_PROMPT = """You are an AI agent given the following objective: "{objective}"

=============================================================
You can take the following actions. args are denoted as (arg1: str, arg2: int), and kwargs are denoted as (kwarg1="default_value").
{actions}

=============================================================
These files / variables are available to you in your memory:
{files}

=============================================================
You have taken the following actions so far. Try not to repeat yourself unless necessary.
{actions_taken}

=============================================================
Here is some potentially helpful context about your environment:
{context}

=============================================================
What is your next action? Please only choose ONE action at a time. Answer with a JSON with the below form which can be loaded with Python `json.loads`. Example:
{example_response_format}

"""

EXAMPLE_RESPONSE_FORMAT = """
{
    "thoughts": {
        "text": "<your thought>",
        "reasoning": "<your reasoning>"
    },
    "command": {
        "action": "selected_action_name",
        "args": ["arg1", "arg2"],
        "kwargs": {
            "kwarg1": "kwarg1_value",
            "kwarg2": "kwarg2_value"
        }
    }
}

Where you can use curly braces to denote a variable from memory, e.g., "args": ["{{file_name}}", "arg2"]. To get a variable from memory, you have to reference it verbatim from the list of files above.
You should provide thoughts and reasoning for your action.

"""


class AgenticGPT:
    def __init__(
        self,
        objective,
        actions_available=[],
        memory_dict={},
        model="gpt-3.5-turbo-16k",
        embedding_model="text-embedding-ada-002",
        ask_user_fn=None,
        max_steps=100,
        verbose=False,
    ):
        """Initialize the agent. An agent is given the following args:
        @param objective: The objective of the agent.
        @param actions_available: a list of `Action`s which it can use to achieve the objective
        @param memory_dict: a dict of name => documents which it loads into its `Memory`
        @param model: a string that specifies the language model to use
        @param embedding_model: a string that specifies the embedding model to use
        @param ask_user_fn: a function that asks the user a question and returns their answer
        @param max_steps: an integer that specifies the maximum number of steps the agent can take
        @param verbose: a boolean that specifies whether to print out the prompt at every step

        The agent then maintains:
        - a list of actions that it has taken so far
        - a `Memory` which it uses to keep track of the files it has in its memory
        - a context which it can use to keep track of the environment it is in
        """
        supported_models = list(SUPPORTED_LANGUAGE_MODELS.keys())
        assert (
            model in supported_models
        ), f"Model {model} not supported. Supported models are {supported_models}."
        self.model = model
        self.embedding_model = embedding_model
        self.ask_user_fn = ask_user_fn
        # self.chat_mode = chat_mode

        # Set the variables given to the agent.
        self.objective = objective
        self.max_steps = max_steps
        self.verbose = verbose
        self.memory = Memory(memory_dict, embedding_model=self.embedding_model)
        self.actions_available = self.__init_actions_available(actions_available)

        self.actions_taken = []
        self.context = ""

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
                description="Query the Memory to synthesize an answer from all documents. Useful for summarization and retrieval using information from all docs.",
                function=self.memory.query_all,
            ),
            Action(
                name="query_one_document_in_memory",
                description="Query the Memory to synthesize an answer from one document. Useful for summarization and retrieval using information from a single doc.",
                function=self.memory.query_one,
            ),
        ]

        default_actions = [
            Action(
                name=ASK_LLM_FUNCTION,
                description='Given a prompt, submit to a language model and return its answer. For instance, "write me a poem about a squirrel" would return a string response with a poem about a squirrel.',
                function=ask_llm,
            ),
            Action(
                name=DONE_FUNCTION,
                description="Declare that you are done with your objective.",
                function=declare_done,
            ),
        ]

        if self.ask_user_fn:
            default_actions.insert(
                0,
                Action(
                    name="ask_user_to_clarify",
                    description="Ask the user to clarify their instructions. Used when the information in the context is not enough to proceed to the next step.",
                    function=self.ask_user_fn,
                ),
            )
            
        default_actions = default_actions + memory_actions
        self.actions_available = given_actions + default_actions

        # Check that the actions_available don't have name collisions with the
        # default actions.
        for action in given_actions:
            assert action.name not in [
                action.name for action in default_actions
            ], f"Action {action.name} collides with a default action."

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

        actions = []
        for action in self.actions_taken:
            action_bullet_str = "- " + action["command"]["action"]
            if "args" in action["command"]:
                action_bullet_str += " with args " + str(action["command"]["args"])
            if "kwargs" in action["command"]:
                action_bullet_str += " and kwargs " + str(action["command"]["kwargs"])
            actions.append(action_bullet_str)

        actions = "\n".join(actions)
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
        max_length = SUPPORTED_LANGUAGE_MODELS[self.model]["max_length"]
        if len(self.context) > max_length:
            logger.info("Context too long. Truncating.")
            query = (
                "Find the part of the context which most helps me with objective: "
                + self.objective
            )
            source = retrieve_segment_of_text(
                query,
                self.context,
                model=self.model,
                embedding_model=self.embedding_model,
            )
            return source
        return self.context

    def from_saved_actions(self, path: str):
        """Load the agent from a list of actions taken."""
        with open(path, "r") as f:
            saved_dict = json.load(f)
            self.objective = saved_dict["objective"]
            self.actions_taken = saved_dict["actions"]
            print("Agent objective: ", self.objective)
            print(f"Loaded f{len(self.actions_taken)} actions.")

    def replay(self):
        """Replay the actions taken by the agent."""
        for action in self.actions_taken:
            self.process_response(action)

    def save_actions_taken(self, path: str):
        """Save the actions taken by the agent to a file."""
        with open(path, "w+") as f:
            # Iterate through the actions taken and remove the ones where
            # we are asking the user to clarify.
            actions_taken = []
            for action in self.actions_taken:
                if action["command"]["action"] != CLARIFY_FUNCTION:
                    actions_taken.append(action)

            saved_dict = {
                "objective": self.objective,
                "actions": actions_taken,
            }
            json.dump(saved_dict, f, indent=2)

    def __template_from_memory(self, variable_string):
        """Get variable string from memory."""
        if not isinstance(variable_string, str):
            return variable_string
        environment = jinja2.Environment(loader=jinja2.DictLoader({}))
        template = environment.from_string(variable_string)
        result = template.render(self.memory.documents)
        if result != variable_string:  # Probably a dumb way to check...
            if not result:
                raise AgentError(
                    f"{variable_string} is not a valid file in memory. Please try again."
                )
            # If it's not the same, then we know that it was templated, and
            # can consequently "eval" the result.
            result = eval(result)
        return result

    def __name_action_returned_variable(self, action_name):
        """Given an `action_name`, check if it has been run before and if so,
        give it a number to disambiguate it in the agent's memory."""
        # Iterate through the Memory variables.
        suffix = 1
        for key, value in self.memory.documents.items():
            if action_name in key:
                # If we find a match, then we know that this action has been
                # run before, and we can give it a number.
                suffix += 1
        return action_name + "_result_" + str(suffix)

    def process_response(self, response_obj) -> Dict:
        chosen_action = response_obj["command"]["action"]
        action_args = []
        if "args" in response_obj["command"]:
            action_args = response_obj["command"]["args"]
            action_args = [self.__template_from_memory(arg) for arg in action_args]

        action_kwargs = {}
        if "kwargs" in response_obj["command"]:
            action_kwargs = response_obj["command"]["kwargs"]
            action_kwargs = {
                key: self.__template_from_memory(value)
                for key, value in action_kwargs.items()
            }

        # Print out reasoning.
        logger.info("\n\nThoughts: %s", response_obj["thoughts"]["text"])
        logger.info("Reasoning: %s", response_obj["thoughts"]["reasoning"])
        logger.info("Chosen action: %s", chosen_action)
        if self.verbose:
            if action_args:
                logger.info("Action args: %s", action_args)
            if action_kwargs:
                logger.info("Action kwargs: %s", action_kwargs)

        action_result = None
        for action in self.actions_available:
            if action.name == chosen_action:
                action_result = action.execute(*action_args, **action_kwargs)
                self.context += "\n\nCommand " + chosen_action + " executed."
                variable = self.__name_action_returned_variable(action.name)
                try:
                    serialized_result = json.dumps(action_result)
                except TypeError:
                    raise TypeError(
                        f"Result from action {chosen_action} is not JSON serializable. Make sure that the `Action` you wrote returns a JSON serializable object."
                    )
                
                if action_result is not None:
                    self.memory.add_document(variable, serialized_result)
                    self.context += "\nResult is stored in Memory as: " + variable

                logger.info(
                    f"Completed action {chosen_action}. Result: {action_result}"
                )
                break

        return {"agent_response": response_obj, "action_result": action_result}

    def run(self):
        """Runs the agent."""

        action = None
        steps = 0
        while action is not DONE_FUNCTION and steps < self.max_steps:
            # Format the prompt and get a completion
            prompt = AGENT_PROMPT.format(
                objective=self.objective,
                actions=self.__get_available_actions(),
                actions_taken=self.__get_actions_taken(),
                files=self.__get_memory_string(),
                context=self.__get_context(),
                example_response_format=EXAMPLE_RESPONSE_FORMAT,
            )
            completion = get_completion(prompt, model=self.model)
            steps += 1

            logger.info(f"Taken steps {steps} of maximum {self.max_steps}.")

            if self.verbose:
                logger.info("PROMPT: \n" + prompt)
                logger.info("AGENT RESPONSE: " + completion)

            # Try loading the completion as JSON.
            try:
                response_obj = json.loads(completion)
            except json.decoder.JSONDecodeError as exc:
                logger.info(prompt)
                logger.info(
                    "!!! INVALID JSON RESPONSE. Prompt shown above, completion below."
                )
                logger.info(completion)
                # Construct new context with error message.
                self.context = self.context + "\nYou gave the answer: " + completion
                self.context = (
                    self.context + "\nCould not decode answer as JSON: " + str(exc)
                )
                self.context = self.context + "\nPlease try again."
                continue

            # TODO eventually figure this out
            # if self.chat_mode:
            #     message = "My thoughts are that: " + response_obj["thoughts"]["text"]
            #     message += "\nMy reasoning is: " + response_obj["reasoning"]["reasoning"]
            #     message += "\nDo you think this is right?"
            #     self.ask_user_fn(message)

            # Process and execute the response.
            try:
                processed = self.process_response(response_obj)
            except AgentError as exc:
                # Construct new context with error message.
                new_context = f"\nJust tried running action "
                new_context += "`" + response_obj["command"]["action"] + "`"
                if "args" in response_obj["command"]:
                    new_context += " given args " + str(response_obj["command"]["args"])
                if "kwargs" in response_obj["command"]:
                    new_context += " and given kwargs " + str(
                        response_obj["command"]["kwargs"]
                    )
                new_context += "\nIt threw an error: " + str(exc)
                self.context = new_context
                continue

            # Some housekeeping.
            self.actions_taken.append(processed["agent_response"])
            response_obj = processed["agent_response"]
            action_result = processed["action_result"]
            action = response_obj["command"]["action"]

            if action == DONE_FUNCTION:
                logger.info("You have completed your objective!")
                return
