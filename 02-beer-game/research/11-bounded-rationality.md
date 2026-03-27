# Inventory Management: Bounded Rationality and Ordering Heuristics

## Bounded Rationality Framework
Following Herbert Simon (1982), Cyert & March (1963):
- Decision-makers operate under **cognitive and information limitations**
- Cannot compute globally optimal solutions in real-time
- Use **satisficing** rather than optimizing strategies
- Heuristics are "good enough" but systematically suboptimal

## Common Ordering Heuristics

### 1. Order-Up-To (s, S) Policy
- When inventory drops to reorder point **s**, order up to level **S**
- Simple and widely used in practice
- Modified version handles minimum/maximum order constraints
- Excellent performance in numerical studies

### 2. Anchor-and-Adjust (Sterman)
- Anchor on expected demand
- Adjust for inventory and supply line discrepancies
- Empirically validated in Beer Game experiments
- Captures bounded rationality naturally

### 3. Order-What-You-Sold (Naive)
- Simply pass through incoming orders
- No inventory management attempt
- Baseline comparison for other strategies

### 4. Newsvendor-Based Heuristics
- Based on single-period inventory problem
- Retailers tend to **overorder** to avoid shortage (loss aversion)
- Aversion to explicit loss of shortage > implicit loss of surplus

## Behavioral Biases in Ordering

### Loss Aversion
- Shortage costs ($1/case) are **2x** holding costs ($0.50/case)
- But psychological aversion to backlog exceeds this ratio
- Leads to systematic overordering

### Recency Bias
- Overweighting recent demand observations
- High θ in exponential smoothing
- Creates overreaction to demand changes

### Anchoring
- Initial conditions (12 cases, 4/week) serve as anchors
- Difficulty adjusting expectations when demand regime changes
- Persistent return to historical ordering patterns

### Neglect of Pipeline
- Orders in transit are cognitively "invisible"
- Sterman's β << 1 captures this systematically
- Root cause of boom-bust cycles

## Optimal vs. Behavioral Performance
| Strategy | Typical Cost | Description |
|----------|-------------|-------------|
| Optimal | ~$200 | Full information, perfect rationality |
| Behavioral | ~$2,000 | Anchor-and-adjust with biases |
| Naive | ~$800-1,500 | Pass-through ordering |
| With information sharing | ~$400-600 | Behavioral + demand visibility |

## Sources
- [Bounded Rationality - Wikipedia](https://en.wikipedia.org/wiki/Bounded_rationality)
- [Behavioral Inventory Decisions](https://www.researchgate.net/publication/328407037_Behavioral_Inventory_Decisions)
- [Bounded Rationality in Newsvendor Models](https://repository.upenn.edu/bitstreams/713efa64-8004-4a68-abdd-5564cf885165/download)
