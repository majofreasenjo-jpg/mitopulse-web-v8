# MitoPulse — Prototipo móvil (Android + iOS) + Backend Enterprise (Local‑First)

Objetivo: que puedas **demostrar el flujo completo** en tus dispositivos:
- Samsung Note 9 (Android)
- iPhone 14 / iPhone 16 (iOS)
- Samsung Galaxy Watch SM‑R800

## Nota importante sobre tu reloj SM‑R800
El **SM‑R800 es Galaxy Watch (Tizen), NO Wear OS**.
- No puedes instalar una app Wear OS (Kotlin) en ese reloj.
- El prototipo funcional recomendado es:
  - Reloj → **Samsung Health** en tu Android (Note 9) sincroniza datos
  - App Android MitoPulse calcula local + envía **solo derivados**
- En iPhone, el reloj SM‑R800 no integra nativamente con HealthKit; el prototipo iOS usa **HealthKit del iPhone** o modo DEMO.

## Arquitectura
1) **Móvil** calcula localmente índice + vector + `dynamic_id=HMAC(secret_local, vector)`
2) **Backend** recibe solo derivados, aplica anti‑replay, auditoría, dashboard y `/verify`.

---

# 1) Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
- Docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

> Para probar desde móviles: PC y teléfono en la misma Wi‑Fi y usa `http://TU_IP:8000`.

---

# 2) Android (Note 9)
Proyecto: `mobile/android/MitoPulseAndroid`
- Abrir en Android Studio
- Editar `Config.kt` y cambiar `BACKEND_BASE_URL` (tu IP).

Botones:
- **Send DEMO Event**: envía un evento derivado (sin sensores) y lo verás en el dashboard.
- **Verify**: llama `/v1/verify`.

---

# 3) iOS (iPhone 14/16)
Proyecto: `mobile/ios/MitoPulseIOS`
Incluye fuentes SwiftUI en `Sources/` y una guía `README_IOS_SETUP.md` para crear el proyecto en Xcode.

---

# Quickstart (sin móviles)
```bash
python sdk_shared/demo_simulator.py
```
