import httpx
from .config import settings

class SupabaseStore:
    def __init__(self):
        self.enabled=bool(settings.supabase_url and settings.supabase_service_role_key)
        self.base=settings.supabase_url.rstrip("/")+"/rest/v1" if self.enabled else ""
        self.storage=settings.supabase_url.rstrip("/")+"/storage/v1" if self.enabled else ""
        self.headers={"apikey":settings.supabase_service_role_key,"Authorization":f"Bearer {settings.supabase_service_role_key}","Content-Type":"application/json"}
    async def request(self,method,table,*,params=None,body=None,prefer=None):
        if not self.enabled:return None
        headers=dict(self.headers)
        if prefer:headers["Prefer"]=prefer
        async with httpx.AsyncClient(timeout=12) as client:
            response=await client.request(method,f"{self.base}/{table}",params=params,json=body,headers=headers)
            response.raise_for_status()
            return response.json() if response.content else []
    async def insert(self,table,row):
        result=await self.request("POST",table,body=row,prefer="return=representation")
        return result[0] if result else None
    async def latest(self,table,params):
        result=await self.request("GET",table,params=params)
        return result[0] if result else None
    async def upload(self,bucket,path,raw,content_type):
        if not self.enabled:return None
        headers={"apikey":settings.supabase_service_role_key,"Authorization":f"Bearer {settings.supabase_service_role_key}","Content-Type":content_type,"x-upsert":"false"}
        async with httpx.AsyncClient(timeout=20) as client:
            response=await client.post(f"{self.storage}/object/{bucket}/{path}",content=raw,headers=headers)
            response.raise_for_status()
            return f"{bucket}/{path}"

store=SupabaseStore()
