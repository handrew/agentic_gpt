# Building Journal
*A log of thoughts while building and experimenting with LLMs.*

## 🎉 July 12, 2023 update

I decided to give this project another whirl before an upcoming hackathon. Some time away helped with unblocking some of the problems I was encountering. In particular, I figured out how to pass variables between LLM API calls — using Jinja to template made it a lot easier to give the AI a way of calling variables in the `AgenticGPT` class's memory. 

At a higher level, I realized that my previous comment (below) about the LLM acting as a glorified "if" statement" was perhaps too reductive. Rather than seeing it as a limitation of the technology, I leaned into the fuzzy, "if-else" routing capacity as *the* primary enabler of today's crop of LLMs. Viewed in that light, a few things became possible: (1) obviously, value arises from being able to translate natural language to actions, executed through an assortment of code building blocks (though the inherent ambiguity of natural language poses some challenge for consistency) and (2) the LLM was able to dynamically reason about its environment and decide if it had accomplished its objective or not, like a human. By contrast, a traditional piece of software is hardcoded; it is inert, and cannot adapt to its environment. It breaks when encountering a situation it has not explicitly been given guidelines to address. 

As an example, I created an `AgenticGPT` to [download investor presentations](../examples/investor_presentations/readme.md) from publicly traded company websites. I initialized it with seven capabilities (i.e., seven functions which I coded ahead of time), gave it a numbered list of instructions, and it did the rest. It doesn't get it right every single time, but I think that it's a promising development. 

If my hypothesis in building this project is correct and this paradigm of agents will become more widespread, a few interesting implications emerge. While much has been said about prompt engineering in discourse today, less has been said about the hybrid between prompt engineering and traditional software engineering. For instance, while debugging errors in the above example, I had to ask myself to what extent an error was arising because (a) I did not write my code functions (the agent's `Action`s well enough), (b) I did not expose the right actions to the agent, (c) the foundation model's reasoning capabilities are not good enough yet, (d) I didn't prompt the agent with clear enough instructions, or (e) some combination of the above. 

If I am right, then the "meta" of AI-enabled software development may change substantially — to involve both "human instruction" debugging as well as "program" debugging — as agents become more widespread. 

##  🚧 June 9, 2023 update

Currently, AgenticGPT is still a bit unreliable, mainly because the language model outputs are pretty unpredictable. Sometimes it doesn't return a JSON and the script breaks. Other times it gets into a loop and doesn't know when to stop. Still other times it accomplishes the task but keeps going anyway, and then it starts bloating its context window until I get an error from OpenAI.

In any case, all of these nondeterministic errors raise the following question: what are agents good for anyway? Won't most high value routines have APIs and be automated by clearly defined logic that creates deterministic and interpretable flows? If so, why not just write code to wrap around pre-defined prompts, or the APIs themselves? **What's the point of agents anyway?**

A bit of reflection after building this project so far yields the following answers:
- Being able to call APIs (and chain them together) in natural language is kind of useful, but ultimately still requires the user to be extremely detailed about their instruction.
- The LLM core acting as the executive decision maker is basically a glorified `if` statement—one which can take fuzzy, unstructured instructions and choose actions to take. This is really only useful if you have a lot of heterogeneous unstructured instructions.

Both of these things lend themselves to "low-code" tools which provide guardrails for nontechnical users to write "code", in the form of natural language. While this could be valuable in its own right, it is a bit of a far cry from the initial hope of building a generalized task-completion agent. I think we'll get there eventually—with larger context windows, better reasoning capabilities, etc. But that day is not today, so I'll likely pause development until I have better ideas about what to do.