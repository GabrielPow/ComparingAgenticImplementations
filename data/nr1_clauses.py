import json
from pathlib import Path

# Get the directory where THIS script lives (i.e., the 'data' directory)
DATA_DIR = Path(__file__).parent

# Construct absolute paths to the JSON files inside the same folder
nr1_docs_path = DATA_DIR / "nr_1_docs.json"
company_doc_path = DATA_DIR / "nr1_company.json"

with open(nr1_docs_path, "r", encoding="utf-8") as f:
    NR1_FRAMEWORK = json.load(f)

with open(company_doc_path, "r", encoding="utf-8") as file:
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