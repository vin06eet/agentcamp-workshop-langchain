# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hands-on workshop teaching how to build AI chat agents using LangChain, Chainlit, and GitHub Models. The codebase is organized into progressive phases, each building on the previous one.

## Common Commands

```bash
# Run any Chainlit app
chainlit run app.py -w

# Run specific phase solution
chainlit run solutions/phase-06/app.py -w

# Test GitHub Models connection
python solutions/phase-02/test_github_models.py

# Install dependencies
pip install -r requirements.txt
# or with uv (faster)
uv pip install -r requirements.txt

# Format code
black .
```

## Architecture

### Phase Progression
The workshop builds incrementally through 6 phases:

1. **Phase 2**: GitHub Models connection test - validates LLM access via `ChatOpenAI` with GitHub's inference endpoint
2. **Phase 3**: Basic Chainlit chat with conversation memory using `@cl.on_chat_start` and `@cl.on_message` decorators
3. **Phase 4**: LangChain agents via `create_agent()` without tools - introduces agent abstraction
4. **Phase 5**: Tool calling - adds `@tool` decorated functions (weather API example)
5. **Phase 6**: MCP integration - combines local tools with remote MCP server tools using `langchain-mcp-adapters`

### Key Patterns

**LLM Configuration** (used in all phases):
```python
ChatOpenAI(
    model="openai/gpt-4.1-nano",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference",
)
```

**Session Management** (Chainlit pattern):
```python
cl.user_session.set("agent", agent)
cl.user_session.set("chat_history", [])
```

**Tool Definition**:
```python
@tool
def function_name(arg: str) -> str:
    """Docstring is critical - agent uses it to decide when to call the tool."""
    ...
```

**Agent Creation with Tools**:
```python
agent = create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)
```

### File Structure
- `solutions/phase-XX/app.py` - Main Chainlit application for each phase
- `solutions/phase-XX/tools.py` - Tool definitions (phases 5-6)
- `docs/` - Workshop documentation for each phase

## Environment Variables

Required in `.env`:
- `GITHUB_TOKEN` - GitHub personal access token for GitHub Models API
- `WEATHER_API_KEY` - WeatherAPI key for tool demo (phase 5+)

## Workshop Writing Guidelines

This section documents how the training materials are structured, useful for creating new workshops.

### Documentation Structure

Each phase doc (`docs/XX-phase-name.md`) follows this pattern:
1. **Header** with time estimate and learning objectives
2. **Concept explanation** with ASCII diagrams where helpful
3. **Step-by-step instructions** that build incrementally
4. **Complete code example** at the end for reference
5. **Project structure** showing expected files
6. **Checkpoint** with testable scenarios
7. **Common issues** section for troubleshooting

### Progressive Complexity

- Each phase builds on the previous one with minimal new concepts
- Early steps show simplified code, final code adds all parameters (e.g., `temperature=0.7`)
- Code is introduced incrementally: first a minimal working version, then enhanced
- Explicit "What's new" tables comparing current phase to previous

### Code Consistency

- Solution files in `solutions/phase-XX/` must match the final code in docs exactly
- All `get_llm()` functions include `temperature=0.7` in final versions
- Streaming code pattern for agents with tools:
  ```python
  async for stream_mode, data in agent.astream(
      {"messages": chat_history},
      stream_mode=["messages", "updates"]
  ):
  ```
- Tool visualization uses `cl.Step()` with input/output tracking via `steps` dict

### Practical Elements

- Each phase folder created with `mkdir -p phase-XX && cd phase-XX && touch app.py`
- Files to create are explicitly listed (no implicit file creation)
- Virtual environment tip: mention `deactivate` to exit
- Chainlit auto-creates `chainlit.md` - no need to copy between phases
- Time estimates are realistic (total ~90 minutes tested)

### Testing Checkpoints

Each phase includes specific test scenarios:
- Concrete user inputs to try
- Expected outputs/behaviors
- Visual confirmations (e.g., "tool step appears in UI")
