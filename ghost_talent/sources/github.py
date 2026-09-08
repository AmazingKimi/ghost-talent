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
MAINTAINER_ASSOCIATIONS={"OWNER","MEMBER"}
MEANINGFUL_EVENT_TYPES={"PushEvent","PullRequestEvent","PullRequestReviewEvent","CommitCommentEvent"}
NON_CORE_PREFIXES=("docs/","doc/","tests/","test/","examples/","example/",".github/","ci/","scripts/","website/")
_CACHE={};_CACHE_TTL_SECONDS=300

class GitHubSource:
    def __init__(self,token:str|None=None):
        headers={"Accept":"application/vnd.github+json","User-Agent":"ghost-talent/0.2.8"}
        if token:headers["Authorization"]=f"Bearer {token}"
        self.authenticated=bool(token);self.client=httpx.AsyncClient(headers=headers,timeout=20.0);self._semaphore=asyncio.Semaphore(6)
    async def close(self):await self.client.aclose()
    async def _get(self,url:str,**params):
        key=f"{url}?{sorted(params.items())}";cached=_CACHE.get(key);now=time.monotonic()
        if cached and now-cached[0]<_CACHE_TTL_SECONDS:return cached[1]
        last_error=None
        for attempt in range(3):
            try:
                async with self._semaphore:
                    r=await self.client.get(url,params=params or None);r.raise_for_status()
                body=r.text.strip()
                if not body:raise ValueError("empty response body")
                data=r.json()
                _CACHE[key]=(time.monotonic(),data);return data
            except httpx.HTTPStatusError:
                raise
            except (httpx.TransportError,ValueError) as e:
                last_error=e
                if attempt<2:
                    await asyncio.sleep(1.5*(attempt+1));continue
                detail=""
                if 'r' in locals():
                    detail=f" status={r.status_code} content_type={r.headers.get('content-type','')} body_prefix={r.text[:120]!r}"
                raise RuntimeError(f"GitHub transient/non-JSON response after 3 attempts:{detail} error={e}") from e
        raise RuntimeError(f"GitHub request failed: {last_error}")
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
            if self.authenticated:
                external=await self._external_validation(item)
                if index<quality_budget:quality=await self._contribution_quality(item)
            counts=self._event_counts(events)
            return {**item,"github_user_id":profile.get("id") if profile else None,"blog":profile.get("blog") if profile else None,"company":profile.get("company") if profile else None,"location":profile.get("location") if profile else None,"primary_repository":self._primary_repo(item),"name":profile.get("name") if profile else None,"profile_url":profile.get("html_url") if profile else item["profile_url"],"followers":profile.get("followers",0) if profile else 0,"noise":self._noise_signals(item,profile),"contribution_quality":quality,"external_validation":external,**counts}
        return await asyncio.gather(*(enrich(i,x) for i,x in enumerate(ranked)))
    async def _external_validation(self,item):
        login=item["login"]
        try:data=await self._get(f"{API}/search/issues",q=f"author:{login} type:pr is:merged",sort="updated",order="desc",per_page=20)
        except httpx.HTTPStatusError:return self._empty_external()
        now=datetime.now(timezone.utc);recent_cutoff=now-timedelta(days=180);rows=[]
        for pr in data.get("items",[])[:20]:
            repo_url=str(pr.get("repository_url") or "");repo=repo_url.split("/repos/")[-1] if "/repos/" in repo_url else "";owner=repo.split("/",1)[0].lower() if "/" in repo else "";recognized=repo.lower() in RECOGNIZED_UPSTREAM
            if owner==login.lower():continue
            closed_at=pr.get("closed_at");closed_ts=None
            if closed_at:
                try:closed_ts=datetime.fromisoformat(str(closed_at).replace("Z","+00:00"))
                except ValueError:closed_ts=None
            rows.append({"repository":repo,"number":pr.get("number"),"title":pr.get("title"),"url":pr.get("html_url"),"merged_or_closed_at":closed_at,"recent_180d":bool(closed_ts and closed_ts>=recent_cutoff),"recognized_upstream":recognized,"core_path_signal":False,"core_path_evidence":"not_inspected","maintainer_accepted":False,"maintainer_acceptance_evidence":"not_inspected","substantive":False,"verified_external_project":False})
        recognized_rows=[row for row in rows if row["recognized_upstream"]]
        open_rows=[row for row in rows if not row["recognized_upstream"] and row.get("recent_180d")]
        inspect=[];seen=set()
        for row in recognized_rows[:4]+open_rows[:4]+rows[:4]:
            key=(row["repository"],row["number"])
            if key in seen:continue
            seen.add(key);inspect.append(row)
            if len(inspect)>=8:break
        async def verify(row):
            try:files,reviews=await asyncio.gather(self._get(f"{API}/repos/{row['repository']}/pulls/{row['number']}/files",per_page=30),self._get(f"{API}/repos/{row['repository']}/pulls/{row['number']}/reviews",per_page=30))
            except httpx.HTTPStatusError:return row
            names=[str(f.get("filename") or "") for f in files];core_files=[name for name in names if self._is_core_path(name)];changed_lines=sum(int(f.get("additions",0))+int(f.get("deletions",0)) for f in files);non_docs=[n for n in names if not n.lower().startswith(NON_CORE_PREFIXES)];substantive=changed_lines>=20 and bool(non_docs)
            approvals=[]
            for review in reviews:
                reviewer=review.get("user") or {};association=str(review.get("author_association") or "").upper();state=str(review.get("state") or "").upper()
                if substantive and state=="APPROVED" and association in MAINTAINER_ASSOCIATIONS and str(reviewer.get("login") or "").lower()!=login.lower():approvals.append({"login":reviewer.get("login"),"author_association":association,"submitted_at":review.get("submitted_at")})
            core_signal=bool(core_files) and substantive;accepted=bool(approvals);verified_external=bool(substantive and (core_signal or accepted))
            return {**row,"substantive":substantive,"changed_lines":changed_lines,"core_path_signal":core_signal,"core_path_evidence":"changed_files" if substantive else "inspected_non_substantive","core_files":core_files[:6],"changed_files_sampled":len(names),"maintainer_accepted":accepted,"maintainer_acceptance_evidence":"approved_review" if approvals else "reviews_inspected_no_maintainer_approval","maintainer_approvals":approvals[:3],"verified_external_project":verified_external,"verification_basis":"substantive_core_or_owner_member_approval" if verified_external else "insufficient"}
        verified=await asyncio.gather(*(verify(row) for row in inspect)) if inspect else [];by_key={(r["repository"],r["number"]):r for r in verified};rows=[by_key.get((r["repository"],r["number"]),r) for r in rows]
        recognized=sum(1 for x in rows if x["recognized_upstream"] and x.get("substantive"));verified_external=sum(1 for x in rows if x.get("verified_external_project"));core=sum(1 for x in rows if x.get("core_path_signal"));accepted=sum(1 for x in rows if x.get("maintainer_accepted"));accepted_core=sum(1 for x in rows if x.get("core_path_signal") and x.get("maintainer_accepted"));substantive=sum(1 for x in rows if x.get("substantive"));recent=[x for x in rows if x.get("recent_180d")];recent_recognized=sum(1 for x in recent if x["recognized_upstream"] and x.get("substantive"));recent_verified=sum(1 for x in recent if x.get("verified_external_project"));recent_core=sum(1 for x in recent if x.get("core_path_signal"));recent_accepted=sum(1 for x in recent if x.get("maintainer_accepted"));recent_accepted_core=sum(1 for x in recent if x.get("core_path_signal") and x.get("maintainer_accepted"))
        return {"available":True,"external_merged_prs":len(rows),"substantive_external_prs":substantive,"verified_external_project_prs":verified_external,"recognized_upstream_prs":recognized,"core_path_prs":core,"core_path_prs_inspected":len(verified),"maintainer_accepted_prs":accepted,"maintainer_review_prs_inspected":len(verified),"maintainer_accepted_core_path_prs":accepted_core,"recent_window_days":180,"recent_external_merged_prs":len(recent),"recent_verified_external_project_prs":recent_verified,"recent_recognized_upstream_prs":recent_recognized,"recent_core_path_prs":recent_core,"recent_maintainer_accepted_prs":recent_accepted,"recent_maintainer_accepted_core_path_prs":recent_accepted_core,"inspection_policy":"bounded_mixed_external_v0.2.8","prs":rows[:8]}
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
        names=[str(f.get("filename",'')) for f in files];core=[n for n in names if self._is_core_path(n)];keywords=sorted({t for t in CORE_TERMS if t in str(top.get("title") or '').lower() or any(t in n.lower() for n in names)});changed=sum(int(f.get("additions",0))+int(f.get("deletions",0)) for f in files)
        return {"available":True,"repository":repo,"merged_pr_count":int(search.get("total_count",len(prs))),"sampled_pr_count":len(prs),"top_pr":{"number":top.get("number"),"title":top.get("title"),"url":top.get("html_url"),"merged_or_closed_at":top.get("closed_at"),"changed_files_sampled":len(files),"core_files":core[:8],"core_file_count":len(core),"keyword_hits":keywords,"additions":sum(int(f.get("additions",0)) for f in files),"deletions":sum(int(f.get("deletions",0)) for f in files),"substantive":changed>=20}}
    @staticmethod
    def _is_core_path(filename):
        path=filename.lower().lstrip("./")
        if path.startswith(NON_CORE_PREFIXES):return False
        base=path.rsplit("/",1)[-1]
        implementation_ext=base.endswith((".cu",".cuh",".c",".cc",".cpp",".py",".rs"))
        implementation_dir=any(seg in path.split("/") for seg in ("csrc","src","runtime","backend","kernels","kernel","compiler","ops"))
        technical_name=any(t in base for t in CORE_TERMS)
        return implementation_ext and (implementation_dir or technical_name)
    @staticmethod
    def _empty_quality(repository=None):return {"available":False,"repository":repository,"merged_pr_count":0,"sampled_pr_count":0,"top_pr":None}
    @staticmethod
    def _empty_external():return {"available":False,"external_merged_prs":0,"substantive_external_prs":0,"verified_external_project_prs":0,"recognized_upstream_prs":0,"core_path_prs":0,"core_path_prs_inspected":0,"maintainer_accepted_prs":0,"maintainer_review_prs_inspected":0,"maintainer_accepted_core_path_prs":0,"recent_window_days":180,"recent_external_merged_prs":0,"recent_verified_external_project_prs":0,"recent_recognized_upstream_prs":0,"recent_core_path_prs":0,"recent_maintainer_accepted_prs":0,"recent_maintainer_accepted_core_path_prs":0,"inspection_policy":"not_checked","prs":[]}
    @staticmethod
    def _event_counts(events):
        now=datetime.now(timezone.utc);d7=now-timedelta(days=7);d30=now-timedelta(days=30);d90=now-timedelta(days=90);c7=c30=c90=0;days=set();ts=[];meaningful=[]
        for e in events:
            if e.get("type") not in MEANINGFUL_EVENT_TYPES or not e.get("created_at"):continue
            t=datetime.fromisoformat(e["created_at"].replace("Z","+00:00"));meaningful.append(e);ts.append(t);c90+=t>=d90;c30+=t>=d30;c7+=t>=d7
            if t>=d30:days.add(t.date().isoformat())
        span=max((max(ts)-min(ts)).total_seconds()/86400,0) if len(ts)>=2 else 0;truncated=len(events)>=100
        return {"recent_events_7d":c7,"recent_events_30d":c30,"recent_events_90d":c90,"active_days_30d":len(days),"observed_event_span_days":round(span,2),"momentum_coverage":{"source":"github_public_events","meaningful_event_types":sorted(MEANINGFUL_EVENT_TYPES),"raw_events_sampled":len(events),"meaningful_events_sampled":len(meaningful),"sample_truncated":truncated,"history_sufficient":span>=14 and c90>c30}}
