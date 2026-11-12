# AI Smart Agri Guard 2.0

**Every Drop Counts, Every Crop Matters.**

Agri Guard is a smart-farming dashboard designed to display real readings from a physical ESP32 sensor unit. It uses a React frontend, FastAPI backend, Supabase database and Gemini-powered Plant Doctor.

## Features
- Supabase email/password authentication.
- Hardware telemetry: soil moisture, air temperature, humidity, water-tank level, battery estimate and solar voltage.
- Dashboard, history charts and alerts based only on readings stored by the backend.
- Gemini Plant Doctor for leaf-photo assessment.
- Three-day weather forecast and irrigation guidance.
- Mobile-friendly progressive web app.
- ESP32 firmware for capacitive soil moisture, DHT22, waterproof ultrasonic tank-level sensing and voltage monitoring.

**Hardware-only data policy:** the frontend does not generate sample readings, fake history or demo alerts. When no ESP32 data has arrived, the dashboard displays a waiting/no-data state. A disconnected or failed sensor must not be represented as a valid reading.

## Start here
1. Create a Supabase project and run `supabase/schema.sql` in its SQL Editor.
2. Configure the backend and frontend environment variables using the example files.
3. Deploy the backend and frontend, or run them locally using [docs/SETUP.md](docs/SETUP.md).
4. Assemble the low-voltage sensor unit using [the ESP32 wiring plan](docs/HARDWARE_WIRING_ESP32.md).
5. Configure and upload the sketch from [the firmware folder](firmware/esp32_agri_guard/README.md).

## Repository map
- `frontend/` — React dashboard, charts, authentication and PWA.
- `backend/` — FastAPI routes, Supabase data access, irrigation policy, weather and Gemini disease analysis.
- `firmware/esp32_agri_guard/` — ESP32 sensor firmware prototype.
- `supabase/schema.sql` — database tables, indexes, RLS policies and realtime publication.
- `docs/` — setup, API, architecture and hardware wiring.

## Plant Doctor
Configure `GEMINI_API_KEY` on the backend service. Never put it in the frontend or commit it to GitHub. AI assessments are not confirmed diagnoses; consult an agricultural expert for treatment decisions.

## Safety
The current firmware is sensor-only: it does not actuate a pump or relay. Do not connect a pump to an ESP32 GPIO. Before adding irrigation hardware, design and independently test a properly rated relay/contactor, fuse, isolated supply, enclosure, watchdog, dry-run protection, emergency stop and tank/overcurrent interlocks. Cloud software must never be the only pump safety layer. Keep the Supabase service-role key and device token server-side/private.
