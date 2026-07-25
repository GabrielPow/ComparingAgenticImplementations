import os
import sys
import asyncio
import json
from pathlib import Path

import streamlit as st

# Ensure subfolders are importable
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "multi_agents"))
sys.path.insert(0, str(ROOT / "multi_agents" / "agents"))
sys.path.insert(0, str(ROOT / "multi_tools"))
sys.path.insert(0, str(ROOT / "multi_tools" / "agents"))
sys.path.insert(0, str(ROOT / "multi_tools" / "skills"))

from evaluator import evaluate_with_judge

# Import engines
orchestrator_available = False
tools_agent_available = False

try:
    from multi_agents.agents.agents import OrchestratorAgent
    from data.nr1_clauses import get_nr1_requirements, get_company_document
    orchestrator_available = True
except Exception as e:
    orchestrator_error = e

try:
    from multi_tools.agents.gemini_ai import compliance_agent as tools_compliance_agent
    tools_agent_available = True
except Exception as e:
    tools_error = e


def run_orchestrator(query: str) -> dict:
    if not orchestrator_available:
        return {"error": f"Orchestrator unavailable: {orchestrator_error}"}

    orchestrator = OrchestratorAgent()
    nr1_framework = get_nr1_requirements()
    company_document = get_company_document()

    result = asyncio.run(
        orchestrator.run_compliance_analysis(query, nr1_framework, company_document)
    )
    return result


def run_tools_agent(query: str) -> dict:
    if not tools_agent_available:
        return {"error": f"Multi-Tools agent unavailable: {tools_error}"}

    result = tools_compliance_agent(query)
    return result


def save_json(result: dict, filename: str) -> str:
    path = ROOT / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return str(path)


def run_single_mode():
    st.markdown("Enter a compliance query to run through your agent pipeline.")
    
    mode = st.selectbox(
        "Engine",
        (
            "Multi-Agents (orchestrator with multiple agent roles)",
            "Multi-Tools (single agent that calls internal tools)",
        ),
    )

    default_query = "Is our company compliant with NR-1 data encryption requirements?"
    query = st.text_area("Compliance query", value=default_query, height=120)

    if st.button("Run Analysis"):
        with st.spinner("Running analysis..."):
            try:
                if mode.startswith("Multi-Agents"):
                    result = run_orchestrator(query)
                else:
                    result = run_tools_agent(query)
            except Exception as e:
                st.error(f"Execution error: {e}")
                return

            st.success("Analysis complete")
            st.subheader("Result JSON")
            st.json(result)


def run_evaluation_mode():
    st.markdown("### LLM-as-a-Judge Evaluation & Benchmarking")
    
    dataset_path = ROOT / "nr1_benchmark.json"
    if not dataset_path.exists():
        st.error("`eval_dataset.json` not found in root path. Please create it first.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    engine_choice = st.radio(
        "Select Engine to Benchmark:",
        ["Multi-Agents", "Multi-Tools"],
        horizontal=True
    )

    if st.button("Run Batch Benchmark"):
        results = []
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(dataset):
            st.write(f"Evaluating **[{item['id']}] Level {item['level']}**...")
            
            # 1. Run Query through Selected Engine
            if engine_choice == "Multi-Agents":
                output = run_orchestrator(item["query_pt"])
            else:
                output = run_tools_agent(item["query_pt"])
            
            raw_text = json.dumps(output, ensure_ascii=False)

            # 2. Judge with LLM
            judge_res = evaluate_with_judge(item, raw_text)

            results.append({
                "id": item["id"],
                "level": item["level"],
                "query": item["query_pt"],
                "score": judge_res.get("score", 0.0),
                "matched": judge_res.get("matched_points", []),
                "missed": judge_res.get("missed_points", []),
                "hallucinations": judge_res.get("hallucination_flags", []),
                "explanation": judge_res.get("explanation", "")
            })
            progress_bar.progress((idx + 1) / len(dataset))

        st.success("Benchmark completed!")

        # Step 4: Display Aggregate Metrics
        st.subheader("Aggregated Metrics")
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        total_hallucinations = sum(len(r["hallucinations"]) for r in results)

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Accuracy Score", f"{avg_score * 100:.1f}%")
        col2.metric("Total Items Tested", len(results))
        col3.metric("Total Hallucination Flags", total_hallucinations)

        # Per-Level Aggregation Table
        st.write("#### Performance by Level")
        level_scores = {}
        for r in results:
            lvl = f"Level {r['level']}"
            level_scores.setdefault(lvl, []).append(r["score"])
        
        level_summary = [
            {"Level": lvl, "Average Score": f"{(sum(scores)/len(scores))*100:.1f}%", "Sample Count": len(scores)}
            for lvl, scores in level_scores.items()
        ]
        st.table(level_summary)

        # Step 5: Item-by-Item Breakdown Explorer
        st.subheader("Item Breakdown Explorer")
        for r in results:
            with st.expander(f"[{r['id']}] Level {r['level']} — Score: {r['score']*100:.0f}%"):
                st.write(f"**Query:** {r['query']}")
                st.write(f"**Judge Explanation:** {r['explanation']}")
                st.write(f"**Matched Points:** {r['matched']}")
                st.write(f"**Missed Points:** {r['missed']}")
                if r["hallucinations"]:
                    st.warning(f"**Hallucinations:** {r['hallucinations']}")


def main():
    st.set_page_config(page_title="Compliance Explorer & Evaluator", layout="wide")
    st.title("LLama-Agents — Compliance Analysis & Benchmark")

    tab1, tab2 = st.tabs(["Single Query Runner", "LLM Judge Evaluation Suite"])

    with tab1:
        run_single_mode()

    with tab2:
        run_evaluation_mode()


if __name__ == "__main__":
    main()