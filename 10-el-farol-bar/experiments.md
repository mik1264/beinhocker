# El Farol Bar Problem -- Experiments

## Theoretical Background

### The Problem (Arthur 1994)
The El Farol Bar Problem, introduced by W. Brian Arthur in "Inductive Reasoning and Bounded Rationality" (1994), is a canonical model of bounded rationality and inductive reasoning in economics.

**Setup:** N agents (typically 100) independently decide each week whether to attend a bar. The bar is enjoyable if attendance is at or below a comfort threshold (typically 60), but overcrowded and unpleasant if more than 60 attend.

**The Self-Referential Paradox:** No deductively rational solution exists. If all agents share the same prediction model, the model invalidates itself:
- If the model predicts low attendance, everyone goes, making it wrong
- If the model predicts high attendance, no one goes, making it wrong

**Arthur's Resolution:** Agents must reason *inductively* -- each maintains a diverse pool of prediction heuristics (mental models) and uses whichever has performed best recently. This creates an evolving ecology of strategies where:
- No single strategy dominates permanently
- Attendance oscillates endogenously around the threshold
- The system self-organizes without equilibrium

### Beinhocker's Interpretation (The Origin of Wealth, Ch. 6)
Beinhocker uses the El Farol problem to illustrate a fundamental shift from traditional economics:
1. **Inductive vs. Deductive Reasoning:** Real agents don't solve optimization problems; they use pattern recognition and adaptive heuristics
2. **Perpetual Novelty:** The strategy ecology never settles; new patterns continuously emerge and dissolve
3. **Self-Referentiality:** The agents' beliefs about the system *are part of* the system -- a hallmark of complex adaptive systems
4. **No Equilibrium:** The system finds a statistical steady state (mean attendance near threshold) without ever reaching a fixed equilibrium

### Strategy Types in This Implementation
- **Last-week mirror:** Go if last week's attendance was below threshold
- **Mean-of-N:** Go if average of last N weeks was below threshold
- **Trend:** Extrapolate the trend from last two weeks
- **Contrarian:** Do the opposite of what last week suggests
- **Random:** Go with a fixed probability
- **Threshold rules:** Use a personal threshold different from the official one
- **Periodic:** Attend on a fixed cycle
- **Weighted average (EMA):** Exponentially weighted moving average
- **Cycle detector:** Look for alternating patterns
- **Median rule:** Use median of recent window

## Planned Experiments

### 1. Baseline (N=100, threshold=60, 10 strategies)
Reproduce Arthur's canonical result. Expect attendance to oscillate around 60 with no convergence to equilibrium.

### 2. Population Size Effects
- **Small (N=50):** Fewer agents, more sampling noise. Does the system still self-organize?
- **Large (N=200):** More agents, smoother dynamics. Does the law of large numbers reduce oscillation?

### 3. Threshold Sensitivity
- **Low threshold (T=30):** Only 30% of agents can comfortably attend. How does the system handle more constrained capacity?
- **High threshold (T=80):** More permissive. Does this reduce oscillation?

### 4. Strategy Diversity
- **Few strategies (k=3):** Limited repertoire. Expect more herding and larger oscillations.
- **Many strategies (k=20):** Rich ecology. Does more diversity dampen or amplify fluctuations?

### 5. Memory and Adaptation
- How does the memory window affect oscillation frequency?
- Do strategies with longer memory outperform reactive ones?

### 6. Asymmetric Payoffs
- What if the cost of going to a crowded bar differs from the cost of missing a good night?
- How does this shift the equilibrium attendance level?

## Key Metrics
- Mean attendance (should be near threshold)
- Standard deviation of attendance (oscillation amplitude)
- Threshold crossing rate (frequency of above/below switches)
- Autocorrelation (predictability of attendance)
- Strategy diversity (entropy of strategy usage distribution)
- Mean decision accuracy (fraction making "correct" choice)
