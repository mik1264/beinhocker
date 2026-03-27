#!/usr/bin/env python3
"""
CLI for the SFI Artificial Stock Market simulation.

Usage:
    python cli.py --learning --agents 25 --ticks 2000
    python cli.py --rational --agents 25 --ticks 2000
    python cli.py --learning --agents 100 --ticks 5000 --output results.csv
"""

import argparse
import csv
import sys
from simulation import Simulation


def parse_args():
    parser = argparse.ArgumentParser(
        description='SFI Artificial Stock Market Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --learning --agents 25 --ticks 2000
  %(prog)s --rational --agents 25 --ticks 2000
  %(prog)s --learning --ticks 5000 --output results.csv
  %(prog)s --learning --mutation-rate 0.05 --ga-interval 100
        """
    )

    # Mode
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--learning', action='store_true',
                      help='Full model with 100 rules per agent and GA evolution')
    mode.add_argument('--rational', action='store_true',
                      help='Single rule per agent, no evolution (rational expectations)')

    # Parameters
    parser.add_argument('--agents', type=int, default=25,
                        help='Number of trading agents (default: 25)')
    parser.add_argument('--ticks', type=int, default=2000,
                        help='Number of simulation time steps (default: 2000)')
    parser.add_argument('--rules-per-agent', type=int, default=100,
                        help='Number of forecasting rules per agent in learning mode (default: 100)')
    parser.add_argument('--mutation-rate', type=float, default=0.03,
                        help='GA mutation rate per bit (default: 0.03)')
    parser.add_argument('--crossover-prob', type=float, default=0.3,
                        help='GA crossover probability (default: 0.3)')
    parser.add_argument('--ga-interval', type=float, default=250.0,
                        help='Mean ticks between GA invocations per agent (default: 250)')
    parser.add_argument('--risk-aversion', type=float, default=0.5,
                        help='Agent risk aversion parameter lambda (default: 0.5)')
    parser.add_argument('--interest-rate', type=float, default=0.10,
                        help='Risk-free interest rate (default: 0.10)')
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

    learning = args.learning
    num_rules = args.rules_per_agent if learning else 1

    if not args.quiet:
        print_header("SFI Artificial Stock Market")
        print(f"  Mode: {'Learning (GA evolution)' if learning else 'Rational (no evolution)'}")
        print(f"  Agents: {args.agents}")
        print(f"  Ticks: {args.ticks}")
        if learning:
            print(f"  Rules per agent: {num_rules}")
            print(f"  Mutation rate: {args.mutation_rate}")
            print(f"  Crossover prob: {args.crossover_prob}")
            print(f"  GA interval: {args.ga_interval}")
        print(f"  Risk aversion: {args.risk_aversion}")
        print(f"  Interest rate: {args.interest_rate}")
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

    sim = Simulation(
        num_agents=args.agents,
        num_ticks=args.ticks,
        learning=learning,
        num_rules=num_rules,
        mutation_rate=args.mutation_rate,
        crossover_prob=args.crossover_prob,
        ga_interval=args.ga_interval,
        risk_aversion=args.risk_aversion,
        interest_rate=args.interest_rate,
        seed=args.seed,
    )

    sim.run(progress_callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    stats = sim.get_statistics()

    if not args.quiet:
        print_header("Price Statistics")
        print(format_stat("Final price", stats['final_price']))
        print(format_stat("Mean price", stats['mean_price']))
        print(format_stat("Std price", stats['std_price']))
        print(format_stat("Fundamental value", stats['final_fundamental_value']))

        print_header("Return Statistics")
        print(format_stat("Mean return", stats['mean_return'], '.6f'))
        print(format_stat("Std return (volatility)", stats['std_return'], '.6f'))
        print(format_stat("Annualized volatility", stats['annualized_volatility']))
        print(format_stat("Excess kurtosis", stats['kurtosis']))
        print(format_stat("Skewness", stats['skewness']))

        print_header("Market Microstructure")
        print(format_stat("Return autocorrelation (lag-1)", stats['return_autocorrelation_lag1']))
        print(format_stat("Volatility clustering (|r| AC1)", stats['volatility_clustering_ac1']))
        print(format_stat("Tail index (Hill est.)", stats['tail_index']))
        print(format_stat("Mean volume", stats['mean_volume']))

        print_header("Wealth Distribution")
        print(format_stat("Gini coefficient", stats['gini_coefficient']))
        print(format_stat("Mean wealth", stats['mean_wealth']))
        print(format_stat("Std wealth", stats['std_wealth']))
        print(format_stat("Min wealth", stats['min_wealth']))
        print(format_stat("Max wealth", stats['max_wealth']))

        # Interpret results
        print_header("Interpretation")
        if stats['kurtosis'] > 1.0:
            print("  [*] Fat tails detected (excess kurtosis > 1)")
        else:
            print("  [ ] Returns near-Gaussian (no significant fat tails)")

        if abs(stats['volatility_clustering_ac1']) > 0.1:
            print("  [*] Volatility clustering present (|returns| autocorrelation)")
        else:
            print("  [ ] No significant volatility clustering")

        if abs(stats['return_autocorrelation_lag1']) < 0.1:
            print("  [*] Returns approximately uncorrelated (weak-form efficiency)")
        else:
            print("  [ ] Significant return autocorrelation detected")

        if stats['gini_coefficient'] > 0.3:
            print("  [*] Significant wealth inequality (Gini > 0.3)")
        else:
            print("  [ ] Moderate wealth equality (Gini <= 0.3)")

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
