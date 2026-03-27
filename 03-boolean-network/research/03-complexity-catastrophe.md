# Complexity Catastrophe

## Definition
The complexity catastrophe is Kauffman's finding that fitness outcomes from adaptive search on NK landscapes show a sharp decline at high complexity (high K). When interdependencies among dimensions become too dense, adaptive search becomes ineffective.

## Mechanism
- As K increases, the fitness landscape becomes more rugged
- More local optima appear, but their average fitness decreases
- At K=N-1 (maximum complexity), fitness of local optima approaches global mean
- The landscape becomes so rugged that hill-climbing cannot find good solutions

## NK Fitness Landscape
- N = number of components/genes/decisions
- K = number of epistatic interactions per component
- K=0: smooth landscape, single global optimum (Fujiyama)
- K=N-1: maximally rugged, random landscape (uncorrelated)
- Fitness = average of N fitness contributions, each depending on K+1 components

## Organizational Application
- Organizations as networks of interdependent decisions
- K represents degree of coupling between business units/decisions
- Low K: easy optimization but limited capability
- High K: rich capability but optimization is nearly impossible
- Optimal K: enough interdependency for capability, not so much that adaptation fails

## The Patch Procedure (Kauffman's Solution)
- Break the organization into semi-autonomous "patches"
- Each patch optimizes locally with limited cross-patch interactions
- Reduces effective K without eliminating all interdependencies
- Analogous to modular organizational design

## Sources
- Kauffman, S.A. (1993). The Origins of Order.
- Levinthal, D.A. (1997). Adaptation on Rugged Landscapes. Management Science.
