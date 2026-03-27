# Boolean Network / Complexity Catastrophe: Experimental Findings

These experiments were run on 2026-03-27 using `simulation.py` (Kauffman random Boolean networks) with `cli.py`. All runs use seed=42 for reproducibility.

---

## Experiment 1: Phase Diagram (K and Bias Sweep)

**Command:** `python3 cli.py --phase-diagram --nodes 50 --seed 42`

Swept K=1..7 against bias p=0.10..0.90 (in 0.05 increments) with N=50 nodes.

### Phase Map

```
       0.10 0.15 0.20 0.25 0.30 0.35 0.40 0.45 0.50 0.55 0.60 0.65 0.70 0.75 0.80 0.85 0.90
K= 1    O    O    O    O    O    O    O    O    O    O    O    O    O    O    O    O    O
K= 2    O    O    O    O    *    *    *    *    *    *    *    *    *    O    O    O    O
K= 3    O    O    *    *    C    C    C    C    C    C    C    *    C    *    *    O    O
K= 4    O    *    C    C    C    C    C    C    C    C    C    C    C    C    *    *    O
K= 5    *    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C    *
K= 6    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C    *
K= 7    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C    C
```

O = ordered (lambda < 0.8), * = critical (0.8 <= lambda <= 1.2), C = chaotic (lambda > 1.2)

### Phase Transition Boundary

The critical boundary follows the theoretical curve **lambda = 2Kp(1-p) = 1**, which traces a symmetric parabola in K-bias space:

| K | Critical bias range (approximate) |
|---|---|
| 1 | Never chaotic -- always ordered at any bias |
| 2 | p in [0.30, 0.70] -- critical band, never fully chaotic |
| 3 | p in [0.20, 0.25] and [0.75, 0.80] are critical; p in [0.30, 0.70] is chaotic |
| 4 | p in [0.15, 0.20] and [0.80, 0.85] are critical; middle range is chaotic |
| 5 | Only extreme bias (p=0.10, p=0.90) remains critical; all else chaotic |
| 6 | Only p=0.90 barely reaches critical; everything else chaotic |
| 7 | Fully chaotic at all tested biases |

The measured Derrida parameters closely track the theoretical prediction. For example, at K=4, p=0.50 the theory predicts lambda=2.000 and we measured 2.083. At K=2, p=0.50 theory predicts 1.000 and we measured 1.127. The diagram is symmetric around p=0.50, confirming that bias toward 0 and bias toward 1 are equivalent stabilizers.

**Key finding:** The phase boundary is sharp and predictable. Organizations wanting to maintain K=4 interconnections need decision-rule predictability (bias) of at least 0.85 to avoid chaos. At K=7, no amount of bias can prevent chaos.

---

## Experiment 2: Ordered Regime (K=1)

**Command:** `python3 cli.py --nodes 50 --connectivity 1 --seed 42`

| Metric | Value |
|---|---|
| Theoretical lambda | 0.500 |
| Measured Derrida parameter | 0.445 |
| Regime | **Ordered** |
| Attractors found | 30/30 |
| Mean cycle length | 8.0 |
| Max cycle length | 8 |
| Mean cascade size | 2.9 / 50 nodes (5.8%) |
| Max cascade size | 12 |
| Mean final Hamming distance | 0.5 |

### Derrida Curve

| d_in | d_out |
|---|---|
| 0.10 | 0.04 |
| 0.20 | 0.09 |
| 0.30 | 0.12 |
| 0.50 | 0.21 |
| 1.00 | 0.42 |

### Observations

**Frozen dynamics, reliable attractors.** The Derrida parameter of 0.445 is well below 1.0. This means perturbations are strongly damped: flip one bit, and on average less than half a bit changes in the next step. The Derrida curve shows d_out consistently below d_in across all initial distances -- the hallmark of error-correcting dynamics.

**Short attractor cycles.** All 30 trials found attractors with a uniform cycle length of 8. The state space collapses quickly into a small set of repeating patterns.

**Tiny cascades.** On average, flipping one node eventually affects only 2.9 of 50 nodes (5.8%). The final Hamming distance of 0.5 means the system almost entirely heals the perturbation. This is an organization of independent workers: stable but incapable of coordinated adaptation.

---

## Experiment 3: Critical Regime (K=2)

**Command:** `python3 cli.py --nodes 50 --connectivity 2 --seed 42`

| Metric | Value |
|---|---|
| Theoretical lambda | 1.000 |
| Measured Derrida parameter | 1.010 |
| Regime | **Critical** |
| Attractors found | 30/30 |
| Mean cycle length | 9.0 |
| Max cycle length | 9 |
| Mean cascade size | 5.9 / 50 nodes (11.8%) |
| Max cascade size | 24 |
| Mean final Hamming distance | 0.7 |

### Derrida Curve

| d_in | d_out |
|---|---|
| 0.10 | 0.10 |
| 0.20 | 0.17 |
| 0.30 | 0.26 |
| 0.50 | 0.36 |
| 1.00 | 0.43 |

### Observations

**Edge of chaos confirmed.** The measured Derrida parameter of 1.010 matches the theoretical prediction of 1.000 with remarkable precision. The Derrida curve shows d_out tracking d_in almost exactly at small distances (d_in=0.10 maps to d_out=0.10) -- the signature of criticality where perturbations neither grow nor shrink.

**Moderate, variable cascades.** Mean cascade size doubles relative to K=1 (5.9 vs 2.9), but the maximum of 24 nodes (48% of the network) reveals the hallmark of criticality: occasional large avalanches coexisting with frequent small ones. This power-law-like distribution is the "interesting" regime where diverse cascade sizes coexist.

**Attractors remain accessible.** All 30 trials find attractors with short cycle lengths (mean 9.0). The system is still computationally tractable -- it can be understood and predicted -- while being responsive enough that signals propagate meaningfully.

**This is Kauffman's sweet spot.** K=2 at p=0.5 sits precisely at the phase boundary. It maximizes information processing: perturbations propagate far enough to allow coordination and adaptation, but not so far as to destroy coherence.

---

## Experiment 4: Chaotic Regime (K=5)

**Command:** `python3 cli.py --nodes 50 --connectivity 5 --seed 42`

| Metric | Value |
|---|---|
| Theoretical lambda | 2.500 |
| Measured Derrida parameter | 2.265 |
| Regime | **Chaotic** |
| Attractors found | 0/30 |
| Mean cascade size | 46.7 / 50 nodes (93.4%) |
| Max cascade size | 50 (100%) |
| Mean final Hamming distance | 23.5 |

### Derrida Curve

| d_in | d_out |
|---|---|
| 0.10 | 0.22 |
| 0.20 | 0.35 |
| 0.30 | 0.44 |
| 0.50 | 0.46 |
| 1.00 | 0.51 |

### Observations

**Total chaos -- no attractors found.** With five inputs per node, the Derrida parameter of 2.265 means each flipped bit causes more than two bits to flip at the next time step -- exponential amplification. Not a single attractor was found in 30 trials within 5000 steps. The state space is so vast and the dynamics so sensitive that the system never revisits any previous state.

**Cascades engulf nearly everything.** Mean cascade size is 46.7 out of 50 nodes (93.4%), and the maximum reaches 100% of the network. Flip one node, and on average 93% of all nodes are eventually affected. The mean final Hamming distance of 23.5 (out of 50) means perturbed and unperturbed trajectories end up in essentially uncorrelated states -- about half the bits differ, indistinguishable from random.

**Derrida curve shows rapid divergence.** At d_in=0.10 (5 differing bits), d_out has already more than doubled to 0.22. By d_in=0.30, the system approaches its saturation value of ~0.50 (the maximum possible for random uncorrelated states). Small differences are amplified to maximum disorder within a single time step.

**Sensitivity to perturbation is extreme.** This is the complexity catastrophe in its purest form: the system is so interconnected that any change propagates everywhere, making prediction, control, and coordination impossible. This is an organization where every decision depends on five other people's decisions -- total gridlock.

---

## Experiment 5: Hierarchy vs Random Topology (K=3)

### Hierarchy Topology

**Command:** `python3 cli.py --nodes 50 --connectivity 3 --topology hierarchy --seed 42`

| Metric | Value |
|---|---|
| Derrida parameter | 1.495 |
| Regime | Chaotic |
| Attractors found | 30/30 |
| Mean cycle length | 426.5 |
| Max cycle length | 489 |
| Mean cascade size | 30.1 / 50 (60.2%) |
| Max cascade size | 49 |
| Mean final Hamming | 13.9 |

### Random Topology

**Command:** `python3 cli.py --nodes 50 --connectivity 3 --topology random --seed 42`

| Metric | Value |
|---|---|
| Derrida parameter | 1.505 |
| Regime | Chaotic |
| Attractors found | 30/30 |
| Mean cycle length | 381.3 |
| Max cycle length | 393 |
| Mean cascade size | 31.2 / 50 (62.4%) |
| Max cascade size | 49 |
| Mean final Hamming | 11.6 |

### Comparative Analysis

| Metric | Hierarchy | Random | Difference |
|---|---|---|---|
| Derrida parameter | 1.495 | 1.505 | Essentially identical |
| Attractors found | 30/30 | 30/30 | Both successful |
| Mean cycle length | 426.5 | 381.3 | Hierarchy slightly longer |
| Mean cascade size | 30.1 (60%) | 31.2 (62%) | Hierarchy slightly smaller cascades |
| Mean final Hamming | 13.9 | 11.6 | Hierarchy slightly higher |

### Observations

**Hierarchy does not change the phase classification.** Both topologies produce nearly identical Derrida parameters (~1.50), confirming that the local sensitivity is determined by K and bias, not by wiring pattern. Both networks are classified as chaotic.

**At N=50 with K=3, hierarchy's advantage is marginal.** Cascade sizes are almost identical (30.1 vs 31.2). Both find all attractors. The modular decomposition of 50 nodes into the default hierarchy (depth=3, branching factor=3, creating 27 leaf modules of ~2 nodes each) is too fine-grained to provide meaningful firebreaks at this scale.

**Hierarchy's value emerges at larger scales.** The prior experiments in `experiments.md` demonstrate that at N=150 with K=3, hierarchy produces a dramatic difference: random networks find zero attractors while hierarchical networks find all 30, and cascade sizes drop from 63% to 36%. At N=50, the network is small enough that both topologies remain manageable. Hierarchy is a scaling strategy -- its benefits are most apparent when the network grows beyond the point where flat structures fail.

**Cycle lengths are longer in hierarchy.** Interestingly, the hierarchical network shows slightly longer cycle lengths (426.5 vs 381.3). The modular structure may create more complex basin-of-attraction landscapes with longer limit cycles, even as it constrains perturbation spread at larger scales.

---

## Experiment 6: Scale Effects (N=20, 100, 200 at K=2)

### Results Summary

| N | Derrida | Regime | Attractors Found | Mean Cycle Length | Max Cycle | Mean Cascade | Max Cascade | Cascade % | Mean Final Hamming |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 0.985 | Critical | 30/30 | 2.6 | 3 | 4.6 | 16 | 23.0% | 0.2 |
| 50 | 1.010 | Critical | 30/30 | 9.0 | 9 | 5.9 | 24 | 11.8% | 0.7 |
| 100 | 0.920 | Critical | 30/30 | 1.0 | 1 | 5.7 | 36 | 5.7% | 0.0 |
| 200 | 0.990 | Critical | 30/30 | 5.8 | 10 | 14.4 | 98 | 7.2% | 0.8 |

### Derrida Curves Compared

| d_in (fraction) | N=20 d_out | N=50 d_out | N=100 d_out | N=200 d_out |
|---|---|---|---|---|
| 0.10 | 0.11 | 0.10 | 0.10 | 0.10 |
| 0.30 | 0.25 | 0.26 | 0.26 | 0.26 |
| 0.50 | 0.38 | 0.36 | 0.37 | 0.37 |
| 1.00 | 0.47 | 0.43 | 0.49 | 0.48 |

### Observations

**All sizes remain critical.** The Derrida parameter stays close to 1.0 across all four network sizes (0.920 to 1.010), confirming that the phase classification at K=2, p=0.5 is a fundamental property of the connectivity and bias, independent of scale.

**Cascade sizes grow sub-linearly.** Absolute cascade sizes increase (4.6, 5.9, 5.7, 14.4) but as a percentage of the network they decrease (23%, 12%, 5.7%, 7.2%). This is a key feature of the critical regime: the system scales gracefully. At N=200, the largest cascade reached 98 nodes (49% of the network), but the mean remains at only 7.2%. Critical networks maintain proportional containment as they grow.

**Attractors remain accessible at all scales.** All four sizes found attractors in every trial. Cycle lengths are short across the board (1.0 to 9.0 mean). The critical regime is computationally tractable even at N=200.

**Final Hamming distances stay near zero.** The system heals perturbations. Mean final Hamming stays below 1.0 at all sizes, meaning the perturbed trajectory converges back to (nearly) the same state as the unperturbed one. This is the error-correcting property of critical networks.

**Maximum cascade sizes do grow.** While mean cascades stay proportionally small, the maximum cascade size scales roughly linearly (16, 24, 36, 98). The tail of the cascade distribution extends further at larger N -- rare extreme events become larger in absolute terms, even though typical events remain contained. This is the power-law signature of criticality: most events are small, but the largest possible event grows with system size.

**Contrast with chaotic scaling.** The prior experiments in `experiments.md` show that at K=4, scaling is catastrophic: N=20 is manageable (cascades ~82%, attractors all found), N=50 is struggling (cascades ~61%, only 27% of attractors found), and N=150 is uncontrollable (cascades ~90%, no attractors found). The critical regime at K=2 avoids this entirely -- scaling is graceful rather than catastrophic.

---

## Summary of Key Findings

### 1. The Phase Transition Is Sharp, Predictable, and Confirmed

The formula lambda = 2Kp(1-p) predicts the boundary between order and chaos with high fidelity. At K=1, lambda=0.445 (ordered). At K=2, lambda=1.010 (critical). At K=5, lambda=2.265 (chaotic). The phase diagram sweeping K=1..7 and p=0.10..0.90 maps the full boundary surface. The transition is not gradual -- it is a qualitative discontinuity.

### 2. Regime Behaviors Are Qualitatively Distinct

| Property | Ordered (K=1) | Critical (K=2) | Chaotic (K=5) |
|---|---|---|---|
| Derrida parameter | 0.445 | 1.010 | 2.265 |
| Attractors found | 30/30 (100%) | 30/30 (100%) | 0/30 (0%) |
| Mean cycle length | 8.0 | 9.0 | Not found |
| Mean cascade % | 5.8% | 11.8% | 93.4% |
| Max cascade size | 12 | 24 | 50 (100%) |
| Final Hamming | 0.5 | 0.7 | 23.5 |
| Perturbation fate | Absorbed | Propagates at boundary | Amplifies to saturation |

The jump from K=2 to K=5 is not a smooth increase -- it is a transition from a regime where the system heals perturbations and finds attractors, to one where perturbations consume the entire network and no stable states can be located.

### 3. Hierarchy Is a Scaling Strategy, Not a Local Fix

At N=50 with K=3, hierarchy and random topology produce nearly identical results (cascade sizes of 60% vs 62%). Hierarchy's value is subtle at small scales because the network is small enough that flat structures still work. The benefit emerges at scale: prior experiments show that at N=150, hierarchy cuts cascade sizes nearly in half and makes attractor-finding possible where flat networks fail entirely. Hierarchy is organizational infrastructure for managing complexity at scale.

### 4. Critical Networks Scale Gracefully

At K=2, increasing N from 20 to 200 preserves the fundamental character of the dynamics. Cascade percentages decrease, attractors remain findable, and the system stays computationally tractable. In contrast, chaotic networks exhibit catastrophic scaling where the same connectivity that works at N=20 produces uncontrollable dynamics at N=150. This is the core argument for why organizations should target K=2 effective connectivity.

### 5. The Complexity Catastrophe Is a Scale-Dependent Threshold

The catastrophe is not about K alone -- it is about K at a given N. A team of 20 with K=4 interdependencies may function (prior experiments show cycle lengths ~24, manageable cascades). The same structure at N=150 is paralyzed. This explains why organizational structures that work in startups fail in large enterprises: the connectivity that enabled agility becomes the source of chaos at scale.

### 6. Bias (Predictability) Is the Other Control Knob

The phase diagram demonstrates that high bias (predictable decision rules) can stabilize networks with high connectivity. K=3 at p=0.85 is ordered; K=3 at p=0.50 is chaotic. This maps to organizational practice: standardized procedures, clear policies, and decision frameworks increase bias, allowing more interconnection without crossing the chaos boundary. Rules and routines are not bureaucratic overhead -- they are the mathematical mechanism that tames the complexity catastrophe.
