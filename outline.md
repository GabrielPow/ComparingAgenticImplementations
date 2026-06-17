Next steps:

1. Start with Gemini API and prompt engineering instead of Gemma/Llama with LoRA to verify architecture and reading comprehension / legal reasoning.

2. Tailor the agent tools and workflows to be based on law codes.

3. With DeepEval write increasingly hard test questions based on NRs (Normas Reguladores), specifically the normas regulamentadoras do ministerio do trabalho, with increasing difficulty, these levels are:
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

4. Verify tests with DeepEval, write interpretations.

5. Check interpretations and if time allows, change model to Gemma/Llama with LoRA.
