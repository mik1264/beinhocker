# Integrated Economy — Experiments

## Integration Approach

This simulation links four foundational models from complexity economics into a single coherent system:

1. **SFI Artificial Stock Market** (Arthur et al., 1997) — Stock prices emerge from sentiment, fundamentals, and contagion rather than equilibrium pricing.
2. **Beer Distribution Game** (Sterman, 1989) — Supply chain dynamics with bullwhip amplification driven by anchor-and-adjust ordering heuristics.
3. **Punctuated Equilibrium** (Jain & Krishna, 2002) — Firm failures cascade through a dependency network, creating ecosystem-level creative destruction.
4. **Rigids vs Flexibles** (Harrington, 1999) — Organizational composition determines adaptive capacity: rigid firms are efficient but fragile, flexible firms adapt but at higher steady-state cost.

### Coupling Channels

- **Supply chain -> Market**: Backlogs and inventory disruptions reduce firm output, depressing fundamental value and stock prices.
- **Market -> Ecosystem**: Stock price collapses reduce firm health, potentially triggering cascade failures through the dependency network.
- **Ecosystem -> Supply chain**: When a supplier fails, its dependents lose a supply source, amplifying chain disruptions.
- **Organization -> All**: Flexible firms smooth supply chain orders (reducing bullwhip), adopt new technology faster, and recover from crises more quickly.
- **Technology -> Ecosystem**: Technology disruptions instantly devalue firms on old paradigms, creating a fitness shock analogous to the Jain-Krishna model.

## Planned Experiments

### Experiment 1: Baseline Characterization
- **Goal**: Characterize the economy under normal conditions (no scheduled shocks).
- **Metrics**: GDP distribution, market index volatility, Gini dynamics, endogenous cascade statistics.
- **Question**: Does the integrated economy self-organize to a critical state even without external shocks?

### Experiment 2: Bullwhip Amplification Through Financial Contagion
- **Goal**: Measure how a supply chain demand shock propagates into the financial system.
- **Scenario**: Supply shock at t=100 (2.5x demand spike), normalization at t=150.
- **Metrics**: Peak bullwhip ratio, market index drawdown, cascade size triggered by the shock.
- **Question**: Does financial contagion amplify the bullwhip effect beyond what the Beer Game alone predicts?

### Experiment 3: Technology Disruption and Creative Destruction
- **Goal**: Test whether organizational flexibility predicts survival after a technology disruption.
- **Scenario**: Tech disruption at t=150.
- **Metrics**: Survival rate by flex fraction quartile, time to technology adoption, GDP recovery time.
- **Question**: Is there a critical threshold of flexibility that determines firm survival?

### Experiment 4: Cascading Crisis (Market Crash Scenario)
- **Goal**: Study the interaction of multiple simultaneous stresses.
- **Scenario**: Supply shock (t=80) + market panic (t=120) + tech disruption (t=160).
- **Metrics**: Peak unemployment, total cascade size, recovery trajectory, Gini at peak crisis.
- **Question**: Are combined shocks superadditive in their damage (i.e., worse than the sum of individual shocks)?

### Experiment 5: Resilience Sweep
- **Goal**: Identify the optimal organizational composition for long-run resilience.
- **Method**: Sweep initial flexible fraction from 0% to 100% under the stress test scenario.
- **Metrics**: Mean GDP, peak unemployment, total cascade size, time in crisis phases.
- **Question**: Is there an optimal rigid/flexible mix, and does it match the Harrington model's prediction?

### Experiment 6: Network Topology and Systemic Risk
- **Goal**: Test how dependency network density affects cascade dynamics.
- **Method**: Sweep dependency probability from 0.02 to 0.20.
- **Metrics**: Mean cascade size, max cascade size, GDP volatility, recovery time.
- **Question**: Is there a critical connectivity threshold where the economy transitions from resilient to fragile?

### Experiment 7: Path Dependence
- **Goal**: Test whether the same shock produces different outcomes depending on the economy's history.
- **Method**: Run the supply shock scenario with different random seeds; analyze variance in outcomes.
- **Metrics**: Distribution of GDP paths, cascade sizes, and recovery times across seeds.
- **Question**: How much of macroeconomic dynamics is path-dependent vs. structurally determined?

## Running Experiments

```bash
# Baseline
python cli.py --scenario normal --ticks 500 --seed 42 --json exp1_baseline.json

# Supply shock
python cli.py --scenario supply_shock --ticks 500 --seed 42 --json exp2_supply.json

# Tech disruption
python cli.py --scenario tech_disruption --ticks 500 --seed 42 --json exp3_tech.json

# Market crash
python cli.py --scenario market_crash --ticks 500 --seed 42 --json exp4_crash.json

# Stress test
python cli.py --scenario stress_test --ticks 500 --seed 42 --json exp5_stress.json
```
