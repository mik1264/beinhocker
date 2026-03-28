# Public Policy Experiments

Based on Beinhocker Ch.18: Policy in a Complex World. The core argument is that policy should enable evolutionary fitness rather than engineer specific outcomes. We test this by running the same economy under different policy regimes.

## Experiment 1: Baseline (Laissez-faire)
```bash
python3 cli.py --ticks 500 --seed 42
```
Default laissez-faire regime. Minimal regulation, low taxes, no subsidies, no market share limits. Establishes the reference evolutionary dynamics of the economy.

## Experiment 2: Laissez-faire (explicit)
```bash
python3 cli.py --ticks 500 --regime laissez-faire --seed 42
```
Identical to baseline. Confirms reproducibility with explicit regime flag.

## Experiment 3: Social Democrat
```bash
python3 cli.py --ticks 500 --regime social-democrat --seed 42
```
High taxes fund a strong safety net and innovation subsidies. Competition policy limits market concentration. Tests whether redistribution and regulation can coexist with healthy evolutionary dynamics.

## Experiment 4: Innovation State
```bash
python3 cli.py --ticks 500 --regime innovation-state --seed 42
```
Low regulation, high innovation subsidies, moderate competition policy. The state as venture capitalist -- subsidizing R&D to boost mutation rates. Tests whether directed innovation support accelerates fitness improvement.

## Experiment 5: Protectionist
```bash
python3 cli.py --ticks 500 --regime protectionist --seed 42
```
High regulation creates barriers to entry. Incumbents are shielded from competition. Tests Beinhocker's prediction that protecting incumbents stifles evolutionary dynamics and reduces long-run fitness.

## Experiment 6: Adaptive
```bash
python3 cli.py --ticks 500 --regime adaptive --seed 42
```
Policy adjusts dynamically based on economic indicators: regulation eases when growth slows, taxes rise when inequality increases, innovation subsidies increase when innovation stalls. Tests the complexity-economics prescription of adaptive governance.
