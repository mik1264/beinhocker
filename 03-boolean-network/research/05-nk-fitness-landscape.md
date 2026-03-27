# NK Model Fitness Landscape

## Mathematical Definition
For N binary components, each with K epistatic interactions:
- Fitness W = (1/N) Σ w_i(x_i, x_{i1}, ..., x_{iK})
- Each w_i depends on gene i and K other genes
- w_i values drawn uniformly from [0,1]
- Total fitness is average of N fitness contributions

## Ruggedness Spectrum
- K=0: Single-peaked "Fujiyama" landscape, unique global optimum
- K small: Smooth landscape, few local optima, correlation between neighbors
- K large: Rugged landscape, many local optima
- K=N-1: Completely random, uncorrelated landscape

## Number of Local Optima
- Grows exponentially with N for K > 0
- For K=N-1: approximately 2^N / (N+1) local optima
- Average fitness of local optima decreases with K

## Python Implementation Approach
```python
# Key data structure: lookup tables for fitness contributions
# For each gene i, create a table of 2^(K+1) fitness values
# indexed by the states of gene i and its K epistatic partners

import numpy as np

def create_nk_landscape(N, K):
    # For each gene, pick K random epistatic partners
    interactions = [np.random.choice([j for j in range(N) if j != i], K, replace=False)
                    for i in range(N)]
    # Create random fitness contribution tables
    fitness_tables = [np.random.random(2**(K+1)) for _ in range(N)]
    return interactions, fitness_tables

def evaluate_fitness(genotype, interactions, fitness_tables, N, K):
    total = 0
    for i in range(N):
        # Build index from gene i and its K partners
        bits = [genotype[i]] + [genotype[j] for j in interactions[i]]
        idx = sum(b << k for k, b in enumerate(bits))
        total += fitness_tables[i][idx]
    return total / N
```

## Sources
- Kauffman, S.A. & Levin, S. (1987). Towards a general theory of adaptive walks on rugged landscapes.
- Kauffman, S.A. (1993). The Origins of Order.
