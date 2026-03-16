# MitoPulse v3 — GLOBAL DEMO PACKAGE (Off‑store Pilot)

Este paquete está pensado para que puedas **demostrar MitoPulse desde cualquier lugar del mundo** sin publicar aún en tiendas.
Incluye:

- **Backend Enterprise (FastAPI)** con Dashboard + Audit Logs + Baselines/Stability/Human‑confidence (v2.5).
- **Pilot PWA** (PC/Notebook/Tablet/Mobile) instalable como app (Add to Home Screen / Install).
- **SDK Shared + Simulator** para poblar datos y probar escenarios.
- **Infra GLOBAL**: scripts y configuración para exponer Backend + PWA por internet con **Cloudflare Tunnel** (HTTPS).
- **Mobile scaffolds (Android/iOS)** para compilar APK/IPA off‑store (para socios).

> Nota de compatibilidad de relojes:
> - Para **Samsung SM‑R800 (Tizen)**: no es Wear OS. En general, lo más universal es usar la **PWA en el teléfono** como “cliente” y el reloj como fuente vía Samsung Health (requerirá integración adicional).
> - Para relojes **Wear OS** (Galaxy Watch modernos): el scaffold Android se puede extender con un módulo Wear OS.

---

## 0) Requisitos

### Backend / PWA (demo global)
- Python 3.10+
- Node 18+
- (Opcional) Docker Desktop (para correr todo con docker-compose)
- Cloudflare Tunnel (cloudflared) *(para demo global HTTPS)*

### Mobile off‑store
- Android Studio (para Samsung Note 9 y Android en general)
- Xcode (para iPhone)

---

## 1) Ejecutar LOCAL (rápido)

### 1.1 Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend:
- API + Docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

### 1.2 PWA
```bash
cd webapp
npm install
npm run dev
```

PWA: http://127.0.0.1:5176 (o el puerto que muestre Vite)

---

## 2) Probar que todo funciona (simulador + endpoints v2)

En otra terminal:

```bash
python sdk_shared/demo_simulator_v25.py --backend http://127.0.0.1:8000
```

Luego abre el dashboard y verás eventos + audit logs.

Estado v2 (ejemplo):
```text
GET /v2/identity/state?user_id=manuel&device_id=sim-device-01
```

---

## 3) Modo GLOBAL (salir de localhost con HTTPS)

Aquí hay dos caminos:

### Camino A (recomendado): Cloudflare Tunnel (sin abrir puertos)
Usa el documento `DEPLOYMENT.md` y la carpeta `infra/`.

Resumen:
1) Levanta Backend y PWA local.
2) Inicia los tunnels (uno para backend, otro para pwa).
3) Comparte los 2 links HTTPS con tus socios:
   - PWA pública
   - Dashboard/API pública

> Importante: en la PWA debes apuntar el Backend URL al link público del tunnel del backend.

### Camino B: VPS + Docker Compose
En `infra/` hay plantillas para correr el stack en una máquina remota con Docker.

---

## 4) App instalable para socios (sin tiendas)

### 4.1 PWA instalable (la más universal)
- Android/Chrome: menú ⋮ → **Install app**
- iOS/Safari: Share → **Add to Home Screen**

Esta opción funciona en:
- PC / Notebook / Tablet / Mobile (casi todo)
- Para la demo es ideal (1 solo build).

### 4.2 Android APK (Note 9)
Carpeta: `mobile/android/`
1) Abrir el proyecto en Android Studio
2) Cambiar `BASE_URL` (Config.kt) al backend público (tunnel) o al servidor remoto
3) Build → Generate Signed Bundle/APK → APK
4) Compartir el APK con socios (instalación permitiendo “Unknown Sources”).

### 4.3 iOS (iPhone 14/16)
Carpeta: `mobile/ios/`
1) Abrir en Xcode
2) Ajustar Config.swift con la URL del backend
3) Instalar en dispositivo con cable (requiere Apple ID de desarrollador) o distribuir con TestFlight (sin App Store público)

---

## 5) Qué hay en este repo

- `backend/`  FastAPI + SQLite + Dashboard + audit logs + v2 baselines/stability/human_conf.
- `webapp/`   Pilot PWA (instalable) con acciones: Send Event / Get State / Human Proof / Live mode.
- `sdk_shared/` Motor de cómputo + simuladores.
- `infra/` + `scripts/`  utilidades para demo global.
- `mobile/`  scaffolds Android + iOS (off‑store).
- `extras/mobilefull_reference/` referencia del “Mobile Prototype FULL” anterior.

---

## 6) Checklist de demo (para cuando estés “en cualquier parte”)

1) Arrancas el backend (local o VPS)  
2) Arrancas la PWA (local o VPS)  
3) Publicas ambos por tunnel (o usas dominio/VPS)  
4) En tu teléfono: abres la PWA → Install  
5) Envías evento DEMO y luego “Get State”  
6) Abres Dashboard y muestras:
   - Eventos (index/risk/tier)
   - Baseline + stability + human_conf
   - Audit logs (verificación + anti‑replay)

---

## Seguridad (recordatorio)
Esto es un piloto. Para una demo con socios:
- Usa API Keys (si están habilitadas en tu build)
- No envíes señales crudas sensibles; este stack está pensado como **local‑first** + “solo derivados”.

