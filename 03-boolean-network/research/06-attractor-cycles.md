# Boolean Network Attractor Cycles

## Definitions
- **State**: Binary vector of length N representing all node values
- **State space**: All 2^N possible states
- **Trajectory**: Sequence of states from synchronous updates
- **Attractor**: Repeating pattern of states (cycle or fixed point)
- **Basin of attraction**: Set of initial states that lead to a given attractor
- **Cycle length**: Number of states in the attractor cycle

## Attractor Properties by Regime
### Ordered (K < Kc)
- Few attractors, short cycles
- Large basins of attraction
- Cycle length ~ polynomial in N
- For K=2: ~√N attractors with ~√N cycle length

### Chaotic (K > Kc)
- Many attractors, long cycles
- Small basins of attraction
- Cycle length ~ exponential in N
- Attractors are unstable to perturbations

### Critical (K = Kc)
- Power-law distribution of cycle lengths
- Moderate number of attractors
- Complex basin structure

## Detection Algorithms
### Exhaustive Enumeration (small N only)
- Enumerate all 2^N states
- Build full state transition graph
- Find all cycles
- Feasible for N ≤ ~20

### Floyd's Cycle Detection (any N)
- Use "tortoise and hare" algorithm
- Two pointers: slow (1 step) and fast (2 steps)
- When they meet, cycle detected
- Then find cycle length by advancing one pointer

### Random Sampling
- Pick random initial states
- Simulate until cycle detected
- Repeat many times to estimate attractor statistics
- May miss rare attractors

## Implementation Notes
- Store states as tuples of ints for hashability
- Use set/dict to detect revisited states
- For large N, use bit-packing for efficiency
- State transition graph is a functional graph (each state has exactly one successor)

## Sources
- Kauffman, S.A. (1993). The Origins of Order.
- Drossel, B. (2008). Random Boolean Networks.
