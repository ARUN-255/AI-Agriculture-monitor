from app.irrigation import decide_irrigation
def test_dry_soil_starts_pump():assert decide_irrigation(mode="auto",moisture=20,tank=90,rain_expected=False,pump_on=False,low=30,high=55)[0] is True
def test_high_moisture_stops_pump():assert decide_irrigation(mode="auto",moisture=60,tank=90,rain_expected=False,pump_on=True)[0] is False
def test_rain_skips_irrigation():assert decide_irrigation(mode="auto",moisture=10,tank=90,rain_expected=True,pump_on=False)[0] is False
def test_empty_tank_blocks_manual():
 on,reason=decide_irrigation(mode="manual",moisture=10,tank=0,rain_expected=False,pump_on=True); assert on is False and "empty" in reason
def test_manual_mode_obeys_command():assert decide_irrigation(mode="manual",moisture=10,tank=90,rain_expected=False,pump_on=True)[0] is True
