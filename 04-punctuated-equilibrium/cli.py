#!/usr/bin/env python3
"""
CLI for the Punctuated Equilibrium Ecosystem simulation.

Usage:
  python cli.py --evolve --species 100 --ticks 1000
  python cli.py --cascade-test --species 50
  python cli.py --evolve --species 100 --ticks 500 --output results.csv --json results.json
"""

import argparse
import sys
import os

from simulation import Ecosystem, Phase


def progress_callback(tick: int, cascade_size: int, phase: Phase):
    """Print progress during evolution."""
    marker = ""
    if cascade_size > 0:
        marker = f"  *** CASCADE size={cascade_size} ***"
    if tick % 50 == 0 or cascade_size > 0:
        print(f"  tick {tick:5d}  phase={phase.value:12s}{marker}")


def run_evolve(args):
    """Run the evolution simulation."""
    print(f"Punctuated Equilibrium Ecosystem Simulation")
    print(f"  Species: {args.species}")
    print(f"  Ticks: {args.ticks}")
    print(f"  Connection probability: {args.connection_prob}")
    print(f"  Weight range: [{args.weight_min}, {args.weight_max}]")
    print(f"  Seed: {args.seed}")
    print()

    eco = Ecosystem(
        n_species=args.species,
        connection_prob=args.connection_prob,
        weight_range=(args.weight_min, args.weight_max),
        seed=args.seed,
    )

    print("Running evolution...")
    eco.run(args.ticks, callback=progress_callback)

    # Summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    total_cascades = len(eco.cascades)
    cascade_sizes = [c.size for c in eco.cascades]
    print(f"  Total ticks: {eco.tick}")
    print(f"  Total cascades: {total_cascades}")
    if cascade_sizes:
        print(f"  Mean cascade size: {sum(cascade_sizes) / len(cascade_sizes):.1f}")
        print(f"  Max cascade size: {max(cascade_sizes)}")
        print(f"  Min cascade size: {min(cascade_sizes)}")

    # Phase transitions
    print(f"\n  Phase transitions: {len(eco.phase_history)}")
    for tick, phase in eco.phase_history[-10:]:
        print(f"    tick {tick:5d}: -> {phase.value}")

    # Cascade size distribution
    dist = eco.get_cascade_distribution()
    if dist:
        print(f"\n  Cascade size distribution:")
        for size, count in sorted(dist.items()):
            bar = "#" * min(count, 50)
            print(f"    size {size:3d}: {count:4d} {bar}")

    # Final state
    state = eco.get_state_json()
    print(f"\n  Final state:")
    print(f"    Mean fitness: {state['stats']['mean_fitness']:.4f}")
    print(f"    Density: {state['stats']['density']:.4f}")
    print(f"    Diversity: {state['stats']['diversity']:.4f}")
    print(f"    Keystones: {state['stats']['num_keystones']}")
    print(f"    Phase: {state['phase']}")

    # Save outputs
    if args.output:
        eco.save_csv(args.output)
        print(f"\n  CSV saved to: {args.output}")

    json_path = args.json
    if not json_path:
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "results.json",
        )
    eco.save_json(json_path)
    print(f"  JSON saved to: {json_path}")


def run_cascade_test(args):
    """Systematically remove species and measure cascades."""
    print(f"Cascade Test")
    print(f"  Species: {args.species}")
    print(f"  Connection probability: {args.connection_prob}")
    print(f"  Weight range: [{args.weight_min}, {args.weight_max}]")
    print(f"  Seed: {args.seed}")
    print()

    eco = Ecosystem(
        n_species=args.species,
        connection_prob=args.connection_prob,
        weight_range=(args.weight_min, args.weight_max),
        seed=args.seed,
    )

    # Run a warmup period to let the ecosystem organize
    warmup = min(args.ticks, 200)
    print(f"Running {warmup}-tick warmup...")
    eco.run(warmup)

    print(f"\nTesting removal of each species...")
    results = eco.cascade_test()

    # Sort by cascade size descending
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"\n{'Species':>8s} {'Cascade':>8s} {'Keystone':>9s}")
    print("-" * 30)
    for species_id, cascade_size, was_keystone in results[:20]:
        ks = "YES" if was_keystone else "no"
        bar = "#" * min(cascade_size, 40)
        print(f"  {species_id:5d}    {cascade_size:5d}     {ks:>4s}  {bar}")

    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more species")

    # Summary statistics
    sizes = [r[1] for r in results]
    keystone_sizes = [r[1] for r in results if r[2]]
    non_keystone_sizes = [r[1] for r in results if not r[2]]

    print(f"\nSummary:")
    print(f"  Total species tested: {len(results)}")
    print(f"  Mean cascade size (all): {sum(sizes) / len(sizes):.1f}")
    if keystone_sizes:
        print(f"  Mean cascade size (keystones): {sum(keystone_sizes) / len(keystone_sizes):.1f}")
    if non_keystone_sizes:
        print(f"  Mean cascade size (non-keystones): {sum(non_keystone_sizes) / len(non_keystone_sizes):.1f}")
    print(f"  Max cascade: species {results[0][0]} (size {results[0][1]})")

    # Save results
    if args.output:
        import csv
        with open(args.output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["species_id", "cascade_size", "was_keystone"])
            for species_id, cascade_size, was_keystone in results:
                writer.writerow([species_id, cascade_size, was_keystone])
        print(f"\n  CSV saved to: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="Punctuated Equilibrium Ecosystem Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --evolve --species 100 --ticks 1000
  %(prog)s --cascade-test --species 50 --output cascade_results.csv
  %(prog)s --evolve --ticks 500 --seed 42 --json results.json
        """,
    )

    # Mode
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--evolve", action="store_true",
                      help="Run evolution simulation")
    mode.add_argument("--cascade-test", action="store_true",
                      help="Systematically remove species and measure cascades")

    # Parameters
    parser.add_argument("--species", type=int, default=100,
                        help="Number of species (default: 100)")
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of ticks to simulate (default: 500)")
    parser.add_argument("--connection-prob", type=float, default=0.05,
                        help="Probability of connection between species (default: 0.05)")
    parser.add_argument("--weight-min", type=float, default=-1.0,
                        help="Minimum edge weight (default: -1.0)")
    parser.add_argument("--weight-max", type=float, default=1.0,
                        help="Maximum edge weight (default: 1.0)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    # Output
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", type=str, default=None,
                        help="Output JSON file path (default: results.json)")

    args = parser.parse_args()

    if args.evolve:
        run_evolve(args)
    elif args.cascade_test:
        run_cascade_test(args)


if __name__ == "__main__":
    main()
