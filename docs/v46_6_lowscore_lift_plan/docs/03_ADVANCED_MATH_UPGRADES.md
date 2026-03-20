# Advanced Math Upgrades

## 1. Probabilidad: de lineal a jerárquica no lineal
Antes:
HRM = combinación lineal simple

Ahora:
HRM usa combinación no lineal con interacción entre niveles:
- node
- cluster
- ecosystem
- field

Fórmula conceptual:
HRM* = sigmoid(
  a1*node
  + a2*cluster
  + a3*ecosystem
  + a4*field
  + a5*(cluster*field)
  + a6*(node*ecosystem)
)

## 2. Wave mechanics: de propagación simple a dinámica con damping
Antes:
propagation ~ score scaling

Ahora:
wave_next = wave_current
          + amplification_term
          - damping_term
          + coupling_term
          + external_field_term

## 3. Criticality: de umbral simple a hazard
hazard_t = h0 * exp(
  b1*criticality
  + b2*pressure
  + b3*reserve_stress
  + b4*coordination_pressure
)

## 4. Forecast: de forecast lineal a trayectoria por horizonte
forecast(t+k) = f(graph_t, memory_state, field_state, coupling_state)

## 5. Resilience: de score fijo a balance dinámico
resilience_t = reserves + homeostasis + regeneration - pressure - distortion
