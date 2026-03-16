# MitoPulse – Global Architecture (TrustGraph + ICP)

## Capa 0 — Edge Node (Usuario)
- Ingesta señales (sensores o inputs)
- Index + Tier
- Ventana deslizante → vector temporal
- Dynamic ID (HMAC/hash con secreto local)
- Risk / Coercion / Stability / HumanConf
- Emite **Proof Packet**: solo derivados + firma

## Capa 1 — Gateway de Verificación (Global Verify API)
- anti‑replay / rate limit
- validación firma (HMAC en demo)
- consistencia temporal
- políticas por tenant

## Capa 2 — Identity State Store
- baseline rolling mean/std
- bandas de estabilidad
- historial de hashes
- auditoría
- **sin biometría cruda**

## Capa 3 — Trust Graph
- Nodo = (user_id, device_id, epoch)
- Edges:
  - Continuity (ICP)
  - Cohab (context_fp + co‑ocurrencia)
  - Risk (coercion bursts)
- Clusters: work/attack (demo), extensible a unit/context.

## ICP — Identity Continuity Protocol
- handoff token firmado por dispositivo viejo
- nuevo dispositivo presenta token + firma
- backend agrega edge continuity y aumenta epoch (ciclo)

## Tier Degradation
- tier0: sin sensores (check‑ins)
- tier1: phone sensors (HR/spo2 aproximado)
- tier2: wearable HRV
- tier3: avanzado

