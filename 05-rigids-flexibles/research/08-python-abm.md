# Agent-Based Modeling in Python: Implementation Notes

## Available Frameworks

1. **Mesa**: Most popular Python ABM framework, supports grid/continuous environments, hierarchical agent groupings
2. **Helipad**: Hook-based architecture for shallow learning curve
3. **BPTK-Py**: System dynamics and ABM combined
4. **Custom implementation**: Often best for specific models like Rigids vs Flexibles

## Recommended Approach for This Simulation

Custom Python implementation (no framework dependency) because:
- The model is relatively simple and well-defined
- We need specific hierarchy structure not well-served by grid-based frameworks
- Custom allows direct control over promotion/exit mechanics
- Easier to generate CSV output and connect to HTML visualizer

## Core Implementation Pattern

```python
class Agent:
    type: str  # "rigid" or "flexible"
    fixed_strategy: str  # "A" or "B" (only used by rigids)
    experience: int
    performance_history: list
    level: int

class Hierarchy:
    levels: int  # default 4
    branching_factor: int  # default 3
    agents: dict[int, list[Agent]]  # level -> agents

class Environment:
    current_state: str  # "A" or "B"
    stability: float  # avg ticks between switches
    mode: str  # "punctuated" or "random"
```

## Key Design Decisions

1. Use numpy random for reproducibility (seeded)
2. Track all metrics in lists for CSV export
3. Each tick: evaluate performance -> promote/exit -> update environment
4. Performance = match_score + experience_weight * experience
5. Flexible agents observe with noise (configurable)
