"""
Multi-Tool Compliance Agent
Single agent that orchestrates 3 tools in-loop for compliance analysis
"""
import os
from dotenv import load_dotenv
from google import genai
from google import GenerateContentConfig, Tool
from skills.gemini_tools import TOOLS, retrieval_fetch_tool, reasoning_comparison_tool, validation_tool
import json
import re


# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Configure Gemini
model_id = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)

# Define tools for Gemini
GEMINI_TOOLS = [
    Tool(
        function_declarations=[
            {
                "name": "retrieval_fetch_tool",
                "description": "Fetches relevant NR-1 compliance clauses based on search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Compliance search query"},
                        "search_type": {"type": "string", "description": "Type: 'all', 'critical', or 'category:<name>'"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "reasoning_comparison_tool",
                "description": "Performs gap analysis between requirements and company document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "extracted_clauses": {"type": "string", "description": "Extracted clauses (JSON or text)"},
                        "analysis_context": {"type": "string", "description": "Type: 'gap_analysis', 'risk_assessment', 'remediation'"}
                    },
                    "required": ["extracted_clauses"]
                }
            },
            {
                "name": "validation_tool",
                "description": "Validates analysis for consistency and hallucinations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis_result": {"type": "string", "description": "Analysis result to validate (JSON)"},
                        "validation_level": {"type": "string", "description": "Type: 'quick', 'full', 'strict'"}
                    },
                    "required": ["analysis_result"]
                }
            }
        ]
    )
]

def compliance_agent(user_query: str) -> dict:
    """
    Single Compliance Agent that orchestrates 3 tools in-loop:
    1. Retrieval tool to fetch relevant NR-1 clauses
    2. Reasoning tool to perform gap analysis
    3. Validation tool to check output quality
    """
    print("\n" + "="*70)
    print("COMPLIANCE AGENT: Starting Orchestrated Tool Analysis")
    print("="*70)
    print(f"Query: {user_query}\n")
    
    system_prompt = """You are an expert Compliance Analyst Agent. Your job is to:
    1. Use retrieval_fetch_tool to find relevant NR-1 compliance clauses
    2. Use reasoning_comparison_tool to analyze gaps between requirements and company document
    3. Use validation_tool to verify the analysis is sound
    
    Execute tools in sequence, using outputs from each tool to inform the next.
    Provide clear explanations at each step.
    
    Always validate your final analysis before completing."""
    
    messages = [
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    final_result = {
        "query": user_query,
        "retrieval_output": None,
        "reasoning_output": None,
        "validation_output": None,
        "agent_summary": ""
    }
    
    # Agentic loop: Run model with tools until completion
    iteration = 0
    max_iterations = 5  # Safety limit
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n[Agent Iteration {iteration}]")
        
        response = client.models.generate_content(
            model=model_id,
            contents=messages,
            tools=GEMINI_TOOLS,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        
        # Check if model wants to call tools
        if not response.content.parts:
            print("No response from model")
            break
        
        # Look for function calls
        tool_calls_made = False
        for part in response.content.parts:
            if hasattr(part, "function_call"):
                tool_calls_made = True
                function_call = part.function_call
                tool_name = function_call.name
                tool_args = json.loads(function_call.args.to_json())
                
                print(f"  → Calling tool: {tool_name}")
                print(f"    Args: {json.dumps(tool_args, indent=2)}")
                
                # Execute the appropriate tool
                if tool_name == "retrieval_fetch_tool":
                    result = retrieval_fetch_tool(**tool_args)
                    final_result["retrieval_output"] = result
                    print(f"    Result: Fetched {json.loads(result).get('count', 0)} relevant clauses")
                    
                elif tool_name == "reasoning_comparison_tool":
                    result = reasoning_comparison_tool(**tool_args)
                    final_result["reasoning_output"] = result
                    gaps = json.loads(result).get("gaps", [])
                    print(f"    Result: Identified {len(gaps)} gaps in compliance")
                    
                elif tool_name == "validation_tool":
                    result = validation_tool(**tool_args)
                    final_result["validation_output"] = result
                    verdict = json.loads(result).get("validation_status", "UNKNOWN")
                    print(f"    Result: Validation {verdict}")
                else:
                    result = "Tool not recognized"
                    print(f"    Error: Tool {tool_name} not found")
                
                # Add tool result to messages for next iteration
                messages.append({
                    "role": "model",
                    "content": [part]  # Include the function call
                })
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": f"Tool result:\n{result}"}]
                })
        
        # If no tools were called, model is done
        if not tool_calls_made:
            # Extract final text response
            for part in response.content.parts:
                if hasattr(part, "text"):
                    final_result["agent_summary"] = part.text
                    print(f"\n[Agent Summary]:\n{part.text}")
            break
    
    print("\n" + "="*70)
    print("COMPLIANCE AGENT: Analysis Complete")
    print("="*70)
    
    return final_result

