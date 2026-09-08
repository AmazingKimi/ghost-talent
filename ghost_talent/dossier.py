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
        if strength=="strong":interpretation="Verified external upstream contribution with same-PR core-path and maintainer-approval evidence."
        elif external:interpretation="External contribution is verified, but the collected evidence is not sufficient for a strong technical endorsement."
        else:interpretation="Internal/discovery-repository contribution; useful for execution evidence, not external validation."
        rows.append({"title":value.get("title") or f"Merged PR #{value.get('number','?')}","repository":value.get("repository"),"number":value.get("number"),"url":evidence.get("source_url"),"observed_at":evidence.get("observed_at") or value.get("merged_or_closed_at"),"external":external,"recognized_upstream":bool(value.get("recognized_upstream")),"maintainer_accepted":bool(value.get("maintainer_accepted")),"core_files":core,"evidence_strength":strength,"evidence_facts":facts,"interpretation":interpretation})
    order={"strong":2,"moderate":1,"limited":0};rows.sort(key=lambda x:(order[x["evidence_strength"]],x["external"],x["recognized_upstream"]),reverse=True);return rows[:8]

def build_dossier(row:dict[str,Any])->dict[str,Any]:
    candidate=row.get("candidate") or {};drivers=row.get("drivers") or {};external=drivers.get("external_validation") or {};momentum=drivers.get("momentum") or {};confidence=drivers.get("confidence") or {};identity=candidate.get("identity") or {};status=row.get("recommendation_status") or "DISCOVERED";why=[]
    why.append(f"Recommendation: {status}")
    for reason in external.get("reasons") or []:why.append(reason)
    if float(row.get("momentum") or 0)>=60:why.append(f"Momentum is elevated at {row.get('momentum')}")
    if status=="WATCH" and not int(external.get("external_merged_prs") or 0):why.append("Internal execution may be strong, but verified external validation is still limited.")
    if status=="PROVEN / ALREADY VISIBLE":why.append("Strong evidence exists, but market visibility is already too high for an emerging-talent signal.")
    return {"schema_version":"0.4","identity":{"login":candidate.get("login"),"name":candidate.get("name"),"profile_url":candidate.get("profile_url"),"subject_id":identity.get("subject_id") or f"github:{str(candidate.get('login') or '').lower()}","github_user_id":identity.get("github_user_id"),"cross_source_status":identity.get("cross_source_status"),"confidence":row.get("evidence_confidence")},"signal":{"ghost_score":row.get("ghost_score"),"radar_score":row.get("radar_score"),"recommendation_status":status,"trend":row.get("trend"),"score_version":row.get("score_version"),"internal_capability":row.get("internal_capability"),"external_validation":row.get("external_validation"),"visibility_gap":row.get("visibility_gap")},"evidence_mix":row.get("evidence_mix") or {},"external_validation":external,"technical_focus":_technical_focus(candidate),"why_now":why,"trajectory":row.get("trajectory") or {},"activity":{"events_7d":momentum.get("events_7d"),"events_30d":momentum.get("events_30d"),"events_90d":momentum.get("events_90d"),"active_days_30d":momentum.get("active_days_30d"),"acceleration_ratio":momentum.get("acceleration_ratio")},"important_contributions":_important_contributions(candidate),"evidence":candidate.get("evidence") or [],"limitations":["Discovery is not a recommendation; STRONG/EARLY require verified external evidence gates.","External PR inspection is bounded and does not constitute a full independent code review.","A merged or maintainer-approved PR does not by itself prove originality, authorship quality, or employment suitability.","Missing evidence is not inferred; uncertain cross-source identity matches are not treated as verified.","The dossier is research intelligence, not an employment decision."]}
