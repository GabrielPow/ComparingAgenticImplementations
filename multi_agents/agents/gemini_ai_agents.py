import os
import json
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

sys.path.append('../..')
from data.nr1_clauses import get_nr1_requirements, get_requirement_by_id

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

model_id = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)

# Pydantic schema for QA Agent validation structured output
class ValidationResponse(BaseModel):
    validation_status: str = Field(description="Must be either 'PASS' or 'NEEDS REVIEW'")
    consistency_check: str
    evidence_verification: str
    hallucination_check: str
    recommendation_viability: str
    issues_found: list[str]

async def call_gemini(prompt: str, system_instruction: str = "", response_schema=None) -> str:
    """Async helper using client.aio for high-performance non-blocking API calls."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction if system_instruction else None,
        response_mime_type="application/json" if response_schema else "text/plain",
        response_schema=response_schema if response_schema else None
    )
    
    response = await client.aio.models.generate_content(
        model=model_id,
        contents=prompt,
        config=config
    )
    return response.text.strip()


async def orchestrator_decompose(query: str, nr1_requirements: list) -> str:
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
    
    prompt = f"""Query: {query}\nAvailable NR-1 Requirements: {', '.join(nr1_requirements)}\nDecompose this compliance analysis into specific steps."""
    return await call_gemini(prompt, system_instruction)


async def retrieval_agent_fetch(query: str, nr1_framework: dict) -> str:
    system_instruction = """You are a Compliance Document Analyst. Your role is to:
    - Analyze the query to understand compliance concerns
    - Identify relevant NR-1 clauses from the framework
    - Extract specific requirements and details
    
    Format your response with:
    1. Relevant NR-1 IDs and Titles
    2. Full requirement text
    3. Severity levels
    4. Categories"""
    
    nr1_text = json.dumps(nr1_framework, indent=2)
    prompt = f"""Compliance Query: {query}\n\nNR-1 Framework:\n{nr1_text}\n\nIdentify and extract all relevant NR-1 clauses that apply to this query."""
    return await call_gemini(prompt, system_instruction)


async def compliance_agent_analyze(retrieved_clauses: str, company_document: dict) -> str:
    system_instruction = """You are a Compliance Gap Analyst. Your role is to:
    - Compare company documentation against NR-1 requirements
    - Identify gaps, weaknesses, and non-compliance areas
    - Assess risk severity for each gap
    
    Format your response with:
    1. Gap Summary (overall compliance score)
    2. Critical Gaps (must fix)
    3. High Priority Gaps (should fix)
    4. Recommendations for Each Gap"""
    
    company_doc_text = json.dumps(company_document, indent=2)
    prompt = f"""Relevant NR-1 Requirements:\n{retrieved_clauses}\n\nCompany Document:\n{company_doc_text}\n\nPerform a detailed gap analysis."""
    return await call_gemini(prompt, system_instruction)


async def qa_agent_validate(compliance_analysis: str) -> dict:
    system_instruction = """You are a Compliance QA Validator. Review the compliance analysis for consistency, accuracy, and absence of hallucinations."""
    prompt = f"""Compliance Analysis to Validate:\n{compliance_analysis}\n\nValidate this analysis for accuracy, consistency, and evidence justification."""
    
    # Returns structured JSON matching ValidationResponse
    raw_json = await call_gemini(prompt, system_instruction, response_schema=ValidationResponse)
    return json.loads(raw_json)