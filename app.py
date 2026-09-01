# =============================================================================
# AUTOVOLT AI — V52.1 GLOBAL PILOT DASHBOARD (ENGLISH EDITION)
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, PilotEvidenceLog

st.set_page_config(page_title="AutoVolt AI — Pilot Evidence Ready v52.1", page_icon="⚡", layout="wide")

st.markdown('<div style="font-size:2.4rem; font-weight:700; color:#1E3A8A;">⚡ AutoVolt AI Core Dashboard</div>', unsafe_allow_html=True)
st.caption(f"Production Pilot Ingestion Layer & ESG Evidence Gateway — Version {VERSION}")

st.sidebar.header("⚙️ Data Ingestion Controls")
industry = st.sidebar.selectbox("Target Industrial Profile", list(INDUSTRY_PROFILES.keys()))

st.markdown("### 📊 Step 1: Telemetry Data Import")
uploaded_file = st.file_uploader("Upload Industrial Sensor Dataset (CSV / Excel / TXT)", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            raw_df = pd.read_excel(uploaded_file)
        else:
            raw_df = pd.read_csv(uploaded_file)
            
        st.success("✅ Dataset structure successfully ingested and parsed.")
        
        # 🔍 Data Quality Check Inscription
        missing_count = int(raw_df.isna().sum().sum())
        if missing_count > 0:
            st.warning(f"⚠️ **Data Quality Telemetry Alert:** Data gaps detected! There are ({missing_count}) missing values rendered as (None) in the stream. Verify sensor physical connectivity.")
        else:
            st.success("🎯 **Data Quality Inscription:** Integrity check passed. Telemetry stream is 100% complete with no missing values detected.")
            
        st.dataframe(raw_df.head(5))
        
        st.markdown("---")
        st.markdown("### 📝 Step 2: Pilot Evidence Registry (ESG Bankable Audit Trail)")
        st.info("Formulate this registry in cooperation with the plant engineer to securely log deployment case studies for institutional funding.")
        
        col1, col2 = st.columns(2)
        with col1:
            exp_id = st.text_input("Pilot Deployment Experiment ID", value="PILOT-001")
            factory_id = st.text_input("Facility / Factory Identifier", placeholder="e.g., Central Metal Smelting Works")
        with col2:
            engineer_review = st.selectbox("On-Site Engineering Prediction Validation", ["Validated and strictly matched operational anomaly", "Requires calibration and parametric adjustments", "Normal baseline telemetry matching reality"])
            action_taken = st.text_input("Mitigation / Corrective Action Taken", placeholder="e.g., Machine isolation and immediate bearing maintenance schedule")
            
        engineer_notes = st.text_area("Detailed Engineering Analytical Observations & Field Notes")
        
        if st.button("🚀 Execute AutoVolt Core & Construct Official Evidence Manifest", type="primary"):
            log_entry = PilotEvidenceLog(
                experiment_id=exp_id,
                factory_id=factory_id,
                engineer_review=engineer_review,
                engineer_notes=engineer_notes,
                action_taken=action_taken
            )
            
            pipeline = AutoVoltPipeline(industry)
            final_report = pipeline.run(raw_df, evidence_log=log_entry)
            
            # Injecting missing metrics for global sustainability audits
            final_report["data_summary"]["missing_sensors_detected"] = missing_count
            
            st.success("🟢 Data processing complete. Pilot Evidence File generated successfully!")
            st.json(final_report)
            
            report_json = json.dumps(final_report, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Official Evidence Manifest (Pilot Evidence JSON)",
                data=report_json,
                file_name=f"AutoVolt_Evidence_{factory_id}_{exp_id}.json",
                mime="application/json"
            )
    except Exception as e:
        st.error(f"Structural runtime ingestion failure: {str(e)}")

