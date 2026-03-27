# Beer Distribution Game: Simulation Experiments

## Background

The **Beer Distribution Game** was invented at MIT's Sloan School of Management in the 1960s by Jay Forrester, a pioneer of system dynamics. It models a simple four-echelon supply chain — **Retailer → Wholesaler → Distributor → Brewery** — where each agent sees only local information (their own inventory, their own incoming orders) and must decide how much to order from the echelon above.

The game's enduring lesson: even when consumer demand changes only slightly (a one-time step from 4 to 8 cases per week), the supply chain erupts into wild oscillations, massive backlogs, and eventual gluts of inventory. Players routinely blame each other — "the wholesaler panicked!" — but the oscillations are **structural**, arising from the interaction of feedback delays, local information, and simple decision heuristics. No individual is irrational; the system produces irrational outcomes.

John Sterman's landmark 1989 paper formalized the ordering heuristic that real players use: **anchor-and-adjust**. Agents anchor on expected demand, then adjust for the gap between desired and actual inventory, and (insufficiently) adjust for beer already on order in the supply pipeline. This model, with its empirically estimated parameters (alpha ≈ 0.5, beta ≈ 0.2), reproduces the oscillations observed in thousands of classroom experiments.

### Why These Experiments Matter

Eric Beinhocker argues in *The Origin of Wealth* that business cycles may be **endogenous** — generated internally by the structure of economic systems — rather than caused by external shocks. The Beer Game is a microcosm of this argument: a tiny demand perturbation, amplified by structural feedback delays and boundedly rational heuristics, produces oscillations that look like exogenous cycles but are entirely self-generated. These experiments explore the mechanisms behind that amplification.

---

## Experiment Results

### Experiment 1: Default Behavioral Mode (Sterman Heuristic)

```
python3 cli.py
```

The baseline: standard step demand (4 → 8 at week 5), 2-tick shipping delay, anchor-and-adjust with alpha=0.5, beta=0.2.

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $229.00 | 2.46 |
| Wholesaler | $373.50 | 7.91 |
| Distributor | $971.50 | 3.74 |
| Brewery | $1,083.00 | 1.73 |
| **Total** | **$2,657.00** | — |

The bullwhip effect is dramatic: the Wholesaler amplifies order variance by nearly **8x** relative to its incoming orders. Costs cascade upstream — the Brewery pays 4.7x more than the Retailer, despite facing the same underlying demand signal. Final inventory at the Brewery: 95 cases (nearly 12 weeks of excess stock).

---

### Experiment 2: Rational (Optimal) Ordering Policy

```
python3 cli.py --rational
```

The rational agent uses inventory-position-based ordering: order what you received, plus a gentle correction spread over the pipeline delay. No panic, no overreaction.

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $273.00 | 1.23 |
| Wholesaler | $296.00 | 2.02 |
| Distributor | $325.50 | 2.23 |
| Brewery | $466.50 | 2.34 |
| **Total** | **$1,361.00** | — |

Costs are distributed far more evenly across echelons. The bullwhip ratios are modest (1.2–2.3x) and increase gently upstream — a stark contrast to the behavioral mode's wild amplification. Note that the Retailer actually costs *more* here ($273 vs $229) because the rational agent doesn't over-correct, accepting short-term inventory costs for long-term system stability.

---

### Experiment 3: Side-by-Side Comparison

```
python3 cli.py --compare
```

| Metric | Behavioral | Rational | Ratio |
|--------|----------:|----------:|------:|
| Total cost | $2,657 | $1,361 | **2.0x** |
| Brewery bullwhip | 1.73 | 2.34 | 0.7x |
| Brewery final inventory | 95 | 28 | 3.4x |

**The "human tax"**: behavioral ordering costs the system **2.0x** more than rational ordering. This is the price of bounded rationality — agents using sensible-seeming heuristics generate nearly double the total supply chain cost. In real supply chains with hundreds of echelons and products, this multiplier compounds.

Interestingly, the rational mode shows a *higher* bullwhip ratio at the Brewery (2.34 vs 1.73). This is because in the behavioral mode, the Brewery's own massive overreaction has already saturated the variance — the denominator (incoming order variance) is itself inflated by upstream panic, masking the true amplification.

---

### Experiment 4: High Shipping Delay (4 ticks)

```
python3 cli.py --shipping-delay 4
```

Doubling the shipping delay from 2 to 4 ticks transforms a manageable oscillation into a catastrophe.

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $492.50 | 27.28 |
| Wholesaler | $3,286.00 | 12.10 |
| Distributor | $7,528.00 | 7.13 |
| Brewery | $8,636.00 | 2.73 |
| **Total** | **$19,942.50** | — |

Total cost explodes to **$19,943** — a **7.5x** increase over the default. The Retailer's bullwhip ratio leaps to 27x. Final inventory at the Brewery: **935 cases** (nearly 2 years of demand sitting on the warehouse floor). The system massively overshoots because agents cannot observe the beer already in transit, and longer pipelines mean corrections arrive far too late.

---

### Experiment 5: Very High Shipping Delay (5 ticks)

```
python3 cli.py --shipping-delay 5
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $644.50 | 40.92 |
| Wholesaler | $4,679.00 | 20.55 |
| Distributor | $13,131.00 | 8.91 |
| Brewery | $17,607.00 | 3.20 |
| **Total** | **$36,061.50** | — |

At 5-tick delay, total cost reaches **$36,062** — a **13.6x** increase over baseline. The Retailer's bullwhip ratio is an extraordinary **41x**. Brewery final inventory: **2,137 cases**. The relationship between delay and cost is clearly super-linear — each additional tick of delay causes proportionally more damage as the system's ability to self-correct degrades.

---

### Experiment 6: Low Shipping Delay (1 tick)

```
python3 cli.py --shipping-delay 1
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $234.50 | 1.14 |
| Wholesaler | $241.00 | 1.55 |
| Distributor | $247.00 | 1.78 |
| Brewery | $300.00 | 1.36 |
| **Total** | **$1,022.50** | — |

With a 1-tick delay, the bullwhip nearly vanishes. Maximum amplification is only 1.78x (Distributor), and costs are distributed almost evenly. Total cost is **$1,023** — just 38% of the default. When feedback is fast, even imperfect heuristics work well. The system can observe the consequences of its orders quickly enough to self-correct before oscillations build.

---

### Experiment 7: Information Sharing (Upstream Sees Consumer Demand)

```
python3 cli.py --information-sharing
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $231.00 | 2.35 |
| Wholesaler | $284.00 | 5.06 |
| Distributor | $480.50 | 2.04 |
| Brewery | $401.00 | 1.04 |
| **Total** | **$1,396.50** | — |

Information sharing cuts total cost by **47%** (from $2,657 to $1,397). The Brewery's bullwhip ratio drops to nearly 1.0 — it can see the actual demand signal instead of reacting to amplified echoes from downstream. The Distributor's cost drops from $972 to $481. However, the Wholesaler still amplifies significantly (5.06x) because, even with shared demand information, the inventory adjustment heuristic still over-corrects based on local inventory gaps.

---

### Experiment 8: High Delay + Information Sharing (Delay=4)

```
python3 cli.py --shipping-delay 4 --information-sharing
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $561.00 | 30.24 |
| Wholesaler | $2,848.50 | 8.55 |
| Distributor | $5,476.00 | 4.40 |
| Brewery | $4,761.00 | 1.31 |
| **Total** | **$13,646.50** | — |

Information sharing reduces the high-delay cost from $19,943 to $13,647 — a **32% reduction**. The Brewery benefits enormously (bullwhip drops from 2.73 to 1.31), but the Retailer still suffers (bullwhip 30x). Information sharing helps, but it cannot fully compensate for structural delay. The physics of the pipeline — beer takes 4 weeks to arrive regardless of what you know — imposes a floor on the bullwhip effect.

---

### Experiment 9: Aggressive Alpha/Beta (alpha=0.8, beta=0.5)

```
python3 cli.py --alpha 0.8 --beta 0.5
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $258.00 | 2.83 |
| Wholesaler | $486.00 | 12.73 |
| Distributor | $1,629.00 | 4.92 |
| Brewery | $1,941.00 | 2.19 |
| **Total** | **$4,314.00** | — |

More aggressive correction (higher alpha and beta) makes things **worse**: total cost rises 62% to $4,314. The Wholesaler's bullwhip ratio nearly doubles to 12.73x. Aggressive correction feels prudent — "I'm short, so I'll order more!" — but in a delayed system, it's the equivalent of turning the steering wheel harder because you can't see around the corner. The correction arrives too late and overshoots.

---

### Experiment 10: Conservative Alpha/Beta (alpha=0.1, beta=0.05)

```
python3 cli.py --alpha 0.1 --beta 0.05
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $260.00 | 2.10 |
| Wholesaler | $416.00 | 2.57 |
| Distributor | $465.00 | 1.85 |
| Brewery | $318.00 | 1.41 |
| **Total** | **$1,459.00** | — |

Conservative correction (alpha=0.1, beta=0.05) dramatically improves performance: total cost drops 45% to $1,459, nearly matching the rational policy ($1,361). Bullwhip ratios stay below 2.6x everywhere. The lesson: **do less**. When you can't see the full system, restrained reaction outperforms aggressive correction. This is Sterman's core finding — people under-weight the supply line (beta is too low relative to what's optimal), but they also over-weight the inventory gap (alpha is too high).

---

### Experiment 11: Sine Demand (Behavioral vs Rational)

**Behavioral:**
```
python3 cli.py --demand-pattern sine --ticks 60
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $1,067.00 | 9.00 |
| Wholesaler | $5,918.50 | 6.64 |
| Distributor | $11,080.00 | 3.44 |
| Brewery | $8,364.00 | 1.77 |
| **Total** | **$26,429.50** | — |

**Rational:**
```
python3 cli.py --demand-pattern sine --ticks 60 --rational
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $774.00 | 5.71 |
| Wholesaler | $1,840.00 | 3.68 |
| Distributor | $3,137.00 | 2.18 |
| Brewery | $4,042.00 | 1.94 |
| **Total** | **$9,793.00** | — |

With continuously varying demand (sine wave), the behavioral policy costs **2.7x** more than rational — even worse than the step demand ratio (2.0x). Continuous change gives the anchor-and-adjust heuristic no time to converge; it's perpetually chasing a moving target. Rational ordering, while not perfect (bullwhip still 2–6x), avoids the catastrophic amplification.

---

### Experiment 12: Ramp Demand

```
python3 cli.py --demand-pattern ramp --ticks 50
```

| Agent | Cumulative Cost | Bullwhip Ratio |
|-------|---------------:|---------------:|
| Retailer | $224.00 | 1.06 |
| Wholesaler | $222.50 | 1.04 |
| Distributor | $218.00 | 1.07 |
| Brewery | $433.00 | 1.07 |
| **Total** | **$1,097.50** | — |

Ramp demand (slowly, linearly increasing) produces almost no bullwhip effect — ratios are essentially 1.0 across all agents. The gradual change gives the exponential smoothing time to track the signal. This confirms that the bullwhip is not about demand *changing* per se, but about demand changing *faster than the system can adapt*.

---

## Summary Comparison Table

| Experiment | Config | Total Cost | Max Bullwhip | Cost vs Baseline |
|------------|--------|----------:|-------------:|-----------------:|
| Baseline behavioral | default | $2,657 | 7.91 | 1.0x |
| Rational | --rational | $1,361 | 2.34 | 0.51x |
| Low delay (1) | --shipping-delay 1 | $1,023 | 1.78 | 0.38x |
| **High delay (4)** | --shipping-delay 4 | **$19,943** | **27.28** | **7.5x** |
| Very high delay (5) | --shipping-delay 5 | $36,062 | 40.92 | 13.6x |
| Info sharing | --information-sharing | $1,397 | 5.06 | 0.53x |
| High delay + info | delay 4 + info | $13,647 | 30.24 | 5.1x |
| Aggressive (α=0.8) | --alpha 0.8 --beta 0.5 | $4,314 | 12.73 | 1.6x |
| Conservative (α=0.1) | --alpha 0.1 --beta 0.05 | $1,459 | 2.57 | 0.55x |
| Sine behavioral | --demand-pattern sine | $26,430 | 9.00 | 9.9x |
| Sine rational | sine + --rational | $9,793 | 5.71 | 3.7x |
| Ramp | --demand-pattern ramp | $1,098 | 1.07 | 0.41x |

### Scaling of Cost with Shipping Delay

| Shipping Delay (ticks) | Total Cost | Cost Multiplier | Max Bullwhip |
|:-----------------------:|----------:|-----------------:|-------------:|
| 1 | $1,023 | 1.0x | 1.78 |
| 2 (default) | $2,657 | 2.6x | 7.91 |
| 4 | $19,943 | 19.5x | 27.28 |
| 5 | $36,062 | 35.3x | 40.92 |

The relationship is emphatically **super-linear** — closer to exponential. Doubling the delay from 2 to 4 increases cost by 7.5x. Adding one more tick (4 → 5) nearly doubles it again. This is because longer delays mean corrections arrive later, overshoot more, and trigger larger counter-corrections, creating a positive feedback loop of amplification.

---

## Key Findings

### 1. Simple Heuristics + Feedback Delays = Emergent Oscillations

The anchor-and-adjust heuristic is not unreasonable — it's what a sensible manager would do: estimate demand, check inventory, adjust. But in a system with multi-week delays between ordering and receiving, this sensible behavior generates oscillations that no individual agent intends or desires. The oscillations are an **emergent property** of the system structure, not a failure of individual rationality.

### 2. The "Human Tax" Is Real but Bounded

Behavioral ordering costs 2.0x more than rational ordering under step demand and 2.7x under sine demand. This is the cost of bounded rationality — the price organizations pay for using simple rules in complex systems. But it's not infinite; the heuristic does converge eventually, just with costly overshooting along the way.

### 3. Delay Is the Dominant Amplifier

Of all parameters tested, **shipping delay** has the most dramatic effect on system performance. Going from 1-tick to 5-tick delay increases costs by 35x. No amount of clever heuristic tuning can compensate for long pipelines. This has profound implications for supply chain design: reducing lead times (JIT manufacturing, local sourcing, faster logistics) may matter more than improving forecasting or information systems.

### 4. Information Sharing Helps — But Is Not a Silver Bullet

Sharing consumer demand with all echelons cuts costs by 47% under default conditions and 32% under high delay. It nearly eliminates the Brewery's bullwhip effect. But it cannot overcome the structural delay — beer still takes weeks to arrive. Information sharing is necessary but not sufficient; it must be paired with appropriate decision policies.

### 5. Less Is More: Conservative Correction Outperforms Aggressive Correction

Agents with conservative parameters (alpha=0.1, beta=0.05) nearly match optimal performance, while aggressive agents (alpha=0.8, beta=0.5) make things 62% worse. The intuition that "I need to correct harder" is precisely wrong in delayed systems. Sterman found that real players exhibit alpha ≈ 0.36 and beta ≈ 0.09 — somewhat conservative, but still too aggressive on inventory correction relative to supply-line awareness.

### 6. Demand Pattern Matters: Abrupt Changes Are Poison

Ramp demand (gradual increase) produces virtually no bullwhip. Step demand (abrupt doubling) produces massive oscillations. Sine demand (continuous variation) produces the worst outcomes because the system never reaches equilibrium. Real-world demand shocks — a viral product, a pandemic, a trade disruption — combine step-like abruptness with the system's inability to know whether the change is temporary or permanent.

---

## Connection to Beinhocker: Endogenous Business Cycles

These experiments provide a vivid microcosm of Beinhocker's argument in *The Origin of Wealth* that business cycles may be **endogenous** rather than driven by external shocks.

**The orthodox view** holds that economies are in or near equilibrium, and cycles are caused by exogenous perturbations — oil shocks, policy changes, technological disruptions. If this were true, the Beer Game should be boring: demand steps from 4 to 8, the supply chain adjusts, and everyone settles into the new equilibrium within a few weeks.

**What actually happens** is that a tiny, one-time demand perturbation generates 35 weeks of oscillation, massive cost overruns, and inventory swings from severe shortages to enormous gluts. The oscillations are not caused by ongoing shocks — there is exactly *one* demand change in the entire simulation. Everything after week 5 is the system reacting to itself.

This is Beinhocker's core insight: **complex adaptive systems with feedback delays and boundedly rational agents generate their own dynamics**. You don't need external shocks to produce boom-bust cycles; you need only:

1. **Delayed feedback** — agents cannot instantly observe the consequences of their actions
2. **Local information** — each agent sees only their own inventory, not the full system state
3. **Reasonable but imperfect heuristics** — agents use rules of thumb that work locally but interact destructively at the system level

The Beer Game demonstrates all three. And crucially, the oscillations look *exactly like* what you'd expect from an exogenous shock — any observer seeing the Brewery's order pattern would assume something dramatic happened in the market. But nothing did. The drama is entirely internal.

This has profound implications for macroeconomics: if supply chains, credit markets, and labor markets all exhibit Beer Game-like dynamics (and there is considerable evidence they do), then the search for *causes* of business cycles may be asking the wrong question. The cycles may not have causes in the traditional sense — they may be **structural properties of interconnected systems with delays**, as inevitable as the oscillations of a pendulum.

The experiments above quantify this: the "human tax" (2x cost multiplier) is the price of bounded rationality, but the *structure tax* (35x cost multiplier from delay alone) dwarfs it. Even perfectly rational agents cannot eliminate the bullwhip when delays are long enough. The oscillations are not a bug in human cognition — they are a feature of system architecture.

As Beinhocker puts it: the economy is not a machine that can be fine-tuned to equilibrium. It is a complex adaptive system that generates its own weather.
