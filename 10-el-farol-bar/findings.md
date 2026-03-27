# El Farol Bar Problem -- Findings

## Experiment Results

### Experiment 1: Baseline (N=100, threshold=60, 10 strategies, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 57.34 |
| Std attendance | 9.97 |
| Min / Max | 17 / 91 |
| % weeks above threshold | 40.0% |
| Threshold crossings | 108 |
| Crossing rate | 0.543 |
| Autocorrelation (lag-1) | -0.206 |
| Mean accuracy | 0.449 |

**Top strategies:** threshold-70 (25), random-60% (17), periodic-2 (16), mean-of-8 (12)

**Key finding:** The system self-organizes with mean attendance near the threshold (57.3 vs. 60). High crossing rate (0.543) means attendance flips above/below threshold nearly every other week. Negative autocorrelation confirms the characteristic oscillation pattern. Mean accuracy below 50% demonstrates the self-referential paradox -- no strategy can consistently "win."

---

### Experiment 2: Small Population (N=50, threshold=60, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 46.89 |
| Std attendance | 0.99 |
| Min / Max | 34 / 47 |
| % weeks above threshold | 0.0% |
| Threshold crossings | 0 |
| Crossing rate | 0.000 |
| Autocorrelation (lag-1) | 0.965 |
| Mean accuracy | 0.938 |

**Key finding:** With only 50 agents and a threshold of 60, the problem becomes trivial. All agents can comfortably attend simultaneously. The system locks into a stable state with near-perfect accuracy and zero oscillation. This is NOT the interesting regime -- the self-referential paradox only emerges when the threshold creates genuine scarcity (threshold < N). The high autocorrelation (0.965) indicates herding: agents all learn that "go" is always correct.

---

### Experiment 3: Large Population (N=200, threshold=60, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 66.94 |
| Std attendance | 19.89 |
| Min / Max | 30 / 136 |
| % weeks above threshold | 56.5% |
| Threshold crossings | 102 |
| Crossing rate | 0.513 |
| Autocorrelation (lag-1) | -0.066 |
| Mean accuracy | 0.448 |

**Key finding:** With 200 agents competing for 60 spots, the problem intensifies. Oscillations are *larger* in absolute terms (std=19.89 vs. 9.97 baseline) because more agents must coordinate. Mean attendance is above threshold (66.9), reflecting the difficulty of coordination with a very constrained resource (only 30% capacity). Autocorrelation is nearly zero, suggesting nearly random attendance patterns -- the system is maximally unpredictable.

---

### Experiment 4: Low Threshold (N=100, threshold=30, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 32.80 |
| Std attendance | 8.66 |
| Min / Max | 13 / 61 |
| % weeks above threshold | 56.0% |
| Threshold crossings | 107 |
| Crossing rate | 0.538 |
| Autocorrelation (lag-1) | -0.097 |
| Mean accuracy | 0.454 |

**Top strategies:** periodic-5 (31), threshold-20 (18), random-40% (12)

**Key finding:** Lowering the threshold to 30 (only 30% capacity) produces qualitatively similar dynamics to baseline: mean near threshold, high crossing rate, low accuracy. The system self-organizes around the new constraint. Notably, periodic-5 dominates -- with severe scarcity, cyclic strategies that "take turns" become more viable.

---

### Experiment 5: Few Strategies (k=3, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 58.12 |
| Std attendance | 7.94 |
| Min / Max | 26 / 75 |
| % weeks above threshold | 37.5% |
| Threshold crossings | 115 |
| Crossing rate | 0.578 |
| Autocorrelation (lag-1) | -0.328 |
| Mean accuracy | 0.468 |

**Key finding:** With only 3 strategies per agent, the system still self-organizes (mean 58.1 vs. threshold 60). However, autocorrelation is more strongly negative (-0.328), indicating more predictable oscillation -- agents have fewer tools to break out of reactive cycles. The crossing rate is the highest (0.578) of any experiment, suggesting more mechanical back-and-forth. Limited strategy diversity leads to more correlated behavior.

---

### Experiment 6: Many Strategies (k=20, seed=42)

| Metric | Value |
|---|---|
| Mean attendance | 59.02 |
| Std attendance | 7.72 |
| Min / Max | 22 / 89 |
| % weeks above threshold | 43.0% |
| Threshold crossings | 116 |
| Crossing rate | 0.583 |
| Autocorrelation (lag-1) | -0.138 |
| Mean accuracy | 0.460 |

**Top strategies:** random-60% (31), periodic-2 (21), random-50% (20), threshold-70 (20)

**Key finding:** With 20 strategies, mean attendance is almost exactly at threshold (59.0 vs. 60). The richer ecology provides better self-organization. Autocorrelation is weaker negative (-0.138), suggesting less mechanical oscillation. The system is somewhat less predictable than the few-strategies case, which aligns with Arthur's insight that strategy diversity creates complex, hard-to-predict dynamics. Interestingly, random and periodic strategies dominate, suggesting that when the ecology is rich enough, simple randomization outperforms sophisticated forecasting.

---

## Cross-Experiment Comparison

| Experiment | Mean Att. | Std | Crossing Rate | AC(1) | Accuracy |
|---|---|---|---|---|---|
| Baseline (N=100, T=60, k=10) | 57.3 | 10.0 | 0.543 | -0.206 | 0.449 |
| Small Pop (N=50, T=60) | 46.9 | 1.0 | 0.000 | 0.965 | 0.938 |
| Large Pop (N=200, T=60) | 66.9 | 19.9 | 0.513 | -0.066 | 0.448 |
| Low Thresh (N=100, T=30) | 32.8 | 8.7 | 0.538 | -0.097 | 0.454 |
| Few Strat (N=100, T=60, k=3) | 58.1 | 7.9 | 0.578 | -0.328 | 0.468 |
| Many Strat (N=100, T=60, k=20) | 59.0 | 7.7 | 0.583 | -0.138 | 0.460 |

## Emergent Behaviors

### 1. Self-Organization Around the Threshold
In all experiments where the threshold creates genuine scarcity (threshold < N), mean attendance gravitates toward the threshold. This is not designed into the system -- it emerges from the competitive ecology of strategies. This is one of the clearest demonstrations of emergent order in economic models.

### 2. The Self-Referential Paradox in Action
Mean accuracy hovers around 45-47% in all scarcity scenarios -- *worse* than coin-flipping. This directly demonstrates Arthur's insight: when your prediction affects the thing you're predicting, no strategy can be consistently correct. The moment a strategy becomes popular, it invalidates itself.

### 3. Oscillation Without External Shocks
All scarcity scenarios show crossing rates of 0.51-0.58, meaning the system crosses the threshold roughly every 2 weeks. These oscillations are *endogenous* -- generated purely by the interaction of strategies, with no external forcing.

### 4. Strategy Ecology Is Path-Dependent
Different experiments produce different dominant strategies, even with the same seed. The ecology is sensitive to the competitive environment. Periodic and random strategies tend to do well because they are less susceptible to the self-referential trap -- they don't try to outsmart a system that punishes outsmarting.

### 5. Strategy Diversity Reduces Predictability
Comparing k=3 vs. k=20: more strategies per agent reduces autocorrelation magnitude (-0.328 to -0.138). A richer ecology of mental models makes the system harder to predict, confirming that complexity arises from diversity of reasoning.

### 6. Population Size Amplifies Coordination Failure
With N=200 competing for 60 spots, std deviation nearly doubles (19.9 vs. 10.0). The coordination problem scales with the ratio of agents to capacity, not just the absolute numbers.

## Connection to Beinhocker's Themes

### Inductive Reasoning
The agents in this simulation embody Beinhocker's concept of inductive reasoning. They don't solve an optimization problem; they maintain a portfolio of heuristics and bet on what has worked. This is how real people navigate complex environments -- not through deductive proof but through adaptive pattern matching.

### Perpetual Novelty and Disequilibrium
The system never reaches equilibrium. Even after 200 weeks, attendance continues to oscillate. Strategy dominance shifts over time. This is Beinhocker's "perpetual novelty" -- the economy as a system that is always in process, never at rest.

### Ecology of Mental Models
The strategy distribution data shows a rich ecology where no single approach dominates. Contrarians coexist with trend-followers; random strategies coexist with sophisticated pattern detectors. This diversity is essential -- if everyone used the same strategy, the system would either collapse or explode. The economy needs cognitive diversity.

### Complexity from Simple Rules
Each agent follows a simple rule: use the strategy that has worked best. Yet the aggregate behavior is complex, unpredictable, and exhibits emergent properties (self-organization around the threshold, endogenous oscillation, sub-50% accuracy). Simple micro-level rules produce rich macro-level dynamics -- a hallmark of complex adaptive systems.

### The Limits of Rational Expectations
The El Farol problem is a direct challenge to the rational expectations hypothesis in economics. There is no way to form a "rational expectation" about attendance because your expectation changes your behavior which changes the outcome. Beinhocker argues this self-referentiality is *pervasive* in real economies, not a special case. The El Farol bar is the economy in miniature.
