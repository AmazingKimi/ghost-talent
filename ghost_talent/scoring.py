import math
from dataclasses import asdict
from .models import Candidate
def _clamp(v):return round(max(0,min(100,float(v))),1)
def _repo_score(r):return min(85,7*math.log1p(min(max(int(r.get("contributions",0)),0),200))+3*math.log1p(max(int(r.get("stars",0)),0)))
def _external(e):
 merged=int(e.get("external_merged_prs",0));recognized=int(e.get("recognized_upstream_prs",0));core=int(e.get("core_path_prs",0));accepted=int(e.get("maintainer_accepted_prs",0));score=_clamp(min(35,13*math.log1p(merged))+min(25,17*math.log1p(recognized))+min(20,13*math.log1p(core))+min(20,14*math.log1p(accepted)));return score
def score_candidate(c:Candidate)->dict:
 repos=sorted([{**r,"capability_signal":round(_repo_score(r),1)} for r in c.repositories],key=lambda r:r["capability_signal"],reverse=True);internal=_clamp(sum(r["capability_signal"] for r in repos[:3])/max(1,len(repos[:3]))) if repos else 0;ext=c.external_validation or {};external_available=bool(ext.get("available"));external=_external(ext) if external_available else 0.0
 prior=max(c.recent_events_90d-c.recent_events_30d,0);prior_week=prior/8.57 if prior else 0;acc=c.recent_events_7d/prior_week if prior_week else (1.6 if c.recent_events_7d else 0);momentum=0 if not c.recent_events_30d else _clamp(.65*_clamp(50+24*math.log2(max(acc,.25)))+20*min(c.active_days_30d/12,1)+15*(min(30/c.observed_event_span_days,2)/2 if c.observed_event_span_days else 0));visibility=_clamp(18*math.log1p(max(c.followers,0)));capability=_clamp(.65*internal+.35*external);gap=_clamp(50+.6*(capability-visibility))
 external_count=int(ext.get("external_merged_prs",0)) if external_available else 0;recognized_count=int(ext.get("recognized_upstream_prs",0)) if external_available else 0;core_count=int(ext.get("core_path_prs",0)) if external_available else 0;accepted_count=int(ext.get("maintainer_accepted_prs",0)) if external_available else 0;accepted_core_count=int(ext.get("maintainer_accepted_core_path_prs",0)) if external_available else 0
 self_repo_evidence=0;external_repo_evidence=0;unclassified_repo_evidence=0
 for r in c.repositories:
  contributions=max(int(r.get("contributions",0)),0);owner=str(r.get("owner_login") or "").lower()
  if owner and owner==c.login.lower():self_repo_evidence+=contributions
  elif owner:external_repo_evidence+=contributions
  else:unclassified_repo_evidence+=contributions
 external_pr_units=external_count*20+recognized_count*25+core_count*15+accepted_count*20;research_units=sum(1 for p in c.paper_matches if p.get("identity_status")=="verified_external_link")*20;total=max(self_repo_evidence+external_repo_evidence+unclassified_repo_evidence+external_pr_units+research_units,1);mix={"self_owned_repo_pct":round(100*self_repo_evidence/total,1),"external_repository_contribution_pct":round(100*external_repo_evidence/total,1),"verified_external_pr_pct":round(100*external_pr_units/total,1),"verified_research_pct":round(100*research_units/total,1),"unclassified_repository_pct":round(100*unclassified_repo_evidence/total,1)}
 confidence=35+min(12,4*len(c.repositories))+(8 if c.name else 0)+(10 if external_count else 0)+(8 if recognized_count else 0)+(8 if accepted_count else 0);noise_clear=(c.noise or {}).get("status","clear")=="clear";concentration=mix["self_owned_repo_pct"]>80 and external_count==0
 if concentration:confidence-=18
 if not noise_clear:confidence-=15
 if not external_available:confidence=min(confidence,35)
 confidence=_clamp(confidence);ghost=_clamp(.30*capability+.25*external+.25*momentum+.10*gap+.10*confidence);radar=_clamp(.35*external+.25*momentum+.20*gap+.15*capability+.05*confidence)
 already_visible=bool(external_available and external>=60 and c.followers>=500);emerging_visibility=bool(c.followers<500);accepted_core=bool(accepted_core_count>=1);credible_upstream=bool(recognized_count>=1 and (accepted_count>=1 or core_count>=1))
 if not external_available:status="LOW CONFIDENCE"
 elif not noise_clear or confidence<40:status="LOW CONFIDENCE"
 elif already_visible:status="PROVEN / ALREADY VISIBLE"
 elif radar>=75 and external>=70 and confidence>=65 and emerging_visibility and accepted_core:status="STRONG SIGNAL"
 elif radar>=65 and external>=50 and confidence>=55 and emerging_visibility and credible_upstream:status="EARLY SIGNAL"
 elif radar>=50 or internal>=55:status="WATCH"
 else:status="DISCOVERED"
 early=status in {"STRONG SIGNAL","EARLY SIGNAL"};priority={"STRONG SIGNAL":5,"EARLY SIGNAL":4,"WATCH":3,"DISCOVERED":2,"PROVEN / ALREADY VISIBLE":1,"LOW CONFIDENCE":0}[status];reasons=[]
 if not external_available:reasons.append("external validation not inspected; recommendation confidence is capped")
 if external_count:reasons.append(f"{external_count} external merged PR(s)")
 if recognized_count:reasons.append(f"{recognized_count} recognized upstream PR(s)")
 if core_count:reasons.append(f"{core_count} changed-file verified core-path PR(s)")
 if accepted_count:reasons.append(f"{accepted_count} maintainer-approved upstream PR(s)")
 if accepted_core_count:reasons.append(f"{accepted_core_count} core-path PR(s) approved by a maintainer on the same PR")
 if concentration:reasons.append("evidence concentration risk: >80% of weighted evidence is self-owned repository activity with no external merged PR")
 if already_visible:reasons.append(f"already visible: {c.followers} GitHub followers with strong external validation")
 if status=="WATCH" and recognized_count and not credible_upstream:reasons.append("upstream presence exists, but core-path or maintainer-approval evidence is not yet verified")
 if status!="STRONG SIGNAL" and accepted_count and core_count and not accepted_core_count:reasons.append("maintainer approval and core-path evidence exist, but not on the same verified PR")
 return {"score_version":"0.2.5","ghost_score":ghost,"radar_score":radar,"capability":capability,"internal_capability":internal,"external_validation":external,"momentum":momentum,"visibility_gap":gap,"evidence_confidence":confidence,"recommendation_status":status,"discovery_priority":priority,"early_signal":early,"trend":"accelerating" if momentum>=65 else "decelerating" if momentum<38 else "stable","evidence_mix":mix,"drivers":{"capability":{"internal":internal,"external":external,"top_repositories":repos[:3]},"external_validation":{**ext,"available":external_available,"score":external,"reasons":reasons},"evidence_mix":mix,"momentum":{"events_7d":c.recent_events_7d,"events_30d":c.recent_events_30d,"events_90d":c.recent_events_90d,"active_days_30d":c.active_days_30d,"acceleration_ratio":round(acc,2)},"visibility":{"followers":c.followers,"visibility_score":visibility,"emerging_visibility":emerging_visibility,"already_visible":already_visible},"confidence":{"score":confidence,"external_validation_available":external_available,"evidence_concentration_risk":concentration},"data_trust":{"noise_status":(c.noise or {}).get("status","clear"),"external_validation_coverage":"checked" if external_available else "not_checked"},"radar":{"score":radar,"recommendation_status":status,"requirements":{"external_validation":external,"external_validation_available":external_available,"noise_clear":noise_clear,"emerging_visibility":emerging_visibility,"credible_upstream":credible_upstream,"accepted_core_same_pr":accepted_core}}},"candidate":asdict(c)}