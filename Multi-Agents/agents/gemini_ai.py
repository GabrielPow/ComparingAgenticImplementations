import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
import json
import re
import sys
sys.path.append('../..')
from data.nr1_clauses import get_nr1_requirements, get_requirement_by_id


# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Configure Gemini
model_id = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)


def call_gemini(prompt: str, system_instruction: str = "") -> str:
    """Helper to call Gemini with a prompt and optional system instruction."""
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            system_instruction=system_instruction,
        ) if system_instruction else None
    )
    return response.text.strip()


def orchestrator_decompose(query: str, nr1_requirements: list) -> str:
    """Orchestrator Agent: Decompose compliance query into analysis steps"""
    system_instruction = """You are a Compliance Analysis Orchestrator. Your role is to:
    - Receive a compliance query
    - Break it into specific analysis tasks
    - Identify which NR-1 requirements are relevant
    - Plan the workflow for subordinate agents
    
    Format your response as a structured analysis plan with:
    1. Query Understanding
    2. Relevant NR-1 Requirements
    3. Analysis Steps
    4. Expected Outputs"""
    
    prompt = f"""Query: {query}
    
Available NR-1 Requirements: {', '.join(nr1_requirements)}

Decompose this compliance analysis into specific steps."""
    
    result = call_gemini(prompt, system_instruction)
    return result


def retrieval_agent_fetch(query: str, nr1_framework: dict) -> str:
    """Retrieval Agent: Extract relevant NR-1 clauses and framework sections"""
    system_instruction = """You are a Compliance Document Analyst. Your role is to:
    - Analyze the query to understand compliance concerns
    - Identify relevant NR-1 clauses from the framework
    - Extract specific requirements and details
    - Present findings in a structured format
    
    Format your response with:
    1. Relevant NR-1 IDs and Titles
    2. Full requirement text
    3. Severity levels
    4. Categories"""
    
    nr1_text = json.dumps(nr1_framework, indent=2)
    prompt = f"""Compliance Query: {query}

NR-1 Framework:
{nr1_text}

Identify and extract all relevant NR-1 clauses that apply to this query."""
    
    result = call_gemini(prompt, system_instruction)
    return result


def compliance_agent_analyze(retrieved_clauses: str, company_document: dict) -> str:
    """Compliance Agent: Perform gap analysis between document and requirements"""
    system_instruction = """You are a Compliance Gap Analyst. Your role is to:
    - Compare company documentation against NR-1 requirements
    - Identify gaps, weaknesses, and non-compliance areas
    - Assess risk severity for each gap
    - Suggest remediation steps
    
    Format your response with:
    1. Gap Summary (overall compliance score)
    2. Critical Gaps (must fix)
    3. High Priority Gaps (should fix)
    4. Medium Priority Gaps
    5. Recommendations for Each Gap
    6. Overall Risk Assessment"""
    
    company_doc_text = json.dumps(company_document, indent=2)
    prompt = f"""Relevant NR-1 Requirements:
{retrieved_clauses}

Company Document:
{company_doc_text}

Perform a detailed gap analysis. Compare what the company document says with what NR-1 requires."""
    
    result = call_gemini(prompt, system_instruction)
    return result


def qa_agent_validate(compliance_analysis: str) -> str:
    """QA Validation Agent: Verify analysis for consistency and hallucinations"""
    system_instruction = """You are a Compliance QA Validator. Your role is to:
    - Review compliance analysis for logical consistency
    - Check for hallucinations or unsupported claims
    - Verify all gaps are justified with evidence
    - Ensure recommendations are practical and traceable
    
    Format your response with:
    1. Validation Status (PASS / NEEDS REVIEW)
    2. Consistency Check (any contradictions?)
    3. Evidence Verification (are claims supported?)
    4. Hallucination Check (any unsupported claims?)
    5. Recommendation Viability
    6. Issues Found (if any)"""
    
    prompt = f"""Compliance Analysis to Validate:
{compliance_analysis}

Validate this analysis for accuracy, consistency, and absence of hallucinations.
Are all claims properly supported? Are recommendations practical?"""
    
    result = call_gemini(prompt, system_instruction)
    return result

