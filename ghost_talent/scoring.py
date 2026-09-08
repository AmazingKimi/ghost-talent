import math
from dataclasses import asdict
from .models import Candidate

def _clamp(v):return round(max(0,min(100,float(v))),1)
def _repo_score(r):return min(85,7*math.log1p(min(max(int(r.get("contributions",0)),0),200))+3*math.log1p(max(int(r.get("stars",0)),0)))
def _external(e):
    substantive=int(e.get("substantive_external_prs",e.get("external_merged_prs",0)));verified=int(e.get("verified_external_project_prs",0));recognized=int(e.get("recognized_upstream_prs",0));core=int(e.get("core_path_prs",0));accepted=int(e.get("maintainer_accepted_prs",0))
    return _clamp(min(25,10*math.log1p(substantive))+min(25,18*math.log1p(verified))+min(15,12*math.log1p(recognized))+min(15,10*math.log1p(core))+min(20,14*math.log1p(accepted)))

def score_candidate(c:Candidate)->dict:
    repos=sorted([{**r,"capability_signal":round(_repo_score(r),1)} for r in c.repositories],key=lambda r:r["capability_signal"],reverse=True);internal=_clamp(sum(r["capability_signal"] for r in repos[:3])/max(1,len(repos[:3]))) if repos else 0
    ext=c.external_validation or {};external_available=bool(ext.get("available"));external=_external(ext) if external_available else 0.0
    coverage=c.momentum_coverage or {};prior=max(c.recent_events_90d-c.recent_events_30d,0);prior_week=prior/8.57 if prior else 0;history_sufficient=bool(coverage.get("history_sufficient",c.observed_event_span_days>=14 and prior>0));sample_truncated=bool(coverage.get("sample_truncated",False));acc=c.recent_events_7d/prior_week if history_sufficient and prior_week else 1.0
    if not c.recent_events_30d:momentum=0.0
    else:
        accel_component=_clamp(50+24*math.log2(max(acc,.25))) if history_sufficient else 50.0
        momentum=_clamp(.60*accel_component+25*min(c.active_days_30d/12,1)+15*min(c.recent_events_30d/20,1))
        if not history_sufficient:momentum=min(momentum,58.0)
        if sample_truncated:momentum=min(momentum,65.0)
    visibility=_clamp(12*math.log1p(max(c.followers,0)));capability=_clamp(.65*internal+.35*external);gap=_clamp(50+.45*(capability-visibility))
    external_count=int(ext.get("external_merged_prs",0)) if external_available else 0;substantive_count=int(ext.get("substantive_external_prs",external_count)) if external_available else 0;verified_count=int(ext.get("verified_external_project_prs",0)) if external_available else 0;recognized_count=int(ext.get("recognized_upstream_prs",0)) if external_available else 0;core_count=int(ext.get("core_path_prs",0)) if external_available else 0;accepted_count=int(ext.get("maintainer_accepted_prs",0)) if external_available else 0;accepted_core_count=int(ext.get("maintainer_accepted_core_path_prs",0)) if external_available else 0;recent_external=int(ext.get("recent_external_merged_prs",0)) if external_available else 0;recent_verified=int(ext.get("recent_verified_external_project_prs",0)) if external_available else 0;recent_recognized=int(ext.get("recent_recognized_upstream_prs",0)) if external_available else 0;recent_core=int(ext.get("recent_core_path_prs",0)) if external_available else 0;recent_accepted=int(ext.get("recent_maintainer_accepted_prs",0)) if external_available else 0;recent_accepted_core=int(ext.get("recent_maintainer_accepted_core_path_prs",0)) if external_available else 0
    self_repo_evidence=0;external_repo_evidence=0;unclassified_repo_evidence=0
    for r in c.repositories:
        contributions=max(int(r.get("contributions",0)),0);owner=str(r.get("owner_login") or "").lower()
        if owner and owner==c.login.lower():self_repo_evidence+=contributions
        elif owner:external_repo_evidence+=contributions
        else:unclassified_repo_evidence+=contributions
    external_pr_units=substantive_count*15+verified_count*30+recognized_count*10+core_count*15+accepted_count*20;research_units=sum(1 for p in c.paper_matches if p.get("identity_status")=="verified_external_link")*20;total=max(self_repo_evidence+external_repo_evidence+unclassified_repo_evidence+external_pr_units+research_units,1);mix={"self_owned_repo_pct":round(100*self_repo_evidence/total,1),"external_repository_contribution_pct":round(100*external_repo_evidence/total,1),"verified_external_pr_pct":round(100*external_pr_units/total,1),"verified_research_pct":round(100*research_units/total,1),"unclassified_repository_pct":round(100*unclassified_repo_evidence/total,1)}
    confidence=35+min(12,4*len(c.repositories))+(8 if c.name else 0)+(10 if substantive_count else 0)+(10 if verified_count else 0)+(5 if recognized_count else 0)+(8 if accepted_count else 0);noise_clear=(c.noise or {}).get("status","clear")=="clear";concentration=mix["self_owned_repo_pct"]>80 and substantive_count==0
    if concentration:confidence-=18
    if not noise_clear:confidence-=15
    if not external_available:confidence=min(confidence,35)
    if not history_sufficient:confidence-=5
    if sample_truncated:confidence-=5
    confidence=_clamp(confidence);ghost=_clamp(.30*capability+.25*external+.25*momentum+.10*gap+.10*confidence);radar=_clamp(.35*external+.25*momentum+.20*gap+.15*capability+.05*confidence)
    already_visible=bool(external_available and external>=60 and c.followers>=500);emerging_visibility=bool(c.followers<500);accepted_core=bool(recent_accepted_core>=1);credible_external=bool(recent_verified>=1 and (recent_accepted>=1 or recent_core>=1));recent_external_signal=bool(recent_external>=1)
    if not external_available:status="LOW CONFIDENCE"
    elif not noise_clear or confidence<40:status="LOW CONFIDENCE"
    elif already_visible:status="PROVEN / ALREADY VISIBLE"
    elif radar>=75 and external>=70 and confidence>=65 and emerging_visibility and accepted_core and history_sufficient:status="STRONG SIGNAL"
    elif radar>=65 and external>=50 and confidence>=55 and emerging_visibility and credible_external and history_sufficient:status="EARLY SIGNAL"
    elif radar>=50 or internal>=55:status="WATCH"
    else:status="DISCOVERED"
    early=status in {"STRONG SIGNAL","EARLY SIGNAL"};priority={"STRONG SIGNAL":5,"EARLY SIGNAL":4,"WATCH":3,"DISCOVERED":2,"PROVEN / ALREADY VISIBLE":1,"LOW CONFIDENCE":0}[status];reasons=[]
    if not external_available:reasons.append("external validation not inspected; recommendation confidence is capped")
    if external_count and not substantive_count:reasons.append(f"{external_count} external merged PR(s) found, but none passed the current substantive-change gate")
    elif substantive_count:reasons.append(f"{substantive_count} substantive external PR(s) in the inspected evidence")
    if verified_count:reasons.append(f"{verified_count} externally verified project PR(s) passed substantive + core/owner-member checks")
    if recognized_count:reasons.append(f"{recognized_count} substantive curated-upstream PR(s); curated status is context, not a mandatory recommendation gate")
    if core_count:reasons.append(f"{core_count} changed-file verified core-path PR(s)")
    if accepted_count:reasons.append(f"{accepted_count} owner/member-approved substantive external PR(s)")
    if recent_external:reasons.append(f"{recent_external} external merged PR(s) within the last {int(ext.get('recent_window_days',180))} days")
    if recent_verified:reasons.append(f"{recent_verified} recent verified external-project PR(s)")
    if recent_accepted_core:reasons.append(f"{recent_accepted_core} recent substantive core-path PR(s) approved by an owner/member on the same PR")
    if concentration:reasons.append("evidence concentration risk: >80% of weighted evidence is self-owned repository activity with no substantive external PR")
    if already_visible:reasons.append(f"already visible: {c.followers} GitHub followers with strong external validation")
    if not history_sufficient:reasons.append("momentum history is insufficient; acceleration is not inferred and EARLY/STRONG is withheld")
    if sample_truncated:reasons.append("GitHub public-event sample reached the 100-event cap; momentum is conservatively capped")
    if external_count and not recent_external_signal:reasons.append(f"external evidence exists, but none falls within the last {int(ext.get('recent_window_days',180))} days; emerging recommendation is withheld")
    return {"score_version":"0.2.8","ghost_score":ghost,"radar_score":radar,"capability":capability,"internal_capability":internal,"external_validation":external,"momentum":momentum,"visibility_gap":gap,"evidence_confidence":confidence,"recommendation_status":status,"discovery_priority":priority,"early_signal":early,"trend":"accelerating" if momentum>=65 and history_sufficient else "decelerating" if momentum<38 else "stable","evidence_mix":mix,"drivers":{"capability":{"internal":internal,"external":external,"top_repositories":repos[:3]},"external_validation":{**ext,"available":external_available,"score":external,"reasons":reasons},"evidence_mix":mix,"momentum":{"events_7d":c.recent_events_7d,"events_30d":c.recent_events_30d,"events_90d":c.recent_events_90d,"active_days_30d":c.active_days_30d,"acceleration_ratio":round(acc,2),"history_sufficient":history_sufficient,"sample_truncated":sample_truncated,"coverage":coverage},"visibility":{"followers":c.followers,"visibility_score":visibility,"visibility_proxy":"github_followers_log_scaled","emerging_visibility":emerging_visibility,"already_visible":already_visible},"confidence":{"score":confidence,"external_validation_available":external_available,"evidence_concentration_risk":concentration},"data_trust":{"noise_status":(c.noise or {}).get("status","clear"),"external_validation_coverage":"checked" if external_available else "not_checked","recent_external_evidence":recent_external_signal,"momentum_history_sufficient":history_sufficient,"event_sample_truncated":sample_truncated},"radar":{"score":radar,"recommendation_status":status,"requirements":{"external_validation":external,"external_validation_available":external_available,"noise_clear":noise_clear,"emerging_visibility":emerging_visibility,"credible_recent_external_project":credible_external,"recent_accepted_core_same_pr":accepted_core,"momentum_history_sufficient":history_sufficient}}},"candidate":asdict(c)}
