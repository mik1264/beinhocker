# Predator-Prey Simulation Findings

## Model Parameters (final tuned defaults)

**Spatial agent-based model:**
- Grid: 50x50 toroidal
- Initial: 200 prey, 30 predators
- Grass regrow: 8 ticks
- Prey: gain 5 energy from grass, 8% reproduce probability
- Predators: gain 5 energy from eating prey, 2% reproduce probability, initial max energy 10
- Predator detection radius: 2 (Manhattan distance)

**ODE model:**
- alpha=1.0, beta=0.1, delta=0.075, gamma=1.5
- Initial: 40 prey, 9 predators
- RK4 integration with dt=0.01

---

## Experiment 1: Spatial Baseline (seed=42)
```
python3 cli.py --ticks 500 --seed 42
```

**Result:** Sustained oscillations through all 500 ticks.
- Prey range: 35 to 1,075
- Predator range: 15 to 138
- Estimated oscillation period: ~56 ticks
- Grass coverage: 22% to 100%
- Final state: 607 prey, 50 predators, 46% grass

**Observation:** Classic boom-bust cycling. Prey boom when predators are scarce, predators
boom when prey are abundant, then prey crash under predation pressure, predators decline
from starvation, and the cycle repeats. The cycle is not perfectly periodic -- amplitude
and period vary from cycle to cycle due to stochastic effects and spatial heterogeneity.

---

## Experiment 2: ODE Baseline
```
python3 cli.py --ode --ticks 500
```

**Result:** Perfectly periodic orbits, no damping or extinction.
- Prey range: 8.08 to 40.14
- Predator range: 3.17 to 22.97
- Oscillation period: 5.48 time units (perfectly constant)

**Observation:** The ODE traces closed loops in phase space indefinitely. This is a
conserved system -- the quantity V = delta*x - gamma*ln(x) + beta*y - alpha*ln(y) is
constant along trajectories. The RK4 integrator preserves this conserved quantity well
over 500 time units. This is the idealized world of traditional equilibrium analysis:
deterministic, no extinctions possible, perfectly predictable.

---

## Experiment 3: More Predators (initial=50, seed=42)
```
python3 cli.py --ticks 500 --initial-predators 50 --seed 42
```

**Result:** Sustained oscillations, slightly more volatile early dynamics.
- Prey range: 17 to 1,173
- Predator range: 14 to 147
- Estimated period: ~37 ticks
- Final state: 41 prey, 41 predators (caught at a trough)

**Observation:** Starting with more predators causes the initial crash to be faster and
deeper (prey bottomed at 17 vs 35 in baseline). But the system recovers -- the extra
predators cannot sustain themselves and starve down. The long-run dynamics are similar
to baseline. The initial condition affects the transient but not the qualitative behavior.
This is consistent with the ODE model where all trajectories on the same energy level
trace the same orbit.

---

## Experiment 4: Fast Starvation (predator_starve=5, seed=42)
```
python3 cli.py --ticks 500 --predator-starve 5 --seed 42
```

**Result:** Dramatic near-extinction of predators, then recovery.
- Prey range: 2 to 1,260
- Predator range: 1 to 158
- Prey peaked at 1,260 (much higher than baseline's 1,075)
- Predators nearly went extinct (min=1 around tick 250-300)
- Period: ~20 ticks (shorter cycle)

**Observation:** When predators starve quickly, they cannot sustain population booms.
The prey-predator ratio shifts dramatically toward prey dominance. Predators dropped to
just 1 individual -- any further stochastic fluctuation would have caused extinction.
This demonstrates the fragility of the spatial model vs the ODE: in the ODE, predators
can be arbitrarily close to zero and still recover perfectly. In the agent model, when
you're at 1 predator, one unlucky tick kills the species forever.

---

## Experiment 5: Prey Reproduce at 0.10 (seed=42)
```
python3 cli.py --ticks 500 --prey-reproduce 0.1 --seed 42
```

**Result:** Faster oscillations with higher prey peaks.
- Prey range: 57 to 1,010
- Predator range: 22 to 161
- Period: ~22 ticks (faster than baseline's ~56)
- More regular-looking cycles

**Observation:** Note that 0.10 is actually *higher* than the default of 0.08, so this
tests faster, not slower, prey reproduction. The higher prey growth rate means prey
recover from crashes faster, shortening the oscillation period. Predator peaks are
slightly higher (161 vs 138 in baseline) because more prey means more food. The prey
minimum is higher (57 vs 35), suggesting the system is more resilient to extinction
when prey reproduce faster -- they bounce back before predators can finish them off.

---

## Experiment 6: Larger World (100x100, seed=42)
```
python3 cli.py --ticks 500 --grid-size 100 --seed 42
```

**Result:** Much larger populations, slower initial transient, sustained dynamics.
- Prey range: 200 to 5,582
- Predator range: 8 to 464
- Grass coverage minimum: 15%
- Final: 2,952 prey, 247 predators

**Observation:** The 100x100 grid (4x the area of 50x50) supports much larger populations.
Starting with only 200 prey in 10,000 cells means extremely low density, so prey boom
unchecked for ~150 ticks before predators catch up. The larger world provides more spatial
refugia -- prey in one corner can grow while predators are concentrated in another. This
makes extinctions much less likely and supports the law of large numbers: with thousands
of individuals, stochastic fluctuations average out. The dynamics become more ODE-like.

---

## Cross-Cutting Findings

### 1. ODE vs Agent-Based: The Extinction Gap
The most striking finding is the qualitative difference between the two models.
The ODE guarantees eternal oscillation -- populations can approach but never reach zero.
The agent-based model can and does produce extinctions, especially when:
- The grid is small (stochastic effects dominate)
- Predators are too efficient (prey crash below recovery threshold)
- One species drops to single digits (demographic stochasticity)

This validates Beinhocker's argument: **the deterministic equilibrium model misses
the most important feature of real systems -- they can collapse**.

### 2. Spatial Refugia Stabilize Dynamics
Larger grids produce more stable dynamics because:
- Spatial separation prevents predators from consuming all prey simultaneously
- Local extinctions can be recolonized from neighboring patches
- The effective population is larger, reducing demographic stochasticity

This is analogous to Beinhocker's point about economic diversity as resilience.

### 3. Endogenous Oscillations Need No External Driver
In both models, the cycles are entirely self-generated. No seasonal forcing, no
random shocks, no exogenous parameter changes. The oscillation period, amplitude,
and phase all emerge from the interaction rules alone. This is the core insight:
**complex adaptive systems generate their own dynamics**.

### 4. Parameter Sensitivity is Asymmetric
The system is much more sensitive to predator parameters than prey parameters:
- Predator starvation rate: changing from 10 to 5 nearly caused extinction
- Prey reproduction rate: changing from 0.08 to 0.10 only shortened the period
- Initial conditions: doubling predators barely affected long-run behavior

This asymmetry arises because predators sit at the top of the food chain --
perturbations propagate upward (bottom-up control).

### 5. Oscillation Period Scales with Parameters
- Baseline: ~56 ticks
- More predators: ~37 ticks (faster predation -> faster cycles)
- Fast starvation: ~20 ticks (predators die quickly -> shorter bust phase)
- Higher prey reproduction: ~22 ticks (prey recover faster -> shorter recovery phase)
