# MitoPulse Universal Prototype v1 (PC + Mobile + Tablet + Wearables)

Este paquete es un **monorepo** listo para que lo ejecutes localmente y luego lo abras en:
- **PC/Notebook/Tablet/Móvil**: vía **Web App (PWA)**.
- **Android (teléfono + Wear OS)**: scaffold en Kotlin (Android Studio).
- **iOS (iPhone + watchOS)**: scaffold en SwiftUI (Xcode).
- **Samsung Galaxy Watch SM-R800 (Tizen)**: no es Wear OS. La ruta “universal” es **Samsung Health → Teléfono Android → MitoPulse** (bridge por export/Health Connect). Se deja documentación y stubs.

> Nota: para que sea portable “a todos los modelos”, el sistema usa **Tiers** según señales disponibles:
Tier1 (teléfono básico), Tier2 (wearable con HRV), Tier3 (sensores avanzados).

---

## 0) Estructura

```
mitopulse/
  backend/            # FastAPI + SQLite + Dashboard
  sdk_shared/         # Engine de referencia (Python) + simulador
  webapp/             # PWA (Vite + React) para PC/Tablet/Móvil
  mobile/
    android/          # Android app + módulo Wear OS (Kotlin)
    ios/              # iOS app + watchOS extension (SwiftUI)
  docs/
  scripts/
```

---

## 1) Ejecutar Backend (PC/Notebook)

### Requisitos
- Python 3.10+

### Pasos
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Luego abre:
- API Docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

---

## 2) Probar flujo completo sin móvil (simulador)
```bash
cd sdk_shared
python -m venv .venv
# activar venv igual que arriba
pip install -r requirements.txt
python demo_simulator.py
```
Esto:
1) Calcula index/tier/risk/coercion localmente
2) Envía `/v1/identity-events`
3) Ejecuta `/v1/verify`
4) Prueba anti-replay

---

## 3) Web App (PWA) — PC/Notebook/Tablet/Móvil
La webapp funciona como “app universal” (instalable como PWA en Android/iOS/desktop).

### Requisitos
- Node 18+

### Pasos
```bash
cd webapp
npm install
npm run dev
```

Abre:
- http://localhost:5173

Configura el backend URL en la UI (por defecto http://127.0.0.1:8000).

**Para usar desde el teléfono**:
- Asegúrate de que PC y teléfono estén en la misma red Wi‑Fi
- Corre backend con host 0.0.0.0:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- En el teléfono entra a: `http://IP_DE_TU_PC:5173`

---

## 4) Android (Note 9) + Wear OS (Galaxy Watch Wear OS)
Ruta recomendada: Android Studio (Electric Eel+).

### Abrir
- `mobile/android/` como proyecto en Android Studio.
- Ajusta `BASE_URL` en `Config.kt` con la IP del backend.

### Qué hace
- Calcula localmente index/tier/risk
- Genera dynamic_id por HMAC-SHA256 (secret en Keystore)
- Envía a backend y verifica
- Wear OS module envía lecturas al teléfono (stub + ejemplo)

---

## 5) iOS (iPhone 14/16) + watchOS
Ruta recomendada: Xcode 15+.

### Abrir
- `mobile/ios/MitoPulseIOS.xcodeproj`
- Ajusta `BASE_URL` en `Config.swift`

### Qué hace
- SwiftUI app con botones “Send Demo Event” y “Verify”
- Engine local + HMAC (secret en Keychain)
- watchOS extension: stub para mandar señales al iPhone (WatchConnectivity)

---

## 6) Samsung Galaxy Watch SM‑R800 (Tizen)
No corre Wear OS ni watchOS. La forma de demo universal:
- Reloj → **Samsung Health** → teléfono Android
- Tu app Android ingesta del repositorio de salud (Health Connect / export / SDK).

Se dejan notas en `docs/tizen_bridge.md`.

---

## 7) Endpoints principales
- `POST /v1/identity-events`
- `POST /v1/verify`
- `GET /dashboard`

---

## 8) Licencia
Prototipo interno. Puedes cambiarlo como quieras.
