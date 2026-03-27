# Prisoner's Dilemma / Evolution of Cooperation: Experiments

## Theoretical Background

### Axelrod's Tournaments (1980-1984)

Robert Axelrod conducted two landmark computer tournaments to answer a simple but profound question: **In a world of self-interested agents, can cooperation evolve?**

Game theorists submitted strategies for an iterated Prisoner's Dilemma. Each strategy was paired against every other in a round-robin tournament of 200 rounds. The results stunned the field:

- **Tit-for-Tat (TFT)** won both tournaments despite never "beating" any individual opponent
- TFT succeeds by being **nice** (cooperates first), **retaliatory** (punishes defection), **forgiving** (returns to cooperation), and **clear** (opponents can model it)
- "Mean" strategies that defect first consistently did worse in the long run
- The simplest strategy was the best -- complexity did not pay

### Beinhocker's Analysis (The Origin of Wealth, Ch. 9)

Beinhocker uses Axelrod's work to make several key points about evolutionary economics:

1. **Cooperation is not a mystery requiring altruism** -- it emerges naturally from repeated interactions and evolutionary selection
2. **The "shadow of the future"** makes cooperation rational: if you expect to interact again, defection is short-sighted
3. **Spatial structure matters**: when agents interact locally (not globally), cooperators can form clusters that resist invasion
4. **Noise and forgiveness**: in a noisy world, pure TFT can fall into retaliatory spirals. Generous TFT and Pavlov are more robust
5. **The ecology of strategies**: no single strategy dominates forever -- evolution produces a shifting landscape of competing approaches

### Nowak & May (1992): Spatial Chaos

Nowak and May showed that placing agents on a grid with local interactions fundamentally changes the dynamics:

- Cooperators survive by clustering together, earning mutual cooperation payoffs
- Defectors can only exploit cooperators at cluster borders
- The result is complex, often chaotic spatial patterns that never reach equilibrium
- Even simple strategies produce kaleidoscopic dynamics on a grid

### The Payoff Matrix

Standard Prisoner's Dilemma payoffs:

|           | Opponent: C | Opponent: D |
|-----------|-------------|-------------|
| **You: C** | R = 3      | S = 0       |
| **You: D** | T = 5      | P = 1       |

Conditions: T > R > P > S and 2R > T + S

- **T (Temptation)**: The reward for defecting against a cooperator
- **R (Reward)**: Mutual cooperation payoff
- **P (Punishment)**: Mutual defection payoff
- **S (Sucker)**: The cost of cooperating against a defector

---

## Planned Experiments

### Experiment 1: Baseline Spatial Dynamics

**Question**: How do the seven strategies interact on a spatial grid with default parameters?

**Parameters**:
- Grid: 50x50, Moore neighborhood
- Rounds/match: 5
- Noise: 0.0
- Mutation: 0.001
- Payoff: T=5, R=3, P=1, S=0
- Generations: 500

**Expected**: TFT and Pavlov should form cooperative clusters. AllD should initially spread but then be contained. AllC should be vulnerable at borders.

**Results**: _(to be filled in)_

---

### Experiment 2: Effect of Noise

**Question**: How does execution error (noise) affect the evolution of cooperation?

**Parameters**: Same as baseline but vary noise from 0.0 to 0.10

**Hypothesis**: Low noise should favor TFT. Higher noise should favor Generous TFT and Pavlov, which are more forgiving and avoid retaliatory spirals.

| Noise | Final Coop Rate | Dominant Strategy | Notes |
|-------|----------------|-------------------|-------|
| 0.00  |                |                   |       |
| 0.01  |                |                   |       |
| 0.02  |                |                   |       |
| 0.05  |                |                   |       |
| 0.10  |                |                   |       |

---

### Experiment 3: Spatial vs. Tournament

**Question**: Does spatial structure promote cooperation compared to well-mixed (tournament) populations?

**Parameters**:
- Spatial: 50x50 grid, Moore neighborhood
- Tournament: 100 agents, round-robin
- Both: noise=0.01, mutation=0.001, 300 generations

**Hypothesis**: Spatial structure should sustain higher cooperation rates because cooperators can cluster.

**Results**: _(to be filled in)_

---

### Experiment 4: Payoff Matrix Sensitivity

**Question**: How sensitive is cooperation to the payoff matrix?

**Parameters**: Vary T (temptation) while keeping R=3, P=1, S=0

| T value | T-R Gap | Final Coop Rate | Dominant Strategy |
|---------|---------|-----------------|-------------------|
| 3.5     | 0.5     |                 |                   |
| 4.0     | 1.0     |                 |                   |
| 5.0     | 2.0     |                 |                   |
| 6.0     | 3.0     |                 |                   |
| 8.0     | 5.0     |                 |                   |

**Hypothesis**: As T increases, defection becomes more tempting and cooperation should decline. There may be a critical threshold.

---

### Experiment 5: Mutation Rate Effects

**Question**: How does mutation rate affect long-term strategy diversity and cooperation?

**Parameters**: Vary mutation from 0.0 to 0.05

**Hypothesis**: Zero mutation leads to fixation (one strategy wins forever). Moderate mutation maintains diversity. High mutation is disruptive.

**Results**: _(to be filled in)_

---

### Experiment 6: Invasion Resistance

**Question**: Can a small cluster of cooperators invade an all-defector population?

**Setup**:
- Start with 95% AllD, 5% TFT (or Pavlov)
- Spatial grid, 50x50
- Observe whether the cooperative cluster expands or contracts

**This tests**: Beinhocker's claim that cooperation can emerge from a hostile environment through cluster formation.

**Results**: _(to be filled in)_

---

### Experiment 7: Von Neumann vs. Moore Neighborhoods

**Question**: Does the number of neighbors (4 vs. 8) affect cooperation dynamics?

**Parameters**: Compare Von Neumann (4 neighbors) with Moore (8 neighbors)

**Hypothesis**: Fewer neighbors should favor cooperation (smaller borders to defend, more intra-cluster interactions).

**Results**: _(to be filled in)_

---

### Experiment 8: Rounds Per Match

**Question**: How does the "shadow of the future" (match length) affect cooperation?

**Parameters**: Vary rounds from 1 to 50

| Rounds | Final Coop Rate | Notes |
|--------|----------------|-------|
| 1      |                | Essentially one-shot PD |
| 2      |                |       |
| 5      |                |       |
| 10     |                |       |
| 20     |                |       |
| 50     |                |       |

**Hypothesis**: More rounds should favor cooperation, as conditional strategies like TFT have more time to establish reciprocal relationships.

---

## Key Metrics to Track

1. **Cooperation rate**: Fraction of all actions that are cooperative
2. **Strategy population fractions**: How each strategy's share evolves
3. **Average payoff**: Population-level welfare measure
4. **Shannon entropy**: Strategy diversity measure
5. **Spatial patterns**: Cluster formation, border dynamics, chaos vs. order
6. **Time to fixation**: How quickly one strategy dominates (if ever)

## Running Experiments

```bash
# Baseline spatial
python cli.py --spatial --grid-size 50 --generations 500 --seed 42 --output exp1_baseline.csv

# Noise sweep
for noise in 0.0 0.01 0.02 0.05 0.10; do
  python cli.py --spatial --noise $noise --generations 300 --seed 42 --output exp2_noise_${noise}.csv
done

# Spatial vs tournament
python cli.py --spatial --grid-size 50 --noise 0.01 --generations 300 --seed 42 --output exp3_spatial.csv
python cli.py --tournament --population 100 --noise 0.01 --generations 300 --seed 42 --output exp3_tournament.csv

# Payoff sensitivity
for t in 3.5 4.0 5.0 6.0 8.0; do
  python cli.py --spatial --payoff-T $t --generations 300 --seed 42 --output exp4_T_${t}.csv
done
```
