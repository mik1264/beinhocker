# Small-World Networks

## Watts-Strogatz Model (1998)
Generates graphs with small-world properties:
- Short average path lengths (like random graphs)
- High clustering coefficient (like regular lattices)

## Algorithm
1. Start with a ring lattice of N nodes, each connected to K nearest neighbors
2. For each edge, with probability β, rewire one end to a random node
3. β=0: regular lattice; β=1: random graph; 0<β<1: small-world

## Key Properties
- Small β (≈0.01-0.1) dramatically reduces average path length
- Clustering coefficient remains high for small β
- "Six degrees of separation" phenomenon
- Regional specialization with efficient global information transfer

## Relevance to Boolean Networks
- Network topology affects dynamics
- Random topology: standard Kauffman model
- Lattice topology: spatially structured, different phase transition
- Small-world topology: intermediate between random and lattice
- Hierarchical topology: modular structure with cross-module links

## Organizational Analogy
- Lattice = strict hierarchy (communicate only with neighbors)
- Random = flat organization (anyone talks to anyone)
- Small-world = hierarchy with cross-cutting connections
- Best organizational designs may be small-world: efficient communication + local specialization

## Implementation
```python
def watts_strogatz(N, K, beta):
    # Start with ring lattice
    edges = set()
    for i in range(N):
        for j in range(1, K//2 + 1):
            edges.add((i, (i+j) % N))

    # Rewire with probability beta
    for i in range(N):
        for j in range(1, K//2 + 1):
            if random.random() < beta:
                # Rewire edge (i, (i+j)%N) to (i, random_node)
                new_target = random.randint(0, N-1)
                while new_target == i or (i, new_target) in edges:
                    new_target = random.randint(0, N-1)
                edges.discard((i, (i+j) % N))
                edges.add((i, new_target))
    return edges
```

## Sources
- Watts, D.J. & Strogatz, S.H. (1998). Collective dynamics of 'small-world' networks. Nature.
