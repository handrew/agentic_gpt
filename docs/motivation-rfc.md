# Request for Comment

Nascent AGI architectures like BabyAGI and AutoGPT have captured a great deal of public interest by demonstrating LLMs' agentic capabilities and capacity for introspective step-by-step reasoning. As proofs-of-concept, they make great strides, but leave a few things wanting. This document is an attempt to sketch an architecture which builds upon and extends the conceptual foundations of the aforementioned products.

The primary contributions I would like to make are twofold:
1. Allowing an LLM to read from a corpus of information and write text according to that information.
2. Enabling more robust reproducibility and modularity.

## Design Requirements

A few attributes of the imagined architecture:
1. Must be modular and easily extensible (e.g., must be easy to swap out vector/data stores). See below usage.
2. Is ideally compatible and interoperable with multiple, GPT3+-quality models. Practically speaking this means that whatever prompts are used are ideally very short and ask the LLM for single-token answers (e.g., from a multiple choice set of options). In practice, I think that ChatGPT and GPT-4 (and perhaps Claude) are still the best models for this sort of task.
3. Must include mechanisms to receive and remember human feedback. A heavyweight (and undesirable approach) is to define a domain specific language which can be used to reproruce instructions.
4. Related to the above point, must be interpretable and deterministic so that users can have some guarantee of reusability. That is, the next time I run an agent flow, I can ideally just load in a set of natural language instructions that it generated from a previous run and it will run in an identical manner.
5. Must include some way for the agent to access a corpus of information, i.e., a "Memory" module. Accordingly, must allow the agent to take actions based on information in that memory (e.g., using information in its memory bank to fill out forms, or using information in its memory to reason about future actions to take).
6. Must be able to re-evaluate its plan after every step, e.g., maybe an OODA loop.
7. Must be easily debuggable, either by having a clean audit log of it's introspections and actions taken or otherwise.

## Initial Sketch

### Concepts
An initial concept ontology would include:
- `Agent`s are instantiated to acccomplish text objectives.
- `Action`s are interfaces to non-LLM capabilities that `Agent`s can take.
- `Memory`s are things that the `Agent` can remember and store that might be useful.
- `Task`s are things that need to be completed to accomplish an objective.
- `State` describes what is in the environment, giving the `Agent` clues about what to do next.

- Users instantiate `Agent`s.
    - `Agent`s generate and complete `Task`s using the `Action`s at their disposal and their `Memory`.
    - `Task`s are discrete objectives which can plausibly be achieved by using a `Action` and `Memory`.
    - `Agent`s can use `Action`s, which are exposed to `Agent`s via prompts like "You can use the following Actions: (A) Python interpreter (B) Google API" etc.
        - Users can define new `Action`s. The simplest architecture for a `Action` is a function, but you would likely want more shared state between the `Action` and the `Agent`.
    - `Agent`s can have a `Memory`. `Memory` files can either be structured or unstructured. If structured, they are machine readable and can be processed according to standard methods. If unstructured, then some form of retrieval must be implemented.
- `State` of the world exposed to the `Agent`, giving it information about its current environment.

The agent:
1. Comes up with a `Task` list to accomplish the goal.
2. Progressively completes `Task`s, taking account of the state of the world after each task is complete.
3. Continues until finished.

Anyone can build arbitrary `Action`s according to their APIs. They can be open-sourced or proprietary. Some default `Action`s might include: querying memory, asking user for feedback and clarity.


### Usage

Ideally all the user would have to do is define a set of `Action`s that they expose to the `Agent`, and the magic under the hood routes actions accordingly. I envision something like the below.

```python
agent = Agent(
    actions=[
        Action(
            name="google",
            function=google_search,
            function_signature="...",
            description="Can be used to search Google. Returns a JSON list of results."
h        ),
        Action(
            name="selenium_click",
            function=selenium_click,
            function_signature="selenium_click(element)",
            description="Used to click on an element in the Selenium instance."
        ),
        Action(
            name="selenium_type",
            function=selenium_type,
            function_signature="selenium_type(text)"
            description="Used to type something in the Selenium instance."
        ),
    ],
    memory=directory_of_files
)
goal = "Reserve me a spot at restaurant X at 7pm."
agent.run(goal)
```

which would set off a subroutine like:

1. Search Google for `restaurant X`.
2. Select the right restaurant link.
3. Select the `reserve` button.
4. ... etc

Because restaurants' ordering flow can differ dramatically, the `Agent` must be able to reconsider its objectives after every step given new information that it is presented with. Probably a built in `Action` would be to pause and ask for user feedback.
