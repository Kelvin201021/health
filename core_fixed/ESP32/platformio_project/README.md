PlatformIO ESP32 Smart Spoon Example

Contents
- platformio.ini
- src/main.cpp

Purpose
- Minimal ready-to-flash Arduino (ESP32) project using PlatformIO.
- Posts a single sodium measurement to the server at boot using device token auth.
- Intentionally simple: uses `client.setInsecure()` (DO NOT use in production).

Before you build
1. Open `src/main.cpp` and set:
   - `WIFI_SSID` and `WIFI_PASS`
   - `SERVER_URL` (include https://)
   - `DEVICE_TOKEN` (device UUID from Django `Device.token`)

Build & flash (local machine)
- Using PlatformIO CLI:
  - Install PlatformIO: `pip install platformio` or use VSCode PlatformIO extension
  - From this directory (`ESP32/platformio_project`) run:

```bash
pio run -e esp32doit -t upload
```

- Or open the folder in VS Code and use PlatformIO "Upload" (select the `esp32doit` environment).

Testing notes
- Use an HTTPS endpoint reachable by the ESP32. For local dev, use `ngrok http 8000` and copy the ngrok `https://...` URL into `SERVER_URL`.
- Example JSON payload posted by device:
  {"name":"esp32-meal","sodium_mg":123}

Security
- Replace `client.setInsecure()` with `client.setCACert()` or certificate pinning for production.
- Store device tokens securely on the device and rotate if compromised.

Next steps I can do
- Add certificate pinning sample (Arduino) using the server CA or public key.
- Create PlatformIO project with `platformio.ini` variations for different ESP32 boards.
- Add OTA update support or retry/backoff logic.

Tell me which next step you want.