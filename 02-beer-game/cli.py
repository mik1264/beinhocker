#!/usr/bin/env python3
"""
Beer Distribution Game — Command-Line Interface
================================================
Run the Beer Game simulation with configurable parameters.

Usage examples:
  python cli.py                              # Default behavioral run
  python cli.py --rational                   # Optimal ordering policy
  python cli.py --ticks 50 --alpha 0.3       # Custom parameters
  python cli.py --information-sharing        # Brewery sees retail demand
  python cli.py --compare                    # Side-by-side comparison
  python cli.py --output results.csv         # Save to CSV
"""

import argparse
import sys

from simulation import (
    Simulation,
    SimulationConfig,
    print_results,
    run_comparison,
    DEMAND_PATTERNS,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Beer Distribution Game Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Demand patterns:
  step      Constant 4, then jumps to 8 at --step-tick (default)
  constant  Fixed demand (set with --demand-value)
  ramp      Linearly increasing demand
  sine      Sinusoidal demand

Examples:
  %(prog)s --rational --ticks 50
  %(prog)s --demand-pattern sine --ticks 100
  %(prog)s --compare --output comparison.csv
        """,
    )

    # Simulation parameters
    parser.add_argument(
        "--ticks", type=int, default=36,
        help="Number of simulation ticks/weeks (default: 36)",
    )
    parser.add_argument(
        "--demand-pattern", choices=list(DEMAND_PATTERNS.keys()), default="step",
        help="Consumer demand pattern (default: step)",
    )
    parser.add_argument(
        "--step-tick", type=int, default=5,
        help="Tick at which step demand increases (default: 5)",
    )
    parser.add_argument(
        "--demand-value", type=int, default=4,
        help="Demand value for constant pattern (default: 4)",
    )
    parser.add_argument(
        "--shipping-delay", type=int, default=2,
        help="Shipping delay in ticks (default: 2)",
    )
    parser.add_argument(
        "--order-delay", type=int, default=1,
        help="Order processing delay in ticks (default: 1)",
    )
    parser.add_argument(
        "--initial-inventory", type=int, default=12,
        help="Initial inventory per agent (default: 12)",
    )
    parser.add_argument(
        "--desired-inventory", type=int, default=12,
        help="Desired inventory target (default: 12)",
    )

    # Decision parameters
    parser.add_argument(
        "--alpha", type=float, default=0.5,
        help="Inventory adjustment weight (default: 0.5)",
    )
    parser.add_argument(
        "--beta", type=float, default=0.2,
        help="Supply line adjustment weight (default: 0.2)",
    )
    parser.add_argument(
        "--theta", type=float, default=0.2,
        help="Demand smoothing factor (default: 0.2)",
    )

    # Mode selection
    parser.add_argument(
        "--rational", action="store_true",
        help="Use optimal (rational) ordering policy instead of behavioral",
    )
    parser.add_argument(
        "--information-sharing", action="store_true",
        help="Enable information sharing (upstream agents see consumer demand)",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Run both behavioral and rational, show comparison",
    )

    # Seed
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility",
    )

    # Output
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Save results to CSV file",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress printed output (useful with --output)",
    )

    return parser.parse_args(argv)


def build_config(args) -> SimulationConfig:
    """Build a SimulationConfig from parsed arguments."""
    demand_kwargs = {}
    if args.demand_pattern == "step":
        demand_kwargs["step_tick"] = args.step_tick
    elif args.demand_pattern == "constant":
        demand_kwargs["value"] = args.demand_value

    return SimulationConfig(
        ticks=args.ticks,
        demand_pattern=args.demand_pattern,
        demand_kwargs=demand_kwargs,
        shipping_delay=args.shipping_delay,
        order_delay=args.order_delay,
        alpha=args.alpha,
        beta=args.beta,
        theta=args.theta,
        initial_inventory=args.initial_inventory,
        desired_inventory=args.desired_inventory,
        rational=args.rational,
        information_sharing=args.information_sharing,
    )


def main(argv=None):
    args = parse_args(argv)
    config = build_config(args)

    if args.compare:
        # Run both modes
        config.rational = False
        results_b, results_r = run_comparison(config)

        if not args.quiet:
            print_results(results_b, "BEHAVIORAL (Sterman Anchor-and-Adjust)")
            print_results(results_r, "RATIONAL (Optimal Ordering)")

            print(f"\n{'='*60}")
            print(f"  COMPARISON")
            print(f"{'='*60}")
            print(f"\n  Cost ratio (behavioral/rational): "
                  f"{results_b.total_cost / max(results_r.total_cost, 0.01):.1f}x")

            print(f"\n  Bullwhip at Brewery:")
            bw_b = dict(results_b.bullwhip_ratios())
            bw_r = dict(results_r.bullwhip_ratios())
            print(f"    Behavioral: {bw_b['Brewery']:.2f}")
            print(f"    Rational:   {bw_r['Brewery']:.2f}")

        if args.output:
            # Save behavioral results (primary)
            results_b.to_csv(args.output)
            # Save rational results with _rational suffix
            rational_path = args.output.replace(".csv", "_rational.csv")
            results_r.to_csv(rational_path)
            if not args.quiet:
                print(f"\nResults saved to {args.output} and {rational_path}")
    else:
        # Single run
        sim = Simulation(config)
        results = sim.run()

        mode = "Rational" if args.rational else "Behavioral"
        info = " + Information Sharing" if args.information_sharing else ""

        if not args.quiet:
            print_results(results, f"Beer Distribution Game — {mode}{info}")

        if args.output:
            results.to_csv(args.output)
            if not args.quiet:
                print(f"\nResults saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
