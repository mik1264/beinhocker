"""
Bak-Tang-Wiesenfeld Abelian Sandpile Model

The canonical model of self-organized criticality (SOC). A 2D grid accumulates
sand grains one at a time. When any cell reaches a critical threshold, it topples:
it loses grains equal to the threshold, distributing one to each neighbor. Grains
that fall off the grid edge are lost. Topplings can cascade, and the resulting
avalanche size distribution follows a power law -- without any parameter tuning.

This is the hallmark of SOC: the system drives itself to the critical state.

References:
  - Bak, Tang & Wiesenfeld, "Self-organized criticality" (PRL, 1987)
  - Beinhocker, "The Origin of Wealth" (2006), Chapter 8, p.178
"""

import random
import math
import csv
import json
import collections
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AvalancheEvent:
    """Record of a single avalanche triggered by one grain drop."""
    tick: int
    drop_row: int
    drop_col: int
    size: int           # total number of topplings
    duration: int       # number of cascade rounds until stable
    grains_lost: int    # grains that fell off the edge


@dataclass
class TickRecord:
    """Snapshot of the system after each grain drop."""
    tick: int
    total_grains: int
    mean_height: float
    max_height: int
    avalanche_size: int
    avalanche_duration: int
    grains_lost: int


class SandPile:
    """
    Bak-Tang-Wiesenfeld Abelian sandpile on a 2D grid.

    Each cell holds an integer number of sand grains. When a cell reaches
    the critical threshold (default 4), it topples: loses 4 grains and
    each of its 4 neighbors gains 1. Boundary grains are lost.
    """

    def __init__(
        self,
        grid_size: int = 50,
        threshold: int = 4,
        seed: Optional[int] = None,
    ):
        self.grid_size = grid_size
        self.threshold = threshold
        self.rng = random.Random(seed)

        # Grid of sand heights (integers)
        self.heights = [[0] * grid_size for _ in range(grid_size)]

        self.tick = 0
        self.total_grains = 0       # grains currently on the grid
        self.total_grains_added = 0  # cumulative grains dropped
        self.total_grains_lost = 0   # cumulative grains fallen off edges

        self.history: list[TickRecord] = []
        self.avalanches: list[AvalancheEvent] = []

        # Neighbor offsets (4-connected)
        self._neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.grid_size and 0 <= c < self.grid_size

    def add_grain(self, row: int, col: int) -> tuple[int, int, int]:
        """
        Add one grain to the specified cell and resolve any cascading topplings.

        Returns (avalanche_size, avalanche_duration, grains_lost).
        """
        self.heights[row][col] += 1
        self.total_grains += 1
        self.total_grains_added += 1

        # Resolve topplings
        avalanche_size = 0
        avalanche_duration = 0
        grains_lost = 0

        # Find all cells that need to topple
        to_topple = set()
        if self.heights[row][col] >= self.threshold:
            to_topple.add((row, col))

        while to_topple:
            avalanche_duration += 1
            # All unstable cells topple simultaneously in this round
            next_topple = set()

            for r, c in to_topple:
                # A cell may have accumulated grains from multiple neighbors;
                # it can topple multiple times in a single round
                while self.heights[r][c] >= self.threshold:
                    avalanche_size += 1
                    # Standard BTW toppling: lose threshold grains,
                    # distribute one to each of threshold neighbor
                    # directions (cycling through the 4 cardinal dirs).
                    # Grains sent off the grid edge are lost.
                    self.heights[r][c] -= self.threshold
                    dirs = self._neighbors[:self.threshold] if self.threshold <= 4 else self._neighbors

                    for i in range(self.threshold):
                        dr, dc = self._neighbors[i % 4]
                        nr, nc = r + dr, c + dc
                        if self._in_bounds(nr, nc):
                            self.heights[nr][nc] += 1
                            if self.heights[nr][nc] >= self.threshold:
                                next_topple.add((nr, nc))
                        else:
                            # Grain falls off the edge
                            grains_lost += 1
                            self.total_grains -= 1
                            self.total_grains_lost += 1

            to_topple = next_topple

        return avalanche_size, avalanche_duration, grains_lost

    def drop_random_grain(self) -> tuple[int, int, int, int, int]:
        """
        Drop one grain on a random cell and resolve cascades.

        Returns (row, col, avalanche_size, avalanche_duration, grains_lost).
        """
        row = self.rng.randint(0, self.grid_size - 1)
        col = self.rng.randint(0, self.grid_size - 1)
        size, duration, lost = self.add_grain(row, col)
        return row, col, size, duration, lost

    def step(self) -> AvalancheEvent:
        """
        Execute one tick: drop a random grain and record the result.
        """
        self.tick += 1
        row, col, size, duration, lost = self.drop_random_grain()

        event = AvalancheEvent(
            tick=self.tick,
            drop_row=row,
            drop_col=col,
            size=size,
            duration=duration,
            grains_lost=lost,
        )
        if size > 0:
            self.avalanches.append(event)

        # Compute stats
        max_h = 0
        total = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                h = self.heights[r][c]
                total += h
                if h > max_h:
                    max_h = h

        n_cells = self.grid_size * self.grid_size
        record = TickRecord(
            tick=self.tick,
            total_grains=total,
            mean_height=total / n_cells,
            max_height=max_h,
            avalanche_size=size,
            avalanche_duration=duration,
            grains_lost=lost,
        )
        self.history.append(record)

        return event

    def run(self, ticks: int, callback=None) -> list[TickRecord]:
        """Run simulation for given number of grain drops."""
        for t in range(ticks):
            event = self.step()
            if callback:
                callback(self.tick, event)
        return self.history

    # --- Statistics ---

    def get_avalanche_size_distribution(self) -> dict[int, int]:
        """Frequency distribution of avalanche sizes (excluding size 0)."""
        dist: dict[int, int] = {}
        for a in self.avalanches:
            dist[a.size] = dist.get(a.size, 0) + 1
        return dict(sorted(dist.items()))

    def get_avalanche_duration_distribution(self) -> dict[int, int]:
        """Frequency distribution of avalanche durations."""
        dist: dict[int, int] = {}
        for a in self.avalanches:
            dist[a.duration] = dist.get(a.duration, 0) + 1
        return dict(sorted(dist.items()))

    def estimate_power_law_exponent(self) -> Optional[float]:
        """
        Estimate the power-law exponent for avalanche sizes using
        maximum likelihood estimation (Clauset et al., 2009).

        For a discrete power-law P(x) ~ x^(-alpha):
            alpha = 1 + n * [ sum( ln(x_i / (x_min - 0.5)) ) ]^(-1)

        Returns None if insufficient data.
        """
        sizes = [a.size for a in self.avalanches if a.size > 0]
        if len(sizes) < 10:
            return None

        x_min = 1
        filtered = [s for s in sizes if s >= x_min]
        if len(filtered) < 10:
            return None

        n = len(filtered)
        log_sum = sum(math.log(x / (x_min - 0.5)) for x in filtered)
        if log_sum == 0:
            return None

        alpha = 1.0 + n / log_sum
        return alpha

    def get_height_distribution(self) -> dict[int, int]:
        """Frequency distribution of cell heights."""
        dist: dict[int, int] = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                h = self.heights[r][c]
                dist[h] = dist.get(h, 0) + 1
        return dict(sorted(dist.items()))

    # --- Export ---

    def get_state_json(self) -> dict:
        """Export current grid state as JSON-serializable dict."""
        return {
            "tick": self.tick,
            "grid_size": self.grid_size,
            "threshold": self.threshold,
            "total_grains": self.total_grains,
            "total_grains_added": self.total_grains_added,
            "total_grains_lost": self.total_grains_lost,
            "heights": self.heights,
            "height_distribution": self.get_height_distribution(),
            "stats": {
                "mean_height": self.total_grains / (self.grid_size ** 2) if self.grid_size > 0 else 0,
                "max_height": max(max(row) for row in self.heights) if self.grid_size > 0 else 0,
                "total_avalanches": len(self.avalanches),
                "power_law_exponent": self.estimate_power_law_exponent(),
            },
        }

    def get_history_json(self) -> list[dict]:
        """Export history as JSON-serializable list."""
        return [
            {
                "tick": r.tick,
                "total_grains": r.total_grains,
                "mean_height": round(r.mean_height, 4),
                "max_height": r.max_height,
                "avalanche_size": r.avalanche_size,
                "avalanche_duration": r.avalanche_duration,
                "grains_lost": r.grains_lost,
            }
            for r in self.history
        ]

    def save_csv(self, filepath: str):
        """Save history to CSV file."""
        if not self.history:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "total_grains", "mean_height", "max_height",
                "avalanche_size", "avalanche_duration", "grains_lost",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, r.total_grains, f"{r.mean_height:.4f}",
                    r.max_height, r.avalanche_size, r.avalanche_duration,
                    r.grains_lost,
                ])

    def save_json(self, filepath: str):
        """Save full state and history to JSON file."""
        data = {
            "params": {
                "grid_size": self.grid_size,
                "threshold": self.threshold,
            },
            "state": self.get_state_json(),
            "history": self.get_history_json(),
            "avalanche_size_distribution": self.get_avalanche_size_distribution(),
            "avalanche_duration_distribution": self.get_avalanche_duration_distribution(),
            "power_law_exponent": self.estimate_power_law_exponent(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
