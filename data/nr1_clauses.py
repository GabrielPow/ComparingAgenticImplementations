# Sample NR-1 Compliance Framework - Security & Data Protection Clauses
# This data source is shared between Multi-Agent and Multi-Tool implementations
import json


with open("nr_1_docs.json", "r", encoding="utf-8") as f:
    NR1_FRAMEWORK = json.load(f)

with open('nr1_company.json', 'r', encoding='utf-8') as file:
    SAMPLE_DOCUMENT = json.load(file)

def get_nr1_requirements():
    """Retrieve all NR-1 compliance requirements"""
    return NR1_FRAMEWORK

def get_company_document():
    """Retrieve the company's security/compliance document"""
    return SAMPLE_DOCUMENT

def get_requirement_by_id(req_id: str):
    """Get specific NR-1 requirement by ID"""
    return NR1_FRAMEWORK.get(req_id)

def get_requirements_by_category(category: str):
    """Filter requirements by category"""
    return {k: v for k, v in NR1_FRAMEWORK.items() if v.get("category") == category}

def get_critical_requirements():
    """Get all critical-severity requirements"""
    return {k: v for k, v in NR1_FRAMEWORK.items() if v.get("severity") == "Critical"}
