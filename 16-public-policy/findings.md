# Public Policy: Findings

Simulation of Beinhocker Ch.18 -- Policy in a Complex World. 50 firms evolve on an NK fitness landscape (N=12, K=3) under different policy regimes. Policy levers affect entry barriers, compliance costs, mutation rates, market share caps, and safety net strength. Fitness is evaluated on a shared rugged landscape; firms keep only beneficial mutations.

## Summary Table

| Experiment | Regime | Mean GDP | Final GDP | Long-Run Growth | Mean Innov Rate | Total Innov | Mean Gini | Mean Unemp | Mean Fitness | Final Fitness | Alive at End |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Baseline | laissez-faire | 6.14 | 5.65 | -0.364 | 0.083 | 1242 | 0.250 | 39.4% | 0.655 | 0.631 | 30 |
| 2. Explicit LF | laissez-faire | 6.14 | 5.65 | -0.364 | 0.083 | 1242 | 0.250 | 39.4% | 0.655 | 0.631 | 30 |
| 3. Social Democrat | social-democrat | 7.59 | 6.73 | -0.291 | 0.102 | 2021 | 0.228 | 19.2% | 0.666 | 0.688 | 39 |
| 4. Innovation State | innovation-state | 8.13 | 6.91 | -0.244 | 0.101 | 1869 | 0.245 | 23.5% | 0.687 | 0.708 | 38 |
| 5. Protectionist | protectionist | 4.70 | 3.84 | -0.492 | 0.107 | 1749 | 0.192 | 33.1% | 0.627 | 0.621 | 29 |
| 6. Adaptive | adaptive | 9.83 | 8.59 | -0.022 | 0.094 | 1939 | 0.266 | 15.3% | 0.690 | 0.715 | 38 |

## Key Findings

### 1. The adaptive regime dominates on nearly every metric

The adaptive regime produced the highest mean GDP (9.83, 60% above laissez-faire), the best long-run growth (-0.022, nearly flat vs laissez-faire's -0.364 decline), the lowest unemployment (15.3%), and the highest final fitness (0.715). It achieved this by dynamically adjusting policy: over 500 ticks it reduced regulation from 0.30 to 0.05, lowered taxes from 0.20 to 0.10, raised innovation subsidies from 0.20 to 0.60, relaxed competition limits from 0.40 to 1.00, and strengthened the safety net from 0.50 to 0.90.

This directly validates Beinhocker's core prescription: complex economies require adaptive governance, not fixed optimization. The adaptive regime essentially discovered a hybrid configuration -- low regulation with high innovation subsidies and a strong safety net -- that no single preset regime offered.

### 2. Laissez-faire generates high inequality and unemployment, not high growth

Counter to the simplest "free market" narrative, laissez-faire produced the second-lowest mean GDP (6.14) and the highest unemployment (39.4%). With a weak safety net (0.10) and no subsidies, failed firms rarely re-entered the economy. The low respawn rate (2-3%) meant that once firms died, their "workers" stayed unemployed. This created a shrinking economy: 30 firms alive at end vs 50 at start. The weak safety net also meant less knowledge spillover from failed to new firms, keeping total innovations low at 1242.

Laissez-faire did produce the highest HHI (0.0455), indicating the most concentrated market structure -- without competition policy, a few fit firms captured outsized market share.

### 3. Social democracy trades growth for stability and equality

The social-democrat regime achieved the lowest Gini (0.228) and second-lowest unemployment (19.2%) while generating more total innovations (2021) than laissez-faire (1242). The combination of innovation subsidies (0.30), strong safety net (0.80), and competition limits (0.25) created a dynamic economy with high turnover (0.0358) and rapid firm re-entry. However, the high tax rate (0.45) and regulation (0.40) depressed GDP -- mean GDP of 7.59 was 23% below the adaptive regime.

The early-game crash (unemployment hit 88% around tick 40-50) shows that even "nice" regimes face severe initial turbulence as unfit firms are culled. But the strong safety net enabled rapid recovery.

### 4. Protectionism is the worst regime by far

The protectionist regime produced the lowest mean GDP (4.70), the worst long-run growth (-0.492), the lowest mean fitness (0.627), and the lowest final fitness (0.621). High regulation (0.80) created entry barriers 2.6x higher than normal, making it expensive for new firms to enter. This did produce the lowest Gini (0.192) -- but only because the economy was uniformly poor.

This strongly confirms Beinhocker's argument: protecting incumbents stifles the evolutionary search process. New entrants bring fresh genetic material (strategy variation) that the economy needs to improve fitness. When entry barriers are high, the population gets stuck on local optima.

### 5. Innovation subsidies boost fitness but need complements

The innovation-state regime achieved the second-highest mean fitness (0.687) and the second-highest mean GDP (8.13). The high innovation subsidy (0.70) boosted the effective mutation rate to 0.12 (vs 0.05 base), increasing the speed of the evolutionary search. But the regime nearly collapsed early (all firms died around tick 75-80) before the safety net respawned them. This fragility suggests that innovation subsidies alone are insufficient -- they need a safety net to handle the inevitable casualties of accelerated creative destruction.

The innovation-state regime produced fewer total innovations (1869) than social democracy (2021) despite a much higher mutation rate. This is because the high mutation rate also disrupted well-adapted genomes more frequently -- the classic exploration-exploitation tradeoff.

### 6. Entry barriers matter more than tax rates

Comparing protectionist (reg=0.80, tax=0.35) to social-democrat (reg=0.40, tax=0.45), social democracy had a higher tax rate but achieved 62% higher GDP and 42% lower unemployment. The key difference was entry barriers: protectionist regulation created 2.6x entry costs vs social democracy's 1.8x. This suggests that in an evolutionary economy, the flow of new entrants (variation supply) matters more than the tax burden on incumbents.

### 7. Safety nets are pro-growth, not just pro-equity

Comparing laissez-faire (safety net 0.10) to the adaptive regime's final state (safety net 0.90), the data shows that stronger safety nets correlate with higher GDP, not lower. The mechanism: safety nets increase the respawn probability for failed firms (from 2.8% to 9.2% per tick), maintaining the population size and the rate of evolutionary search. A dead firm slot that stays empty is a wasted position in the fitness landscape search.

This reframes the traditional growth-vs-equity debate: safety nets are a mechanism for maintaining the evolutionary search population, not just a redistributive cost.

### 8. The adaptive regime converges toward a specific policy mix

The adaptive regime's final policy state is revealing:
- Regulation: 0.05 (minimum) -- barriers to entry are anti-growth
- Tax rate: 0.10 (low) -- light taxation
- Innovation subsidy: 0.60 (high) -- heavy R&D support
- Competition limit: 1.00 (no limit) -- with enough entrants, concentration self-corrects
- Safety net: 0.90 (near maximum) -- maintain the search population

This converged configuration resembles an "innovation-state-plus" -- low barriers, high subsidies, strong safety net. It is closest to the innovation-state preset but with a much stronger safety net and lower taxes. The adaptive process discovered that competition policy is unnecessary when entry barriers are low and the safety net keeps firms flowing in.

## Connection to Beinhocker's Framework

The simulation confirms several core arguments from Chapter 18:

1. **Policy shapes fitness landscapes, not outcomes**: No regime could "pick" the optimal firm strategy. All regimes produced firms with similar fitness levels (0.62-0.72). The difference was in how many firms survived to search the landscape and how fast they searched.

2. **Evolutionary dynamics require variation supply**: The strongest regimes (adaptive, social-democrat) maintained high firm populations through safety nets and respawning. The weakest (laissez-faire, protectionist) lost firms and never recovered them, shrinking the evolutionary search.

3. **Adaptive governance outperforms fixed rules**: The adaptive regime's 60% GDP advantage over laissez-faire and 109% advantage over protectionism demonstrates Beinhocker's point that complex systems need responsive, not ideological, governance.

4. **No free lunch -- every regime has tradeoffs**: The adaptive regime achieved the best GDP and lowest unemployment but had the highest Gini (0.266). Social democracy had the lowest Gini but lower GDP. There is no regime that dominates on every dimension simultaneously.

5. **Protecting incumbents is the cardinal sin**: Protectionism's consistent last-place performance confirms that the worst thing policy can do is restrict the evolutionary process -- blocking entry, shielding unfit firms, and reducing variation.
