# Power Laws and Fat Tails in Stock Market Simulations

## Empirical Facts (Stylized Facts)
- Stock returns are NOT normally distributed
- Tails follow power law: P(|r| > x) ~ x^(-alpha), alpha ≈ 3 (cubic law)
- This holds across markets, time periods, and asset classes

## Mechanisms in Agent-Based Models
1. **Herding**: Agents influenced by neighbors create collective behavior
2. **Strategy switching**: Agents switching between rules creates regime changes
3. **Institutional demand**: Large order sizes follow power law distribution
4. **Information cascades**: Price changes trigger further trading

## How SFI ASM Produces Fat Tails
- Heterogeneous agents with different forecasting rules
- Evolutionary pressure creates diverse strategy ecology
- Occasional synchronization of strategies amplifies moves
- Mean-reversion forces eventually correct, creating sharp reversals

## Testing for Power Laws
- Log-log plot of absolute returns vs frequency
- Hill estimator for tail index
- Kolmogorov-Smirnov test against power law fit
- Kurtosis > 3 indicates fat tails (excess kurtosis)

## Key Results from SFI ASM
- LeBaron et al. (1999): Returns show excess kurtosis
- Complex regime produces realistic fat-tailed distributions
- Rational regime produces near-Gaussian returns
