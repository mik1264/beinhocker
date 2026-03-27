# Schelling Segregation Model: Theoretical Background

## The Model (Schelling, 1971)

Thomas Schelling's segregation model is one of the most celebrated examples of emergence in the social sciences. Published in "Dynamic Models of Segregation" (1971) and later expanded in *Micromotives and Macrobehavior* (1978), the model demonstrates a profound and counterintuitive result: **extreme macro-level segregation can arise from mild individual preferences for similarity**.

### Setup

- A checkerboard-like grid is populated with two types of agents (e.g., representing two demographic groups) and some empty cells.
- Each agent evaluates its **Moore neighborhood** (the 8 surrounding cells) and counts the fraction of occupied neighboring cells that contain agents of its own type.
- If this fraction falls below a **tolerance threshold**, the agent is "unhappy" and will relocate to a random empty cell.
- Agents do not coordinate. They do not choose *where* to move strategically -- they simply pick a random vacancy.

### The Central Paradox

A threshold of 30% means an agent is happy even when 70% of its neighbors are different. This is not bigotry -- it is a preference for not being *completely* isolated. Yet when all agents act on this mild preference simultaneously:

1. **Initial random placement** yields neighborhoods that are approximately 50% same-type (as expected by chance with equal group sizes).
2. **A few agents** on the margins of mixed areas find themselves below threshold and move.
3. **Their departure** changes the composition of two neighborhoods -- the one they left and the one they entered.
4. **Cascading relocations** ensue, each creating new unhappy agents at the boundaries.
5. The system settles into an equilibrium where **neighborhoods are 70-80% homogeneous** -- far exceeding what any individual demanded.

This is Schelling's paradox: **no one wants segregation, yet everyone gets it**.

## Beinhocker's Context: Emergence and Complexity

Eric Beinhocker discusses Schelling's model in *The Origin of Wealth* (2006) as a canonical illustration of **emergence** -- the phenomenon where macro-level patterns arise from micro-level interactions in ways that cannot be predicted by studying individuals in isolation.

Key themes from Beinhocker's treatment:

- **Non-linearity**: The relationship between threshold and segregation is highly non-linear. Small changes in individual tolerance can produce dramatic changes in aggregate patterns.
- **Unintended consequences**: The emergent segregation is not desired by any participant. It is a collective outcome of individual optimizing behavior.
- **Path dependence**: The specific pattern of clusters depends on initial conditions and the order of agent moves, but the *degree* of segregation is remarkably robust.
- **No equilibrium in the traditional sense**: While the system stabilizes (all agents become happy), the resulting configuration is one of many possible stable states, none of which is "optimal" in any global sense.

## Key Parameters and Their Effects

### Tolerance Threshold
- **0%**: No movement occurs. Grid stays random. Control case.
- **10%**: Very mild preference. Some measurable segregation, but limited.
- **30%**: Schelling's classic case. Extreme segregation from mild preferences.
- **50%**: Agents want a majority of neighbors to be like them. Fast, strong segregation.
- **75%**: High intolerance. Near-total segregation. May not converge if too few empty cells.

### Population Density
- **Low (50%)**: Many empty cells. Agents can easily find satisfactory positions. Fast convergence.
- **Medium (70%)**: Schelling's typical setup. Good balance of mobility and constraint.
- **High (95%)**: Very few empty cells create a bottleneck. Segregation proceeds slowly and may be incomplete -- unhappy agents cannot find vacancies.

### Group Ratio
- **Equal (50/50)**: Symmetric dynamics. Both groups segregate similarly.
- **Asymmetric (70/30)**: The minority group faces more pressure (higher chance of being surrounded by the majority) and tends to form tighter, more compact clusters. The majority group may barely notice the segregation.

## Metrics

### Segregation Index
Average fraction of same-type neighbors across all agents. In a perfectly random 50/50 grid, this would be approximately 0.50. Values above 0.70 indicate strong segregation.

### Happiness Rate
Fraction of agents whose same-type neighbor fraction meets or exceeds their threshold. Rises from some initial level to 1.0 as the system reaches equilibrium.

### Interface Density
Fraction of adjacent agent pairs that are of *different* types. This is the complement of segregation -- it measures how much intergroup contact exists at neighborhood boundaries. Falls as segregation increases.

### Moves Per Tick
Number of agents that relocated during each time step. Starts high (many unhappy agents in random placement) and falls toward zero as the system stabilizes. The shape of this curve reveals the dynamics: a sharp drop suggests rapid tipping; a gradual decline suggests more incremental sorting.

### Largest Cluster Size
Size of the largest contiguous group of same-type agents (connected via Moore neighborhoods). Grows as segregation proceeds. In extreme cases, can encompass a significant fraction of all agents of one type.

## Connections to Other Models

- **Sugarscape** (Epstein & Axtell): Another grid-based model where simple agent rules produce emergent macro patterns (inequality from heterogeneous resource gathering).
- **Game of Life** (Conway): Cellular automaton showing emergence of complex patterns from simple local rules, though without agent agency.
- **Voter Model**: Agents adopt their neighbors' opinions, producing consensus clustering through a different mechanism.
- **Sakoda's Model** (1971): Actually preceded Schelling and explored similar dynamics with attraction/repulsion parameters.

## References

- Schelling, T. C. (1971). "Dynamic Models of Segregation." *Journal of Mathematical Sociology*, 1(2), 143-186.
- Schelling, T. C. (1978). *Micromotives and Macrobehavior*. W.W. Norton.
- Beinhocker, E. D. (2006). *The Origin of Wealth*. Harvard Business Press.
- Clark, W. A. V., & Fossett, M. (2008). "Understanding the Social Context of the Schelling Segregation Model." *Proceedings of the National Academy of Sciences*, 105(11), 4109-4114.
