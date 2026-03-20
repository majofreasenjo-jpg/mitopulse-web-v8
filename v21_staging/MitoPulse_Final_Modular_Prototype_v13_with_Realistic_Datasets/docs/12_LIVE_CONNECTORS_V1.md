# MitoPulse Live Connectors v1

## Qué agrega
Una capa de ingestión viva para conectar MitoPulse con:
- APIs REST
- WebSockets
- carpetas batch / file drop

## Idea central
Las fuentes online no entran directo al motor.
Primero se normalizan al contrato canónico:
- customers.csv
- devices.csv
- events.csv
- signals.csv

## Casos de uso
### Mercados / bolsas
- precios
- ticks
- spreads
- volatilidad
- señales de liquidez

### Bancos / fintech
- transacciones
- logins
- eventos de sesión
- señales AML/fraude

### AFP / fondos
- posiciones
- retornos
- exposiciones
- pasivos

## Flujo
Fuente → Connector → Normalizer → live_output/<source>/...csv → Loader MitoPulse

## Estado
v1 es scaffolding funcional:
- conectores stub
- normalizador
- configs de ejemplo
- contrato de datos

El siguiente paso sería conectar proveedores reales.
