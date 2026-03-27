# Integrated Economy Simulation: Experiment Findings

## Model Overview

The simulation integrates four interacting sub-models from Beinhocker's *Origin of Wealth*:

- **Supply Chain** (Beer Game): Sterman's anchor-and-adjust ordering with bullwhip amplification across 4 echelons
- **Stock Market** (SFI model): Fundamental-based pricing with sentiment momentum and contagion
- **Ecosystem Dynamics** (Punctuated Equilibrium): Dependency network with cascade failures
- **Organizational Adaptation** (Rigids vs Flexibles): Flexibility-rigidity tradeoff under stability vs crisis

Each firm has composite health (25% supply chain + 25% org fitness + 30% tech fitness + 20% stock price). Firms fail when health drops below the cascade threshold (0.4), and failures propagate through the dependency network. Failed firms respawn at 2% probability per tick.

All experiments: 40 firms (unless noted), seed=42, dependency probability 0.08.

---

## Experiment 1: Normal Operations (200 ticks)

**Command:** `python3 cli.py --scenario normal --ticks 200 --seed 42`

### Results

| Metric | Value |
|---|---|
| Mean GDP | 11.20 |
| GDP range | 11.02 -- 11.56 |
| Market index | 97.35 -> 22.03 (converges ~21-22) |
| Gini coefficient | 0.066 -> 0.696 |
| Firms alive | 40/40 (no failures) |
| Cascades | 0 |
| Tech disruptions | 1 (stochastic) |
| Final phase | normal |

### Key Observations

1. **GDP is remarkably stable.** Standard deviation of only 0.053 over 200 ticks. The supply chain finds equilibrium quickly and holds it. This confirms the Beer Game steady state -- without exogenous shocks, Sterman ordering converges.

2. **Market index collapses from ~97 to ~21.** This is the most striking "normal" behavior. The stock price systematically declines because of a structural feature: initial stock prices average ~100, but the fundamental value formula (output_ratio * sqrt(tech * org_adjusted) * 100) produces values well below 100 at equilibrium. The market converges to fundamentals via mean reversion, creating a long bear market even without shocks.

3. **Gini rises steadily from 0.07 to 0.70.** Inequality grows under normal operations because idiosyncratic noise in stock prices compounds over time. Without shocks, there is no equalizing destruction -- early winners accumulate advantage.

4. **Flexibility floor reached.** The flexible fraction drops from 0.395 to the model's floor of 0.200 by tick 50 and stays there. In stable conditions, rigidity dominates because of the efficiency bonus (+0.15). This is the "peacetime drift toward rigidity" that Beinhocker describes.

5. **One stochastic tech disruption** occurred (prob 0.005/tick, so ~1 expected per 200 ticks) but had no visible impact on GDP or firm survival. In stable conditions, the disruption is absorbed.

---

## Experiment 2: Supply Shock (200 ticks)

**Command:** `python3 cli.py --scenario supply_shock --ticks 200 --seed 42`

Demand spike to 2.5x at tick 100, normalizes at tick 150.

### Results

| Metric | Value |
|---|---|
| Mean GDP | 15.42 |
| Peak GDP | 32.02 (tick ~103) |
| Trough GDP | 10.00 (tick ~151) |
| Firms alive | 40/40 throughout |
| Cascades | 0 |
| Phase transitions | supply_shock -> recovery (t=120) -> normal (t=150) |

### Key Observations

1. **The bullwhip effect is clearly visible.** When demand jumps 2.5x at tick 100, GDP surges from 11.2 to 26.5 in one tick, overshoots to 32.0 by tick 103, then oscillates downward. The immediate GDP jump is 2.4x -- close to the 2.5x demand multiplier -- showing downstream firms pass through demand almost instantly.

2. **Demand normalization causes undershoot.** When demand resets at tick 150, GDP drops abruptly from 28.1 to 10.8, then to 10.0 -- briefly undershooting the original 11.2. This is the classic bullwhip "whiplash": firms built up inventory and supply lines during the shock, and now over-correct downward.

3. **Recovery takes ~15 ticks.** GDP returns to 11.2 by approximately tick 165, about 15 ticks after normalization. The exponential smoothing (theta=0.3) determines this recovery speed.

4. **No firm failures despite a major shock.** The 2.5x demand shock is absorbed entirely by the supply chain mechanism -- inventories buffer it, and health never drops below the cascade threshold. This suggests supply-side shocks alone are insufficient to trigger cascading failures in this economy.

5. **Market is surprisingly unresponsive.** The market index barely moves during the supply shock (from ~23 to ~24 at peak). This is because stock prices track *output* (which rises with demand) and *fundamentals* (which depend on output ratio, capped at 2.0). The market sees higher output as positive, masking the underlying stress buildup.

6. **Supply chain stress is constant at 0.25.** The stress metric (fraction of firms with backlog > 0.5 * expected demand) stays at 0.25 throughout, including during the shock. This suggests the stress metric is measuring baseline oscillation rather than shock-induced disruption.

---

## Experiment 3: Technology Disruption (200 ticks)

**Command:** `python3 cli.py --scenario tech_disruption --ticks 200 --seed 42`

Major tech disruption forced at tick 150.

### Results

| Metric | Value |
|---|---|
| Mean GDP | 11.20 |
| GDP range | 11.02 -- 11.56 |
| Firms alive | 40/40 |
| Cascades | 0 |
| Tech disruptions | 2 (1 forced + 1 stochastic) |
| Final market index | 19.28 (vs 22.03 normal) |
| Final flex fraction | 0.641 (vs 0.200 normal) |

### Key Observations

1. **Tech disruption has zero GDP impact.** This is surprising. The forced disruption at tick 150 drops tech fitness (severity 0.6), but since tech fitness has weight 0.30 in the health formula and the cascade threshold is 0.40, firms absorb the shock without failing. GDP stays flat at 11.2 throughout.

2. **The real effect is on stock prices.** Final market index is 19.28 vs 22.03 under normal conditions -- a 12.5% lower valuation. The tech disruption damages fundamentals through the quality multiplier (sqrt(tech * org)), depressing prices.

3. **Organizational response is dramatic.** The flexibility fraction jumps from 0.200 (rigid equilibrium) to 0.641 after the disruption. This is the key emergent behavior: tech disruption triggers crisis mode, which causes flexibility to increase (rigid leaders fail, flexible leaders emerge). This matches Beinhocker's thesis that disruption selects for organizational flexibility.

4. **No creative destruction occurred.** Despite the tech disruption, no firms actually died. The disruption severity (0.6) reduces tech fitness to ~0.32 for generation-0 firms (from ~0.80), but composite health stays above the 0.40 threshold because supply chain and org fitness components provide buffer.

5. **Tech fitness recovers within ~50 ticks.** By tick 200 (50 ticks post-disruption), mean tech fitness is back to 0.805 -- essentially recovered. Flexible firms adopt new tech at speed 0.15, rigid at 0.03. With the post-disruption flex fraction of 0.64, the blended adoption speed is ~0.107, meaning ~90% recovery in 20-25 ticks.

---

## Experiment 4: Market Crash (200 ticks)

**Command:** `python3 cli.py --scenario market_crash --ticks 200 --seed 42`

Triple shock: supply shock (t=80), market panic (t=120), tech disruption (t=160).

### Results

| Metric | Value |
|---|---|
| Mean GDP | 18.19 |
| Peak GDP | 26.64 |
| Trough GDP | 11.02 |
| Max unemployment | 67.5% (27 of 40 firms dead) |
| Total cascades | 2 (sizes: 28, 3) |
| Firms alive at end | 33/40 |
| Final phase | market_crash |

### Key Observations

1. **The market panic is the lethal event, not the supply shock.** The supply shock at t=80 causes zero failures (as in Experiment 2). It is the market panic at t=120 that triggers mass failure. The panic mechanism directly slashes stock prices (to 40-70% of prior value), org fitness (*0.7), and health (*0.8). This multi-channel simultaneous shock pushes firms below the cascade threshold.

2. **Cascade timing reveals a delay.** The panic hits at t=120, but the major cascade (size 28) does not fire until t=130 -- a 10-tick delay. During ticks 120-129, firm health gradually degrades as the multiple damage channels compound. The cascade is not instantaneous; it requires cumulative weakening before the threshold is breached.

3. **The cascade is catastrophic and concentrated.** 28 of 40 firms fail in a single tick (t=130), followed by 3 more at t=131. The cascade propagation through the dependency network amplifies the initial failures: each failed firm damages dependents by 0.20 health, and dependents below 0.32 health (cascade threshold * 0.8) join the cascade.

4. **Gini paradoxically drops after the crash.** Gini falls from 0.70 pre-crash to 0.34 post-crash. This is because the crash eliminates the most unequal firms (those with the lowest stock prices die first), and the survivors plus respawned firms start at more similar values. Inequality then rebuilds from 0.34 to 0.59 by tick 200.

5. **Recovery is slow and incomplete.** By tick 200, only 33 of 40 firms are alive (2% respawn rate per tick per dead firm). The market index actually *rises* post-crash (from 37 at t=100 to 39.6 at t=200) because the surviving/respawned firms have a cleaner composition.

6. **Flexibility surges from crisis.** Mean flex fraction jumps from 0.279 (t=120) to 0.592 (t=150) to 0.737 (t=200). The crisis forces organizational adaptation; respawned firms enter with 0.50-0.80 flexibility, and surviving firms shift toward flexibility under crisis dynamics.

7. **Sentiment signature.** Market sentiment crashes to -0.72 at the panic tick, then recovers: -0.53 (t+1), -0.37 (t+2), -0.27 (t+3). The sentiment momentum parameter (0.7) means 70% of the shock carries forward each tick, producing roughly exponential decay.

---

## Experiment 5: Stress Test (300 ticks)

**Command:** `python3 cli.py --scenario stress_test --ticks 300 --seed 42`

Repeated shocks: supply shock (t=50), normalize (t=100), tech disruption (t=150), market panic (t=250), supply shock (t=300), tech disruption (t=400 -- beyond sim window).

### Results

| Metric | Value |
|---|---|
| Mean GDP | 12.75 |
| Peak GDP | 23.36 (final tick) |
| Firms alive | 40/40 throughout |
| Cascades | 0 |
| Max unemployment | 0% |
| Final flex fraction | 0.803 |
| Final Gini | 0.706 |

### Key Observations

1. **The economy survives all shocks with zero failures.** This is the most important result. Despite 4 scheduled events including a market panic, no firms fail. Why? The stress test's shocks are more spread out temporally than the market crash scenario. Each shock is absorbed before the next arrives.

2. **The market panic at t=250 does not trigger cascades.** In the market crash scenario, panic at t=120 (after a supply shock at t=80) killed 28 firms. Here, panic at t=250 (after tech disruption at t=150 and 100 ticks of recovery) kills none. The difference: by t=250, the economy has had time to recover from prior shocks, and the tech disruption at t=150 pushed flexibility up to ~0.65, making firms more resilient.

3. **Flexibility ratchets upward.** Each crisis pushes flexibility up, and the intervening stable periods do not fully reverse it. The trajectory: 0.395 -> 0.200 (stable drift, t=50) -> 0.208 (barely responsive to supply shock) -> 0.229 (t=100) -> 0.205 (drift back) -> 0.651 (t=200, post tech disruption) -> 0.803 (t=300, post panic). This is a ratchet: crises build flexibility faster than stability erodes it.

4. **GDP at final tick is anomalously high (23.36).** This is because the supply shock at t=300 doubles demand right at the last tick, so GDP reflects the inflated demand. The pre-shock GDP was stable at 11.2.

5. **Inequality grows despite shocks.** Gini rises from 0.066 to 0.706 -- comparable to the normal scenario (0.696). The shocks do not significantly reduce inequality because no firms fail. Inequality is driven by cumulative noise in stock prices, not by shocks.

6. **Resilience through adaptation.** The key finding: repeated, spaced shocks make the economy *more resilient* by driving organizational flexibility upward. This validates Beinhocker's argument that economies need periodic disruption to maintain adaptive capacity.

---

## Experiment 6: Large Economy -- 100 Firms (200 ticks)

**Command:** `python3 cli.py --scenario market_crash --ticks 200 --firms 100 --seed 42`

Same market crash scenario as Experiment 4, but with 100 firms instead of 40.

### Results

| Metric | Value |
|---|---|
| Mean GDP | 18.26 |
| Peak GDP | 78.36 |
| Trough GDP | 0.60 (near-total collapse) |
| Max unemployment | 97% (only 3 firms alive at t=83) |
| Total cascades | 2 (sizes: 100, 3) |
| Firms alive at end | 90/100 |
| SC Stress max | 1.000 |

### Key Observations

1. **Scale amplifies cascade severity dramatically.** At 40 firms, the market crash killed 28/40 (70%). At 100 firms, the cascade killed 100/100 (100%) at tick 83 -- a total wipeout. The denser dependency network (100 * 99 * 0.08 = ~792 edges vs 40 * 39 * 0.08 = ~125 edges) creates many more contagion paths, making the cascade self-sustaining once initiated.

2. **The cascade arrives 47 ticks earlier.** In the 40-firm economy, the lethal cascade hits at t=130 (10 ticks after panic at t=120). In the 100-firm economy, it hits at t=83 -- just 3 ticks after the supply shock at t=80, *before* the panic even occurs. The supply shock alone, which was harmless at 40 firms, triggers total collapse at 100 firms. This is a phase transition in network behavior.

3. **Near-death and resurrection.** At tick 83, only 3 firms survive. By tick 100 (17 ticks later), 38 firms are alive. By tick 200, 90 of 100 are alive. The 2% respawn rate, applied to 97 dead firms, produces ~2 new entrants per tick. The economy rebuilds from near-zero.

4. **GDP exhibits extreme volatility.** GDP goes from 10.4 (t=82) to 0.6 (t=83) to 78.4 (t=86). The spike to 78.4 occurs because a handful of surviving/respawned firms face the full 2x demand (from the supply shock) with no competition, producing enormous per-firm output. As more firms respawn, output per firm normalizes.

5. **Post-crash market index is paradoxically higher.** The market index at t=100 (60.9) is far higher than the pre-crash level (23.1 at t=79). This "phoenix effect" occurs because respawned firms enter at stock_price = 50 (half of initial 100), which is much higher than the pre-crash beaten-down prices of ~23. The market is structurally reset.

6. **Gini trajectory reverses.** Gini drops from 0.69 to 0.09 during the crash (as surviving firms converge in value), then rebuilds to 0.72 by tick 200. The crash is a great equalizer -- but only temporarily.

7. **Supply chain stress hits 1.0.** After the total wipeout, supply chain stress maxes out at 1.000 (every surviving firm has significant backlog). This is never observed in the 40-firm experiments.

8. **Recovery takes ~100 ticks to reach 90% employment.** The economy reaches 90/100 firms by tick ~195. The 2% respawn rate is the binding constraint on recovery speed. With 10 dead firms, only ~0.2 firms respawn per tick on average, explaining the long tail.

---

## Cross-Experiment Comparative Analysis

### Organizational Flexibility as Leading Indicator

| Scenario | Flex at t=50 | Flex at t=100 | Flex at t=150 | Flex at t=200 | Survived? |
|---|---|---|---|---|---|
| Normal | 0.200 | 0.200 | 0.200 | 0.200 | Yes (no shock) |
| Supply Shock | 0.200 | 0.200 | 0.200 | 0.198 | Yes |
| Tech Disruption | 0.200 | 0.200 | 0.207 | 0.641 | Yes |
| Market Crash | 0.200 | 0.362 | 0.592 | 0.737 | 33/40 survived |
| Stress Test | 0.208 | 0.229 | 0.205 | 0.651 | Yes (all 40) |

**Finding:** Flexibility only rises significantly under tech disruption or market panic. Supply shocks alone do not trigger organizational adaptation. The crisis detection threshold (avg_health < 0.45 or explicit crisis phase) must be met for the org engine to shift toward flexibility.

### Cascade Threshold is a Sharp Phase Transition

| Economy Size | Supply Shock (t=80) | Market Panic (t=120) | Max Cascade |
|---|---|---|---|
| 40 firms | 0 failures | 28 failures (t=130) | 28 |
| 100 firms | 100 failures (t=83) | N/A (already collapsed) | 100 |

The dependency network creates a critical density threshold. At 40 firms with 0.08 edge probability, the expected degree is ~3.1 per firm. At 100 firms, it is ~7.9. The higher connectivity makes cascades self-sustaining: each failure damages enough neighbors to trigger further failures.

### GDP Volatility Decomposition

| Scenario | GDP Std Dev | Main Driver |
|---|---|---|
| Normal | 0.053 | Baseline noise |
| Supply Shock | 7.45 | Demand multiplier |
| Tech Disruption | 0.053 | None (absorbed) |
| Market Crash | 5.79 | Demand + firm deaths |
| Stress Test | 3.47 | Multiple demand shocks |
| Large Economy | 9.86 | Total collapse + respawn |

Supply-side demand shocks dominate GDP volatility. Tech disruptions and market panics, despite being devastating to firm survival, affect GDP primarily through firm death count (reducing the number of producers) rather than through per-firm output changes.

---

## Emergent Behaviors Summary

1. **Peacetime rigidity drift:** Without shocks, organizations converge to maximum rigidity (flex=0.20) within ~50 ticks. This makes them efficient but fragile -- setting the stage for catastrophic cascades.

2. **Shock sequencing matters more than shock magnitude:** A 2.5x supply shock alone causes zero failures. A market panic alone (not tested directly but observable in the market crash timeline) kills firms only after a preceding supply shock has weakened health. The *combination and sequence* of shocks is what breaches the cascade threshold.

3. **Scale creates fragility, not just bigger failures:** The 100-firm economy does not experience "proportionally larger" failures than the 40-firm economy. It experiences *qualitatively different* behavior -- a total system wipeout from a shock that the 40-firm economy shrugs off. This is a network percolation phase transition.

4. **The flexibility ratchet:** Crises push organizations toward flexibility rapidly (0.02 per tick per unit of health deficit). Stability erodes flexibility slowly (0.005 per tick). The asymmetry means that repeated shocks ratchet flexibility upward over time, which is precisely Beinhocker's thesis about adaptive efficiency.

5. **The inequality cycle:** Gini rises steadily during normal operations (driven by cumulative stock price noise), drops sharply during cascades (as the distribution is truncated by firm death), then rebuilds during recovery. Catastrophic crashes are paradoxically equalizing.

6. **Phoenix economy effect:** After a total wipeout, the respawned economy can briefly exhibit *higher* GDP and market valuations than the pre-crash economy, because few firms face all demand. This overshooting is transient but dramatic.

7. **Market prices are a lagging indicator:** Stock prices decline throughout the normal scenario due to mean reversion to depressed fundamentals. They fail to signal the buildup of fragility (low flexibility, high network density). The market crash surprise at t=130 in Experiment 4 -- coming 10 ticks after the panic event -- shows that the market does not anticipate cascades.

---

## Methodology Notes

- All experiments used seed=42 for reproducibility
- Default parameters: 4 supply chain echelons, base demand 10.0, dependency probability 0.08
- The progress callback only prints every 50 ticks or on cascades > 2, so intermediate dynamics were extracted from JSON output
- One stochastic tech disruption (p=0.005/tick) occurs in most 200-tick runs, adding a small source of non-determinism within the deterministic event schedule
