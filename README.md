# AI Smart Agri Guard 2.0

Solar-powered smart agriculture monitoring and irrigation platform combining a React dashboard, FastAPI backend, Supabase, a Python device simulator, weather intelligence, and plant-disease inference.

> Hardware-free development mode is supported: the Python simulator generates sensor readings and accepts irrigation commands. Connect an ESP32 later by implementing the documented device transport.

## Quick start

See [docs/SETUP.md](docs/SETUP.md) for local setup, environment variables, Supabase SQL, and deployment. Copy `.env.example` files and add your own credentials; never commit secrets.

## Architecture

- `frontend/` — React + Vite dashboard, charts, auth, controls, plant doctor.
- `backend/` — FastAPI REST API, irrigation rules, weather integration, disease inference adapter.
- `simulator/` — Python sensor/device simulator that posts telemetry and polls commands.
- `supabase/schema.sql` — database schema, indexes, RLS policies and seed settings.
- `docs/` — setup, API and hardware integration notes.

## Safety

The simulator is not a safety-certified irrigation controller. Before attaching a real pump, add independent electrical protection, a hardware watchdog, fail-safe relay wiring, and local tank/overcurrent interlocks. Do not expose the backend or Supabase service-role key in the browser.
