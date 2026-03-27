# Heterogeneous Agent Models in Financial Markets

## Paradigm Shift
From representative agent with rational expectations to boundedly rational agents with heterogeneous expectations. This has been driven by:
- Empirical evidence contradicting efficient market hypothesis
- Unconvincing justification of unbounded rationality
- Behavioral finance findings on investor psychology

## Agent Types in Typical HAMs
1. **Fundamentalists**: Trade based on deviation from fundamental value
2. **Chartists/Technical traders**: Trade based on price trends and patterns
3. **Noise traders**: Random trading providing liquidity

## Market Maker
- Adjusts price according to aggregate excess demand
- p_{t+1} = p_t + β * excess_demand_t
- Or Walrasian auctioneer clearing at equilibrium

## Stylized Facts Explained by HAMs
- Excess volatility (beyond what fundamentals justify)
- High trading volume
- Temporary bubbles and trend following
- Sudden crashes and mean reversion
- Clustered volatility and fat tails

## SFI ASM as a HAM
- Agents are heterogeneous through different rule sets
- No fixed types - agents evolve their strategies
- Can be fundamentalist-like (low a, focus on P/D ratio bits) or chartist-like (focus on MA bits)
- Strategy composition changes over time via GA
- This endogenous heterogeneity is more realistic than fixed-type models

## Key Parameters Controlling Behavior
- Learning rate (GA invocation frequency)
- Mutation rate (diversity of new strategies)
- Risk aversion (sensitivity to forecast uncertainty)
- Market impact (how orders affect price)
