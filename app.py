import os
import sys
import asyncio
import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "multi_agents"))
sys.path.insert(0, str(ROOT / "multi_agents" / "agents"))
sys.path.insert(0, str(ROOT / "multi_tools"))
sys.path.insert(0, str(ROOT / "multi_tools" / "agents"))
sys.path.insert(0, str(ROOT / "multi_tools" / "skills"))

orchestrator_available = False
tools_agent_available = False

try:
    from multi_agents.agents.agents import OrchestratorAgent
    from data.nr1_clauses import get_nr1_requirements
    orchestrator_available = True
except Exception as e:
    orchestrator_error = e

try:
    from multi_tools.agents.gemini_ai_tools import compliance_agent as tools_compliance_agent
    tools_agent_available = True
except Exception as e:
    tools_error = e


# Ground-Truth Audit Matrix based on the 11 injected compliance traps
GROUND_TRUTH_MATRIX = [
    {
        "clause_key": "pgr_retention",
        "expected_status": "Non-compliant",
        "violation": "Retention is set to 5 years, but NR-1 mandates keeping risk inventory update history for at least 20 years.",
        "reference": "NR-1.5.7.3.3"
    },
    {
        "clause_key": "pgr_review_cadence",
        "expected_status": "Non-compliant",
        "violation": "Standard review is biennial (2 years). Major process changes or new equipment require immediate anticipated review.",
        "reference": "NR-1.5.4.4.6 / NR-1.5.4.2.1"
    },
    {
        "clause_key": "hierarchy_of_controls",
        "expected_status": "Non-compliant",
        "violation": "PPE (EPI) cannot be primary; controls must follow: Elimination -> Collective Protection (EPC) -> Administrative -> PPE.",
        "reference": "NR-1.4.1 (g)"
    },
    {
        "clause_key": "right_of_refusal",
        "expected_status": "Non-compliant",
        "violation": "Workers can interrupt work immediately upon reasonable suspicion of imminent danger without prior written approval.",
        "reference": "NR-1.4.3 / NR-1.4.3.2"
    },
    {
        "clause_key": "contractor_management",
        "expected_status": "Non-compliant",
        "violation": "The host organization's PGR must extend prevention measures to third parties and MEIs working on-site.",
        "reference": "NR-1.5.8.1 / NR-1.8.1.1"
    },
    {
        "clause_key": "training_certification",
        "expected_status": "Non-compliant",
        "violation": "Attendance lists do not replace individual signed certificates containing workload, syllabus, and technical responsible details.",
        "reference": "NR-1.7.1.1 / NR-1.7.3"
    },
    {
        "clause_key": "ead_practical_training",
        "expected_status": "Non-compliant",
        "violation": "Practical heavy machinery training via distance learning (EAD) is prohibited unless explicitly allowed by specific NRs (e.g., NR-12).",
        "reference": "NR-1.7.9.1 / Anexo II"
    },
    {
        "clause_key": "digital_documentation",
        "expected_status": "Non-compliant",
        "violation": "Digitized SST documents require an ICP-Brasil digital certificate and encryption/security measures.",
        "reference": "NR-1.6.3 / NR-1.6.4"
    },
    {
        "clause_key": "harassment_prevention",
        "expected_status": "Non-compliant",
        "violation": "Anti-harassment training must occur at least every 12 months, and whistleblowing procedures must guarantee anonymity.",
        "reference": "NR-1.4.1.1"
    },
    {
        "clause_key": "trade_union_access",
        "expected_status": "Non-compliant",
        "violation": "PGR documents must be always available to trade unions and inspectors. Commercial secrecy cannot override transparency.",
        "reference": "NR-1.5.7.2.1"
    },
    {
        "clause_key": "post_accident_protocol",
        "expected_status": "Non-compliant",
        "violation": "Serious accidents require a documented cause analysis, an anticipated risk review, and potential eventual training.",
        "reference": "NR-1.5.5.5.1 / NR-1.5.4.4.6"
    }
]


def run_orchestrator(query: str, company_doc: dict) -> dict:
    if not orchestrator_available:
        return {"error": f"Orchestrator unavailable: {orchestrator_error}"}

    orchestrator = OrchestratorAgent()
    nr1_framework = get_nr1_requirements()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                orchestrator.run_compliance_analysis(query, nr1_framework, company_doc)
            )
    except RuntimeError:
        pass

    return asyncio.run(orchestrator.run_compliance_analysis(query, nr1_framework, company_doc))


def run_tools_agent(query: str) -> dict:
    if not tools_agent_available:
        return {"error": f"Multi-Tools agent unavailable: {tools_error}"}

    return tools_compliance_agent(query)


def run_audit_mode():
    st.markdown("### 📋 Single-Document Audit Runner (NR-1 Compliance)")
    st.caption("Upload or paste a target company document to perform an automated full audit in a single API call.")

    # 1. Load default company document with injected traps
    company_doc_path = "data\\nr1_company.json"
    default_json_str = "{}"
    if not company_doc_path:
        with open(company_doc_path, "r", encoding="utf-8") as f:
            default_json_str = f.read()

    col_doc, col_opts = st.columns([1, 1])

    with col_doc:
        st.subheader("1. Target Company Document")
        json_input = st.text_area(
            "Company Document JSON (`company_document.json`)",
            value=default_json_str,
            height=300
        )
        try:
            company_doc = json.loads(json_input)
        except Exception as e:
            st.error(f"Invalid JSON format: {e}")
            company_doc = None

    with col_opts:
        st.subheader("2. Audit Execution Settings")
        engine_choice = st.radio(
            "Select Engine:",
            ["Multi-Agents", "Multi-Tools"],
            horizontal=True
        )

        audit_prompt = (
            "Você é um auditor sênior de Segurança e Saúde no Trabalho (SST) especialista na Norma Regulamentadora nº 1 (NR-1). "
            "Analise a política de SST da empresa anexada. Para cada cláusula presente no documento: "
            "1. Identifique se está em Conformidade ou Não Conformidade com a NR-1. "
            "2. Explique objetivamente o motivo de qualquer violação. "
            "3. Cite os itens/subitens específicos da NR-1 correspondentes."
        )
        query = st.text_area("Audit Instruction Prompt", value=audit_prompt, height=150)

        run_btn = st.button("🚀 Run Full Document Audit", use_container_width=True)

    # 2. Execution logic
    if run_btn and company_doc:
        with st.spinner("Analyzing document against NR-1 rules..."):
            try:
                # Append the full document string into the prompt context for tools engine
                full_query = f"{query}\n\nDocumento a analisar:\n{json.dumps(company_doc, ensure_ascii=False)}"
                
                if engine_choice == "Multi-Agents":
                    result = run_orchestrator(query, company_doc)
                else:
                    result = run_tools_agent(full_query)
                
                st.session_state.audit_result = result
                st.success("Audit Completed!")
            except Exception as e:
                st.error(f"Execution error: {e}")

    # 3. Side-by-side Results & Evaluation Matrix
    if "audit_result" in st.session_state:
        st.divider()
        st.subheader("3. Audit Report vs. Ground-Truth Matrix")

        # Added a new tab "📝 Clean Audit Report"
        tab_text, tab_report, tab_matrix = st.tabs([
            "📝 Clean Audit Report", 
            "🤖 Raw JSON Output", 
            "🎯 Ground-Truth Evaluation Matrix"
        ])

        result = st.session_state.audit_result

        with tab_text:
            st.markdown("### Executive Audit Summary")
            
            # Helper to pull text regardless of exact key name returned by your agent
            extracted_text = ""
            if isinstance(result, dict):
                extracted_text = (
                    result.get("agent_summary") or 
                    result.get("response") or 
                    result.get("output") or 
                    result.get("result") or 
                    ""
                )
            elif isinstance(result, str):
                extracted_text = result

            if extracted_text:
                st.markdown(extracted_text)
            else:
                st.warning("Could not automatically locate the plain text field in the output dictionary. Check the 'Raw JSON Output' tab.")

        with tab_report:
            st.json(result)

        with tab_matrix:
            st.markdown("Compare the model's audit findings against the 11 injected violations:")
            
            # Interactive Human-Scoring Matrix
            score_count = 0
            total_traps = len(GROUND_TRUTH_MATRIX)

            for idx, item in enumerate(GROUND_TRUTH_MATRIX):
                with st.expander(f"Key: `{item['clause_key']}` | Ref: {item['reference']}"):
                    st.write(f"**Expected Violation:** {item['violation']}")
                    caught = st.checkbox(
                        f"Model correctly flagged violation for `{item['clause_key']}`?", 
                        key=f"trap_{idx}"
                    )
                    if caught:
                        score_count += 1

            # Summary Metric
            st.metric(
                "Human Audit Precision Score", 
                f"{(score_count / total_traps) * 100:.1f}%", 
                delta=f"{score_count}/{total_traps} Traps Caught"
            )


def main():
    st.set_page_config(page_title="SST Compliance Audit Suite", layout="wide")
    st.title("🛡️ NR-1 SST Compliance Document Auditor")

    run_audit_mode()


if __name__ == "__main__":
    main()