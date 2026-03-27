# Hamming Distance and Perturbation Analysis

## Hamming Distance
The Hamming distance between two binary states s1 and s2 of length N:
```
d(s1, s2) = Σ |s1_i - s2_i|
```
Normalized: ρ = d / N

## Perturbation Analysis
1. Take a network in state S
2. Flip a single bit to create perturbed state S'
3. Evolve both S and S' synchronously
4. Track Hamming distance d(S(t), S'(t)) over time

## Cascade Measurement
A "cascade" is the set of nodes that change state due to a perturbation:
- **Cascade size**: Total number of nodes affected
- **Cascade duration**: Time until perturbation effect dies or network returns to original attractor
- **Cascade depth**: Maximum number of propagation steps

## Cascade Size Distributions by Regime
- **Ordered**: Exponential decay (most cascades are small)
- **Critical**: Power-law distribution P(s) ~ s^(-3/2)
- **Chaotic**: Most perturbations spread to entire network

## Derrida Curve Construction
1. Generate many pairs of random states at various Hamming distances d
2. For each pair, evolve one step
3. Measure resulting Hamming distance d'
4. Plot average d' vs d
5. The slope at d=0 gives the Derrida coefficient λ

## Practical Sensitivity Measurement
For a network with state S:
1. For each node i, flip bit i to create S_i
2. Evolve S and S_i one step
3. Measure Hamming distance h_i = d(f(S), f(S_i))
4. Average sensitivity = (1/N) Σ h_i

## Sources
- Derrida, B. & Weisbuch, G. (1986). Random Networks of Automata.
- Shmulevich, I. & Kauffman, S.A. (2004). Activities and Sensitivities in Boolean Network Models.
