# AI Smart Agri Guard 2.0

**Every Drop Counts, Every Crop Matters.**

A solar-powered smart farming platform built to monitor crop conditions, reduce unnecessary irrigation and help farmers inspect leaf health. This repository includes a React dashboard, FastAPI backend, Supabase PostgreSQL, a virtual ESP32 simulator, Open-Meteo weather integration and an optional TensorFlow Lite disease classifier.

## Included features

- Supabase email/password authentication and protected dashboard.
- Live dashboard: soil moisture, temperature, humidity, tank level, battery, solar voltage and pump status.
- Automatic/manual irrigation with moisture hysteresis, rain skip, empty-tank interlock and maximum pump runtime.
- Plant Doctor image upload, private Supabase Storage and optional TensorFlow Lite inference.
- Three-day weather forecast and irrigation suggestion (Open-Meteo requires no API key).
- Solar monitor, sensor history charts, alert history and alert resolution.
- Mobile-friendly PWA shell, service worker and install manifest.
- Python simulator that posts telemetry and polls device commands. One-farm mode discovers the signed-in farm automatically.

## Start here

1. Create a Supabase project and run `supabase/schema.sql` in its SQL Editor.
2. Copy the relevant `.env.example` files and enter your Supabase URL, anon key, service-role key and a strong shared device token. Never commit real secrets.
3. Start FastAPI, the simulator and the Vite frontend using [docs/SETUP.md](docs/SETUP.md).
4. Create an account in the app and keep the dashboard open; the simulator will discover this farm and begin sending readings.

## Repository map

- `frontend/` — React + Vite application, charts, authentication and PWA.
- `backend/` — FastAPI routes, Supabase data access, irrigation policy, weather and disease inference.
- `simulator/` — virtual ESP32 sensor and pump simulation.
- `supabase/schema.sql` — database tables, indexes, RLS policies and realtime publication.
- `docs/` — setup, API and architecture.

## Plant Doctor model requirement

A trained TensorFlow Lite model is not bundled. To enable real disease predictions, add a compatible model at `backend/models/plant_disease.tflite`, its matching `labels.txt`, and install the optional runtime from `backend/requirements-ml.txt`. Until then, the endpoint explicitly reports that the model is not configured; it never fabricates a diagnosis.

## Safety

The simulator is for development and demonstration, not a safety-certified irrigation controller. Before connecting a physical pump, add an appropriately rated relay/contactor, fuse, isolated supply, enclosure, hardware watchdog, dry-run protection and independent tank/overcurrent interlocks. Cloud software must never be the only pump safety layer. Keep the Supabase service-role key and device token on the server.
