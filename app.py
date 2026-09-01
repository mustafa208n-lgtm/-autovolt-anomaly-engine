# =============================================================================
# AUTOVOLT AI — V53.0 CLEAN SUSTAINABLE INDUSTRIAL CORE (OPEN ACCESS)
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, PilotEvidenceLog

st.set_page_config(page_title="AutoVolt AI — Green Industrial Core v53.0", page_icon="⚡", layout="wide")

st.markdown('<div style="font-size:2.4rem; font-weight:700; color:#1E3A8A;">⚡ AutoVolt AI Green Industrial Core</div>', unsafe_allow_html=True)
st.caption(f"Production Pilot Ingestion Layer & ESG Evidence Gateway — Version {VERSION}")

# Open Access Environment (No Password Gateway Required)
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
            
            # Safe pandas chaining conversion for signal continuity
            interpolated_numeric = numeric_df.drop(columns=time_cols, errors='ignore').interpolate().bfill()
            
            processed_df = raw_df.copy()
            for col in interpolated_numeric.columns:
                processed_df[col] = interpolated_numeric[col]
        else:
            st.success("🎯 **Data Quality Inscription:** Integrity check passed. Telemetry stream is complete.")
            processed_df = raw_df.copy()
            
        st.markdown("#### Raw Ingested Stream (First 5 Rows)")
        st.dataframe(raw_df.head(5))
        
        if missing_count > 0:
            st.markdown("#### Algorithmic Reconstructed Stream (Continuity Safe)")
            st.dataframe(processed_df.head(5))
            
        # 📈 محرك الرسم المباشر الفوري فور رفع الملف:
        st.markdown("#### 📈 Interactive Temporal Fleet Anomaly Analysis")
        chart_cols = [col for col in processed_df.columns if "time" not in col.lower() and "date" not in col.lower()]
        if chart_cols:
            st.line_chart(processed_df[chart_cols])
        
        st.markdown("---")
        st.markdown("### 📝 Step 2: Pilot Evidence Registry (ESG Bankable Audit Trail)")
        st.info("Formulate this registry in cooperation with the plant engineer to securely log deployment case studies.")
        
        col1, col2 = st.columns(2)
        with col1:
            exp_id = st.text_input("Pilot Deployment Experiment ID", value="PILOT-001")
            factory_id = st.text_input("Facility / Factory Identifier", placeholder="e.g., Central Manufacturing Plant")
        with col2:
            engineer_review = st.selectbox("On-Site Engineering Validation", ["Validated and strictly matched operational anomaly", "Requires calibration and parametric adjustments", "Normal baseline telemetry matching reality"])
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
            final_report["data_summary"]["missing_sensors_detected"] = missing_count
            
            st.success("🟢 Data processing complete. Pilot Evidence File generated successfully with Dual-Action Sustainability Metrics!")
            
            # 📊 عرض بطاقات وفورات الطاقة والكربون المزدوجة صراحة
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(label="Energy Saved (⚡ Electricity Saved)", value=f"{final_report['green_sustainability_metrics']['energy_waste_reduction_kwh']} kWh")
            with metric_col2:
                st.metric(label="CO2 Reduced (🌱 CO2 Footprint Lowered)", value=f"{final_report['green_sustainability_metrics']['carbon_emissions_avoided_kg_co2']} kg CO2")
            
            # 🛡️ صندوق الأمان وإخلاء المسؤولية القانوني لحمايتك أمام وزارة الصناعة الإسبانية
            st.error("⚠️ **Engineering Responsibility Disclaimer & Operational Advisory:**\n\n"
                     "This analytical report functions strictly as a diagnostic baseline for statistical anomalies and data stream validation. "
                     "It does NOT constitute a final, definitive mechanical repair verdict or physical engineering certification.\n\n"
                     "**Mandatory Safety Action Required:** On-site plant engineers, field technicians, and specialized mechanical experts MUST "
                     "be consulted to physically audit the machinery, inspect sensor physical connectivity, and verify conditions on the shop floor before executing any hardware modifications or operational shut-downs.")
            
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

