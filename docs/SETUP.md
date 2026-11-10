## Requirements
Python 3.11+, Node.js 20+, a Supabase project. Plant Doctor additionally needs a compatible TensorFlow Lite model and labels.

## Supabase setup
1. Create a Supabase project.
2. Run supabase/schema.sql in the SQL Editor.
3. Enable Email authentication in Authentication > Providers.
4. Copy Project URL, anon/publishable key and service-role key from Project Settings > API.
5. Never expose the service-role key in the frontend.

## Environment
Copy the root .env.example to .env, backend/.env.example to backend/.env, frontend/.env.example to frontend/.env, and simulator/.env.example to simulator/.env. Use the same Supabase URL and anon key in backend and frontend. Generate a long random DEVICE_TOKEN and set it in backend and simulator. The single-farm simulator discovers the signed-in farm automatically after you open the dashboard once. SIMULATOR_USER_ID is optional and is only needed when operating multiple farms.

## Verify Supabase before starting

From the backend folder, activate the virtual environment and run `python scripts/check_supabase.py`. It checks the Supabase URL and keys, all four database tables, the private `leaf-images` bucket and the Auth endpoint. It reports only pass/fail status and never prints secrets. Resolve any failures before starting the simulator.

## Run locally
Backend terminal:

    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Simulator terminal:

    cd simulator
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export DEVICE_TOKEN=your-device-token
    python simulator.py

    # SIMULATOR_USER_ID is optional for a single farm; the simulator discovers it after you sign in to the dashboard once.

Frontend terminal:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173. API documentation is at http://localhost:8000/docs and health status at http://localhost:8000/health.

## Plant Doctor model
Install the optional inference runtime with pip install -r requirements-ml.txt. Put a TensorFlow Lite classifier at backend/models/plant_disease.tflite and matching labels at backend/models/labels.txt, one class per line. Confirm the model input dimensions, normalization and class order match the preprocessing in backend/app/disease.py. Model weights are not included. Without the model, the endpoint explicitly reports model_not_configured instead of inventing a diagnosis.

## Render cloud demo (keep the laptop simulator feeding every phone)

The Render dashboard and the Docker simulator on your laptop must use the same hosted backend and Supabase database. The Docker simulator should post to `https://agri-guard-api.onrender.com`, not to a laptop-only address such as `localhost` or `http://backend:8000`.

1. In Render, open **agri-guard-api → Environment** and copy the value of `DEVICE_TOKEN` (do not send it in chat).
2. In the root `.env` file on your laptop, set `API_BASE_URL=https://agri-guard-api.onrender.com` and set `DEVICE_TOKEN` to that exact Render value.
3. Confirm the Supabase URL and service-role key in the Render backend belong to the same Supabase project used by the dashboard.
4. Restart only the simulator so it picks up the new values: `docker compose up -d --build simulator`.
5. Open the hosted dashboard on your phone and sign in with the same account used to initialize the farm. Readings should begin appearing within about 10–20 seconds.

The simulator needs to remain running on the laptop for continuous demo readings. Render's free API can sleep when idle; the simulator's regular requests normally wake it. If the phone still shows empty values, check the Render API logs for simulator requests and confirm they return HTTP 200 rather than 401 (device token mismatch) or 404 (no farm initialized).

Deploy FastAPI and the simulator as separate Python services for a fully cloud-only setup. Deploy the Vite frontend to a static host and set VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY and VITE_API_URL at build time. Add the deployed frontend origin to backend CORS. Use HTTPS and rotate secrets.
