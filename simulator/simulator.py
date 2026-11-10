import asyncio,os,random
from datetime import datetime,timezone
import httpx
from dotenv import load_dotenv
load_dotenv()
BASE=os.getenv("API_BASE_URL","http://localhost:8000").rstrip("/"); USER_ID=os.getenv("SIMULATOR_USER_ID",""); TOKEN=os.getenv("DEVICE_TOKEN",""); INTERVAL=max(2,int(os.getenv("SIMULATOR_INTERVAL_SECONDS","5")))
async def run():
 if not TOKEN:raise SystemExit("Set DEVICE_TOKEN before starting the simulator.")
 soil,temp,humidity,tank,battery,water_used=48.0,29.0,65.0,92.0,78.0,0.0; active_user_id=USER_ID; headers={"X-Device-Token":TOKEN}
 async with httpx.AsyncClient(timeout=10) as client:
  print(f"Virtual ESP32 running for user {USER_ID}; API {BASE}")
  while True:
   try:
    response=await client.get(f"{BASE}/device/command",params=({"user_id":active_user_id} if active_user_id else None),headers=headers); response.raise_for_status(); state=response.json(); active_user_id=active_user_id or state.get("user_id"); pump=bool(state.get("pump_command",False))
    if pump and tank>1:soil=min(100,soil+random.uniform(.6,1.5)); tank=max(0,tank-random.uniform(.08,.22)); water_used+=random.uniform(.15,.3)
    else:soil=max(5,soil-random.uniform(.03,.16))
    temp=min(42,max(18,temp+random.uniform(-.15,.15))); humidity=min(95,max(25,humidity+random.uniform(-.5,.5))); battery=min(100,max(5,battery+random.uniform(-.03,.08))); voltage=max(0,18+random.uniform(-1.2,1.2))
    payload={"user_id":active_user_id,"soil_moisture":round(soil,1),"temperature":round(temp,1),"humidity":round(humidity,1),"water_tank":round(tank,1),"battery_level":round(battery,1),"solar_voltage":round(voltage,2),"pump_on":pump,"water_used_l":round(water_used,2)}
    posted=await client.post(f"{BASE}/readings",json=payload,headers=headers); posted.raise_for_status(); print(datetime.now(timezone.utc).isoformat(),payload)
   except Exception as exc:print("Simulator warning:",exc)
   await asyncio.sleep(INTERVAL)
if __name__=="__main__":asyncio.run(run())
