#!/usr/bin/env python3
"""
CLI for the Schelling Segregation Model simulation.

Usage:
    python3 cli.py --ticks 100 --seed 42
    python3 cli.py --ticks 200 --threshold 0.5 --seed 42
    python3 cli.py --grid-size 30 --density 0.8 --threshold 0.3 --seed 42
"""

import argparse
import csv
import sys
from simulation import Simulation, SchellingConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description='Schelling Segregation Model (1971)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 100 --seed 42
  %(prog)s --ticks 200 --threshold 0.5 --seed 42
  %(prog)s --grid-size 30 --density 0.8 --threshold 0.3
  %(prog)s --ticks 100 --density 0.5 --seed 42
  %(prog)s --ticks 100 --threshold 0.75 --seed 42
        """
    )

    # Grid parameters
    parser.add_argument('--grid-size', type=int, default=50,
                        help='Grid dimension (NxN) (default: 50)')
    parser.add_argument('--ticks', type=int, default=200,
                        help='Maximum number of simulation time steps (default: 200)')

    # Agent / population parameters
    parser.add_argument('--density', type=float, default=0.7,
                        help='Fraction of cells occupied (default: 0.7)')
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='Tolerance threshold: min fraction of same-type neighbors (default: 0.3)')
    parser.add_argument('--ratio', type=float, default=0.5,
                        help='Fraction of agents that are type A (default: 0.5)')

    # Topology
    parser.add_argument('--bounded', action='store_true',
                        help='Use bounded edges instead of torus wrap-around')

    # Output
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path for time series data')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress progress output')

    return parser.parse_args()


def print_separator(char='=', width=64):
    print(char * width)


def print_header(title, width=64):
    print_separator()
    print(f" {title}")
    print_separator()


def format_stat(label, value, fmt='.4f'):
    if isinstance(value, float):
        return f"  {label:.<44s} {value:>12{fmt}}"
    if isinstance(value, bool):
        return f"  {label:.<44s} {'Yes' if value else 'No':>12s}"
    if value is None:
        return f"  {label:.<44s} {'N/A':>12s}"
    return f"  {label:.<44s} {str(value):>12s}"


def main():
    args = parse_args()

    config = SchellingConfig(
        grid_size=args.grid_size,
        density=args.density,
        threshold=args.threshold,
        ratio=args.ratio,
        max_ticks=args.ticks,
        bounded=args.bounded,
        seed=args.seed,
    )

    if not args.quiet:
        print_header("Schelling Segregation Model")
        print(f"  Grid: {config.grid_size}x{config.grid_size} ({'bounded' if config.bounded else 'torus'})")
        print(f"  Density: {config.density:.0%} occupied")
        print(f"  Threshold: {config.threshold:.0%} same-type neighbors")
        print(f"  Type ratio: {config.ratio:.0%} A / {1-config.ratio:.0%} B")
        print(f"  Max ticks: {config.max_ticks}")
        if args.seed is not None:
            print(f"  Seed: {args.seed}")
        print_separator('-')
        print("  Running simulation...")

    def progress(t, n):
        if not args.quiet:
            pct = t / n * 100
            bar_len = 30
            filled = int(bar_len * t / n)
            bar = '#' * filled + '-' * (bar_len - filled)
            print(f"\r  [{bar}] {pct:5.1f}% (tick {t}/{n})", end='', flush=True)

    sim = Simulation(config=config)
    sim.run(progress_callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    stats = sim.get_statistics()

    if not args.quiet:
        print_header("Population")
        print(format_stat("Total agents", str(stats['total_agents'])))
        print(format_stat("Type A count", str(stats['type_a_count'])))
        print(format_stat("Type B count", str(stats['type_b_count'])))
        print(format_stat("Empty cells", str(stats['empty_cells'])))

        print_header("Segregation Metrics")
        print(format_stat("Initial segregation index", stats['initial_segregation_index']))
        print(format_stat("Final segregation index", stats['final_segregation_index']))
        print(format_stat("Segregation change", stats['segregation_change']))
        print(format_stat("Interface density (boundary frac)", stats['interface_density']))
        print(format_stat("Largest cluster size", str(stats['largest_cluster'])))

        print_header("Dynamics")
        print(format_stat("Ticks simulated", str(stats['num_ticks'])))
        print(format_stat("Final happiness rate", stats['final_happiness_rate']))
        print(format_stat("Total moves", str(stats['total_moves'])))
        print(format_stat("Peak moves per tick", str(stats['peak_moves_per_tick'])))
        conv = stats['converged_at_tick']
        print(format_stat("Converged at tick", str(conv) if conv is not None else None))

        # Interpretation
        print_header("Interpretation")
        seg = stats['final_segregation_index']
        init_seg = stats['initial_segregation_index']
        threshold = config.threshold

        if seg > 0.85:
            print("  [*] EXTREME segregation -- neighborhoods almost entirely homogeneous")
        elif seg > 0.70:
            print("  [*] HIGH segregation -- clear spatial clustering")
        elif seg > 0.55:
            print("  [*] MODERATE segregation -- some clustering visible")
        else:
            print("  [ ] LOW segregation -- population remains relatively mixed")

        amplification = (seg - init_seg) / init_seg * 100 if init_seg > 0 else 0
        print(f"  [*] Segregation amplified {amplification:.0f}% from initial random placement")

        if threshold <= 0.33:
            print(f"  [*] KEY INSIGHT: Even mild preference ({threshold:.0%}) produces {seg:.0%} segregation")
            print(f"      This is Schelling's central paradox: micro-tolerance -> macro-segregation")
        elif threshold >= 0.5:
            print(f"  [*] With {threshold:.0%} threshold, strong segregation is expected")

        if stats['final_happiness_rate'] >= 1.0:
            print(f"  [*] System reached equilibrium: all agents satisfied")
        else:
            print(f"  [*] System did NOT fully converge: {stats['final_happiness_rate']:.1%} happy")
            print(f"      (may need more ticks or fewer agents relative to empty cells)")

        print_separator()

    # Save CSV if requested
    if args.output:
        ts_data = sim.get_timeseries_data()
        min_len = min(len(v) for v in ts_data.values())
        with open(args.output, 'w', newline='') as f:
            writer = csv.writer(f)
            headers = list(ts_data.keys())
            writer.writerow(headers)
            for i in range(min_len):
                row = [ts_data[h][i] for h in headers]
                writer.writerow(row)
        if not args.quiet:
            print(f"\n  Time series data saved to: {args.output}")


if __name__ == '__main__':
    main()
