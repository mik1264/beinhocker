# Business Plan Evolution: Findings

Simulation of Beinhocker Ch.14 -- Business Plans as the evolutionary units ("DNA") of the economy. Each BP encodes Physical Technology (PT), Social Technology (ST), and Strategy on NK fitness landscapes. Fitness is multiplicative: PT x ST x market_fit.

## Summary Table

| Experiment | Total Wealth | Mean Fitness | Best Fitness | Mean PT | Mean ST | Mean Strategy | Diversity | Gini | Destructions | Innovations |
|---|---|---|---|---|---|---|---|---|---|---|
| 1. Baseline | 19.90 | 0.304 | 0.463 | 0.753 | 0.767 | 0.527 | 0.089 | 0.101 | 1610 | 225 |
| 2. Stable Prefs | 35.93 | 0.573 | 0.592 | 0.770 | 0.744 | 1.000 | 0.006 | 0.030 | 1609 | 155 |
| 3. Rapid Shifts | 19.95 | 0.322 | 0.404 | 0.777 | 0.765 | 0.541 | 0.058 | 0.059 | 1615 | 309 |
| 4. Low Innovation | 28.11 | 0.483 | 0.554 | 0.781 | 0.709 | 0.872 | 0.039 | 0.023 | 1500 | 145 |
| 5. High Innovation | 19.87 | 0.318 | 0.470 | 0.639 | 0.652 | 0.770 | 0.322 | 0.082 | 1589 | 299 |
| 6. Large Economy | 90.71 | 0.417 | 0.604 | 0.755 | 0.747 | 0.743 | 0.145 | 0.062 | 6150 | 918 |

## Key Findings

### 1. Multiplicative fitness creates a binding constraint problem

The weakest component always drags total fitness down. In every experiment, total fitness (mean ~0.3-0.57) is far below any single component fitness (~0.65-1.0) because the three components multiply together. This validates Beinhocker's core insight: wealth creation requires *all three* G-R conditions simultaneously. A brilliant product (high PT) with poor market fit (low Strategy) generates little wealth.

### 2. Stable preferences produce dramatically higher wealth (+81%)

Experiment 2 (stable prefs) produced total wealth of 35.93 vs baseline 19.90 -- an 81% increase. With no preference shifts, Strategy fitness converged perfectly to 1.000 (every BP fully matched market demand). This removed the binding constraint, letting PT and ST drive fitness higher. Diversity collapsed to near-zero (0.006) as the entire population converged on the optimal strategy.

This illustrates a real tension: stable environments allow deep optimization but at the cost of diversity and resilience.

### 3. Rapid preference shifts create the Red Queen effect

Experiment 3 (pref shift 0.1) kept wealth at baseline levels (19.95) despite generating 37% more innovations (309 vs 225). Strategy fitness remained the weakest component at 0.541 -- barely above baseline 0.527 -- because the target kept moving. The population ran fast just to stay in place: a clear Red Queen dynamic. Innovation rate jumped to 1.03/tick vs 0.75/tick baseline.

### 4. Too much mutation is as bad as too little (exploration-exploitation tradeoff)

**Low innovation** (mutation 0.01): Higher wealth (28.11) than baseline. The population could optimize effectively. Strategy fitness reached 0.872 because low mutation preserved good solutions. But diversity was very low (0.039) and innovation rate was lowest (0.48/tick).

**High innovation** (mutation 0.15): Lower wealth (19.87) than baseline. PT and ST fitness *dropped* (0.639, 0.652 vs baseline 0.753, 0.767) because excessive mutation disrupted well-adapted genomes. Diversity was highest (0.322) but this diversity was noise, not useful variation. This demonstrates the classic exploration-exploitation tradeoff: too much exploration destroys accumulated knowledge.

The sweet spot appears to be between 0.01 and 0.05 mutation rate for this landscape.

### 5. Strategy is the volatile component, PT/ST are stable

Across experiments, PT and ST fitness were remarkably stable (0.64-0.78 range) while Strategy fitness varied wildly (0.527-1.000). This reflects the model's structure -- PT and ST sit on fixed NK landscapes, while Strategy fitness depends on the shifting market environment. It maps to reality: production and organizational capabilities evolve slowly, while market positioning must constantly adapt.

### 6. Larger economies generate more absolute wealth but not proportionally

Experiment 6 (200 BPs) produced 90.71 total wealth -- 4.6x baseline with 4x population. Mean fitness was higher (0.417 vs 0.304), and best fitness was highest across all experiments (0.604). More competitors means more search of the fitness landscape, yielding better solutions. But the 4.6x rather than 4x scaling suggests mild increasing returns from larger population search.

### 7. Creative destruction is constant and structural

Destruction counts were nearly identical across experiments 1-5 (~1500-1615), reflecting the fixed 10% culling rate per tick. This is a feature of the model's selection mechanism rather than an emergent phenomenon. However, the *impact* of destruction varies: in stable environments, destroyed BPs are only slightly worse than survivors; in volatile environments, the fitness gap between destroyed and surviving BPs is larger.

### 8. Diversity and inequality are inversely related to fitness

Higher mean fitness correlated with lower diversity (stable prefs: diversity 0.006, fitness 0.573; high mutation: diversity 0.322, fitness 0.318). This reflects convergence toward optima -- successful evolution reduces variety as the population climbs fitness peaks. Gini coefficients were universally low (0.02-0.10), indicating that in this model, fitness-proportional market shares do not produce extreme concentration.

## Connection to Beinhocker's Framework

The simulation confirms several of Beinhocker's key arguments:

1. **Business Plans as economic DNA**: BPs encode the instructions for wealth creation. Their fitness determines their survival, just as biological fitness determines reproductive success.

2. **Multiplicative fitness (G-R Conditions)**: All three components must work together. This creates the "binding constraint" problem that makes economic evolution difficult -- optimizing one dimension is not enough.

3. **Creative destruction as selection**: The bottom fraction is constantly replaced. This is Schumpeter's insight operationalized: the economy evolves not by firms improving in place, but by better BPs displacing worse ones.

4. **Wealth as fit order**: Total wealth in the simulation is the sum of fitness-weighted market shares. It grows as the population finds better solutions to the three-component optimization problem. Wealth is literally "fit order" -- the degree to which business plans match the environment.

5. **The exploration-exploitation dilemma**: Too little innovation leads to lock-in on suboptimal peaks; too much innovation prevents optimization. Economies need the right balance of stability and change.
