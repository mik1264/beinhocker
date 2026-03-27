# Beer Game: Information Sharing and Demand Visibility

## The Information Problem
In the standard Beer Game:
- Each player only sees their **own inventory and backlogs**
- Upstream players see **orders from their immediate customer**, not final consumer demand
- No communication between players allowed
- This local-only information creates systematic distortion

## Impact of Information Sharing

### Bullwhip Reduction
- Information sharing reduces mean bullwhip effect by roughly **60%**
- Cash-flow bullwhip reduced by approximately **70%**
- Variance amplification attenuated by **~50%** at the factory level

### Mechanisms of Improvement
1. **Demand visibility**: Upstream agents can see actual consumer demand
2. **Better forecasting**: Access to point-of-sale data improves demand estimates
3. **Reduced phantom ordering**: Knowledge of pipeline state prevents over-ordering
4. **Coordination**: Aligned ordering policies across echelons

## Types of Information Sharing

### Point-of-Sale (POS) Data Sharing
- All echelons see actual consumer demand
- Eliminates demand signal processing distortion
- Most effective single intervention

### Inventory Level Sharing
- All echelons see each other's inventory positions
- Enables better allocation and prioritization
- Reduces rationing game effects

### Order Pipeline Sharing
- Visibility into orders-in-transit
- Directly addresses supply line underweighting
- Helps β approach optimal value of 1.0

## Mixed Results
- Direct customer demand sharing **isn't always helpful** without complementary changes
- Analyzing **demand volatility** (not just levels) can dramatically improve outcomes
- Information sharing works best when combined with **appropriate decision rules**
- Without behavioral change, more information can actually increase ordering variance

## Beer Game Variant: Information Sharing Mode
When the brewery can see retail demand directly:
- Factory uses consumer demand for forecasting instead of distributor orders
- Dramatically reduces upstream amplification
- Illustrates the value of end-to-end visibility

## Real-World Applications
- VMI (Vendor Managed Inventory): Supplier manages customer's stock
- CPFR (Collaborative Planning, Forecasting, and Replenishment)
- Real-time EDI and IoT-enabled demand sensing
- Blockchain for supply chain transparency

## Sources
- [Beer Game by AI Agents](https://infotheorylab.github.io/beer-game/)
- [Beer Distribution Game - Wikipedia](https://en.wikipedia.org/wiki/Beer_distribution_game)
- [Springer - Impact of Information Sharing on Bullwhip Effect](https://link.springer.com/article/10.1007/s12351-025-00915-3)
