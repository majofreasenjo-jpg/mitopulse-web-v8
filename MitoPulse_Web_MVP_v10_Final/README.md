# MitoPulse Web MVP v10

Prototipo cloud-only de MitoPulse orientado a banca, marketplaces, fraude telefónico/WhatsApp y wallets.

## Principios
- `DATABASE_URL` obligatorio: no usa SQLite local.
- Node IDs persistentes en web y móvil.
- Trust Graph + Shared Reality + Fraud Hunter + módulos por industria.
- Dashboard combinado: antifraude + mapa de red.
- Simulaciones con métricas de falsos positivos.

## Ejecutar en nube
1. Crea base PostgreSQL administrada (Neon, Supabase, Railway, Render Postgres).
2. Configura `DATABASE_URL`.
3. Despliega en Render / Railway / Fly / ECS.
4. Abre `/`, `/network`, `/simulator`, `/node`, `/app`.

## Flujo de demo
1. `POST /seed_demo_network` desde el dashboard.
2. Inicia auto-demo.
3. Abre `/network` para ver guardianes, clusters y nodos en riesgo.
4. Abre `/node` en dos dispositivos y emite latidos / cross pulses.
5. Usa `/app` o `/simulator` para ejecutar escenarios reales.
