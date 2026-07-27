"""
Multi-Tool Compliance Agent System
Single agent orchestrates 3 tools in-loop for compliance analysis
"""
from multi_tools.agents.gemini_ai_tools import compliance_agent
import json


if __name__ == "__main__":
    # Example compliance queries
    queries = [
        "Is our company compliant with NR-1 data encryption and access control requirements?",
        "What are our data retention and backup compliance gaps?",
    ]
    
    # Run compliance analysis with the multi-tool agent
    result = compliance_agent(queries[0])
    
    # Save the detailed result
    with open("compliance_analysis.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ Detailed analysis saved to compliance_analysis.json")

