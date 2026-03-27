#!/usr/bin/env python3
"""
CLI for the Prisoner's Dilemma / Evolution of Cooperation simulation.

Usage:
    python cli.py --spatial --grid-size 50 --generations 200
    python cli.py --tournament --population 100 --generations 200
    python cli.py --spatial --noise 0.05 --mutation-rate 0.01 --output results.csv
"""

import argparse
import sys
from simulation import (
    Simulation, StrategyType, PayoffMatrix,
    SpatialSimulation, TournamentSimulation
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prisoner's Dilemma / Evolution of Cooperation Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --spatial --grid-size 50 --generations 200
  %(prog)s --tournament --population 100 --generations 300
  %(prog)s --spatial --noise 0.05 --seed 42 --output results.csv
  %(prog)s --tournament --payoff-T 5 --payoff-R 3 --payoff-P 1 --payoff-S 0
        """
    )

    # Mode
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument('--spatial', action='store_true', default=True,
                      help='Spatial mode: agents on a grid play neighbors (default)')
    mode.add_argument('--tournament', action='store_true',
                      help='Tournament mode: round-robin with replication')

    # Grid parameters (spatial)
    parser.add_argument('--grid-size', type=int, default=50,
                        help='Grid size for spatial mode (default: 50)')
    parser.add_argument('--neighborhood', choices=['moore', 'von_neumann'],
                        default='moore',
                        help='Neighborhood type for spatial mode (default: moore)')

    # Tournament parameters
    parser.add_argument('--population', type=int, default=100,
                        help='Population size for tournament mode (default: 100)')

    # Shared parameters
    parser.add_argument('--generations', '--ticks', type=int, default=200,
                        help='Number of generations (default: 200)')
    parser.add_argument('--rounds', type=int, default=10,
                        help='Rounds per match (default: 10)')
    parser.add_argument('--noise', type=float, default=0.0,
                        help='Probability of execution error (default: 0.0)')
    parser.add_argument('--mutation-rate', type=float, default=0.001,
                        help='Mutation rate per agent per generation (default: 0.001)')

    # Payoff matrix
    parser.add_argument('--payoff-T', type=float, default=5.0,
                        help='Temptation payoff (default: 5.0)')
    parser.add_argument('--payoff-R', type=float, default=3.0,
                        help='Reward payoff (default: 3.0)')
    parser.add_argument('--payoff-P', type=float, default=1.0,
                        help='Punishment payoff (default: 1.0)')
    parser.add_argument('--payoff-S', type=float, default=0.0,
                        help='Sucker payoff (default: 0.0)')

    # Output
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path')
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
        return f"  {label:.<40s} {value:>12{fmt}}"
    return f"  {label:.<40s} {str(value):>12s}"


def main():
    args = parse_args()

    mode = "tournament" if args.tournament else "spatial"

    # Validate payoff matrix
    pm = PayoffMatrix(T=args.payoff_T, R=args.payoff_R,
                      P=args.payoff_P, S=args.payoff_S)
    if not pm.is_valid():
        print("WARNING: Payoff matrix does not satisfy PD conditions "
              "(T > R > P > S and 2R > T + S)")

    if not args.quiet:
        print_header("Prisoner's Dilemma / Evolution of Cooperation")
        print(f"  Mode: {mode.capitalize()}")
        if mode == "spatial":
            print(f"  Grid size: {args.grid_size}x{args.grid_size}")
            print(f"  Neighborhood: {args.neighborhood}")
        else:
            print(f"  Population: {args.population}")
        print(f"  Generations: {args.generations}")
        print(f"  Rounds/match: {args.rounds}")
        print(f"  Noise: {args.noise}")
        print(f"  Mutation rate: {args.mutation_rate}")
        print(f"  Payoffs: T={args.payoff_T} R={args.payoff_R} "
              f"P={args.payoff_P} S={args.payoff_S}")
        if args.seed is not None:
            print(f"  Seed: {args.seed}")
        print_separator('-')
        print("  Running simulation...")

    def progress(g, n):
        if not args.quiet:
            pct = g / n * 100
            bar_len = 30
            filled = int(bar_len * g / n)
            bar = '#' * filled + '-' * (bar_len - filled)
            print(f"\r  [{bar}] {pct:5.1f}% (gen {g}/{n})",
                  end='', flush=True)

    sim = Simulation(
        mode=mode,
        grid_size=args.grid_size,
        population_size=args.population,
        rounds_per_match=args.rounds,
        noise=args.noise,
        mutation_rate=args.mutation_rate,
        payoff_T=args.payoff_T,
        payoff_R=args.payoff_R,
        payoff_P=args.payoff_P,
        payoff_S=args.payoff_S,
        neighborhood=args.neighborhood,
        generations=args.generations,
        seed=args.seed,
    )

    sim.run(progress_callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    stats = sim.get_statistics()

    if not args.quiet:
        print_header("Cooperation Metrics")
        print(format_stat("Final cooperation rate",
                          stats['final_cooperation_rate']))
        print(format_stat("Mean cooperation rate",
                          stats['mean_cooperation_rate']))
        print(format_stat("Final average payoff",
                          stats['final_average_payoff']))
        print(format_stat("Mean average payoff",
                          stats['mean_average_payoff']))

        print_header("Final Strategy Distribution")
        fracs = stats['final_strategy_fractions']
        for st in StrategyType:
            frac = fracs.get(st.value, 0)
            bar = '#' * int(frac * 40)
            print(f"  {st.short_name:>8s}: {frac:6.1%} {bar}")

        print_header("Interpretation")
        final_coop = stats['final_cooperation_rate']
        if final_coop > 0.7:
            print("  [*] Cooperation dominates the population")
        elif final_coop > 0.3:
            print("  [*] Mixed cooperation and defection")
        else:
            print("  [*] Defection dominates the population")

        tft_frac = fracs.get(StrategyType.TIT_FOR_TAT.value, 0)
        pavlov_frac = fracs.get(StrategyType.PAVLOV.value, 0)
        if tft_frac + pavlov_frac > 0.5:
            print("  [*] Reciprocal strategies (TFT/Pavlov) are dominant")

        defect_frac = fracs.get(StrategyType.ALWAYS_DEFECT.value, 0)
        if defect_frac < 0.05:
            print("  [*] Always Defect has been driven to near-extinction")

        print_separator()

    # Save CSV if requested
    if args.output:
        sim.to_csv(args.output)
        if not args.quiet:
            print(f"\n  Time series data saved to: {args.output}")


if __name__ == '__main__':
    main()
