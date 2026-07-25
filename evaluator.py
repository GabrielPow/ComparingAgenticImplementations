# evaluator.py
import json
import os
import google as genai

# Configure Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

JUDGE_PROMPT_TEMPLATE = """
You are an expert compliance auditor and LLM Evaluator for Brazilian Regulatory Standards (NR-1).
Your task is to evaluate an AI agent system's response against a verified Ground Truth and a list of expected Key Points.

### Input Data:
- User Query: {query}
- Expected Ground Truth: {ground_truth}
- Expected Key Points: {key_points}
- Relevant NR-1 Clauses: {references}

### Agent System Output:
{system_output}

### Evaluation Instructions:
Evaluate the system output strictly and objectively. Output a JSON object with EXACTLY the following keys:
1. "score": A float between 0.0 and 1.0 representing overall accuracy and completeness.
2. "matched_points": List of strings from Expected Key Points that were correctly addressed.
3. "missed_points": List of strings from Expected Key Points that were missing or incorrect.
4. "hallucination_flags": List of claims in the system output that are unsupported or contradict NR-1 / Ground Truth.
5. "explanation": A concise 2-3 sentence justification of the score.

Respond ONLY with valid JSON.
"""

def evaluate_with_judge(item: dict, system_output_text: str) -> dict:
    """Uses Gemini as an LLM Judge to grade the system response."""
    if not GEMINI_API_KEY:
        return {
            "score": 0.0,
            "matched_points": [],
            "missed_points": item.get("key_points", []),
            "hallucination_flags": ["GEMINI_API_KEY missing in environment."],
            "explanation": "Could not run Judge: API key not configured."
        }

    formatted_prompt = JUDGE_PROMPT_TEMPLATE.format(
        query=item.get("query_pt", ""),
        ground_truth=item.get("ground_truth", ""),
        key_points=json.dumps(item.get("key_points", []), ensure_ascii=False),
        references=json.dumps(item.get("references", []), ensure_ascii=False),
        system_output=system_output_text
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            formatted_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "score": 0.0,
            "matched_points": [],
            "missed_points": item.get("key_points", []),
            "hallucination_flags": [f"Judge parsing failed: {str(e)}"],
            "explanation": "Failed to generate evaluation response from Judge."
        }