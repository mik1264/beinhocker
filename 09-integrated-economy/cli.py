#!/usr/bin/env python3
"""
CLI for the Integrated Economy simulation.

Usage:
  python cli.py --scenario normal --ticks 500
  python cli.py --scenario market_crash --firms 40 --seed 42
  python cli.py --scenario stress_test --ticks 500 --output results.csv --json results.json
  python cli.py --list-scenarios
"""

import argparse
import sys
import os

from simulation import Config, Simulation, SCENARIOS


def progress_callback(tick: int, total: int, record):
    """Print progress during simulation."""
    marker = ""
    if record.cascade_size > 0:
        marker = f"  *** CASCADE size={record.cascade_size} ***"
    if tick % 50 == 0 or record.cascade_size > 2:
        print(
            f"  tick {tick:5d}/{total}  phase={record.phase:16s}  "
            f"GDP={record.gdp:7.1f}  index={record.market_index:6.1f}  "
            f"alive={record.num_alive:3d}/{record.num_firms}{marker}"
        )


def run_simulation(args):
    """Run the integrated economy simulation."""
    print("Integrated Economy Simulation")
    print("=" * 60)
    print(f"  Scenario:  {args.scenario}")
    print(f"  Firms:     {args.firms}")
    print(f"  Ticks:     {args.ticks}")
    print(f"  Seed:      {args.seed}")
    print(f"  Demand:    {args.base_demand}")
    print(f"  Dep prob:  {args.dependency_prob}")
    print()

    config = Config(
        num_firms=args.firms,
        num_ticks=args.ticks,
        base_demand=args.base_demand,
        dependency_prob=args.dependency_prob,
        supply_chain_length=args.chain_length,
        seed=args.seed,
    )

    # Create scenario
    if args.scenario not in SCENARIOS:
        print(f"Error: Unknown scenario '{args.scenario}'")
        print(f"Available: {', '.join(SCENARIOS.keys())}")
        sys.exit(1)

    sim = SCENARIOS[args.scenario](config)

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
        else:
            print(f"  {key:30s}: {value}")

    # Phase transitions
    if sim.phase_history:
        print(f"\n  Phase transitions ({len(sim.phase_history)}):")
        for tick, phase in sim.phase_history[-15:]:
            print(f"    tick {tick:5d}: -> {phase}")

    # Events
    if sim.events:
        print(f"\n  Scheduled events triggered ({len(sim.events)}):")
        for event in sim.events:
            print(f"    tick {event['tick']:5d}: {event['type']}")

    # Cascade distribution
    cascade_sizes = [r.cascade_size for r in sim.history if r.cascade_size > 0]
    if cascade_sizes:
        from collections import Counter
        dist = Counter(cascade_sizes)
        print(f"\n  Cascade size distribution:")
        for size in sorted(dist.keys()):
            bar = "#" * min(dist[size], 50)
            print(f"    size {size:3d}: {dist[size]:4d} {bar}")

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


def list_scenarios():
    """List available scenarios."""
    print("Available scenarios:")
    print()
    descriptions = {
        "normal": "Normal operations. No scheduled disruptions. Economy evolves organically.",
        "supply_shock": "Demand spike at tick 100 (2.5x), normalizes at tick 150. Tests bullwhip effect.",
        "tech_disruption": "Major technology shift at tick 150. Old firms must adapt or die.",
        "market_crash": "Combined crisis: supply shock (t=80) + market panic (t=120) + tech disruption (t=160).",
        "stress_test": "Repeated shocks across the simulation. Tests long-run resilience and recovery.",
    }
    for name, desc in descriptions.items():
        print(f"  {name:20s}  {desc}")


def main():
    parser = argparse.ArgumentParser(
        description="Integrated Economy Simulation — Cross-Model Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scenario normal --ticks 500 --seed 42
  %(prog)s --scenario market_crash --firms 40 --json results.json
  %(prog)s --scenario stress_test --ticks 500 --output results.csv
  %(prog)s --list-scenarios
        """,
    )

    # Mode
    parser.add_argument("--list-scenarios", action="store_true",
                        help="List available scenario presets")

    # Scenario
    parser.add_argument("--scenario", "-s", type=str, default="normal",
                        help="Scenario preset (default: normal)")

    # Parameters
    parser.add_argument("--firms", type=int, default=40,
                        help="Number of firms (default: 40)")
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of ticks (default: 500)")
    parser.add_argument("--base-demand", type=float, default=10.0,
                        help="Base consumer demand (default: 10.0)")
    parser.add_argument("--dependency-prob", type=float, default=0.08,
                        help="Inter-firm dependency probability (default: 0.08)")
    parser.add_argument("--chain-length", type=int, default=4,
                        help="Supply chain echelons (default: 4)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    # Output
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", type=str, default=None,
                        help="Output JSON file path (default: results.json)")

    args = parser.parse_args()

    if args.list_scenarios:
        list_scenarios()
        return

    run_simulation(args)


if __name__ == "__main__":
    main()
