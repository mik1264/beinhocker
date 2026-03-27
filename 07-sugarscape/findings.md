# Sugarscape Simulation: Experiment Findings

## Model Overview

The Sugarscape model (Epstein & Axtell 1996, discussed in Beinhocker 2006) places
heterogeneous agents on a 2D grid with two Gaussian sugar peaks. Agents vary in
vision (how far they can see), metabolism (sugar consumed per tick), and initial
endowment. Each tick, agents scan the four cardinal directions up to their vision
range, move to the richest visible empty cell, gather its sugar, then pay their
metabolic cost. Agents with zero sugar die. Sugar regrows gradually each tick.

All experiments use seed 42 for reproducibility.

---

## Experiment 1: Baseline

**Command:** `python3 cli.py --ticks 200 --seed 42`
**Parameters:** 400 agents, 50x50 grid, vision 1-6, metabolism 1-4, regrowth 1/tick

### Results

| Metric | Value |
|---|---|
| Final population | 173 (43% survival) |
| Gini coefficient | 0.375 |
| Mean wealth | 211.6 |
| Median wealth | 204.0 |
| Mean vision (survivors) | 3.88 |
| Mean metabolism (survivors) | 1.51 |

### Emergent Behaviors

**Rapid initial die-off, then stabilization.** The population crashes from 400 to
~275 in the first 10 ticks (31% loss) as agents with poor trait combinations
(high metabolism, low vision) quickly deplete their endowments. The biggest
single-tick drop is 21 agents at tick 4. By tick 50 the population stabilizes at
~175, losing only 2 more agents over the remaining 150 ticks.

**Natural selection operates on both traits.** Survivors show a strong bias toward
low metabolism: 54% have metabolism=1, 42% have metabolism=2, and only 5% have
metabolism=3. None with metabolism=4 survive. Vision is also selected upward
(mean 3.88 vs initial expected mean of 3.5), with 45% of survivors having
vision 5 or 6.

**Moderate inequality emerges from homogeneous rules.** Despite identical
behavioral rules, the Gini coefficient rises from 0.22 (reflecting only
endowment variation) to 0.375 -- moderate inequality comparable to many
real-world pre-industrial economies. The gap between the top 10% (mean
wealth 408) and bottom 10% (mean wealth 10) is a 39:1 ratio, driven
almost entirely by trait differences.

**Trait-wealth correlations.** Wealth correlates negatively with metabolism
(r = -0.55) and positively with vision (r = 0.39). Metabolism matters more for
survival and wealth accumulation than vision does. The top 10% all have
metabolism=1 and mean vision=5.3; the bottom 10% average metabolism=1.65 and
vision=3.2.

---

## Experiment 2: High Population Density

**Command:** `python3 cli.py --ticks 200 --agents 800 --seed 42`
**Parameters:** 800 agents on 50x50 grid (0.32 agents/cell)

### Results

| Metric | Value |
|---|---|
| Final population | 289 (36% survival) |
| Gini coefficient | 0.395 |
| Mean wealth | 153.2 |
| Median wealth | 132.0 |
| Mean vision (survivors) | 3.80 |
| Mean metabolism (survivors) | 1.35 |

### Emergent Behaviors

**Intensified competition drives larger die-offs but higher carrying capacity.**
Starting with double the agents causes a more violent initial crash -- 53 agents
die in a single tick (tick 5), and the population drops from 800 to 481 by tick 10
(40% loss). However, the final population (289) is 67% higher than the baseline
(173), indicating the grid can support more agents when only the fittest survive
early crowding.

**Harsher selection pressure.** Mean survivor metabolism drops to 1.35 (vs 1.51
in baseline), indicating that competition weeds out marginal agents more
aggressively. The survival rate (36%) is lower than baseline (43%).

**Competition suppresses wealth accumulation.** Mean wealth (153) is 28% lower
than baseline (211) despite similar grid resources, because 289 agents share what
173 agents had to themselves. More agents survive but each is poorer.

**Slightly higher inequality.** Gini reaches 0.395 (vs 0.375 baseline). The
additional competitive pressure widens the gap between those near peaks and
those in sugar deserts.

---

## Experiment 3: Low Regrowth (Scarcity)

**Command:** Direct Python with regrowth_rate=0.25 (0.25 sugar/tick vs default 1)
**Parameters:** 400 agents, 50x50 grid, regrowth rate 0.25/tick

### Results

| Metric | Value |
|---|---|
| Final population | 110 (28% survival) |
| Gini coefficient | 0.263 |
| Mean wealth | 145.3 |
| Median wealth | 180.3 |
| Mean vision (survivors) | 3.90 |
| Mean metabolism (survivors) | 1.15 |

### Emergent Behaviors

**Scarcity causes deeper population collapse.** Only 28% of the initial population
survives (vs 43% at baseline). By tick 10 the population has already dropped to
220 (45% gone). The reduced regrowth means sugar on the grid drops to 1,316 at
tick 10 (vs 2,325 in baseline), creating a resource crisis.

**Extreme metabolic selection.** Mean survivor metabolism is just 1.15 -- nearly
the absolute minimum of 1. In a scarce environment, even metabolism=2 becomes a
serious liability. This is the most intense selection on metabolism of any
experiment.

**Lower inequality under scarcity.** Counterintuitively, the Gini coefficient
(0.263) is the lowest of any non-reproduction experiment. Scarcity acts as an
equalizer: there simply is not enough surplus sugar for anyone to accumulate great
wealth. The median (180) actually exceeds the mean (145), indicating a left-skewed
distribution where most survivors accumulate modestly and a few marginal agents
drag the average down.

**Grid sugar never fully recovers.** Total grid sugar stabilizes around 1,750
(vs ~2,490 at baseline). The slow regrowth rate means agents persistently deplete
sugar faster than it can regrow near the peaks, creating a permanent state of
partial depletion.

---

## Experiment 4: With Reproduction

**Command:** `python3 cli.py --ticks 300 --reproduction --seed 42`
**Parameters:** 400 initial agents, reproduction threshold=50, 300 ticks

### Results

| Metric | Value |
|---|---|
| Final population | 1,302 (326% of initial) |
| Gini coefficient | 0.148 |
| Mean wealth | 33.6 |
| Mean vision (survivors) | 4.63 |
| Mean metabolism (survivors) | 1.03 |
| Original agents surviving | 86 |
| Descendants | 1,216 |

### Emergent Behaviors

**Population explosion after initial die-off.** The early die-off is identical to
baseline (same seed, same initial agents). But starting around tick 25, surviving
agents begin accumulating enough sugar to reproduce (threshold=50). The population
reverses course: 231 at tick 25, 325 at tick 50, 646 at tick 100, 987 at tick 200,
and 1,302 at tick 300. Growth shows no sign of leveling off, suggesting the
system has not yet reached carrying capacity.

**Dramatic trait evolution through heredity.** This is the most striking emergent
behavior across all experiments. Children inherit parent traits with small random
mutations (+/-1). After 300 ticks of selection:
- **97.3% of agents have metabolism=1** (only 2.7% have metabolism=2, none higher)
- Vision distribution shifts strongly upward: 62% have vision 5 or 6 (vs ~33%
  initially)
- Descendants (mean vision 4.69) have higher vision than surviving originals
  (mean vision 3.83), demonstrating evolutionary improvement over generations

**Low inequality in a reproductive society.** Gini drops to 0.148 -- the lowest of
any experiment. Reproduction acts as a wealth-equalizing mechanism because
reproducing agents split their sugar in half. No agent can accumulate runaway
wealth because exceeding the threshold triggers reproduction and a 50% wealth
haircut.

**Resource pressure from growth.** Total grid sugar declines steadily from 2,978
to 1,745 as the growing population increasingly outstrips regrowth. Mean wealth
stabilizes around 33-34 (just below the reproduction threshold of 50), indicating
a Malthusian equilibrium where population growth consumes any surplus.

---

## Experiment 5: Large Grid

**Command:** `python3 cli.py --ticks 200 --grid-size 100 --agents 800 --seed 42`
**Parameters:** 800 agents on 100x100 grid (0.08 agents/cell)

### Results

| Metric | Value |
|---|---|
| Final population | 129 (16% survival) |
| Gini coefficient | 0.376 |
| Mean wealth | 225.9 |
| Mean vision (survivors) | 4.14 |
| Mean metabolism (survivors) | 1.71 |

### Emergent Behaviors

**Catastrophic die-off from spatial mismatch.** This experiment produces the lowest
survival rate (16%) because the sugar peaks remain at their default positions
(15,15) and (35,35) -- both in the lower-left quadrant of the 100x100 grid. The
remaining 75% of the grid is a sugar desert. Agents placed far from the peaks have
no viable migration path (vision maxes out at 6 cells). The biggest single-tick
drop is 82 agents at tick 3 -- agents placed in the desert with high metabolism
die almost immediately.

**Complete spatial concentration.** 100% of the 129 survivors occupy the lower-left
quadrant (x<50, y<50). Every single survivor is within 18 cells of a sugar peak,
with a mean distance of only 6.5 cells. This quadrant contains 98.7% of the
grid's total sugar capacity. Agents in the other three quadrants go extinct.

**Less metabolic selection than expected.** Mean metabolism (1.71) is higher than
baseline (1.51), which seems counterintuitive. The explanation: location matters
more than traits on the large grid. An agent with metabolism=3 but placed near
a peak survives, while an agent with metabolism=1 placed in the desert does not.
Geography dominates genetics.

**Higher mean wealth from lower density.** Survivors average 225.9 sugar (vs 211.6
baseline) because only 129 agents share the peak resources, compared to 173 in
baseline. Lower competition at the peaks means richer survivors.

---

## Experiment 6: Extreme Inequality Setup

**Command:** `python3 cli.py --ticks 200 --vision-max 10 --metabolism-max 6 --seed 42`
**Parameters:** Vision 1-10, metabolism 1-6 (wider trait ranges)

### Results

| Metric | Value |
|---|---|
| Final population | 132 (33% survival) |
| Gini coefficient | 0.308 |
| Mean wealth | 247.8 |
| Mean vision (survivors) | 6.44 |
| Mean metabolism (survivors) | 1.61 |

### Emergent Behaviors

**Wider trait range causes faster, more brutal selection.** Survival drops to 33%
(vs 43% baseline). Agents with metabolism 4-6 die almost immediately -- no agent
with metabolism above 3 survives to tick 200. The biggest single-tick drop (33
agents at tick 3) happens as high-metabolism agents exhaust their endowment. By
tick 10, 51% of the population is already dead.

**Vision ceiling effect: more vision helps, but with diminishing returns.** Mean
survivor vision is 6.44 -- higher than the baseline maximum of 6. However,
vision shows a weaker wealth correlation (r=0.22) than metabolism (r=-0.83).
The top 10% have mean vision=9.0 and metabolism=1.0 (the ideal combination),
but many agents with modest vision (3-5) survive if their metabolism is low
enough.

**Metabolism is the dominant survival trait.** The wealth-metabolism correlation
(r=-0.83) is the strongest of any experiment. In the extreme-range setup,
metabolism variation is the primary axis of selection. 49% of survivors have
metabolism=1, 40% have metabolism=2, and only 11% have metabolism=3. None with
metabolism 4-6 survive.

**Paradoxically lower Gini than baseline.** Despite wider trait ranges, the Gini
(0.308) is lower than baseline (0.375). The explanation: brutal selection
eliminates the would-be poor agents entirely rather than leaving them alive but
destitute. Dead agents do not count in inequality statistics. The survivors are
a more homogeneous group of "winners" with similar trait profiles.

---

## Cross-Experiment Synthesis

### Key Findings

1. **Inequality emerges from simple rules.** Even with identical behavioral rules
   and random initial conditions, Gini coefficients in the range 0.26-0.40
   arise naturally -- comparable to real pre-industrial societies. No agent
   is "programmed" to be rich or poor; outcomes emerge from the interaction of
   heterogeneous traits with a spatially structured resource landscape.

2. **Metabolism matters more than vision.** Across all experiments, low metabolism
   is the single most important survival trait. The wealth-metabolism correlation
   is consistently stronger (r = -0.55 to -0.83) than the wealth-vision
   correlation (r = 0.22 to 0.39). This makes intuitive sense: reducing costs
   by 1 unit per tick has a compounding advantage that exceeds the benefit of
   seeing 1 cell further.

3. **Selection pressure varies by environment.**

   | Experiment | Survival | Survivor Mean Metabolism | Survivor Mean Vision |
   |---|---|---|---|
   | Baseline | 43% | 1.51 | 3.88 |
   | High Density | 36% | 1.35 | 3.80 |
   | Low Regrowth | 28% | 1.15 | 3.90 |
   | Reproduction | 326% | 1.03 | 4.63 |
   | Large Grid | 16% | 1.71 | 4.14 |
   | Extreme Inequality | 33% | 1.61 | 6.44 |

   Scarcity (low regrowth) produces the strongest metabolic selection. Reproduction
   allows cumulative evolutionary refinement to near-optimal trait values.

4. **Geography can dominate genetics.** The large grid experiment shows that spatial
   position -- proximity to resources -- can matter more than individual traits.
   All survivors cluster within 18 cells of a sugar peak regardless of traits.

5. **Reproduction fundamentally changes system dynamics.** It is the only experiment
   where population grows, the only one with Gini below 0.20, and the only one
   where traits evolve cumulatively across generations. The wealth-splitting
   reproduction mechanism creates a natural limit on inequality while population
   growth creates Malthusian resource pressure.

6. **Scarcity equalizes; competition polarizes.** Low regrowth produces the lowest
   Gini (0.263) in non-reproductive runs because there is not enough surplus
   to create wealth disparities. High density produces the highest Gini (0.395)
   because intensified competition amplifies small trait advantages.

7. **The dead are invisible to inequality measures.** The "extreme inequality"
   setup actually produces lower measured inequality than baseline because
   brutal selection kills the would-be poor rather than leaving them alive and
   destitute. This is a cautionary note about interpreting Gini coefficients --
   they only measure inequality among the living.

### Connection to Beinhocker

These results illustrate several themes from "The Origin of Wealth":

- **Complexity economics:** Simple agent rules generate rich emergent macro-patterns
  (skewed wealth distributions, natural selection, spatial clustering) that cannot
  be predicted from the rules alone.
- **Out-of-equilibrium dynamics:** The system never reaches a static equilibrium.
  Population, wealth distribution, and trait composition shift continuously,
  especially with reproduction enabled.
- **Evolution as an economic force:** The reproduction experiment demonstrates how
  differential survival and heredity with variation produce directional change in
  population traits -- a purely economic analog of biological natural selection.
- **Endogenous inequality:** Wealth inequality is not imposed externally but
  emerges endogenously from agent heterogeneity interacting with resource
  geography, a key insight of the complexity economics perspective.
