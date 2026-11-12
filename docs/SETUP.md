## Requirements
Python 3.11+, Node.js 20+, Arduino IDE 2.x, ESP32 board support, and a Supabase project.

## Supabase setup
1. Create a Supabase project.
2. Run `supabase/schema.sql` in the SQL Editor.
3. Enable Email authentication in Authentication > Providers.
4. Copy Project URL, anon/publishable key and service-role key from Project Settings > API.
5. Never expose the service-role key in the frontend.

## Environment
Copy the root `.env.example` to `.env`, `backend/.env.example` to `backend/.env`, and `frontend/.env.example` to `frontend/.env`. Use the same Supabase URL and anon key in backend and frontend. Generate a long random `DEVICE_TOKEN`; set it in the backend environment and in the private ESP32 `config.h`. Never commit `config.h` or expose device credentials.

## Verify Supabase before starting
From the backend folder, activate the virtual environment and run `python scripts/check_supabase.py`. It checks the Supabase URL and keys, database tables, the private `leaf-images` bucket and the Auth endpoint. It reports only pass/fail status and never prints secrets.

## Run locally
Backend terminal:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend terminal:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API documentation is at http://localhost:8000/docs and health status at http://localhost:8000/health.

## Connect the physical ESP32
1. Follow [the ESP32 wiring plan](HARDWARE_WIRING_ESP32.md) before powering any sensor.
2. Install ESP32 board support by Espressif Systems in Arduino IDE.
3. Install the DHT sensor library by Adafruit, Adafruit Unified Sensor, and ArduinoJson v7.
4. Copy `firmware/esp32_agri_guard/config.example.h` to `config.h` in the same folder.
5. Enter Wi-Fi credentials, the signed-in farm user's Supabase Auth UUID, the same device token configured on the backend, and the deployed API URL.
6. Calibrate soil dry/wet ADC values, tank empty/full distances, and battery voltage limits for the exact hardware.
7. Open `esp32_agri_guard.ino`, select ESP32 Dev Module and the correct port, upload, then open Serial Monitor at 115200 baud.
8. Confirm HTTP 2xx responses and check that real sensor readings appear in the dashboard.

The dashboard does not generate fallback readings. Until the ESP32 posts a valid reading, it displays **Waiting for hardware data**. Sensor read failures are skipped rather than replaced with estimates.

## Plant Doctor
Gemini is used when `GEMINI_API_KEY` is configured on the backend. Keep that key server-side only. The optional TensorFlow Lite fallback requires a compatible model at `backend/models/plant_disease.tflite` and matching labels. AI results are screening guidance, not a confirmed agricultural diagnosis.

## Deployment
Deploy FastAPI and the frontend as separate services. Set backend Supabase credentials, `DEVICE_TOKEN`, Gemini API key and CORS origins in the backend service environment. Set `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` and `VITE_API_URL` at frontend build time. Add the deployed frontend origin to backend CORS. Use HTTPS and rotate secrets if they have ever been exposed.

## Hardware safety
This firmware is sensor-only. It reads capacitive soil moisture, DHT22 temperature/humidity, ultrasonic tank level and voltage-divider inputs. It does not switch a pump or relay. Never connect a pump to an ESP32 GPIO. Voltage dividers, input protection, common-ground design and sensor logic levels must be checked against the exact module datasheets. Have a qualified person review the wiring before connecting a battery or solar panel.
