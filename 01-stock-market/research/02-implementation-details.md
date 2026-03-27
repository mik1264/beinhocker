# SFI ASM - Implementation Details

## Rule Encoding
- J=12 bit condition arrays using ternary values {1, 0, #}
- # means "don't care" (wildcard)
- Bits 1-6: Fundamental descriptors (price/dividend ratio thresholds: 0.250, 0.500, 0.750, 0.875, 1.000, 1.125)
- Bits 7-10: Technical indicators (price vs 5, 10, 100, 500-period moving averages)
- Bits 11-12: Control bits (always 1 and 0)

## Forecasting Rule Structure
Each rule has condition C and parameters (var, a, b):
- Forecast: E[p+d] = a*(p+d) + b
- Variance updated via exponential smoothing: var_t = (1-θ)*var_{t-1} + θ*(error²)
- Rule fitness: f = -var - c*specificity, where c=0.005

## Initialization
- Condition bits: # with p=0.90, 0 with p=0.05, 1 with p=0.05
- Parameter a: uniform [0.7, 1.2]
- Parameter b: uniform [-10, 19]
- 500-step observation period before trading begins

## Market Parameters
- N=25 traders, each with 1 initial share
- Initial price = d/r = 100 (with d_bar=10, r=0.10)
- Max 10 shares per period, max short position 5 shares
- Dividend: d_t = 10 + 0.95*(d_{t-1} - 10) + w_t, where w_t ~ N(0, 0.0743)

## Known Issues
- Original model had faulty mutation operator causing upwardly biased bit distribution
- Ehrentreich (2007) identified and corrected this issue
