## Requirements
Python 3.11+, Node.js 20+, a Supabase project. Plant Doctor additionally needs a compatible TensorFlow Lite model and labels.

## Supabase setup
1. Create a Supabase project.
2. Run supabase/schema.sql in the SQL Editor.
3. Enable Email authentication in Authentication > Providers.
4. Copy Project URL, anon/publishable key and service-role key from Project Settings > API.
5. Never expose the service-role key in the frontend.

## Environment
Copy the root .env.example to .env, backend/.env.example to backend/.env, frontend/.env.example to frontend/.env, and simulator/.env.example to simulator/.env. Use the same Supabase URL and anon key in backend and frontend. Generate a long random DEVICE_TOKEN and set it in backend and simulator. After signing up, copy your user UUID from Supabase Authentication > Users into SIMULATOR_USER_ID.

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
    export SIMULATOR_USER_ID=your-auth-user-uuid DEVICE_TOKEN=your-device-token
    python simulator.py

Frontend terminal:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173. API documentation is at http://localhost:8000/docs and health status at http://localhost:8000/health.

## Plant Doctor model
Put a TensorFlow Lite classifier at backend/models/plant_disease.tflite and matching labels at backend/models/labels.txt, one class per line. Confirm the model input dimensions, normalization and class order match the preprocessing in backend/app/disease.py. Model weights are not included. Without the model, the endpoint explicitly reports model_not_configured instead of inventing a diagnosis.

## Deployment
Deploy FastAPI and the simulator as separate Python services. Deploy the Vite frontend to a static host and set VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY and VITE_API_URL at build time. Add the deployed frontend origin to backend CORS. Use HTTPS and rotate secrets.
