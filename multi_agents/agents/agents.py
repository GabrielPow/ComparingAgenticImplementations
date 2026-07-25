import asyncio
from gemini_ai import (
    orchestrator_decompose,
    retrieval_agent_fetch,
    compliance_agent_analyze,
    qa_agent_validate
)
import json


class RetrieverAgent:
    """Pulls relevant NR-1 clauses/sections from compliance framework"""
    
    async def fetch(self, query: str, document_context: dict):
        print(f"[Retriever] Fetching relevant clauses for: {query}")
        result = await asyncio.to_thread(retrieval_agent_fetch, query, document_context)
        print(f"[Retriever] Found clauses:\n{result}")
        return result


class ComplianceAgent:
    """Performs gap analysis between Tests and NR-1 norm"""
    
    async def analyze(self, retrieved_clauses: str, company_doc: dict):
        print("[Compliance] Analyzing gaps between test samples and NR-1 requirements...")
        result = await asyncio.to_thread(compliance_agent_analyze, retrieved_clauses, company_doc)
        print(f"[Compliance] Gap Analysis:\n{result}")
        return result


class QAValidationAgent:
    """Checks reasoning output for consistency and hallucinations"""
    
    async def validate(self, compliance_analysis: str):
        print("[QA Validator] Validating analysis for hallucinations and consistency...")
        result = await asyncio.to_thread(qa_agent_validate, compliance_analysis)
        print(f"[QA Validator] Validation Result:\n{result}")
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
        
        # Step 1: Orchestrator decomposes the query
        print(f"\n[Orchestrator] Decomposing query: {query}")
        decomposition = await asyncio.to_thread(
            orchestrator_decompose,
            query,
            list(nr1_framework.keys())
        )
        print(f"[Orchestrator] Analysis Plan:\n{decomposition}\n")
        
        # Step 2: Retriever fetches relevant clauses
        print("[Orchestrator] Routing to Retriever Agent...")
        retrieved_clauses = await self.retriever.fetch(query, nr1_framework)
        
        # Step 3: Compliance Agent analyzes gaps
        print("\n[Orchestrator] Routing to Compliance Agent...")
        compliance_result = await self.compliance.analyze(retrieved_clauses, company_document)
        
        # Step 4: QA Agent validates
        print("\n[Orchestrator] Routing to QA Validation Agent...")
        qa_result = await self.qa.validate(compliance_result)
        
        # Step 5: Orchestrator aggregates findings
        aggregated_report = {
            "query": query,
            "decomposition": decomposition,
            "retrieved_clauses": retrieved_clauses,
            "compliance_gaps": compliance_result,
            "validation_verdict": qa_result,
            "status": "COMPLETE ✅" if "PASS" in qa_result else "NEEDS REVIEW ⚠️"
        }
        
        print("\n" + "="*70)
        print("ORCHESTRATOR: Final Aggregated Report")
        print("="*70)
        print(json.dumps(aggregated_report, indent=2))
        
        return aggregated_report
[]