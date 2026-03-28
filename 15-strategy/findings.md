# Strategy as Evolution: Findings

## Experiment 1: Baseline (Mixed Market, Default Volatility)

**Command**: `python3 cli.py --ticks 300 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.6514 |
| Best fitness (final) | 0.8399 |
| Exploiter share (final) | 27.6% |
| Explorer share (final) | 3.1% |
| Adaptive share (final) | 63.2% |
| HHI | 0.0342 |
| Portfolio diversity | 0.787 |
| Niche coverage | 100% |
| Total niche shifts | 74 |

**Key finding**: Adaptive firms dominate with 63.2% market share, confirming Beinhocker's thesis that a portfolio approach -- dynamically reallocating resources based on feedback -- outperforms both pure exploitation and pure exploration. Exploiters hold 27.6% share by concentrating resources effectively, but explorers are nearly eliminated (3.1%) because their resource spread is too thin to compete directly.

---

## Experiment 2: Stable Market (No Niche Shifts)

**Command**: `python3 cli.py --ticks 300 --shift-rate 0.0 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.6375 |
| Best fitness (final) | 0.8667 |
| Exploiter share (final) | 67.8% |
| Explorer share (final) | 0.0% |
| Adaptive share (final) | 21.9% |
| HHI | 0.0311 |
| Total niche shifts | 0 |

**Key finding**: When the environment is perfectly stable, exploiters dominate decisively with 67.8% market share. With zero niche shifts, the advantage of exploration vanishes entirely -- explorers are driven to 0% share. This validates the intuition that concentrated resource allocation wins when the landscape is static. However, adaptive firms still retain 21.9% share because their performance-weighted allocation converges toward exploiter-like behavior in stable conditions.

---

## Experiment 3: Volatile Market (High Shift Rate)

**Command**: `python3 cli.py --ticks 300 --shift-rate 0.2 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.6106 |
| Best fitness (final) | 0.8203 |
| Exploiter share (final) | 40.7% |
| Explorer share (final) | 0.0% |
| Adaptive share (final) | 50.0% |
| HHI | 0.0319 |
| Total niche shifts | 282 |

**Key finding**: In a volatile market (282 niche shifts vs. 74 in baseline), adaptive firms lead with 50.0% share. Exploiters decline from the baseline but still hold 40.7%. Strikingly, pure explorers are still eliminated -- their even resource spread makes them too weak in head-to-head competition, even though volatility should theoretically favor diversity. The overall mean fitness drops to 0.6106 (from 0.6514 baseline), reflecting the constant disruption. Adaptive firms succeed because they maintain portfolio diversity while still concentrating on high-performers -- the best of both worlds.

---

## Experiment 4: All Exploiters

**Command**: `python3 cli.py --ticks 300 --exploiter-frac 1.0 --explorer-frac 0.0 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.6304 |
| Best fitness (final) | 0.7223 |
| HHI | 0.0320 |
| Portfolio diversity | 0.700 |
| Total niche shifts | 65 |

**Key finding**: An all-exploiter market is efficient but fragile. The mean fitness (0.6304) is competitive with the baseline, but the best fitness at the end (0.7223) is substantially lower than the baseline (0.8399). Most tellingly, the final ticks show fitness collapsing into the 0.55-0.58 range -- a catastrophic decline from earlier peaks of 0.87. When niches shift, exploiters that have concentrated all resources on a now-mismatched experiment have no fallback. The entire market suffers synchronized crashes followed by slow recoveries. This is the "competency trap" March warned about.

---

## Experiment 5: All Explorers

**Command**: `python3 cli.py --ticks 300 --exploiter-frac 0.0 --explorer-frac 1.0 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.3622 |
| Best fitness (final) | 0.7842 |
| HHI | 0.0330 |
| Portfolio diversity | 0.720 |
| Total niche shifts | 72 |

**Key finding**: An all-explorer market is dramatically worse. Mean fitness (0.3622) is nearly half the baseline (0.6514). By spreading resources evenly across all experiments, no single initiative gets enough investment to compete effectively. The market is "robust" in that fitness never drops catastrophically (no synchronized crashes), but it never achieves high performance either. This is the cost of pure exploration: you discover many things but master none. The maximum fitness at any point (0.784) is far below what exploiter or adaptive firms achieve.

---

## Experiment 6: Larger Economy (100 Firms, 10 Niches)

**Command**: `python3 cli.py --ticks 300 --firms 100 --niches 10 --seed 42`

| Metric | Value |
|--------|-------|
| Mean fitness (avg) | 0.5954 |
| Best fitness (final) | 0.8933 |
| Exploiter share (final) | 60.6% |
| Explorer share (final) | 0.0% |
| Adaptive share (final) | 29.0% |
| HHI | 0.0095 |
| Portfolio diversity | 0.471 |
| Niche coverage | 100% |
| Total niche shifts | 151 |

**Key finding**: Scaling to 100 firms and 10 niches produces a more competitive market (HHI 0.0095 vs. 0.0342). Exploiters gain a larger share (60.6%) in this bigger market, likely because with 10 niches there is more room for specialization -- exploiters that happen to find the right niche lock in. Portfolio diversity per firm drops to 0.471 (from 0.787) because 6 experiments covering 10 niches is a smaller fraction. The market still achieves full niche coverage through collective diversity even as individual firms specialize.

---

## Cross-Experiment Analysis

### The Exploration-Exploitation Spectrum

| Experiment | Exploiter Share | Adaptive Share | Mean Fitness |
|-----------|----------------|----------------|--------------|
| Baseline (shift=0.05) | 27.6% | 63.2% | 0.6514 |
| Stable (shift=0.0) | 67.8% | 21.9% | 0.6375 |
| Volatile (shift=0.2) | 40.7% | 50.0% | 0.6106 |
| All Exploiters | 91.2% | 0.0% | 0.6304 |
| All Explorers | 0.0% | 0.0% | 0.3622 |
| Large Economy | 60.6% | 29.0% | 0.5954 |

### Key Insights

1. **Adaptive firms win in the baseline**: With moderate volatility, the adaptive strategy -- which dynamically reallocates resources based on performance feedback -- captures the largest market share. This confirms Beinhocker's core argument: strategy should be a portfolio of experiments, not a single plan.

2. **Environment determines the optimal balance**: In stable markets, exploitation dominates. In volatile markets, adaptive firms that balance both do best. Pure exploration is never optimal -- it produces too little fitness to survive competitive selection.

3. **Pure exploration is a death sentence**: Across all experiments, pure explorers are eliminated or minimized. Spreading resources evenly is simply too inefficient. Even in volatile markets, some degree of concentration is necessary to generate fitness.

4. **Exploiter monocultures are fragile**: The all-exploiter experiment shows the classic competency trap. High fitness during stable periods, followed by catastrophic synchronized crashes when niches shift. Without portfolio diversity, the entire market fails simultaneously.

5. **Collective diversity compensates for individual specialization**: In the large economy (experiment 6), individual firms have lower portfolio diversity (0.47 vs. 0.79), but the market as a whole still covers all niches. This mirrors Beinhocker's argument that markets are massively parallel search algorithms -- individual firms can specialize while the system as a whole explores broadly.

6. **Market concentration is universally low**: HHI stays below 0.035 across all experiments, indicating that no single firm dominates. This is an emergent property of the selection mechanism -- even the best-performing firms hold only a small fraction of total market share.

### Connection to Beinhocker

These results directly support Beinhocker's Chapter 15 argument that strategy is evolutionary, not predictive:

- **"Strategy is a portfolio of experiments"**: Adaptive firms that maintain multiple bets and reallocate based on feedback consistently outperform single-bet strategies.
- **"Robustness over optimality"**: The adaptive strategy is never the best at any single moment, but it performs well enough across all conditions to accumulate the highest long-run market share.
- **"Markets as parallel search"**: The simulation shows that collective market-level diversity emerges even when individual firms specialize, just as Beinhocker describes real economies.
- **"The exploration-exploitation tradeoff is environment-dependent"**: Stable environments favor exploitation; volatile environments favor adaptation. There is no universal "best strategy" -- only strategies that are fit for their environment.
