import math
from dataclasses import asdict
from .models import Candidate

def _clamp(value:float)->float:return round(max(0.0,min(100.0,value)),1)
def _repo_capability(repository:dict)->float:
    contributions=max(int(repository.get("contributions",0)),0);stars=max(int(repository.get("stars",0)),0);return min(92.0,8.0*math.log1p(min(contributions,250))+4.0*math.log1p(stars))
def _contribution_quality(candidate:Candidate)->tuple[float,dict]:
    quality=candidate.contribution_quality or {};top_pr=quality.get("top_pr") or {}
    if not quality.get("available") or not top_pr:return 0.0,{"available":False,"score":0.0,"reason":"merged PR quality evidence unavailable"}
    merged=max(int(quality.get("merged_pr_count",0)),0);core=max(int(top_pr.get("core_file_count",0)),0);changed=max(int(top_pr.get("changed_files_sampled",0)),0);keywords=top_pr.get("keyword_hits") or [];volume=max(int(top_pr.get("additions",0)),0)+max(int(top_pr.get("deletions",0)),0);core_ratio=min(core/max(changed,1),1.0);score=_clamp(min(28.0,12.0*math.log1p(merged))+34.0*core_ratio+min(22.0,5.5*len(keywords))+min(16.0,4.0*math.log1p(volume)));return score,{"available":True,"score":score,"repository":quality.get("repository"),"merged_pr_count":merged,"top_pr":top_pr,"core_ratio":round(core_ratio,2)}
def score_candidate(candidate:Candidate)->dict:
    repos=[{**r,"capability_signal":round(_repo_capability(r),1)} for r in candidate.repositories];repos.sort(key=lambda r:r["capability_signal"],reverse=True);scores=[r["capability_signal"] for r in repos];base=_clamp(sum(scores[:3])/len(scores[:3])+4.0*math.log1p(len(scores))) if scores else 0.0;quality,qdriver=_contribution_quality(candidate);capability=_clamp(base+0.18*quality)
    prior=max(candidate.recent_events_90d-candidate.recent_events_30d,0);prior_week=prior/8.57 if prior else 0.0;current=float(candidate.recent_events_7d);acc=current/prior_week if prior_week>0 else 1.6 if current>0 else 0.0;active=min(candidate.active_days_30d/12.0,1.0);density=min(30.0/candidate.observed_event_span_days,2.0)/2.0 if candidate.observed_event_span_days>0 else 0.0;momentum=0.0 if candidate.recent_events_30d==0 else _clamp(0.65*_clamp(50.0+24.0*math.log2(max(acc,0.25)))+20.0*active+15.0*density)
    visibility=_clamp(18.0*math.log1p(max(candidate.followers,0)));gap=_clamp(50.0+0.6*(capability-visibility));reasons=["GitHub repository contribution evidence"];confidence=35.0
    if candidate.name:confidence+=8.0;reasons.append("public GitHub name available")
    confidence+=min(12.0,4.0*len(candidate.repositories))
    if len(candidate.repositories)>1:reasons.append(f"evidence across {len(candidate.repositories)} repositories")
    if qdriver.get("available"):confidence+=8.0;reasons.append("merged PR quality evidence")
    verified=[p for p in candidate.paper_matches if p.get("identity_status")=="verified"];uncertain=[p for p in candidate.paper_matches if p.get("identity_status")!="verified"]
    if verified:confidence+=10.0+min(10.0,5.0*max(len(verified)-1,0));reasons.append(f"{len(verified)} verified OpenAlex match(es)")
    if uncertain:reasons.append(f"{len(uncertain)} uncertain OpenAlex name match(es) excluded from confidence")
    noise=candidate.noise or {};noise_clear=noise.get("status","clear")=="clear"
    if not noise_clear:confidence-=15.0;reasons.append("data trust noise flag: "+", ".join(noise.get("reasons") or ["unspecified"]))
    confidence=_clamp(confidence);ghost=_clamp(.35*capability+.35*momentum+.20*gap+.10*confidence);trend="accelerating" if momentum>=65 else "decelerating" if momentum<38 else "stable";radar=_clamp(.35*momentum+.30*quality+.25*gap+.10*confidence);early=bool(noise_clear and qdriver.get("available") and radar>=65 and momentum>=60 and gap>=45);top=repos[0] if repos else None
    drivers={"capability":{"repository_count":len(candidate.repositories),"base_capability":base,"contribution_quality":quality,"top_repository":top,"top_repositories":repos[:3]},"contribution_quality":qdriver,"momentum":{"events_7d":candidate.recent_events_7d,"events_30d":candidate.recent_events_30d,"events_90d":candidate.recent_events_90d,"active_days_30d":candidate.active_days_30d,"current_weekly_rate":round(current,2),"prior_weekly_rate":round(prior_week,2),"acceleration_ratio":round(acc,2),"observed_event_span_days":candidate.observed_event_span_days},"visibility":{"followers":candidate.followers,"visibility_score":visibility},"confidence":{"paper_matches":len(candidate.paper_matches),"verified_paper_matches":len(verified),"uncertain_paper_matches":len(uncertain),"reasons":reasons},"data_trust":{"noise_status":noise.get("status","clear"),"noise_reasons":noise.get("reasons") or [],"noise_repositories":noise.get("noise_repositories") or []},"radar":{"score":radar,"early_signal":early,"requirements":{"quality_evidence":bool(qdriver.get("available")),"noise_clear":noise_clear,"momentum_at_least_60":momentum>=60,"visibility_gap_at_least_45":gap>=45,"radar_score_at_least_65":radar>=65}}}
    return {"score_version":"0.1.6","ghost_score":ghost,"capability":capability,"momentum":momentum,"visibility_gap":gap,"evidence_confidence":confidence,"trend":trend,"radar_score":radar,"early_signal":early,"drivers":drivers,"candidate":asdict(candidate)}
