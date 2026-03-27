# Genetic Algorithm for Rule Evolution

## Population Management
- K=100 rules per trader
- Elite retention: top 80% survive
- Bottom 20% culled and replaced each GA invocation

## Selection
- Tournament selection: pairwise comparison of fitness
- Winners selected as parents for offspring

## Crossover (probability P=0.30 slow, P=0.10 medium)
- Uniform crossover of condition bits
- Three equiprobable methods for parameter vectors:
  1. Take from parent A
  2. Take from parent B
  3. Average of both parents

## Mutation
- Applied to offspring (probability 1-P for mutation-only offspring)
- Condition bits: random flip (0->1, 1->0, or to/from #)
- Parameters: small random perturbation
- Mutation rate per bit typically 0.003-0.01

## GA Invocation
- NOT every period - stochastic invocation
- Slow learning: probability 1/1000 per period per agent
- Medium/fast learning: probability 1/250 per period per agent
- Each agent's GA invoked independently

## Fitness Function
- f = -forecast_variance - c*specificity
- Specificity = number of non-# bits in condition
- c = 0.005 (specificity penalty)
- Variance updated exponentially with smoothing parameter θ

## Key Insight
- Slow GA invocation -> rational equilibrium (agents converge to similar forecasts)
- Fast GA invocation -> complex dynamics (diverse strategies coexist)
- The learning rate is the critical parameter controlling market behavior
