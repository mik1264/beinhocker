# Business Plan Evolution Experiments

Based on Beinhocker Ch.14: Business Plans as evolutionary units of the economy.

## Experiment 1: Baseline
```bash
python3 cli.py --ticks 300 --seed 42
```
Default parameters. Establishes the reference behavior of BP evolution with moderate mutation, gradual preference shifts, and 50 business plans.

## Experiment 2: Stable Preferences
```bash
python3 cli.py --ticks 300 --preference-shift-rate 0.0 --seed 42
```
Market preferences never change. BPs can fully optimize for a fixed demand landscape. Tests whether evolutionary pressure alone (without environmental change) drives convergence.

## Experiment 3: Rapidly Shifting Preferences
```bash
python3 cli.py --ticks 300 --preference-shift-rate 0.1 --seed 42
```
Market shifts 5x faster than baseline. Tests the Red Queen hypothesis: BPs must constantly adapt just to maintain fitness. Strategy component should be under heaviest pressure.

## Experiment 4: Low Innovation
```bash
python3 cli.py --ticks 300 --mutation-rate 0.01 --seed 42
```
Very low mutation rate. Tests whether the economy stagnates when business plans barely mutate. Expect slower fitness improvement and less creative destruction.

## Experiment 5: High Innovation
```bash
python3 cli.py --ticks 300 --mutation-rate 0.15 --seed 42
```
High mutation rate. Tests whether too much innovation is destabilizing -- constant disruption may prevent optimization. Could show exploration-exploitation tradeoff.

## Experiment 6: Large Economy
```bash
python3 cli.py --ticks 300 --population 200 --seed 42
```
4x larger population. Tests whether more competing BPs leads to faster evolution, more creative destruction, and different market structure (potentially higher Gini).
