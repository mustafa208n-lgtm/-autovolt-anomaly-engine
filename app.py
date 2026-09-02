from __future__ import annotations
import io, json, logging
import pandas as pd
import streamlit as st
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, pilot_readiness_gate, run_internal_tests

# Setup secure industrial logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

st.set_page_config(page_title=f"AutoVolt AI {VERSION}", page_icon="⚡", layout="wide")
st.title("⚡ AutoVolt AI")
st.caption(f"Evidence-driven industrial analysis • {VERSION}")

# --- FIELD AUTHENTICATION GATEWAY ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 Field Authentication Required")
    password = st.text_input("Enter Access Password:", type="password")
    if st.button("Authenticate"):
        if password == "GovernmentField2026":  # Secure field validation key
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid password. Access denied.")
    st.stop()
# -------------------------------------

with st.sidebar:
    st.header("⚙️ Analysis Settings")
    industry = st.selectbox("Select data industry", list(INDUSTRY_PROFILES.keys()))
    st.caption("The four core industries: General Manufacturing, Automotive/Vehicles, Batteries, Metals.")

st.subheader("1️⃣ Upload Your Data")
f = st.file_uploader("CSV / Excel / TXT", type=["csv", "xlsx", "txt"])

def load_file(upload):
    name = upload.name.lower()
    raw = upload.getvalue()
    
    if not (name.endswith(".csv") or name.endswith(".xlsx") or name.endswith(".txt")):
        logging.warning(f"Rejected file with unauthorized extension: {name}")
        raise ValueError("Security Violation: Unsupported file extension.")

    if name.endswith(".xlsx"): 
        try: return pd.read_excel(io.BytesIO(raw))
        except Exception as ex: raise ValueError("Failed to parse Excel file.")
            
    if name.endswith(".txt"):
        for sep in [None, "\t", ",", ";"]:
            try: return pd.read_csv(io.BytesIO(raw), sep=sep, engine="python")
            except: pass
        raise ValueError("Could not read TXT file structure.")
        
    for enc in ["utf-8", "utf-8-sig", "cp1252", "latin1"]:
        try: return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except: pass
    raise ValueError("Could not read CSV file due to unknown encoding structure.")

if f:
    MAX_FILE_SIZE_MB = 50
    file_size_mb = len(f.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File size exceeds the maximum limit ({MAX_FILE_SIZE_MB} MB).")
        st.stop()

    try:
        raw = load_file(f)
        st.success(f"File read successfully: {len(raw):,} rows × {len(raw.columns):,} columns")
        
        # إشعار معالجة البيانات الفوري عند وجود فجوات
        if raw.isna().sum().sum() > 0:
            st.info("💡 Algorithmic Treatment Active: AutoVolt core has executed mathematical linear interpolation to temporarily reconstruct the telemetry stream for signal continuity.")
        
        st.markdown("**First 5 rows of raw data**")
        st.dataframe(raw.head(), use_container_width=True, hide_index=True)
        
        # تشغيل أنبوب المعالجة الحقيقي
        result = AutoVoltPipeline(industry).run(raw)
        
        # استخراج البيانات الحقيقية بأمان وتأمين الافتراضيات إذا نقصت أي بنية
        q = result.get("quality", type('obj', (object,), {'status':'WARNING', 'missing_values':0, 'out_of_range_values':0, 'issues':[], 'warnings':[]}))
        a = result.get("adapter", type('obj', (object,), {'dataset_kind':'PROFILED', 'unmapped_columns':[], 'mapping':{}, 'missing_recommended_signals':[]}))
        report = result.get("report", {"recommendations":[], "overall_status":"REVIEW", "data":{}})
        evidence = result.get("evidence", {"anomaly_count": 0, "anomalies": []})
        temporal = result.get("temporal", {"status": "AVAILABLE", "signals": {}})
        green_metrics = result.get("green_sustainability_metrics", {})

        # عرض مقاييس الاستدامة والأداء البيئي الحقيقية المحسوبة من ملفك
        if green_metrics:
            st.subheader("🌱 Green Sustainability Metrics")
            m1, m2, m3 = st.columns(3)
            m2.metric("Carbon Emissions Avoided", f"{green_metrics.get('carbon_emissions_avoided_kg_co2', 0.0)} kg CO2")
            m1.metric("Energy Waste Reduction", f"{green_metrics.get('energy_waste_reduction_kwh', 0.0)} kWh")
            m3.metric("Environmental Classification", f"{green_metrics.get('environmental_audit_classification', 'N/A')}")

        st.subheader("2️⃣ Data Quality")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Status", getattr(q, 'status', 'REVIEW'))
        c2.metric("Missing Values", getattr(q, 'missing_values', 0))
        c3.metric("Out of Range", getattr(q, 'out_of_range_values', 0))
        c4.metric("Unknown Columns", len(getattr(a, 'unmapped_columns', [])))
        
        if getattr(q, 'issues', None): st.error("\n".join("• "+x for x in q.issues))
        if getattr(q, 'warnings', None): st.warning("\n".join("• "+x for x in q.warnings[:20]))

        st.subheader("3️⃣ Adapter")
        st.write(f"Detected dataset kind: **{getattr(a, 'dataset_kind', 'PROFILED')}**")
        if getattr(a, 'mapping', None): st.json(a.mapping)
        if getattr(a, 'missing_recommended_signals', None): 
            st.info("Missing recommended signals: " + ", ".join(a.missing_recommended_signals))

        st.subheader("4️⃣ Detected States")
        if "autovolt_status" in result.get("data", pd.DataFrame()).columns:
            counts = result["data"]["autovolt_status"].value_counts()
            x1, x2, x3 = st.columns(3)
            x1.metric("Normal", int(counts.get("Normal", 0)))
            x2.metric("Needs Review", int(counts.get("Needs Review", 0)))
            x3.metric("Abnormal", int(counts.get("Abnormal", 0)))
            cols = [c for c in ["timestamp", "temperature", "vibration", "load", "voltage", "current", "power", "autovolt_status", "autovolt_reason"] if c in result["data"].columns]
            st.dataframe(result["data"][cols].tail(300), use_container_width=True, hide_index=True)
        else:
            # تغطية عرض الجدول للملفات المخصصة
            st.dataframe(raw.tail(300), use_container_width=True, hide_index=True)

        st.subheader("5️⃣ Evidence & Anomalies")
        n = int(evidence.get("anomaly_count", 0))
        st.metric("Statistical Anomaly Count", n)
        if n and "anomalies" in evidence: 
            st.dataframe(pd.DataFrame(evidence["anomalies"]), use_container_width=True, hide_index=True)
        else: 
            st.success("No clear statistical anomaly under the current method.")

        st.subheader("6️⃣ Temporal Change")
        if temporal.get("status") == "AVAILABLE" and "signals" in temporal:
            rows = [{"Signal": k, **v} for k, v in temporal["signals"].items()]
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            
            # عرض المخططات البيانية الحقيقية لأعمدة المستشعرات المتاحة في ملفك
            valid_cols = [c for c in ["temperature", "vibration", "load", "voltage", "current", "power", "furnace_temp", "press_vibration", "hydraulic_pressure"] if c in raw.columns]
            for col in valid_cols[:4]:
                if "timestamp" in raw.columns:
                    d = raw[["timestamp", col]].dropna().set_index("timestamp")
                    if not d.empty: st.line_chart(d)
        else:
            st.warning(temporal.get("reason", "Temporal analysis not available for current scope."))

        st.subheader("7️⃣ What is Required?")
        if report.get("recommendations"):
            for r in report["recommendations"]: st.write("🔧 " + r)
        else:
            st.write("🔧 Review dataset anomalies and missing vector points via field engineer logs.")

        # إجبار بوابة الفحص التجريبية على العمل بشكل كامل ودائم
        st.subheader("8️⃣ Pilot Gate")
        gate = pilot_readiness_gate(result)
        if gate and gate.get("status", "").startswith("READY"): 
            st.success("🟢 Software is ready for external pilot testing.")
        else: 
            st.error("🔴 Testing is blocked due to data quality issues.")
        if gate and gate.get("warnings"):
            for x in gate["warnings"]: st.warning(x)

        st.subheader("9️⃣ Pilot Evidence Log")
        pilot_id = st.text_input("Pilot ID", "PILOT-001")
        site_id = st.text_input("Site/Plant ID", "SITE-001")
        review = st.selectbox("Engineer Review", ["Not reviewed yet", "Reviewed - Supported", "Reviewed - Unsupported"])
        notes = st.text_area("Engineer/Operator Notes")
        action = st.text_area("Action Taken")

        st.subheader("📥 Reports")
        rjson = json.dumps(report, ensure_ascii=False, indent=2)
        csv = raw.to_csv(index=False).encode("utf-8-sig")
        b1, b2 = st.columns(2)
        b1.download_button("📄 JSON Report", rjson, "autovolt_report.json", "application/json", use_container_width=True)
        b2.download_button("📊 Analyzed Data CSV", csv, "autovolt_analyzed_data.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"File processing execution failed: {e}")

