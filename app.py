# =============================================================================
# AUTOVOLT AI — V52.0 PILOT DASHBOARD WITH EVIDENCE GATEWAY
# =============================================================================

import io
import json
import pandas as pd
import streamlit as st
from validation import VERSION, INDUSTRY_PROFILES, AutoVoltPipeline, PilotEvidenceLog

st.set_page_config(page_title="AutoVolt AI — Pilot Evidence Ready v52.0", page_icon="⚡", layout="wide")

st.markdown('<div style="font-size:2.4rem; font-weight:700; color:#1E3A8A;">⚡ لوحة تحكم ومستندات AutoVolt AI</div>', unsafe_allow_html=True)
st.caption(f"بوابة توثيق الأدلة الميدانية للمصانع والتمويل — الإصدار {VERSION}")

st.sidebar.header("⚙️ إعداد واستيراد البيانات")
industry = st.sidebar.selectbox("نوع النشاط الصناعي", list(INDUSTRY_PROFILES.keys()))

st.markdown("### 📊 خطوة 1: استيراد ملف البيانات التشغيلية")
uploaded_file = st.file_uploader("ارفع ملف القراءات للمصنع (CSV / Excel / TXT)", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            raw_df = pd.read_excel(uploaded_file)
        else:
            raw_df = pd.read_csv(uploaded_file)
            
        st.success("✅ تم استلام وقراءة بنية ملف البيانات بنجاح.")
        st.dataframe(raw_df.head(5))
        
        st.markdown("---")
        st.markdown("### 📝 خطوة 2: سجل توثيق الـ Pilot (دليل الشريك الصناعي للتمويل)")
        st.info("قم بتعبئة هذا السجل بالتعاون مع مهندس المصنع لإنشاء تقرير حالة (Case Study) قابل للاستدعاء الفوري أمام الممولين.")
        
        col1, col2 = st.columns(2)
        with col1:
            exp_id = st.text_input("رقم / معرّف التجربة التجريبية", value="PILOT-001")
            factory_id = st.text_input("اسم / معرّف المصنع أو الورشة", placeholder="مثال: ورشة الحديد والصلب المركزية")
        with col2:
            engineer_review = st.selectbox("نتيجة مراجعة المهندس الميداني للتنبؤات", ["مطابق ومكتشف بدقة لحالة شاذة", "بحاجة إلى مراجعة وتعديل معايير", "قراءة طبيعية متوافقة مع الواقع"])
            action_taken = st.text_input("الإجراء الذي اتخذه المصنع بناءً على الفحص", placeholder="مثال: إيقاف المكبس وجدول صيانة فورية للمحمل")
            
        engineer_notes = st.text_area("ملاحظات المهندس الفنية التفصيلية وتوصياته الميدانية")
        
        if st.button("🚀 تشغيل محرك AutoVolt وإنشاء مستند الأدلة الرسمي", type="primary"):
            log_entry = PilotEvidenceLog(
                experiment_id=exp_id,
                factory_id=factory_id,
                engineer_review=engineer_review,
                engineer_notes=engineer_notes,
                action_taken=action_taken
            )
            
            pipeline = AutoVoltPipeline(industry)
            final_report = pipeline.run(raw_df, evidence_log=log_entry)
            
            st.success("🟢 اكتملت معالجة البيانات وبناء ملف الأدلة (Pilot Evidence File) بنجاح!")
            
            st.json(final_report)
            
            # تصدير التقرير كملف قابل للتنزيل فوراً
            report_json = json.dumps(final_report, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 تحميل ملف الأدلة الرسمي (Pilot Evidence JSON)",
                data=report_json,
                file_name=f"AutoVolt_Evidence_{factory_id}_{exp_id}.json",
                mime="application/json"
            )
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف الهيكلي: {str(e)}")
