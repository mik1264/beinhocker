#!/usr/bin/env python3
"""
CLI for the Strategy as Evolution simulation.

Usage:
    python3 cli.py --ticks 300 --seed 42
    python3 cli.py --ticks 300 --firms 30 --niches 5 --shift-rate 0.05
    python3 cli.py --ticks 300 --exploiter-frac 1.0 --explorer-frac 0.0 --seed 42
"""

import argparse
import json
import sys
from simulation import StrategySimulation, SimConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description='Strategy as Evolution: Portfolio-Based Competition (Beinhocker Ch.15)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 300 --seed 42
  %(prog)s --ticks 300 --shift-rate 0.0 --seed 42         # stable market
  %(prog)s --ticks 300 --shift-rate 0.2 --seed 42         # volatile market
  %(prog)s --ticks 300 --exploiter-frac 1.0 --explorer-frac 0.0 --seed 42
  %(prog)s --ticks 300 --firms 100 --niches 10 --seed 42  # larger economy
        """
    )

    parser.add_argument('--firms', type=int, default=30,
                        help='Number of firms (default: 30)')
    parser.add_argument('--ticks', type=int, default=300,
                        help='Number of simulation ticks (default: 300)')
    parser.add_argument('--niches', type=int, default=5,
                        help='Number of market niches (default: 5)')
    parser.add_argument('--shift-rate', type=float, default=0.05,
                        help='Probability each niche shifts per tick (default: 0.05)')
    parser.add_argument('--exploiter-frac', type=float, default=0.33,
                        help='Fraction of firms that are exploiters (default: 0.33)')
    parser.add_argument('--explorer-frac', type=float, default=0.33,
                        help='Fraction of firms that are explorers (default: 0.33)')
    parser.add_argument('--mutation-rate', type=float, default=0.1,
                        help='Base mutation rate for portfolio changes (default: 0.1)')
    parser.add_argument('--exit-threshold', type=float, default=0.15,
                        help='Bottom fraction of firms culled per tick (default: 0.15)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path')
    parser.add_argument('--json-output', type=str, default=None,
                        help='Output JSON file path')
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

    # Normalize fractions: if exploiter + explorer > 1, clamp
    exploiter_frac = max(0.0, min(1.0, args.exploiter_frac))
    explorer_frac = max(0.0, min(1.0, args.explorer_frac))
    if exploiter_frac + explorer_frac > 1.0:
        explorer_frac = 1.0 - exploiter_frac

    config = SimConfig(
        num_firms=args.firms,
        num_niches=args.niches,
        ticks=args.ticks,
        shift_rate=args.shift_rate,
        exploiter_frac=exploiter_frac,
        explorer_frac=explorer_frac,
        mutation_rate=args.mutation_rate,
        exit_threshold=args.exit_threshold,
        seed=args.seed,
    )

    adaptive_frac = 1.0 - exploiter_frac - explorer_frac

    if not args.quiet:
        print_header("Strategy as Evolution Simulation")
        print(f"  Firms: {config.num_firms}")
        print(f"  Niches: {config.num_niches}")
        print(f"  Ticks: {config.ticks}")
        print(f"  Shift rate: {config.shift_rate}")
        print(f"  Type mix: exploiter={exploiter_frac:.2f} explorer={explorer_frac:.2f} adaptive={adaptive_frac:.2f}")
        print(f"  Mutation rate: {config.mutation_rate}")
        print(f"  Exit threshold: {config.exit_threshold}")
        if config.seed is not None:
            print(f"  Seed: {config.seed}")
        print_separator('-')
        print("  Running simulation...")

    def progress(t, n, record):
        if not args.quiet:
            pct = t / n * 100
            bar_len = 30
            filled = int(bar_len * t / n)
            bar = '#' * filled + '-' * (bar_len - filled)
            mf = record.mean_fitness
            bf = record.best_fitness
            nf = record.total_firms
            print(f"\r  [{bar}] {pct:5.1f}% tick {t}/{n} | mean={mf:.3f} best={bf:.3f} firms={nf}",
                  end='', flush=True)

    sim = StrategySimulation(config)
    sim.run(callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    # Summary statistics
    summary = sim.get_summary()

    if not args.quiet:
        print_header("Final Composition")
        print(format_stat("Total firms", str(summary["final_firms"])))
        print(format_stat("Exploiters", str(summary["final_exploiters"])))
        print(format_stat("Explorers", str(summary["final_explorers"])))
        print(format_stat("Adaptive", str(summary["final_adaptive"])))

        print_header("Market Share by Type")
        print(format_stat("Exploiter share", summary["final_exploiter_share"]))
        print(format_stat("Explorer share", summary["final_explorer_share"]))
        print(format_stat("Adaptive share", summary["final_adaptive_share"]))

        print_header("Fitness")
        print(format_stat("Mean fitness (avg over run)", summary["mean_fitness_avg"]))
        print(format_stat("Mean fitness (final)", summary["mean_fitness_final"]))
        print(format_stat("Best fitness (final)", summary["best_fitness_final"]))
        print(format_stat("Exploiter avg fitness", summary["exploiter_avg_fitness"]))
        print(format_stat("Explorer avg fitness", summary["explorer_avg_fitness"]))
        print(format_stat("Adaptive avg fitness", summary["adaptive_avg_fitness"]))

        print_header("Market Structure")
        print(format_stat("HHI (concentration)", summary["hhi_final"]))
        print(format_stat("Portfolio diversity", summary["avg_portfolio_diversity"]))
        print(format_stat("Niche coverage", summary["niche_coverage"]))
        print(format_stat("Total niche shifts", str(summary["total_niche_shifts"])))
        print(format_stat("Total exits", str(summary["total_exits"])))
        print(format_stat("Total entries", str(summary["total_entries"])))

        # Interpretation
        print_header("Interpretation")

        # Which type dominates?
        shares = {
            "Exploiter": summary["final_exploiter_share"],
            "Explorer": summary["final_explorer_share"],
            "Adaptive": summary["final_adaptive_share"],
        }
        dominant = max(shares, key=shares.get)
        print(f"  [*] Dominant type: {dominant} ({shares[dominant]:.1%} market share)")

        if summary["hhi_final"] > 0.25:
            print("  [*] High market concentration -- few firms dominate")
        elif summary["hhi_final"] < 0.1:
            print("  [*] Low market concentration -- competitive market")
        else:
            print("  [*] Moderate market concentration")

        if summary["niche_coverage"] < 0.8:
            print("  [*] Some niches underserved -- market gaps exist")
        else:
            print("  [*] Full niche coverage -- all market segments served")

        shift_rate_effective = summary["total_niche_shifts"] / max(config.ticks, 1)
        print(format_stat("Effective shift rate (per tick)", shift_rate_effective))

        if config.shift_rate > 0.1:
            print("  [*] Volatile market: explorers and adaptive firms should have advantage")
        elif config.shift_rate == 0.0:
            print("  [*] Stable market: exploiters should dominate")
        else:
            print("  [*] Moderate volatility: mixed strategies viable")

        print_separator()

    # Save outputs
    if args.output:
        sim.to_csv(args.output)
        if not args.quiet:
            print(f"\n  CSV data saved to: {args.output}")

    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(sim.to_json(), f, indent=2)
        if not args.quiet:
            print(f"  JSON data saved to: {args.json_output}")


if __name__ == '__main__':
    main()
