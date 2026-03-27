# Condition-Action Rules in the SFI ASM

## Binary Condition Strings
Each forecasting rule has a condition part encoded as a ternary string (0, 1, #):
- Matched against current market state
- More specific rules (fewer #s) have higher specificity cost
- Multiple rules can be active simultaneously; most accurate one is used

## Market State Descriptors
1. price/dividend > 0.25 * fundamental value
2. price/dividend > 0.50 * fundamental value
3. price/dividend > 0.75 * fundamental value
4. price/dividend > 0.875 * fundamental value
5. price/dividend > 1.00 * fundamental value
6. price/dividend > 1.125 * fundamental value
7. price > 5-period moving average
8. price > 10-period moving average
9. price > 100-period moving average
10. price > 500-period moving average
11. always 1 (control)
12. always 0 (control)

## Action Part
- Linear forecast: E[p+d] = a*(p+d) + b
- Parameters a and b are real-valued
- Each rule tracks its own forecast variance

## Rule Selection
- Check which rules' conditions match current market state
- Among active rules, select the one with highest fitness (lowest variance + specificity penalty)
- Use selected rule's forecast to compute optimal demand

## Fitness/Credit Assignment
- f = -variance - c*specificity
- Variance updated exponentially: v_t = (1-θ)*v_{t-1} + θ*error²
- c = 0.005 penalizes overly specific rules
