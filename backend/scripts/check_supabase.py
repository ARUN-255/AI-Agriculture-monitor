"""Verify Supabase credentials, schema tables and private storage bucket.

Run from backend/: python scripts/check_supabase.py
The script never prints or uploads credentials.
"""
import asyncio
import sys
import httpx
from app.config import settings

TABLES = ("sensor_readings", "device_state", "disease_scans", "alerts")

async def main():
    missing = []
    for key, value in (
        ("SUPABASE_URL", settings.supabase_url),
        ("SUPABASE_ANON_KEY", settings.supabase_anon_key),
        ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
        ("DEVICE_TOKEN", settings.device_token if settings.device_token != "development-only-change-me" else ""),
    ):
        if not value:
            missing.append(key)
    if missing:
        print("Missing configuration: " + ", ".join(missing))
        print("Copy backend/.env.example to backend/.env and fill the values.")
        return 2

    base = settings.supabase_url.rstrip("/")
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    failures = []
    async with httpx.AsyncClient(timeout=15) as client:
        for table in TABLES:
            try:
                response = await client.get(
                    f"{base}/rest/v1/{table}",
                    params={"select": "*", "limit": "1"},
                    headers=headers,
                )
                response.raise_for_status()
                print(f"PASS  table {table}")
            except Exception as exc:
                failures.append(table)
                print(f"FAIL  table {table}: {type(exc).__name__}: {exc}")

        try:
            response = await client.get(
                f"{base}/storage/v1/bucket/leaf-images",
                headers=headers,
            )
            response.raise_for_status()
            print("PASS  private storage bucket leaf-images")
        except Exception as exc:
            failures.append("storage bucket leaf-images")
            print(f"FAIL  storage bucket leaf-images: {type(exc).__name__}: {exc}")

        try:
            response = await client.get(
                f"{base}/auth/v1/settings",
                headers={"apikey": settings.supabase_anon_key},
            )
            response.raise_for_status()
            print("PASS  Supabase Auth endpoint")
        except Exception as exc:
            failures.append("Supabase Auth")
            print(f"FAIL  Supabase Auth: {type(exc).__name__}: {exc}")

    if failures:
        print("\nSupabase is not ready. Check the SQL migration, project URL and keys.")
        return 1
    print("\nSupabase integration checks passed. You can start the backend and simulator.")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
