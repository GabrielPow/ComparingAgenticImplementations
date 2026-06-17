from agents.agents import OrchestratorAgent
from data.nr1_clauses import get_nr1_requirements, get_company_document
import asyncio
import json


async def main():
    # Initialize the orchestrator
    orchestrator = OrchestratorAgent()
    
    # Get compliance framework and company document
    nr1_framework = get_nr1_requirements()
    company_document = get_company_document()
    
    # Example compliance analysis queries
    queries = [
        "Is our company compliant with NR-1 data encryption requirements?",
        "What gaps exist between our access control policies and NR-1.2 requirements?",
        "Audit our data retention practices against NR-1.4"
    ]
    
    # Run compliance analysis for first query (can parallelize multiple queries if needed)
    result = await orchestrator.run_compliance_analysis(
        queries[0],
        nr1_framework,
        company_document
    )
    
    # Optionally save the report
    with open("compliance_report.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n✅ Report saved to compliance_report.json")


if __name__ == "__main__":
    asyncio.run(main())