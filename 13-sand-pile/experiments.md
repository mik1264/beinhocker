# Sand Pile / Self-Organized Criticality -- Experiments

Based on Bak, Tang & Wiesenfeld (1987) and Beinhocker, *The Origin of Wealth*, Ch 8, p.178.

## Model

The Abelian sandpile model on a 2D grid:
- Each cell holds an integer number of sand grains
- One grain is dropped on a random cell each tick
- If any cell reaches the critical threshold (default 4), it topples: loses 4 grains, each of its 4 neighbors gains 1
- Grains falling off the grid edge are lost forever
- Toppling cascades: neighbors may also exceed the threshold
- The system self-organizes to a critical state where avalanche sizes follow a power law

## Experiments

### 1. Baseline (50x50, threshold 4, 10k ticks)
```
python3 cli.py --ticks 10000 --seed 42
```
Standard BTW sandpile. Expect the system to reach criticality within a few thousand ticks, with avalanche sizes distributed as a power law.

### 2. Small Grid (25x25, threshold 4, 10k ticks)
```
python3 cli.py --ticks 10000 --grid-size 25 --seed 42
```
Smaller grid means more boundary effects -- grains fall off edges more often. Expect criticality to arrive faster but with a noisier power-law distribution.

### 3. Large Grid (100x100, threshold 4, 10k ticks)
```
python3 cli.py --ticks 10000 --grid-size 100 --seed 42
```
Larger grid allows larger avalanches and cleaner power-law behavior, but takes longer to reach criticality.

### 4. Long Run (50x50, threshold 4, 50k ticks)
```
python3 cli.py --ticks 50000 --seed 42
```
Extended run for better statistics. With 50,000 grain drops, the power-law fit should be more convincing.

### 5. High Threshold (50x50, threshold 8, 10k ticks)
```
python3 cli.py --ticks 10000 --threshold 8 --seed 42
```
Higher threshold means each cell accumulates more grains before toppling. Avalanches should be rarer but potentially larger.

### 6. Low Threshold (50x50, threshold 2, 10k ticks)
```
python3 cli.py --ticks 10000 --threshold 2 --seed 42
```
Lower threshold means more frequent topplings. The system reaches criticality faster, with more frequent but generally smaller avalanches.

## Key Questions

1. Does the avalanche size distribution follow a power law? What is the exponent?
2. How does grid size affect the distribution?
3. How does the threshold affect the time to reach criticality and the distribution?
4. Does the system truly self-organize -- does it reach criticality without any parameter tuning?
5. What does the height distribution look like at criticality?
