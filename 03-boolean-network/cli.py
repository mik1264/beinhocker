#!/usr/bin/env python3
"""
Command-line interface for Boolean Network simulation.

Usage examples:
    python cli.py --nodes 50 --connectivity 2 --bias 0.5 --topology random
    python cli.py --phase-diagram --nodes 30
    python cli.py --cascade-analysis --nodes 100 --connectivity 3
    python cli.py --attractor-search --nodes 40 --connectivity 2 --trials 100
    python cli.py --topology hierarchy --hierarchy-depth 3 --branching-factor 3
"""

import argparse
import sys
import os

from simulation import (
    Network,
    compute_phase_diagram,
    run_full_analysis,
    save_results_csv,
    save_results_json,
)


def main():
    parser = argparse.ArgumentParser(
        description="Boolean Network Organization / Complexity Catastrophe Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --nodes 50 --connectivity 2 --bias 0.5
  %(prog)s --phase-diagram --nodes 30 --output phase.csv
  %(prog)s --cascade-analysis --nodes 100 --connectivity 3
  %(prog)s --attractor-search --nodes 40 --connectivity 2 --trials 100
  %(prog)s --topology hierarchy --hierarchy-depth 3 --branching-factor 3
        """,
    )

    # Network parameters
    parser.add_argument(
        "-n", "--nodes", type=int, default=50, help="Number of nodes N (default: 50)"
    )
    parser.add_argument(
        "-k",
        "--connectivity",
        type=int,
        default=2,
        help="Number of inputs per node K (default: 2)",
    )
    parser.add_argument(
        "-b",
        "--bias",
        type=float,
        default=0.5,
        help="Bias parameter p for Boolean functions (default: 0.5)",
    )
    parser.add_argument(
        "-t",
        "--topology",
        choices=["random", "lattice", "hierarchy", "small-world"],
        default="random",
        help="Network topology (default: random)",
    )
    parser.add_argument(
        "--hierarchy-depth",
        type=int,
        default=3,
        help="Depth of hierarchy tree (default: 3)",
    )
    parser.add_argument(
        "--branching-factor",
        type=int,
        default=3,
        help="Branching factor of hierarchy tree (default: 3)",
    )
    parser.add_argument(
        "--rewire-prob",
        type=float,
        default=0.1,
        help="Rewiring probability for small-world topology (default: 0.1)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )

    # Analysis modes
    parser.add_argument(
        "--phase-diagram",
        action="store_true",
        help="Sweep K and bias to compute phase diagram",
    )
    parser.add_argument(
        "--cascade-analysis",
        action="store_true",
        help="Run cascade/perturbation analysis",
    )
    parser.add_argument(
        "--attractor-search",
        action="store_true",
        help="Search for attractor cycles",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full analysis (Derrida + attractors + cascades)",
    )

    # Analysis parameters
    parser.add_argument(
        "--trials",
        type=int,
        default=50,
        help="Number of trials for attractor search or cascade analysis (default: 50)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=50,
        help="Number of steps per cascade (default: 50)",
    )
    parser.add_argument(
        "--k-range",
        type=str,
        default="1-7",
        help="Range of K values for phase diagram, e.g. '1-7' (default: 1-7)",
    )

    # Output
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file path (CSV for phase diagram, JSON for others)",
    )

    args = parser.parse_args()

    if args.phase_diagram:
        run_phase_diagram(args)
    elif args.cascade_analysis:
        run_cascade(args)
    elif args.attractor_search:
        run_attractors(args)
    elif args.full:
        run_full(args)
    else:
        run_full(args)


def run_phase_diagram(args):
    """Sweep K and bias to compute and display phase diagram."""
    k_start, k_end = map(int, args.k_range.split("-"))
    K_values = list(range(k_start, k_end + 1))
    bias_values = [round(0.1 + 0.05 * i, 2) for i in range(17)]

    print("=" * 60)
    print("Phase Diagram Computation")
    print(f"  N={args.nodes}, topology={args.topology}")
    print(f"  K range: {K_values}")
    print(f"  Bias range: {bias_values[0]} to {bias_values[-1]}")
    print("=" * 60)

    results = compute_phase_diagram(
        N=args.nodes,
        K_values=K_values,
        bias_values=bias_values,
        topology=args.topology,
        num_pairs=100,
        num_repeats=3,
    )

    # Display as table
    print(f"\n{'K':>3} | {'bias':>5} | {'lambda':>8} | {'theory':>8} | {'regime':<10}")
    print("-" * 50)
    for r in results:
        print(
            f"{r['K']:>3} | {r['bias']:>5.2f} | {r['derrida_parameter']:>8.3f} | "
            f"{r['theoretical_lambda']:>8.3f} | {r['classification']:<10}"
        )

    # Display compact phase map
    print("\nPhase Map (O=ordered, C=chaotic, *=critical):")
    print(f"{'':>5}", end="")
    for b in bias_values:
        print(f"{b:.2f} ", end="")
    print()
    for K in K_values:
        print(f"K={K:>2} ", end="")
        for b in bias_values:
            r = next(x for x in results if x["K"] == K and x["bias"] == b)
            sym = {"ordered": "O", "chaotic": "C", "critical": "*"}[
                r["classification"]
            ]
            print(f"  {sym}  ", end="")
        print()

    # Save
    output = args.output or "phase_diagram.csv"
    save_results_csv(results, output)
    print(f"\nResults saved to {output}")


def run_cascade(args):
    """Run cascade analysis."""
    print("=" * 60)
    print("Cascade Analysis")
    print(
        f"  N={args.nodes}, K={args.connectivity}, bias={args.bias}, topology={args.topology}"
    )
    print(f"  Trials={args.trials}, Steps per cascade={args.steps}")
    print("=" * 60)

    net = Network(
        N=args.nodes,
        K=args.connectivity,
        bias=args.bias,
        topology=args.topology,
        hierarchy_depth=args.hierarchy_depth,
        branching_factor=args.branching_factor,
        rewire_prob=args.rewire_prob,
        seed=args.seed,
    )

    theoretical = 2 * args.connectivity * args.bias * (1 - args.bias)
    print(f"Theoretical lambda: {theoretical:.3f}")

    # Derrida parameter first
    derrida = net.derrida_parameter(200)
    regime = net.classify_regime(200)
    print(f"Measured Derrida parameter: {derrida:.3f}")
    print(f"Regime: {regime}")

    # Cascade analysis
    print("\nRunning cascade analysis...")
    stats = net.cascade_analysis(
        num_perturbations=args.trials, steps=args.steps
    )

    print(f"\nResults:")
    print(f"  Mean cascade size: {stats['mean_cascade_size']:.2f} / {args.nodes} nodes")
    print(f"  Max cascade size: {stats['max_cascade_size']}")
    print(f"  Mean max Hamming distance: {stats['mean_max_hamming']:.2f}")
    print(f"  Mean final Hamming distance: {stats['mean_final_hamming']:.2f}")

    print(f"\nCascade size distribution:")
    for size, count in sorted(stats["size_distribution"].items()):
        bar = "#" * count
        print(f"  {size:>4}: {count:>3} {bar}")

    if args.output:
        save_results_json(
            {
                "parameters": {
                    "N": args.nodes,
                    "K": args.connectivity,
                    "bias": args.bias,
                    "topology": args.topology,
                },
                "derrida_parameter": derrida,
                "regime": regime,
                "cascade_stats": stats,
            },
            args.output,
        )
        print(f"\nResults saved to {args.output}")


def run_attractors(args):
    """Search for attractor cycles."""
    print("=" * 60)
    print("Attractor Search")
    print(
        f"  N={args.nodes}, K={args.connectivity}, bias={args.bias}, topology={args.topology}"
    )
    print(f"  Trials={args.trials}")
    print("=" * 60)

    net = Network(
        N=args.nodes,
        K=args.connectivity,
        bias=args.bias,
        topology=args.topology,
        hierarchy_depth=args.hierarchy_depth,
        branching_factor=args.branching_factor,
        rewire_prob=args.rewire_prob,
        seed=args.seed,
    )

    theoretical = 2 * args.connectivity * args.bias * (1 - args.bias)
    print(f"Theoretical lambda: {theoretical:.3f}")

    stats = net.attractor_search(num_trials=args.trials, max_steps=5000)

    print(f"\nResults:")
    print(f"  Attractors found: {stats['attractors_found']}/{stats['num_trials']}")
    print(f"  Unique attractors: {stats['unique_attractors']}")
    if stats["mean_cycle_length"] is not None:
        print(f"  Mean cycle length: {stats['mean_cycle_length']:.2f}")
        print(f"  Median cycle length: {stats['median_cycle_length']:.2f}")
        print(f"  Max cycle length: {stats['max_cycle_length']}")
        print(f"  Mean transient length: {stats['mean_transient_length']:.2f}")

        print(f"\nCycle length distribution:")
        cycle_counts = {}
        for c in stats["cycle_lengths"]:
            cycle_counts[c] = cycle_counts.get(c, 0) + 1
        for length, count in sorted(cycle_counts.items()):
            bar = "#" * min(count, 50)
            print(f"  {length:>6}: {count:>3} {bar}")

    if args.output:
        save_results_json(
            {
                "parameters": {
                    "N": args.nodes,
                    "K": args.connectivity,
                    "bias": args.bias,
                    "topology": args.topology,
                },
                "attractor_stats": stats,
            },
            args.output,
        )
        print(f"\nResults saved to {args.output}")


def run_full(args):
    """Run full analysis."""
    results = run_full_analysis(
        N=args.nodes,
        K=args.connectivity,
        bias=args.bias,
        topology=args.topology,
        seed=args.seed,
    )

    if args.output:
        save_results_json(results, args.output)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
