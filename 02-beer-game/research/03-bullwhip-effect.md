# Bullwhip Effect: Supply Chain Amplification

## Definition
The bullwhip effect describes how small fluctuations in demand at the retail level cause progressively larger fluctuations in demand at the wholesale, distributor, manufacturer, and raw material supplier levels.

## Key Statistics
- In studies with a simple four-step supply chain, small variations in initial demand could lead to **order amplitudes of 900%** only four steps upstream
- The variance of orders is larger than the variance of sales, and distortion increases moving upstream
- Information sharing reduces mean bullwhip effect by roughly **60%**

## Four Major Causes (Lee, Padmanabhan & Whang, 1997)
1. **Demand Signal Processing**: Each echelon uses local forecasting, amplifying perceived demand changes
2. **Rationing Game**: When supply is limited, customers inflate orders to secure allocation
3. **Order Batching**: Accumulating demand into larger, less frequent orders amplifies variability
4. **Price Variations**: Forward-buying during promotions creates artificial demand spikes

## Behavioral Causes
- **Supply-chain underweighting**: Decision-makers fail to account for orders already in the pipeline (Sterman's β < 1)
- **Anchoring bias**: Over-reliance on recent demand as a predictor
- **Panic ordering**: Anxiety-driven over-ordering when inventory falls below targets
- **Phantom ordering**: Placing orders for goods already in transit

## Measurement: Bullwhip Ratio
```
BWR = Var(Orders_placed) / Var(Orders_received)
```
- BWR > 1 indicates bullwhip amplification
- BWR = 1 indicates no amplification (optimal)
- BWR < 1 indicates demand smoothing

## Simulation Findings
- Statistically significant variables: α, order batching, β, material delay, information delay, purchasing delay
- Lead-time variability exacerbates variance amplification
- Information sharing and information quality are highly significant — variance amplification attenuated by **~50%** at the factory

## Sources
- [Bullwhip Effect - Wikipedia](https://en.wikipedia.org/wiki/Bullwhip_effect)
- [Lee et al. - Information Distortion in a Supply Chain](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546)
- [MIT Sloan Management Review - The Bullwhip Effect in Supply Chains](https://sloanreview.mit.edu/article/the-bullwhip-effect-in-supply-chains/)
