#!/usr/bin/env python3
"""
CLI for the Predator-Prey / Lotka-Volterra simulation.

Usage:
  python3 cli.py --ticks 500 --seed 42                    (spatial agent-based)
  python3 cli.py --ode --ticks 500                         (classic ODE)
  python3 cli.py --ticks 500 --grid-size 100 --seed 42    (larger spatial world)
"""

import argparse
import sys
import os

from simulation import (
    LotkaVolterraODE, ODEConfig,
    PredatorPreySpatial, SpatialConfig,
)


def ode_callback(tick: int, prey: float, predators: float):
    if tick % 50 == 0:
        print(f"  t={tick:5d}  prey={prey:8.2f}  predators={predators:8.2f}")


_extinction_reported = set()

def spatial_callback(tick: int, prey: int, predators: int):
    global _extinction_reported
    marker = ""
    if prey == 0 and "prey" not in _extinction_reported:
        marker = "  *** PREY EXTINCT ***"
        _extinction_reported.add("prey")
    elif predators == 0 and "predators" not in _extinction_reported:
        marker = "  *** PREDATORS EXTINCT ***"
        _extinction_reported.add("predators")
    if tick % 50 == 0 or marker:
        print(f"  tick {tick:5d}  prey={prey:5d}  predators={predators:5d}{marker}")


def run_ode(args):
    """Run the classic ODE Lotka-Volterra model."""
    print("Lotka-Volterra ODE Model")
    print(f"  alpha (prey birth):      {args.alpha}")
    print(f"  beta (predation rate):   {args.beta}")
    print(f"  delta (pred efficiency): {args.delta}")
    print(f"  gamma (pred death rate): {args.gamma}")
    print(f"  initial prey:            {args.ode_prey}")
    print(f"  initial predators:       {args.ode_predators}")
    print(f"  ticks:                   {args.ticks}")
    print()

    config = ODEConfig(
        alpha=args.alpha,
        beta=args.beta,
        delta=args.delta,
        gamma=args.gamma,
        initial_prey=args.ode_prey,
        initial_predators=args.ode_predators,
        ticks=args.ticks,
    )

    sim = LotkaVolterraODE(config)
    print("Running ODE simulation...")
    sim.run(callback=ode_callback)

    # Summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    prey_vals = [r.prey for r in sim.history]
    pred_vals = [r.predators for r in sim.history]

    print(f"  Prey   -- min: {min(prey_vals):8.2f}  max: {max(prey_vals):8.2f}  final: {prey_vals[-1]:8.2f}")
    print(f"  Preds  -- min: {min(pred_vals):8.2f}  max: {max(pred_vals):8.2f}  final: {pred_vals[-1]:8.2f}")

    period = sim.detect_period()
    if period:
        print(f"  Oscillation period: {period:.2f} time units")
    else:
        print(f"  Oscillation period: not detected")

    # Save
    json_path = args.json or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results.json"
    )
    sim.save_json(json_path)
    print(f"\n  JSON saved to: {json_path}")

    if args.output:
        sim.save_csv(args.output)
        print(f"  CSV saved to: {args.output}")


def run_spatial(args):
    """Run the spatial agent-based model."""
    print("Predator-Prey Spatial Agent-Based Model")
    print(f"  grid size:            {args.grid_size}x{args.grid_size}")
    print(f"  initial prey:         {args.initial_prey}")
    print(f"  initial predators:    {args.initial_predators}")
    print(f"  prey reproduce:       {args.prey_reproduce}")
    print(f"  predator reproduce:   {args.predator_reproduce}")
    print(f"  predator starve:      {args.predator_starve}")
    print(f"  grass regrow time:    {args.grass_regrow}")
    print(f"  ticks:                {args.ticks}")
    print(f"  seed:                 {args.seed}")
    print()

    config = SpatialConfig(
        grid_size=args.grid_size,
        initial_prey=args.initial_prey,
        initial_predators=args.initial_predators,
        grass_regrow_time=args.grass_regrow,
        prey_reproduce=args.prey_reproduce,
        predator_reproduce=args.predator_reproduce,
        predator_starve=args.predator_starve,
        seed=args.seed,
        ticks=args.ticks,
    )

    sim = PredatorPreySpatial(config)
    print("Running spatial simulation...")
    global _extinction_reported
    _extinction_reported = set()
    sim.run(callback=spatial_callback)

    # Summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    prey_vals = [r.prey_count for r in sim.history]
    pred_vals = [r.predator_count for r in sim.history]
    grass_vals = [r.grass_fraction for r in sim.history]

    final = sim.history[-1]
    print(f"  Final tick:   {final.tick}")
    print(f"  Final prey:   {final.prey_count}")
    print(f"  Final preds:  {final.predator_count}")
    print(f"  Final grass:  {final.grass_fraction:.2%}")
    print()

    if max(prey_vals) > 0:
        print(f"  Prey   -- min: {min(prey_vals):5d}  max: {max(prey_vals):5d}")
    else:
        print(f"  Prey   -- EXTINCT from start")

    if max(pred_vals) > 0:
        print(f"  Preds  -- min: {min(pred_vals):5d}  max: {max(pred_vals):5d}")
    else:
        print(f"  Preds  -- EXTINCT from start")

    print(f"  Grass  -- min: {min(grass_vals):.2%}  max: {max(grass_vals):.2%}")

    # Check for extinctions
    prey_extinct_tick = None
    pred_extinct_tick = None
    for r in sim.history:
        if r.prey_count == 0 and prey_extinct_tick is None:
            prey_extinct_tick = r.tick
        if r.predator_count == 0 and pred_extinct_tick is None:
            pred_extinct_tick = r.tick

    if prey_extinct_tick is not None:
        print(f"\n  Prey went extinct at tick {prey_extinct_tick}")
    if pred_extinct_tick is not None:
        print(f"  Predators went extinct at tick {pred_extinct_tick}")

    period = sim.detect_period()
    if period:
        print(f"\n  Estimated oscillation period: {period:.1f} ticks")
    else:
        print(f"\n  Oscillation period: not detected (may need more ticks or population extinct)")

    # Save
    json_path = args.json or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results.json"
    )
    sim.save_json(json_path)
    print(f"\n  JSON saved to: {json_path}")

    if args.output:
        sim.save_csv(args.output)
        print(f"  CSV saved to: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="Predator-Prey / Lotka-Volterra Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 500 --seed 42              (spatial, default)
  %(prog)s --ode --ticks 500                  (classic ODE)
  %(prog)s --ticks 500 --grid-size 100        (larger spatial world)
  %(prog)s --ticks 500 --initial-predators 50 (more predators)
        """,
    )

    # Mode
    parser.add_argument("--ode", action="store_true", default=False,
                        help="Run classic ODE model instead of spatial")

    # Common
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of ticks to simulate (default: 500)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    # Spatial parameters
    parser.add_argument("--grid-size", type=int, default=50,
                        help="Grid size for spatial model (default: 50)")
    parser.add_argument("--initial-prey", type=int, default=200,
                        help="Initial prey count (default: 200)")
    parser.add_argument("--initial-predators", type=int, default=30,
                        help="Initial predator count (default: 30)")
    parser.add_argument("--prey-reproduce", type=float, default=0.08,
                        help="Prey reproduction probability (default: 0.08)")
    parser.add_argument("--predator-reproduce", type=float, default=0.02,
                        help="Predator reproduction probability (default: 0.02)")
    parser.add_argument("--predator-starve", type=int, default=10,
                        help="Predator initial energy / starvation threshold (default: 10)")
    parser.add_argument("--grass-regrow", type=int, default=8,
                        help="Ticks for grass to regrow (default: 8)")

    # ODE parameters
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="ODE: prey birth rate (default: 1.0)")
    parser.add_argument("--beta", type=float, default=0.1,
                        help="ODE: predation rate (default: 0.1)")
    parser.add_argument("--delta", type=float, default=0.075,
                        help="ODE: predator efficiency (default: 0.075)")
    parser.add_argument("--gamma", type=float, default=1.5,
                        help="ODE: predator death rate (default: 1.5)")
    parser.add_argument("--ode-prey", type=float, default=40.0,
                        help="ODE: initial prey population (default: 40.0)")
    parser.add_argument("--ode-predators", type=float, default=9.0,
                        help="ODE: initial predator population (default: 9.0)")

    # Output
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", type=str, default=None,
                        help="Output JSON file path (default: results.json)")

    args = parser.parse_args()

    if args.ode:
        run_ode(args)
    else:
        run_spatial(args)


if __name__ == "__main__":
    main()
