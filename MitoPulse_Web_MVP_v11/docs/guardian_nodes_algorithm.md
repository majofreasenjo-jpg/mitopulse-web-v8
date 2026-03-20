
# Guardian Nodes Algorithm

Guardian score:
`0.18*stability + 0.18*trust_rank + 0.15*nodal_mass + 0.12*pulse_factor + 0.17*cross_factor + 0.20*(100-fraud_exposure)`

Guardian threshold:
- score >= 72
- fraud_exposure < 25
- degree >= 2

Where:
- stability = degree and avg relationship weight
- trust_rank = local trust estimate
- nodal_mass = accumulated strength by events
- pulse_factor = heartbeat activity
- cross_factor = cross-pulse activity
- fraud_exposure = propagated fraud risk from neighbors
