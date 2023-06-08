# 🪽 AgenticGPT

Nascent AGI architectures like BabyAGI and AutoGPT have captured a great deal of public interest by demonstrating LLMs' agentic capabilities and capacity for introspective step-by-step reasoning. As proofs-of-concept, they make great strides, but a few things wanting.

The primary contributions I would like to make are twofold:
1. Allowing an LLM to read from a corpus of information and act according to that information.
2. Enabling more robust reproducibility and modularity.

Conceptually, the user provides the `AgenticGPT` agent with an objective and a list of `Action`s that it can take, and then the agent figures out the rest, and asks the user for clarification when it needs help.

## 🎬 Getting Started
### 🔨 Installation
1. `pip install -r requirements.txt`
2. Set up your OpenAI API key as the `OPENAI_API_KEY` environment variable.

### 🦭 Usage
AgenticGPT can be instantiated with the following signature:
```python
AgenticGPT(
    objective,
    actions_available=[],
    memory_dict={},
    model="gpt-3.5-turbo",
    embedding_model="text-embedding-ada-002",
    ask_user_fn=ask_user_to_clarify,
    max_steps=100,
    verbose=False,
)
```
All you have to do is give it a string `objective`, define a list of `Action`s, and optionally give it a `memory_dict` of `name` to `text` for it to remember. The agent is equipped with a few `Action`s by default, such as being able to ask you for clarification if necessary, and a memory which it can query to help achieve its objectives.

See some [examples](examples/). TODO: If you want to run the examples, you have to move them into the root folder and then run `python <example_file>.py`.

#### 🏃🏽 Creating actions and running

Example: 

```python
"""Example of using AgenticGPT to make a folder on the filesystem.
Also demonstrates how to ask the user for input and use it in the agent's
thoughts."""
import os
from agentic_gpt.agent import AgenticGPT
from agentic_gpt.agent.action import Action


def mkdir(folder):
    os.mkdir(folder)

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
```

`Action`s are instantiated with a `name`, `description`, and `function`. The `name`, `description`, and function signature are then injected into the agent prompt to tell them what they can do. `Action` results are stored in context, unless a dict answer is given with `{"context": }` which sets the context accordingly.

#### ♻️ Reusing saved routines
You can then save the steps that the LLM generated using

```python
agent.save_actions_taken("mkdir.json")
```

and reuse it using: 

```python
agent = AgenticGPT(
    "Ask the user what folder they want to make and make it for them.",
    actions_available=actions,
)
agent.from_saved_actions("mkdir.json")
agent.replay()
```

## ⚜️ Design

See [request for comment](docs/motivation-rfc.md) for the original motivation for and considerations around building this.

TODO, add a diagram and explanation

## 🚧 TODO

- [x] Memory instantiation and routing of queries.
- [x] Add "query memory" and "add to memory" default functions.
- [x] Retry when there is an error.
- [x] Save and load routine to file.
- [x] Write some initial docs. Be sure to add emojis because people can't get enough emojis.
- [x] Create and document examples. Start setting up a library of actions.
- [x] Support sentencetransformers and gpt-4.
- [x] Don't make it incumbent on the user to make Actions return a context.
- [x] Figure out a more modular way to solicit the user for feedback, maybe a default `ask_user_to_clarify` hook.
- [ ] Create chatbot mode where it stops after every step and asks you how it's doing.
- [ ] Make some diagrams describing the architecture.
- [ ] Put on pypi.
- [ ] Test Memory functions: adding a document, querying all, loading document.

## 🚨 Disclaimer

- Be careful what tools you expose to the agent, because it is running autonomously.
- Be careful what data you expose to the agent, because it may be processed by the LLM APIs under the hood.
