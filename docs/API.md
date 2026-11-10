Interactive API documentation is served at /docs.

All user routes require Authorization: Bearer <Supabase access token>. Device routes require X-Device-Token.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | API and configuration status |
| GET | /readings/latest | Latest authenticated user's reading |
| GET | /readings/history?limit=100 | Sensor history |
| POST | /readings | Simulator telemetry |
| GET | /irrigation/state | Irrigation mode and thresholds |
| POST | /irrigation/state | Update mode, pump command or thresholds |
| GET | /device/command | Simulator discovers the first farm; optionally pass user_id for multi-farm setups |
| GET | /weather | Open-Meteo weather and irrigation advice |
| POST | /disease/predict | Multipart upload field named file |
| GET | /disease/history | Disease scan history |
| GET | /alerts | Alerts |
| PATCH | /alerts/{id} | Resolve alert |

Reading fields: user_id, soil_moisture, temperature, humidity, water_tank, battery_level, solar_voltage, pump_on and water_used_l. Irrigation updates accept mode (auto/manual), pump_command, moisture_low and moisture_high. Low must be lower than high.
