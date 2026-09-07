from __future__ import annotations
import asyncio,os
from .identity import resolve_openalex_identity,stable_subject_id
from .models import Candidate,Evidence
from .scoring import score_candidate
from .sources.github import GitHubSource
from .sources.openalex import OpenAlexSource
def _source_status(r):
 if not isinstance(r,Exception):return {"status":"ok"}
 m=str(r).lower();return {"status":"rate_limited" if any(x in m for x in ("rate limit","429","403")) else "unavailable","detail":str(r)}
async def scout(query:str,limit:int=20)->dict:
 github=GitHubSource(os.getenv("GITHUB_TOKEN"));openalex=OpenAlexSource()
 try:
  gr,oa=await asyncio.gather(github.discover(query),openalex.works(query),return_exceptions=True);sources={"github":_source_status(gr),"openalex":_source_status(oa)};items=[] if isinstance(gr,Exception) else gr;works=[] if isinstance(oa,Exception) else oa;scored=[]
  for item in items:
   sid=stable_subject_id(item);matches=[]
   if not isinstance(oa,Exception):matches=[{**m,**resolve_openalex_identity(item,m)} for m in openalex.match_author(item.get("name"),works)]
   evidence=[]
   for repo in item["repositories"]:evidence.append(Evidence(type="repository_contribution",source="github",source_url=repo["url"],subject_id=sid,value={"repository":repo["name"],"contributions":repo["contributions"],"stars":repo["stars"],"owner_login":repo.get("owner_login")}))
   quality=item.get("contribution_quality") or {};top=quality.get("top_pr") or {}
   if quality.get("available") and top.get("url"):evidence.append(Evidence(type="merged_pull_request",source="github",source_url=top["url"],subject_id=sid,observed_at=top.get("merged_or_closed_at"),value={"repository":quality.get("repository"),"number":top.get("number"),"title":top.get("title"),"core_file_count":top.get("core_file_count",0),"core_files":top.get("core_files",[]),"keyword_hits":top.get("keyword_hits",[]),"additions":top.get("additions",0),"deletions":top.get("deletions",0)}))
   external=item.get("external_validation") or {}
   for pr in external.get("prs",[]):evidence.append(Evidence(type="external_merged_pull_request",source="github",source_url=pr.get("url") or "",subject_id=sid,value=pr))
   for p in matches:evidence.append(Evidence(type="paper",source="openalex",source_url=p["url"],subject_id=sid,observed_at=p.get("publication_date"),value={"title":p["title"],"citations":p["cited_by_count"],"author":p["author"],"openalex_author_id":p.get("openalex_author_id"),"identity_status":p.get("identity_status")},confidence=float(p.get("identity_confidence",.35))))
   identity={"subject_id":sid,"github_user_id":item.get("github_user_id"),"login":item.get("login"),"blog":item.get("blog"),"company":item.get("company"),"location":item.get("location"),"cross_source_status":"verified" if any(p.get("identity_status")=="verified_external_link" for p in matches) else "uncertain" if matches else "github_only"}
   c=Candidate(login=item["login"],name=item.get("name"),profile_url=item["profile_url"],followers=item["followers"],repositories=item["repositories"],recent_events_7d=item["recent_events_7d"],recent_events_30d=item["recent_events_30d"],recent_events_90d=item["recent_events_90d"],active_days_30d=item["active_days_30d"],observed_event_span_days=item["observed_event_span_days"],contribution_quality=quality,paper_matches=matches,evidence=evidence,noise=item.get("noise") or {},identity=identity,external_validation=external);scored.append(score_candidate(c))
  scored.sort(key=lambda x:(x.get("discovery_priority",0),x["radar_score"],x["ghost_score"]),reverse=True);return {"results":scored[:limit],"sources":sources}
 finally:await github.close();await openalex.close()