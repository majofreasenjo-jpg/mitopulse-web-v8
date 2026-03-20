# SAP / ERP Integration Notes

## Qué rol cumple el ERP
ERP gestiona:
- inventario
- finanzas
- costos
- compras
- activos
- planificación
- órdenes

## Qué hace MitoPulse por encima
- conecta módulos que en ERP suelen verse separados
- modela relaciones ocultas entre inventario, costos, mantenimiento y continuidad
- convierte eventos administrativos en presión sistémica
- aporta dinámica y propagación, no solo estado administrativo

## Enfoque recomendado
No tocar el ERP directamente como primer paso.
Usar:
- exports
- vistas
- capa API
- integration middleware

## Ejemplos de objetos ERP útiles
- purchase_order
- inventory_position
- asset
- work_order
- cost_center
- supplier
- project
- shipment
- invoice
