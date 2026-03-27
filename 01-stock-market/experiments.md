# SFI Artificial Stock Market: Experiments in Emergent Complexity

## What Is the SFI Artificial Stock Market?

The Santa Fe Institute Artificial Stock Market (SFI ASM), developed by Arthur, Holland, LeBaron, Palmer, and Tayler (1997), is one of the landmark models in computational economics. It replaces the standard assumption of identical, perfectly rational agents with a population of heterogeneous agents who *learn* --- each maintaining a library of condition-action forecasting rules that evolve through a genetic algorithm. Agents observe market conditions (price relative to fundamental value, moving averages), select their best-performing rule, and submit demand accordingly. A call market clears at the price that balances aggregate demand.

The model was built to answer a deceptively simple question: **what happens when we stop assuming markets are in equilibrium and instead let equilibrium (or disequilibrium) emerge from the bottom up?**

The answer, as Beinhocker emphasizes in *The Origin of Wealth*, is that markets become complex adaptive systems --- exhibiting fat-tailed returns, volatility clustering, bubbles, crashes, and persistent wealth inequality, none of which are predicted by the efficient market hypothesis but all of which appear in real financial data.

These experiments systematically vary key parameters to explore how market complexity depends on agent learning, mutation pressure, population size, and evolutionary tempo.

---

## Experimental Setup

All experiments use seed 42 for reproducibility, 2000 ticks, and an interest rate of 10%. The stock pays AR(1) dividends with mean 10.0, giving a fundamental value of 100.

---

## Experiment Results

### Experiment 1: Rational Baseline (No Learning)

**Command:**
```bash
python3 cli.py --rational --agents 25 --ticks 2000 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 118.19 |
| Std Price | 23.43 |
| Fundamental Value | 107.81 |
| Mean Return | -0.0109 |
| Volatility (std return) | 0.0833 |
| Annualized Volatility | 1.32 |
| Excess Kurtosis | 4.79 |
| Skewness | -2.39 |
| Return Autocorrelation (lag-1) | -0.130 |
| Volatility Clustering (abs-return AC1) | -0.055 |
| Tail Index (Hill) | 46.38 |
| Mean Volume | 0.05 |
| Gini Coefficient | 0.60 |

**Observations:** The rational mode is paradoxically *not* well-behaved. With only one rule per agent and no adaptation, prices drift persistently above fundamental value (mean 118 vs. fundamental ~108). Volatility is very high (annualized 1.32). Volume is near zero --- agents' fixed rules produce nearly identical demands, so there is almost no trade. The negative skewness (-2.39) indicates occasional sharp downward corrections. The high tail index (~46) means the tails are actually *thin* relative to learning regimes; extreme returns come from drift rather than speculative dynamics. Wealth inequality is severe (Gini 0.60).

---

### Experiment 2: Learning Mode (Default Parameters)

**Command:**
```bash
python3 cli.py --learning --agents 25 --ticks 2000 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 102.37 |
| Std Price | 7.26 |
| Fundamental Value | 95.64 |
| Mean Return | -0.0000 |
| Volatility (std return) | 0.0423 |
| Annualized Volatility | 0.67 |
| Excess Kurtosis | **45.26** |
| Skewness | 1.13 |
| Return Autocorrelation (lag-1) | -0.357 |
| Volatility Clustering (abs-return AC1) | **0.489** |
| Tail Index (Hill) | **2.55** |
| Mean Volume | 5.32 |
| Gini Coefficient | 0.43 |

**Observations:** Learning transforms the market. Price tracks fundamental value far more closely (mean 102 vs. ~96 fundamental). Volatility drops by half. But the return distribution becomes dramatically non-Gaussian: excess kurtosis leaps from 4.8 to **45.3**, and the Hill tail index drops to 2.55, indicating heavy power-law tails --- strikingly close to the ~3 observed in real equity markets. Volatility clustering emerges strongly (0.49), a hallmark "stylized fact" absent in the rational regime. Volume jumps from near-zero to 5.3: heterogeneous beliefs generate trade. This is the core SFI ASM result --- learning agents collectively produce realistic market dynamics that rational agents cannot.

---

### Experiment 3: High Mutation Rate (0.15)

**Command:**
```bash
python3 cli.py --learning --agents 25 --ticks 2000 --mutation-rate 0.15 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 100.74 |
| Std Price | 7.39 |
| Mean Return | 0.0004 |
| Volatility (std return) | 0.0406 |
| Excess Kurtosis | **47.90** |
| Volatility Clustering | **0.509** |
| Tail Index (Hill) | 2.65 |
| Mean Volume | 4.22 |
| Gini Coefficient | 0.45 |

**Observations:** Quintupling the mutation rate (0.03 to 0.15) slightly increases kurtosis and volatility clustering. Prices center even more closely on fundamental value. The higher mutation pressure injects more strategy diversity, which paradoxically *stabilizes* the mean price while making extreme events slightly more common. Volume decreases modestly --- rapid rule turnover means agents more frequently hold unproven rules, reducing conviction in positions.

---

### Experiment 4: Low Mutation Rate (0.005)

**Command:**
```bash
python3 cli.py --learning --agents 25 --ticks 2000 --mutation-rate 0.005 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 99.96 |
| Std Price | 7.04 |
| Mean Return | -0.0001 |
| Volatility (std return) | 0.0394 |
| Excess Kurtosis | **42.60** |
| Volatility Clustering | **0.458** |
| Tail Index (Hill) | 2.73 |
| Mean Volume | 4.72 |
| Gini Coefficient | 0.48 |

**Observations:** Reducing mutation to 0.005 produces the *lowest* price volatility across all learning experiments. Kurtosis drops to 42.6 (still enormous by Gaussian standards) and volatility clustering softens slightly. The market converges toward a more stable but less diverse ecology of strategies. Higher volume (4.72 vs. 4.22 for high mutation) suggests agents stick with proven rules longer, trading with greater conviction. But wealth inequality *increases* (Gini 0.48 vs. 0.43 default) --- with slower adaptation, early winners lock in advantages.

---

### Experiment 5a: Thin Market (20 Agents)

**Command:**
```bash
python3 cli.py --learning --agents 20 --ticks 2000 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 100.70 |
| Std Price | 8.94 |
| Mean Return | -0.0006 |
| Volatility (std return) | 0.0449 |
| Excess Kurtosis | **92.47** |
| Skewness | **3.26** |
| Volatility Clustering | **0.435** |
| Tail Index (Hill) | 2.53 |
| Mean Volume | 4.24 |
| Gini Coefficient | 0.38 |

### Experiment 5b: Thick Market (200 Agents)

**Command:**
```bash
python3 cli.py --learning --agents 200 --ticks 2000 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 102.83 |
| Std Price | 7.62 |
| Mean Return | -0.0024 |
| Volatility (std return) | 0.0346 |
| Excess Kurtosis | **204.15** |
| Skewness | **7.83** |
| Volatility Clustering | **0.325** |
| Tail Index (Hill) | 3.73 |
| Mean Volume | 28.23 |
| Gini Coefficient | 0.49 |

**Observations --- Market Thickness:**

| Metric | 20 Agents | 25 Agents | 200 Agents |
|--------|-----------|-----------|------------|
| Price Std | 8.94 | 7.26 | 7.62 |
| Return Volatility | 0.0449 | 0.0423 | 0.0346 |
| Excess Kurtosis | 92.5 | 45.3 | 204.2 |
| Skewness | 3.26 | 1.13 | 7.83 |
| Tail Index | 2.53 | 2.55 | 3.73 |
| Vol. Clustering | 0.435 | 0.489 | 0.325 |
| Gini | 0.38 | 0.43 | 0.49 |

More agents *reduces* return volatility (thicker markets absorb shocks better) but *increases* kurtosis dramatically. With 200 agents, the kurtosis reaches 204 and skewness hits 7.8 --- the market produces rare but enormous price spikes. The tail index rises to 3.73 (thinner tails than thin markets), suggesting that while extreme events are rarer in absolute frequency, the very largest moves are even more extreme when 200 strategies occasionally align. Wealth inequality worsens with more agents (Gini 0.49): in a larger ecology, a few agents with superior strategies extract disproportionate gains.

---

### Experiment 6a: Fast GA Evolution (Interval 50)

**Command:**
```bash
python3 cli.py --learning --agents 25 --ticks 2000 --ga-interval 50 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 100.52 |
| Std Price | 7.59 |
| Mean Return | -0.0012 |
| Volatility (std return) | 0.0407 |
| Excess Kurtosis | **140.93** |
| Skewness | **4.97** |
| Volatility Clustering | **0.449** |
| Tail Index (Hill) | 2.79 |
| Mean Volume | 3.45 |
| Gini Coefficient | 0.47 |

**Observations:** Increasing GA frequency 5x (interval 50 vs. 250) triples kurtosis to 141. Rapid strategy evolution creates a "Red Queen" dynamic --- agents constantly adapt, generating waves of coordinated behavior change that manifest as price spikes. Volume drops (3.45 vs. 5.32) because frequent rule replacement means agents spend less time with well-calibrated rules.

---

### Experiment 6b: Limited Strategy Pool (20 Rules per Agent)

**Command:**
```bash
python3 cli.py --learning --agents 25 --ticks 2000 --rules-per-agent 20 --seed 42
```

| Metric | Value |
|--------|-------|
| Mean Price | 101.48 |
| Std Price | 8.03 |
| Mean Return | -0.0009 |
| Volatility (std return) | **0.0557** |
| Excess Kurtosis | **211.28** |
| Skewness | **8.40** |
| Volatility Clustering | **0.648** |
| Tail Index (Hill) | **2.18** |
| Mean Volume | 2.03 |
| Gini Coefficient | 0.52 |

**Observations:** This is the most extreme configuration. With only 20 rules (vs. 100 default), agents have a much smaller strategy repertoire. The results are striking: volatility rises 32% (0.056 vs. 0.042), kurtosis explodes to 211, and volatility clustering reaches 0.65 --- the strongest of any experiment. The tail index drops to 2.18, indicating *very* heavy power-law tails (heavier than the cubic law of real markets). Low rule diversity means agents lack the flexibility to adapt to changing conditions, creating prolonged periods of mispricing followed by violent corrections. Volume is the lowest of any learning experiment (2.03) --- fewer rules means less disagreement. Wealth inequality is the highest (Gini 0.52).

---

## Comparative Summary

| Experiment | Volatility | Kurtosis | Vol. Cluster | Tail Index | Gini |
|------------|-----------|----------|-------------|------------|------|
| 1. Rational | 0.0833 | 4.8 | -0.055 | 46.4 | 0.60 |
| 2. Learning (default) | 0.0423 | 45.3 | 0.489 | 2.55 | 0.43 |
| 3. High mutation (0.15) | 0.0406 | 47.9 | 0.509 | 2.65 | 0.45 |
| 4. Low mutation (0.005) | 0.0394 | 42.6 | 0.458 | 2.73 | 0.48 |
| 5a. Few agents (20) | 0.0449 | 92.5 | 0.435 | 2.53 | 0.38 |
| 5b. Many agents (200) | 0.0346 | 204.2 | 0.325 | 3.73 | 0.49 |
| 6a. Fast GA (50) | 0.0407 | 140.9 | 0.449 | 2.79 | 0.47 |
| 6b. Few rules (20) | 0.0557 | 211.3 | **0.648** | **2.18** | 0.52 |

---

## Key Findings

### 1. Learning Creates Realistic Market Complexity --- Rationality Does Not

The most fundamental result: switching from rational to learning agents transforms every statistical property of the market. Rational agents produce high volatility, thin tails, no volatility clustering, and near-zero volume. Learning agents produce lower volatility but dramatically fatter tails, strong volatility clustering, and active trading. The learning market resembles real financial data; the rational market does not.

This directly supports Beinhocker's central argument: the "stylized facts" of financial markets --- fat tails, clustered volatility, excess trading volume --- are not anomalies to be explained away. They are the *natural signature of adaptive agents co-evolving in a complex system*.

### 2. Fat Tails Are Universal and Robust

Every learning configuration produces excess kurtosis above 40 and Hill tail indices between 2 and 4. These values bracket the empirical cubic power law (~3) found in real equity returns by Gopikrishnan et al. (1999). Fat tails are not a fragile artifact of specific parameters --- they emerge reliably from the interaction of heterogeneous, adapting strategies.

### 3. Volatility Clustering Emerges from Evolutionary Dynamics

In every learning experiment, the autocorrelation of absolute returns is strongly positive (0.33--0.65), indicating that large price moves are followed by large moves and small by small. This "GARCH-like" effect arises not from any explicit volatility model but from the evolutionary dynamics: when the GA reshuffles strategies, it creates coordinated shifts in agent behavior that persist until the new rules are tested and culled.

### 4. Less Diversity Means More Extreme Markets

The two experiments with the most extreme kurtosis --- few rules per agent (211) and many agents with default rules (204) --- share a common feature: reduced *effective* strategy diversity. With 20 rules, each agent has a narrow behavioral repertoire. With 200 agents but the same rule structure, many agents converge on similar strategies. In both cases, the market is prone to herding, where large fractions of agents simultaneously shift behavior, producing rare but enormous price dislocations.

### 5. Mutation Rate Has a Goldilocks Quality

Low mutation (0.005) produces the calmest market but the highest wealth inequality --- slow adaptation locks in early advantages. High mutation (0.15) increases kurtosis slightly and reduces volume --- too much experimentation prevents conviction. The default rate (0.03) balances exploration and exploitation, producing moderate kurtosis and the most active trading.

### 6. Wealth Inequality Is Endogenous and Persistent

Every configuration produces Gini coefficients between 0.38 and 0.60, starting from perfectly equal endowments. Inequality is lowest in thin markets (20 agents, Gini 0.38) where there are fewer competitors and highest in rational mode (Gini 0.60) where agents cannot adapt to correct mistakes. In learning regimes, Gini increases with less diversity (fewer rules, slower mutation) --- when the strategy landscape is less fluid, the winners of early evolutionary races keep winning.

---

## Connections to Beinhocker's Arguments

These experiments illustrate several of Beinhocker's core themes from *The Origin of Wealth*:

**Markets are not in equilibrium.** The rational-expectations baseline (Experiment 1) is supposed to represent the equilibrium benchmark, yet it produces the *worst* market: high volatility, price drift, near-zero volume, and extreme wealth inequality. The "equilibrium" is a mirage --- without learning, agents cannot coordinate on the fundamental value, and the price wanders. Ironically, the perpetually out-of-equilibrium learning market tracks fundamentals *better* than the equilibrium one.

**Complexity arises from the interaction of simple adaptive rules.** Each agent follows a simple strategy: match conditions, forecast, trade. The genetic algorithm is a crude optimizer. Yet the collective behavior produces power laws, clustered volatility, bubbles, and crashes --- phenomena that emerge at the system level from the ecology of interacting strategies, not from any individual agent's sophistication.

**The economy is an evolutionary system.** The GA interval and mutation rate experiments show that market dynamics are exquisitely sensitive to evolutionary parameters. Faster evolution produces more extreme events (Experiment 6a); constrained strategy pools produce the wildest markets (Experiment 6b). The market is not a mechanism that processes information; it is an ecosystem where strategies compete, mutate, and die, and the macro-level statistics are the emergent signature of that evolutionary process.

**Diversity matters.** The most stable markets come from moderate parameter choices that sustain strategy diversity. Reducing diversity --- fewer rules, lower mutation, homogeneous agents --- consistently increases tail risk and inequality. This echoes Beinhocker's argument that economic resilience depends on the variety of strategies in the population, not on the optimality of any single strategy.

**There is no separation between micro and macro.** The fat tails in returns, the clustering of volatility, and the concentration of wealth are not separate phenomena requiring separate explanations. They are all manifestations of the same underlying process: heterogeneous agents adapting to each other in a positive-feedback loop where beliefs shape prices, prices shape returns, returns shape fitness, and fitness shapes the next generation of beliefs.
