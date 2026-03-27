# SFI Artificial Stock Market - Model Architecture

## Origins
The SFI market was born at the Santa Fe Institute in the late 1980s-early 1990s, originating from Brian Arthur and John Holland's desire to build a financial market with an ecology of trading strategies. The key paper is "Asset Pricing Under Endogenous Expectations in an Artificial Stock Market" by Arthur, Holland, LeBaron, Palmer, and Tayler.

## Core Architecture
- Central computational market with N artificially intelligent agents (typically N=25)
- Agents choose between investing in a risky stock and a risk-free bond (interest rate r=0.10)
- Stock pays stochastic dividend following AR(1) process
- Price fluctuates according to aggregate agent demand

## Agent Structure
- CARA utility function: U(W) = -exp(-λW), where λ=0.50
- Each agent maintains K=100 binary condition-action forecasting rules
- Agents select most accurate active rule for forecasting
- Demand function: x = (E[p+d] - p(1+r)) / (λ * var)

## Two Regimes
1. **Rational Expectations (slow learning)**: GA invoked rarely (1/1000), converges to homogeneous equilibrium
2. **Complex/Learning regime**: GA invoked frequently (1/250), produces heterogeneous strategies, technical trading, excess volatility, bubbles/crashes

## Sources
- Arthur et al. (1997) "Asset Pricing Under Endogenous Expectations in an Artificial Stock Market"
- LeBaron et al. (1999) "Time series properties of an artificial stock market"
- Ehrentreich (2007) "Agent-Based Modeling: The SFI ASM Revisited"
