# 🏛️ Registry

Right now the following `AgenticGPT`-based agents exist:

## PlaywrightAgent
Uses `AgenticGPT` to automate browser actions. Sample usage:

```python
objective = "Go to https://google.com, search for 'cats', and click the first result. Wait 10 seconds. Then you're done."

with sync_playwright() as playwright_obj:
    agent = PlaywrightAgent(playwright_obj, objective, verbose=True)
    agent.run()
```