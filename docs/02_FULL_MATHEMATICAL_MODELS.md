# 02. Modelos Matemáticos Completos

## 2.1 Grafo relacional dinámico
Sea:

G_t = (V_t, E_t, W_t)

donde:
- V_t: nodos activos al tiempo t
- E_t: relaciones al tiempo t
- W_t: pesos relacionales

## 2.2 Identidad relacional
Para un nodo i:

RI_i(t) = (N_i(t), E_i(t), W_i(t), H_i(t))

y una versión escalar:

ri_i = \sigma(
a_1 * deg_i +
a_2 * cust_i +
a_3 * dev_i -
a_4 * ext_i -
a_5 * susp_i
)

donde:
- deg_i: grado
- cust_i: vecinos customer
- dev_i: vecinos device
- ext_i: vecinos external
- susp_i: enlaces sospechosos
- sigma(x) = 1 / (1 + e^{-x})

## 2.3 Fingerprint relacional
RF_i = f(deg_i, cc_i, m_i, s_i, ctx_i)

donde:
- deg_i: grado
- cc_i: clustering coefficient
- m_i: motif dominante
- s_i: enlaces sospechosos
- ctx_i: diversidad contextual

## 2.4 Propagación de riesgo
Sea R_i(t) el riesgo del nodo i.
La propagación local:

R_i^{prop}(t) =
\sum_{j \in \mathcal{N}_k(i)} \left( \beta^{d(i,j)-1} * W_{ij} * S_j \right)

donde:
- \mathcal{N}_k(i): vecinos hasta k saltos
- d(i,j): distancia
- beta \in (0,1): atenuación
- S_j: severidad de señal del nodo j

## 2.5 Relational Quorum
Sea un conjunto local de señales x_1, ..., x_n:

Q_i(t) = \sum_{m=1}^n w_m * x_m(t)

Activación:
A_i(t) =
1   si Q_i(t) >= theta_i
0   en otro caso

donde theta_i puede ser fijo o dependiente del tipo de nodo.

## 2.6 Trazas estigmérgicas
Para una relación (i,j):

\tau_{ij}(t+1) = \rho * \tau_{ij}(t) + \Delta_{ij}(t)

donde:
- rho \in (0,1): decaimiento temporal
- \Delta_{ij}(t): incremento por interacción nueva

La traza del nodo i puede definirse como:

ST_i(t) = (1 / |\mathcal{N}(i)|) * \sum_{j \in \mathcal{N}(i)} \tau_{ij}(t)

## 2.7 Danger signal model
Sea D_i(t):

D_i(t) = \sum_{k=1}^{K} \alpha_k * d_{ik}(t)

donde d_{ik} son señales de daño digital, por ejemplo:
- urgent_transfer
- social_engineering
- fake_receipt
- identity_shift
- sim_swap_hint
- device_reset

## 2.8 Reality anchors
Sea A_i^{real}(t):

A_i^{real}(t) = \sum_{r=1}^{R} \lambda_r * a_{ir}(t)

donde a_{ir} representa eventos de alta confianza.

## 2.9 Reserva alostática de confianza
Sea Z_i(t) la reserva alostática:

Z_i(t+1) = Z_i(t) + Rec_i(t) - Stress_i(t)

con:

Rec_i(t) = b_1 * RI_i(t) + b_2 * A_i^{real}(t)
Stress_i(t) = c_1 * D_i(t)

y acotando:
0 <= Z_i(t) <= 1

## 2.10 Trust efectivo
T_i^{eff}(t) = 
clip(
u_1 * RI_i(t)
+ u_2 * A_i^{real}(t)
+ u_3 * Z_i(t)
- u_4 * D_i(t),
0, 1)

## 2.11 Riesgo pre-contacto
Para una interacción potencial entre i y j:

Risk(i,j,t) =
clip(
v_1 * R_i^{prop}(t) +
v_2 * R_j^{prop}(t) +
v_3 * ST_i(t) +
v_4 * ST_j(t) +
v_5 * D_i(t) +
v_6 * D_j(t) +
v_7 * A_i(t) +
v_8 * A_j(t)
- v_9 * A_i^{real}(t)
- v_{10} * A_j^{real}(t),
0,1)

## 2.12 Decisión operativa
Decision(i,j,t) =
ALLOW   si Risk < theta_1
REVIEW  si theta_1 <= Risk < theta_2
BLOCK   si Risk >= theta_2

## 2.13 Morfogénesis de fraude
Sea un cluster c:

M_c(t) =
m_1 * g_c(t) +
m_2 * b_c(t) +
m_3 * q_c(t) +
m_4 * h_c(t)

donde:
- g_c(t): growth rate
- b_c(t): aparición de bridge nodes
- q_c(t): intensidad de etiquetas anómalas
- h_c(t): irregularidad temporal / entropía

Esto detecta firmas de crecimiento de redes sospechosas.
