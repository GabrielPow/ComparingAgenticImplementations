# Multi-Tools and Multi-Agents Architecture

## Overview
This repository contains two example projects that demonstrate different LLM-driven agent architectures:

- `Multi-Agents`: asynchronous multi-role workflow orchestration
- `Multi-Tools`: tool selection and invocation via an LLM controller

Both projects share a common dependency on the Google Gemini SDK and use a `.env` file to load the `GEMINI_API_KEY`.

---

## Multi-Agents Architecture

### Purpose
`Multi-Agents` is designed to show an agent workflow with distinct specialist roles collaborating on a task. It models a simplified product development cycle:

1. Product Manager defines requirements
2. Engineer produces an implementation
3. QA validates the output

### Structure
- `Multi-Agents/main.py`
  - Creates a `Coordinator`
  - Runs concurrent workflows with `asyncio.gather(...)`
  - Example tasks: build a factorial function, create a sorting algorithm

- `Multi-Agents/agents/agents.py`
  - Defines role classes:
    - `ProductManager`
    - `Engineer`
    - `QA`
  - Implements `Coordinator` orchestration
  - Workflow steps:
    1. `ProductManager.analyze(prompt)`
    2. `Engineer.implement(requirements)`
    3. `QA.test(implementation)`
  - If QA fails, the coordinator restarts a second cycle with revision feedback

- `Multi-Agents/agents/gemini_ai.py`
  - Provides Gemini API integration and role-specific prompts
  - Exposes:
    - `product_manager_analyze(prompt)`
    - `engineer_implement(task)`
    - `qa_test(solution)`
  - Each function includes a system instruction for the model role

### Behavior
- The `Coordinator` uses async methods to keep I/O nonblocking.
- Each step is computed via Gemini LLM calls.
- QA may trigger a revision loop if the first result fails validation.
- The architecture emphasizes role separation and sequential task handoff.

---

## Multi-Tools Architecture

### Purpose
`Multi-Tools` demonstrates a tool-routing agent pattern where a single LLM chooses from predefined tools and the application executes the selected tool.

### Structure
- `Multi-Tools/main.py`
  - Starts the example agent execution
  - Calls a sample request through `agent(...)`

- `Multi-Tools/agents/gemini_ai.py`
  - Implements the controller that interprets user input
  - Sends a system prompt describing available tools
  - Parses model output as JSON containing `tool` and `params`
  - Dispatches the tool call to the local tool registry

- `Multi-Tools/skills/gemini_tools.py`
  - Defines the actual tool implementations:
    - `search_web(query: str)`
    - `send_email(to: str, subject: str, body: str)`
    - `create_event(title: str, date: str)`
  - Exports a `TOOLS` dictionary used by the agent controller

### Behavior
- The LLM decides which tool to invoke and returns a structured JSON payload.
- The controller validates the tool name and executes the corresponding function.
- This architecture isolates tool selection from tool execution.
- It is useful for building reliable agents that operate with explicit capabilities.

---

## Comparison

| Aspect | Multi-Agents | Multi-Tools |
|---|---|---|
| Pattern | Role-based workflow | Tool-oriented agent |
| Orchestration | `Coordinator` async pipeline | LLM selects tool and dispatches |
| Main files | `Multi-Agents/main.py` | `Multi-Tools/main.py` |
| Agent roles | Product Manager, Engineer, QA | Single controller, multiple tools |
| Retry logic | QA-driven revision cycle | None |
| Tool use | Role-specific Gemini prompts | Explicit local tools registry |

---

## Common Infrastructure

- Uses `.env` for `GEMINI_API_KEY`
- Uses `google.genai` for Gemini API integration
- Supports Python async execution in `Multi-Agents`
- Models are invoked through shared Gemini helper functions

---

## Notes

- `Multi-Agents` is well-suited for workflows requiring sequential role handoff.
- `Multi-Tools` is ideal for tasks that can be solved by choosing and executing a known tool.
- Both examples are useful references for building LLM-native orchestration patterns.

NR-1

Orchestrator
Retrieval/Fetch Agent
Compliance/Reasoning Agent
QA/Validation Agent 

4 Agents

VS

Orchestrator
Fetch Tool
Reasoning Tool
Validation Tool

1 Agent