import math
from dataclasses import asdict
from .models import Candidate
def _clamp(v):return round(max(0,min(100,float(v))),1)
def _repo_score(r):return min(85,7*math.log1p(min(max(int(r.get("contributions",0)),0),200))+3*math.log1p(max(int(r.get("stars",0)),0)))
def _external(e):
 merged=int(e.get("external_merged_prs",0));recognized=int(e.get("recognized_upstream_prs",0));core=int(e.get("core_path_prs",0));score=_clamp(min(45,16*math.log1p(merged))+min(35,22*math.log1p(recognized))+min(20,13*math.log1p(core)));return score
def score_candidate(c:Candidate)->dict:
 repos=sorted([{**r,"capability_signal":round(_repo_score(r),1)} for r in c.repositories],key=lambda r:r["capability_signal"],reverse=True);internal=_clamp(sum(r["capability_signal"] for r in repos[:3])/max(1,len(repos[:3]))) if repos else 0;ext=c.external_validation or {};external=_external(ext)
 prior=max(c.recent_events_90d-c.recent_events_30d,0);prior_week=prior/8.57 if prior else 0;acc=c.recent_events_7d/prior_week if prior_week else (1.6 if c.recent_events_7d else 0);momentum=0 if not c.recent_events_30d else _clamp(.65*_clamp(50+24*math.log2(max(acc,.25)))+20*min(c.active_days_30d/12,1)+15*(min(30/c.observed_event_span_days,2)/2 if c.observed_event_span_days else 0));visibility=_clamp(18*math.log1p(max(c.followers,0)));capability=_clamp(.65*internal+.35*external);gap=_clamp(50+.6*(capability-visibility))
 external_count=int(ext.get("external_merged_prs",0));self_evidence=max(sum(int(r.get("contributions",0)) for r in c.repositories),0);external_units=external_count*20+int(ext.get("recognized_upstream_prs",0))*25+int(ext.get("core_path_prs",0))*15;research_units=sum(1 for p in c.paper_matches if p.get("identity_status")=="verified_external_link")*20;total=max(self_evidence+external_units+research_units,1);mix={"self_owned_or_discovery_repo_pct":round(100*self_evidence/total,1),"external_upstream_pct":round(100*external_units/total,1),"verified_research_pct":round(100*research_units/total,1)}
 confidence=35+min(12,4*len(c.repositories))+(8 if c.name else 0)+(12 if external_count else 0)+(8 if ext.get("recognized_upstream_prs") else 0);noise_clear=(c.noise or {}).get("status","clear")=="clear";concentration=mix["self_owned_or_discovery_repo_pct"]>80 and external_count==0
 if concentration:confidence-=18
 if not noise_clear:confidence-=15
 confidence=_clamp(confidence);ghost=_clamp(.30*capability+.25*external+.25*momentum+.10*gap+.10*confidence);radar=_clamp(.35*external+.25*momentum+.20*gap+.15*capability+.05*confidence)
 if not noise_clear or confidence<40:status="LOW CONFIDENCE"
 elif radar>=75 and external>=70 and confidence>=65:status="STRONG SIGNAL"
 elif radar>=65 and external>=50 and confidence>=55:status="EARLY SIGNAL"
 elif radar>=50 or internal>=55:status="WATCH"
 else:status="DISCOVERED"
 early=status in {"STRONG SIGNAL","EARLY SIGNAL"};reasons=[]
 if external_count:reasons.append(f"{external_count} external merged PR(s)")
 if ext.get("recognized_upstream_prs"):reasons.append(f"{ext['recognized_upstream_prs']} recognized upstream PR(s)")
 if ext.get("core_path_prs"):reasons.append(f"{ext['core_path_prs']} core-path external PR signal(s)")
 if concentration:reasons.append("evidence concentration risk: >80% self/discovery-repo activity with no external merged PR")
 return {"score_version":"0.2.0","ghost_score":ghost,"radar_score":radar,"capability":capability,"internal_capability":internal,"external_validation":external,"momentum":momentum,"visibility_gap":gap,"evidence_confidence":confidence,"recommendation_status":status,"early_signal":early,"trend":"accelerating" if momentum>=65 else "decelerating" if momentum<38 else "stable","evidence_mix":mix,"drivers":{"capability":{"internal":internal,"external":external,"top_repositories":repos[:3]},"external_validation":{**ext,"score":external,"reasons":reasons},"evidence_mix":mix,"momentum":{"events_7d":c.recent_events_7d,"events_30d":c.recent_events_30d,"events_90d":c.recent_events_90d,"active_days_30d":c.active_days_30d,"acceleration_ratio":round(acc,2)},"visibility":{"followers":c.followers,"visibility_score":visibility},"confidence":{"score":confidence,"evidence_concentration_risk":concentration},"data_trust":{"noise_status":(c.noise or {}).get("status","clear")},"radar":{"score":radar,"recommendation_status":status,"requirements":{"external_validation":external,"noise_clear":noise_clear}}},"candidate":asdict(c)}