# Technology Evolution Simulation: Experiment Findings

## Model Overview

This simulation implements Kauffman's NK fitness landscape model as described in Beinhocker's *The Origin of Wealth*. Firms search a 12-dimensional binary technology space (N=12) with tunable epistatic interdependencies (K), using four strategies: random search, local hill-climbing, long-jump adaptation, and recombination. The system features creative destruction (exit of unfit firms) and new entrant dynamics.

All experiments: 200 ticks, seed=42, 30 initial firms.

---

## Experiment Results Summary

| Experiment | K | Mut. Rate | Strategy Mix | Global Best | Final Mean | Final Firms | Diversity | Innovations | Destructions |
|---|---|---|---|---|---|---|---|---|---|
| 1. Baseline | 4 | 0.05 | mixed | 0.7999 | 0.784 | 15 | 0.222 | 165 | 31 |
| 2. Smooth (K=1) | 1 | 0.05 | mixed | 0.6562 | 0.639 | 17 | 0.222 | 152 | 17 |
| 3. Rugged (K=8) | 8 | 0.05 | mixed | 0.7671 | 0.727 | 15 | 0.483 | 182 | 40 |
| 4. High Mutation | 4 | 0.15 | mixed | 0.7999 | 0.783 | 15 | 0.222 | 145 | 32 |
| 5. All Local | 4 | 0.05 | 100% local | 0.7999 | 0.769 | 16 | 0.351 | 137 | 24 |
| 6. All Long Jump | 4 | 0.05 | 100% long_jump | 0.7999 | 0.764 | 16 | 0.294 | 163 | 23 |

---

## Experiment 1: Baseline (K=4, default strategy mix)

**Configuration:** N=12, K=4, ruggedness=0.36, mixed strategies (15% random, 40% local, 25% long-jump, 20% recombination).

**Fitness trajectory:** Best fitness reached 0.800 by tick 1 and never improved -- the initial population already contained a near-optimal technology. Mean fitness climbed from 0.571 to ~0.784 over 200 ticks, with the steepest gains in the first 50 ticks (0.571 to 0.755) followed by slow refinement.

**Strategy performance:** Local climbers dominated the final population (8 of 15 firms), followed by recombination (6). Long-jump firms were entirely eliminated (0 remaining). This confirms that on a moderately rugged landscape, incremental improvement outperforms radical exploration once good solutions are found.

**Creative destruction:** 31 firm exits over 200 ticks (0.155/tick) -- classified as a turbulent market. Most exits occurred in the first 60 ticks as the population culled low-fitness firms. The population contracted from 30 to ~15 firms and stabilized.

**Convergence:** Low diversity (0.222) by tick 200 -- nearly all firms converged to similar technology configurations near the global peak. 14 of 15 firms were in the "mature" S-curve phase.

---

## Experiment 2: Smooth Landscape (K=1)

**Configuration:** Ruggedness=0.09 (near Mt. Fuji landscape with a single broad peak).

**Key observation -- lower absolute fitness:** The global best was only 0.656, substantially lower than the baseline's 0.800. This is a property of how NK landscapes work: with K=1, each locus's fitness contribution depends on only one other locus. The fitness function becomes nearly additive, reducing the variance of the landscape. The single peak exists but sits at a lower absolute height because the random fitness tables generate less extreme values when averaged over near-independent contributions.

**Hill-climbing dominance confirmed:** The smooth landscape converged quickly (best=0.656 by tick 2, never improved). Mean fitness plateaued around 0.648 by tick 50. The path to the optimum was straightforward -- firms climbed monotonically with no traps.

**Lower creative destruction:** Only 17 exits (0.085/tick), roughly half the baseline rate. On a smooth landscape, even poor initial positions can hill-climb to decent fitness, reducing the gap between leaders and laggards. Only 4 new entrants over 200 ticks.

**Stagnation after convergence:** From tick ~50 onward, the simulation was essentially static. The mean fitness line flatlined at 0.648-0.652. Innovation rate was 0.76/tick, slightly below baseline (0.825/tick), reflecting that most firms had already reached their local (= global) optimum and had nowhere to go.

---

## Experiment 3: Rugged Landscape (K=8)

**Configuration:** Ruggedness=0.73. Many local optima, deep valleys between peaks.

**Key finding -- highest innovation AND highest destruction:** 182 innovations (0.91/tick) and 40 destructions (0.20/tick), both the highest of any experiment. The rugged landscape creates a turbulent competitive environment: firms frequently find improvements (jumping between local peaks) but also frequently fall behind when others discover better peaks.

**Diversity remained high:** Tech diversity was 0.483, more than double the baseline's 0.222. Firms occupied genuinely different regions of the landscape, trapped on different local optima. Three firms were still in the "growth" phase at tick 200 (vs. 1 in baseline), indicating ongoing exploration.

**Mean fitness oscillation:** The mean fitness showed notable volatility, oscillating between 0.687 and 0.735 in the second half. This reflects the creative destruction cycle: a firm discovers a better peak, pulling the mean up, then weaker firms are culled, new entrants arrive with lower fitness, pulling the mean back down.

**Long-jump advantage on rugged landscapes:** Despite the same initial strategy mix as the baseline, 2 long-jump firms survived (vs. 0 in the baseline). On rugged landscapes, the ability to jump across fitness valleys to reach distant peaks provides a competitive advantage that does not exist on smoother landscapes.

**More new entrants:** 25 entries (vs. 16 in baseline), reflecting higher turnover. The market was in constant flux.

---

## Experiment 4: High Mutation (rate=0.15, 3x baseline)

**Configuration:** Same as baseline but mutation rate tripled from 0.05 to 0.15.

**Surprisingly similar to baseline:** Global best=0.7999, final mean=0.783, diversity=0.222. The same landscape (same seed) was used, so the fitness surface was identical. Higher mutation did not help firms find better peaks.

**Fewer innovations despite more exploration:** Only 145 innovations (0.725/tick) vs. 165 (0.825/tick) in baseline. High mutation rate acts as noise on the search process: local climbers try a 1-bit neighbor but then have ~1.8 additional random flips applied (15% per bit x 12 bits), corrupting the directed search. This makes every strategy noisier and less efficient.

**Faster early convergence, then similar plateau:** Mean fitness reached 0.775 by tick 50 (vs. 0.755 in baseline at tick 50). The extra mutation helped escape early local optima faster but did not yield superior long-run performance. The noisy mutations occasionally produce lucky jumps but more often destroy good configurations.

**Creative destruction comparable:** 32 exits, essentially identical to baseline (31). The high mutation rate did not materially change market dynamics.

---

## Experiment 5: All Local Climbers (100% local hill-climbing)

**Configuration:** Entire population uses greedy 1-bit hill-climbing. No random, long-jump, or recombination.

**Fast initial convergence:** Mean fitness jumped from 0.607 to 0.735 by tick 20 -- the fastest early gains of any experiment. Local search is maximally efficient when improvements are nearby, and it found them quickly.

**Stagnation and trapped firms:** After tick ~50, the mean fitness plateaued around 0.750-0.755, noticeably below the baseline's 0.784. Without long-jump or recombination strategies, firms that reached a local optimum had no mechanism to escape. Each firm sat at the top of its local hill with no upward-pointing 1-bit moves available.

**Higher diversity than expected:** Diversity was 0.351 (vs. 0.222 baseline). This is the signature of local optima trapping: different firms converged to different local peaks and stayed there permanently. In the baseline, long-jump and recombination strategies helped firms escape traps and converge toward the global optimum. Without those mechanisms, the population fractured into isolated clusters.

**Fewest innovations:** Only 137 total innovations (0.685/tick), the lowest of all experiments. Once firms reach their local peaks, innovation stops entirely. The system reached a "frozen" state faster than any other configuration.

**Lowest creative destruction:** Only 24 exits, because firms stuck on different local peaks all had similar (decent but not great) fitness, reducing the fitness gap that drives creative destruction.

---

## Experiment 6: All Long Jumpers (100% long-jump)

**Configuration:** All firms use 3-bit long-jump search. No local, random, or recombination.

**Slower convergence, more sustained exploration:** Mean fitness climbed more gradually than any other experiment: 0.549 at tick 1, 0.730 at tick 50, 0.764 at tick 200. Long-jump search is inherently noisier -- flipping 3 of 12 bits at once means each candidate is far from the current position, making it unlikely to find an improvement.

**More firms survived longer:** 22 firms remained at tick 100 (vs. 15-16 in baseline), and the population held 16 at the end. The slower convergence meant less fitness dispersion early on, so fewer firms were culled.

**More innovations than local climbers:** 163 innovations (0.815/tick) vs. 137 for all-local. Long-jump firms kept finding improvements throughout the run, even late in the simulation. Four firms were still in the "growth" phase at tick 200.

**Fitness volatility:** The mean fitness showed periodic drops (0.777 at tick 180, then 0.733 at tick 197, back to 0.764 at tick 200). Each long-jump attempt is essentially a gamble -- accepting a 3-bit perturbation only when it improves fitness, but the search itself introduces instability.

**Lower final mean fitness:** 0.764 vs. baseline's 0.784. Long-jump alone cannot perform the fine-grained 1-bit refinements needed to climb to the very top of a peak. It gets firms to the right neighborhood but cannot polish the solution.

---

## Cross-Experiment Emergent Behaviors

### 1. The Exploration-Exploitation Tradeoff is Real

The clearest pattern across all experiments: **local search exploits efficiently but stagnates; long-jump explores broadly but converges slowly.** The baseline mixed strategy (40% local, 25% long-jump, 20% recombination) outperformed both pure strategies on final mean fitness (0.784 vs. 0.769 vs. 0.764), confirming Beinhocker's argument that diverse search strategies in an economy produce better outcomes than any single approach.

### 2. Landscape Ruggedness Drives Market Turbulence

| Metric | K=1 (smooth) | K=4 (moderate) | K=8 (rugged) |
|---|---|---|---|
| Destructions | 17 | 31 | 40 |
| Innovations | 152 | 165 | 182 |
| Diversity | 0.222 | 0.222 | 0.483 |
| Destruction rate | 0.085 | 0.155 | 0.200 |

Rugged landscapes produce more creative destruction, more innovation, and more technological diversity. This maps to Beinhocker's claim that industries with complex, interdependent technologies (high K) experience more Schumpeterian disruption than industries with modular, independent technologies (low K).

### 3. The Population Self-Regulates to ~15 Firms

Every experiment, regardless of initial conditions or parameters, converged to a population of 14-18 firms. This emergent equilibrium arises from the tension between the exit threshold (firms below 15% of best fitness are at risk) and the entry rate (2% per tick). The system finds a natural carrying capacity.

### 4. Creative Destruction is Front-Loaded

In all experiments, the majority of firm exits occurred in the first 50-60 ticks, during the initial shakeout when fitness dispersion was highest. After the population converged, the destruction rate dropped sharply. This mirrors real industry life cycles: intense competition during the formative phase, consolidation, then relative stability.

### 5. Mutation is Not a Substitute for Strategy Diversity

Experiment 4 (high mutation) showed that adding noise to the search process does not replicate the benefits of having genuinely different search strategies. Tripling the mutation rate produced fewer innovations than the baseline, despite more raw exploration. Structured diversity (different strategies searching different ways) outperforms unstructured randomness.

### 6. Local Optima Trapping Creates "Frozen" Diversity

The all-local-climbers experiment (5) produced the counterintuitive result of higher diversity (0.351) than the mixed-strategy baseline (0.222). But this is "frozen" diversity -- firms trapped on different peaks unable to move, not productive diversity driven by ongoing exploration. This distinction matters: not all diversity is adaptive.

---

## Connections to Beinhocker's Framework

1. **Technology as combinatorial search** (Ch. 9): The NK model directly implements this idea. Technologies are combinations of binary choices, and firms search the resulting fitness landscape.

2. **Creative destruction** (Ch. 11): The simulation reproduces Schumpeter's gale -- inferior technologies are swept away by superior ones, with the intensity depending on landscape ruggedness (industry complexity).

3. **The value of strategy diversity** (Ch. 12): No single search strategy dominates. Economies (and the simulation) benefit from a portfolio of approaches -- some firms doing incremental improvement, others making radical leaps, others recombining existing technologies.

4. **Punctuated equilibrium**: The fitness trajectories show periods of stasis interrupted by bursts of improvement, especially visible in the rugged landscape (K=8) where mean fitness oscillates as firms discover new peaks and old ones become obsolete.
