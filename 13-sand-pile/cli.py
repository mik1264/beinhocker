#!/usr/bin/env python3
"""
CLI for the Bak-Tang-Wiesenfeld Sandpile simulation.

Usage:
  python3 cli.py --ticks 10000 --seed 42
  python3 cli.py --ticks 50000 --grid-size 100 --seed 42
  python3 cli.py --ticks 10000 --threshold 8 --seed 42
"""

import argparse
import sys
import os

from simulation import SandPile, AvalancheEvent


def progress_callback(tick: int, event: AvalancheEvent):
    """Print progress during simulation."""
    marker = ""
    if event.size >= 10:
        marker = f"  *** AVALANCHE size={event.size} duration={event.duration} ***"
    if tick % 1000 == 0 or event.size >= 50:
        print(f"  tick {tick:7d}  grains_on_grid={event.size:5d}{marker}")


def run_simulation(args):
    """Run the sandpile simulation."""
    print(f"Bak-Tang-Wiesenfeld Sandpile Simulation")
    print(f"  Grid size: {args.grid_size}x{args.grid_size}")
    print(f"  Ticks (grain drops): {args.ticks}")
    print(f"  Critical threshold: {args.threshold}")
    print(f"  Seed: {args.seed}")
    print()

    pile = SandPile(
        grid_size=args.grid_size,
        threshold=args.threshold,
        seed=args.seed,
    )

    print("Running simulation...")
    pile.run(args.ticks, callback=progress_callback)

    # Summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    n_cells = args.grid_size * args.grid_size
    total_avalanches = len(pile.avalanches)
    sizes = [a.size for a in pile.avalanches]
    durations = [a.duration for a in pile.avalanches]

    print(f"  Total ticks: {pile.tick}")
    print(f"  Total grains added: {pile.total_grains_added}")
    print(f"  Total grains on grid: {pile.total_grains}")
    print(f"  Total grains lost (edges): {pile.total_grains_lost}")
    print(f"  Mean height: {pile.total_grains / n_cells:.3f}")
    print(f"  Grid cells: {n_cells}")
    print()

    print(f"  Total avalanches (size > 0): {total_avalanches}")
    print(f"  Fraction of drops causing avalanche: {total_avalanches / pile.tick:.3f}")
    if sizes:
        print(f"  Mean avalanche size: {sum(sizes) / len(sizes):.2f}")
        print(f"  Max avalanche size: {max(sizes)}")
        print(f"  Median avalanche size: {sorted(sizes)[len(sizes) // 2]}")
        print()
        print(f"  Mean avalanche duration: {sum(durations) / len(durations):.2f}")
        print(f"  Max avalanche duration: {max(durations)}")

    # Power-law exponent
    alpha = pile.estimate_power_law_exponent()
    if alpha:
        print(f"\n  Power-law exponent (MLE): {alpha:.3f}")
        print(f"  (Theory predicts ~1.0-1.2 for 2D BTW model)")

    # Height distribution
    height_dist = pile.get_height_distribution()
    print(f"\n  Height distribution:")
    for h, count in sorted(height_dist.items()):
        pct = 100 * count / n_cells
        bar = "#" * min(int(pct), 50)
        print(f"    height {h}: {count:6d} ({pct:5.1f}%) {bar}")

    # Avalanche size distribution (top entries)
    size_dist = pile.get_avalanche_size_distribution()
    if size_dist:
        print(f"\n  Avalanche size distribution (top 20 sizes):")
        items = sorted(size_dist.items())
        # Show first 15 and last 5
        display_items = items[:15]
        if len(items) > 20:
            display_items += [("...", "")]
            display_items += items[-5:]
        elif len(items) > 15:
            display_items = items[:20]

        for size, count in display_items:
            if size == "...":
                print(f"    ...")
            else:
                bar = "#" * min(count, 50)
                print(f"    size {size:5d}: {count:5d} {bar}")

    # Duration distribution
    dur_dist = pile.get_avalanche_duration_distribution()
    if dur_dist:
        print(f"\n  Avalanche duration distribution:")
        for dur, count in sorted(dur_dist.items())[:15]:
            bar = "#" * min(count, 50)
            print(f"    duration {dur:3d}: {count:5d} {bar}")

    # Largest avalanches
    if pile.avalanches:
        print(f"\n  Top 10 largest avalanches:")
        sorted_avals = sorted(pile.avalanches, key=lambda a: a.size, reverse=True)[:10]
        for a in sorted_avals:
            print(f"    tick {a.tick:7d}: size={a.size:5d}  duration={a.duration:3d}  "
                  f"drop=({a.drop_row},{a.drop_col})  lost={a.grains_lost}")

    # Save outputs
    if args.output:
        pile.save_csv(args.output)
        print(f"\n  CSV saved to: {args.output}")

    json_path = args.json
    if not json_path:
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "results.json",
        )
    pile.save_json(json_path)
    print(f"  JSON saved to: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bak-Tang-Wiesenfeld Sandpile Simulation (Self-Organized Criticality)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticks 10000 --seed 42
  %(prog)s --ticks 50000 --grid-size 100 --seed 42
  %(prog)s --ticks 10000 --threshold 8 --seed 42
        """,
    )

    parser.add_argument("--grid-size", type=int, default=50,
                        help="Grid dimension NxN (default: 50)")
    parser.add_argument("--ticks", type=int, default=10000,
                        help="Number of grain drops (default: 10000)")
    parser.add_argument("--threshold", type=int, default=4,
                        help="Critical height for toppling (default: 4)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", type=str, default=None,
                        help="Output JSON file path (default: results.json)")

    args = parser.parse_args()
    run_simulation(args)


if __name__ == "__main__":
    main()
