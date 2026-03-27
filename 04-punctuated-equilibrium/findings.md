# Punctuated Equilibrium Ecosystem Simulation: Experimental Findings

Date: 2026-03-27

## Model Overview

This simulation implements a hybrid Jain-Krishna / Bak-Sneppen model of ecosystem evolution. Species interact through a directed weighted graph where positive edges represent mutualism/catalysis and negative edges represent competition/inhibition. Each tick, the least-fit species is replaced and its neighbors are perturbed. Fitness is relational -- it depends on incoming connections weighted by source species' fitness. Cascades occur when a replacement causes other species' fitness to drop below viability thresholds, triggering further replacements.

The simulation tracks four phases: RANDOM (disorganized), GROWTH (rising fitness), ORGANIZED (high fitness, low variance), and PUNCTUATION (sharp fitness collapse).

---

## Experiment 1: Baseline Evolution

```
python3 cli.py --evolve --species 100 --ticks 500 --seed 42
```

| Metric | Value |
|---|---|
| Species | 100 |
| Connection probability | 0.05 |
| Weight range | [-1.0, 1.0] |
| Total cascades | 174 |
| Mean cascade size | 2.5 |
| Max cascade size | 21 |
| Final mean fitness | 0.6177 |
| Final density | 0.0523 |
| Final diversity | 0.9021 |
| Keystones at end | 10 |
| Phase transitions | 24 |
| Final phase | random |

**Cascade size distribution:**

| Size | Count |
|---|---|
| 1 | 89 |
| 2 | 39 |
| 3 | 19 |
| 4 | 2 |
| 5 | 7 |
| 6 | 5 |
| 7 | 3 |
| 8 | 3 |
| 9 | 1 |
| 10 | 2 |
| 11-12 | 2 |
| 17 | 1 |
| 21 | 1 |

**Observations:**

The cascade distribution exhibits a clear power-law-like pattern: 89 cascades of size 1 (single replacement), tapering steeply through mid-range sizes, with a thin tail extending to 21. The ratio of size-1 to size-2 events (89:39 = 2.28) and size-2 to size-3 (39:19 = 2.05) suggest a power-law exponent around 2.0.

The system oscillated between RANDOM and GROWTH phases across 24 transitions, never achieving a sustained ORGANIZED state. The largest cascade (size 21) occurred at tick 1, when the initial random network was most fragile and had not yet undergone any selection-driven structuring. A second notable cascade of size 17 struck at tick 169 during a GROWTH phase, demonstrating that even partially organized systems remain vulnerable.

The 10 keystone species at the end represent the top 10% by the keystoneness metric (outgoing positive weight times own fitness times dependent count). Network density held steady around 0.052, close to the initial connection probability of 0.05, confirming that the replacement mechanism approximately preserves graph density.

---

## Experiment 2: Small Ecosystem (20 species)

```
python3 cli.py --evolve --species 20 --ticks 500 --seed 42
```

| Metric | Value |
|---|---|
| Species | 20 |
| Total cascades | 102 |
| Mean cascade size | 2.1 |
| Max cascade size | 12 |
| Final mean fitness | 0.5265 |
| Final diversity | 0.7813 |
| Phase transitions | 94 |
| Punctuation events | 10 |
| Keystones at end | 2 |
| Final phase | growth |

**Cascade size distribution:**

| Size | Count |
|---|---|
| 1 | 57 |
| 2 | 22 |
| 3 | 10 |
| 4 | 2 |
| 5 | 3 |
| 6 | 4 |
| 9 | 2 |
| 11 | 1 |
| 12 | 1 |

**Observations:**

The small ecosystem is dramatically more volatile than the baseline. With 94 phase transitions in 500 ticks (one every 5.3 ticks on average vs. one every 20.8 ticks for baseline), the system rapidly flips between states. It experienced 10 explicit PUNCTUATION events -- sharp fitness collapses detected by the phase detector -- compared to zero for the 100-species baseline. The maximum cascade of 12 represents 60% of the entire ecosystem being replaced in a single event.

The system briefly achieved ORGANIZED phase twice (ticks 69 and 434) but could not sustain it. With only 20 species, each replacement is a 5% perturbation to the network, making stability nearly impossible. Only 2 keystones were identified at the end -- in a network this small, there is less room for structural differentiation.

Lower final fitness (0.5265 vs. 0.6177) and diversity (0.7813 vs. 0.9021) indicate the small ecosystem struggles to build and maintain complex structure. The power-law tail is proportionally larger: the max cascade of 12 (60% of N) compared to 21 (21% of N) in baseline shows that small systems experience relatively larger disruptions.

---

## Experiment 3: Large Ecosystem (200 species)

```
python3 cli.py --evolve --species 200 --ticks 500 --seed 42
```

| Metric | Value |
|---|---|
| Species | 200 |
| Total cascades | 325 |
| Mean cascade size | 23.4 |
| Max cascade size | 120 |
| Final mean fitness | 0.6059 |
| Final diversity | 0.9059 |
| Phase transitions | 33 |
| Punctuation events | 1 |
| Keystones at end | 20 |
| Final phase | random |

**Cascade size distribution (grouped):**

| Size Range | Count |
|---|---|
| 1-5 | 143 |
| 6-10 | 30 |
| 11-20 | 21 |
| 21-40 | 30 |
| 41-60 | 37 |
| 61-80 | 38 |
| 81-100 | 19 |
| 101-120 | 7 |

**Observations:**

The 200-species ecosystem displays qualitatively different dynamics from both the small and baseline systems. The mean cascade size of 23.4 is nearly 10x the baseline's 2.5, and the maximum cascade of 120 species (60% of the ecosystem) dwarfs the baseline's 21 (21%). But the truly striking feature is the cascade size distribution: unlike the baseline's steep power-law drop-off, the large ecosystem shows a remarkably flat distribution from sizes 20-90, with substantial numbers of cascades at every scale. This suggests the system is perpetually near criticality, with perturbation pathways that reach deeply into the network.

The system spent most of its time in RANDOM phase. The lone PUNCTUATION event (tick 434, cascade size 106) removed 53% of species in one event. Phase transitions were moderate (33), between the small system's 94 and the baseline's 24. The initial ticks were especially turbulent: tick 1 saw a cascade of 97, tick 2 saw 60, and several cascades above 80 occurred in the first 100 ticks before any structure could form.

The large system produces rarer but more catastrophic tail events. With 200 nodes and 5% connection probability, each species has approximately 10 connections on average, creating dense dependency chains through which perturbations propagate over long distances.

---

## Experiment 4: Dense Connections (connection probability 0.15)

```
python3 cli.py --evolve --species 100 --ticks 500 --connection-prob 0.15 --seed 42
```

| Metric | Value |
|---|---|
| Species | 100 |
| Connection probability | 0.15 (3x baseline) |
| Total cascades | 427 |
| Mean cascade size | 56.9 |
| Max cascade size | 89 |
| Final mean fitness | 0.5122 |
| Final density | 0.1524 |
| Final diversity | 0.9351 |
| Phase transitions | 88 |
| Keystones at end | 4 |
| Final phase | growth |

**Cascade size distribution (grouped):**

| Size Range | Count |
|---|---|
| 1-10 | 57 |
| 11-30 | 5 |
| 31-50 | 28 |
| 51-60 | 53 |
| 61-70 | 128 |
| 71-80 | 112 |
| 81-89 | 44 |

**Observations:**

This is the most dramatic result across all experiments. Tripling connection density transforms the ecosystem from one with occasional small cascades into a system of perpetual catastrophe. The cascade distribution is strikingly bimodal: a cluster of 57 small cascades (sizes 1-10) and a massive concentration of 365 large cascades centered around sizes 60-75. The mean cascade of 56.9 means the average perturbation replaces more than half the ecosystem.

The system cascades on 427 of 500 ticks (85.4% cascade rate). It cycles through 88 phase transitions, never stabilizing. Mean fitness is the lowest of any experiment (0.5122), and only 4 keystones were identified -- when everything is connected to everything, no species is disproportionately important, but every removal propagates system-wide.

This confirms a fundamental principle: **increased connectivity increases fragility**. Dense networks cannot compartmentalize damage. Each replacement rewires a node with ~15 connections on average (vs. ~5 for baseline), affecting many species simultaneously. Since those affected species are themselves highly connected, the shockwave propagates rapidly to most of the network.

The contrast with the sparse experiment is stark: sparse systems isolate failures while dense systems amplify them.

---

## Experiment 5: Sparse Connections (connection probability 0.02)

```
python3 cli.py --evolve --species 100 --ticks 500 --connection-prob 0.02 --seed 42
```

| Metric | Value |
|---|---|
| Species | 100 |
| Connection probability | 0.02 (40% of baseline) |
| Total cascades | 120 |
| Mean cascade size | 2.4 |
| Max cascade size | 11 |
| Final mean fitness | 0.6911 |
| Final density | 0.0221 |
| Final diversity | 0.7733 |
| Phase transitions | 88 |
| Keystones at end | 10 |
| Final phase | organized |

**Cascade size distribution:**

| Size | Count |
|---|---|
| 1 | 61 |
| 2 | 23 |
| 3 | 11 |
| 4 | 9 |
| 5 | 5 |
| 6 | 4 |
| 7 | 3 |
| 8 | 1 |
| 9 | 1 |
| 10 | 1 |
| 11 | 1 |

**Observations:**

The sparse ecosystem achieved what no other configuration could: a sustained ORGANIZED phase (the final state). It has the highest final mean fitness (0.6911) and the smallest maximum cascade (11). The cascade distribution follows a textbook power-law: steep initial drop-off, negligible tail.

With only ~2 connections per species on average, species are semi-independent. Removing one node rarely affects more than its immediate neighbors. The system achieves stability because compartmentalization prevents cascading failures. The high phase transition count (88) reflects the system repeatedly entering and exiting ORGANIZED, but the important point is that it keeps returning to organization -- it has structural resilience.

The trade-off is clear: diversity is lowest at 0.7733 (vs. 0.9021 for baseline). Fewer interactions mean fewer ecological niches, less interdependence, and less variety. The sparse system found stability at the cost of richness.

---

## Experiment 6: Cascade Analysis (50 species, systematic removal)

```
python3 cli.py --cascade-test --species 50 --seed 42
```

After a 200-tick warmup period, each of the 50 species was individually removed and the resulting cascade was measured (with state restored between tests).

| Metric | Value |
|---|---|
| Total species tested | 50 |
| Keystones identified | 5 |
| Mean cascade (all) | 2.2 |
| Mean cascade (keystones) | 2.8 |
| Mean cascade (non-keystones) | 2.2 |
| Max cascade | 9 (species 3, non-keystone) |

**Top cascade-triggering species:**

| Species | Cascade Size | Keystone? |
|---|---|---|
| 3 | 9 | no |
| 25 | 7 | no |
| 34 | 6 | no |
| 48 | 6 | no |
| 4 | 5 | no |
| 22 | 5 | no |
| 42 | 5 | no |
| 24 | 4 | no |
| 33 | 4 | YES |
| 11 | 3 | YES |
| 47 | 3 | YES |

**Cascade size distribution (all 50 removals):**

| Size | Count |
|---|---|
| 1 | 28 |
| 2 | 7 |
| 3 | 6 |
| 4 | 2 |
| 5 | 3 |
| 6 | 2 |
| 7 | 1 |
| 9 | 1 |

**Observations:**

Keystones produce modestly larger cascades on average (2.8 vs. 2.2 for non-keystones, a 27% increase). However, the single largest cascade (size 9) was triggered by species 3, which was NOT classified as a keystone. Of the top 8 cascade-triggering species, only 1 was a keystone (species 33, cascade size 4). This reveals a significant gap between the keystoneness heuristic and actual cascade vulnerability.

The keystoneness metric captures species with high outgoing positive support to fit dependents, but it misses species that are critical through indirect dependency chains, species that serve as bridges between network clusters, or species whose negative edges prevent competitors from overwhelming others. Species 3 apparently occupies a structural position in the network -- perhaps bridging otherwise disconnected subclusters -- that makes its removal disproportionately damaging.

The distribution of cascade sizes across all 50 removals is heavily skewed: 56% (28/50) of species cause only a single replacement (the new entrant), while 44% cause at least one additional replacement. Only 6% (3/50) cause cascades of 5+. This confirms that cascade vulnerability is concentrated in a small number of structurally important nodes.

---

## Comparative Summary

### Ecosystem Size Effects

| Metric | N=20 | N=100 (baseline) | N=200 |
|---|---|---|---|
| Total cascades | 102 | 174 | 325 |
| Mean cascade size | 2.1 | 2.5 | 23.4 |
| Max cascade size | 12 (60% of N) | 21 (21% of N) | 120 (60% of N) |
| Final mean fitness | 0.5265 | 0.6177 | 0.6059 |
| Diversity | 0.7813 | 0.9021 | 0.9059 |
| Phase transitions | 94 | 24 | 33 |
| Punctuation events | 10 | 0 | 1 |

Larger ecosystems produce dramatically larger absolute cascades but fewer per-capita phase disruptions. The N=200 system's mean cascade of 23.4 (11.7% of N) compared to the baseline's 2.5 (2.5% of N) suggests a nonlinear scaling relationship: cascade severity scales super-linearly with ecosystem size. The N=200 system never achieved stability, remaining in RANDOM phase most of the time due to continuous large perturbations.

### Connection Density Effects

| Metric | Sparse (0.02) | Default (0.05) | Dense (0.15) |
|---|---|---|---|
| Total cascades | 120 | 174 | 427 |
| Mean cascade size | 2.4 | 2.5 | 56.9 |
| Max cascade size | 11 | 21 | 89 |
| Cascade rate (per tick) | 24.0% | 34.8% | 85.4% |
| Final mean fitness | 0.6911 | 0.6177 | 0.5122 |
| Final phase | organized | random | growth |
| Diversity | 0.7733 | 0.9021 | 0.9351 |
| Keystones | 10 | 10 | 4 |

Connection density is the single most powerful parameter in the model. The phase transition from sparse to dense is dramatic: the dense system's mean cascade of 56.9 is 23x the sparse system's 2.4. Increasing connectivity from 0.05 to 0.15 produces a qualitative shift from power-law cascades (many small, few large) to bimodal cascades (a few small, most catastrophically large). The sparse system achieved ORGANIZED; the dense system could never organize at all.

---

## Key Emergent Behaviors

### 1. Self-Organized Criticality

The baseline system naturally drives itself toward a critical state where cascades follow a power-law distribution -- many small events, few large ones, no characteristic scale. This emerges without tuning: the extremal dynamics (always replacing the least fit) are sufficient to produce SOC. The estimated power-law exponent from the baseline is approximately 2.0.

### 2. Phase Cycling Without Stable Equilibrium

No configuration achieved permanent stability. Even the sparse system (which most frequently reached ORGANIZED phase) continued to cycle through states. The system perpetually builds structure, which creates keystones and dependencies, which eventually fail and trigger reorganization. This cycle is intrinsic and unavoidable -- organization sows the seeds of its own disruption.

### 3. The Connectivity-Fragility Paradox

Dense networks are simultaneously more productive (higher diversity: 0.9351) and more fragile (mean cascade: 56.9). Sparse networks are stable but stagnant (diversity: 0.7733, mean cascade: 2.4). There is a productive middle ground around the default connection probability of 0.05 that balances richness and resilience -- the "edge of chaos" described by Kauffman and Beinhocker.

### 4. Keystone Identification Is Incomplete

The cascade test reveals that the simple keystoneness heuristic (outgoing positive support weighted by fitness and dependent count) captures only part of the picture. The most destructive species to remove was NOT flagged as a keystone. True structural vulnerability depends on the full topology -- bridge nodes, cycle participants, and indirect dependency chains -- not just local metrics.

### 5. Size Creates Qualitative Phase Transitions

Small ecosystems (N=20) exhibit frequent, rapid state changes -- high volatility, many punctuation events. Large ecosystems (N=200) exhibit rare but catastrophic collapses. The N=200 system saw cascades exceeding 100 species (50%+ of the ecosystem), events that have no analog in the N=20 or N=100 systems. This mirrors real-world observations: small island ecosystems undergo frequent turnover while continental ecosystems experience rare mass extinctions.

### 6. Initial Conditions Matter Enormously

Across all experiments, the first 20-50 ticks consistently produce the largest or near-largest cascades. The initial random network has no evolved structure, no mutualistic clusters, no load-bearing keystones. Every removal in the early phase has a high probability of cascading because the network has not yet undergone selection for robustness. This parallels how newly formed ecosystems (after mass extinction events, for instance) are especially vulnerable to further disruption.
