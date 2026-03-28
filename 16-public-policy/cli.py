#!/usr/bin/env python3
"""
CLI for the Public Policy simulation.

Usage:
  python3 cli.py --ticks 500 --seed 42
  python3 cli.py --regime laissez-faire --ticks 500 --seed 42
  python3 cli.py --regime social-democrat --firms 50 --seed 42
  python3 cli.py --regime adaptive --ticks 500 --output results.csv --json results.json
  python3 cli.py --list-regimes
"""

import argparse
import sys
import os

from simulation import Config, Simulation, PolicyRegime, REGIMES


def progress_callback(tick: int, total: int, record):
    """Print progress during simulation."""
    if tick % 50 == 0:
        print(
            f"  tick {tick:5d}/{total}  "
            f"GDP={record.gdp:8.4f}  fitness={record.mean_fitness:.3f}  "
            f"alive={record.num_alive:3d}/{record.num_firms}  "
            f"gini={record.gini:.3f}  innov={record.innovation_rate:.3f}"
        )


def run_simulation(args):
    """Run the public policy simulation."""
    print("Public Policy Simulation")
    print("=" * 60)
    print(f"  Regime:              {args.regime}")
    print(f"  Firms:               {args.firms}")
    print(f"  Ticks:               {args.ticks}")
    print(f"  Seed:                {args.seed}")

    config = Config(
        num_firms=args.firms,
        num_ticks=args.ticks,
        regulation=args.regulation if args.regulation is not None else 0.3,
        tax_rate=args.tax_rate if args.tax_rate is not None else 0.2,
        innovation_subsidy=args.innovation_subsidy if args.innovation_subsidy is not None else 0.0,
        competition_limit=args.competition_limit if args.competition_limit is not None else 1.0,
        safety_net=args.safety_net if args.safety_net is not None else 0.3,
        seed=args.seed,
    )

    # Select regime
    if args.regime in REGIMES:
        regime = PolicyRegime(
            name=REGIMES[args.regime].name,
            regulation=REGIMES[args.regime].regulation,
            tax_rate=REGIMES[args.regime].tax_rate,
            innovation_subsidy=REGIMES[args.regime].innovation_subsidy,
            competition_limit=REGIMES[args.regime].competition_limit,
            safety_net=REGIMES[args.regime].safety_net,
        )
    elif args.regime == "custom":
        regime = PolicyRegime(
            name="custom",
            regulation=config.regulation,
            tax_rate=config.tax_rate,
            innovation_subsidy=config.innovation_subsidy,
            competition_limit=config.competition_limit,
            safety_net=config.safety_net,
        )
    else:
        print(f"Error: Unknown regime '{args.regime}'")
        print(f"Available: {', '.join(REGIMES.keys())}, custom")
        sys.exit(1)

    # Override individual policy levers if specified
    if args.regulation is not None and args.regime != "custom":
        regime.regulation = args.regulation
    if args.tax_rate is not None and args.regime != "custom":
        regime.tax_rate = args.tax_rate
    if args.innovation_subsidy is not None and args.regime != "custom":
        regime.innovation_subsidy = args.innovation_subsidy
    if args.competition_limit is not None and args.regime != "custom":
        regime.competition_limit = args.competition_limit
    if args.safety_net is not None and args.regime != "custom":
        regime.safety_net = args.safety_net

    print(f"  Regulation:          {regime.regulation:.2f}")
    print(f"  Tax rate:            {regime.tax_rate:.2f}")
    print(f"  Innovation subsidy:  {regime.innovation_subsidy:.2f}")
    print(f"  Competition limit:   {regime.competition_limit:.2f}")
    print(f"  Safety net:          {regime.safety_net:.2f}")
    print()

    sim = Simulation(config, regime)

    print("Running simulation...")
    sim.run(progress_callback=progress_callback)

    # Summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    stats = sim.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key:30s}: {value:.4f}")
        elif isinstance(value, str):
            print(f"  {key:30s}: {value}")
        else:
            print(f"  {key:30s}: {value}")

    # Save outputs
    if args.output:
        sim.save_csv(args.output)
        print(f"\n  CSV saved to: {args.output}")

    json_path = args.json
    if not json_path:
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "results.json",
        )
    sim.save_json(json_path)
    print(f"  JSON saved to: {json_path}")


def list_regimes():
    """List available policy regimes."""
    print("Available policy regimes:")
    print()
    descriptions = {
        "laissez-faire": "Low regulation, low tax, no subsidies, no market share limits. Minimal state.",
        "social-democrat": "Moderate regulation, high tax, strong safety net, innovation subsidies, competition policy.",
        "innovation-state": "Low regulation, moderate tax, high innovation subsidies. Focus on R&D.",
        "protectionist": "High regulation (entry barriers), moderate tax, minimal subsidies. Incumbents favored.",
        "adaptive": "Policy adjusts dynamically based on economic health indicators (GDP growth, Gini, unemployment).",
    }
    for name, desc in descriptions.items():
        r = REGIMES[name]
        print(f"  {name:20s}  {desc}")
        print(f"  {'':20s}  reg={r.regulation:.2f} tax={r.tax_rate:.2f} "
              f"subsidy={r.innovation_subsidy:.2f} comp={r.competition_limit:.2f} "
              f"safety={r.safety_net:.2f}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Public Policy Simulation -- Policy in a Complex World (Beinhocker Ch.18)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 500 --seed 42
  %(prog)s --regime laissez-faire --ticks 500 --seed 42
  %(prog)s --regime social-democrat --ticks 500 --seed 42
  %(prog)s --regime adaptive --ticks 500 --seed 42
  %(prog)s --regime custom --regulation 0.5 --tax-rate 0.3 --seed 42
  %(prog)s --list-regimes
        """,
    )

    # Mode
    parser.add_argument("--list-regimes", action="store_true",
                        help="List available policy regime presets")

    # Regime
    parser.add_argument("--regime", "-r", type=str, default="laissez-faire",
                        help="Policy regime preset (default: laissez-faire)")

    # Parameters
    parser.add_argument("--firms", type=int, default=50,
                        help="Number of firms (default: 50)")
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of ticks (default: 500)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    # Policy levers (override regime defaults)
    parser.add_argument("--regulation", type=float, default=None,
                        help="Regulation intensity 0-1 (overrides regime)")
    parser.add_argument("--tax-rate", type=float, default=None,
                        help="Tax rate 0-1 (overrides regime)")
    parser.add_argument("--innovation-subsidy", type=float, default=None,
                        help="Innovation subsidy 0-1 (overrides regime)")
    parser.add_argument("--competition-limit", type=float, default=None,
                        help="Max market share per firm 0-1 (overrides regime)")
    parser.add_argument("--safety-net", type=float, default=None,
                        help="Safety net strength 0-1 (overrides regime)")

    # Output
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", type=str, default=None,
                        help="Output JSON file path (default: results.json)")

    args = parser.parse_args()

    if args.list_regimes:
        list_regimes()
        return

    run_simulation(args)


if __name__ == "__main__":
    main()
