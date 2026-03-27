# Sugarscape Experiments

## Theoretical Background

### The Model

Sugarscape was introduced by Joshua Epstein and Robert Axtell in their 1996 book *Growing Artificial Societies: Social Science from the Bottom Up*. It is one of the foundational agent-based models in computational social science.

The core model is deceptively simple:
- A 2D grid contains a renewable resource ("sugar") distributed in two mountain-like peaks
- Agents are scattered across the landscape, each with heterogeneous traits: vision range (how far they can see) and metabolism (how much sugar they consume per tick)
- Every tick, agents look in the four cardinal directions, move to the richest visible unoccupied cell, and eat the sugar there
- If an agent's sugar reserves hit zero, it dies

From these minimal rules, a rich set of social phenomena emerges.

### Beinhocker's Analysis

In *The Origin of Wealth* (2006), Eric Beinhocker uses Sugarscape as a central exhibit in his argument that economic complexity arises from simple evolutionary dynamics. Key points:

1. **Emergent inequality**: Starting from random initial conditions with identical rules, the wealth distribution rapidly becomes highly skewed. The Gini coefficient rises to 0.4-0.6, comparable to many real economies. No agent exploits another; inequality emerges purely from heterogeneous abilities interacting with an uneven resource landscape.

2. **Natural selection without genetics**: Over time, agents with high vision and low metabolism survive preferentially. The surviving population's average traits shift, demonstrating evolution through differential survival rather than reproduction.

3. **Carrying capacity**: The landscape can only support a certain number of agents. Population drops rapidly in early ticks as marginal agents starve, then stabilizes at the carrying capacity.

4. **Wealth distribution shape**: The resulting distribution is right-skewed with a long tail, resembling real-world wealth distributions (often Pareto or log-normal).

5. **Extensions breed complexity**: Adding trade produces emergent market prices. Adding reproduction produces demographic transitions. Adding cultural tags produces tribal conflict. Each extension demonstrates how simple local rules generate macroscopic social patterns.

---

## Experiment 1: Baseline Inequality Emergence

**Question**: How quickly does inequality emerge from equal starting conditions?

**Setup**:
```
python cli.py --agents 400 --ticks 500 --grid-size 50 --seed 42
```

**Parameters**:
- Grid: 50x50, standard two-peak landscape
- Agents: 400, vision 1-6, metabolism 1-4
- Regrowth: 1 per tick (gradual)
- No reproduction

**Metrics to track**:
- Gini coefficient over time
- Population over time
- Wealth distribution at ticks 10, 50, 100, 500

**Expected results**:
- Gini rises rapidly in first 50 ticks
- Population drops to ~60-70% of initial within 100 ticks
- Wealth distribution becomes right-skewed by tick 50

---

## Experiment 2: Vision vs Metabolism as Survival Determinants

**Question**: Which trait matters more for survival?

**Setup**: Run multiple scenarios varying trait ranges:

```
# Equal vision, varying metabolism
python cli.py --agents 400 --ticks 500 --vision-min 3 --vision-max 3 --metabolism-min 1 --metabolism-max 4 --seed 42

# Varying vision, equal metabolism
python cli.py --agents 400 --ticks 500 --vision-min 1 --vision-max 6 --metabolism-min 2 --metabolism-max 2 --seed 42

# Both varying (baseline)
python cli.py --agents 400 --ticks 500 --vision-min 1 --vision-max 6 --metabolism-min 1 --metabolism-max 4 --seed 42
```

**Metrics to track**:
- Final mean vision and metabolism of survivors
- Gini coefficient comparison
- Population survival rate

**Expected results**:
- Vision heterogeneity produces more inequality than metabolism heterogeneity
- When both vary, vision is the stronger predictor of survival
- Equal-trait scenarios produce lower Gini

---

## Experiment 3: Regrowth Rate Effects

**Question**: How does sugar regrowth rate affect population dynamics and inequality?

**Setup**:
```
# Instant regrowth
python cli.py --agents 400 --ticks 500 --regrowth-rate 0 --seed 42

# Slow regrowth (1/tick)
python cli.py --agents 400 --ticks 500 --regrowth-rate 1 --seed 42

# Fast regrowth (2/tick)
python cli.py --agents 400 --ticks 500 --regrowth-rate 2 --seed 42
```

**Metrics to track**:
- Population at equilibrium
- Gini coefficient at equilibrium
- Total sugar on grid over time

**Expected results**:
- Instant regrowth supports the largest population
- Slow regrowth produces the most inequality (competition is fierce)
- The relationship between regrowth and inequality is non-monotonic

---

## Experiment 4: Population Density Effects

**Question**: How does initial population density affect outcomes?

**Setup**:
```
python cli.py --agents 100 --ticks 500 --seed 42
python cli.py --agents 250 --ticks 500 --seed 42
python cli.py --agents 400 --ticks 500 --seed 42
python cli.py --agents 800 --ticks 500 --seed 42
python cli.py --agents 1200 --ticks 500 --seed 42
```

**Expected results**:
- Higher initial density leads to faster die-off
- Equilibrium population is relatively independent of initial population
- Inequality may peak at intermediate densities

---

## Experiment 5: Reproduction and Population Dynamics

**Question**: How does reproduction change the system dynamics?

**Setup**:
```
# Without reproduction
python cli.py --agents 400 --ticks 1000 --seed 42

# With reproduction
python cli.py --agents 400 --ticks 1000 --reproduction --reproduction-threshold 50 --seed 42

# With reproduction and age limit
python cli.py --agents 400 --ticks 1000 --reproduction --reproduction-threshold 50 --max-agent-age 100 --seed 42
```

**Metrics to track**:
- Population over time (does it stabilize, grow, or oscillate?)
- Gini coefficient trajectory
- Mean vision and metabolism of the population over time (evolutionary dynamics)

**Expected results**:
- Reproduction creates a demographic transition: initial die-off, then recovery
- With age limits, population may oscillate
- Natural selection effects are stronger with reproduction (traits are inherited with variation)
- Gini may be higher with reproduction due to inherited wealth

---

## Experiment 6: Pollution and Environmental Degradation

**Question**: How does pollution change agent behavior and outcomes?

**Setup**:
```
# Without pollution
python cli.py --agents 400 --ticks 500 --seed 42

# With pollution
python cli.py --agents 400 --ticks 500 --pollution --seed 42
```

**Expected results**:
- Pollution creates a "tragedy of the commons" dynamic
- Agents flee polluted areas, creating migration waves
- Population may decline more with pollution
- The sugar mountains become less valuable over time

---

## Experiment 7: Cultural Tags and Tribal Dynamics

**Question**: Do arbitrary cultural markers lead to spatial segregation?

**Setup**:
```
python cli.py --agents 400 --ticks 1000 --cultural-tags --seed 42
```

**Metrics to track**:
- Spatial distribution of cultural tribes
- Whether cultural boundaries align with geographic features

**Expected results**:
- Cultural groups tend to cluster spatially over time
- Cultural boundaries form near the saddle between the two sugar mountains
- Cultural homogenization occurs within local neighborhoods

---

## Analysis Framework

For each experiment, analyze:

1. **Time series**: Plot population, Gini, mean/median wealth over time
2. **Distributions**: Wealth histogram at key time points
3. **Spatial patterns**: Grid snapshots showing agent positions and sugar levels
4. **Trait evolution**: How survivor traits change over time
5. **Steady state**: Whether and when the system reaches equilibrium

### Key Metrics

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| Gini coefficient | Wealth inequality (0=equal, 1=max) | 0.3-0.6 |
| Carrying capacity | Equilibrium population | 40-80% of grid capacity |
| Mean survivor vision | Average vision of living agents | Biased high |
| Mean survivor metabolism | Average metabolism of living agents | Biased low |
| Wealth skewness | Asymmetry of wealth distribution | Positive (right-skewed) |

---

## References

- Epstein, J.M. & Axtell, R. (1996). *Growing Artificial Societies: Social Science from the Bottom Up*. MIT Press.
- Beinhocker, E.D. (2006). *The Origin of Wealth: Evolution, Complexity, and the Radical Remaking of Economics*. Harvard Business Press.
- Epstein, J.M. (2006). *Generative Social Science: Studies in Agent-Based Computational Modeling*. Princeton University Press.
- Axtell, R. (2001). "Zipf Distribution of U.S. Firm Sizes." *Science*, 293(5536), 1818-1820.
