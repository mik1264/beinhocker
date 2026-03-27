# Jain-Krishna Model: Autocatalytic Sets and Evolving Networks

## Overview
The Jain-Krishna model (1998-2002) simulates a "prebiotic pond" containing s chemical species that coevolve through catalytic interactions in a directed network. It demonstrates how autocatalytic sets emerge, grow, and collapse in patterns resembling punctuated equilibrium.

## Model Structure
- **Network**: Directed graph with s nodes. Adjacency matrix C where c_ij = 1 (with probability p) means species j catalyzes species i. Self-catalysis forbidden.
- **Population dynamics**: dx_i/dt = Σ_j c_ij x_j - x_i Σ_k c_ik x_k, with populations normalized so Σx_i = 1.
- **Steady state**: System reaches attractor X = (X_1, ..., X_s) depending on network topology.

## Autocatalytic Sets (ACS)
- Subgraph where each node has at least one incoming link from within the subgraph
- **Core**: Maximal subgraph from which all ACS nodes are reachable
- **Periphery**: Remaining ACS members sustained by core
- **Largest eigenvalue λ₁**: Measures core strength; λ₁ = 0 when no ACS exists, λ₁ ≥ 1 when ACS exists

## Evolution Algorithm
1. Initialize random graph with s nodes, catalytic probability p
2. Integrate population dynamics to reach attractor
3. Remove least-populated species, introduce new node with random connections
4. Repeat

## Innovation and Extinction Mechanics
- **Innovation**: New species achieves nonzero population in attractor
- **Keystone species**: Species whose removal produces zero core overlap
- **Complete crashes**: ACS vanishes when keystone removed (mean 98.2 species extinct)
- **Core-transforming takeovers**: New ACS replaces old (mean 48.2 species extinct)
- **Dormant innovation takeovers**: Pre-existing downstream innovation activates (mean 62.2 species extinct)

## Parameters
- s = 100 (species capacity), p = 0.0025 (catalytic probability)
- Analysis of 1.55 million iterations showed 612 core-shift events

## Sources
- Jain & Krishna, "Autocatalytic Sets and the Growth of Complexity" (PRL, 1998)
- Jain & Krishna, "Large Extinctions in an Evolutionary Model" (PNAS, 2002)
- Jain & Krishna, "A Model for the Emergence of Cooperation" (PNAS, 2001)
