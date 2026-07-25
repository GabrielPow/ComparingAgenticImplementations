# evaluator.py
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

# Configure Gemini API key
# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Configure Gemini
model_id = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)
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
    if not api_key:
        return {
            "score": 0.0,
            "matched_points": [],
            "missed_points": item.get("key_points", []),
            "hallucination_flags": ["Gemini Key missing in environment."],
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
        response = client.models.generate_content(
            formatted_prompt,
            config=GenerateContentConfig{"response_mime_type": "application/json"}
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