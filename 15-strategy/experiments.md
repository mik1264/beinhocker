# Strategy as Evolution: Portfolio-Based Competition

## Theoretical Background

### Strategy Is Not Planning (Beinhocker, 2006)

Traditional strategic planning assumes that the future is predictable enough to find
the "one right answer." Beinhocker argues this is fundamentally wrong. In a complex
adaptive system, the future is inherently unpredictable, and the best strategy is not
a single plan but a **portfolio of experiments**.

Key insights from Chapter 15:
- **Strategy as portfolio**: firms should maintain multiple strategic experiments,
  allocating resources dynamically based on feedback
- **Robust vs. optimal**: a robust strategy that performs adequately across many
  scenarios beats an "optimal" strategy that excels in one scenario but fails in others
- **Explore and exploit**: the fundamental tension is between exploiting known
  opportunities (efficiency) and exploring new ones (adaptability)

### Three Strategic Archetypes

| Archetype | Resource Allocation | Mutation Rate | Strength | Weakness |
|-----------|-------------------|---------------|----------|----------|
| Exploiter | Concentrated on best | Low | Efficient in stable environments | Fragile to change |
| Explorer | Spread evenly | High | Robust to disruption | Inefficient |
| Adaptive | Performance-weighted | Moderate | Balanced | Moderate at everything |

### March's Exploration-Exploitation Tradeoff (1991)

James March showed that organizations face a fundamental tradeoff:
- **Exploitation**: refining existing capabilities for short-term efficiency
- **Exploration**: searching for new opportunities for long-term survival
- Organizations that only exploit become "competency traps"
- Organizations that only explore never develop competence

### Niche Fitness Landscapes

Each market niche has an "ideal" capability profile that shifts over time as
consumer preferences, technology, and regulation change. A firm's fitness in a
niche depends on how closely its capabilities match the current ideal.

---

## Experiment 1: Baseline -- Mixed Market

**Question**: In a mixed market with all three types, which archetype dominates?

**Setup**:
```
python3 cli.py --ticks 300 --seed 42
```

**Predictions**:
- Adaptive firms should gain the largest market share over time
- Exploiters start strong but lose ground as niches shift
- Explorers maintain presence but with lower average fitness

---

## Experiment 2: Stable Market

**Question**: When niches never shift, do exploiters dominate?

**Setup**:
```
python3 cli.py --ticks 300 --shift-rate 0.0 --seed 42
```

**Predictions**:
- Exploiters should dominate: concentrated resources on the best experiment
- Explorers waste resources on unnecessary diversity
- Market concentration (HHI) should increase as exploiters lock in

---

## Experiment 3: Volatile Market

**Question**: When niches shift frequently, do explorers survive better?

**Setup**:
```
python3 cli.py --ticks 300 --shift-rate 0.2 --seed 42
```

**Predictions**:
- Explorers and adaptive firms should outperform exploiters
- Higher portfolio diversity should correlate with survival
- More creative destruction (higher exit/entry rate)

---

## Experiment 4: All Exploiters

**Question**: What happens in a market of pure exploiters?

**Setup**:
```
python3 cli.py --ticks 300 --exploiter-frac 1.0 --explorer-frac 0.0 --seed 42
```

**Predictions**:
- High efficiency in stable periods
- Catastrophic failures when niches shift
- Low portfolio diversity, high concentration

---

## Experiment 5: All Explorers

**Question**: What happens in a market of pure explorers?

**Setup**:
```
python3 cli.py --ticks 300 --exploiter-frac 0.0 --explorer-frac 1.0 --seed 42
```

**Predictions**:
- Lower overall fitness than exploiter market
- But more robust to niche shifts
- Higher portfolio diversity, lower concentration

---

## Experiment 6: Larger Economy

**Question**: Do the patterns scale to more firms and niches?

**Setup**:
```
python3 cli.py --ticks 300 --firms 100 --niches 10 --seed 42
```

**Predictions**:
- Similar archetype dynamics but with richer niche coverage
- More competitive market (lower HHI)
- More resilient to shocks due to greater diversity

---

## Key Metrics to Track

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| Survival by type | Count of each archetype over time | Which strategy wins |
| Market share by type | Revenue allocation to each type | Competitive dominance |
| Mean/best fitness | Overall and frontier performance | Market productivity |
| HHI | Market concentration | Competition vs. monopoly |
| Portfolio diversity | Niche coverage per firm | Strategic breadth |
| Niche coverage | Fraction of niches served | Market completeness |
| Adaptation speed | Resource reallocation rate | Responsiveness to change |

---

## References

1. Beinhocker, E. (2006). *The Origin of Wealth*, Ch. 15: "Strategy."
2. March, J. (1991). "Exploration and Exploitation in Organizational Learning." *Organization Science*, 2(1), 71-87.
3. Levinthal, D. & March, J. (1993). "The Myopia of Learning." *Strategic Management Journal*, 14(S2), 95-112.
4. Gavetti, G. & Levinthal, D. (2000). "Looking Forward and Looking Backward." *Administrative Science Quarterly*, 45(1), 113-137.
5. Mintzberg, H. (1994). *The Rise and Fall of Strategic Planning*. Free Press.
6. Sull, D. (2009). *The Upside of Turbulence*. Harper Business.
