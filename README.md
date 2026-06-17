<div style="text-align: right;">
  <a href="README.md">English</a> | <a href="README.pt.md">Português</a>
</div>

# Comparing Agentic Implementations

## Purpose
This project compares two agentic implementation styles for solving legal reasoning and compliance problems using Google Gemini.

The goal is to evaluate which architecture works better for increasingly complex legal reasoning tasks, using the Brazilian NR-1 regulatory framework as the domain example.

## What we want to solve
We are using law as an edge-case domain to compare agentic behavior across four difficulty levels:

- Level 1 — Definitional
  - "O que significa X no artigo Y?"
  - Single article, single concept, verifiable answer
- Level 2 — Interpretive
  - "Como o artigo X se aplica à situação Y?"
  - Requires reasoning over one law
- Level 3 — Cross-referential
  - "Este caso é coberto pela lei X ou pela lei Y?"
  - Multi-hop, requires comparing across codes
- Level 4 — Conflicting/Edge cases
  - "Dado X e Y, qual lei prevalece e por quê?"
  - Requires legal reasoning, hierarchy of norms

## Architecture Overview
This repository contains two separate architectures for agentic compliance analysis.

### 1) `Multi-Agents`

`Multi-Agents` uses an explicit multi-agent pipeline:

- `Multi-Agents/main.py`
  - Entry point that loads NR-1 framework and company document data.
  - Sends a compliance query into the orchestrator.
- `Multi-Agents/agents/agents.py`
  - `OrchestratorAgent`: orchestrates the workflow.
  - `RetrieverAgent`: fetches relevant legal clauses.
  - `ComplianceAgent`: performs gap analysis.
  - `QAValidationAgent`: validates the analysis.
- `Multi-Agents/agents/gemini_ai.py`
  - Implements the Gemini calls for each agent role.
  - Separates decomposition, retrieval, reasoning, and validation.

This architecture is best when you want:

- clear role separation
- modular reasoning steps
- explicit pipeline visibility
- better tracing and inspection of each stage

### 2) `Multi-Tools`

`Multi-Tools` uses a single agent with tool-based reasoning:

- `Multi-Tools/main.py`
  - Entry point that issues a compliance query to the single `compliance_agent`.
- `Multi-Tools/agents/gemini_ai.py`
  - Defines a single Gemini agent loop.
  - The model can invoke tool calls during the session.
- `Multi-Tools/skills/gemini_tools.py`
  - Defines three tools:
    - `retrieval_fetch_tool`
    - `reasoning_comparison_tool`
    - `validation_tool`
  - Tools are declared to Gemini and executed from Python.

This architecture is best when you want:

- flexible model-driven orchestration
- tool-specified capabilities
- a smaller code surface for agent management
- model-internal decision-making over tool usage

## Data and Example Domain

- `data/nr1_clauses.py`
  - Contains the NR-1 regulatory framework data used for compliance queries.
  - Also provides example company document content for gap analysis.

The domain is intentionally legal/compliance-focused so we can test agentic reasoning across:

- exact text retrieval
- normative interpretation
- cross-reference comparison
- conflict resolution and hierarchy of norms

## How to Run

1. Add your Gemini API key to `.env` in both `Multi-Agents` and `Multi-Tools` if needed:

```env
GEMINI_API_KEY=your_api_key_here
```

2. Run the multi-agent pipeline:

```bash
python Multi-Agents/main.py
```

3. Run the single-agent tool pipeline:

```bash
python Multi-Tools/main.py
```

## Evaluation Strategy

Use the same set of legal reasoning queries across both implementations and compare:

- quality of retrieval
- chain of thought transparency
- correctness on definitional questions
- ability to interpret a single law
- ability to compare multiple laws
- ability to resolve conflicting norms
- hallucination rate and validation confidence

### Suggested test flow

1. Start with a Level 1 definitional query to validate retrieval accuracy.
2. Move to a Level 2 interpretive query to test reasoning over one law.
3. Use a Level 3 cross-referential query to force multi-hop comparison.
4. Finish with a Level 4 conflict query to evaluate legal hierarchy reasoning.

## What to compare

- `Multi-Agents` gives explicit, inspectable sub-agents and is good for structured workflows.
- `Multi-Tools` gives model-driven tool invocation and is good for adaptive tool reasoning.

Use the law example as a testbed for deciding which approach is better for:

- strict compliance workflows
- legal reasoning edge cases
- adversarial or conflicting inputs
- explainability vs tool flexibility

## Notes

The current implementation uses Gemini 2.5 Flash and a small NR-1 compliance dataset. The same pattern can be extended to other legal codes or regulatory domains.

> Note: an `app.py` Streamlit front-end will be implemented soon to streamline both architectures into a unified interface. The current design is intentionally exploratory and the architecture may evolve as testing reveals the best agentic approach.

