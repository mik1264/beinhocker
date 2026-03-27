#!/usr/bin/env python3
"""
CLI for the Rigids vs Flexibles Organizational Adaptation Simulation.

Usage examples:
    python cli.py --ticks 500 --stability 100
    python cli.py --mode random --noise 0.2
    python cli.py --sweep --sweep-steps 21 --ticks 1000
    python cli.py --json output.json
"""

import argparse
import csv
import json
import sys

from simulation import Simulation, run_sweep


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rigids vs Flexibles: Organizational Adaptation Simulation"
    )

    # Hierarchy parameters
    parser.add_argument("--levels", type=int, default=4,
                        help="Number of hierarchy levels (default: 4)")
    parser.add_argument("--branching-factor", type=int, default=3,
                        help="Branching factor per level (default: 3)")

    # Simulation parameters
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of simulation ticks (default: 500)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    # Environment parameters
    parser.add_argument("--stability", type=float, default=100.0,
                        help="Avg ticks between environment switches (default: 100)")
    parser.add_argument("--mode", choices=["punctuated", "random"],
                        default="punctuated",
                        help="Environment switching pattern (default: punctuated)")

    # Agent parameters
    parser.add_argument("--rigid-fraction", type=float, default=0.5,
                        help="Initial fraction of rigid agents (default: 0.5)")
    parser.add_argument("--experience-weight", type=float, default=0.1,
                        help="Weight of experience in performance (default: 0.1)")
    parser.add_argument("--noise", type=float, default=0.1,
                        help="Flexible agent observation noise (default: 0.1)")

    # Sweep mode
    parser.add_argument("--sweep", action="store_true",
                        help="Run sweep over rigid fraction values")
    parser.add_argument("--sweep-steps", type=int, default=11,
                        help="Number of steps in sweep (default: 11)")

    # Output
    parser.add_argument("--csv", type=str, default=None,
                        help="Save tick-by-tick results to CSV file")
    parser.add_argument("--json", type=str, default=None,
                        help="Save full results to JSON file")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress console output")

    return parser.parse_args()


def print_header(args, total_agents, level_sizes):
    print("=" * 60)
    print("  Rigids vs Flexibles: Organizational Adaptation")
    print("=" * 60)
    print(f"  Hierarchy:  {args.levels} levels, branching factor {args.branching_factor}")
    print(f"  Agents:     {total_agents} total ({level_sizes})")
    print(f"  Ticks:      {args.ticks}")
    print(f"  Stability:  {args.stability} (avg ticks between switches)")
    print(f"  Mode:       {args.mode}")
    print(f"  Rigid frac: {args.rigid_fraction:.0%}")
    print(f"  Experience: weight={args.experience_weight}")
    print(f"  Noise:      {args.noise}")
    if args.seed is not None:
        print(f"  Seed:       {args.seed}")
    print("=" * 60)
    print()


def print_level_composition(sim):
    print("Level-by-Level Composition (final state):")
    print(f"  {'Level':<8} {'Agents':<8} {'Rigid%':<10} {'Flexible%':<10}")
    print(f"  {'-'*36}")
    for level in range(sim.hierarchy.levels):
        agents = sim.hierarchy.agents_by_level[level]
        total = len(agents)
        rigid = sum(1 for a in agents if a.agent_type == "rigid")
        flex = total - rigid
        r_pct = rigid / total * 100 if total > 0 else 0
        f_pct = flex / total * 100 if total > 0 else 0
        label = "top" if level == sim.hierarchy.levels - 1 else f"L{level}"
        print(f"  {label:<8} {total:<8} {r_pct:>5.1f}%    {f_pct:>5.1f}%")
    print()


def print_performance_summary(sim):
    import numpy as np

    history = sim.history
    perfs = [r.org_performance for r in history]
    rigid_perfs = [r.rigid_avg_performance for r in history]
    flex_perfs = [r.flexible_avg_performance for r in history]

    print("Performance Summary:")
    print(f"  Overall avg:       {np.mean(perfs):.4f}")
    print(f"  Rigid avg:         {np.mean(rigid_perfs):.4f}")
    print(f"  Flexible avg:      {np.mean(flex_perfs):.4f}")
    print()

    # Transition analysis
    transitions = sim.get_transition_analysis()
    if transitions:
        print(f"Transition Analysis ({len(transitions)} environment switches):")
        print(f"  {'Switch':<8} {'Pre-perf':<10} {'Post-perf':<10} {'Drop':<10} {'Recovery':<10}")
        print(f"  {'-'*48}")
        for t in transitions:
            print(f"  t={t['switch_tick']:<5} {t['before_avg_performance']:.4f}    "
                  f"{t['after_avg_performance']:.4f}    "
                  f"{t['performance_drop']:+.4f}   "
                  f"{t['recovery_ticks']} ticks")
        avg_drop = np.mean([t["performance_drop"] for t in transitions])
        avg_recovery = np.mean([t["recovery_ticks"] for t in transitions])
        print(f"\n  Avg transition cost:   {avg_drop:+.4f}")
        print(f"  Avg recovery time:     {avg_recovery:.1f} ticks")
    else:
        print("No environment switches occurred.")
    print()


def print_sweep_results(results):
    print("Sweep Results: Rigid Fraction vs Performance")
    print(f"  {'Rigid%':<8} {'Avg Perf':<10} {'Steady':<10} {'Trans Cost':<12} {'Recovery':<10}")
    print(f"  {'-'*50}")
    for r in results:
        print(f"  {r['rigid_fraction']:>5.0%}   "
              f"{r['avg_performance']:.4f}    "
              f"{r['steady_state_performance']:.4f}    "
              f"{r['avg_transition_cost']:+.4f}     "
              f"{r['avg_recovery_ticks']:>5.1f}")
    print()

    # Find optimal
    best = max(results, key=lambda r: r["avg_performance"])
    print(f"  Optimal rigid fraction: {best['rigid_fraction']:.0%} "
          f"(avg performance: {best['avg_performance']:.4f})")
    print()


def main():
    args = parse_args()

    if args.sweep:
        # Sweep mode
        if not args.quiet:
            print("Running sweep over rigid fraction values...")
            print(f"  Steps: {args.sweep_steps}, Ticks per run: {args.ticks}")
            print()

        results = run_sweep(
            levels=args.levels,
            branching_factor=args.branching_factor,
            ticks=args.ticks,
            stability=args.stability,
            experience_weight=args.experience_weight,
            noise=args.noise,
            mode=args.mode,
            seed=args.seed,
            steps=args.sweep_steps,
        )

        if not args.quiet:
            print_sweep_results(results)

        if args.json:
            with open(args.json, "w") as f:
                json.dump({"sweep": results}, f, indent=2)
            if not args.quiet:
                print(f"Sweep results saved to {args.json}")

        if args.csv:
            with open(args.csv, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            if not args.quiet:
                print(f"Sweep results saved to {args.csv}")

    else:
        # Single run mode
        sim = Simulation(
            levels=args.levels,
            branching_factor=args.branching_factor,
            ticks=args.ticks,
            stability=args.stability,
            rigid_fraction=args.rigid_fraction,
            experience_weight=args.experience_weight,
            noise=args.noise,
            mode=args.mode,
            seed=args.seed,
        )

        total_agents = sim.hierarchy.total_agents()
        level_sizes = [sim.hierarchy.level_size(l)
                       for l in range(sim.hierarchy.levels)]

        if not args.quiet:
            print_header(args, total_agents, level_sizes)

        sim.run()

        if not args.quiet:
            print_level_composition(sim)
            print_performance_summary(sim)

        if args.csv:
            sim.to_csv(args.csv)
            if not args.quiet:
                print(f"Results saved to {args.csv}")

        if args.json:
            data = sim.to_json()
            with open(args.json, "w") as f:
                json.dump(data, f, indent=2)
            if not args.quiet:
                print(f"Results saved to {args.json}")


if __name__ == "__main__":
    main()
