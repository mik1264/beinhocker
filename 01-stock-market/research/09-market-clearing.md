# Double Auction and Market Clearing

## SFI ASM Market Mechanism
The original SFI ASM uses a **call market** (not continuous double auction):
- All agents submit orders simultaneously
- A specialist/auctioneer finds the clearing price
- Price set so total demand = total supply (N shares)

## Price Determination
1. Each agent computes demand based on their forecast: x_i = (E[p+d] - p(1+r)) / (λ*var_i)
2. Specialist finds price p* where Σx_i(p*) = N (total shares)
3. This is equivalent to a Walrasian auctioneer

## Alternative: Iterative Auction
Some implementations use iterative adjustment:
- Specialist announces trial price
- Agents respond with buy/sell orders
- Price adjusted up if excess demand, down if excess supply
- Maximum 6 iterations to converge

## Simplified Approach for Simulation
For computational efficiency:
- Aggregate demand curve is monotonically decreasing in price
- Can use bisection method to find clearing price
- Or solve linear system if demands are linear in price

## Demand Function
With CARA utility and linear forecasts:
- x_i(p) = (a_i*(p+d) + b_i - p*(1+r)) / (λ*σ²_i)
- Aggregate: X(p) = Σ x_i(p)
- Clear at p* where X(p*) = N

## Constraints
- Maximum position: 10 shares (long)
- Maximum short: 5 shares
- These constraints create nonlinearities at boundaries
