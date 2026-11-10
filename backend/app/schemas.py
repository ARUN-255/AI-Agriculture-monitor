from typing import Literal
from pydantic import BaseModel,Field
class ReadingIn(BaseModel):
 user_id:str; soil_moisture:float=Field(ge=0,le=100); temperature:float=Field(ge=-20,le=80); humidity:float=Field(ge=0,le=100); water_tank:float=Field(ge=0,le=100); battery_level:float=Field(ge=0,le=100); solar_voltage:float=Field(ge=0,le=60); pump_on:bool=False; water_used_l:float=Field(default=0,ge=0)
class IrrigationUpdate(BaseModel):
 mode:Literal["auto","manual"]|None=None; pump_command:bool|None=None; moisture_low:float|None=Field(default=None,ge=0,le=95); moisture_high:float|None=Field(default=None,ge=5,le=100)
