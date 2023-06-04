# AgenticGPT

## Usage
### Installation
1. `pip install -r requirements.txt`
2. Set up your OpenAI API key as the `OPENAI_API_KEY` environment variable.

### Setup
Instantiate the 

See some [examples](examples/) folder.


## Design

See [request for comment](motivation-rfc.md) for the original motivation for and considerations around building this.

## TODO

- [x] Memory instantiation and routing
- [x] Add "query memory" default function
- [x] Add "add to memory" function
- [x] Retry when there is an error
- [x] Save and load routine to file
- [ ] Write some docs, make some diagrams
- [ ] Create and document examples
- [ ] Recursively modularize the context window in case it gets too long