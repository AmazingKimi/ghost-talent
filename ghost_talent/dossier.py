from __future__ import annotations
from typing import Any

TECH_TERMS=("cuda","triton","kernel","inference","attention","gemm","moe","quantization","gpu","compiler","benchmark","distributed","pytorch")

def _technical_focus(candidate:dict[str,Any])->list[str]:
    hits={}
    for evidence in candidate.get("evidence",[]):
        value=evidence.get("value") or {};text=" ".join(str(value.get(k,"")) for k in ("title","repository","description","path")).lower()
        for term in TECH_TERMS:
            if term in text:hits[term]=hits.get(term,0)+1
    return [term for term,_ in sorted(hits.items(),key=lambda item:(-item[1],item[0]))[:6]]

def _contribution_assessment(value:dict[str,Any])->dict[str,Any]:
    core_files=value.get("core_files") or [];meta_keywords=value.get("keyword_hits") or [];patch_keywords=value.get("patch_keyword_hits") or [];additions=int(value.get("additions") or 0);deletions=int(value.get("deletions") or 0);changed=additions+deletions;patch_available=bool(value.get("patch_available"));code_lines=int(value.get("changed_code_lines_sampled") or 0)
    strength=0
    if core_files:strength+=2
    if meta_keywords:strength+=1
    if patch_keywords:strength+=2
    if patch_available and code_lines>=20:strength+=1
    if changed>=250:strength+=1
    level="strong" if strength>=5 else "moderate" if strength>=2 else "limited"
    facts=[]
    if core_files:facts.append(f"touches {len(core_files)} sampled core files")
    if patch_keywords:facts.append("patch signals: "+", ".join(patch_keywords[:6]))
    elif meta_keywords:facts.append("metadata signals: "+", ".join(meta_keywords[:6]))
    if patch_available:facts.append(f"{code_lines} changed code lines inspected from bounded patch sample")
    if changed:facts.append(f"sampled diff: +{additions} / -{deletions}")
    if patch_keywords and core_files:interpretation="Bounded patch evidence shows changes inside technically relevant code paths; this is a strong candidate for expert code review."
    elif core_files or patch_keywords:interpretation="Collected patch evidence indicates technical relevance, but does not by itself prove originality or engineering quality."
    else:interpretation="Collected evidence is insufficient to judge technical depth; inspect the source PR."
    return {"evidence_strength":level,"evidence_facts":facts,"patch_evidence":patch_available,"interpretation":interpretation}

def _important_contributions(candidate:dict[str,Any])->list[dict[str,Any]]:
    rows=[]
    for evidence in candidate.get("evidence",[]):
        if evidence.get("type")!="merged_pull_request":continue
        value=evidence.get("value") or {};assessment=_contribution_assessment(value)
        rows.append({"title":value.get("title") or f"Merged PR #{value.get('number','?')}","repository":value.get("repository"),"number":value.get("number"),"url":evidence.get("source_url"),"observed_at":evidence.get("observed_at"),"confidence":evidence.get("confidence"),"core_file_count":value.get("core_file_count"),"core_files":value.get("core_files") or [],"keyword_hits":value.get("keyword_hits") or [],"patch_keyword_hits":value.get("patch_keyword_hits") or [],"additions":value.get("additions",0),"deletions":value.get("deletions",0),**assessment})
    order={"strong":2,"moderate":1,"limited":0};rows.sort(key=lambda row:(order.get(row["evidence_strength"],0),int(row.get("core_file_count") or 0)),reverse=True);return rows[:5]

def build_dossier(row:dict[str,Any])->dict[str,Any]:
    candidate=row.get("candidate") or {};drivers=row.get("drivers") or {};quality=drivers.get("contribution_quality") or {};momentum=drivers.get("momentum") or {};confidence=drivers.get("confidence") or {};focus=_technical_focus(candidate);contributions=_important_contributions(candidate);why_now=[]
    if row.get("early_signal"):why_now.append(f"EARLY SIGNAL with Radar {row.get('radar_score')}")
    if float(row.get("momentum") or 0)>=60:why_now.append(f"Momentum is elevated at {row.get('momentum')}")
    if float(row.get("visibility_gap") or 0)>=45:why_now.append(f"Visibility gap remains high at {row.get('visibility_gap')}")
    if quality.get("available"):why_now.append(f"Contribution quality evidence is available ({quality.get('score',0)}/100)")
    if not why_now:why_now.append("Current evidence does not meet a strong early-attention threshold")
    return {"schema_version":"0.3","identity":{"login":candidate.get("login"),"name":candidate.get("name"),"profile_url":candidate.get("profile_url"),"subject_id":f"github:{str(candidate.get('login') or '').lower()}","confidence":row.get("evidence_confidence"),"confidence_reasons":confidence.get("reasons") or []},"signal":{"ghost_score":row.get("ghost_score"),"radar_score":row.get("radar_score"),"early_signal":bool(row.get("early_signal")),"trend":row.get("trend"),"score_version":row.get("score_version")},"technical_focus":focus,"why_now":why_now,"trajectory":row.get("trajectory") or {},"activity":{"events_7d":momentum.get("events_7d"),"events_30d":momentum.get("events_30d"),"events_90d":momentum.get("events_90d"),"active_days_30d":momentum.get("active_days_30d"),"acceleration_ratio":momentum.get("acceleration_ratio")},"important_contributions":contributions,"evidence":candidate.get("evidence") or [],"limitations":["PR technical analysis uses a bounded GitHub patch sample and deterministic evidence signals; it is not a full independent code review.","Patch evidence can support technical relevance but does not prove originality, authorship quality, or causal impact.","Missing evidence is not inferred.","Uncertain cross-source identity matches are not treated as verified.","The dossier is research intelligence, not an employment decision."]}
