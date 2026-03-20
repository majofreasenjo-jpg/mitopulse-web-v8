# MitoPulse TrustGraph + ICP Prototype (v1)

Este repo implementa lo que describiste (Capa 0→3) en un prototipo ejecutable:

- **Capa 0 (Edge Node)**: motor local (Python) que calcula Index/Tier/Vector/DynamicID + Risk/Coercion/Stability/HumanConf y emite un **Proof Packet** firmado.
- **Capa 1 (Gateway de Verificación)**: API global (FastAPI) que recibe proof packets, aplica **anti‑replay**, validación HMAC, reglas por tenant y devuelve `ok/suspicious/fail`.
- **Capa 2 (Identity State Store)**: SQLite con estado derivado (baselines rolling, bandas, historial de hashes, auditoría). **No guarda biometría cruda.**
- **Capa 3 (Trust Graph)**: grafo de nodos `(user_id, device_id, epoch)` con edges de continuidad, convivencia y riesgo, + clustering simple.
- **Identity Continuity Protocol (ICP)**: migración de identidad (cambio de reloj/celular) y “hibernación/retorno”.

> ⚠️ Nota: es un prototipo de ingeniería para demo/pilotos. No es un producto médico.

---

## Requisitos
- Python 3.10+

## Quickstart (local)

### 1) Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Dashboard: http://127.0.0.1:8000/dashboard
- Docs: http://127.0.0.1:8000/docs

### 2) Edge Node (simulador)
En otra terminal:
```bash
cd edge_node
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1) Registrar tenant + device (demo)
python scripts/register_demo_devices.py --base http://127.0.0.1:8000

# 2) Enviar eventos Tier0/Tier1/Tier2/Tier3 + abandono + migración
python scripts/run_scenarios.py --base http://127.0.0.1:8000
```

### 3) Ver el “sistema vivo”
- Dashboard → secciones: **Identity Events**, **State**, **Trust Graph (edges/clusters)**.

---

## Qué demuestra (casos críticos)

1) **Sin reloj / celular básico** → Tier degradable (Tier0/1). La identidad no cae a 0, baja el *confidence tier*.
2) **Abandono** → el nodo entra a hibernación; al volver se hace *re-onboarding* suave.
3) **Cambio de dispositivo** → ICP handoff token (si hay dispositivo viejo) o recuperación por “trusted group”/tenant.

---

## Estructura
- `backend/` FastAPI + Dashboard + SQLite
- `edge_node/` motor local + scripts de simulación
- `docs/` blueprint + payloads

---

## Próximo salto (si quieres)
- Reemplazar HMAC compartido por **firma asimétrica** (Ed25519) con registro de public keys.
- Reglas de cluster más avanzadas (circadiano real, correlaciones robustas).
- App instalable: PWA + wrappers (Capacitor) o nativos Android/iOS conectados al mismo Gateway.
