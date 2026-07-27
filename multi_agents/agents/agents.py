import asyncio
import json
from gemini_ai_agents import (
    orchestrator_decompose,
    retrieval_agent_fetch,
    compliance_agent_analyze,
    qa_agent_validate
)

class RetrieverAgent:
    """Pulls relevant NR-1 clauses/sections from compliance framework"""
    async def fetch(self, query: str, nr1_framework: dict):
        print(f"[Retriever] Fetching relevant clauses for: {query}")
        result = await retrieval_agent_fetch(query, nr1_framework)
        print(f"[Retriever] Found clauses:\n{result}")
        return result


class ComplianceAgent:
    """Performs gap analysis between Tests and NR-1 norm"""
    async def analyze(self, retrieved_clauses: str, company_doc: dict):
        print("[Compliance] Analyzing gaps between test samples and NR-1 requirements...")
        result = await compliance_agent_analyze(retrieved_clauses, company_doc)
        print(f"[Compliance] Gap Analysis:\n{result}")
        return result


class QAValidationAgent:
    """Checks reasoning output for consistency and hallucinations"""
    async def validate(self, compliance_analysis: str) -> dict:
        print("[QA Validator] Validating analysis for hallucinations and consistency...")
        result = await qa_agent_validate(compliance_analysis)
        print(f"[QA Validator] Validation Result:\n{json.dumps(result, indent=2)}")
        return result


class OrchestratorAgent:
    """Multi-agent coordinator: decomposes task, routes to agents, aggregates findings"""
    def __init__(self):
        self.retriever = RetrieverAgent()
        self.compliance = ComplianceAgent()
        self.qa = QAValidationAgent()

    async def run_compliance_analysis(self, query: str, nr1_framework: dict, company_document: dict):
        print("\n" + "="*70)
        print("ORCHESTRATOR: Starting Compliance Analysis Pipeline")
        print("="*70)
        
        # Step 1: Decompose
        print(f"\n[Orchestrator] Decomposing query: {query}")
        decomposition = await orchestrator_decompose(
            query,
            list(nr1_framework.keys())
        )
        print(f"[Orchestrator] Analysis Plan:\n{decomposition}\n")
        
        # Step 2: Fetch Clauses
        print("[Orchestrator] Routing to Retriever Agent...")
        retrieved_clauses = await self.retriever.fetch(query, nr1_framework)
        
        # Step 3: Analyze Gaps
        print("\n[Orchestrator] Routing to Compliance Agent...")
        compliance_result = await self.compliance.analyze(retrieved_clauses, company_document)
        
        # Step 4: Validate
        print("\n[Orchestrator] Routing to QA Validation Agent...")
        qa_result = await self.qa.validate(compliance_result)
        
        # Step 5: Aggregate
        status_pass = qa_result.get("validation_status") == "PASS"
        aggregated_report = {
            "query": query,
            "decomposition": decomposition,
            "retrieved_clauses": retrieved_clauses,
            "compliance_gaps": compliance_result,
            "validation_verdict": qa_result,
            "status": "COMPLETE ✅" if status_pass else "NEEDS REVIEW ⚠️"
        }
        
        print("\n" + "="*70)
        print("ORCHESTRATOR: Final Aggregated Report")
        print("="*70)
        print(json.dumps(aggregated_report, indent=2))
        
        return aggregated_report