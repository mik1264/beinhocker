# Technology Evolution on NK Fitness Landscapes

## Theoretical Background

### NK Fitness Landscapes (Kauffman, 1993)

Stuart Kauffman introduced the NK model as a tunably rugged fitness landscape for studying
evolutionary search. The model has two parameters:

- **N**: the number of components (dimensions) in the design. Each component is binary (0 or 1),
  giving a total design space of 2^N possible configurations.
- **K**: the number of epistatic interactions per component. Each component's fitness contribution
  depends on its own state plus the states of K other components.

**Key properties:**
- When K=0, the landscape is smooth with a single global peak. Hill-climbing always finds the optimum.
- When K=N-1, the landscape is maximally rugged (random). Local peaks are everywhere.
- For intermediate K, the landscape has a rich structure of peaks and valleys.
- The "complexity catastrophe": as K increases, the expected fitness of local peaks *decreases*.
  More interdependencies make it harder to find good solutions.

### Technology as Design Search (Beinhocker, 2006)

Beinhocker frames economic evolution as a search process over design spaces:

1. **Technologies are recipes**: combinations of components, processes, materials, and ideas.
   Each "recipe" occupies a point on a vast fitness landscape.
2. **Markets are parallel search algorithms**: millions of firms simultaneously explore
   different regions of the design space.
3. **Creative destruction is the selection mechanism**: superior designs drive inferior ones
   to extinction, concentrating search effort around promising regions.
4. **Combinatorial innovation**: most innovations are not wholly new but recombinations of
   existing technologies, ideas, and components.

### Search Strategies

Different firms use different search strategies, each with strengths and weaknesses:

| Strategy | Description | Best When | Risk |
|----------|-------------|-----------|------|
| Random | Try completely random designs | K is very high (rugged landscape) | Low expected payoff |
| Local (hill-climbing) | Test all 1-bit neighbors, pick the best | K is low (smooth landscape) | Gets stuck on local peaks |
| Long-jump | Flip several bits at once | Stuck on mediocre peak | May land in valleys |
| Recombination | Combine modules from different designs | Modular landscape (moderate K) | Breaks good combinations |

### Creative Destruction (Schumpeter, 1942)

Joseph Schumpeter described capitalism as a process of "creative destruction" where:
- New innovations render old technologies obsolete
- Incumbents are displaced by entrepreneurs with better designs
- This process is inherently wasteful (many failures per success) but drives long-run growth
- The "gale of creative destruction" is the essential feature of capitalism

### S-Curve Dynamics

Technologies follow a characteristic lifecycle:
1. **Emerging**: initial development, low performance, few adopters
2. **Growth**: rapid improvement as the technology matures
3. **Maturity**: diminishing returns, approaching the technology's theoretical limits
4. **Decline**: a superior technology emerges and displaces the incumbent

---

## Experiment 1: Landscape Ruggedness and Optimal Strategy

**Question**: How does the ruggedness of the technology landscape (K) affect which search strategies succeed?

**Setup**:
```
python cli.py --n 16 --k 0 --firms 40 --ticks 1000 --seed 42 --output smooth.csv
python cli.py --n 16 --k 4 --firms 40 --ticks 1000 --seed 42 --output moderate.csv
python cli.py --n 16 --k 8 --firms 40 --ticks 1000 --seed 42 --output rugged.csv
python cli.py --n 16 --k 15 --firms 40 --ticks 1000 --seed 42 --output random.csv
```

**Predictions**:
- K=0: Hill-climbers dominate. Single global peak, so local search always wins.
- K=4: Mixed strategies. Hill-climbers do well but occasionally get stuck.
- K=8: Long-jumpers and recombiners gain advantage.
- K=15: Random search becomes competitive. No structure to exploit.

**Analysis**:
- Track final fitness by strategy type
- Compare diversity trajectories
- Measure time to reach 80% of maximum fitness

---

## Experiment 2: Strategy Diversity vs. Monoculture

**Question**: Does a diverse population of search strategies outperform a monoculture?

**Setup**:
```
# All local
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --local-frac 1.0 --random-frac 0 --longjump-frac 0 --recomb-frac 0 --seed 42 --output all_local.csv

# All long-jump
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --local-frac 0 --random-frac 0 --longjump-frac 1.0 --recomb-frac 0 --seed 42 --output all_longjump.csv

# Mixed (default)
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --seed 42 --output mixed.csv
```

**Predictions**:
- Mixed strategies should find higher peaks overall
- Local monoculture converges fastest but to a lower peak
- Long-jump monoculture has high variance

---

## Experiment 3: Creative Destruction Rate

**Question**: How does the intensity of creative destruction affect innovation?

**Setup**:
```
# Low destruction (high tolerance for poor performers)
python cli.py --n 12 --k 4 --firms 30 --ticks 1000 --exit-threshold 0.05 --seed 42 --output low_destruction.csv

# Medium destruction (default)
python cli.py --n 12 --k 4 --firms 30 --ticks 1000 --exit-threshold 0.15 --seed 42 --output med_destruction.csv

# High destruction (aggressive culling)
python cli.py --n 12 --k 4 --firms 30 --ticks 1000 --exit-threshold 0.30 --seed 42 --output high_destruction.csv
```

**Predictions**:
- Too little destruction: firms survive on local peaks, little pressure to innovate
- Optimal destruction: balance of exploration and exploitation
- Too much destruction: firms die before they can explore, diversity collapses

---

## Experiment 4: Mutation Rate and Innovation

**Question**: What mutation rate maximizes innovation?

**Setup**:
```
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --mutation-rate 0.01 --seed 42 --output low_mutation.csv
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --mutation-rate 0.05 --seed 42 --output med_mutation.csv
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --mutation-rate 0.15 --seed 42 --output high_mutation.csv
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --mutation-rate 0.30 --seed 42 --output very_high_mutation.csv
```

**Predictions**:
- Too low: search is too conservative, stuck on local peaks
- Optimal (around 0.05): enough perturbation to escape local peaks without destroying good solutions
- Too high: search becomes essentially random; no ability to accumulate improvements

---

## Experiment 5: Combinatorial Explosion

**Question**: How does the size of the design space (N) affect search difficulty?

**Setup**:
```
python cli.py --n 8  --k 3 --firms 30 --ticks 500 --seed 42 --output n8.csv
python cli.py --n 12 --k 4 --firms 30 --ticks 500 --seed 42 --output n12.csv
python cli.py --n 16 --k 6 --firms 30 --ticks 500 --seed 42 --output n16.csv
python cli.py --n 20 --k 8 --firms 30 --ticks 500 --seed 42 --output n20.csv
```

**Predictions**:
- N=8 (256 possible designs): easily searchable, high final fitness
- N=12 (4,096 designs): moderate difficulty
- N=16 (65,536 designs): significant challenge
- N=20 (1,048,576 designs): very difficult, many local peaks

**Key insight from Beinhocker**: the combinatorial explosion of design space is why
markets need to be *massively parallel* search algorithms. No central planner can
explore 10^18 possible designs; only millions of decentralized agents can.

---

## Key Metrics to Track

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| Best fitness | Highest technology found | Innovation frontier |
| Mean fitness | Average technology quality | Overall economic productivity |
| Technology diversity | Hamming distance between firms | Exploration breadth |
| Firm survival rate | Fraction surviving per epoch | Market stability |
| Innovation rate | Fitness improvements per tick | Rate of progress |
| S-curve transitions | Phase changes per epoch | Technology lifecycle dynamics |
| Strategy distribution | Firms per search strategy | Which approaches win |

---

## References

1. Kauffman, S. (1993). *The Origins of Order: Self-Organization and Selection in Evolution*. Oxford University Press.
2. Kauffman, S. & Levin, S. (1987). "Towards a general theory of adaptive walks on rugged landscapes." *Journal of Theoretical Biology*, 128(1), 11-45.
3. Beinhocker, E. (2006). *The Origin of Wealth: Evolution, Complexity, and the Radical Remaking of Economics*. Harvard Business Press.
4. Schumpeter, J. (1942). *Capitalism, Socialism and Democracy*. Harper & Brothers.
5. Fleming, L. & Sorenson, O. (2001). "Technology as a complex adaptive system: evidence from patent data." *Research Policy*, 30(7), 1019-1039.
6. Arthur, W.B. (2009). *The Nature of Technology: What It Is and How It Evolves*. Free Press.
7. Levinthal, D. (1997). "Adaptation on rugged landscapes." *Management Science*, 43(7), 934-950.
