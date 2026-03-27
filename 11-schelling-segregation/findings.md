# Schelling Segregation Model: Experimental Findings

All experiments run on a 50x50 torus grid with seed 42 for reproducibility.

## Summary Table

| Experiment | Threshold | Density | Init Seg | Final Seg | Amplification | Happiness | Total Moves | Converged Tick | Largest Cluster |
|---|---|---|---|---|---|---|---|---|---|
| 1. Baseline | 30% | 70% | 0.503 | 0.750 | +49% | 100% | 705 | 10 | 670 |
| 2. Moderate | 50% | 70% | 0.503 | 0.899 | +79% | 100% | 1,823 | 11 | 856 |
| 3. High intolerance | 75% | 70% | 0.503 | 0.998 | +99% | 100% | 65,820 | 95 | 852 |
| 4. Very tolerant | 10% | 70% | 0.503 | 0.540 | +7% | 100% | 65 | 2 | 387 |
| 5. Sparse | 30% | 50% | 0.489 | 0.778 | +59% | 100% | 552 | 14 | 104 |
| 6. Dense | 30% | 95% | 0.496 | 0.753 | +52% | 100% | 1,040 | 12 | 1,176 |

## Detailed Analysis

### Experiment 1: Baseline (threshold 30%, density 70%)

This is Schelling's classic case. Starting from random placement (segregation index ~0.50), the system rapidly self-organizes into neighborhoods that are 75% homogeneous -- converging in just 10 ticks with 705 total relocations. The key paradox is on full display: agents who are happy being a minority (70% of neighbors can be different) collectively produce neighborhoods far more segregated than anyone demanded. The largest cluster reaches 670 agents -- nearly 77% of one type in a single contiguous region.

### Experiment 2: Moderate intolerance (threshold 50%)

Raising the threshold to 50% (agents want at least half their neighbors to match) drives segregation to 90%. The system converges in 11 ticks but requires 1,823 moves -- more than 2.5x the baseline. The interface density drops to just 6.8%, meaning almost no cross-type boundaries remain. The largest cluster (856) encompasses nearly all agents of one type.

### Experiment 3: High intolerance (threshold 75%)

The most dramatic experiment. With a 75% threshold, agents demand strong homogeneity. The segregation index reaches 0.998 -- essentially perfect segregation. But the cost is enormous: 65,820 total moves over 95 ticks before convergence. This is because with 70% density, the limited empty cells create a bottleneck. Agents keep shuffling back and forth in an extended sorting process. The peak moves per tick (1,462) exceeds the total moves in the baseline experiment. Interface density drops to 0.03% -- virtually zero cross-type contact.

### Experiment 4: Very tolerant (threshold 10%)

With a 10% threshold, agents tolerate almost any neighborhood composition. Only 65 agents moved (3.7% of the population), and the system converged in just 2 ticks. The final segregation index of 0.54 is barely above the random baseline of 0.50. This serves as a useful control: very low thresholds produce minimal segregation, confirming that the effect is driven by the threshold parameter, not an artifact of the movement rule.

### Experiment 5: Sparse population (density 50%)

With half the grid empty, agents have abundant room to relocate. The final segregation (0.78) is actually slightly higher than the baseline (0.75) despite fewer agents, because the abundance of empty cells allows agents to find optimal positions more easily. However, the largest cluster is much smaller (104 vs 670) -- the sparse population naturally fragments into many small clusters rather than a few large ones. Total moves (552) are lower than the baseline because fewer agents are unhappy to begin with.

### Experiment 6: Dense population (density 95%)

With only 125 empty cells (5% of the grid), the mobility bottleneck is severe. Yet the system still reaches a segregation index of 0.75 -- essentially identical to the 70% density baseline. It takes slightly more ticks (12 vs 10) and more total moves (1,040 vs 705). The largest cluster is massive (1,176) because the dense packing means any cluster tends to merge with nearby same-type agents. The key finding: even extreme density constraints do not prevent Schelling segregation from emerging.

## Key Findings

### 1. The micro-macro disconnect is real and dramatic
A 30% threshold (tolerance for being a minority) produces 75% segregation. A 50% threshold (wanting a bare majority) produces 90% segregation. The amplification factor ranges from 49% to 99% depending on threshold.

### 2. The threshold-segregation relationship is non-linear
- 10% threshold: 7% amplification (trivial effect)
- 30% threshold: 49% amplification (major effect)
- 50% threshold: 79% amplification (extreme effect)
- 75% threshold: 99% amplification (near-total segregation)

There appears to be a critical region between 10% and 30% where the system transitions from minimal to major segregation.

### 3. Density affects dynamics more than outcomes
The final segregation level is remarkably similar across densities (0.75 at 70% density, 0.78 at 50% density, 0.75 at 95% density). What changes is the dynamics: sparse populations converge faster with many small clusters; dense populations take longer but form massive contiguous blocks.

### 4. Convergence speed varies enormously
- Low threshold (10%): 2 ticks, 65 moves
- Baseline (30%): 10 ticks, 705 moves
- Moderate (50%): 11 ticks, 1,823 moves
- High (75%): 95 ticks, 65,820 moves

The relationship between threshold and convergence effort is super-linear, especially above 50%.

### 5. All experiments reached full equilibrium
Every experiment achieved 100% happiness. This is notable for the high-intolerance case (75% threshold), which took 95 ticks but still found a stable configuration. The availability of 30% empty cells in the standard setup provides enough mobility for even demanding agents to sort themselves.

## Implications for Beinhocker's Emergence Theme

These results illustrate Beinhocker's core argument about emergence:

1. **Simple rules, complex outcomes**: The agent rule is trivial (check neighbors, maybe move). The emergent spatial patterns are intricate and unpredictable in their specific geometry.

2. **No central planner**: Segregation arises without any agent intending or coordinating it. It is a pure collective phenomenon.

3. **Sensitivity to parameters**: Small changes in individual tolerance produce qualitatively different macro outcomes -- a hallmark of complex adaptive systems.

4. **Policy implications**: If mild preferences produce extreme segregation, then integration requires active intervention at the systemic level. Individual tolerance is necessary but not sufficient for collective integration.
