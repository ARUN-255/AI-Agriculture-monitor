# Hardware connection guide

Agri Guard can be demonstrated without physical devices. The current random simulator can remain in place until the hardware is available.

## Future hardware layout

- ESP32 development board: reads sensors and sends readings over Wi-Fi.
- Soil-moisture sensor: measures soil moisture.
- Temperature and humidity sensor: measures air conditions.
- Water-level sensor: measures tank level.
- Battery-voltage sensor: measures the battery level/voltage.
- Relay module and a correctly rated pump driver: switches the pump.

The exact sensors and wiring can be chosen when the parts are purchased. Do not connect a pump directly to an ESP32 pin.

## Existing server connection

The backend already has the device routes needed for a first hardware version:

- Send readings: `POST /readings`
- Read the latest pump/mode command: `GET /device/command?user_id=YOUR_FARM_USER_ID`

Both device routes use the `x-device-token` HTTP header. Keep this token private and store it in the ESP32 firmware configuration; never put it in the public website.

Example reading body:

```json
{
  "user_id": "YOUR_SUPABASE_USER_ID",
  "soil_moisture": 42.5,
  "temperature": 29.1,
  "humidity": 68,
  "water_tank": 82,
  "battery_level": 78,
  "solar_voltage": 18.4,
  "pump_on": false,
  "water_used_l": 0
}
```

The ESP32 will need to send the JSON body to the backend URL using HTTPS and the device token header. It should poll the command route to learn whether the app wants the pump on or off.

## Important safety rules

This project is not a certified pump controller. Before operating a real pump:

1. Use a relay/contactor rated for the pump voltage and current.
2. Use a suitable fuse, protected power supply, insulated enclosure and correct wiring.
3. Add local safety cut-offs for an empty tank, dry running, over-current and maximum run time.
4. Make the ESP32 default to pump OFF after a restart or network failure.
5. Test first with an LED or low-voltage test load, not a live pump.
6. Have an experienced electrician or electronics mentor check the wiring.

Cloud commands must never be the only safety protection. Until hardware is connected and tested, all pump actions in the website are demonstrations only.
