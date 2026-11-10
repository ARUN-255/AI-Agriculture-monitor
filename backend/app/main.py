from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import store
from .schemas import ReadingIn, IrrigationUpdate
from .security import current_user, device_auth
from .irrigation import decide_irrigation
from .weather import get_weather
from .disease import DiseaseClassifier

app = FastAPI(title="AI Smart Agri Guard API", version="1.0.0", description="Smart agriculture telemetry, irrigation, weather and plant health API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
classifier = DiseaseClassifier(settings.disease_model_path, settings.disease_labels_path)

@app.get("/health")
async def health():
    return {"status":"ok", "database_configured":store.enabled, "authentication_configured":bool(settings.supabase_url and settings.supabase_anon_key), "device_configured":bool(settings.device_token and settings.device_token != "development-only-change-me"), "disease_model_ready":classifier.ready, "weather_provider":"Open-Meteo"}

async def user_id(user=Depends(current_user)):
    return user["id"]

async def ensure_state(uid):
    state = await store.latest("device_state", {"user_id":f"eq.{uid}", "select":"*", "limit":"1"})
    if state:
        return state
    return await store.insert("device_state", {"user_id":uid, "mode":"auto", "pump_command":False, "pump_started_at":None, "moisture_low":settings.moisture_low_default, "moisture_high":settings.moisture_high_default})

@app.get("/readings/latest")
async def latest_reading(uid=Depends(user_id)):
    if not store.enabled:
        raise HTTPException(503, "Database is not configured. Add Supabase credentials.")
    return await store.latest("sensor_readings", {"user_id":f"eq.{uid}", "select":"*", "order":"created_at.desc", "limit":"1"})

@app.get("/readings/history")
async def reading_history(limit:int=Query(100, ge=1, le=1000), uid=Depends(user_id)):
    rows = await store.request("GET", "sensor_readings", params={"user_id":f"eq.{uid}", "select":"*", "order":"created_at.desc", "limit":str(limit)})
    return list(reversed(rows or []))

@app.post("/readings")
async def create_reading(reading:ReadingIn, _=Depends(device_auth)):
    if not store.enabled:
        raise HTTPException(503, "Database is not configured")
    state = await ensure_state(reading.user_id)
    now = datetime.now(timezone.utc)
    started = state.get("pump_started_at")
    started_at = datetime.fromisoformat(started.replace("Z", "+00:00")) if started else None
    rain = False
    if state.get("mode") == "auto":
        try:
            rain = (await get_weather()).get("rain_expected", False)
        except Exception:
            rain = False
    pump, reason = decide_irrigation(
        mode=state.get("mode", "auto"), moisture=reading.soil_moisture,
        tank=reading.water_tank, rain_expected=rain,
        pump_on=bool(state.get("pump_command")), pump_started_at=started_at, now=now,
        low=float(state.get("moisture_low", 30)), high=float(state.get("moisture_high", 55))
    )
    next_started = started or now.isoformat() if pump else None
    await store.request("PATCH", "device_state", params={"user_id":f"eq.{reading.user_id}"},
        body={"pump_command":pump, "pump_started_at":next_started, "updated_at":now.isoformat()}, prefer="return=minimal")
    reading.pump_on = pump
    row = await store.insert("sensor_readings", reading.model_dump())
    if reason.startswith("Pump blocked") or reason.startswith("Pump stopped"):
        await store.insert("alerts", {"user_id":reading.user_id, "type":"safety", "message":reason})
    if reading.water_tank <= 15:
        await store.insert("alerts", {"user_id":reading.user_id, "type":"low_water", "message":"Water tank level is below 15%."})
    if reading.battery_level <= 15:
        await store.insert("alerts", {"user_id":reading.user_id, "type":"low_battery", "message":"Solar battery level is below 15%."})
    return row or {"accepted":True}

@app.get("/irrigation/state")
async def irrigation_state(uid=Depends(user_id)):
    if not store.enabled:
        raise HTTPException(503, "Database is not configured")
    return await ensure_state(uid)

@app.post("/irrigation/state")
async def update_irrigation(update:IrrigationUpdate, uid=Depends(user_id)):
    if not store.enabled:
        raise HTTPException(503, "Database is not configured")
    state = await ensure_state(uid)
    changes = update.model_dump(exclude_none=True)
    low = changes.get("moisture_low", state["moisture_low"])
    high = changes.get("moisture_high", state["moisture_high"])
    if low >= high:
        raise HTTPException(422, "Low moisture threshold must be below high threshold")
    if changes.get("mode") == "auto":
        changes["pump_command"] = False
        changes["pump_started_at"] = None
    elif changes.get("pump_command") is True and not state.get("pump_command"):
        changes["pump_started_at"] = datetime.now(timezone.utc).isoformat()
    elif changes.get("pump_command") is False:
        changes["pump_started_at"] = None
    changes["updated_at"] = datetime.now(timezone.utc).isoformat()
    rows = await store.request("PATCH", "device_state", params={"user_id":f"eq.{uid}", "select":"*"}, body=changes, prefer="return=representation")
    return rows[0] if rows else await ensure_state(uid)

@app.get("/device/command")
async def device_command(user_id:str|None=None, _=Depends(device_auth)):
    if not store.enabled:
        raise HTTPException(503, "Database is not configured")
    if user_id:
        return await ensure_state(user_id)
    state = await store.latest("device_state", {"select":"*", "order":"updated_at.asc", "limit":"1"})
    if not state:
        raise HTTPException(404, "No farm is registered yet. Sign in to the dashboard once to initialize device state.")
    return state

@app.get("/weather")
async def weather(lat:float|None=None, lon:float|None=None, _=Depends(current_user)):
    try:
        return await get_weather(lat, lon)
    except Exception:
        raise HTTPException(502, "Weather service unavailable")

@app.get("/alerts")
async def alerts(limit:int=Query(50, ge=1, le=200), uid=Depends(user_id)):
    return await store.request("GET", "alerts", params={"user_id":f"eq.{uid}", "select":"*", "order":"created_at.desc", "limit":str(limit)}) or []

@app.patch("/alerts/{alert_id}")
async def resolve_alert(alert_id:str, uid=Depends(user_id)):
    rows = await store.request("PATCH", "alerts", params={"id":f"eq.{alert_id}", "user_id":f"eq.{uid}", "select":"*"}, body={"resolved":True}, prefer="return=representation")
    if not rows:
        raise HTTPException(404, "Alert not found")
    return rows[0]

@app.post("/disease/predict")
async def predict_disease(file:UploadFile=File(...), uid=Depends(user_id)):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Upload a JPG, PNG or WEBP leaf image")
    raw = await file.read()
    if len(raw) > 8*1024*1024:
        raise HTTPException(413, "Image must be smaller than 8 MB")
    try:
        result = classifier.predict(raw)
    except Exception as exc:
        raise HTTPException(422, f"Could not process image: {exc}")
    if result["status"] == "ok" and store.enabled:
        suffix = {"image/jpeg":"jpg", "image/png":"png", "image/webp":"webp"}[file.content_type]
        object_path = f"{uid}/{uuid4()}.{suffix}"
        try:
            image_path = await store.upload("leaf-images", object_path, raw, file.content_type)
            await store.insert("disease_scans", {"user_id":uid, "image_url":image_path, "disease":result["disease"], "confidence":result["confidence"], "treatment":result["treatment"]})
        except Exception:
            await store.insert("disease_scans", {"user_id":uid, "disease":result["disease"], "confidence":result["confidence"], "treatment":result["treatment"]})
    return result

@app.get("/disease/history")
async def disease_history(uid=Depends(user_id)):
    return await store.request("GET", "disease_scans", params={"user_id":f"eq.{uid}", "select":"*", "order":"created_at.desc", "limit":"50"}) or []
