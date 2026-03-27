# Sterman's Behavioral Decision Rule: Deep Dive

## The Stock Management Problem
Subjects manage a simulated inventory distribution system containing:
- Multiple actors with independent decisions
- Feedback loops between echelons
- Nonlinearities (orders can't be negative)
- Time delays in information and material flow

## Decision Rule Structure

### Managers choose orders to:
1. **Replace expected losses** from the stock (the anchor)
2. **Reduce the discrepancy** between desired and actual stock (inventory adjustment)
3. **Reduce the discrepancy** between desired and actual supply line (supply line adjustment)

### Formal Specification
```
O_t = max(0, D^e_t + α·(I* - I_t) + β·(SL* - SL_t))
```

### Component Breakdown

**Anchor (D^e_t)**: Expected demand via exponential smoothing
- Represents "what I expect to sell next period"
- Adaptive: responds to recent demand changes

**Inventory Adjustment**: α·(I* - I_t)
- Corrects for inventory deviations from target
- α controls speed of correction
- Higher α → more aggressive restocking

**Supply Line Adjustment**: β·(SL* - SL_t)
- Accounts for orders already placed but not yet received
- β controls how much weight is placed on pipeline
- **Critical finding**: β is systematically underweighted

## The Supply Line Underweighting Problem

### Optimal vs. Actual
- **Optimal β** = 1.0 (full accounting of pipeline)
- **Typical β** = 0.1–0.3 (severe underweighting)

### Consequences
- Managers "forget" about orders already in the pipeline
- They order more than needed, creating phantom demand
- When the pipeline eventually delivers, massive oversupply results
- This creates the characteristic boom-bust oscillation

### Why It Happens
1. Pipeline orders are **out of sight, out of mind**
2. Cognitive complexity of tracking multiple pending orders
3. Uncertainty about delivery timing
4. Anchoring too strongly on current inventory state

## Empirical Validation
- R² ≈ 0.71 (explains 71% of ordering variance)
- RMSE ≈ 2.86
- 4 parameters per player: θ (smoothing), α (stock adjustment), β (supply line), I* (desired inventory)
- Model consistently outperforms alternatives in explaining subject behavior

## Sources
- [Sterman 1989 - Modeling Managerial Behavior](https://pubsonline.informs.org/doi/10.1287/mnsc.35.3.321)
- [Behavioral Causes of the Bullwhip Effect](http://web.mit.edu/~paulopg/www/OG_Overreaction.pdf)
