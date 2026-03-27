# Prisoner's Dilemma / Evolution of Cooperation: Experiment Findings

## Model Overview

This simulation implements an iterated Prisoner's Dilemma with evolutionary dynamics, based on Axelrod's tournaments and Beinhocker's *The Origin of Wealth* (Chapter 9). Seven strategies compete:

| Strategy | Behavior |
|----------|----------|
| **AllC** (Always Cooperate) | Unconditionally cooperates |
| **AllD** (Always Defect) | Unconditionally defects |
| **TFT** (Tit-for-Tat) | Cooperates first, then copies opponent's last move |
| **GTFT** (Generous TFT) | Like TFT but forgives defections with ~33% probability |
| **Pavlov** | Win-Stay, Lose-Shift: repeats action after good outcome, switches after bad |
| **Random** | 50/50 cooperate or defect |
| **Grudger** | Cooperates until opponent defects once, then defects forever |

Default payoff matrix: T=5, R=3, P=1, S=0. Initial mix: TFT 20%, AllC/AllD/Pavlov/Grudger each 15%, GTFT/Random each 10%.

---

## Experiment 1: Spatial Baseline

**Command:** `python3 cli.py --spatial --ticks 100 --seed 42`
**Parameters:** 50x50 grid, Moore neighborhood, noise=0.0, mutation=0.001

### Results

| Metric | Value |
|--------|-------|
| Final cooperation rate | **100.0%** |
| Mean cooperation rate | 99.0% |
| Final average payoff | 3.00 (mutual cooperation) |

**Final strategy distribution:**
- Grudger: **46.3%** (dominant)
- TFT: 27.4%
- Pavlov: 13.0%
- GTFT: 7.4%
- AllC: 5.9%
- AllD: 0.0% (extinct)
- Random: 0.0% (extinct)

### Evolutionary Trajectory

Cooperation rose rapidly from 69.6% at generation 0 to 99.0% by generation 10. AllD was eliminated by generation 20; Random vanished by generation 50. Once defectors were gone, all surviving strategies cooperated perfectly, producing a payoff of 3.0 (mutual cooperation reward).

### Key Finding

**Spatial structure strongly promotes cooperation.** Grudger dominated because it punishes defectors permanently, forming impenetrable defensive clusters on the grid. TFT thrived as the second-most successful retaliatory cooperator. The spatial structure allowed cooperative clusters to form and resist invasion by defectors, which could only exploit agents at cluster borders.

---

## Experiment 2: Tournament Baseline

**Command:** `python3 cli.py --tournament --ticks 100 --seed 42`
**Parameters:** Population 100, noise=0.0, mutation=0.001

*Note: A bug was found and fixed in cli.py where `--tournament` was not properly overriding the default spatial mode. The mode selection logic was changed from `"spatial" if args.spatial` to `"tournament" if args.tournament`.*

### Results

| Metric | Value |
|--------|-------|
| Final cooperation rate | **0.0%** |
| Mean cooperation rate | 8.6% |
| Final average payoff | 1.00 (mutual defection) |

**Final strategy distribution:**
- AllD: **100.0%** (total domination)
- All other strategies: 0.0%

### Evolutionary Trajectory

Cooperation collapsed from 68.1% at generation 0 to 4.4% by generation 20. By generation 50, AllD had achieved total fixation at 100%.

The trajectory shows AllD grew from 14% to 35% in just 10 generations, then to 91% by generation 20.

### Key Finding: Spatial vs. Tournament -- A Stark Contrast

This is the single most important result across all experiments. **The same strategies, payoff matrix, and initial conditions produce diametrically opposite outcomes depending on population structure:**

| | Spatial | Tournament |
|---|---------|-----------|
| Final cooperation | 100% | 0% |
| Dominant strategy | Grudger (46%) | AllD (100%) |
| Final payoff | 3.0 | 1.0 |

In the well-mixed tournament, AllD can exploit every cooperator in the population. Without spatial clustering, cooperative strategies cannot form protective groups. This reproduces Axelrod's finding that **population structure is essential for the evolution of cooperation**. The spatial grid provides what evolutionary biologists call "population viscosity" -- agents interact mostly with neighbors, allowing cooperative clusters to outcompete defector clusters even though individual defectors beat individual cooperators.

---

## Experiment 3: High Noise (10% Execution Error)

**Command:** `python3 cli.py --spatial --ticks 100 --noise 0.10 --seed 42`
**Parameters:** 50x50 grid, noise=0.10, mutation=0.001

### Results

| Metric | Value |
|--------|-------|
| Final cooperation rate | **75.3%** |
| Mean cooperation rate | 73.7% |
| Final average payoff | 2.60 |

**Final strategy distribution:**
- Pavlov: **97.6%** (near-total domination)
- AllD: 2.1%
- Grudger: 0.2%
- GTFT: 0.1%
- TFT: 0.0%
- AllC: 0.0%
- Random: 0.0%

### Evolutionary Trajectory

The trajectory reveals a dramatic strategy succession:
- **Gen 1-10:** TFT initially rose to 51.6%, with Pavlov at 22.7% and GTFT at 19.6%
- **Gen 10-20:** Pavlov overtook TFT (45.2% vs 13.7%), while GTFT also grew (39.1%)
- **Gen 20-50:** Pavlov surged to 84.3%, displacing all others
- **Gen 50-100:** Pavlov reached 97.6% dominance

### Key Finding: Noise Transforms the Strategy Landscape

With 10% execution error, **Pavlov completely displaced TFT and Grudger** -- the two dominant strategies under zero noise. This is one of the most celebrated results in evolutionary game theory (Nowak & Sigmund, 1993).

**Why Pavlov wins under noise:**
- **TFT's weakness:** When noise causes an accidental defection, two TFT players enter a destructive cycle of alternating retaliation (CD-DC-CD-DC...), earning only 2.5 on average instead of 3.0.
- **Grudger's weakness:** A single noise-triggered defection causes Grudger to permanently retaliate, destroying the cooperative relationship forever. Under 10% noise, this happens quickly.
- **Pavlov's resilience:** Pavlov uses a "Win-Stay, Lose-Shift" heuristic. After an accidental defection leads to mutual defection (both lose), both Pavlov players shift back to cooperation, self-correcting the error.
- **GTFT's intermediate success:** GTFT initially thrived because its 33% forgiveness rate partially handles noise, but Pavlov's more systematic error correction proved superior.

The cooperation rate dropped from 100% (zero noise) to 75.3% because 10% of intended cooperations are randomly flipped to defections, and vice versa, creating an irreducible noise floor.

---

## Experiment 4: Zero Noise (Perfect Execution)

**Command:** `python3 cli.py --spatial --ticks 100 --noise 0.0 --seed 42`
**Parameters:** Identical to Experiment 1 (noise was already 0.0 by default)

### Results

Identical to Experiment 1 (as expected, since default noise is already 0.0):
- Final cooperation rate: 100%
- Grudger: 46.3%, TFT: 27.4%
- AllD: extinct

### Key Finding: Grudger and TFT Dominate Under Deterministic Play

Under zero noise, there is no risk of accidental defection, so Grudger's "never forgive" policy carries no cost. Grudger's absolute punishment of defectors makes it the strongest defensive strategy. TFT is nearly as effective but neutral against Grudger (both always cooperate with each other). Pavlov, GTFT, and AllC survive as free-riders in the cooperative ecosystem since all strategies cooperate with each other once defectors are eliminated.

---

## Experiment 5: High Mutation Rate

**Command:** `python3 cli.py --spatial --ticks 200 --mutation-rate 0.05 --seed 42`
**Parameters:** 50x50 grid, noise=0.0, mutation=0.05 (50x baseline)

### Results

| Metric | Value |
|--------|-------|
| Final cooperation rate | **97.3%** |
| Mean cooperation rate | 97.2% |
| Final average payoff | 2.95 |

**Final strategy distribution:**
- Grudger: **70.9%** (dominant)
- Pavlov: 8.4%
- TFT: 7.6%
- AllC: 5.6%
- GTFT: 5.7%
- AllD: 1.0%
- Random: 0.9%

### Evolutionary Trajectory

| Generation | Coop Rate | Grudger | AllD | Random |
|-----------|-----------|---------|------|--------|
| 1 | 69.6% | 15.4% | 15.0% | 10.4% |
| 20 | 98.0% | 55.2% | 0.7% | 0.7% |
| 50 | 98.2% | 65.4% | 0.6% | 0.6% |
| 100 | 97.8% | 67.9% | 0.8% | 0.7% |
| 200 | 97.3% | 70.9% | 1.0% | 0.9% |

### Key Finding: High Mutation Maintains Diversity but Cannot Destabilize Cooperation

With 5% mutation rate, **all seven strategies persist** indefinitely. Mutants constantly appear but are rapidly selected against if they are exploitative (AllD, Random). The key observations:

1. **Strategy diversity is maintained:** Unlike the low-mutation baseline where AllD and Random went completely extinct, high mutation keeps them at ~1% as a constant mutational "rain." This is analogous to mutation-selection balance in population genetics.

2. **Grudger's dominance intensifies:** Grudger rose from 46% (baseline) to 71%. The constant influx of AllD mutants actually *benefits* Grudger, which efficiently punishes them and gains a fitness edge over more forgiving strategies like TFT and GTFT.

3. **Cooperation is robust:** Despite 5% of the population mutating every generation, cooperation stayed above 97%. The spatial structure provides strong enough selection pressure to contain defector mutants before they can spread.

4. **No evolutionary arms races observed:** The strategy distribution reached a stable equilibrium by generation ~50 and showed only gentle drift thereafter. The system did not exhibit the cyclical dynamics (AllD invades cooperators, then TFT invades AllD, etc.) sometimes seen in well-mixed populations.

---

## Experiment 6: Modified Payoff Matrix (High Temptation)

**Command:** `python3 cli.py --spatial --ticks 100 --payoff-T 10 --seed 42`
**Parameters:** 50x50 grid, T=10 (doubled from default 5), R=3, P=1, S=0

*Note: The simulation warns this violates the standard PD condition 2R > T+S (6 > 10 is false). This makes the "temptation to defect" extremely strong and mutual cooperation is no longer the socially optimal outcome when amortized.*

### Results

| Metric | Value |
|--------|-------|
| Final cooperation rate | **99.9%** |
| Mean cooperation rate | 94.6% |
| Final average payoff | 3.00 |

**Final strategy distribution:**
- Grudger: **94.0%** (overwhelming domination)
- TFT: 2.4%
- Pavlov: 1.3%
- GTFT: 1.3%
- AllC: 1.0%
- AllD: 0.0%
- Random: 0.0%

### Evolutionary Trajectory

| Generation | Coop Rate | Grudger | AllD | TFT | Random |
|-----------|-----------|---------|------|-----|--------|
| 1 | 69.6% | 15.4% | 15.0% | 20.4% | 10.4% |
| 10 | 96.0% | **92.1%** | 1.4% | 3.6% | 2.8% |
| 20 | 94.3% | 86.6% | 0.0% | 2.7% | 10.3% |
| 50 | 99.9% | 96.8% | 0.0% | 1.9% | 0.1% |
| 100 | 99.9% | 94.0% | 0.0% | 2.4% | 0.0% |

### Key Finding: Higher Temptation Amplifies Grudger Dominance

Counterintuitively, doubling the temptation payoff did NOT lead to more defection. Instead, **Grudger surged from 46% to 94%** of the population. The mechanism:

1. **Stronger selection against defectors:** When T=10, a defector who exploits a cooperator gets 10 instead of 5. But a Grudger neighbor who retaliates imposes mutual defection (payoff=1) on the defector for all remaining rounds. The *cost* of triggering a Grudger's retaliation is now much higher in relative terms, because the defector's neighbors who are Grudgers retaliate immediately and permanently.

2. **Grudger beats TFT decisively:** With T=10, the first-round exploitation matters more. Against a defector, both TFT and Grudger start cooperating and get exploited once. But Grudger's absolute commitment to retaliation makes it a slightly more credible deterrent in the spatial dynamics. The increased stakes amplify the advantage of never forgiving.

3. **Interesting anomaly at Gen 20:** Cooperation temporarily dipped to 94.3% while Random spiked to 10.3%. This suggests a brief period where Random agents, who cooperate 50% of the time, benefited from the elevated T payoff when they happened to defect against cooperators. However, Grudger quickly extinguished this.

4. **Cooperation survives despite broken PD condition:** Even though 2R > T+S is violated (making the game technically not a standard PD), the spatial structure still sustained near-perfect cooperation. The grid's local interactions prevented global exploitation.

---

## Cross-Experiment Summary

### Strategy Dominance Across Conditions

| Experiment | Winner | Coop Rate | Key Driver |
|-----------|--------|-----------|------------|
| Spatial Baseline | Grudger (46%) | 100% | Spatial clustering |
| Tournament Baseline | AllD (100%) | 0% | No spatial protection |
| High Noise (0.10) | Pavlov (98%) | 75% | Error correction |
| Zero Noise | Grudger (46%) | 100% | Permanent retaliation |
| High Mutation | Grudger (71%) | 97% | Constant defense needed |
| High Temptation (T=10) | Grudger (94%) | 100% | Amplified punishment logic |

### Major Emergent Behaviors

**1. Spatial Structure as the Foundation of Cooperation**
The most fundamental finding: removing spatial structure (Experiment 2) completely inverts the outcome from 100% cooperation to 0%. This confirms Nowak & May (1992): spatial structure provides the scaffolding on which cooperation can evolve and persist. Without it, defection is the only evolutionarily stable strategy.

**2. Strategy Succession Under Noise**
Noise triggers a complete regime change in strategy dominance (Experiment 3). The succession follows a clear evolutionary logic:
- Gen 0-10: TFT rises first (retaliatory cooperator beats unconditional strategies)
- Gen 10-20: GTFT and Pavlov overtake TFT (forgiveness becomes necessary under noise)
- Gen 20-100: Pavlov dominates (Win-Stay/Lose-Shift provides optimal error correction)

This reproduces the Nowak & Sigmund (1993) finding that Pavlov is the most robust strategy in noisy environments.

**3. The Paradox of Temptation**
Increasing the temptation to defect (Experiment 6) actually *strengthened* cooperation by making Grudger's punishment more consequential. This is a genuine paradox: making defection more attractive made defectors less successful, because the spatial structure converted higher stakes into stronger selection against exploitation.

**4. Mutation-Selection Balance**
High mutation (Experiment 5) created a steady-state ecosystem where all strategies persist at low levels, analogous to mutation-selection balance in genetics. Cooperation was robust to this constant perturbation, losing only ~3% compared to the low-mutation baseline.

**5. Grudger as the Spatial Champion**
Across all spatial experiments, Grudger was the dominant or co-dominant strategy. Its "cooperate until betrayed, then defect forever" rule is maximally effective on a grid where agents have persistent local relationships. The permanent memory of defection acts as an absolute deterrent, and the spatial structure means Grudger clusters can wall off and contain any defector incursion.

### Connection to Beinhocker's Thesis

These results directly illustrate Beinhocker's argument in *The Origin of Wealth* that:
- **Structure matters:** The same agents with the same rules produce radically different macro-level outcomes depending on population structure (spatial vs. well-mixed)
- **Cooperation is an emergent property** of spatial evolutionary dynamics, not a pre-programmed outcome
- **Simple rules produce complex dynamics:** Seven simple strategies interacting on a grid generate rich phenomena including strategy succession, spatial pattern formation, and counterintuitive responses to parameter changes
- **Evolution selects for robustness:** The winning strategies (Grudger under zero noise, Pavlov under noise) are not the most sophisticated but the most robust to their specific environmental challenges

### Bug Fix

During the experiments, a bug was discovered in `cli.py` at line 100. The mode selection logic `mode = "spatial" if args.spatial else "tournament"` always selected spatial mode because `args.spatial` defaults to `True`. This was fixed to `mode = "tournament" if args.tournament else "spatial"`.
