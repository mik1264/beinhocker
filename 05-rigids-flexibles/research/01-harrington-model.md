# Harrington's Rigidity of Social Systems Model

## Source
Joseph E. Harrington, Jr. "Rigidity of Social Systems." Journal of Political Economy, 1999, vol 107, pp 40-64.

## Core Model

Harrington explores why members of corporations and governments tend to be resistant to change. The model encompasses two endemic features of hierarchical social systems:

1. **Hierarchical Selection**: The social system is modeled as a hierarchy with an implicit selection process that determines who advances to higher levels. Agents who perform better advance.

2. **Imitation Dynamics**: An agent's behavior is partially determined by imitating those who have risen in the ranks. Junior agents look at what successful seniors did and copy their approach.

## Key Mechanism

- Agents face an environment that can be in different states
- Agents choose strategies/behaviors in response to environmental conditions
- "Rigid" agents stick with the same behavior regardless of environmental state
- "Flexible" agents adjust their behavior to match the current environment
- Promotion is based on performance (up-or-out tournament)
- New entrants learn by imitating the behavior of those who were promoted

## Critical Finding

**A behavioral norm of being rigid is found to be more prevalent and robust than one of being flexible.** Even a more volatile environment may induce agents to be more resistant to change.

### Why Rigidity Wins

The key insight is about selection bias in promotion:
- In a stable environment, rigid agents who happen to match the environment accumulate experience and perform well consistently
- They get promoted, and juniors imitate their rigid approach
- When the environment changes, the organization is full of rigid agents with the wrong strategy
- But even then, the few rigid agents who happen to have the NEW right strategy start outperforming
- Flexible agents, who adapt but never accumulate deep expertise, rarely outperform the best rigid agents
- This creates a self-reinforcing cycle favoring rigidity

## Related Work

- Harrington 1998 version with heterogeneous agents and simple behavioral rules: agents at higher hierarchy levels are MORE rigid
- Harrington 1999 version with homogeneous agents and subgame perfect equilibrium: higher-level agents prove MORE flexible
- Chang & Harrington 2006: Extended to agent-based models of organizations in Handbook of Computational Economics

## Relevance to Beinhocker Simulation

This is the foundational model for the "Rigids vs Flexibles" simulation. The key dynamics are:
- Tournament-based promotion through hierarchy levels
- Rigid agents: always play their born strategy, gain experience bonus
- Flexible agents: observe and adapt, but with noise and lower experience accumulation
- Environment switches between states (punctuated equilibrium pattern)
- The promotion mechanism creates a self-reinforcing bias toward rigidity
- Organizations dominated by rigids perform well in stability but fail catastrophically at regime changes
