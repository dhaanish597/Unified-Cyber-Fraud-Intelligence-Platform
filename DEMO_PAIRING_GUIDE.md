# Hackathon Demo Pairing

1. Start the API on the LAN interface (for example `uvicorn api.main:app --host 0.0.0.0 --port 18001`) and open the React dashboard.
2. Open **Developer Portal → Generate Pairing QR**. Copy the generated JSON into a QR encoder (the payload expires after five minutes).
3. Install `fusion-reference-bank/app/build/outputs/apk/debug/app-debug.apk` on a phone or emulator.
4. On first launch, paste the decoded JSON into **Paste pairing QR payload** and tap **PAIR DEVICE**. The APK stores the backend/WebSocket configuration and device JWT in encrypted storage.
5. Log in with a configured banking user. The device and session appear in the Developer Portal automatically; actions stream through the authenticated WebSocket.
6. Use **Start Synthetic Sessions** to run synthetic traffic. Synthetic activity uses the same backend pipeline but is marked separately from `LIVE_DEVICE` records.

The APK contains no judge-specific backend URL. Pairing is the runtime configuration step.
