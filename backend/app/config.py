from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
 supabase_url:str=""; supabase_anon_key:str=""; supabase_service_role_key:str=""; device_token:str="development-only-change-me"; cors_origins:str="http://localhost:5173"
 weather_lat:float=13.1439; weather_lon:float=79.9089; weather_location_name:str="Tiruvallur"; moisture_low_default:float=30; moisture_high_default:float=55; max_pump_runtime_seconds:int=900
 disease_model_path:str="models/plant_disease.tflite"; disease_labels_path:str="models/labels.txt"
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
 @property
 def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
