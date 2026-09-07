from __future__ import annotations

import re
import unicodedata

import httpx

API = "https://api.openalex.org"

def _norm(value: str | None) -> str:
    if not value:return ""
    value=unicodedata.normalize("NFKD",value);value="".join(ch for ch in value if not unicodedata.combining(ch));return re.sub(r"[^a-z0-9]","",value.lower())

class OpenAlexSource:
    def __init__(self)->None:self.client=httpx.AsyncClient(timeout=20.0)
    async def close(self)->None:await self.client.aclose()
    async def works(self,query:str,per_page:int=25)->list[dict]:
        response=await self.client.get(f"{API}/works",params={"search":query,"per-page":per_page});response.raise_for_status();return response.json().get("results",[])
    @staticmethod
    def match_author(name:str|None,works:list[dict])->list[dict]:
        needle=_norm(name)
        if len(needle)<4:return []
        matches=[]
        for work in works:
            for authorship in work.get("authorships",[]):
                author=authorship.get("author") or {}
                if _norm(author.get("display_name"))!=needle:continue
                matches.append({"title":work.get("display_name"),"url":work.get("doi") or work.get("id"),"publication_date":work.get("publication_date"),"cited_by_count":work.get("cited_by_count",0),"author":author.get("display_name"),"openalex_author_id":author.get("id"),"orcid":author.get("orcid"),"identity_status":"uncertain_name_match","identity_confidence":0.35})
                break
        return matches
