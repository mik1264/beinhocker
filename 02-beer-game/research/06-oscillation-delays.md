# Supply Chain Oscillation, Time Delays, and Feedback Loops

## Fundamental Mechanism
- The basic mechanism around inventory is a **delayed negative feedback loop**
- Oscillations require delays — negative feedback systems without delays will not oscillate
- The delay in response causes systems to **overshoot their target** and oscillate around the goal

## Four Behavior Patterns (with increasing delay)
1. **Smooth convergence**: Low delay, system settles to equilibrium quickly
2. **Fluctuant convergence**: Moderate delay, damped oscillations
3. **Sustained oscillation**: Critical delay, constant-amplitude cycles
4. **Divergent fluctuation**: Excessive delay, growing oscillations (instability)

## Time Delay Sources
- **Information delay**: Time for order information to propagate upstream
- **Decision delay**: Time for managers to process information and decide
- **Production lead time**: Time to manufacture/acquire goods
- **Transportation delay**: Physical shipping time
- **Order processing delay**: Administrative time to process orders

## Direct Correlation
- Lead time length directly correlates with the **magnitude of demand amplification**
- As time delay extends, participants place **larger, less frequent orders** to compensate
- This creates a positive feedback loop that exacerbates the bullwhip effect

## Beer Game Specific Delays
| Delay | Duration | Effect |
|-------|----------|--------|
| Order mailing | 1 week | Information propagation upstream |
| Shipping | 2 weeks | Physical delivery downstream |
| Production | 2 weeks | Factory manufacturing time |

## System Dynamics Perspective
- Each participant's decision influences others, creating **coupled feedback loops**
- The interaction of individual heuristic decisions with system delays produces **emergent oscillation**
- Oscillation period in Beer Game: ~20 weeks (4-5x the total pipeline delay)

## Sources
- [The Systems Thinker - Balancing Loops with Delays](https://thesystemsthinker.com/balancing-loops-with-delays/)
- [Springer - Inventory Dynamics Models with Delays](https://link.springer.com/chapter/10.1007/978-3-642-02897-7_29)
