import httpx
from .config import settings
WMO={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",51:"Drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",80:"Rain showers",95:"Thunderstorm"}
async def get_weather(lat=None,lon=None):
 lat=settings.weather_lat if lat is None else lat; lon=settings.weather_lon if lon is None else lon
 params={"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,precipitation,weather_code","daily":"precipitation_probability_max,precipitation_sum,weather_code","forecast_days":3,"timezone":"auto"}
 async with httpx.AsyncClient(timeout=12) as client:
  response=await client.get("https://api.open-meteo.com/v1/forecast",params=params); response.raise_for_status(); data=response.json()
 cur=data.get("current",{}); daily=data.get("daily",{}); rain=any(float(x or 0)>=40 for x in daily.get("precipitation_probability_max",[])[:2])
 return {"location":settings.weather_location_name,"temperature":cur.get("temperature_2m"),"humidity":cur.get("relative_humidity_2m"),"condition":WMO.get(cur.get("weather_code"),"Unknown"),"precipitation_mm":cur.get("precipitation"),"dates":daily.get("time",[]),"rain_probability":daily.get("precipitation_probability_max",[]),"rain_expected":rain,"irrigation_suggestion":"Rain is likely soon; check soil before irrigating." if rain else "No significant rain is forecast; irrigate only if soil moisture is low."}
