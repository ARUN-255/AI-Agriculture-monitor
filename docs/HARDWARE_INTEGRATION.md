# Hardware connection guide

Agri Guard supports a virtual sensor simulator today and now includes a first ESP32 firmware prototype for future physical sensors.

## Hardware prototype

- ESP32 DevKit V1
- Capacitive soil-moisture sensor
- DHT22 temperature/humidity sensor
- JSN-SR04T waterproof ultrasonic tank-level sensor
- Two protected analog voltage-divider channels (solar and battery)

See [ESP32 wiring plan](HARDWARE_WIRING_ESP32.md) and [firmware setup](../firmware/esp32_agri_guard/README.md).

## Existing server connection

The backend already has the device routes needed for the first hardware version:

- Send readings: `POST /readings`
- Read the latest pump/mode command: `GET /device/command?user_id=YOUR_FARM_USER_ID`

Both device routes use the `X-Device-Token` HTTP header. The ESP32 firmware sends this header and posts the same reading fields used by the simulator.

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

## Current firmware behavior

The firmware reads soil moisture, air temperature/humidity, tank level, solar voltage and battery voltage. It posts readings to the deployed API and polls for irrigation commands. It logs received pump commands to Serial Monitor only; it does not drive a relay or pump.

The soil sensor and tank sensor require calibration. Battery percentage is a rough voltage-based estimate and must be configured for the exact battery chemistry and pack. Voltage divider inputs must be protected and must never exceed the ESP32 ADC input range.

## Security and setup

1. Copy `firmware/esp32_agri_guard/config.example.h` to `config.h`.
2. Enter Wi-Fi credentials, the farm owner's Supabase auth user UUID, and the same `DEVICE_TOKEN` configured in Render.
3. Keep `config.h` private; it is gitignored. Never commit credentials or paste them into chat.
4. The prototype currently uses `tls.setInsecure()` to simplify bench testing. Before production, replace it with certificate validation using the verified root CA for the API host.
5. The Render free service may sleep when idle, so the first request can take longer.

## Important safety rules

This project is not a certified pump controller. Before operating a real pump:

1. Use a relay/contactor or motor driver rated for the pump voltage and current.
2. Use a suitable fuse, protected power supply, insulated enclosure and correct wiring.
3. Add local safety cut-offs for an empty tank, dry running, over-current and maximum run time.
4. Make the ESP32 default to pump OFF after a restart or network failure.
5. Test first with an LED or low-voltage test load, not a live pump.
6. Have an experienced electrician or electronics mentor check the wiring.

Cloud commands must never be the only safety protection. Until the pump hardware is separately designed and tested, all pump actions in the website remain demonstrations only.
