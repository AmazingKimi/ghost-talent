from __future__ import annotations
import asyncio,time
from collections import defaultdict
from datetime import datetime,timedelta,timezone
import httpx
API="https://api.github.com"
CORE_TERMS=("cuda","triton","kernel","kernels","compiler","inference","attention","gemm","moe","quant","quantization","nvfp","fp8","int8","runtime","backend","gpu","csrc","ops","benchmark","benchmarks")
NOISE_REPO_TERMS=("course","courses","homework","assignment","assignments","tutorial","tutorials","leetcode","bootcamp","classroom","lab-assignment")
BOT_LOGIN_TERMS=("[bot]","-bot","_bot","dependabot","renovate","github-actions")
RECOGNIZED_UPSTREAM=("vllm-project/vllm","ggerganov/llama.cpp","pytorch/pytorch","triton-lang/triton","sgl-project/sglang","huggingface/transformers","huggingface/text-generation-inference","flashinfer-ai/flashinfer","dao-ai-lab/flash-attention","nvidia/cutlass")
MAINTAINER_ASSOCIATIONS={"OWNER","MEMBER","COLLABORATOR"}
_CACHE={};_CACHE_TTL_SECONDS=300
class GitHubSource:
 def __init__(self,token:str|None=None):
  headers={"Accept":"application/vnd.github+json"};
  if token:headers["Authorization"]=f"Bearer {token}"
  self.authenticated=bool(token);self.client=httpx.AsyncClient(headers=headers,timeout=20.0);self._semaphore=asyncio.Semaphore(6)
 async def close(self):await self.client.aclose()
 async def _get(self,url:str,**params):
  key=f"{url}?{sorted(params.items())}";cached=_CACHE.get(key);now=time.monotonic()
  if cached and now-cached[0]<_CACHE_TTL_SECONDS:return cached[1]
  async with self._semaphore:r=await self.client.get(url,params=params or None);r.raise_for_status();data=r.json()
  _CACHE[key]=(now,data);return data
 @staticmethod
 def _candidate(candidates,login,profile_url=None):
  item=candidates[login];item["login"]=login;item["profile_url"]=profile_url or item.get("profile_url") or f"https://github.com/{login}";item.setdefault("repositories",[]);item.setdefault("discovery_sources",[]);item.setdefault("merged_pr_discoveries",[]);return item
 @staticmethod
 def _primary_repo(item):
  repos=item.get("repositories",[]);return max(repos,key=lambda r:(int(r.get("contributions",0)),int(r.get("stars",0)))).get("name","unknown") if repos else "unknown"
 @classmethod
 def _diversify(cls,ranked,limit,max_per_repo):
  selected=[];overflow=[];counts=defaultdict(int)
  for item in ranked:
   p=cls._primary_repo(item)
   if counts[p]<max_per_repo:selected.append(item);counts[p]+=1
   else:overflow.append(item)
   if len(selected)>=limit:return selected
  return (selected+overflow)[:limit]
 @staticmethod
 def _noise_signals(item,profile):
  login=str(item.get("login") or "").lower();reasons=[];repos=item.get("repositories",[]);noisy=[]
  if str((profile or {}).get("type") or "User")!="User" or any(t in login for t in BOT_LOGIN_TERMS):reasons.append("bot_or_automation_identity")
  for repo in repos:
   if any(t in str(repo.get("name") or "").lower() for t in NOISE_REPO_TERMS):noisy.append(repo.get("name"))
  if noisy and len(noisy)>=max(1,len(repos)//2):reasons.append("course_or_exercise_repository_pattern")
  return {"status":"flagged" if reasons else "clear","reasons":reasons,"noise_repositories":noisy[:5]}
 async def discover(self,query,repo_limit=15,candidate_limit=20,contributor_limit=25,quality_budget=12,pr_repo_budget=10,pr_limit=20):
  search=await self._get(f"{API}/search/repositories",q=query,sort="stars",order="desc",per_page=repo_limit);repositories=search.get("items",[]);candidates=defaultdict(dict)
  async def lc(repo):
   try:return repo,await self._get(repo["contributors_url"],per_page=contributor_limit)
   except httpx.HTTPStatusError as e:
    if e.response.status_code in {403,404,429}:return repo,[]
    raise
  for repo,contributors in await asyncio.gather(*(lc(r) for r in repositories)):
   for c in contributors:
    login=str(c.get("login") or "")
    if c.get("type")!="User" or not login or any(t in login.lower() for t in BOT_LOGIN_TERMS):continue
    item=self._candidate(candidates,login,c.get("html_url"));item["repositories"].append({"name":repo["full_name"],"url":repo["html_url"],"stars":repo.get("stargazers_count",0),"contributions":c.get("contributions",0),"owner_login":(repo.get("owner") or {}).get("login")})
  async def lp(repo):
   try:return repo,await self._get(f"{API}/repos/{repo['full_name']}/pulls",state="closed",sort="updated",direction="desc",per_page=pr_limit)
   except httpx.HTTPStatusError as e:
    if e.response.status_code in {403,404,429}:return repo,[]
    raise
  if self.authenticated:
   for repo,pulls in await asyncio.gather(*(lp(r) for r in repositories[:pr_repo_budget])):
    for pull in pulls:
     user=pull.get("user") or {};login=user.get("login")
     if not pull.get("merged_at") or not login or user.get("type")!="User" or any(t in login.lower() for t in BOT_LOGIN_TERMS):continue
     item=self._candidate(candidates,login,user.get("html_url"));item["merged_pr_discoveries"].append({"repository":repo["full_name"],"number":pull.get("number"),"title":pull.get("title"),"url":pull.get("html_url"),"merged_at":pull.get("merged_at")})
     if not any(r["name"]==repo["full_name"] for r in item["repositories"]):item["repositories"].append({"name":repo["full_name"],"url":repo["html_url"],"stars":repo.get("stargazers_count",0),"contributions":0,"owner_login":(repo.get("owner") or {}).get("login")})
  ranked=self._diversify(sorted(candidates.values(),key=lambda c:(len(c.get("merged_pr_discoveries",[]))>0,sum(r["contributions"] for r in c.get("repositories",[])),len(c.get("repositories",[]))),reverse=True),candidate_limit,max(2,candidate_limit//5))
  async def enrich(index,item):
   profile=None;events=[]
   try:profile,events=await asyncio.gather(self._get(f"{API}/users/{item['login']}"),self._get(f"{API}/users/{item['login']}/events/public",per_page=100))
   except httpx.HTTPStatusError as e:
    if e.response.status_code not in {403,404,429}:raise
   quality=self._empty_quality();external=self._empty_external()
   if self.authenticated and index<quality_budget:quality,external=await asyncio.gather(self._contribution_quality(item),self._external_validation(item))
   return {**item,"github_user_id":profile.get("id") if profile else None,"blog":profile.get("blog") if profile else None,"company":profile.get("company") if profile else None,"location":profile.get("location") if profile else None,"primary_repository":self._primary_repo(item),"name":profile.get("name") if profile else None,"profile_url":profile.get("html_url") if profile else item["profile_url"],"followers":profile.get("followers",0) if profile else 0,"noise":self._noise_signals(item,profile),"contribution_quality":quality,"external_validation":external,**self._event_counts(events)}
  return await asyncio.gather(*(enrich(i,x) for i,x in enumerate(ranked)))
 async def _external_validation(self,item):
  login=item["login"]
  try:data=await self._get(f"{API}/search/issues",q=f"author:{login} type:pr is:merged",sort="updated",order="desc",per_page=20)
  except httpx.HTTPStatusError:return self._empty_external()
  rows=[]
  for pr in data.get("items",[])[:20]:
   repo_url=str(pr.get("repository_url") or "");repo=repo_url.split("/repos/")[-1] if "/repos/" in repo_url else "";owner=repo.split("/",1)[0].lower() if "/" in repo else "";recognized=repo.lower() in RECOGNIZED_UPSTREAM
   if owner==login.lower():continue
   rows.append({"repository":repo,"number":pr.get("number"),"title":pr.get("title"),"url":pr.get("html_url"),"recognized_upstream":recognized,"core_path_signal":False,"core_path_evidence":"not_inspected","maintainer_accepted":False,"maintainer_acceptance_evidence":"not_inspected"})
  # High-value claims require direct evidence from the PR, never inference from title or merge alone.
  inspect=[row for row in rows if row["recognized_upstream"]][:5]
  async def verify(row):
   try:
    files,reviews=await asyncio.gather(self._get(f"{API}/repos/{row['repository']}/pulls/{row['number']}/files",per_page=30),self._get(f"{API}/repos/{row['repository']}/pulls/{row['number']}/reviews",per_page=30))
   except httpx.HTTPStatusError:return row
   names=[str(f.get("filename") or "") for f in files];core_files=[name for name in names if self._is_core_path(name)]
   approvals=[]
   for review in reviews:
    reviewer=review.get("user") or {};association=str(review.get("author_association") or "").upper();state=str(review.get("state") or "").upper()
    if state=="APPROVED" and association in MAINTAINER_ASSOCIATIONS and str(reviewer.get("login") or "").lower()!=login.lower():approvals.append({"login":reviewer.get("login"),"author_association":association,"submitted_at":review.get("submitted_at")})
   return {**row,"core_path_signal":bool(core_files),"core_path_evidence":"changed_files","core_files":core_files[:6],"changed_files_sampled":len(names),"maintainer_accepted":bool(approvals),"maintainer_acceptance_evidence":"approved_review" if approvals else "reviews_inspected_no_maintainer_approval","maintainer_approvals":approvals[:3]}
  verified=await asyncio.gather(*(verify(row) for row in inspect)) if inspect else []
  by_key={(r["repository"],r["number"]):r for r in verified};rows=[by_key.get((r["repository"],r["number"]),r) for r in rows]
  recognized=sum(1 for x in rows if x["recognized_upstream"]);core=sum(1 for x in rows if x["core_path_signal"] and x.get("core_path_evidence")=="changed_files");accepted=sum(1 for x in rows if x.get("maintainer_accepted") and x.get("maintainer_acceptance_evidence")=="approved_review");return {"available":True,"external_merged_prs":len(rows),"recognized_upstream_prs":recognized,"core_path_prs":core,"core_path_prs_inspected":len(verified),"maintainer_accepted_prs":accepted,"maintainer_review_prs_inspected":len(verified),"prs":rows[:8]}
 async def _contribution_quality(self,item):
  repos=sorted(item.get("repositories",[]),key=lambda r:int(r.get("contributions",0)),reverse=True)
  if not repos:return self._empty_quality()
  repo=repos[0]["name"];login=item["login"]
  try:search=await self._get(f"{API}/search/issues",q=f"repo:{repo} author:{login} type:pr is:merged",sort="updated",order="desc",per_page=3)
  except httpx.HTTPStatusError:return self._empty_quality(repo)
  prs=search.get("items",[])[:3]
  if not prs:return self._empty_quality(repo)
  top=prs[0];files=[]
  try:files=await self._get(f"{API}/repos/{repo}/pulls/{top['number']}/files",per_page=30)
  except httpx.HTTPStatusError:pass
  names=[str(f.get("filename",'')) for f in files];core=[n for n in names if self._is_core_path(n)];keywords=sorted({t for t in CORE_TERMS if t in str(top.get("title") or '').lower() or any(t in n.lower() for n in names)})
  return {"available":True,"repository":repo,"merged_pr_count":int(search.get("total_count",len(prs))),"sampled_pr_count":len(prs),"top_pr":{"number":top.get("number"),"title":top.get("title"),"url":top.get("html_url"),"merged_or_closed_at":top.get("closed_at"),"changed_files_sampled":len(files),"core_files":core[:8],"core_file_count":len(core),"keyword_hits":keywords,"additions":sum(int(f.get("additions",0)) for f in files),"deletions":sum(int(f.get("deletions",0)) for f in files)}}
 @staticmethod
 def _is_core_path(filename):return any(t in filename.lower() for t in CORE_TERMS) or filename.lower().endswith((".cu",".cuh",".cc",".cpp"))
 @staticmethod
 def _empty_quality(repository=None):return {"available":False,"repository":repository,"merged_pr_count":0,"sampled_pr_count":0,"top_pr":None}
 @staticmethod
 def _empty_external():return {"available":False,"external_merged_prs":0,"recognized_upstream_prs":0,"core_path_prs":0,"core_path_prs_inspected":0,"maintainer_accepted_prs":0,"maintainer_review_prs_inspected":0,"prs":[]}
 @staticmethod
 def _event_counts(events):
  now=datetime.now(timezone.utc);d7=now-timedelta(days=7);d30=now-timedelta(days=30);d90=now-timedelta(days=90);c7=c30=c90=0;days=set();ts=[]
  for e in events:
   if not e.get("created_at"):continue
   t=datetime.fromisoformat(e["created_at"].replace("Z","+00:00"));ts.append(t);c90+=t>=d90;c30+=t>=d30;c7+=t>=d7
   if t>=d30:days.add(t.date().isoformat())
  span=max((max(ts)-min(ts)).total_seconds()/86400,0) if len(ts)>=2 else 0
  return {"recent_events_7d":c7,"recent_events_30d":c30,"recent_events_90d":c90,"active_days_30d":len(days),"observed_event_span_days":round(span,2)}