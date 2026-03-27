# Phase Transitions in Boolean Networks

## Three Regimes
1. **Ordered phase**: Network converges to short attractor cycles; perturbations decay
2. **Chaotic phase**: Attractor cycles grow exponentially with N; perturbations amplify
3. **Critical (Edge of Chaos)**: Boundary between order and chaos; perturbations propagate on average to one other node

## Critical Connectivity
The phase transition is governed by the critical condition:
```
2K·p(1-p) = 1
```
where:
- K = average number of inputs per node (connectivity)
- p = bias parameter (probability of 1 in Boolean function output)

For unbiased functions (p=0.5): critical K = 2
For biased functions: critical K = 1/(2p(1-p))

## Behavior by Regime
### Ordered (K < Kc)
- Small perturbations die out
- Short attractor cycles (polynomial in N)
- Frozen core: most nodes settle to fixed values
- Derrida coefficient < 1

### Chaotic (K > Kc)
- Small perturbations amplify exponentially
- Long attractor cycles (exponential in N)
- Most nodes fluctuate
- Derrida coefficient > 1

### Critical (K = Kc)
- Perturbations propagate to ~1 other node on average
- Power-law distributed cascade sizes
- Derrida coefficient = 1
- Maximum computational capacity

## Sources
- Derrida, B. & Weisbuch, G. (1986). Evolution of overlaps between configurations in random Boolean networks.
- Kauffman, S.A. (1993). The Origins of Order.
