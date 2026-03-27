# LeBaron, Palmer, Tayler (1999) - Key Results and Parameters

## Paper
"Time series properties of an artificial stock market"
Journal of Economic Dynamics and Control, 23(9-10), 1487-1516

## Model Parameters
- 25 agents, each with 100 forecasting rules
- 12-bit condition strings (6 fundamental + 4 technical + 2 control)
- AR(1) dividend: d_t = 10 + 0.95*(d_{t-1} - 10) + ε, ε ~ N(0, 0.0743)
- Interest rate: r = 0.10
- Risk aversion: λ = 0.50
- Initialization: condition bits # with p=0.90, 0 with p=0.05, 1 with p=0.05
- Forecast parameters: a ~ U[0.7, 1.2], b ~ U[-10, 19]

## Experimental Design
- 260,000 periods (250,000 preliminary + 10,000 data collection)
- 25 replications per treatment with different random seeds
- Two key treatments: slow vs fast GA invocation

## Key Results

### Return Properties
- Excess kurtosis (fat tails) in complex regime
- Very little linear autocorrelation (near-efficient market)
- Persistent volatility (long memory in |returns|)

### Volume Properties
- Trading volume strongly persistent
- Correlated with price volatility

### Predictability
- Small predictability from technical trading rules
- Price/dividend ratio has forecasting power
- Similar to patterns found in real market data

### Two Regimes
- **Slow learning** (GA every ~1000 periods): Near-rational equilibrium
- **Fast learning** (GA every ~250 periods): Complex dynamics with realistic stylized facts

## Significance
- First rigorous demonstration that agent heterogeneity + learning can produce realistic market statistics
- Showed that technical trading can emerge endogenously
- Demonstrated that complexity arises from the interaction of learning agents
