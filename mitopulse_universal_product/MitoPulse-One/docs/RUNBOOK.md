# MitoPulse One — Runbook

## Demo Flow
1) Start backend (`/dashboard`).
2) Start PWA.
3) In PWA: set Backend URL, press **START LIVE MODE**.
4) Open Dashboard and show events + audit logs updating.
5) Trigger higher risk by lowering HRV/SpO2/sleep and raising HR/load.

## Security (pilot)
- API key header: `X-API-Key: demo-key`
- Anti-replay: `request_id` uniqueness
- Integrity: HMAC-SHA256(api_key, user|device|ts|dynamic_id)

