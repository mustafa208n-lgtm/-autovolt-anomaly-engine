# =============================================================================
# AUTOVOLT AI — V52.9-MASTER WITH DEVELOPER BYPASS & SUBSCRIPTION GATEWAY
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, PilotEvidenceLog

st.set_page_config(page_title="AutoVolt AI — Secure Enterprise Licensing v52.9", page_icon="⚡", layout="wide")

# 🔑 MASTER OWNER KEY (Never expires, unlocks everything for you)
MASTER_KEY = "AV-MASTER-MUSTAFA"

# 🔒 CLIENT SUBSCRIPTION REGISTRY (Keys expire after 30 days for factories)
LICENSE_REGISTRY = {
    "AV-SPAIN-IRON-9921X": {"factory": "Madrid Heavy Metals Works", "expiry": "2026-10-01", "status": "ACTIVE"},
    "AV-BAGHDAD-STEEL-4412B": {"factory": "Central Steel Smelting Plant", "expiry": "2026-10-15", "status": "ACTIVE"},
    "AV-TEST-KEY-2026": {"factory": "Global Pilot Test Lab", "expiry": "2026-09-30", "status": "ACTIVE"}
}

st.markdown('<div style="font-size:2.4rem; font-weight:700; color:#1E3A8A;">⚡ AutoVolt AI Green Industrial Core</div>', unsafe_allow_html=True)
st.caption(f"Production Pilot Ingestion Layer & ESG Evidence Gateway — Version {VERSION}")

# 📦 GATEWAY LAYER: Subscription Key Validation Box
st.markdown("### 🔐 Security & Licensing Gateway")
user_key = st.text_input("Enter Your Encrypted Subscription Key or Master Pass:", type="password", help="Provide your 30-day client token or the Master Admin Pass.")

# Core Authentication Logic
is_authenticated = False
current_factory_name = "Unauthorized Client"
is_master_owner = False

if user_key:
    # ⚡ Check 1: Developer Master Bypass
    if user_key == MASTER_KEY:
        is_authenticated = True
        is_master_owner = True
        current_factory_name = "AutoVolt Owner / Admin Mode"
        st.success("👑 **Master Access Granted:** Welcome back, Mustafa. Admin Environment fully unlocked with lifetime commercial privileges.")
    
    # 🔒 Check 2: Standard Corporate Clients
    elif user_key in LICENSE_REGISTRY:
        license_info = LICENSE_REGISTRY[user_key]
        expiry_date = datetime.strptime(license_info["expiry"], "%Y-%m-%d")
        
        if datetime.utcnow() < expiry_date and license_info["status"] == "ACTIVE":
            is_authenticated = True
            current_factory_name = license_info["factory"]
            st.success(f"🔓 **Access Granted:** License authenticated for **[{current_factory_name}]**. Subscription active until: {license_info['expiry']}.")
        else:
            st.error(f"❌ **License Expired:** This subscription expired on {license_info['expiry']}. Ingestion layer locked.")
    else:
        st.error("❌ **Invalid Token:** The signature or license key entered is not registered in AutoVolt secure vault.")
else:
    st.info("🔒 **System Locked:** Provide your Master Pass or a valid 30-day enterprise activation key to initialize the runtime.")

# =============================================================================
# PROTECTED RUNTIME ENVIRONMENT (Executes ONLY if is_authenticated is True)
# =============================================================================
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
            
            # Data Quality Check Inscription
            missing_count = int(raw_df.isna().sum().sum())
            if missing_count > 0:
                st.warning(f"⚠️ **Data Quality Telemetry Alert:** {missing_count} data gaps detected! Missing values isolated as (None) to prevent grid arithmetic corruption.")
                
                # Ultra-Safe Patch: Isolate timestamp and strictly force numeric translation before interpolation
                numeric_df = raw_df.copy()
                for col in numeric_df.columns:
                    if "time" not in col.lower() and "date" not in col.lower():
                        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")
                
                st.info("💡 **Algorithmic Treatment Active:** AutoVolt core has executed mathematical linear interpolation to temporarily reconstruct the telemetry stream for signal continuity.")
                interpolated_numeric = numeric_df.drop(columns=[col for col in numeric_df.columns if "time" in col.lower() or "date" in col.lower()], errors='ignore').interpolate(method='linear').fillna(method='bfill')
                
                processed_df = raw_df.copy()
                for col in interpolated_numeric.columns:
                    processed_df[col] = interpolated_numeric[col]
            else:
                st.success("🎯 **Data Quality Inscription:** Integrity check passed. Telemetry stream is 100% complete with no missing values detected.")
                processed_df = raw_df.copy()
                
            st.markdown("#### Raw Ingested Stream (First 5 Rows)")
            st.dataframe(raw_df.head(5))
            
            if missing_count > 0:
                st.markdown("#### Algorithmic Reconstructed Stream (Continuity Safe)")
                st.dataframe(processed_df.head(5))
            
            st.markdown("---")
            st.markdown("### 📝 Step 2: Pilot Evidence Registry (ESG Bankable Audit Trail)")
            st.info(f"Logging active for authenticated client: **{current_factory_name}**")
            
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
                engineer_review = st.selectbox("On-Site Engineering Prediction Validation", ["Validated and strictly matched operational anomaly", "Requires calibration and parametric adjustments", "Normal baseline telemetry matching reality"])
                action_taken = st.text_input("Mitigation / Corrective Action Taken", placeholder="e.g., Machine isolation and immediate bearing maintenance schedule")
                
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
                
                st.success("🟢 Data processing complete. Pilot Evidence File generated successfully with Dual-Action Sustainability Metrics!")
                
                # 📊 Visualizing the separate Dual Sustainability metrics side-by-side
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric(label="📉 Energy Waste Reduction (⚡ Electricity Saved)", value=f"{final_report['green_sustainability_metrics']['energy_waste_reduction_kwh']} kWh")
                with metric_col2:
                    st.metric(label="🌱 Carbon Emissions Avoided (📉 CO2 Footprint Lowered)", value=f"{final_report['green_sustainability_metrics']['carbon_emissions_avoided_kg_co2']} kg CO2")
                
                # THE SECURITY RED BOX: Explicit Engineering Disclaimer & Liability Shield
                st.error("⚠️ **Engineering Responsibility Disclaimer & Operational Advisory:**\n\n"
                         "This analytical report functions strictly as a diagnostic baseline for statistical anomalies and data stream validation. "
                         "It does **NOT** constitute a final, definitive mechanical repair verdict or physical engineering certification.\n\n"
                         "**Mandatory Safety Action Required:** On-site plant engineers, field technicians, and specialized mechanical experts **MUST** "
                         "be consulted to physically audit the machinery, inspect sensor physical connectivity, and verify conditions on the shop floor before executing any hardware modifications or operational shut-downs.")
                
                st.json(final_report)
                
                report_json = json.dumps(final_report, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download Official Evidence Manifest (Pilot Evidence JSON)",
                    data=report_json,
                    file_name=f"AutoVolt_Evidence_{display_factory}_{exp_id}.json",
                    mime="application/json"
                )
        except Exception as e:
