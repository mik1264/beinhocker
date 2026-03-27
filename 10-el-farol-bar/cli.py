#!/usr/bin/env python3
"""
CLI for the El Farol Bar Problem simulation.

Usage:
    python3 cli.py --ticks 200 --seed 42
    python3 cli.py --agents 50 --ticks 200 --seed 42
    python3 cli.py --ticks 200 --threshold 30 --num-strategies 20 --seed 42
"""

import argparse
import csv
import sys
from simulation import Simulation, Config


def parse_args():
    parser = argparse.ArgumentParser(
        description='El Farol Bar Problem Simulation (Arthur 1994)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 200 --seed 42
  %(prog)s --agents 50 --ticks 200 --seed 42
  %(prog)s --ticks 200 --threshold 30 --seed 42
  %(prog)s --ticks 200 --num-strategies 20 --seed 42
        """
    )

    parser.add_argument('--agents', type=int, default=100,
                        help='Number of agents (default: 100)')
    parser.add_argument('--ticks', type=int, default=200,
                        help='Number of simulation weeks (default: 200)')
    parser.add_argument('--threshold', type=int, default=60,
                        help='Comfort threshold for bar attendance (default: 60)')
    parser.add_argument('--num-strategies', type=int, default=10,
                        help='Number of strategies per agent (default: 10)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path for time series data')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress progress output')

    return parser.parse_args()


def print_separator(char='=', width=60):
    print(char * width)


def print_header(title, width=60):
    print_separator()
    print(f" {title}")
    print_separator()


def format_stat(label, value, fmt='.4f'):
    if isinstance(value, float):
        if abs(value) > 1e6:
            return f"  {label:.<40s} {value:>12,.0f}"
        return f"  {label:.<40s} {value:>12{fmt}}"
    return f"  {label:.<40s} {str(value):>12s}"


def main():
    args = parse_args()

    config = Config(
        num_agents=args.agents,
        num_ticks=args.ticks,
        threshold=args.threshold,
        num_strategies=args.num_strategies,
        seed=args.seed,
    )

    if not args.quiet:
        print_header("El Farol Bar Problem (Arthur 1994)")
        print(f"  Agents: {config.num_agents}")
        print(f"  Ticks: {config.num_ticks}")
        print(f"  Threshold: {config.threshold}")
        print(f"  Strategies per agent: {config.num_strategies}")
        if config.seed is not None:
            print(f"  Seed: {config.seed}")
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
        print_header("Attendance Statistics")
        print(format_stat("Mean attendance", stats['mean_attendance'], '.2f'))
        print(format_stat("Std attendance", stats['std_attendance'], '.2f'))
        print(format_stat("Min attendance", float(stats['min_attendance']), '.0f'))
        print(format_stat("Max attendance", float(stats['max_attendance']), '.0f'))
        print(format_stat("Median attendance", stats['median_attendance'], '.1f'))
        print(format_stat("Coeff. of variation", stats['coeff_variation']))

        print_header("Threshold Analysis")
        print(format_stat("Threshold", float(stats['threshold']), '.0f'))
        print(format_stat("Weeks above threshold", float(stats['weeks_above_threshold']), '.0f'))
        print(format_stat("Weeks at or below", float(stats['weeks_at_or_below']), '.0f'))
        print(format_stat("% above threshold", stats['pct_above_threshold'], '.1f'))

        print_header("Oscillation Analysis")
        print(format_stat("Threshold crossings", float(stats['threshold_crossings']), '.0f'))
        print(format_stat("Crossing rate", stats['crossing_rate']))
        print(format_stat("Mean run length", stats['mean_run_length'], '.2f'))
        print(format_stat("Autocorrelation (lag-1)", stats['autocorrelation_lag1']))

        print_header("Strategy & Accuracy")
        print(format_stat("Mean accuracy", stats['mean_accuracy']))
        print()
        print("  Strategy distribution (final tick):")
        usage = stats['final_strategy_usage']
        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_usage:
            bar = '#' * count
            print(f"    {name:<20s} {count:3d} {bar}")

        # Interpretation
        print_header("Interpretation")
        att = stats['mean_attendance']
        thresh = stats['threshold']

        if abs(att - thresh) < thresh * 0.1:
            print(f"  [*] Mean attendance ({att:.1f}) near threshold ({thresh})")
            print("      System self-organizes around comfort level")
        else:
            print(f"  [ ] Mean attendance ({att:.1f}) deviates from threshold ({thresh})")

        if stats['crossing_rate'] > 0.3:
            print(f"  [*] High oscillation (crossing rate {stats['crossing_rate']:.3f})")
            print("      Attendance fluctuates rapidly around threshold")
        elif stats['crossing_rate'] > 0.1:
            print(f"  [*] Moderate oscillation (crossing rate {stats['crossing_rate']:.3f})")
        else:
            print(f"  [ ] Low oscillation (crossing rate {stats['crossing_rate']:.3f})")

        if abs(stats['autocorrelation_lag1']) > 0.3:
            print(f"  [*] Strong autocorrelation ({stats['autocorrelation_lag1']:.3f})")
            print("      Attendance is predictable -- strategies may be herding")
        elif stats['autocorrelation_lag1'] < -0.3:
            print(f"  [*] Strong negative autocorrelation ({stats['autocorrelation_lag1']:.3f})")
            print("      Classic oscillation: high weeks followed by low weeks")
        else:
            print(f"  [*] Weak autocorrelation ({stats['autocorrelation_lag1']:.3f})")
            print("      Attendance is difficult to predict -- as Arthur predicted")

        if stats['mean_accuracy'] < 0.6:
            print(f"  [*] Low mean accuracy ({stats['mean_accuracy']:.3f})")
            print("      No strategy dominates -- the self-referential paradox in action")
        else:
            print(f"  [ ] Moderate accuracy ({stats['mean_accuracy']:.3f})")

        print_separator()

    # Save CSV if requested
    if args.output:
        ts_data = sim.get_timeseries_data()
        n = len(ts_data['tick'])
        with open(args.output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['tick', 'attendance', 'threshold', 'accuracy'])
            for i in range(n):
                writer.writerow([
                    ts_data['tick'][i],
                    ts_data['attendance'][i],
                    ts_data['threshold'][i],
                    f"{ts_data['accuracy'][i]:.4f}",
                ])
        if not args.quiet:
            print(f"\n  Time series data saved to: {args.output}")


if __name__ == '__main__':
    main()
