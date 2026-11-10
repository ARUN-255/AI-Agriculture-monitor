from datetime import datetime,timezone
from .config import settings
def decide_irrigation(*,mode,moisture,tank,rain_expected,pump_on,pump_started_at=None,now=None,low=30,high=55):
 now=now or datetime.now(timezone.utc)
 if tank<=1:return False,"Pump blocked: water tank is empty"
 if pump_on and pump_started_at and (now-pump_started_at).total_seconds()>=settings.max_pump_runtime_seconds:return False,"Pump stopped: maximum runtime reached"
 if mode=="manual":return pump_on,"Manual mode"
 if rain_expected:return False,"Irrigation skipped: rain is forecast"
 if moisture<=low:return True,"Soil is dry: irrigation started"
 if moisture>=high:return False,"Soil moisture target reached"
 return pump_on,"Moisture is within the configured range"
