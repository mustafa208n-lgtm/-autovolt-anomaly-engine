# =============================================================================
# AUTOVOLT AI — V53.0 MASTER LICENSING CORE (ALL SECTORS ACTIVE)
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, PilotEvidenceLog

st.set_page_config(page_title="AutoVolt AI — Secure Enterprise Licensing v53.0", page_icon="⚡", layout="wide")

MASTER_KEY = "AV-MASTER-MUSTAFA"

LICENSE_REGISTRY = {
    "AV-SPAIN-IRON-9921X": {"factory": "Madrid Heavy Metals Works", "expiry": "2026-10-01", "status": "ACTIVE"},
    "AV-BAGHDAD-STEEL-4412B": {"factory": "Central Steel Smelting Plant", "expiry": "2026-10-15", "status": "ACTIVE"},
    "AV-TEST-KEY-2026": {"factory": "Global Pilot Test Lab", "expiry": "2026-09-30", "status": "ACTIVE"}
}

st.markdown('<div style="font-size:2.4rem; font-weight:700; color:#1E3A8A;">⚡ AutoVolt AI Green Industrial Core</div>', unsafe_allow_html=True)
st.caption(f"Production Pilot Ingestion Layer & ESG Evidence Gateway — Version {VERSION}")

st.markdown("### 🔐 Security & Licensing Gateway")
user_key = st.text_input("Enter Your Encrypted Subscription Key or Master Pass:", type="password")

is_authenticated = False
current_factory_name = "Unauthorized Client"
is_master_owner = False

if user_key:
    if user_key == MASTER_KEY:
        is_authenticated = True
        is_master_owner = True
        current_factory_name = "AutoVolt Owner / Admin Mode"
        st.success("👑 **Master Access Granted:** Welcome back, Mustafa. Admin Environment fully unlocked.")
    elif user_key in LICENSE_REGISTRY:
        license_info = LICENSE_REGISTRY[user_key]
        expiry_date = datetime.strptime(license_info["expiry"], "%Y-%m-%d")
        if datetime.utcnow() < expiry_date and license_info["status"] == "ACTIVE":
            is_authenticated = True
            current_factory_name = license_info["factory"]
            st.success(f"🔓 **Access Granted:** License authenticated for **[{current_factory_name}]**.")
        else:
            st.error(f"❌ **License Expired:** This subscription expired on {license_info['expiry']}.")
    else:
        st.error("❌ **Invalid Token:** The signature or license key entered is not registered.")
else:
    st.info("🔒 **System Locked:** Provide your Master Pass or a valid 30-day enterprise activation key.")

if is_authenticated:
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
            missing_count = int(raw_df.isna().sum().sum())
            
            if missing_count > 0:
                st.warning(f"⚠️ **Data Quality Telemetry Alert:** {missing_count} data gaps detected!")
                numeric_df = raw_df.copy()
                for col in numeric_df.columns:
                    if "time" not in col.lower() and "date" not in col.lower():
                        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")
                
                st.info("💡 **Algorithmic Treatment Active:** Reconstructing telemetry stream via linear interpolation.")
                time_cols = [col for col in numeric_df.columns if "time" in col.lower() or "date" in col.lower()]
                interpolated_numeric = numeric_df.drop(columns=time_cols, errors='ignore').interpolate(method='linear').fillna(method='bfill')
                
                processed_df = raw_df.copy()
                for col in interpolated_numeric.columns:
                    processed_df[col] = interpolated_numeric[col]
            else:
                st.success("🎯 **Data Quality Inscription:** Integrity check passed.")
                processed_df = raw_df.copy()
                
            st.markdown("#### Raw Ingested Stream (First 5 Rows)")
            st.dataframe(raw_df.head(5))
            
            if missing_count > 0:
                st.markdown("#### Algorithmic Reconstructed Stream")
                st.dataframe(processed_df.head(5))
            
            st.markdown("---")
            st.markdown("### 📝 Step 2: Pilot Evidence Registry (ESG Bankable Audit Trail)")
            
            col1, col2 = st.columns(2)
            with col1:
                exp_id = st.text_input("Pilot Deployment Experiment ID", value="PILOT-001")
                if is_master_owner:
                    factory_id = st.text_input("Facility / Factory Identifier", value="Custom Factory Demo")
                    display_factory = factory_id
                else:
                    factory_id = st.text_input("Facility / Factory Identifier", value=current_factory_name, disabled=True)
                    display_factory = current_factory_name
            with col2:
                engineer_review = st.selectbox("On-Site Engineering Validation", ["Validated and strictly matched operational anomaly", "Requires calibration", "Normal baseline telemetry"])
                action_taken = st.text_input("Mitigation / Corrective Action Taken", placeholder="e.g., Machine isolation")
                
            engineer_notes = st.text_area("Detailed Engineering Analytical Observations & Field Notes")
            
            if st.button("🚀 Execute AutoVolt Core & Construct Official Evidence Manifest", type="primary"):
                log_entry = PilotEvidenceLog(
                    experiment_id=exp_id,
                    factory_id=display_factory,
                    engineer_review=engineer_review,
                    engineer_notes=engineer_notes,
                    action_taken=action_taken
                )
                
                pipeline = AutoVoltPipeline(industry)
                final_report = pipeline.run(raw_df, evidence_log=log_entry)
                final_report["data_summary"]["missing_sensors_detected"] = missing_count
                
                st.success("🟢 Data processing complete. Pilot Evidence File generated successfully!")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric(label="降低能源浪费 (⚡ Energy Saved)", value=f"{final_report['green_sustainability_metrics']['energy_waste_reduction_kwh']} kWh")
                with metric_col2:
                    st.metric(label="减少碳排放 (🌱 CO2 Reduced)", value=f"{final_report['green_sustainability_metrics']['carbon_emissions_avoided_kg_co2']} kg CO2")
                
                st.error("⚠️ **Engineering Responsibility Disclaimer & Operational Advisory:**\n\nThis report functions strictly as a statistical diagnostic baseline. Plant engineers MUST be consulted before executing mechanical modifications.")
                st.json(final_report)
                
                report_json = json.dumps(final_report, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download Official Evidence Manifest (Pilot Evidence JSON)",
                    data=report_json,
                    file_name=f"AutoVolt_Evidence_{display_factory}_{exp_id}.json",
                    mime="application/json"
                )
        except Exception as e:
            st.error(f"Structural runtime ingestion failure: {str(e)}")
else:
    st.markdown('<div style="text-align:center; padding:50px; background-color:#F3F4F6; border-radius:10px; color:#6B7280; font-weight:600;">⚠️ DATA INGESTION ENGINE LOCKED — PROVIDE VALID REVENUE TOKEN TO INITIALIZE RUNTIME</div>', unsafe_allow_html=True)
