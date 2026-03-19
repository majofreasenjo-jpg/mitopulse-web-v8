# Hierarchical Risk Model (HRM)

## Intuición
El riesgo real no vive en un solo score.
Vive en distintos niveles:
- local
- meso
- global
- exógeno

## Componentes
### Node risk
riesgo del nodo o entidad

### Cluster risk
riesgo del subgrafo o comunidad

### Ecosystem risk
riesgo del sistema completo

### External field risk
riesgo inducido por clima, mercado, geopolítica, etc.

## Fórmula conceptual
P(evento | sistema) = f(
  node_risk,
  cluster_risk,
  ecosystem_risk,
  external_field_pressure
)

## Outputs
- hierarchical_risk_score
- node_contribution_map
- cluster_contribution_map
- field_contribution_map

## Uso
Base probabilística previa a calibración.
