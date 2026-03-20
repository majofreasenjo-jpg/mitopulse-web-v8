# Mapa de Conectores por Industria

## Banking / Fintech
### Fuentes típicas
- core banking
- AML / fraud engine
- transaction processor
- device intelligence
- beneficiary registry
- customer channels

### Conectores / formatos
- REST / GraphQL APIs
- batch CSV / Parquet
- ISO 20022-like mappings
- webhooks / event streams
- Kafka / message bus

### Objetos típicos
- account
- wallet
- beneficiary
- transfer
- device
- channel
- customer

---

## Marketplace
### Fuentes típicas
- orders
- listings
- reviews
- payouts
- seller onboarding
- trust & safety logs
- device / session signals

### Conectores / formatos
- REST APIs
- webhooks
- object storage batch
- event bus
- BI exports

### Objetos típicos
- seller
- buyer
- listing
- order
- payout
- device
- review cluster

---

## Energy / Refining / Offshore
### Fuentes típicas
- SCADA / historian
- maintenance systems
- lab / quality systems
- dispatch / terminal systems
- trading desks
- external field signals

### Conectores / formatos
- OPC-UA adapter
- MQTT adapter
- historian batch exports
- CSV / SQL
- APIs
- weather / energy market feeds

### Objetos típicos
- unit
- tank
- route
- supplier
- contract
- maintenance team
- external field

---

## Logistics / Maritime / Supply Chain
### Fuentes típicas
- TMS
- WMS
- route planning
- telematics
- shipment tracking
- port operations
- vessel / truck status

### Conectores / formatos
- REST APIs
- EDI / flat files
- GPS / telemetry streams
- port event APIs
- vessel status feed
- ERP exports

### Objetos típicos
- shipment
- vessel
- truck
- route
- warehouse
- port
- cargo
- contract

---

## Mining / Industrial Operations
### Fuentes típicas
- plant monitoring
- fleet management
- maintenance backlog
- inventory / spare parts
- procurement
- contractor systems

### Conectores / formatos
- SCADA / historian exports
- telemetry
- ERP APIs
- CMMS exports
- CSV / batch

### Objetos típicos
- asset
- fleet
- pit / plant node
- maintenance task
- spare part
- supplier
- haul route

---

## ERP / SAP-like / Administrative Systems
### Fuentes típicas
- finance
- inventory
- procurement
- costing
- HR / org structure
- production planning
- order management

### Conectores / formatos
- API layer
- database views
- batch exports
- ETL/ELT pipeline
- integration middleware
- file drops

### Objetos típicos
- material
- inventory position
- cost center
- supplier
- purchase order
- invoice
- asset
- org unit
- project
