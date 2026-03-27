#!/usr/bin/env python3
"""
CLI for the Sugarscape simulation.

Usage:
    python cli.py --agents 400 --ticks 500
    python cli.py --agents 200 --ticks 1000 --reproduction --output results.csv
    python cli.py --agents 300 --grid-size 50 --seed 42
"""

import argparse
import csv
import sys
from simulation import Simulation, SugarscapeConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description='Sugarscape Simulation (Epstein & Axtell)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --agents 400 --ticks 500
  %(prog)s --agents 200 --ticks 1000 --reproduction
  %(prog)s --agents 300 --grid-size 50 --seed 42 --output results.csv
  %(prog)s --agents 400 --pollution --regrowth-rate 1
  %(prog)s --agents 400 --cultural-tags --reproduction
        """
    )

    # Grid parameters
    parser.add_argument('--grid-size', type=int, default=50,
                        help='Grid dimension (NxN) (default: 50)')
    parser.add_argument('--agents', type=int, default=400,
                        help='Initial number of agents (default: 400)')
    parser.add_argument('--ticks', type=int, default=500,
                        help='Number of simulation time steps (default: 500)')

    # Agent parameters
    parser.add_argument('--vision-min', type=int, default=1,
                        help='Minimum agent vision range (default: 1)')
    parser.add_argument('--vision-max', type=int, default=6,
                        help='Maximum agent vision range (default: 6)')
    parser.add_argument('--metabolism-min', type=int, default=1,
                        help='Minimum agent metabolism (default: 1)')
    parser.add_argument('--metabolism-max', type=int, default=4,
                        help='Maximum agent metabolism (default: 4)')
    parser.add_argument('--endowment-min', type=int, default=5,
                        help='Minimum initial sugar endowment (default: 5)')
    parser.add_argument('--endowment-max', type=int, default=25,
                        help='Maximum initial sugar endowment (default: 25)')

    # Sugar regrowth
    parser.add_argument('--regrowth-rate', type=int, default=1,
                        help='Sugar regrowth per tick (0=instant) (default: 1)')

    # Extensions
    parser.add_argument('--reproduction', action='store_true',
                        help='Enable agent reproduction')
    parser.add_argument('--reproduction-threshold', type=float, default=50.0,
                        help='Sugar needed to reproduce (default: 50.0)')
    parser.add_argument('--max-agent-age', type=int, default=0,
                        help='Maximum agent age in ticks (0=unlimited) (default: 0)')

    parser.add_argument('--pollution', action='store_true',
                        help='Enable pollution mechanics')
    parser.add_argument('--pollution-production', type=float, default=1.0,
                        help='Pollution per sugar gathered (default: 1.0)')
    parser.add_argument('--pollution-consumption', type=float, default=1.0,
                        help='Pollution per sugar consumed (default: 1.0)')
    parser.add_argument('--pollution-diffusion', type=float, default=0.25,
                        help='Pollution diffusion rate (default: 0.25)')

    parser.add_argument('--cultural-tags', action='store_true',
                        help='Enable cultural tag exchange')
    parser.add_argument('--num-cultural-bits', type=int, default=11,
                        help='Number of cultural tag bits (default: 11)')

    # Output
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
    if isinstance(value, bool):
        return f"  {label:.<40s} {'Yes' if value else 'No':>12s}"
    return f"  {label:.<40s} {str(value):>12s}"


def main():
    args = parse_args()

    config = SugarscapeConfig(
        grid_size=args.grid_size,
        num_agents=args.agents,
        max_ticks=args.ticks,
        vision_min=args.vision_min,
        vision_max=args.vision_max,
        metabolism_min=args.metabolism_min,
        metabolism_max=args.metabolism_max,
        endowment_min=args.endowment_min,
        endowment_max=args.endowment_max,
        regrowth_rate=args.regrowth_rate,
        reproduction=args.reproduction,
        reproduction_threshold=args.reproduction_threshold,
        max_agent_age=args.max_agent_age,
        pollution=args.pollution,
        pollution_production=args.pollution_production if args.pollution else 0.0,
        pollution_consumption=args.pollution_consumption if args.pollution else 0.0,
        pollution_diffusion_rate=args.pollution_diffusion if args.pollution else 0.0,
        cultural_tags=args.cultural_tags,
        num_cultural_bits=args.num_cultural_bits,
        seed=args.seed,
    )

    if not args.quiet:
        print_header("Sugarscape Simulation")
        print(f"  Grid: {config.grid_size}x{config.grid_size}")
        print(f"  Agents: {config.num_agents}")
        print(f"  Ticks: {config.max_ticks}")
        print(f"  Vision range: {config.vision_min}-{config.vision_max}")
        print(f"  Metabolism range: {config.metabolism_min}-{config.metabolism_max}")
        print(f"  Endowment range: {config.endowment_min}-{config.endowment_max}")
        print(f"  Regrowth rate: {'instant' if config.regrowth_rate == 0 else config.regrowth_rate}")
        if config.reproduction:
            print(f"  Reproduction: enabled (threshold={config.reproduction_threshold})")
        if config.pollution:
            print(f"  Pollution: enabled")
        if config.cultural_tags:
            print(f"  Cultural tags: enabled ({config.num_cultural_bits} bits)")
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
        print(format_stat("Initial population", str(config.num_agents)))
        print(format_stat("Final population", str(stats['final_population'])))
        print(format_stat("Population change", str(stats['population_change'])))

        print_header("Wealth Distribution")
        print(format_stat("Gini coefficient", stats['gini_coefficient']))
        print(format_stat("Mean wealth", stats['mean_wealth']))
        print(format_stat("Median wealth", stats['median_wealth']))
        print(format_stat("Std wealth", stats['std_wealth']))
        print(format_stat("Min wealth", stats['min_wealth']))
        print(format_stat("Max wealth", stats['max_wealth']))

        print_header("Surviving Agent Traits")
        print(format_stat("Mean vision", stats['mean_vision']))
        print(format_stat("Mean metabolism", stats['mean_metabolism']))
        print(format_stat("Mean age", stats['mean_age']))

        print_header("Environment")
        print(format_stat("Total sugar on grid", stats['total_sugar_on_grid']))

        # Interpret results
        print_header("Interpretation")
        gini = stats['gini_coefficient']
        if gini > 0.5:
            print("  [*] High inequality (Gini > 0.5) -- wealth concentrated among few")
        elif gini > 0.3:
            print("  [*] Moderate inequality (Gini 0.3-0.5)")
        else:
            print("  [ ] Low inequality (Gini < 0.3)")

        pop_pct = stats['final_population'] / config.num_agents * 100
        if pop_pct < 50:
            print(f"  [*] Major die-off: only {pop_pct:.0f}% survived")
        elif pop_pct < 80:
            print(f"  [*] Significant attrition: {pop_pct:.0f}% survived")
        else:
            print(f"  [ ] Population stable: {pop_pct:.0f}% survived")

        if stats['mean_vision'] > (config.vision_min + config.vision_max) / 2:
            print("  [*] Natural selection favors higher vision")
        if stats['mean_metabolism'] < (config.metabolism_min + config.metabolism_max) / 2:
            print("  [*] Natural selection favors lower metabolism")

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
