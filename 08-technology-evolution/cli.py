#!/usr/bin/env python3
"""
CLI for the Technology Evolution / Innovation simulation.

Usage:
    python cli.py --ticks 500 --firms 30 --n 12 --k 4
    python cli.py --ticks 1000 --firms 50 --seed 42 --output results.csv
    python cli.py --ticks 500 --n 16 --k 6 --mutation-rate 0.08
"""

import argparse
import sys
from simulation import TechEvolutionSimulation, SimConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description='Technology Evolution / Innovation Simulation (NK Landscape)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 500 --firms 30 --n 12 --k 4
  %(prog)s --ticks 1000 --firms 50 --seed 42 --output results.csv
  %(prog)s --ticks 500 --n 16 --k 6 --mutation-rate 0.08
  %(prog)s --ticks 2000 --firms 100 --n 20 --k 8 --output long_run.csv
        """
    )

    # Landscape parameters
    parser.add_argument('--n', type=int, default=12,
                        help='Number of technology dimensions / bit-string length (default: 12)')
    parser.add_argument('--k', type=int, default=4,
                        help='Epistatic interdependencies per dimension, 0..N-1 (default: 4)')

    # Firm parameters
    parser.add_argument('--firms', type=int, default=30,
                        help='Number of firms (default: 30)')
    parser.add_argument('--ticks', type=int, default=500,
                        help='Number of simulation ticks (default: 500)')

    # Search parameters
    parser.add_argument('--mutation-rate', type=float, default=0.05,
                        help='Mutation rate per bit per search (default: 0.05)')
    parser.add_argument('--rd-budget', type=float, default=0.3,
                        help='R&D budget as fraction of fitness (default: 0.3)')
    parser.add_argument('--exploration-rate', type=float, default=0.3,
                        help='Exploration vs exploitation balance (default: 0.3)')
    parser.add_argument('--long-jump-distance', type=int, default=3,
                        help='Bits flipped in long-jump strategy (default: 3)')

    # Strategy mix
    parser.add_argument('--random-frac', type=float, default=0.15,
                        help='Fraction of firms using random search (default: 0.15)')
    parser.add_argument('--local-frac', type=float, default=0.40,
                        help='Fraction of firms using local hill-climbing (default: 0.40)')
    parser.add_argument('--longjump-frac', type=float, default=0.25,
                        help='Fraction of firms using long-jump adaptation (default: 0.25)')
    parser.add_argument('--recomb-frac', type=float, default=0.20,
                        help='Fraction of firms using recombination (default: 0.20)')

    # Creative destruction
    parser.add_argument('--entry-rate', type=float, default=0.02,
                        help='Probability of new firm entry per tick (default: 0.02)')
    parser.add_argument('--exit-threshold', type=float, default=0.15,
                        help='Relative fitness threshold for firm exit (default: 0.15)')

    # General
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path')
    parser.add_argument('--json-output', type=str, default=None,
                        help='Output JSON file path (full state + history)')
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

    # Normalize strategy mix
    total_frac = args.random_frac + args.local_frac + args.longjump_frac + args.recomb_frac
    strategy_mix = {
        "random": args.random_frac / total_frac,
        "local": args.local_frac / total_frac,
        "long_jump": args.longjump_frac / total_frac,
        "recombination": args.recomb_frac / total_frac,
    }

    config = SimConfig(
        n=args.n,
        k=args.k,
        num_firms=args.firms,
        ticks=args.ticks,
        mutation_rate=args.mutation_rate,
        rd_budget=args.rd_budget,
        exploration_rate=args.exploration_rate,
        entry_rate=args.entry_rate,
        exit_threshold=args.exit_threshold,
        long_jump_distance=args.long_jump_distance,
        strategy_mix=strategy_mix,
        seed=args.seed,
    )

    if not args.quiet:
        print_header("Technology Evolution Simulation")
        print(f"  NK Landscape: N={config.n}, K={config.k}")
        print(f"  Firms: {config.num_firms}")
        print(f"  Ticks: {config.ticks}")
        print(f"  Mutation rate: {config.mutation_rate}")
        print(f"  R&D budget: {config.rd_budget}")
        print(f"  Long-jump distance: {config.long_jump_distance}")
        print(f"  Strategy mix: {strategy_mix}")
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
            best = record.best_fitness
            mean = record.mean_fitness
            nf = record.num_firms
            print(f"\r  [{bar}] {pct:5.1f}% tick {t}/{n} | best={best:.3f} mean={mean:.3f} firms={nf}",
                  end='', flush=True)

    sim = TechEvolutionSimulation(config)
    sim.run(callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    # Summary statistics
    state = sim.get_state_json()
    stats = state["stats"]

    if not args.quiet:
        print_header("Landscape Statistics")
        print(format_stat("Technology dimensions (N)", str(config.n)))
        print(format_stat("Interdependencies (K)", str(config.k)))
        print(format_stat("Landscape ruggedness", f"{config.k/(config.n-1):.2f} (K/(N-1))"))

        print_header("Fitness Results")
        print(format_stat("Global best fitness", stats["global_best_fitness"]))
        print(format_stat("Current best fitness", stats["best_fitness"]))
        print(format_stat("Current mean fitness", stats["mean_fitness"]))
        print(format_stat("Technology diversity", stats["tech_diversity"]))

        print_header("Population Dynamics")
        print(format_stat("Final firm count", str(stats["num_firms"])))
        print(format_stat("Total innovations", str(stats["total_innovations"])))
        print(format_stat("Total destructions (exits)", str(stats["total_destructions"])))
        print(format_stat("Total entries", str(stats["total_entries"])))

        print_header("Strategy Breakdown")
        for strat, count in stats["strategy_counts"].items():
            print(format_stat(f"  {strat}", str(count)))

        print_header("Technology Phase Distribution")
        for phase, count in stats["phase_counts"].items():
            print(format_stat(f"  {phase}", str(count)))

        # Interpretation
        print_header("Interpretation")
        ruggedness = config.k / (config.n - 1) if config.n > 1 else 0

        if ruggedness < 0.3:
            print("  [*] Smooth landscape (low K/N): local search should dominate")
        elif ruggedness > 0.7:
            print("  [*] Rugged landscape (high K/N): long-jump and random search favored")
        else:
            print("  [*] Moderately rugged landscape: mixed strategies viable")

        if stats["tech_diversity"] > 0.6:
            print("  [*] High technology diversity -- many distinct approaches coexist")
        elif stats["tech_diversity"] < 0.3:
            print("  [*] Low diversity -- convergence to similar technologies")
        else:
            print("  [*] Moderate diversity -- some clustering with variation")

        if stats["total_destructions"] > config.ticks * 0.1:
            print("  [*] High creative destruction -- turbulent market")
        else:
            print("  [*] Low creative destruction -- relatively stable market")

        destruction_rate = stats["total_destructions"] / max(config.ticks, 1)
        innovation_rate = stats["total_innovations"] / max(config.ticks, 1)
        print(format_stat("Destruction rate (per tick)", destruction_rate))
        print(format_stat("Innovation rate (per tick)", innovation_rate))

        print_separator()

    # Save outputs
    if args.output:
        sim.save_csv(args.output)
        if not args.quiet:
            print(f"\n  CSV data saved to: {args.output}")

    if args.json_output:
        sim.save_json(args.json_output)
        if not args.quiet:
            print(f"  JSON data saved to: {args.json_output}")


if __name__ == '__main__':
    main()
