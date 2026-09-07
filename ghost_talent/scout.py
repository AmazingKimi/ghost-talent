from __future__ import annotations
import asyncio, os
from .identity import resolve_openalex_identity, stable_subject_id
from .models import Candidate, Evidence
from .scoring import score_candidate
from .sources.github import GitHubSource
from .sources.openalex import OpenAlexSource

def _source_status(result)->dict:
    if not isinstance(result,Exception):return {"status":"ok"}
    message=str(result).lower()
    if "rate limit" in message or "429" in message or "403" in message:return {"status":"rate_limited","detail":str(result)}
    return {"status":"unavailable","detail":str(result)}

async def scout(query:str,limit:int=20)->dict:
    github=GitHubSource(os.getenv("GITHUB_TOKEN"));openalex=OpenAlexSource()
    try:
        github_result,openalex_result=await asyncio.gather(github.discover(query),openalex.works(query),return_exceptions=True);sources={"github":_source_status(github_result),"openalex":_source_status(openalex_result)};github_candidates=[] if isinstance(github_result,Exception) else github_result;works=[] if isinstance(openalex_result,Exception) else openalex_result;scored=[]
        for item in github_candidates:
            subject_id=stable_subject_id(item);raw_matches=[] if isinstance(openalex_result,Exception) else openalex.match_author(item.get("name"),works);paper_matches=[]
            for match in raw_matches:
                resolved={**match,**resolve_openalex_identity(item,match)};paper_matches.append(resolved)
            evidence=[]
            for repo in item["repositories"]:evidence.append(Evidence(type="repository_contribution",source="github",source_url=repo["url"],subject_id=subject_id,value={"repository":repo["name"],"contributions":repo["contributions"],"stars":repo["stars"]}))
            quality=item.get("contribution_quality") or {};top_pr=quality.get("top_pr") or {}
            if quality.get("available") and top_pr.get("url"):evidence.append(Evidence(type="merged_pull_request",source="github",source_url=top_pr["url"],subject_id=subject_id,observed_at=top_pr.get("merged_or_closed_at"),value={"repository":quality.get("repository"),"number":top_pr.get("number"),"title":top_pr.get("title"),"core_file_count":top_pr.get("core_file_count",0),"core_files":top_pr.get("core_files",[]),"keyword_hits":top_pr.get("keyword_hits",[]),"patch_keyword_hits":top_pr.get("patch_keyword_hits",[]),"patch_available":top_pr.get("patch_available",False),"patch_sample_chars":top_pr.get("patch_sample_chars",0),"changed_code_lines_sampled":top_pr.get("changed_code_lines_sampled",0),"additions":top_pr.get("additions",0),"deletions":top_pr.get("deletions",0)}))
            for paper in paper_matches:
                confidence=float(paper.get("identity_confidence",0.35));evidence.append(Evidence(type="paper",source="openalex",source_url=paper["url"],subject_id=subject_id,observed_at=paper.get("publication_date"),value={"title":paper["title"],"citations":paper["cited_by_count"],"author":paper["author"],"openalex_author_id":paper.get("openalex_author_id"),"orcid":paper.get("orcid"),"identity_status":paper.get("identity_status","uncertain_name_match"),"identity_evidence":paper.get("identity_evidence",[])},confidence=confidence))
            identity={"subject_id":subject_id,"github_user_id":item.get("github_user_id"),"login":item.get("login"),"blog":item.get("blog"),"company":item.get("company"),"location":item.get("location"),"cross_source_status":"verified" if any(p.get("identity_status")=="verified_external_link" for p in paper_matches) else "uncertain" if paper_matches else "github_only"}
            candidate=Candidate(login=item["login"],name=item.get("name"),profile_url=item["profile_url"],followers=item["followers"],repositories=item["repositories"],recent_events_7d=item["recent_events_7d"],recent_events_30d=item["recent_events_30d"],recent_events_90d=item["recent_events_90d"],active_days_30d=item["active_days_30d"],observed_event_span_days=item["observed_event_span_days"],contribution_quality=quality,paper_matches=paper_matches,evidence=evidence,noise=item.get("noise") or {},identity=identity)
            scored.append(score_candidate(candidate))
        scored.sort(key=lambda row:row["ghost_score"],reverse=True)
        if sources["github"]["status"]=="ok" and not scored:sources["github"]={"status":"ok","detail":"No candidates matched this query."}
        if sources["openalex"]["status"]=="ok" and not works:sources["openalex"]={"status":"ok","detail":"No research works matched this query."}
        return {"results":scored[:limit],"sources":sources}
    finally:await github.close();await openalex.close()
