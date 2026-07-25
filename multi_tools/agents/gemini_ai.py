import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import python tool implementations directly
from skills.gemini_tools import (
    retrieval_fetch_tool,
    reasoning_comparison_tool,
    validation_tool
)

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Initialize Client
client = genai.Client(api_key=api_key)
model_id = "gemini-2.5-flash"

# Simply register the python functions as tools directly!
TOOLS_LIST = [retrieval_fetch_tool, reasoning_comparison_tool, validation_tool]

def compliance_agent(user_query: str) -> dict:
    print("\n" + "="*70)
    print("COMPLIANCE AGENT: Starting Orchestrated Tool Analysis")
    print("="*70)
    print(f"Query: {user_query}\n")
    
    system_prompt = """You are an expert Compliance Analyst Agent. Your job is to:
    1. Use retrieval_fetch_tool to find relevant NR-1 compliance clauses.
    2. Use reasoning_comparison_tool to analyze gaps between requirements and company document.
    3. Use validation_tool to verify the analysis is sound.
    
    Execute tools in sequence, using outputs from each tool to inform the next.
    Always validate your final analysis before completing."""

    # Config setup
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=TOOLS_LIST,  # Pass function list directly
        temperature=0.2
    )

    # Use client.chats to let the SDK automatically manage conversation history & automatic function calls
    chat = client.chats.create(
        model=model_id,
        config=config
    )

    # Send initial query - SDK executes function calling loop internally!
    response = chat.send_message(user_query)

    print("\n[Execution Completed]")
    print(f"\n[Agent Summary]:\n{response.text}")

    print("\n" + "="*70)
    print("COMPLIANCE AGENT: Analysis Complete")
    print("="*70)
    
    return {
        "query": user_query,
        "agent_summary": response.text,
        "history": chat.get_history()
    }