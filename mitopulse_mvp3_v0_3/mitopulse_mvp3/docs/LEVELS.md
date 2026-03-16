# MitoPulse – 3 Niveles de Cómputo (Tiers)

El motor selecciona automáticamente el nivel más alto posible en cada muestra, según disponibilidad de señales.

## Tier 1 (Básico – "Phone-only")
**Entradas típicas**
- `hr` (frecuencia cardiaca)
- `accel_load` (carga mecánica / movimiento)
- opcional: `spo2`, `sleep_score`

**Uso**
- Demostración inicial de pipeline Local-First.
- Funciona bien para pilotos B2B donde solo quieres *prueba de vida* + anti-replay.

## Tier 2 (Mejorado – "Wearable estándar")
**Entradas típicas**
- Tier 1 +
- `hrv_rmssd` (HRV)

**Uso**
- Identidad dinámica más estable y discriminativa.
- Ideal para MVP B2B de autenticación on-demand.

## Tier 3 (Avanzado – "NIRS / Tissue oxygenation")
**Entradas típicas**
- Tier 2 +
- `sto2` (tissue oxygenation, 0..1 o 0..100)
- y/o `hhb_dt` (derivada de deoxyhemoglobin)

**Uso**
- Capa avanzada cuando existan sensores ópticos más ricos.
- En el MVP queda como **opcional** (se activa si el CSV/API trae esos campos).

## Qué se envía al servidor
Siempre **solo derivados**: `dynamic_id`, `index`, `slope`, `tier_used`, y metadatos de verificación.
Nunca se envían señales fisiológicas crudas.
