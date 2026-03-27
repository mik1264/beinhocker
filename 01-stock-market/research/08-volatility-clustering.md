# Volatility Clustering

## Definition
"Large changes tend to be followed by large changes, of either sign, and small changes tend to be followed by small changes" (Mandelbrot, 1963)

## GARCH Connection
- GARCH(1,1) captures volatility clustering with lagged variance terms
- σ²_t = ω + α*ε²_{t-1} + β*σ²_{t-1}
- Agent-based models can produce GARCH-like dynamics endogenously

## Agent-Based Explanation
- Agents switch between strategies based on relative performance
- Switching times correspond to crossing thresholds
- Time between switches is heavy-tailed (power-law decay)
- This creates alternating low/high volatility regimes

## SFI ASM Mechanism
- In complex regime, GA occasionally reshuffles agent strategies
- When many agents simultaneously adopt new strategies, volatility spikes
- Stable periods occur when current rules perform well (no GA pressure)
- The interaction between learning rate and market stability creates clusters

## Measuring Volatility Clustering
- Autocorrelation of absolute or squared returns
- Should decay slowly (long memory)
- ARCH/GARCH model fitting
- Hurst exponent estimation

## Key Finding
- SFI ASM with frequent GA invocation produces persistent volatility
- Trading volume also shows clustering, correlated with price volatility
- These emerge endogenously without being programmed
