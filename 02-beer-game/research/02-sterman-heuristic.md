# Sterman's Anchor-and-Adjust Heuristic

## Background
John D. Sterman (1989) proposed the **anchoring and adjustment heuristic** as a model of how participants make ordering decisions in the Beer Distribution Game. Published in *Management Science* 35(3), pp. 321-339, "Modeling Managerial Behavior: Misperceptions of Feedback in a Dynamic Decision Making Experiment."

## The Decision Rule

The ordering decision follows an **anchor-and-adjust** framework from Kahneman & Tversky:

### Order = Anchor + Adjustment_inventory + Adjustment_supply_line

Formally:
```
O_t = max(0, D^e_t + α·(I* - I_t) + β·(SL* - SL_t))
```

Where:
- **O_t**: Order placed at time t
- **D^e_t**: Expected demand (the anchor) — estimated via exponential smoothing
- **α**: Stock adjustment parameter (weight on inventory discrepancy)
- **β**: Supply line adjustment parameter (weight on supply line discrepancy)
- **I***: Desired inventory level
- **I_t**: Actual inventory (negative = backlog)
- **SL***: Desired supply line (orders in pipeline)
- **SL_t**: Actual supply line

### Expected Demand (Exponential Smoothing)
```
D^e_t = θ·D_{t-1} + (1-θ)·D^e_{t-1}
```
Where θ is the smoothing parameter (0 < θ ≤ 1).

## Key Findings

### Misperceptions of Feedback
Sterman identified several systematic biases:
1. **Underweighting the supply line** (β significantly less than optimal value of 1)
2. Subjects fail to account for orders already in the pipeline
3. This leads to **phantom ordering** — placing orders for beer already on its way

### Empirical Parameter Estimates (Sterman 1989)
- Average R² = 0.71 (model explains 71% of variance in subject ordering)
- Average RMSE = 2.86
- Four parameters per player: θ, α, β, I*
- β typically estimated around 0.1-0.3 (far below optimal value of 1.0)
- α typically around 0.2-0.5

### Performance Implications
- Average team costs: ~$2,000 (sometimes exceeding $10,000)
- Optimal performance: ~$200
- Performance gap of roughly **10x** attributed to behavioral biases

## Bounded Rationality
The model follows Herbert Simon's tradition of bounded rationality:
- Decision-makers use locally available information
- No assumption of global knowledge of system structure
- Cognitive limitations prevent optimal decision-making
- The heuristic is "good enough" but systematically suboptimal

## Sources
- [Sterman 1989 - Modeling Managerial Behavior](https://pubsonline.informs.org/doi/10.1287/mnsc.35.3.321)
- [EOLSS - Supply Chain Dynamics](https://www.eolss.net/sample-chapters/c15/E6-63-01-02.pdf)
- [JASSS - A Mathematical Model of the Beer Game](https://www.jasss.org/17/4/2.html)
