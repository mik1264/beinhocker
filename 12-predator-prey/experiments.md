# Predator-Prey Experiments

## Lotka-Volterra / Beinhocker Ch 8 p.168

### What this demonstrates

The predator-prey system produces **endogenous oscillations** -- population cycles
that arise from internal dynamics, not external forcing. Beinhocker uses this as
a building block for the argument that economic systems are far-from-equilibrium:
they cycle, adapt, and restructure without ever reaching a static optimum.

### Two model variants

**A) Classic ODE (Lotka-Volterra):** Continuous differential equations solved via
RK4 integration. Produces perfectly periodic orbits that never damp or diverge.
The system has a conserved quantity -- trajectories trace closed loops in phase space.

**B) Spatial Agent-Based:** Discrete agents (rabbits and foxes) on a 2D toroidal grid
with grass regrowth. Produces noisy oscillations with the ever-present possibility of
stochastic extinction -- the gap between the deterministic ideal and messy reality.

---

## Experiment 1: Spatial Baseline (seed=42)
```
python3 cli.py --ticks 500 --seed 42
```
**Question:** Do stable population oscillations emerge from the spatial model with default parameters?

## Experiment 2: ODE Baseline
```
python3 cli.py --ode --ticks 500
```
**Question:** How do the deterministic ODE dynamics compare to the stochastic spatial model?

## Experiment 3: More Predators (50 initial)
```
python3 cli.py --ticks 500 --initial-predators 50 --seed 42
```
**Question:** Does starting with more predators destabilize the system or lead to faster extinction?

## Experiment 4: Fast Starvation (predator starve = 5)
```
python3 cli.py --ticks 500 --predator-starve 5 --seed 42
```
**Question:** When predators die quickly without food, does it prevent boom-bust collapses?

## Experiment 5: Prey Reproduce at 10% (vs 8% default)
```
python3 cli.py --ticks 500 --prey-reproduce 0.1 --seed 42
```
**Question:** How does higher prey fertility affect oscillation amplitude and period?

## Experiment 6: Larger World (100x100)
```
python3 cli.py --ticks 500 --grid-size 100 --seed 42
```
**Question:** Does a larger world with more space stabilize dynamics through spatial refugia?
