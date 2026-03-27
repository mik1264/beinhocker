# Bak-Sneppen Model of Evolution

## Overview
Developed by Per Bak and Kim Sneppen (1993) to show how self-organized criticality explains punctuated equilibrium in the fossil record.

## Model Mechanics
1. N species arranged on a ring/lattice, each with random fitness in [0,1]
2. Each timestep: find species with lowest fitness
3. Replace it AND its two neighbors with new random fitness values
4. System self-organizes to critical threshold (~0.667 for 1D)

## Key Properties
- **Self-organized criticality**: System evolves to critical state without external tuning
- **Avalanches**: Bursts of activity (species replacements) follow power-law size distribution
- **Punctuated equilibrium**: Long periods of stasis interrupted by avalanches
- **No external cause needed**: Large extinction events emerge from same dynamics as small ones
- **Fitness threshold**: Below threshold, species are unstable; above, they persist

## Relevance to Our Simulation
- Demonstrates that replacing lowest-fitness species + neighbor effects → SOC
- Power-law distribution of avalanche sizes emerges naturally
- Provides simpler alternative mechanism to Jain-Krishna for punctuated equilibrium
- Our model combines Bak-Sneppen's replacement rule with Jain-Krishna's network structure

## Sources
- Bak & Sneppen, "Punctuated Equilibrium and Criticality in a Simple Model of Evolution" (PRL, 1993)
- Bak, "How Nature Works: The Science of Self-Organised Criticality" (1996)
