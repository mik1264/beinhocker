# Environmental Dynamics: Markov Switching and Punctuated Equilibrium

## Markov Switching Model

For the environment state transitions:
- Two states: A-favored and B-favored
- At each tick, probability p of switching to the other state
- Stability parameter controls average length of stable periods: avg_stable = 1/p
- For punctuated equilibrium: long stable runs (e.g., 50-200 ticks) then sudden switch

## Punctuated Equilibrium Mode

Implementation approach:
- Draw the duration of each stable period from a geometric distribution
- Mean duration controlled by stability parameter
- When the period expires, switch state
- This creates the long-stability / sudden-change pattern

## Random Mode

Alternative for comparison:
- At each tick, environment state is drawn with fixed probability
- No autocorrelation in environment state
- Creates a noisy environment where neither state dominates for long
- Flexible agents should excel in this mode

## Environmental Impact on Performance

When environment = A:
- Strategy A yields base score of 1.0
- Strategy B yields base score of 0.0 (or some penalty)

When environment = B:
- Strategy A yields 0.0
- Strategy B yields 1.0

## Connection to Agent Types

**Rigid agents**:
- Always play their fixed strategy (A or B)
- In matching environment: score = 1.0 + experience_weight * experience
- In non-matching: score = 0.0 + experience_weight * experience
- Experience grows each tick (rigids accumulate faster due to consistency)

**Flexible agents**:
- Observe environment and try to match
- Observation has noise: probability (1-noise) of correct observation
- Score = match_score + experience_weight * experience
- Experience grows slower (context-switching cost)

## Key Parameters

- stability: average ticks between environment switches (default 100)
- noise: flexible agent observation error rate (default 0.1)
- experience_weight: how much experience matters vs match (default 0.1)
