# Boolean Network Python Simulation

## Existing Tools
- **PyBoolNet**: Full-featured, uses NuSMV for model checking, NetworkX for graphs
- **BoolSi**: High-performance, YAML-based configuration
- **BooleanNet**: Supports synchronous, stochastic, and hybrid models
- **SimpleBool**: User-friendly, no coding experience required

## Implementation Approach

### Core Data Structures
```python
class Node:
    state: bool           # Current binary state
    inputs: list[int]     # Indices of K input nodes
    truth_table: list[bool]  # 2^K entries
    bias: float           # Probability of 1 in truth table

class Network:
    nodes: list[Node]
    N: int                # Number of nodes
    K: int                # Connectivity
    topology: str         # random, lattice, hierarchy, small-world
```

### State Update (Synchronous)
```python
def update(network):
    new_states = []
    for node in network.nodes:
        input_states = [network.nodes[i].state for i in node.inputs]
        idx = sum(s << k for k, s in enumerate(input_states))
        new_states.append(node.truth_table[idx])
    for i, node in enumerate(network.nodes):
        node.state = new_states[i]
```

### Attractor Detection
```python
def find_attractor(network, max_steps=10000):
    seen = {}
    state = get_state(network)
    for t in range(max_steps):
        state_key = tuple(state)
        if state_key in seen:
            cycle_length = t - seen[state_key]
            return cycle_length
        seen[state_key] = t
        update(network)
        state = get_state(network)
    return None  # No attractor found in max_steps
```

### Derrida Curve
```python
def derrida_curve(network, num_pairs=1000, distances=None):
    if distances is None:
        distances = range(1, network.N + 1)
    results = {}
    for d in distances:
        d_out_list = []
        for _ in range(num_pairs):
            s1 = random_state(network.N)
            s2 = flip_random_bits(s1, d)
            set_state(network, s1); update(network); s1_next = get_state(network)
            set_state(network, s2); update(network); s2_next = get_state(network)
            d_out_list.append(hamming(s1_next, s2_next))
        results[d] = np.mean(d_out_list)
    return results
```

### Visualization Approaches
- NetworkX + matplotlib for network graphs
- Heatmap for state evolution over time
- Phase diagram: 2D grid of K vs bias, colored by regime
- Browser-based: D3.js or plain Canvas for interactive visualization

## Sources
- PyBoolNet documentation
- BoolSi documentation
- Custom implementation patterns
