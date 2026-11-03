import json
from pathlib import Path

import pandas as pd
import streamlit as st

from app.evaluation.evaluator import evaluate_dataset

st.set_page_config(
    page_title="LLM Evaluation Platform",
    page_icon="📊",
    layout="wide",
)

st.title("LLM Evaluation & Guardrails Platform")
st.caption("Evaluate response quality, groundedness and safety.")

dataset_path = Path("data/sample/evaluation_cases.json")

if st.button("Run Evaluation", type="primary"):
    with dataset_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    report = evaluate_dataset(cases)
    st.session_state["report"] = report

if "report" in st.session_state:
    report = st.session_state["report"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Pass Rate", f"{report['pass_rate']:.1%}")
    col2.metric("Passed", report["passed_cases"])
    col3.metric("Failed", report["failed_cases"])
    col4.metric("Overall Score", f"{report['average_score']:.1%}")

    st.subheader("Evaluation Metrics")

    metrics = pd.DataFrame({
        "Metric": [
            "Relevance",
            "Groundedness",
            "Refusal Compliance",
        ],
        "Score": [
            report["average_relevance"],
            report["average_groundedness"],
            report["average_refusal_compliance"],
        ],
    })

    st.bar_chart(metrics.set_index("Metric"))

    st.subheader("Individual Test Results")

    results = pd.DataFrame(report["results"])
    st.dataframe(results, use_container_width=True)

else:
    st.info("Click Run Evaluation to evaluate the sample dataset.")