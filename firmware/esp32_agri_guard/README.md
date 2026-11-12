# Agri Guard ESP32 sensor firmware

This is the first physical-sensor prototype for the existing Agri Guard API. It reads sensors and sends telemetry; it does **not** operate a pump or relay.

## Arduino IDE libraries

Install:
- ESP32 board support by Espressif Systems
- DHT sensor library by Adafruit
- Adafruit Unified Sensor
- ArduinoJson (v7)

Select an ESP32 Dev Module board and the correct serial port.

## Configure

1. Copy `config.example.h` to `config.h` in this folder.
2. Fill in Wi-Fi name/password, the Supabase auth user UUID for the farm, and the same device token configured on Render as `DEVICE_TOKEN`.
3. Set soil dry/wet ADC calibration values.
4. Set tank empty/full distance values.
5. Set battery empty/full voltage values for the exact battery chemistry and pack. The values in the example are only a 12 V lead-acid illustration.
6. Keep `config.h` private. Do not commit it to GitHub or paste secrets into chat.

## Upload and test

1. Connect only the low-voltage sensors listed in the wiring guide.
2. Upload the sketch.
3. Open Serial Monitor at 115200 baud.
4. Check sensor readings and HTTPS response codes.
5. Confirm new readings appear in Agri Guard.

The Render free service may sleep when idle, so the first request can take a while. The firmware retries on the next interval.

## Important prototype limitations

- TLS certificate validation is disabled in this prototype to simplify first bench testing. Before real deployment, replace `tls.setInsecure()` with `tls.setCACert()` and the verified root CA certificate for the API host.
- The ultrasonic sensor is a tank-level approximation; calibrate its distance range on the actual tank.
- Battery percentage is a rough linear estimate between configured voltage limits, not a laboratory state-of-charge measurement.
- Solar and battery voltage inputs use external resistor dividers. Never connect a panel or battery directly to an ESP32 ADC pin.
- The firmware receives cloud pump commands for visibility only. It never switches a relay or pump.
- Sensor failures skip the telemetry upload rather than sending invented values.
