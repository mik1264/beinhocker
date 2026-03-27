# Sand Pile / Self-Organized Criticality -- Findings

Bak-Tang-Wiesenfeld Abelian Sandpile Model. CLI experiments run with `simulation.py` and `cli.py`.

---

## Experiment 1: Baseline (50x50, threshold=4, 10k ticks, seed=42)

```
python3 cli.py --ticks 10000 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 2,732     |
| Fraction causing avalanche | 27.3%  |
| Mean avalanche size     | 163.5     |
| Median avalanche size   | 11        |
| Max avalanche size      | 6,647     |
| Max avalanche duration  | 331       |
| Power-law exponent (MLE)| 1.289     |
| Mean height at end      | 2.097     |
| Grains lost to edges    | 4,757     |

**Height distribution at criticality:** 7.7% at 0, 18.8% at 1, 29.6% at 2, 43.9% at 3. The system is heavily weighted toward height 3 (one grain below threshold), confirming the critical state.

**Key observation:** The system reaches criticality around tick 4,000-5,000 (after ~2 mean-heights worth of grain accumulation). Afterward, avalanches of all sizes occur continuously. The largest single avalanche (6,647 topplings) was triggered by a single grain drop at position (28,17). The ratio of max to median avalanche size is ~600:1, demonstrating the extreme range of event scales characteristic of power-law systems.

---

## Experiment 2: Small Grid (25x25, threshold=4, 10k ticks, seed=42)

```
python3 cli.py --ticks 10000 --grid-size 25 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 3,774     |
| Fraction causing avalanche | 37.7%  |
| Mean avalanche size     | 58.7      |
| Median avalanche size   | 14        |
| Max avalanche size      | 972       |
| Power-law exponent (MLE)| 1.299     |
| Mean height at end      | 2.066     |
| Grains lost to edges    | 8,709     |

**Comparison to baseline:** Smaller grid reaches criticality faster (higher avalanche frequency: 37.7% vs 27.3%). Maximum avalanche size is much smaller (972 vs 6,647) due to the smaller available area. The power-law exponent is similar (1.299 vs 1.289). Edge effects dominate: 87% of grains were lost to edges vs 48% for the 50x50 grid.

---

## Experiment 3: Large Grid (100x100, threshold=4, 10k ticks, seed=42)

```
python3 cli.py --ticks 10000 --grid-size 100 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 223       |
| Fraction causing avalanche | 2.2%   |
| Mean avalanche size     | 1.20      |
| Max avalanche size      | 7         |
| Power-law exponent (MLE)| 2.225     |
| Mean height at end      | 0.999     |
| Grains lost to edges    | 6         |

**Not yet critical.** With 10,000 cells and only 10,000 grains dropped, the mean height is ~1.0 -- far below the critical mean height of ~2.1. The system has barely begun to reach criticality. Only 6 grains have been lost to edges, and the largest avalanche involved only 7 topplings. This experiment demonstrates that **larger grids require proportionally more grain drops to reach criticality**.

To reach criticality on a 100x100 grid, we would need approximately 10,000 * (100/50)^2 = 40,000+ ticks just to fill the grid to the critical mean height.

---

## Experiment 4: Long Run (50x50, threshold=4, 50k ticks, seed=42)

```
python3 cli.py --ticks 50000 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 20,110    |
| Fraction causing avalanche | 40.2%  |
| Mean avalanche size     | 210.5     |
| Median avalanche size   | 22        |
| Max avalanche size      | 6,647     |
| Power-law exponent (MLE)| 1.256     |
| Mean height at end      | 2.104     |
| Grains lost to edges    | 44,741    |

**Better statistics confirm the power law.** With 5x more data than the baseline, the power-law exponent converges to 1.256 (closer to the theoretical range of 1.0-1.2). The avalanche frequency stabilizes at ~40% of drops causing an avalanche. The height distribution is nearly identical to the baseline, confirming the system is in a stable critical state.

The 10 largest avalanches range from 4,872 to 6,647 topplings, spanning the entire simulation from tick 5,703 to tick 49,588. This confirms that extreme events continue to occur at all times once criticality is reached -- they are not transient phenomena.

---

## Experiment 5: High Threshold (50x50, threshold=8, 10k ticks, seed=42)

```
python3 cli.py --ticks 10000 --threshold 8 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 163       |
| Fraction causing avalanche | 1.6%   |
| Mean avalanche size     | 3.00      |
| Max avalanche size      | 23        |
| Power-law exponent (MLE)| 1.711     |
| Mean height at end      | 3.989     |
| Grains lost to edges    | 28        |

**Not yet critical.** With threshold=8, each cell must accumulate 8 grains before toppling. With 10,000 grains spread across 2,500 cells, the mean height is ~4.0, which is only half the threshold. The system is still in the sub-critical accumulation phase. Toppling redistributes 8 grains per event (2 to each of the 4 neighbors), which creates richer cascade dynamics when it finally reaches criticality, but we would need approximately 20,000+ ticks for the mean height to approach the critical level (~6-7).

**Height distribution:** roughly uniform from 0-7, as expected for a sub-critical state.

---

## Experiment 6: Low Threshold (50x50, threshold=2, 10k ticks, seed=42)

```
python3 cli.py --ticks 10000 --threshold 2 --seed 42
```

| Metric                  | Value     |
|-------------------------|-----------|
| Avalanches (size > 0)   | 8,515     |
| Fraction causing avalanche | 85.2%  |
| Mean avalanche size     | 195.5     |
| Median avalanche size   | 153       |
| Max avalanche size      | 650       |
| Power-law exponent (MLE)| 1.190     |
| Mean height at end      | 0.980     |
| Grains lost to edges    | 7,550     |

**Rapid criticality with constrained dynamics.** With threshold=2, cells topple almost immediately. The system reaches criticality very quickly and 85% of grain drops cause avalanches. However, because each topple only redistributes 2 grains (to 2 of the 4 neighbors -- up and down), the cascade dynamics are more constrained. The max avalanche size (650) is much smaller than the standard model, and the distribution is narrower.

**Height distribution:** 98.0% of cells at height 1, 2.0% at height 0. The system is almost uniformly at height 1 (one below threshold), with edge cells occasionally at 0 from grain loss.

The power-law exponent of 1.190 is within the theoretical range, though the distribution has a visible upper cutoff around 650 due to the directional constraint of the 2-grain redistribution.

---

## Cross-Experiment Comparison

| Experiment | Grid | Threshold | Ticks  | alpha | Max Aval | Aval Freq |
|-----------|------|-----------|--------|-------|----------|-----------|
| 1. Baseline | 50   | 4        | 10k    | 1.289 | 6,647    | 27.3%     |
| 2. Small    | 25   | 4        | 10k    | 1.299 | 972      | 37.7%     |
| 3. Large    | 100  | 4        | 10k    | 2.225 | 7        | 2.2%      |
| 4. Long     | 50   | 4        | 50k    | 1.256 | 6,647    | 40.2%     |
| 5. High thr | 50   | 8        | 10k    | 1.711 | 23       | 1.6%      |
| 6. Low thr  | 50   | 2        | 10k    | 1.190 | 650      | 85.2%     |

---

## Key Findings

### 1. Self-organized criticality is real and robust

The system spontaneously evolves to a critical state without any parameter tuning (experiments 1, 2, 4, 6). Once at criticality, the avalanche size distribution follows a power law with exponent ~1.2-1.3 for the standard 2D BTW model. This confirms Bak et al.'s central claim.

### 2. Power-law behavior requires reaching the critical state

Experiments 3 and 5 demonstrate that systems not yet at criticality show no power-law behavior. The 100x100 grid with only 10k grains and the threshold=8 case both had insufficient loading to reach criticality. The power-law is an emergent property of the critical state, not of the dynamics per se.

### 3. Grid size controls the maximum event scale but not the exponent

The power-law exponent is a property of the universality class, not the system size. Both the 25x25 and 50x50 grids at criticality show similar exponents (~1.29). But the maximum avalanche size scales with the grid area: 972 for 25x25 vs 6,647 for 50x50.

### 4. The height distribution at criticality is diagnostic

At criticality, the height distribution is strongly peaked at height = threshold - 1. For threshold=4: 43.9% of cells at height 3. For threshold=2: 98.0% at height 1. This "loaded spring" state is what enables cascade propagation.

### 5. No typical event size exists

The median-to-max avalanche ratio for the baseline is ~1:600. This is the core insight of SOC as applied to economics (Beinhocker Ch 8): traditional risk models based on normal distributions systematically underestimate tail risk because they assume a "typical" event size exists. In power-law systems, extreme events are not outliers -- they are an inherent, predictable consequence of the system's dynamics.

### 6. Conservation and dissipation balance at criticality

At the critical state, the system reaches a dynamic equilibrium where the rate of grain addition (1 per tick) balances the rate of grain loss through edges. For the 50x50 baseline after 50k ticks, the mean height stabilizes at ~2.1 and 89.5% of all grains added have been lost to edges. The system is an open dissipative system at a far-from-equilibrium steady state -- a hallmark of complex adaptive systems.
