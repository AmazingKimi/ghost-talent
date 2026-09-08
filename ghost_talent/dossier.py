from __future__ import annotations
from typing import Any

TECH_TERMS=("cuda","triton","kernel","inference","attention","gemm","moe","quantization","gpu","compiler","benchmark","distributed","pytorch","runtime","vllm","sglang","llama.cpp")

def _technical_profile(candidate:dict[str,Any])->list[dict[str,Any]]:
    hits={}
    for evidence in candidate.get("evidence",[]):
        value=evidence.get("value") or {}; text=" ".join(str(value.get(k,"")) for k in ("title","repository","description","path")).lower(); external=evidence.get("type")=="external_merged_pull_request"
        for term in TECH_TERMS:
            if term in text:
                row=hits.setdefault(term,{"term":term,"support":0,"external_support":0});row["support"]+=1;row["external_support"]+=int(external)
    return sorted(hits.values(),key=lambda x:(x["external_support"],x["support"]),reverse=True)[:6]

def _important_contributions(candidate:dict[str,Any])->list[dict[str,Any]]:
    rows=[]
    for evidence in candidate.get("evidence",[]):
        if evidence.get("type") not in {"merged_pull_request","external_merged_pull_request"}:continue
        value=evidence.get("value") or {};external=evidence.get("type")=="external_merged_pull_request";facts=[]
        if external:facts.append("external merged PR")
        if value.get("recognized_upstream"):facts.append("recognized upstream")
        if value.get("core_path_signal") and value.get("core_path_evidence")=="changed_files":facts.append("core path verified from changed files")
        if value.get("maintainer_accepted") and value.get("maintainer_acceptance_evidence")=="approved_review":facts.append("maintainer-approved review")
        if value.get("recent_180d"):facts.append("recent (180d)")
        core=value.get("core_files") or []
        if core:facts.append(f"{len(core)} sampled core file(s)")
        strength="strong" if external and value.get("recognized_upstream") and value.get("maintainer_accepted") and value.get("core_path_signal") else "moderate" if external and (value.get("recognized_upstream") or value.get("core_path_signal")) else "limited"
        interpretation="Verified external upstream contribution with same-PR core-path and maintainer-approval evidence." if strength=="strong" else "External contribution is verified, but collected evidence is not sufficient for a strong technical endorsement." if external else "Internal/discovery-repository contribution; useful for execution evidence, not external validation."
        rows.append({"title":value.get("title") or f"Merged PR #{value.get('number','?')}","repository":value.get("repository"),"number":value.get("number"),"url":evidence.get("source_url"),"observed_at":evidence.get("observed_at") or value.get("merged_or_closed_at"),"external":external,"recognized_upstream":bool(value.get("recognized_upstream")),"maintainer_accepted":bool(value.get("maintainer_accepted")),"core_files":core,"evidence_strength":strength,"evidence_facts":facts,"interpretation":interpretation})
    order={"strong":2,"moderate":1,"limited":0};rows.sort(key=lambda x:(order[x["evidence_strength"]],x["external"],x["recognized_upstream"]),reverse=True);return rows[:5]

def _recommendation(status:str,external:dict[str,Any],mix:dict[str,Any],confidence:float)->dict[str,str]:
    actions={"STRONG SIGNAL":"Priority technical review","EARLY SIGNAL":"Worth technical review now","WATCH":"Monitor and collect more external evidence","PROVEN / ALREADY VISIBLE":"Strong profile, but outside emerging-talent target","DISCOVERED":"Insufficient evidence for recommendation","LOW CONFIDENCE":"Do not recommend until evidence quality improves"}
    risks=[]
    if not external.get("available"):risks.append("external validation not fully inspected")
    if not int(external.get("external_merged_prs") or 0):risks.append("no verified external merged PR in current collection")
    if float(mix.get("self_owned_repo_pct") or mix.get("self_owned_or_discovery_repo_pct") or 0)>80:risks.append("evidence concentrated in self-owned/discovery repositories")
    if confidence<55:risks.append("evidence confidence is still limited")
    if status=="PROVEN / ALREADY VISIBLE":risks.append("already visible to the market")
    return {"status":status,"action":actions.get(status,"Further review required"),"main_risk":"; ".join(risks[:2]) if risks else "No major evidence-boundary risk detected in the current collection."}

def build_dossier(row:dict[str,Any])->dict[str,Any]:
    candidate=row.get("candidate") or {};drivers=row.get("drivers") or {};external=drivers.get("external_validation") or {};momentum=drivers.get("momentum") or {};identity=candidate.get("identity") or {};status=row.get("recommendation_status") or "DISCOVERED";mix=row.get("evidence_mix") or {};profile=_technical_profile(candidate);contributions=_important_contributions(candidate);why=[]
    for reason in external.get("reasons") or []:why.append(reason)
    if float(row.get("momentum") or 0)>=60:why.append(f"Momentum is elevated at {row.get('momentum')}")
    if status=="WATCH" and not int(external.get("external_merged_prs") or 0):why.append("Internal execution may be strong, but verified external validation is still limited.")
    if status=="PROVEN / ALREADY VISIBLE":why.append("Strong evidence exists, but market visibility is already too high for an emerging-talent signal.")
    if not why:why.append("Current evidence does not justify a stronger recommendation.")
    return {"schema_version":"0.5","identity":{"login":candidate.get("login"),"name":candidate.get("name"),"profile_url":candidate.get("profile_url"),"subject_id":identity.get("subject_id") or f"github:{str(candidate.get('login') or '').lower()}","github_user_id":identity.get("github_user_id"),"cross_source_status":identity.get("cross_source_status"),"confidence":row.get("evidence_confidence")},"recommendation":_recommendation(status,external,mix,float(row.get("evidence_confidence") or 0)),"signal":{"ghost_score":row.get("ghost_score"),"radar_score":row.get("radar_score"),"recommendation_status":status,"trend":row.get("trend"),"score_version":row.get("score_version"),"internal_capability":row.get("internal_capability"),"external_validation":row.get("external_validation"),"visibility_gap":row.get("visibility_gap")},"technical_profile":profile,"technical_focus":[x["term"] for x in profile],"evidence_mix":mix,"external_validation":external,"why_now":why,"trajectory":row.get("trajectory") or {},"activity":{"events_7d":momentum.get("events_7d"),"events_30d":momentum.get("events_30d"),"events_90d":momentum.get("events_90d"),"active_days_30d":momentum.get("active_days_30d"),"acceleration_ratio":momentum.get("acceleration_ratio")},"best_evidence":contributions[:3],"important_contributions":contributions,"evidence":candidate.get("evidence") or [],"limitations":["Discovery is not a recommendation; STRONG/EARLY require verified external evidence gates.","External PR inspection is bounded and does not constitute a full independent code review.","A merged or maintainer-approved PR does not by itself prove originality, authorship quality, or employment suitability.","Missing evidence is not inferred; uncertain cross-source identity matches are not treated as verified.","The dossier is research intelligence, not an employment decision."]}
