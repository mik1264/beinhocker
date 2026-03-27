# SFI Artificial Stock Market: Experiment Findings

## Overview

Five experiments were run on the SFI Artificial Stock Market simulation to explore how agent learning, mutation pressure, population size, risk preferences, and evolutionary tempo shape emergent market dynamics. All experiments use seed 42 and 2000 ticks for reproducibility. A bug in the CLI was fixed during the process: the `--rational` flag was not disabling learning mode due to an argparse default conflict (line 85 of `cli.py` now reads `learning = not args.rational`).

---

## Experiment 1: Baseline Learning vs Rational

**Commands:**
```
python3 cli.py --learning --ticks 2000 --seed 42
python3 cli.py --rational --ticks 2000 --seed 42
```

| Metric | Learning | Rational |
|--------|----------|----------|
| Mean Price | 102.37 | 118.19 |
| Std Price | 7.26 | 23.43 |
| Fundamental Value (final) | 95.64 | 107.81 |
| Mean Return | -0.0000 | -0.0109 |
| Volatility (std return) | 0.0423 | 0.0833 |
| Annualized Volatility | 0.67 | 1.32 |
| Excess Kurtosis | **45.26** | 4.79 |
| Skewness | 1.13 | -2.39 |
| Return Autocorrelation (lag-1) | -0.357 | -0.130 |
| Volatility Clustering (|r| AC1) | **0.489** | -0.055 |
| Tail Index (Hill) | **2.55** | 46.38 |
| Mean Volume | 5.32 | 0.05 |
| Gini Coefficient | 0.43 | 0.60 |

**Analysis:** The contrast is stark. The rational market -- where each agent holds a single, fixed forecasting rule -- produces double the volatility, persistent overpricing (mean 118 vs fundamental ~108), and near-zero volume. Without heterogeneous beliefs, there is almost no motive to trade. The return distribution is mildly leptokurtic (kurtosis 4.8) but shows no volatility clustering and has thin tails (Hill index 46).

The learning market is qualitatively different. Price tracks fundamental value much more closely. Volatility drops by half. But the return distribution becomes dramatically non-Gaussian: kurtosis leaps to 45, the Hill tail index drops to 2.55 (close to the empirical cubic power law of ~3 found in real equity markets), and volatility clustering emerges strongly at 0.49. Volume jumps 100-fold as heterogeneous, evolving beliefs generate disagreement and trade.

Wealth inequality is lower under learning (Gini 0.43 vs 0.60) -- adaptive agents can correct mistakes and recover from poor initial positions, while rational agents are locked into their initial rule forever.

---

## Experiment 2: High Mutation Rate (0.10 vs default 0.03)

**Command:**
```
python3 cli.py --learning --ticks 2000 --mutation-rate 0.10 --seed 42
```

| Metric | Default (0.03) | High Mutation (0.10) |
|--------|---------------|---------------------|
| Mean Price | 102.37 | 100.96 |
| Std Price | 7.26 | 7.75 |
| Volatility (std return) | 0.0423 | 0.0417 |
| Excess Kurtosis | 45.26 | **51.69** |
| Skewness | 1.13 | 0.26 |
| Volatility Clustering | 0.489 | **0.555** |
| Tail Index (Hill) | 2.55 | **2.50** |
| Mean Volume | 5.32 | 5.16 |
| Gini Coefficient | 0.43 | 0.43 |

**Analysis:** Tripling the mutation rate from 0.03 to 0.10 amplifies the market's "stylized facts" without fundamentally changing its character. Kurtosis rises 14% to 51.7, volatility clustering strengthens from 0.49 to 0.56, and the Hill tail index drops to 2.50 -- indicating even heavier tails. Mean price centers slightly closer to fundamental value. Skewness drops from 1.13 to near zero, suggesting a more symmetric return distribution where extreme moves are equally likely in both directions.

The mechanism: higher mutation injects more strategy diversity into the population. Agents more frequently try novel rules, creating bursts of exploratory behavior that manifest as larger price displacements. The market is slightly more volatile in its extremes but similarly volatile on average. Volume stays nearly the same, indicating that mutation-driven exploration does not reduce trading conviction significantly at this rate.

This confirms Beinhocker's insight that higher mutation pressure sustains the "edge of chaos" dynamics that generate realistic market statistics.

---

## Experiment 3: Large Population (100 agents vs default 25)

**Command:**
```
python3 cli.py --learning --ticks 2000 --agents 100 --seed 42
```

| Metric | 25 Agents | 100 Agents |
|--------|-----------|------------|
| Mean Price | 102.37 | 101.02 |
| Std Price | 7.26 | 6.88 |
| Volatility (std return) | 0.0423 | **0.0267** |
| Excess Kurtosis | 45.26 | **18.04** |
| Skewness | 1.13 | 0.38 |
| Volatility Clustering | 0.489 | **0.232** |
| Tail Index (Hill) | 2.55 | **3.85** |
| Mean Volume | 5.32 | **16.53** |
| Gini Coefficient | 0.43 | **0.46** |

**Analysis:** Quadrupling the population produces a dramatically calmer market. Return volatility drops 37% (from 0.042 to 0.027), kurtosis falls 60% (from 45 to 18), and volatility clustering weakens substantially (from 0.49 to 0.23). The Hill tail index rises to 3.85, indicating thinner tails -- closer to the boundary where the cubic power law transitions toward Gaussian behavior.

The key mechanism is **diversification of strategies**. With 100 agents, the market contains a richer ecology of forecasting rules. When one group of agents shifts behavior (due to GA evolution), the remaining agents act as a stabilizing buffer. Extreme herding events become rarer because it is harder for 100 agents to accidentally align on the same strategy shift simultaneously.

Volume triples (from 5.3 to 16.5), reflecting greater disagreement among a larger, more diverse population. Yet wealth inequality slightly increases (Gini 0.46 vs 0.43) -- with more competitors, the best-adapted agents capture a somewhat larger relative share.

Fat tails persist (kurtosis 18 is still far above the Gaussian value of 0), confirming that the emergence of non-Gaussian statistics is robust to population size. But the effect weakens -- this market is closer to efficient-market predictions while still retaining the qualitative signatures of complexity.

---

## Experiment 4: Low Risk Aversion (0.1 vs default 0.5)

**Command:**
```
python3 cli.py --learning --ticks 2000 --risk-aversion 0.1 --seed 42
```

| Metric | Default (0.5) | Low Risk Aversion (0.1) |
|--------|--------------|------------------------|
| Mean Price | 102.37 | 102.94 |
| Std Price | 7.26 | **8.67** |
| Volatility (std return) | 0.0423 | **0.0500** |
| Excess Kurtosis | 45.26 | **69.50** |
| Skewness | 1.13 | **2.78** |
| Volatility Clustering | 0.489 | **0.410** |
| Tail Index (Hill) | 2.55 | 2.75 |
| Mean Volume | 5.32 | **9.73** |
| Gini Coefficient | 0.43 | 0.44 |

**Analysis:** Reducing risk aversion 5-fold (from 0.5 to 0.1) unleashes dramatically more aggressive trading. The demand function `x = E[excess return] / (lambda * variance)` means a 5x reduction in lambda produces 5x larger position sizes for the same expected return. The consequences are visible across every metric.

Volume nearly doubles (from 5.3 to 9.7) as agents take larger positions. Return volatility increases 18% (from 0.042 to 0.050). But the most striking effect is on tail risk: kurtosis jumps 54% to 69.5 and positive skewness more than doubles to 2.78, indicating that the market is now prone to larger upward price spikes -- proto-bubbles driven by aggressive buying.

Volatility clustering weakens slightly (from 0.49 to 0.41), suggesting that with more aggressive trading, volatility is more uniformly elevated rather than concentrated in bursts. The Hill tail index rises slightly from 2.55 to 2.75.

Wealth inequality stays nearly unchanged (Gini 0.44 vs 0.43), despite the much more aggressive market. The higher trading volume creates both bigger winners and bigger losers, but the net distributional effect is small.

This experiment illustrates how risk preferences at the micro level propagate to systemic tail risk. The same ecology of strategies, the same evolutionary dynamics, but less risk-averse agents amplify small forecast disagreements into larger price dislocations. This is directly relevant to financial crisis dynamics, where declining risk aversion (rising leverage) historically precedes market instability.

---

## Experiment 5: Fast Evolution (GA interval 50 vs default 250)

**Command:**
```
python3 cli.py --learning --ticks 2000 --ga-interval 50 --seed 42
```

| Metric | Default (250) | Fast GA (50) |
|--------|--------------|--------------|
| Mean Price | 102.37 | 100.52 |
| Std Price | 7.26 | 7.59 |
| Volatility (std return) | 0.0423 | 0.0407 |
| Excess Kurtosis | 45.26 | **140.93** |
| Skewness | 1.13 | **4.97** |
| Volatility Clustering | 0.489 | **0.449** |
| Tail Index (Hill) | 2.55 | 2.79 |
| Mean Volume | 5.32 | **3.45** |
| Gini Coefficient | 0.43 | **0.47** |

**Analysis:** Quintupling the GA frequency (interval 50 vs 250, meaning each agent evolves strategies on average every 50 ticks rather than every 250) produces the most extreme tail behavior of any experiment. Kurtosis triples to 141 and skewness reaches 4.97 -- the market produces rare but enormous upward price dislocations.

Paradoxically, average volatility is essentially unchanged (0.041 vs 0.042). The market is not noisier in its typical behavior -- it is the *extreme* events that multiply. This is the signature of a Red Queen dynamic: agents constantly reshuffle their strategies, and when multiple agents happen to evolve in the same direction simultaneously, the resulting correlated behavior change creates a massive temporary imbalance in demand.

Volume drops 35% (from 5.3 to 3.4). This is counterintuitive at first but makes sense: frequent rule replacement means agents spend less time with well-calibrated, high-conviction rules. New, untested rules produce smaller position demands until they are validated by experience.

Wealth inequality increases (Gini 0.47 vs 0.43). Faster evolution amplifies the advantage of agents who happen to adopt winning strategies early in an evolutionary cycle, before the strategy becomes crowded.

---

## Key Metrics Comparison Table

| Experiment | Volatility | Kurtosis | Vol. Cluster | Tail Index | Volume | Gini |
|------------|-----------|----------|-------------|------------|--------|------|
| 1a. Learning (baseline) | 0.0423 | 45.3 | 0.489 | 2.55 | 5.32 | 0.43 |
| 1b. Rational (no learning) | 0.0833 | 4.8 | -0.055 | 46.38 | 0.05 | 0.60 |
| 2. High Mutation (0.10) | 0.0417 | 51.7 | 0.555 | 2.50 | 5.16 | 0.43 |
| 3. Large Pop (100 agents) | 0.0267 | 18.0 | 0.232 | 3.85 | 16.53 | 0.46 |
| 4. Low Risk Aversion (0.1) | 0.0500 | 69.5 | 0.410 | 2.75 | 9.73 | 0.44 |
| 5. Fast GA (interval 50) | 0.0407 | 140.9 | 0.449 | 2.79 | 3.45 | 0.47 |

---

## Emergent Behaviors Observed

### 1. Fat Tails Are Universal Under Learning

Every learning configuration produces excess kurtosis far above zero (18 to 141) and Hill tail indices between 2.5 and 3.9. These bracket the empirical cubic power law (~3) documented in real equity returns. Fat tails are not a fragile parameter-dependent artifact -- they are the robust emergent signature of adaptive agents co-evolving in a market. The rational baseline, by contrast, produces near-Gaussian tails (kurtosis 4.8, Hill index 46). Fat tails require learning.

### 2. Volatility Clustering Requires Evolutionary Dynamics

Positive autocorrelation of absolute returns (0.23 to 0.56 across learning experiments, vs -0.055 for rational) emerges without any explicit volatility model. The mechanism is the genetic algorithm: when the GA reshuffles strategies for a cluster of agents, their coordinated behavior shift produces a period of elevated volatility that persists until the new rules are tested, culled, or adapted. This is a GARCH-like effect generated entirely from the bottom up.

### 3. Evolutionary Tempo Controls Tail Extremity

The GA interval has the single strongest effect on kurtosis of any parameter tested. Reducing the interval from 250 to 50 triples kurtosis (45 to 141). Faster evolution means more frequent waves of correlated strategy changes, producing rarer but more extreme price events. This is a form of endogenous systemic risk: the same mechanism that allows agents to adapt (evolution) also generates the market's most dangerous events (fat tails).

### 4. Risk Aversion Shapes Bubble Dynamics

Low risk aversion (0.1 vs 0.5) increases volume 83%, kurtosis 54%, and skewness 146%. The market becomes distinctly bubble-prone, with large positive skewness indicating that upward price spikes are much more extreme than downward corrections. This is consistent with real-world observations that declining risk aversion (or rising leverage) precedes speculative bubbles.

### 5. Population Size Has a Stabilizing Effect

More agents (100 vs 25) reduce volatility, kurtosis, and volatility clustering substantially while increasing volume. A larger, more diverse ecology of strategies acts as a buffer against herding events. However, fat tails still persist -- the market remains a complex adaptive system, just a somewhat calmer one. This result is consistent with the empirical observation that deeper, more liquid markets tend to be less volatile but are not immune to tail events.

### 6. Wealth Inequality Emerges Endogenously

Starting from identical endowments, every configuration produces Gini coefficients of 0.43-0.60. The rational baseline (0.60) has the highest inequality -- without adaptation, agents who drew poor initial rules can never recover. Learning reduces inequality (0.43 baseline) by allowing agents to evolve better strategies over time. Among learning experiments, faster evolution and larger populations slightly increase inequality (0.47, 0.46), suggesting that more dynamic competitive environments have stronger winner-take-more dynamics.

---

## Connection to Beinhocker's Thesis

These experiments provide direct computational evidence for several of the central arguments in *The Origin of Wealth*:

**"Traditional economics is wrong about equilibrium."** The rational-expectations baseline (Experiment 1b) is the theoretical gold standard of neoclassical finance -- it should represent the most "efficient" market. Instead, it produces the worst outcomes: the highest volatility, largest mispricing, near-zero liquidity, and most extreme wealth inequality. The perpetually out-of-equilibrium learning market tracks fundamentals better, trades more actively, and distributes wealth more equally. Equilibrium is not a useful approximation; it is the opposite of what happens.

**"The economy is a complex adaptive system."** Every stylized fact of real financial markets -- fat tails, volatility clustering, excess volume, wealth concentration -- emerges spontaneously from the interaction of simple adaptive agents. No single agent is sophisticated; the complexity is a system-level property arising from evolutionary competition among heterogeneous strategies. This is the hallmark of a complex adaptive system.

**"Evolution, not optimization, drives economic dynamics."** The GA interval experiment (Experiment 5) is the most revealing. When evolution runs faster, the market does not become more efficient -- it becomes more extreme, with kurtosis tripling. The evolutionary process that allows agents to find better strategies is the same process that generates systemic risk. Adaptation and instability are two sides of the same coin. This is precisely Beinhocker's point: economies are evolutionary systems, and you cannot have adaptation without the creative destruction that comes with it.

**"Diversity is a source of resilience."** The large-population experiment (Experiment 3) shows that a richer ecology of strategies stabilizes the market. More agents mean more diverse approaches to forecasting, which acts as a natural hedge against herding. Conversely, the fast-GA experiment (Experiment 5) creates periods of reduced effective diversity (many agents simultaneously adopting new untested rules), producing the most extreme tail events. Beinhocker argues that the resilience of economic systems depends on maintaining a diverse population of business strategies and organizational forms -- these simulations provide a precise computational analogy.

**"There is no separation between micro and macro."** The risk aversion experiment (Experiment 4) shows how a micro-level preference parameter (individual risk tolerance) propagates directly into macro-level systemic properties (market-wide kurtosis, skewness, and volume). There is no aggregation trick, no representative agent -- the macro statistics emerge from the micro interactions. This is the methodological core of Beinhocker's complexity economics: you cannot understand the macro without simulating the micro.
