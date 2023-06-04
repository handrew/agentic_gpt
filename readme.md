# 🪽 AgenticGPT

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
    max_steps=100,
    model="gpt-3.5-turbo",
    verbose=False
)
```
All you have to do is give it a string `objective`, define a list of `Action`s, and optionally give it a `memory_dict` of `name` to `text` for it to remember.

See some [examples](examples/) folder.

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

`Action`s are instantiated with a `name`, `description`, and `function`. The `name`, `description`, and function signature are then injected into the agent prompt to tell them what they can do.

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

## 🚧 TODO

- [x] Memory instantiation and routing
- [x] Add "query memory" default function
- [x] Add "add to memory" function
- [x] Retry when there is an error
- [x] Save and load routine to file
- [x] Write some initial docs. Be sure to add emojis because people can't get enough emojis
- [ ] Make some diagrams describing the architecture
- [ ] Create and document examples. Start setting up a library of actions.
- [ ] Create chatbot mode where it stops after every step and asks you how it's doing
- [ ] Recursively modularize the context window in case it gets too long

## 🚨 Disclaimer

- Be careful what tools you expose to the agent, because it is running autonomously.
- Be careful what data you expose to the agent, because it may be processed by the LLM APIs under the hood.