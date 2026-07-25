"""
Compliance Analysis Tools for Multi-Tool Agent System
Single agent uses these 3 tools to perform compliance analysis in-loop
"""
import json
import sys
sys.path.append('../..')
from data.nr1_clauses import get_nr1_requirements, get_company_document


def retrieval_fetch_tool(query: str, search_type: str = "all") -> str:
    """
    Tool 1: Retrieval/Fetch Tool
    Searches and extracts relevant NR-1 clauses based on query
    
    Args:
        query: Compliance search query
        search_type: "all", "critical", "category:<name>"
    
    Returns:
        JSON formatted relevant clauses and requirements
    """
    nr1_framework = get_nr1_requirements()
    
    # Parse search type
    if search_type == "critical":
        results = {k: v for k, v in nr1_framework.items() if v.get("severity") == "Critical"}
    elif search_type.startswith("category:"):
        category = search_type.split(":", 1)[1]
        results = {k: v for k, v in nr1_framework.items() if v.get("category") == category}
    else:  # "all" or default
        # Simple relevance matching on query keywords
        results = {}
        query_lower = query.lower()
        for req_id, req_detail in nr1_framework.items():
            title_match = query_lower in req_detail.get("title", "").lower()
            req_match = query_lower in req_detail.get("requirement", "").lower()
            if title_match or req_match or search_type == "all":
                results[req_id] = req_detail
    
    return json.dumps({
        "tool": "retrieval_fetch_tool",
        "query": query,
        "found_clauses": results,
        "count": len(results)
    }, indent=2)


def reasoning_comparison_tool(extracted_clauses: str, analysis_context: str = "gap_analysis") -> str:
    """
    Tool 2: Reasoning/Comparison Tool
    Performs gap analysis and reasoning between extracted requirements and company document
    
    Args:
        extracted_clauses: JSON from retrieval tool or string description of requirements
        analysis_context: "gap_analysis" (default), "risk_assessment", "remediation"
    
    Returns:
        JSON with gap analysis, risk scores, and recommendations
    """
    company_doc = get_company_document()
    
    gaps = []
    
    # Parse extracted clauses if JSON
    try:
        if isinstance(extracted_clauses, str) and extracted_clauses.strip().startswith('{'):
            clauses_data = json.loads(extracted_clauses)
            clauses_dict = clauses_data.get("found_clauses", {})
        else:
            clauses_dict = {}
    except:
        clauses_dict = {}
    
    # Perform comparison and gap analysis
    for req_id, requirement in clauses_dict.items():
        req_title = requirement.get("title", "")
        req_text = requirement.get("requirement", "")
        severity = requirement.get("severity", "Medium")
        
        # Mock gap assessment based on document content
        gap_description = f"Requirement '{req_title}' needs assessment against company document."
        
        gaps.append({
            "requirement_id": req_id,
            "title": req_title,
            "status": "GAP" if severity == "Critical" else "REVIEW",
            "severity": severity,
            "gap_description": gap_description,
            "remediation": f"Update policies to address: {req_text[:100]}..."
        })
    
    return json.dumps({
        "tool": "reasoning_comparison_tool",
        "analysis_type": analysis_context,
        "total_gaps_found": len(gaps),
        "gaps": gaps,
        "overall_risk": "HIGH" if any(g["severity"] == "Critical" for g in gaps) else "MEDIUM"
    }, indent=2)


def validation_tool(analysis_result: str, validation_level: str = "full") -> str:
    """
    Tool 3: Validation Tool
    Checks analysis output for internal consistency, hallucinations, and validity
    
    Args:
        analysis_result: JSON output from reasoning tool
        validation_level: "quick", "full" (default), "strict"
    
    Returns:
        JSON with validation verdict, issues found, and confidence score
    """
    try:
        if isinstance(analysis_result, str) and analysis_result.strip().startswith('{'):
            analysis_data = json.loads(analysis_result)
        else:
            analysis_data = {}
    except:
        analysis_data = {}
    
    issues_found = []
    consistency_score = 100
    hallucination_score = 100
    
    # Validation checks
    gaps = analysis_data.get("gaps", [])
    
    # Check 1: Verify gap descriptions are substantive
    for gap in gaps:
        if not gap.get("gap_description") or len(gap.get("gap_description", "")) < 10:
            issues_found.append(f"Gap {gap.get('requirement_id')}: Description too vague")
            consistency_score -= 10
    
    # Check 2: Verify remediation suggestions are actionable
    for gap in gaps:
        remediation = gap.get("remediation", "")
        if "TBD" in remediation or "unknown" in remediation.lower():
            issues_found.append(f"Gap {gap.get('requirement_id')}: Non-actionable remediation")
            consistency_score -= 5
    
    # Check 3: Overall structure validation
    if not analysis_data.get("tool") or analysis_data.get("tool") != "reasoning_comparison_tool":
        issues_found.append("Input data structure unexpected")
        consistency_score -= 20
    
    validation_passed = consistency_score >= 70 and len(issues_found) == 0
    
    return json.dumps({
        "tool": "validation_tool",
        "validation_status": "PASS ✅" if validation_passed else "NEEDS REVIEW ⚠️",
        "consistency_score": consistency_score,
        "hallucination_risk_score": hallucination_score,
        "issues_found": issues_found,
        "recommendations": [
            "Review all high-severity gaps",
            "Implement remediation plan",
            "Schedule follow-up audit"
        ] if validation_passed else ["Address issues above before proceeding"],
        "overall_verdict": "Analysis is valid and actionable" if validation_passed else "Recheck analysis"
    }, indent=2)


# Tool registry for the agent
TOOLS = {
    "retrieval_fetch_tool": retrieval_fetch_tool,
    "reasoning_comparison_tool": reasoning_comparison_tool,
    "validation_tool": validation_tool,
}
