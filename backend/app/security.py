from fastapi import Header,HTTPException
import httpx
from .config import settings
async def current_user(authorization:str|None=Header(default=None)):
 if not authorization or not authorization.lower().startswith("bearer "):raise HTTPException(401,"Sign in to continue")
 token=authorization.split(" ",1)[1].strip()
 if not settings.supabase_url or not settings.supabase_anon_key:raise HTTPException(503,"Supabase authentication is not configured")
 try:
  async with httpx.AsyncClient(timeout=8) as client: response=await client.get(settings.supabase_url.rstrip("/")+"/auth/v1/user",headers={"apikey":settings.supabase_anon_key,"Authorization":f"Bearer {token}"})
  if response.status_code!=200:raise HTTPException(401,"Session is invalid or expired")
  return response.json()
 except httpx.HTTPError:raise HTTPException(503,"Authentication service unavailable")
async def device_auth(x_device_token:str|None=Header(default=None)):
 if not settings.device_token or settings.device_token=="development-only-change-me":raise HTTPException(503,"Set a strong DEVICE_TOKEN before enabling simulator writes")
 if x_device_token!=settings.device_token:raise HTTPException(401,"Invalid device token")
 return True
