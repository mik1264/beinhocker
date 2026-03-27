#!/usr/bin/env python3
"""
CLI for the Business Plan Evolution simulation.

Usage:
    python3 cli.py --ticks 300 --seed 42
    python3 cli.py --ticks 300 --population 100 --mutation-rate 0.1
    python3 cli.py --ticks 300 --preference-shift-rate 0.0 --seed 42
"""

import argparse
import sys
from simulation import BusinessPlanSimulation, SimConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description='Business Plan Evolution Simulation (Beinhocker Ch.14)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 300 --seed 42
  %(prog)s --ticks 300 --preference-shift-rate 0.0 --seed 42
  %(prog)s --ticks 300 --mutation-rate 0.15 --seed 42
  %(prog)s --ticks 300 --population 200 --seed 42
        """
    )

    # Population
    parser.add_argument('--population', type=int, default=50,
                        help='Number of business plans (default: 50)')
    parser.add_argument('--ticks', type=int, default=300,
                        help='Number of simulation ticks (default: 300)')

    # Component lengths
    parser.add_argument('--pt-length', type=int, default=8,
                        help='Physical Technology bit-string length (default: 8)')
    parser.add_argument('--st-length', type=int, default=8,
                        help='Social Technology bit-string length (default: 8)')
    parser.add_argument('--strategy-length', type=int, default=8,
                        help='Strategy bit-string length (default: 8)')

    # Evolution parameters
    parser.add_argument('--mutation-rate', type=float, default=0.05,
                        help='Mutation rate per bit (default: 0.05)')
    parser.add_argument('--crossover-rate', type=float, default=0.3,
                        help='Crossover probability during replication (default: 0.3)')
    parser.add_argument('--preference-shift-rate', type=float, default=0.02,
                        help='Rate of market preference shifts (default: 0.02)')
    parser.add_argument('--k-epistasis', type=int, default=3,
                        help='NK epistatic interactions per locus (default: 3)')

    # General
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output CSV file path')
    parser.add_argument('--json-output', type=str, default=None,
                        help='Output JSON file path')
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
        if abs(value) > 1e6:
            return f"  {label:.<44s} {value:>14,.0f}"
        return f"  {label:.<44s} {value:>14{fmt}}"
    return f"  {label:.<44s} {str(value):>14s}"


def main():
    args = parse_args()

    config = SimConfig(
        population=args.population,
        ticks=args.ticks,
        pt_length=args.pt_length,
        st_length=args.st_length,
        strategy_length=args.strategy_length,
        k_epistasis=args.k_epistasis,
        mutation_rate=args.mutation_rate,
        crossover_rate=args.crossover_rate,
        preference_shift_rate=args.preference_shift_rate,
        seed=args.seed,
    )

    if not args.quiet:
        print_header("Business Plan Evolution Simulation")
        print(f"  Population: {config.population}")
        print(f"  Ticks: {config.ticks}")
        print(f"  Components: PT={config.pt_length}, ST={config.st_length}, Strategy={config.strategy_length}")
        print(f"  K (epistasis): {config.k_epistasis}")
        print(f"  Mutation rate: {config.mutation_rate}")
        print(f"  Crossover rate: {config.crossover_rate}")
        print(f"  Preference shift rate: {config.preference_shift_rate}")
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
            w = record.total_wealth
            mf = record.mean_fitness
            bf = record.best_fitness
            print(f"\r  [{bar}] {pct:5.1f}% tick {t}/{n} | wealth={w:.3f} mean={mf:.3f} best={bf:.3f}",
                  end='', flush=True)

    sim = BusinessPlanSimulation(config)
    sim.run(callback=progress)

    if not args.quiet:
        print()  # newline after progress bar

    # Summary statistics
    state = sim.get_state_json()
    stats = state["stats"]

    if not args.quiet:
        print_header("Wealth and Fitness")
        print(format_stat("Total wealth (fit order)", stats["total_wealth"]))
        print(format_stat("Best fitness", stats["best_fitness"]))
        print(format_stat("Mean fitness", stats["mean_fitness"]))

        print_header("Component Fitness Breakdown")
        print(format_stat("Mean Physical Technology (PT)", stats["mean_pt_fitness"]))
        print(format_stat("Mean Social Technology (ST)", stats["mean_st_fitness"]))
        print(format_stat("Mean Strategy (market fit)", stats["mean_strategy_fitness"]))

        print_header("Population Dynamics")
        print(format_stat("Final population", str(stats["population"])))
        print(format_stat("Total creative destructions", str(stats["total_destructions"])))
        print(format_stat("Total new entrants", str(stats["total_entries"])))
        print(format_stat("Total innovations", str(stats["total_innovations"])))

        print_header("Market Structure")
        print(format_stat("Population diversity", stats["diversity"]))
        print(format_stat("Market share Gini", stats["gini"]))

        # Interpretation
        print_header("Interpretation")

        # Compare component fitnesses
        pt = stats["mean_pt_fitness"]
        st = stats["mean_st_fitness"]
        strat = stats["mean_strategy_fitness"]
        components = [("Physical Technology", pt), ("Social Technology", st), ("Strategy", strat)]
        components.sort(key=lambda x: x[1], reverse=True)
        print(f"  [*] Strongest component: {components[0][0]} ({components[0][1]:.3f})")
        print(f"  [*] Weakest component:   {components[2][0]} ({components[2][1]:.3f})")

        if stats["diversity"] > 0.4:
            print("  [*] High diversity -- many distinct business plan strategies coexist")
        elif stats["diversity"] < 0.2:
            print("  [*] Low diversity -- convergence toward similar business plans")
        else:
            print("  [*] Moderate diversity -- some clustering with variation")

        if stats["gini"] > 0.5:
            print("  [*] High inequality -- a few dominant BPs capture most market share")
        elif stats["gini"] < 0.25:
            print("  [*] Low inequality -- market share relatively evenly distributed")
        else:
            print("  [*] Moderate inequality in market share distribution")

        if config.preference_shift_rate == 0.0:
            print("  [*] Stable preferences -- BPs can fully optimize for fixed demand")
        elif config.preference_shift_rate > 0.05:
            print("  [*] Rapid preference shifts -- Red Queen effect, constant adaptation needed")
        else:
            print("  [*] Gradual preference shifts -- evolutionary pressure present but manageable")

        destruction_rate = stats["total_destructions"] / max(config.ticks, 1)
        innovation_rate = stats["total_innovations"] / max(config.ticks, 1)
        print(format_stat("Destruction rate (per tick)", destruction_rate))
        print(format_stat("Innovation rate (per tick)", innovation_rate))

        # Track fitness trajectory
        if sim.history:
            early = sim.history[:30]
            late = sim.history[-30:]
            early_mean = sum(r.mean_fitness for r in early) / len(early)
            late_mean = sum(r.mean_fitness for r in late) / len(late)
            improvement = (late_mean - early_mean) / max(early_mean, 0.001)
            print(format_stat("Fitness improvement (early->late)", improvement))

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
