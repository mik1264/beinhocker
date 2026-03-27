# Tournament-Based Promotion Models

## Sources
- Lazear & Rosen, "Rank-Order Tournaments as Optimum Labor Contracts," Journal of Political Economy, 1981
- Connelly et al., "Tournament Theory," Journal of Management, 2014

## Core Mechanism

Tournament theory (Lazear & Rosen 1981) posits:
- Compensation is based on relative ranking within an organization, not absolute performance
- Promotions function as sequential elimination tournaments
- Employees compete with peers at their level; best performers advance
- Worst performers exit or are demoted
- This creates incentives for effort and self-selection

## Key Properties

1. **Relative performance**: Only rank matters, not absolute score
2. **Winner-take-all dynamics**: Small performance differences lead to large career outcomes
3. **Sequential elimination**: Each level is a new round of competition
4. **Self-reinforcing**: Winners accumulate advantages (experience, visibility, resources)

## Recent Findings on Limitations

Research (2024) shows tournament-based evaluation with forced ranking produces:
- 32% classification error under idealized conditions
- 53% error rates under realistic conditions
- Adverse selection as high-performers exit when they observe random outcomes
- Risk-averse behavior that suppresses innovation

## Connection to Rigids vs Flexibles

The promotion mechanism in the simulation should follow tournament dynamics:
- At each level, agents compete based on performance
- Best performer at each level promoted up
- Worst performer at bottom level exits, replaced by random new agent
- This creates selection pressure that interacts with agent type:
  - In stable environments: rigid agents with right strategy consistently outperform
  - They get promoted, creating rigid-dominated upper levels
  - At regime change: rigid-dominated hierarchy is slow to adapt
  - Flexible agents rarely accumulate enough consistent performance to reach top levels
