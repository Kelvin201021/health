ESP32 / Smart Spoon Integration

Overview
- Endpoint: POST /dashboard/api/sodium/add-meal/
- Auth: Authorization: Token <DEVICE_TOKEN> or X-Device-Token: <DEVICE_TOKEN>
- Content-Type: application/json
- Payload: {"name":"spoon-meal","sodium_mg":123,"recorded_at":"ISO8601 optional"}

Quick steps
1. Create or reuse a `Device` token using the management command or Django shell (see project `tools/create_device_and_post.py` or `manage.py shell`).
2. Flash ESP32 with the sketch in `arduino_spoon.ino` and set `SERVER` and `DEVICE_TOKEN`.
3. Use HTTPS; prefer certificate validation/pinning (replace the CA PEM placeholder).

Files
- `arduino_spoon.ino` — Arduino-style example using `WiFiClientSecure` + `HTTPClient`.
- `esp_idf_example/main.c` — Minimal ESP-IDF example with `esp_http_client` and CA cert usage.

Security notes
- Do NOT use `client.setInsecure()` in production. Use `client.setCACert()` with the CA or perform certificate pinning.
- Rotate device tokens if a device is compromised.

Testing
- Use `ngrok` or host the server with HTTPS accessible by the ESP32 during development.
- Example curl (workstation):
  curl -i -X POST https://your-host/dashboard/api/sodium/add-meal/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Token <DEVICE_TOKEN>" \
    -d '{"name":"spoon-test","sodium_mg":200}'

Support
- For integration help, tell me which build system you prefer (Arduino core or ESP-IDF) and whether you want certificate pinning examples.