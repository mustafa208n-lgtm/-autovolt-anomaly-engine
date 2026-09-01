from __future__ import annotations
import io, json
import pandas as pd
import streamlit as st
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, pilot_readiness_gate, run_internal_tests

st.set_page_config(page_title=f"AutoVolt AI {VERSION}",page_icon="⚡",layout="wide")
st.title("⚡ AutoVolt AI")
st.caption(f"Evidence-driven industrial analysis • {VERSION}")

with st.sidebar:
    st.header("⚙️ Analysis Settings")
    industry=st.selectbox("Select data industry",list(INDUSTRY_PROFILES.keys()))
    st.caption("The four core industries: General Manufacturing, Automotive/Vehicles, Batteries, Metals.")

st.subheader("1️⃣ Upload Your Data")
f=st.file_uploader("CSV / Excel / TXT",type=["csv","xlsx","txt"])

def load_file(upload):
    name=upload.name.lower()
    raw=upload.getvalue()
    if name.endswith(".xlsx"): return pd.read_excel(io.BytesIO(raw))
    if name.endswith(".txt"):
        for sep in [None,"\t",",",";"]:
            try: return pd.read_csv(io.BytesIO(raw),sep=sep,engine="python")
            except Exception: pass
        raise ValueError("Could not read TXT. Check the column separator.")
    for enc in ["utf-8","utf-8-sig","cp1252","latin1"]:
        try: return pd.read_csv(io.BytesIO(raw),encoding=enc)
        except Exception: pass
    raise ValueError("Could not read CSV.")

if f:
    try:
        raw=load_file(f)
        st.success(f"File read successfully: {len(raw):,} rows × {len(raw.columns):,} columns")
        st.markdown("**First 5 rows of raw data**")
        st.dataframe(raw.head(),use_container_width=True,hide_index=True)
        result=AutoVoltPipeline(industry).run(raw)
        q=result["quality"]; a=result["adapter"]; report=result["report"]; evidence=result["evidence"]; temporal=result["temporal"]

        st.subheader("2️⃣ Data Quality")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Status",q.status); c2.metric("Missing Values",q.missing_values); c3.metric("Out of Range",q.out_of_range_values); c4.metric("Unknown Columns",len(a.unmapped_columns))
        if q.issues:
            st.error("\n".join("• "+x for x in q.issues))
        if q.warnings:
            st.warning("\n".join("• "+x for x in q.warnings[:20]))

        st.subheader("3️⃣ Adapter")
        st.write(f"Detected dataset kind: **{a.dataset_kind}**")
        if a.mapping: st.json(a.mapping)
        if a.missing_recommended_signals: st.info("Missing recommended signals: "+", ".join(a.missing_recommended_signals))
        if len(raw.columns)>=500: st.info("Handled high-dimensional file; unknown columns are not given invented names or meanings.")

        st.subheader("4️⃣ Detected States")
        if "autovolt_status" in result["data"]:
            counts=result["data"]["autovolt_status"].value_counts(); x1,x2,x3=st.columns(3)
            x1.metric("Normal",int(counts.get("Normal",0))); x2.metric("Needs Review",int(counts.get("Needs Review",0))); x3.metric("Abnormal",int(counts.get("Abnormal",0)))
            cols=[c for c in ["timestamp","temperature","vibration","load","voltage","current","power","autovolt_status","autovolt_reason"] if c in result["data"].columns]
            st.dataframe(result["data"][cols].tail(300),use_container_width=True,hide_index=True)

        st.subheader("5️⃣ Evidence & Anomalies")
        n=int(evidence.get("anomaly_count",0))
        st.metric("Statistical Anomaly Count",n)
        if n: st.dataframe(pd.DataFrame(evidence["anomalies"]),use_container_width=True,hide_index=True)
        else: st.success("No clear statistical anomaly under the current method.")
        st.caption("The anomaly is a statistical indicator, not a failure probability or final diagnosis.")

        st.subheader("6️⃣ Temporal Change")
        if temporal.get("status")=="AVAILABLE":
            rows=[{"Signal":k,**v} for k,v in temporal["signals"].items()]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            if "timestamp" in result["data"]:
                for col in [c for c in ["temperature","vibration","load","voltage","current","power"] if c in result["data"]][:4]:
                    d=result["data"][["timestamp",col]].dropna().set_index("timestamp")
                    if not d.empty: st.line_chart(d)
        else: st.warning(temporal.get("reason","Temporal analysis not available."))

        st.subheader("7️⃣ What is Required?")
        for r in report["recommendations"]: st.write("🔧 "+r)
        gate=pilot_readiness_gate(result)
        st.subheader("8️⃣ Pilot Gate")
        if gate["status"].startswith("READY"): st.success("🟢 Software is ready for external pilot testing.")
        else: st.error("🔴 Testing is blocked due to data quality issues.")
        for x in gate["warnings"]: st.warning(x)
        st.caption(gate["note"])

        st.subheader("9️⃣ Pilot Evidence Log")
        pilot_id=st.text_input("Pilot ID","PILOT-001"); site_id=st.text_input("Site/Plant ID","SITE-001")
        review=st.selectbox("Engineer Review",["Not reviewed yet","Reviewed - Supported","Reviewed - Unsupported","Inconclusive"])
        notes=st.text_area("Engineer/Operator Notes"); action=st.text_area("Action Taken")
        evidence_manifest={"pilot_id":pilot_id,"site_id":site_id,"industry":industry,"application_version":VERSION,"analysis_status":report["overall_status"],"quality_status":q.status,"anomaly_count":n,"engineer_review":review,"notes":notes,"action_taken":action,"data":report["data"]}

        st.subheader("📥 Reports")
        rjson=json.dumps(report,ensure_ascii=False,indent=2); manifest=json.dumps(evidence_manifest,ensure_ascii=False,indent=2); csv=result["data"].to_csv(index=False).encode("utf-8-sig")
        b1,b2,b3=st.columns(3)
        b1.download_button("📄 JSON Report",rjson,"autovolt_report.json","application/json",use_container_width=True)
        b2.download_button("📦 Pilot Evidence",manifest,f"{pilot_id}_evidence.json","application/json",use_container_width=True)
        b3.download_button("📊 Analyzed Data CSV",csv,"autovolt_analyzed_data.csv","text/csv",use_container_width=True)

        st.markdown("---")
        st.warning("This software assists in data screening and anomaly detection. It is not a substitute for an engineer or a machine stop/repair decision.")
    except Exception as e:
        st.error(f"File input failed: {e}")

with st.expander("Internal Software Test"):
    if st.button("Run Internal Tests"):
        st.json(run_internal_tests())
