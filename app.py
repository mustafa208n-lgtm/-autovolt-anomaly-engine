# =============================================================================
# AUTOVOLT AI — V51.1 PILOT APPLICATION (STREAMLIT DASHBOARD)
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, run_internal_tests
from external_validation import ExternalValidationModule

st.set_page_config(page_title="AutoVolt AI — Industrial Pilot V51.1", page_icon="⚡", layout="wide")

st.markdown('<div style="font-size:2.4rem; font-weight:700;">⚡ AutoVolt AI Dashboard</div>', unsafe_allow_html=True)
st.caption(f"Production Pilot Ingestion Layer — {VERSION}")

st.sidebar.header("⚙️ إعداد واستيراد البيانات")
analysis_mode = st.sidebar.radio("نوع الفحص المخبري", ["بيانات المصنع الميدانية", "بيانات البحوث العالمية (Module 6)"])

if analysis_mode == "بيانات المصنع الميدانية":
    industry = st.sidebar.selectbox("نوع النشاط الصناعي", list(INDUSTRY_PROFILES.keys()))
    uploaded_file = st.file_uploader("📂 ارفع ملف القراءات (CSV / TXT)", type=["csv", "txt"])
    
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        st.subheader("📄 معاينة جودة وهيكل البيانات المرفوعة")
        st.dataframe(raw_df.head(5))
        
        if st.button("🚀 ابدأ تحليل محرك AutoVolt", type="primary"):
            pipeline = AutoVoltPipeline(industry)
            result = pipeline.run(raw_df)
            st.success("🟢 اكتمل الفحص الأولي للجودة بصمة الملف المشفرة.")
            st.json(result["report"])

else:
    st.subheader("🔬 موديول 6: فحص الهياكل غير النمطية المعقدة (NASA / SECOM)")
    st.info("هذا الموديل مخصص لاختبار مرونة النظام برمجياً على تحمل البيانات الضخمة وفك الـ ZIP تلقائياً دون تلاعب بالقيم.")
    
    research_type = st.selectbox("اختر نوع الصيغة البحثية المستهدفة", ["SECOM (أشباه الموصلات - 591 متغير)", "NASA IMS (صيغة ملفات الفضاء المضغوطة ZIP)"])
    uploaded_research = st.file_uploader("📂 ارفع الملف الخام للاختبار الهيكلي", type=["data", "zip", "txt", "csv"])
    
    if uploaded_research is not None:
        ext_module = ExternalValidationModule()
        file_bytes = io.BytesIO(uploaded_research.read())
        
        if st.button("🔍 تشغيل الفحص الهيكلي الآمن", type="primary"):
            with st.spinner("جاري تحليل الروابط والـ Features..."):
                if research_type == "SECOM (أشباه الموصلات - 591 متغير)":
                    res = ext_module.validate_secom(file_bytes)
                else:
                    res = ext_module.validate_nasa_ims(file_bytes)
                
                if res["status"] == "PASS":
                    st.success("✅ PASS: بنية البيانات متوافقة مع الكود البرمجي وجاهزة للاستيعاب الفعلي.")
                else:
                    st.error("❌ تعذر التحقق الهيكلي من الملف.")
                st.write(res)

