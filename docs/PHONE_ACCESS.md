# Open Agri Guard on your phone

The dashboard is responsive and can be opened from a phone on the same Wi-Fi network as the computer running Docker.

## 1. Find your computer's local IPv4 address

On Windows, open PowerShell and run:

```powershell
ipconfig
```

Under the Wi-Fi adapter that is connected to your network, note the **IPv4 Address**, for example `192.168.1.25`. Do not use the Default Gateway.

## 2. Update the root `.env`

Use that address in both settings below (replace the example IP):

```env
VITE_API_URL=http://192.168.1.25:8000
CORS_ORIGINS=http://localhost:5173,http://192.168.1.25:5173
```

Keep the existing Supabase values and other environment settings. Do not put the Supabase secret/service-role key in any `VITE_*` variable.

## 3. Rebuild the frontend and restart

From the repository root:

```powershell
docker compose down
docker compose up --build -d
```

The Vite frontend variables are embedded at build time, so the rebuild is required after changing `VITE_API_URL`.

## 4. Open it on your phone

1. Connect your phone to the same Wi-Fi network as your computer.
2. Open the phone browser and visit `http://192.168.1.25:5173` (use your actual IPv4 address).
3. Sign in with the same Agri Guard account.
4. Use the browser menu's **Add to Home screen** or **Install app** option if available.

## 5. If it does not load

- Allow Docker Desktop / the app through Windows Defender Firewall on **Private networks**.
- Confirm Docker is running and both ports `5173` and `8000` are available.
- Check `http://192.168.1.25:8000/health` from the phone browser.
- Make sure the phone and PC are on the same Wi-Fi; guest Wi-Fi or client isolation can block device-to-device access.
- If the computer's IPv4 address changes, update both environment values and rebuild.

This is local-network access, not public hosting. It works while the PC and Docker containers are running.