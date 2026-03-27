# Rigids vs Flexibles: Experiment Findings

Experiments run on the Harrington/Beinhocker organizational adaptation simulation.
All runs use seed 42 for reproducibility, 500 ticks, 4-level hierarchy (40 agents)
unless otherwise noted.

---

## Experiment 1: Baseline (default parameters)

**Command:** `python3 cli.py --ticks 500 --seed 42`

**Parameters:** stability=100, punctuated mode, 50% initial rigid fraction, experience weight=0.1

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 27     | 70.4%  | 29.6%     |
| L1    | 9      | 77.8%  | 22.2%     |
| L2    | 3      | 100.0% | 0.0%      |
| Top   | 1      | 100.0% | 0.0%      |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.1943 |
| Rigid avg performance   | 1.1906 |
| Flexible avg performance| 1.1057 |
| Environment switches    | 4      |
| Avg transition cost     | +0.3368|
| Avg recovery time       | 15.0 ticks |

### Rigid Fraction Trajectory

The tournament's selection pressure is visible in the time series:

- Tick 0: 45% rigid overall, top level starts flexible
- Tick 50: 65% rigid, top already 100% rigid
- Tick 100: 85% rigid, L0 at 78% rigid
- Tick 200: 97.5% rigid -- near total purge of flexibles
- Tick 232: **First environment switch** -- organization is 96.3% rigid at L0, 100% above

At the moment of the first switch, the organization had systematically eliminated
almost all adaptive capacity. The result was a catastrophic performance drop of
+0.87 (from 1.49 to 0.62) with a 20-tick recovery period.

### Emergent Behavior

**The purge-crash cycle.** During each stable period, the tournament ruthlessly
promotes rigids whose fixed strategy matches the current environment. Flexibles,
penalized by observation noise (10% misread rate), steadily lose ground. By the
time the environment switches, the organization is a monoculture -- and the crash
is severe. The organization then partially recovers as new agents with correct
strategies enter at the bottom, but the pipeline is slow: it takes 15-20 ticks for
correct-strategy agents to filter up through the hierarchy.

---

## Experiment 2: High Stability (stability=500)

**Command:** `python3 cli.py --ticks 500 --stability 500 --seed 42`

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 27     | 96.3%  | 3.7%      |
| L1    | 9      | 100.0% | 0.0%      |
| L2    | 3      | 100.0% | 0.0%      |
| Top   | 1      | 100.0% | 0.0%      |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.4389 |
| Rigid avg performance   | 1.4453 |
| Flexible avg performance| 0.7730 |
| Environment switches    | 0      |

### The Thatcher Trap

With no environment switches across the entire run, the tournament had 500
uninterrupted ticks to optimize. The result is near-total rigidity: 97.5% overall,
with exactly one flexible agent remaining (a brand-new entrant at level 0 with
zero experience).

Key timeline:
- **Tick 1:** Top level becomes 100% rigid
- **Tick 38:** L1 becomes 100% rigid
- **Tick 200:** Only one flexible agent remains at L0

Performance is the highest of all experiments (1.44), but the organization is
maximally fragile. This is the Thatcher trap: the leader is perfectly matched to
the current regime, the organization has purged all dissent, and performance metrics
look excellent. But the first disruption will be devastating because there is
literally no adaptive capacity left.

The flexible agents' average performance (0.77) is roughly half that of rigids
(1.45). In a stable world, the data "proves" that flexibles are dead weight. The
rational response is to eliminate them. This is exactly the logic that makes the
trap so dangerous -- the evidence for purging flexibility is strongest precisely
when the need for flexibility is greatest.

---

## Experiment 3: High Volatility (stability=20)

**Command:** `python3 cli.py --ticks 500 --stability 20 --seed 42`

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 27     | 70.4%  | 29.6%     |
| L1    | 9      | 66.7%  | 33.3%     |
| L2    | 3      | 33.3%  | 66.7%     |
| Top   | 1      | 0.0%   | 100.0%    |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.0441 |
| Rigid avg performance   | 0.9723 |
| Flexible avg performance| 1.1784 |
| Environment switches    | 24     |
| Avg transition cost     | +0.0413|
| Avg recovery time       | 6.0 ticks |

### Flexible Dominance and the Inverted Hierarchy

This is the most striking result. With 24 environment switches in 500 ticks, the
hierarchy inverts compared to the baseline:

- **Top level: 100% flexible** (vs. 100% rigid in baseline)
- **L2: 67% flexible** (vs. 0% flexible in baseline)
- Flexibles outperform rigids on average: 1.18 vs. 0.97

The inversion happens because frequent switches prevent rigids from accumulating
enough of a run to dominate the tournament. A rigid agent playing "A" might win for
15 ticks, get promoted, and then the environment switches to "B" -- suddenly they
are the worst performer and get demoted. Flexibles, who track the environment
(with some noise), maintain consistent above-average performance regardless of which
state the environment is in.

Transition costs are nearly zero (+0.04) and many individual transitions actually
show *negative* cost (performance improves after switching), because at any given
moment many rigids are already mismatched. Recovery is fast at 6 ticks.

This is the Clinton/Blair model: pragmatic, poll-reading leadership that sacrifices
peak performance for resilience. Overall performance (1.04) is lower than the
stable environment (1.44), but the organization never experiences a catastrophic
crash.

---

## Experiment 4: Random Mode

**Command:** `python3 cli.py --ticks 500 --mode random --seed 42`

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 27     | 85.2%  | 14.8%     |
| L1    | 9      | 100.0% | 0.0%      |
| L2    | 3      | 100.0% | 0.0%      |
| Top   | 1      | 100.0% | 0.0%      |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.2559 |
| Rigid avg performance   | 1.2572 |
| Flexible avg performance| 0.9488 |
| Environment switches    | 3      |
| Avg transition cost     | +0.2243|
| Avg recovery time       | 9.0 ticks |

### Punctuated vs. Random: The Pattern Matters

Random mode with stability=100 gives each tick a 1% chance of switching
independently. This produced only 3 switches in 500 ticks (vs. 4 in punctuated
mode), but crucially, the switching *pattern* is different. In punctuated mode,
switches come in bursts separated by long stable periods. In random mode, switches
are independent events.

The result resembles the high-stability case more than the volatile case: rigids
dominate all levels above L0, reaching 100% at L1 through Top. The organization
is 92.5% rigid overall.

The key insight: **the pattern of environmental change matters as much as its
frequency.** Punctuated equilibrium (long stability, sudden shifts) creates a
specific pathology: the organization has time to over-specialize during stable
periods, making the eventual shock maximally painful. Random variation, even at
the same average rate, produces a different organizational structure because
switches are less predictable and the organization cannot settle as deeply into
any single configuration.

One dramatic transition stands out: at tick 333, after 272 ticks of stability in
state A, a switch caused a +0.88 performance drop -- nearly identical to the worst
baseline transition. Long runs without switches in random mode can be just as
dangerous as in punctuated mode.

---

## Experiment 5: Deep Hierarchy (6 levels)

**Command:** `python3 cli.py --ticks 500 --levels 6 --seed 42`

**Parameters:** 6 levels, branching factor 3, 364 total agents

### Final Composition

| Level | Agents | Rigid%  | Flexible% |
|-------|--------|---------|-----------|
| L0    | 243    | 57.2%   | 42.8%     |
| L1    | 81     | 100.0%  | 0.0%      |
| L2    | 27     | 100.0%  | 0.0%      |
| L3    | 9      | 100.0%  | 0.0%      |
| L4    | 3      | 100.0%  | 0.0%      |
| Top   | 1      | 100.0%  | 0.0%      |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.1916 |
| Rigid avg performance   | 1.1002 |
| Flexible avg performance| 1.3346 |
| Environment switches    | 5      |
| Avg transition cost     | +0.0493|
| Avg recovery time       | 8.6 ticks |

### Hierarchy as Rigidity Amplifier

The deep hierarchy reveals a stark rigidity gradient. By tick 50, every level
above L0 is already 100% rigid. The gradient is steep and persistent:

- **L0 (243 agents):** 57% rigid -- the population reservoir, constantly refreshed
  by new entrants, maintains meaningful diversity
- **L1 through Top (121 agents):** 100% rigid -- the entire upper hierarchy is
  a rigid monoculture

Each level acts as a selection filter. An agent must outperform peers to advance.
During stable periods, rigids with the correct strategy have a performance edge
(no noise penalty). Each promotion round filters out another layer of flexibles.
With 5 promotion boundaries instead of 3, the filtering is more thorough.

Interestingly, flexibles actually outperform rigids on average in this run (1.33
vs. 1.10). This is because with 5 environment switches, many rigids are stuck
playing the wrong strategy for extended periods, while the large flexible base
at L0 adapts. But the tournament keeps promoting rigids during each stable window
regardless.

The large agent pool (364 vs. 40) means better population-level buffering: the
L0 pool of 243 agents maintains 43% flexibility even at tick 500, acting as a
deep reserve that can feed correct-strategy agents upward after switches.

---

## Experiment 6: Shallow Hierarchy (2 levels)

**Command:** `python3 cli.py --ticks 500 --levels 2 --seed 42`

**Parameters:** 2 levels, branching factor 3, 4 total agents

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 3      | 66.7%  | 33.3%     |
| Top   | 1      | 100.0% | 0.0%      |

### Performance

| Metric                 | Value   |
|------------------------|---------|
| Overall avg performance | 1.0961 |
| Rigid avg performance   | 1.0248 |
| Flexible avg performance| 0.7945 |
| Environment switches    | 7      |
| Avg transition cost     | +0.1381|
| Avg recovery time       | 6.9 ticks |

### Flat Organizations: Less Amplification, More Noise

With only 4 agents and 1 promotion boundary, the dynamics are dramatically
different:

**Reduced rigidity amplification.** There is only one tournament boundary to cross
(L0 to Top), so the filtering effect is weaker. The top is still rigid, but
L0 maintains 33% flexibility.

**Higher stochastic noise.** With only 4 agents, individual events dominate. The
simulation saw 7 environment switches (more than baseline's 4, due to the same
seed producing different random draws for a differently-sized hierarchy). Each
switch has outsized impact because replacing even one agent changes the org by 25%.

**Faster but noisier recovery.** Average transition cost (+0.14) is lower than
baseline (+0.34), and recovery is faster (6.9 vs. 15 ticks). With fewer levels,
correct-strategy agents only need to win one tournament to reach the top. But the
small population means recovery depends heavily on whether a new entrant happens
to have the right strategy.

**The tradeoff:** Flat organizations are less prone to the rigidity trap (fewer
amplification levels), but they lack the population diversity that buffers large
hierarchies against disruption. They are more volatile but less fragile.

---

## Experiment 7: High Experience Weight (experience_weight=0.5)

**Command:** `python3 cli.py --ticks 500 --experience-weight 0.5 --seed 42`

### Final Composition

| Level | Agents | Rigid% | Flexible% |
|-------|--------|--------|-----------|
| L0    | 27     | 44.4%  | 55.6%     |
| L1    | 9      | 44.4%  | 55.6%     |
| L2    | 3      | 100.0% | 0.0%      |
| Top   | 1      | 100.0% | 0.0%      |

### Performance

| Metric                  | Value   |
|-------------------------|---------|
| Overall avg performance  | 3.1164 |
| Rigid avg performance    | 3.1223 |
| Flexible avg performance | 3.1130 |
| Environment switches     | 3      |
| Avg transition cost      | +0.0110|
| Avg recovery time        | 0.0 ticks |

### Seniority Overwhelms Strategy

This experiment produces the most surprising result: **experience weight at 0.5
nearly eliminates the rigid-flexible distinction.**

At the default experience weight (0.1), rigids outperform flexibles by 0.085
(1.19 vs. 1.11). At weight 0.5, the gap shrinks to 0.009 (3.12 vs. 3.11) --
essentially zero. Here is why:

Performance = strategy_match (0 or 1) + 0.5 * log(1 + experience)

After 100 ticks, a rigid agent has experience ~100 and an experience bonus of
~2.31. A flexible agent has experience ~50, giving a bonus of ~1.96. The strategy
match component (0 or 1) becomes a relatively small fraction of total performance.
An experienced agent who picks the wrong strategy still scores ~2.3, while a new
agent who picks correctly scores only ~1.0. **Seniority dominates strategy.**

The consequences are dramatic:

1. **The hierarchy preserves flexibility.** L0 and L1 are both 56% flexible --
   the tournament does not systematically purge flexibles because their experience
   compensates for the noise penalty.

2. **Transitions are painless.** Average transition cost is +0.011 (vs. +0.337
   at default weight) and recovery time is 0 ticks. When the environment switches,
   the strategy-match component shifts, but it is swamped by the experience
   component. The organization barely notices.

3. **A different form of inertia.** The organization is resilient but for the
   wrong reason: not because it adapts, but because it is insensitive to the
   environment. It selects for tenure over capability. This mirrors real-world
   seniority-heavy organizations (civil services, tenured academia) that are
   stable but potentially disconnected from environmental demands.

---

## Cross-Experiment Comparison

### Composition Summary

| Experiment            | Overall Rigid% | Top Rigid% | L0 Rigid% |
|-----------------------|----------------|------------|-----------|
| 1. Baseline           | 75.0%          | 100%       | 70.4%     |
| 2. High Stability     | 97.5%          | 100%       | 96.3%     |
| 3. High Volatility    | 60.0%          | 0%         | 70.4%     |
| 4. Random Mode        | 90.0%          | 100%       | 85.2%     |
| 5. Deep Hierarchy     | 71.4%          | 100%       | 57.2%     |
| 6. Shallow Hierarchy  | 75.0%          | 100%       | 66.7%     |
| 7. High Experience    | 52.5%          | 100%       | 44.4%     |

### Performance and Resilience Summary

| Experiment            | Avg Perf | Switches | Transition Cost | Recovery |
|-----------------------|----------|----------|-----------------|----------|
| 1. Baseline           | 1.1943   | 4        | +0.3368         | 15.0     |
| 2. High Stability     | 1.4389   | 0        | n/a             | n/a      |
| 3. High Volatility    | 1.0441   | 24       | +0.0413         | 6.0      |
| 4. Random Mode        | 1.2559   | 3        | +0.2243         | 9.0      |
| 5. Deep Hierarchy     | 1.1916   | 5        | +0.0493         | 8.6      |
| 6. Shallow Hierarchy  | 1.0961   | 7        | +0.1381         | 6.9      |
| 7. High Experience    | 3.1164   | 3        | +0.0110         | 0.0      |

---

## Key Emergent Behaviors

### 1. The Tournament Is a Rigidity Ratchet

In every experiment with moderate-to-high stability, the promotion tournament
drives the organization toward rigid dominance at upper levels. This is not a
bug but an emergent property of meritocratic selection: during stable periods,
rigids with the correct strategy genuinely outperform flexibles. The tournament
does what it is designed to do -- promote the best performers -- and in doing so
systematically eliminates organizational adaptability.

The ratchet operates at different speeds depending on conditions:
- High stability: L1 reaches 100% rigid by tick 38
- Baseline: L2 reaches 100% rigid by tick 50
- High volatility: the ratchet reverses -- flexibles dominate the top

### 2. Environmental Volatility Is the Master Variable

The single most important parameter is how often the environment changes. This
one variable determines whether rigids or flexibles dominate, whether transition
costs are catastrophic or negligible, and whether the organization is fragile or
resilient. At stability=500, 100% rigid is optimal. At stability=20, 0% rigid is
optimal. Organizations cannot know which regime they are in until it changes.

### 3. The Rigidity Gradient Steepens with Hierarchy Depth

In the 6-level hierarchy, every level above L0 was 100% rigid by tick 50, while
L0 maintained 43% flexibility. Each hierarchical level acts as an additional
selection filter. The implication for real organizations: the deeper the management
chain, the more homogeneous the leadership becomes, and the more disconnected it
grows from the adaptive capacity that persists only at the front lines.

### 4. Experience Creates an Alternative to Adaptation

High experience weight (0.5) produced the most resilient organization, but through
a counterintuitive mechanism: it made the organization insensitive to environmental
changes rather than responsive to them. When seniority dominates performance
evaluation, strategy-environment match becomes irrelevant, and the rigid-flexible
distinction dissolves. This is a third path beyond "rigid efficiency" and "flexible
adaptation": **inertial stability through accumulated competence.** It resembles
bureaucratic organizations that persist through institutional knowledge rather than
environmental responsiveness.

### 5. The Flexible Reserve Acts as Organizational Insurance

Across experiments, the L0 population consistently maintained more flexibility than
upper levels. In the baseline, L0 was 70% rigid when L2 and Top were 100% rigid.
These lower-level flexibles are the "insurance policy" -- they look like
underperformers during stability (and would be cut in any efficiency drive), but
they provide the adaptive raw material the organization needs after a regime change.
The 6-level hierarchy, with its 243-agent L0, maintained the deepest reserve (43%
flexible), which contributed to its faster recovery despite more levels of rigid
lock-in above.

### 6. Punctuated Equilibrium Is More Dangerous Than Random Variation

The random-mode experiment (Exp. 4) produced fewer switches (3 vs. 4) at the same
average rate, yet a qualitatively similar organizational structure to the stable
case. The pattern of change matters: punctuated equilibrium allows organizations to
over-specialize during long stable periods, then delivers maximum shock. Random
variation keeps the organization in a moderate state of readiness. This mirrors
Taleb's distinction between fragility (systems that break under rare, large shocks)
and antifragility (systems that benefit from frequent, small perturbations).

### 7. The Performance-Resilience Tradeoff Is Real and Steep

The data reveals a clear tradeoff frontier:

- **Peak performance (1.44):** High stability, near-total rigidity, zero resilience
- **Maximum resilience (0.01 transition cost):** High experience weight, performance
  dominated by tenure, insensitive to strategy
- **Balanced adaptation (1.04 avg, 6-tick recovery):** High volatility, flexible
  dominance, lower peak but no crashes

There is no free lunch. Every path to resilience involves sacrificing some measure
of peak-period performance. The question for any organization is how much
steady-state efficiency it is willing to trade for insurance against disruption --
a question that can only be answered honestly before the disruption arrives, not
after.
