import json
from pathlib import Path

import requests
import streamlit as st

from app.orchestrator import PolicyAnalysisOrchestrator
from app.schemas import PolicyInput


st.set_page_config(page_title="Government Policy Agent", layout="wide")
st.title("Government Policy Analyst Agent")

api_url = st.sidebar.text_input("API URL", value="http://127.0.0.1:8000")
run_mode = st.sidebar.radio("Run mode", ["Local Python", "FastAPI"], horizontal=True)

title = st.text_input("Policy title", value="Digital Public Infrastructure Governance Rules")
jurisdiction = st.text_input("Jurisdiction", value="India")
policy_text = st.text_area("Policy text", height=220)
urls_text = st.text_area("Source URLs, one per line", height=100)
analysis_depth = st.selectbox("Analysis depth", ["rapid", "standard", "deep"], index=1)

if st.button("Run analysis", type="primary"):
    payload = {
        "title": title,
        "jurisdiction": jurisdiction,
        "policy_text": policy_text,
        "urls": [line.strip() for line in urls_text.splitlines() if line.strip()],
        "analysis_depth": analysis_depth,
    }
    try:
        if run_mode == "FastAPI":
            response = requests.post(f"{api_url}/analyze", json=payload, timeout=60)
            response.raise_for_status()
            report = response.json()
        else:
            report_obj = PolicyAnalysisOrchestrator().analyze(PolicyInput(**payload))
            report = report_obj.model_dump(mode="json")

        consensus = report["consensus"]
        col1, col2 = st.columns(2)
        col1.metric("Recommendation", consensus["recommendation"])
        col2.metric("Directional confidence", f'{consensus["directional_confidence_score"]}/100')

        tab_memo, tab_findings, tab_evidence, tab_json = st.tabs(
            ["Final Memo", "Agent Findings", "Evidence Log", "JSON Output"]
        )
        with tab_memo:
            st.markdown(report["memo_markdown"])
        with tab_findings:
            for finding in report["findings"]:
                st.subheader(finding["agent_name"])
                st.write(finding["summary"])
                st.write("Recommendation:", finding["recommendation"])
                st.progress(finding["confidence_score"] / 100)
                st.write(finding["key_points"])
        with tab_evidence:
            st.dataframe(report["evidence"], use_container_width=True)
        with tab_json:
            st.json(report)
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")

st.sidebar.caption(f"Reports are saved under {Path('app/data/reports').resolve()}")

