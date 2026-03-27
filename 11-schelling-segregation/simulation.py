"""
Schelling Segregation Model Simulation
Based on Thomas Schelling's "Dynamic Models of Segregation" (1971)
As discussed in Beinhocker's "The Origin of Wealth" (2006) -- emergence context

Implements the classic Schelling model:
- 2D grid with two agent types (A and B) and empty cells
- Each agent has a tolerance threshold: minimum fraction of same-type neighbors to be happy
- Unhappy agents relocate to random empty cells
- Key insight: even mild individual preferences (30%) produce extreme macro-level segregation
- Tracks: segregation index, happiness rate, moves per tick, cluster sizes
"""

import random
from dataclasses import dataclass, field
from typing import Optional
from collections import deque


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class SchellingConfig:
    """Configuration for a Schelling segregation simulation run."""
    grid_size: int = 50
    density: float = 0.7          # fraction of cells occupied
    threshold: float = 0.3        # minimum fraction of same-type neighbors to be happy
    ratio: float = 0.5            # fraction of agents that are type A
    max_ticks: int = 200
    bounded: bool = False         # True = bounded edges, False = torus (wrap-around)
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """A Schelling agent with a type and tolerance threshold."""
    agent_id: int
    x: int
    y: int
    agent_type: str              # 'A' or 'B'
    threshold: float             # minimum fraction of same-type neighbors to be happy
    happy: bool = True


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the Schelling segregation simulation."""

    def __init__(self, config: Optional[SchellingConfig] = None, **kwargs):
        if config is None:
            config = SchellingConfig(**kwargs)
        self.config = config

        if config.seed is not None:
            random.seed(config.seed)

        self.tick = 0
        self.grid_size = config.grid_size

        # Grid stores agent references or None
        self.grid: list[list[Optional[Agent]]] = [
            [None for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        self.agents: list[Agent] = []
        self.empty_cells: list[tuple[int, int]] = []

        self._place_initial_agents()

        # Compute initial state
        self._update_happiness()

        # Metrics over time
        self.segregation_history: list[float] = [self._compute_segregation_index()]
        self.happiness_history: list[float] = [self._compute_happiness_rate()]
        self.moves_history: list[int] = [0]
        self.interface_density_history: list[float] = [self._compute_interface_density()]
        self.largest_cluster_history: list[int] = [self._compute_largest_cluster()]

    # -------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------

    def _place_initial_agents(self):
        """Place agents randomly on the grid according to density and ratio."""
        cfg = self.config
        total_cells = cfg.grid_size * cfg.grid_size
        num_agents = int(total_cells * cfg.density)
        num_a = int(num_agents * cfg.ratio)
        num_b = num_agents - num_a

        # Build list of all positions and shuffle
        all_positions = [(x, y) for y in range(cfg.grid_size) for x in range(cfg.grid_size)]
        random.shuffle(all_positions)

        agent_id = 0
        # Place type A agents
        for i in range(num_a):
            x, y = all_positions[i]
            agent = Agent(agent_id=agent_id, x=x, y=y, agent_type='A',
                          threshold=cfg.threshold)
            self.grid[y][x] = agent
            self.agents.append(agent)
            agent_id += 1

        # Place type B agents
        for i in range(num_a, num_a + num_b):
            x, y = all_positions[i]
            agent = Agent(agent_id=agent_id, x=x, y=y, agent_type='B',
                          threshold=cfg.threshold)
            self.grid[y][x] = agent
            self.agents.append(agent)
            agent_id += 1

        # Track empty cells
        for i in range(num_agents, len(all_positions)):
            self.empty_cells.append(all_positions[i])

    # -------------------------------------------------------------------
    # Neighbor logic
    # -------------------------------------------------------------------

    def _get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Get coordinates of 8 surrounding neighbors (Moore neighborhood)."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.config.bounded:
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        neighbors.append((nx, ny))
                else:
                    # Torus wrap-around
                    neighbors.append((nx % self.grid_size, ny % self.grid_size))
        return neighbors

    def _is_happy(self, agent: Agent) -> bool:
        """Check if an agent is happy based on its neighborhood."""
        neighbors = self._get_neighbors(agent.x, agent.y)
        same = 0
        total = 0
        for nx, ny in neighbors:
            occupant = self.grid[ny][nx]
            if occupant is not None:
                total += 1
                if occupant.agent_type == agent.agent_type:
                    same += 1
        if total == 0:
            return True  # No neighbors = happy (no dissatisfaction trigger)
        return (same / total) >= agent.threshold

    def _update_happiness(self):
        """Recompute happiness status for all agents."""
        for agent in self.agents:
            agent.happy = self._is_happy(agent)

    # -------------------------------------------------------------------
    # Step
    # -------------------------------------------------------------------

    def step(self) -> int:
        """Execute one time step. Returns number of moves made."""
        moves = 0

        # Shuffle agent order for fairness
        random.shuffle(self.agents)

        for agent in self.agents:
            if agent.happy:
                continue
            if not self.empty_cells:
                continue

            # Pick a random empty cell
            idx = random.randint(0, len(self.empty_cells) - 1)
            new_x, new_y = self.empty_cells[idx]

            # Move agent: vacate old cell
            old_x, old_y = agent.x, agent.y
            self.grid[old_y][old_x] = None

            # Place at new cell
            agent.x = new_x
            agent.y = new_y
            self.grid[new_y][new_x] = agent

            # Update empty cells list
            self.empty_cells[idx] = (old_x, old_y)

            moves += 1

        # Re-evaluate happiness after all moves
        self._update_happiness()

        self.tick += 1

        # Record metrics
        self.segregation_history.append(self._compute_segregation_index())
        self.happiness_history.append(self._compute_happiness_rate())
        self.moves_history.append(moves)
        self.interface_density_history.append(self._compute_interface_density())
        self.largest_cluster_history.append(self._compute_largest_cluster())

        return moves

    def run(self, progress_callback=None):
        """Run the full simulation."""
        for t in range(self.config.max_ticks):
            moves = self.step()
            if progress_callback and t % 10 == 0:
                progress_callback(t, self.config.max_ticks)
            # Early termination if everyone is happy and no moves
            if moves == 0:
                break

    # -------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------

    def _compute_segregation_index(self) -> float:
        """Average fraction of same-type neighbors across all agents.
        1.0 = perfectly segregated, ratio = perfectly mixed."""
        if not self.agents:
            return 0.0
        total_frac = 0.0
        count = 0
        for agent in self.agents:
            neighbors = self._get_neighbors(agent.x, agent.y)
            same = 0
            occupied = 0
            for nx, ny in neighbors:
                occupant = self.grid[ny][nx]
                if occupant is not None:
                    occupied += 1
                    if occupant.agent_type == agent.agent_type:
                        same += 1
            if occupied > 0:
                total_frac += same / occupied
                count += 1
        return total_frac / count if count > 0 else 0.0

    def _compute_happiness_rate(self) -> float:
        """Fraction of agents that are happy."""
        if not self.agents:
            return 1.0
        happy_count = sum(1 for a in self.agents if a.happy)
        return happy_count / len(self.agents)

    def _compute_interface_density(self) -> float:
        """Fraction of neighbor-pairs that are of different types (boundary density).
        Lower = more segregated."""
        different = 0
        total = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                occupant = self.grid[y][x]
                if occupant is None:
                    continue
                # Check right and down neighbors only (to avoid double-counting)
                for dx, dy in [(1, 0), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if self.config.bounded:
                        if nx >= self.grid_size or ny >= self.grid_size:
                            continue
                    else:
                        nx %= self.grid_size
                        ny %= self.grid_size
                    neighbor = self.grid[ny][nx]
                    if neighbor is not None:
                        total += 1
                        if neighbor.agent_type != occupant.agent_type:
                            different += 1
        return different / total if total > 0 else 0.0

    def _compute_largest_cluster(self) -> int:
        """Find the largest contiguous cluster of same-type agents using BFS."""
        visited = [[False] * self.grid_size for _ in range(self.grid_size)]
        largest = 0

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if visited[y][x]:
                    continue
                occupant = self.grid[y][x]
                if occupant is None:
                    visited[y][x] = True
                    continue

                # BFS from this cell
                agent_type = occupant.agent_type
                queue = deque()
                queue.append((x, y))
                visited[y][x] = True
                cluster_size = 0

                while queue:
                    cx, cy = queue.popleft()
                    cluster_size += 1
                    for nx, ny in self._get_neighbors(cx, cy):
                        if visited[ny][nx]:
                            continue
                        neighbor = self.grid[ny][nx]
                        if neighbor is not None and neighbor.agent_type == agent_type:
                            visited[ny][nx] = True
                            queue.append((nx, ny))

                largest = max(largest, cluster_size)

        return largest

    # -------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        num_a = sum(1 for a in self.agents if a.agent_type == 'A')
        num_b = sum(1 for a in self.agents if a.agent_type == 'B')

        return {
            'num_ticks': self.tick,
            'grid_size': self.config.grid_size,
            'density': self.config.density,
            'threshold': self.config.threshold,
            'ratio': self.config.ratio,
            'total_agents': len(self.agents),
            'type_a_count': num_a,
            'type_b_count': num_b,
            'empty_cells': len(self.empty_cells),
            'final_segregation_index': self.segregation_history[-1],
            'initial_segregation_index': self.segregation_history[0],
            'segregation_change': self.segregation_history[-1] - self.segregation_history[0],
            'final_happiness_rate': self.happiness_history[-1],
            'total_moves': sum(self.moves_history),
            'peak_moves_per_tick': max(self.moves_history),
            'interface_density': self.interface_density_history[-1],
            'largest_cluster': self.largest_cluster_history[-1],
            'converged_at_tick': self._convergence_tick(),
        }

    def _convergence_tick(self) -> Optional[int]:
        """Return the tick at which the system first reached 100% happiness, or None."""
        for i, h in enumerate(self.happiness_history):
            if h >= 1.0:
                return i
        return None

    def get_timeseries_data(self) -> dict:
        """Return time series data suitable for CSV export."""
        n = len(self.segregation_history)
        return {
            'tick': list(range(n)),
            'segregation_index': self.segregation_history,
            'happiness_rate': self.happiness_history,
            'moves': self.moves_history,
            'interface_density': self.interface_density_history,
            'largest_cluster': self.largest_cluster_history,
        }

    def get_grid_state(self) -> dict:
        """Return current grid state for visualization."""
        grid_data = []
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                occupant = self.grid[y][x]
                if occupant is None:
                    row.append(0)  # empty
                elif occupant.agent_type == 'A':
                    row.append(1)  # type A
                else:
                    row.append(2)  # type B
            grid_data.append(row)

        agents_data = [
            {
                'id': a.agent_id,
                'x': a.x,
                'y': a.y,
                'type': a.agent_type,
                'happy': a.happy,
            }
            for a in self.agents
        ]

        return {
            'grid': grid_data,
            'agents': agents_data,
            'tick': self.tick,
        }


if __name__ == '__main__':
    print("Running Schelling Segregation simulation...")
    config = SchellingConfig(
        grid_size=50,
        density=0.7,
        threshold=0.3,
        max_ticks=200,
        seed=42,
    )
    sim = Simulation(config=config)
    sim.run(progress_callback=lambda t, n: print(f"  tick {t}/{n}"))
    stats = sim.get_statistics()
    print("\nResults:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
