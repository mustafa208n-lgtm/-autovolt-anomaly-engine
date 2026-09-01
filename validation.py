from __future__ import annotations
import hashlib, json, math, re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

VERSION = "V53.0-PILOT-CONSOLIDATED"

INDUSTRY_PROFILES = {
 "General Manufacturing": {"aliases": {
  "timestamp":["timestamp","time","datetime","date","zeit"],
  "temperature":["temperature","temperature_c","temp","temp_c","temperature_celsius","machine_temperature"],
  "vibration":["vibration","vibration_mm_s","vibration_mms","vib","vib_mm_s","machine_vibration","motor_vibration"],
  "power":["power","power_kw","power_w","energy_power","active_power","electrical_power"],
  "load":["load","load_percent","load_pct","machine_load"],
  "operating_hours":["operating_hours","hours","runtime","runtime_hours"]},
  "limits":{"temperature":(-50,300),"vibration":(0,50),"power":(0,None),"load":(0,100),"operating_hours":(0,None)}},
 "Automotive / Vehicles": {"aliases": {
  "timestamp":["timestamp","time","datetime","date"],"temperature":["temperature","coolant_temperature","coolant_temp","engine_temperature","engine_temp"],
  "vibration":["vibration","engine_vibration","vibration_mm_s"],"power":["power","power_kw","engine_power"],"load":["load","engine_load","engine_load_percent"],
  "operating_hours":["operating_hours","engine_hours","runtime_hours"],"rpm":["rpm","engine_rpm","engine_speed"],"battery_voltage":["battery_voltage","battery_voltage_v","voltage","voltage_v"]},
  "limits":{"temperature":(-50,180),"vibration":(0,50),"power":(0,None),"load":(0,100),"operating_hours":(0,None),"rpm":(0,30000),"battery_voltage":(0,100)}},
 "Batteries": {"aliases": {
  "timestamp":["timestamp","time","datetime","date"],"temperature":["temperature","temperature_c","cell_temperature","cell_temp","pack_temperature","battery_temp"],
  "voltage":["voltage","voltage_v","pack_voltage","cell_voltage"],"current":["current","current_a","pack_current"],"power":["power","power_kw","power_w","charge_power","discharge_power"],
  "soc":["soc","state_of_charge","state_of_charge_percent"],"soh":["soh","state_of_health","state_of_health_percent"]},
  "limits":{"temperature":(-50,150),"voltage":(0,2000),"current":(-5000,5000),"power":(0,None),"soc":(0,100),"soh":(0,100)}},
 "Iron / Aluminum / Metals": {"aliases": {
  "timestamp":["timestamp","time","datetime","date"],"temperature":["temperature","temperature_c","furnace_temperature","furnace_temp","molten_temperature","melt_temp"],
  "vibration":["vibration","vibration_mm_s","motor_vibration","mill_vibration","press_vibration"],"power":["power","power_kw","electrical_power","mill_power","motor_power"],
  "load":["load","load_percent","machine_load","hydraulic_pressure","force_kn"],"pressure":["pressure","pressure_bar","pressure_kpa"],"flow":["flow","flow_rate","flow_rate_l_min"]},
  "limits":{"temperature":(-50,2000),"vibration":(0,150),"power":(0,None),"load":(0,5000),"pressure":(0,10000),"flow":(0,None)}},
 "Textiles": {"aliases": {
  "timestamp":["timestamp","time","datetime","date"],"temperature":["temperature","temperature_c","machine_temperature"],"vibration":["vibration","vibration_mm_s","machine_vibration"],
  "power":["power","power_kw","energy_power"],"load":["load","load_percent","machine_load"],"speed":["speed","rpm","machine_speed","spindle_speed"],"humidity":["humidity","humidity_percent","relative_humidity"]},
  "limits":{"temperature":(-50,150),"vibration":(0,50),"power":(0,None),"load":(0,100),"speed":(0,100000),"humidity":(0,100)}}
}


def normalize_name(x:str)->str:
    s=str(x).strip().lower()
    s=re.sub(r"[%]","percent",s); s=re.sub(r"[^a-z0-9_]+","_",s)
    return re.sub(r"_+","_",s).strip("_")

def finite_float(x)->Optional[float]:
    try:
        y=float(x); return y if math.isfinite(y) else None
    except Exception: return None

def sha256_dataframe(df:pd.DataFrame)->str:
    return hashlib.sha256(df.to_csv(index=False).encode("utf-8",errors="replace")).hexdigest()

def infer_kind(df:pd.DataFrame)->str:
    cols=[normalize_name(c) for c in df.columns]
    if len(cols)>=500: return "HIGH_DIMENSIONAL_MANUFACTURING"
    if any("bearing" in c or "vibration" in c for c in cols): return "CONDITION_MONITORING"
    return "GENERIC_INDUSTRIAL"

@dataclass
class AdapterResult:
    dataframe:pd.DataFrame; mapping:Dict[str,str]; unmapped_columns:List[str]; missing_recommended_signals:List[str]; warnings:List[str]; dataset_kind:str

class IndustrialAdapter:
    def __init__(self,industry:str):
        if industry not in INDUSTRY_PROFILES: raise ValueError("Unknown industry profile")
        self.industry=industry; self.profile=INDUSTRY_PROFILES[industry]
    def adapt(self,df:pd.DataFrame)->AdapterResult:
        if df is None or df.empty: raise ValueError("Data is empty.")
        original=list(df.columns); norm={c:normalize_name(c) for c in original}; mapping={}; used=set()
        for canonical,candidates in self.profile["aliases"].items():
            aliases={normalize_name(x) for x in candidates}
            for c,n in norm.items():
                if c not in used and n in aliases:
                    mapping[c]=canonical; used.add(c); break
        out=df.rename(columns=mapping).copy(); warnings=[]
        for c in out.columns:
            if c!="timestamp" and (c in mapping.values() or pd.api.types.is_numeric_dtype(out[c])):
                out[c]=pd.to_numeric(out[c],errors="coerce")
        if "timestamp" in out.columns: out["timestamp"]=pd.to_datetime(out["timestamp"],errors="coerce")
        kind="PROFILED" if any(c in out.columns for c in ("temperature","vibration","voltage","current")) else infer_kind(out)
        if kind!="PROFILED": warnings.append("Standard signals were not recognized; numerical columns were kept for high-dimensional general analysis.")
        unmapped=[c for c in original if c not in mapping]
        if unmapped: warnings.append(f"Retained {len(unmapped)} unknown columns without assuming meaning.")
        if "timestamp" not in out: warnings.append("No known timestamp; temporal analysis is limited.")
        rec=self.recommended_signals(); missing=[x for x in rec if x not in out.columns]
        return AdapterResult(out,mapping,unmapped,missing,warnings,kind)
    def recommended_signals(self)->List[str]:
        if self.industry=="Batteries": return ["temperature","voltage","current","soc","soh"]
        if self.industry=="Automotive / Vehicles": return ["temperature","vibration","rpm","battery_voltage"]
        if self.industry=="Iron / Aluminum / Metals": return ["temperature","vibration","power"]
        return ["temperature","vibration","load"]

@dataclass
class QualityReport:
    status:str; rows:int; columns:int; missing_values:int; duplicate_rows:int; duplicate_timestamps:int; invalid_timestamps:int; invalid_numeric_cells:int; out_of_range_values:int; issues:List[str]; warnings:List[str]

class DataQualityEngine:
    def evaluate(self,df:pd.DataFrame,industry:str)->QualityReport:
        if df is None or df.empty: return QualityReport("REJECT",0,0,0,0,0,0,0,0,["Dataset is empty."],[])
        p=INDUSTRY_PROFILES[industry]; issues=[]; warnings=[]; missing=int(df.isna().sum().sum()); dup=int(df.duplicated().sum())
        invalid_ts=dup_ts=0
        if "timestamp" in df:
            invalid_ts=int(df["timestamp"].isna().sum()); dup_ts=int(df["timestamp"].duplicated().sum())
            if invalid_ts: issues.append(f"There are {invalid_ts} invalid timestamps.")
            if dup_ts: warnings.append(f"There are {dup_ts} duplicate timestamps.")
        else: warnings.append("No timestamp.")
        invalid=oor=0
        for c,(lo,hi) in p["limits"].items():
            if c not in df: continue
            raw=df[c]; s=pd.to_numeric(raw,errors="coerce"); invalid += int((s.isna() & raw.notna()).sum())
            if lo is not None: oor += int((s<lo).sum())
            if hi is not None: oor += int((s>hi).sum())
        if missing: warnings.append(f"There are {missing} missing values; not considered a valid measurement.")
        if dup: warnings.append(f"There are {dup} duplicate rows.")
        if invalid: issues.append(f"There are {invalid} non-numeric values in known signals.")
        if oor: issues.append(f"There are {oor} values outside the specified physical range.")
        status="REJECT" if issues else ("WARNING" if warnings else "ACCEPT")
        return QualityReport(status,len(df),len(df.columns),missing,dup,dup_ts,invalid_ts,invalid,oor,issues,warnings)

class TemporalAnalysisEngine:
    def analyze(self,df:pd.DataFrame)->Dict:
        if "timestamp" not in df: return {"status":"BLOCKED","reason":"No valid timestamp."}
        w=df.dropna(subset=["timestamp"]).sort_values("timestamp"); sig={}
        nums=[c for c in w.columns if c!="timestamp" and pd.api.types.is_numeric_dtype(w[c])]
        for c in nums:
            s=pd.to_numeric(w[c],errors="coerce").dropna()
            if len(s)<3: continue
            base=float(s.iloc[:min(10,len(s))].mean()); x=np.arange(len(s),dtype=float)
            try: slope=float(np.polyfit(x,s.to_numpy(float),1)[0])
            except Exception: slope=0.0
            sig[c]={"first":float(s.iloc[0]),"last":float(s.iloc[-1]),"baseline":base,"drift":float(s.iloc[-1]-base),"trend_slope":slope,"rolling_mean_last":float(s.rolling(min(10,len(s)),min_periods=1).mean().iloc[-1])}
        return {"status":"AVAILABLE","signals":sig,"rows_used":len(w)} if sig else {"status":"BLOCKED","reason":"Not enough numerical signals."}

class EvidenceEngine:
    def analyze(self,df:pd.DataFrame)->Dict:
        ignored={"timestamp","label","labels","target","class","failure","fault"}; rows=[]; stats={}
        for c in [x for x in df.columns if x not in ignored and pd.api.types.is_numeric_dtype(df[x])]:
            s=pd.to_numeric(df[c],errors="coerce"); v=s.dropna()
            if len(v)<5: continue
            med=float(v.median()); mad=float(np.median(np.abs(v-med)))
            if mad>0: score=(0.6745*(s-med)/mad).abs()
            else:
                tol=max(1e-9,abs(med)*0.20,10.0); score=(s-med).abs()/tol
            stats[c]={"median":med,"mad":mad,"max_robust_score":float(score.max())}
            for idx in s.index[score.fillna(0)>3.5]:
                val=finite_float(s.loc[idx]);
                if val is not None: rows.append({"row_index":int(idx) if isinstance(idx,(int,np.integer)) else str(idx),"signal":c,"value":val,"baseline":med,"deviation":val-med,"robust_score":float(score.loc[idx])})
        return {"status":"AVAILABLE","anomaly_count":len(rows),"anomalies":rows,"signal_statistics":stats}

class OperationalClassifier:
    def __init__(self,industry:str): self.industry=industry
    def classify(self,df:pd.DataFrame)->pd.DataFrame:
        out=df.copy(); statuses=[]; reasons=[]
        for _,r in out.iterrows():
            st="Normal"; rs=[]; t=finite_float(r.get("temperature")); v=finite_float(r.get("vibration")); load=finite_float(r.get("load"))
            if self.industry=="Batteries":
                if t is not None: st="Abnormal" if t>60 else ("Needs Review" if t>45 else st); rs += ["Battery temperature is high." if t>60 else "Battery temperature is higher than reference."] if t>45 else []
                soc=finite_float(r.get("soc")); soh=finite_float(r.get("soh"));
                if soc is not None and not 0<=soc<=100: st="Invalid"; rs.append("SOC outside 0–100%.")
                if soh is not None and not 0<=soh<=100: st="Invalid"; rs.append("SOH outside 0–100%.")
            elif self.industry=="Automotive / Vehicles":
                if t is not None: st="Abnormal" if t>115 else ("Needs Review" if t>100 else st); rs += ["Engine temperature is very high." if t>115 else "Engine temperature is high."] if t>100 else []
                rpm=finite_float(r.get("rpm")); bv=finite_float(r.get("battery_voltage"))
                if rpm is not None and rpm>9000: st="Abnormal" if rpm>12000 else "Needs Review"; rs.append("High RPM.")
                if bv is not None and (bv<10 or bv>16): st="Needs Review" if st=="Normal" else st; rs.append("Vehicle battery voltage is outside the normal range.")
                if v is not None and v>7: st="Abnormal"; rs.append("High vibration.")
            elif self.industry=="Iron / Aluminum / Metals":
                if t is not None: st="Abnormal" if t>1800 else ("Needs Review" if t>1500 else st); rs += ["Metal process temperature is very high." if t>1800 else "Metal process temperature is high."] if t>1500 else []
                if v is not None: st="Abnormal" if v>7 else ("Needs Review" if v>4.5 and st=="Normal" else st); rs.append("High vibration.") if v>4.5 else None
            else:
                if t is not None: st="Abnormal" if t>105 else ("Needs Review" if t>90 else st); rs += ["Temperature is very high." if t>105 else "Temperature is higher than reference."] if t>90 else []
                if v is not None: st="Abnormal" if v>7 else ("Needs Review" if v>4.5 and st=="Normal" else st); rs.append("High vibration.") if v>4.5 else None
                if load is not None and not 0<=load<=100: st="Invalid"; rs.append("Load outside 0–100%.")
            statuses.append(st); reasons.append(" ".join(rs) if rs else "No clear operational deviation appeared under current rules.")
        out["autovolt_status"]=statuses; out["autovolt_reason"]=reasons; return out

class ReportEngine:
    def build(self,raw,adapted,industry,quality,adapter,temporal,evidence)->Dict:
        overall="BLOCKED" if quality.status=="REJECT" else ("REVIEW_REQUIRED" if evidence.get("anomaly_count",0)>0 else "NO_CLEAR_ANOMALY_DETECTED")
        rec=[]
        if quality.status=="REJECT": rec.append("Fix data quality issues before relying on results.")
        if quality.missing_values: rec.append("Review missing values and do not consider them real measurements.")
        if evidence.get("anomaly_count",0): rec.append("Field-review anomalies by an engineer/maintenance officer.")
        if temporal.get("status")=="BLOCKED": rec.append("Add a valid timestamp for better temporal analysis.")
        if not rec: rec.append("The result can be used as a preliminary check, with continued field verification.")
        return {"application":"AutoVolt AI","version":VERSION,"generated_at":datetime.now(timezone.utc).isoformat(),"industry":industry,"overall_status":overall,
         "data":{"rows":len(raw),"columns":len(raw.columns),"sha256":sha256_dataframe(raw)},"quality":asdict(quality),"adapter":{"mapping":adapter.mapping,"unmapped_columns":adapter.unmapped_columns,"missing_recommended_signals":adapter.missing_recommended_signals,"warnings":adapter.warnings,"dataset_kind":adapter.dataset_kind},"temporal_analysis":temporal,"evidence":evidence,"recommendations":rec,
         "economic_claims":{"measured_savings_eur":None,"potential_savings_eur":None,"energy_savings_kwh":None,"co2_reduction_kg":None,"statement":"No financial, energy, or CO2 savings are claimed without documented before/after measurements from a real pilot."},
         "limitations":["Result is not a final engineering diagnosis.","Anomaly does not necessarily mean a failure.","Academic research data does not prove commercial success.","Commercial adoption requires a pilot with real customer data."]}

class AutoVoltPipeline:
    def __init__(self,industry:str): self.industry=industry; self.adapter=IndustrialAdapter(industry); self.quality=DataQualityEngine(); self.temporal=TemporalAnalysisEngine(); self.evidence=EvidenceEngine(); self.classifier=OperationalClassifier(industry); self.reporter=ReportEngine()
    def run(self,df:pd.DataFrame)->Dict:
        ar=self.adapter.adapt(df); q=self.quality.evaluate(ar.dataframe,self.industry)
        if q.status=="REJECT":
            t={"status":"BLOCKED","reason":"Analysis stopped due to data quality."}; e={"status":"BLOCKED","reason":"Analysis stopped due to data quality."}; data=ar.dataframe
        else:
            data=self.classifier.classify(ar.dataframe); t=self.temporal.analyze(data); e=self.evidence.analyze(data)
        report=self.reporter.build(df,data,self.industry,q,ar,t,e)
        return {"report":report,"data":data,"quality":q,"adapter":ar,"temporal":t,"evidence":e}

def pilot_readiness_gate(result:Dict)->Dict:
    q=result["quality"]; a=result["adapter"]; blockers=[]; warnings=[]
    if q.status=="REJECT": blockers.append("Data quality is rejected.")
    if a.missing_recommended_signals: warnings.append("Recommended signals are missing: "+", ".join(a.missing_recommended_signals))
    if result["evidence"].get("status")=="BLOCKED" and q.status!="REJECT": warnings.append("Evidence analysis unavailable for current dataset.")
    return {"status":"BLOCKED" if blockers else "READY_FOR_EXTERNAL_PILOT","blockers":blockers,"warnings":warnings,"note":"This means the software is ready for external testing, not proof of commercial or engineering success."}

def run_internal_tests()->Dict:
    tests=[]; p=AutoVoltPipeline("General Manufacturing")
    base=pd.DataFrame({"timestamp":pd.date_range("2026-01-01",periods=20,freq="h"),"temperature":70.0,"vibration":2.0,"load":70.0})
    r=p.run(base); tests.append(("normal_accept",r["quality"].status=="ACCEPT"))
    m=base.copy(); m.loc[5,"temperature"]=np.nan; tests.append(("missing_warning",p.run(m)["quality"].status=="WARNING"))
    bad=base.copy(); bad.loc[5,"vibration"]=999; tests.append(("range_reject",p.run(bad)["quality"].status=="REJECT"))
    an=base.copy(); an.loc[10,"temperature"]=180; tests.append(("anomaly_detected",p.run(an)["evidence"].get("anomaly_count",0)>0))
    car=pd.DataFrame({"datetime":pd.date_range("2026-01-01",periods=10,freq="h"),"coolant_temp":85.0,"engine_vibration":2.0,"engine_load":60.0}); tests.append(("car_adapter", "temperature" in AutoVoltPipeline("Automotive / Vehicles").run(car)["data"].columns))
    hi=pd.DataFrame(np.random.default_rng(42).normal(size=(30,591)),columns=[f"sensor_{i}" for i in range(591)]); hr=AutoVoltPipeline("General Manufacturing").run(hi); tests.append(("591_columns_no_crash",hr["adapter"].dataset_kind=="HIGH_DIMENSIONAL_MANUFACTURING"))
    passed=sum(x[1] for x in tests); return {"version":VERSION,"overall":"PASS" if passed==len(tests) else "FAIL","passed":passed,"total":len(tests),"tests":[{"name":n,"passed":ok} for n,ok in tests]}
