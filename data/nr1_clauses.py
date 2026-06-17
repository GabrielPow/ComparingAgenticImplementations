# Sample NR-1 Compliance Framework - Security & Data Protection Clauses
# This data source is shared between Multi-Agent and Multi-Tool implementations

NR1_FRAMEWORK = {
    "NR-1.1": {
        "title": "Data Encryption",
        "requirement": "All sensitive data must be encrypted at rest using AES-256 or equivalent",
        "category": "Security",
        "severity": "Critical"
    },
    "NR-1.2": {
        "title": "Access Control",
        "requirement": "Role-based access control (RBAC) must be implemented with least privilege principle",
        "category": "Security",
        "severity": "Critical"
    },
    "NR-1.3": {
        "title": "Audit Logging",
        "requirement": "All access to sensitive data must be logged with timestamp and user identity",
        "category": "Audit",
        "severity": "High"
    },
    "NR-1.4": {
        "title": "Data Retention",
        "requirement": "Personal data must not be retained longer than 3 years after last access",
        "category": "Privacy",
        "severity": "High"
    },
    "NR-1.5": {
        "title": "Incident Response",
        "requirement": "Security incidents must be reported within 24 hours with impact assessment",
        "category": "Operations",
        "severity": "High"
    },
    "NR-1.6": {
        "title": "Third-Party Compliance",
        "requirement": "All vendors must maintain same compliance level and undergo annual audits",
        "category": "Security",
        "severity": "Medium"
    },
    "NR-1.7": {
        "title": "Data Classification",
        "requirement": "All data must be classified and handled according to sensitivity level",
        "category": "Governance",
        "severity": "High"
    },
    "NR-1.8": {
        "title": "Backup & Recovery",
        "requirement": "Backup systems must be tested quarterly with documented RTO of 4 hours",
        "category": "Operations",
        "severity": "Medium"
    }
}

SAMPLE_DOCUMENT = {
    "company": "TechCorp Inc",
    "document_type": "Security Policy",
    "clauses": {
        "data_protection": "We encrypt important data using industry standards",
        "access_control": "We use basic username/password authentication",
        "logging": "System logs are kept for 6 months in our servers",
        "retention": "We keep customer data indefinitely for business purposes",
        "incident_response": "Incidents are reviewed monthly in our security meetings",
        "vendor_management": "We occasionally check our vendors' security",
        "data_classification": "We have internal data categories (public, internal, confidential)",
        "backup": "Backups are performed weekly, recovery time unknown"
    }
}

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
