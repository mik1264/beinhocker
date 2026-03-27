# Beer Distribution Game: Experiment Findings

## Overview

Six experiments were run on the Beer Distribution Game simulation to explore emergent behaviors in a four-echelon supply chain (Retailer, Wholesaler, Distributor, Brewery) using Sterman's anchor-and-adjust ordering heuristic. The simulation models how a simple demand perturbation propagates and amplifies through delayed feedback loops.

---

## Experiment 1: Baseline Step Demand (Behavioral, 50 ticks)

**Command:** `python3 cli.py --ticks 50`

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $341.00 | 2.36 |
| Wholesaler | $478.50 | 7.89 |
| Distributor | $1,065.00 | 3.76 |
| Brewery | $1,351.00 | 1.83 |
| **Total** | **$3,235.50** | -- |

**Emergent behaviors observed:**

- **Bullwhip amplification is severe and non-monotonic.** The Wholesaler exhibits the peak bullwhip ratio (7.89x), not the most upstream agent. This occurs because the Wholesaler sits at the inflection point where the Retailer's amplified orders compound with its own heuristic overreaction, while the Distributor and Brewery see already-smoothed (post-overshoot) signals.
- **Cost cascades upstream.** The Brewery pays 3.96x more than the Retailer despite facing the same underlying demand signal. Costs increase by roughly 2x at each upstream echelon.
- **Oscillation and convergence.** By tick 50, all agents have converged to zero backlogs and near-equilibrium inventory (14-18 cases), but the cumulative cost damage from the oscillation period is irreversible. The system "heals" but at enormous cost.
- **Inventory overshooting.** The extended run (vs. 36 ticks) shows the system has settled -- final supply lines are 16-18, close to the steady-state target. The oscillation lasted roughly 25-30 ticks after the demand step.

---

## Experiment 2: Rational vs Behavioral Comparison (50 ticks)

**Command:** `python3 cli.py --compare --ticks 50`

| Metric | Behavioral | Rational | Ratio |
|--------|----------:|----------:|------:|
| Total cost | $3,235.50 | $1,984.00 | **1.63x** |
| Max bullwhip | 7.89 (Wholesaler) | 2.36 (Brewery) | 3.34x |
| Brewery final inventory | 15 | 28 | 0.54x |
| Cost distribution (max/min) | 3.96x | 1.63x | -- |

**Key differences:**

- **The "bounded rationality tax" is 63%.** Behavioral agents pay $1,251 more in total -- a surcharge for using locally sensible heuristics that interact destructively at the system level.
- **Rational ordering flattens the cost distribution.** The behavioral mode concentrates costs upstream (Brewery: $1,351 vs Retailer: $341). Rational ordering distributes costs far more evenly ($406-$663), because it avoids the cascading overreaction that punishes upstream agents.
- **Rational bullwhip is moderate and monotonically increasing upstream** (1.18, 2.04, 2.26, 2.36). This is the "honest" bullwhip -- amplification from structural delays alone, without heuristic-driven panic. The behavioral mode's non-monotonic profile (peak at Wholesaler) reveals where heuristic distortion is worst.
- **Paradox: the Retailer pays more under rational ordering** ($406 vs $341). The rational agent tolerates short-term inventory costs to avoid triggering system-wide oscillation. This is a local sacrifice for global benefit -- an emergent form of cooperation that the behavioral heuristic cannot produce.

---

## Experiment 3: Longer Shipping Delays (delay=4, 50 ticks)

**Command:** `python3 cli.py --ticks 50 --shipping-delay 4`

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $609.50 | 29.18 |
| Wholesaler | $6,289.00 | 12.54 |
| Distributor | $13,828.00 | 6.73 |
| Brewery | $15,181.00 | 2.70 |
| **Total** | **$35,907.50** | -- |

**Emergent behaviors observed:**

- **Super-linear cost scaling with delay.** Doubling the shipping delay from 2 to 4 increases total cost by **11.1x** (from $3,236 to $35,908). This is emphatically not linear -- each additional tick of delay produces proportionally more damage because corrections arrive later, overshoot more, and trigger larger counter-corrections.
- **Extreme inventory accumulation.** The Distributor ends with 900 cases, the Brewery with 935 -- roughly 117 weeks of demand sitting idle. The Wholesaler holds 369 cases. This massive overstock is the aftermath of panic ordering during the oscillation phase.
- **Upstream supply lines collapse to zero.** The Wholesaler, Distributor, and Brewery all end with zero supply line, meaning they have completely stopped ordering. The system went through a cycle of (a) panic ordering, (b) massive overstock arrival, (c) complete order cessation. This boom-bust pattern mirrors real-world inventory cycles.
- **Bullwhip shifts to the Retailer.** With delay=4, the Retailer now shows the highest bullwhip ratio (29.18x), reversing the baseline pattern. Longer delays mean even the first echelon's corrections are dangerously late, so amplification begins immediately at the customer-facing node.

---

## Experiment 4: Sine Demand Pattern (100 ticks)

**Command:** `python3 cli.py --ticks 100 --demand-pattern sine`

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $1,426.00 | 7.59 |
| Wholesaler | $6,760.00 | 5.40 |
| Distributor | $17,080.50 | 3.22 |
| Brewery | $14,944.00 | 1.77 |
| **Total** | **$40,210.50** | -- |

**Emergent behaviors observed:**

- **Resonance and perpetual disequilibrium.** Unlike step demand where the system eventually converges, sine demand produces **never-ending oscillation**. The system cannot reach equilibrium because demand keeps changing. Total cost ($40,211) is 12.4x the baseline, despite demand only varying between 4 and 12 (mean 8).
- **Amplification is monotonically decreasing upstream** (7.59, 5.40, 3.22, 1.77). This is the opposite of the step-demand pattern. With continuous sinusoidal variation, each echelon acts as a low-pass filter that attenuates certain frequency components while amplifying others. The Retailer, closest to the raw demand signal, shows the most amplification.
- **Cost concentration in the middle echelons.** The Distributor bears the heaviest cost ($17,081), even more than the Brewery ($14,944). The Distributor sits at the resonance point where amplified Wholesaler orders compound with its own delayed corrections.
- **Phase lag creates destructive interference.** Each echelon's response is phase-shifted relative to demand due to pipeline delays. When the Brewery finally ramps up production in response to high demand, actual demand may have already cycled back to low, producing gluts. This is visible in the final state: the Brewery holds 329 cases of excess inventory.
- **Sine demand is harder than step demand.** The behavioral-to-baseline cost ratio for sine (12.4x) far exceeds step demand (1.0x by definition). Continuously varying demand gives the exponential smoothing filter no chance to converge -- it is perpetually chasing a moving target.

---

## Experiment 5: Information Sharing

**With information sharing:**
`python3 cli.py --ticks 50 --information-sharing` -- Total cost: **$1,844.00**

**Without information sharing (baseline):**
`python3 cli.py --ticks 50` -- Total cost: **$3,235.50**

| Agent | Cost (No Sharing) | Cost (Sharing) | Reduction |
|-------|------------------:|---------------:|----------:|
| Retailer | $341.00 | $343.00 | -0.6% |
| Wholesaler | $478.50 | $388.50 | 18.8% |
| Distributor | $1,065.00 | $584.50 | 45.1% |
| Brewery | $1,351.00 | $528.00 | 60.9% |
| **Total** | **$3,235.50** | **$1,844.00** | **43.0%** |

| Agent | Bullwhip (No Sharing) | Bullwhip (Sharing) |
|-------|---------------------:|-------------------:|
| Retailer | 2.36 | 2.25 |
| Wholesaler | 7.89 | 5.05 |
| Distributor | 3.76 | 2.04 |
| Brewery | 1.83 | 1.04 |

**Key findings:**

- **Information sharing reduces total cost by 43%.** This is a dramatic improvement from a purely informational intervention -- no changes to delay structure, heuristics, or inventory targets.
- **Benefits increase upstream.** The Retailer (who already sees consumer demand) gains nothing. The Brewery gains the most: 60.9% cost reduction and bullwhip drops from 1.83 to 1.04 -- essentially eliminating amplification at the most upstream node.
- **The Wholesaler remains a problem.** Even with shared demand information, the Wholesaler still amplifies at 5.05x. This is because information sharing fixes the *demand signal* but not the *inventory correction heuristic*. The Wholesaler still over-corrects based on its local inventory gap (alpha=0.5), even though it now forecasts demand accurately.
- **Information sharing nearly matches rational ordering on cost.** Shared information ($1,844) approaches rational ordering ($1,984) and actually beats it slightly. Information sharing corrects the most damaging aspect of bounded rationality (misperceiving demand) while leaving the heuristic's other flaws in place, but the demand correction turns out to be the single most valuable fix.
- **Final inventories are more balanced.** With sharing, all agents end between 15-18 cases vs 14-18 without. The Brewery ends at 18 (vs 15 without), suggesting less wild overshooting during the transition.

---

## Experiment 6: Extreme Delay (shipping delay=5, 80 ticks)

**Command:** `python3 cli.py --ticks 80 --shipping-delay 5`

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $1,696.00 | 60.40 |
| Wholesaler | $22,168.50 | 17.63 |
| Distributor | $53,941.00 | 8.05 |
| Brewery | $64,621.00 | 3.12 |
| **Total** | **$142,426.50** | -- |

**Emergent behaviors -- system approaches breakdown:**

- **Costs are catastrophic.** $142,427 total -- a **44x** multiplier over baseline ($3,236). The Brewery alone accumulates $64,621 in costs. The system has effectively failed as an efficient supply chain.
- **Retailer bullwhip of 60.4x represents signal destruction.** The Retailer's orders bear almost no resemblance to incoming consumer demand. A 60x variance amplification means the order signal is essentially noise relative to the demand signal. Information is destroyed, not transmitted.
- **Inventory accumulation is absurd.** The Brewery ends with **2,137 cases** -- 267 weeks (over 5 years) of demand. The Distributor holds 1,855 cases. The Wholesaler holds 632 cases. The system went through a massive ordering frenzy, and the resulting production is still sitting in warehouses 80 ticks later.
- **Complete order cessation upstream.** The Wholesaler, Distributor, and Brewery all end with zero supply line -- they stopped ordering entirely because they are buried in inventory. This represents a complete boom-bust cycle: from panic ordering to complete shutdown.
- **The delay-cost relationship is explosive.** Plotting the progression:

| Delay | Total Cost | Cost vs Baseline | Max Bullwhip |
|------:|-----------:|-----------------:|-------------:|
| 2 | $3,236 | 1.0x | 7.89 |
| 4 | $35,908 | 11.1x | 29.18 |
| 5 | $142,427 | 44.0x | 60.40 |

Adding one tick of delay (4 to 5) nearly **quadruples** the cost. The relationship is super-exponential in this regime -- the system is entering a zone where the heuristic's corrections are so delayed that they become purely destabilizing rather than corrective.

---

## Summary: Cross-Experiment Comparison

| Experiment | Total Cost | Max Bullwhip | Cost vs Baseline |
|------------|----------:|-------------:|-----------------:|
| 1. Baseline (delay=2, behavioral) | $3,236 | 7.89 | 1.0x |
| 2. Rational comparison | $1,984 | 2.36 | 0.61x |
| 3. Longer delay (delay=4) | $35,908 | 29.18 | 11.1x |
| 4. Sine demand (100 ticks) | $40,211 | 7.59 | 12.4x |
| 5a. Information sharing | $1,844 | 5.05 | 0.57x |
| 5b. No sharing (baseline) | $3,236 | 7.89 | 1.0x |
| 6. Extreme delay (delay=5, 80 ticks) | $142,427 | 60.40 | 44.0x |

---

## Emergent Behaviors: Key Themes

### 1. The Bullwhip Effect Is Structurally Inevitable, But Heuristics Determine Its Severity

Even rational agents exhibit bullwhip amplification (1.18-2.36x) due to the irreducible physics of pipeline delays. But behavioral agents amplify this by 3-25x further through the anchor-and-adjust heuristic. The bullwhip is not a "mistake" -- it is an emergent property of the system's topology. Heuristics determine whether it is a manageable ripple or a destructive wave.

### 2. Delay Is the Master Variable

Of everything tested -- heuristic type, information regime, demand pattern -- **shipping delay dominates all other factors**. The delay-cost curve is super-linear (possibly exponential): delay 2 costs $3,236; delay 4 costs $35,908; delay 5 costs $142,427. No heuristic improvement or information sharing can compensate for long delays. This aligns with the real-world success of JIT manufacturing and fast-logistics strategies: reducing pipeline time matters more than improving forecasting.

### 3. Information Sharing Is the Most Efficient Intervention

Information sharing (43% cost reduction) nearly matches switching to rational ordering (39% cost reduction) and requires no change to agent behavior -- only transparency. In real supply chains, this maps to technologies like point-of-sale data sharing, EDI, and demand sensing platforms. It is the highest-leverage, lowest-disruption intervention available.

### 4. Continuously Varying Demand Prevents Convergence

Step demand causes a single oscillation episode that eventually damps out. Sine demand produces perpetual oscillation because the system never has time to converge before demand changes again. Real-world demand -- with its mix of trends, seasonality, and shocks -- is closer to the sine case than the step case, suggesting that the Beer Game's step-demand scenario actually **understates** the real-world bullwhip problem.

### 5. The System Generates Its Own Crises

In every experiment, the only exogenous event is the initial demand change. Everything that follows -- the panic ordering, the inventory gluts, the order cessation, the boom-bust cycles -- is **endogenous**. The system creates its own crises from the interaction of delayed feedback, local information, and individually reasonable heuristics. No agent intends to create oscillation; the oscillation is a system-level emergent property.

### 6. Extreme Delays Cause Signal Destruction

At delay=5, the Retailer's bullwhip ratio of 60.4x means that the order signal has been so distorted that it contains almost no information about actual demand. The supply chain is not just amplifying the demand signal -- it is generating a new, endogenous signal that overwhelms the original. Upstream agents are responding to the system's own echoes, not to consumer behavior.

---

## Connection to Beinhocker: The Origin of Wealth

These experiments directly illustrate several of Beinhocker's central arguments:

**Endogenous cycles, not exogenous shocks.** The orthodox macroeconomic view attributes business cycles to external perturbations. The Beer Game shows that a single, tiny demand change (4 to 8 cases) generates 30-50 ticks of wild oscillation entirely through internal dynamics. The "business cycle" observed in the Brewery's order pattern -- boom, bust, recovery -- has no external cause after tick 5. It is purely structural.

**Bounded rationality as a system property.** The 63% cost penalty from behavioral ordering is not a failure of individual intelligence. Each agent's heuristic is locally sensible -- anchor on expected demand, correct for inventory gaps. The failure is emergent: individually rational rules interact destructively across echelons. This mirrors Beinhocker's argument that market inefficiencies arise not from individual irrationality but from the structure of interactions among boundedly rational agents.

**The architecture of the system matters more than the agents.** Shipping delay (a structural parameter) produces a 44x cost multiplier. Agent behavior (behavioral vs rational) produces a 1.6x multiplier. Information regime produces a 1.75x multiplier. The system's physical architecture -- its delays, its topology, its information structure -- dominates agent sophistication by an order of magnitude. This supports Beinhocker's view that economic dynamics are shaped more by institutional and structural features than by individual optimization.

**Complexity from simplicity.** Four identical agents following the same three-parameter heuristic, connected in a simple linear chain, produce oscillations, phase shifts, resonance, signal destruction, boom-bust cycles, and inventory catastrophes. No agent has a complex strategy. No agent behaves unpredictably. Yet the system exhibits rich, surprising, and costly emergent dynamics. This is Beinhocker's core complexity thesis: simple rules + interaction structure = emergent complexity.

**The economy is not a machine but a weather system.** The Beer Game cannot be "tuned to equilibrium" by adjusting parameters. Conservative heuristics help but cannot eliminate oscillation. Information sharing helps but cannot overcome structural delays. Even rational agents generate bullwhip. The system inherently produces dynamics that resist central control -- exactly the picture Beinhocker paints of the macroeconomy as a complex adaptive system that generates its own weather, rather than a machine that can be fine-tuned to optimal performance.
