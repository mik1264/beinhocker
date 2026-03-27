# Derrida-Weisbuch Annealed Approximation

## Overview
Bernard Derrida and Gérard Weisbuch (1986) developed the annealed approximation for analyzing random Boolean networks, providing analytical predictions for the order-chaos phase transition.

## The Derrida Curve
Plot ρ(t+1) vs ρ(t), where ρ = normalized Hamming distance between two network states:
- **Ordered regime**: Curve lies below diagonal → perturbations shrink
- **Chaotic regime**: Curve lies above diagonal → perturbations grow
- **Critical**: Curve is tangent to diagonal at origin

## Derrida Parameter (Sensitivity)
The Derrida coefficient λ measures average spreading after one time step:
```
λ = 2K·p(1-p)
```
- λ < 1: ordered
- λ = 1: critical
- λ > 1: chaotic

## Annealed Approximation
The "annealed" approximation assumes Boolean functions are redrawn at each time step (rather than fixed/quenched). This simplification enables exact analytical results:

For normalized Hamming distance a(t) between two configurations:
```
a(t+1) = 1 - (1 - a(t))^K · (1-2p(1-p)) - 2p(1-p)·(something more complex)
```

Simplified near a=0:
```
a(t+1) ≈ 2K·p(1-p)·a(t)
```

## Bias Parameter p
- p = probability that a Boolean function outputs 1 for a random input
- p = 0.5: unbiased (maximum sensitivity)
- p → 0 or p → 1: highly biased (more frozen nodes, more ordered)
- Bias creates a "frozen core" of nodes that don't change

## Computational Approach
1. Generate two random initial states differing by Hamming distance d
2. Evolve both for one time step
3. Measure new Hamming distance d'
4. Average over many pairs: Derrida curve is d' vs d
5. Slope at origin = Derrida coefficient λ

## Sources
- Derrida, B. & Weisbuch, G. (1986). Random Networks of Automata: A Simple Annealed Approximation.
