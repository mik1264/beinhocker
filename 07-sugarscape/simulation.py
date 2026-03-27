"""
Sugarscape Simulation
Based on Epstein & Axtell's "Growing Artificial Societies" (1996)
As discussed in Beinhocker's "The Origin of Wealth" (2006)

Implements the classic Sugarscape model with:
- 2D grid with sugar landscape (two Gaussian mountain peaks)
- Heterogeneous agents with varying vision, metabolism, and endowment
- Movement rule: look in 4 cardinal directions, move to richest empty cell
- Configurable sugar regrowth (instant or gradual)
- Agent death when sugar reserves reach 0
- Optional reproduction when sugar exceeds threshold
- Optional pollution and cultural tags
- Tracks population, Gini coefficient, wealth distribution, landscape state
"""

import random
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class SugarscapeConfig:
    """Configuration for a Sugarscape simulation run."""
    grid_size: int = 50
    num_agents: int = 400
    max_ticks: int = 500

    # Sugar landscape
    peak1_x: float = 15.0
    peak1_y: float = 15.0
    peak1_height: float = 4.0
    peak1_radius: float = 20.0
    peak2_x: float = 35.0
    peak2_y: float = 35.0
    peak2_height: float = 4.0
    peak2_radius: float = 20.0

    # Agent attributes (uniform random ranges)
    vision_min: int = 1
    vision_max: int = 6
    metabolism_min: int = 1
    metabolism_max: int = 4
    endowment_min: int = 5
    endowment_max: int = 25

    # Sugar regrowth
    regrowth_rate: int = 1      # units per tick (0 = instant regrowth to capacity)
    max_sugar_level: int = 4    # maximum sugar capacity at any cell

    # Reproduction
    reproduction: bool = False
    reproduction_threshold: float = 50.0   # sugar needed to reproduce
    max_agent_age: int = 0                 # 0 = no age limit

    # Pollution
    pollution: bool = False
    pollution_production: float = 0.0      # pollution per sugar gathered
    pollution_consumption: float = 0.0     # pollution per sugar consumed
    pollution_diffusion_rate: float = 0.0  # fraction of pollution that spreads

    # Cultural tags
    cultural_tags: bool = False
    num_cultural_bits: int = 11            # number of cultural tag bits

    # Reproducibility
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class Agent:
    """A Sugarscape agent that gathers and consumes sugar to survive."""

    _next_id = 0

    def __init__(self, x: int, y: int, vision: int, metabolism: int,
                 sugar: float, config: SugarscapeConfig):
        self.id = Agent._next_id
        Agent._next_id += 1
        self.x = x
        self.y = y
        self.vision = vision
        self.metabolism = metabolism
        self.sugar = sugar
        self.initial_sugar = sugar
        self.age = 0
        self.alive = True
        self.max_age = 0  # 0 means no age limit

        # Cultural tags (binary string)
        if config.cultural_tags:
            self.cultural_tags = [random.randint(0, 1)
                                  for _ in range(config.num_cultural_bits)]
        else:
            self.cultural_tags = None

        # Track wealth over time (sampled, not every tick)
        self.wealth_history = []

    @property
    def tribe(self) -> Optional[int]:
        """Determine tribe from cultural tags (majority rule).
        Returns 0 or 1, or None if no cultural tags."""
        if self.cultural_tags is None:
            return None
        ones = sum(self.cultural_tags)
        return 1 if ones > len(self.cultural_tags) / 2 else 0

    @staticmethod
    def reset_id_counter():
        Agent._next_id = 0


# ---------------------------------------------------------------------------
# Grid Cell
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    """A single cell in the Sugarscape grid."""
    sugar: float = 0.0
    capacity: float = 0.0
    pollution: float = 0.0
    agent: Optional[Agent] = None


# ---------------------------------------------------------------------------
# Sugarscape Grid
# ---------------------------------------------------------------------------

class SugarscapeGrid:
    """The 2D sugar landscape with two Gaussian mountain peaks."""

    def __init__(self, config: SugarscapeConfig):
        self.size = config.grid_size
        self.config = config
        self.cells = [[Cell() for _ in range(self.size)]
                      for _ in range(self.size)]
        self._init_landscape()

    def _init_landscape(self):
        """Initialize sugar capacity using two Gaussian peaks."""
        cfg = self.config
        for y in range(self.size):
            for x in range(self.size):
                # Distance to each peak
                d1 = math.sqrt((x - cfg.peak1_x)**2 + (y - cfg.peak1_y)**2)
                d2 = math.sqrt((x - cfg.peak2_x)**2 + (y - cfg.peak2_y)**2)

                # Gaussian contribution from each peak
                s1 = cfg.peak1_height * math.exp(-(d1**2) / (2 * (cfg.peak1_radius / 2.5)**2))
                s2 = cfg.peak2_height * math.exp(-(d2**2) / (2 * (cfg.peak2_radius / 2.5)**2))

                capacity = min(max(round(s1 + s2), 0), cfg.max_sugar_level)
                self.cells[y][x].capacity = capacity
                self.cells[y][x].sugar = capacity

    def regrow(self):
        """Regrow sugar on all cells according to the regrowth rule."""
        for y in range(self.size):
            for x in range(self.size):
                cell = self.cells[y][x]
                if self.config.regrowth_rate == 0:
                    # Instant regrowth: sugar returns to full capacity
                    cell.sugar = cell.capacity
                else:
                    # Gradual regrowth: add regrowth_rate per tick up to capacity
                    cell.sugar = min(cell.sugar + self.config.regrowth_rate,
                                     cell.capacity)

    def diffuse_pollution(self):
        """Spread pollution to neighboring cells."""
        if not self.config.pollution or self.config.pollution_diffusion_rate <= 0:
            return

        rate = self.config.pollution_diffusion_rate
        new_pollution = [[0.0] * self.size for _ in range(self.size)]

        for y in range(self.size):
            for x in range(self.size):
                p = self.cells[y][x].pollution
                keep = p * (1 - rate)
                spread = p * rate / 4.0  # spread equally to 4 neighbors

                new_pollution[y][x] += keep
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx = (x + dx) % self.size
                    ny = (y + dy) % self.size
                    new_pollution[ny][nx] += spread

        for y in range(self.size):
            for x in range(self.size):
                self.cells[y][x].pollution = new_pollution[y][x]

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[y % self.size][x % self.size]

    def get_sugar_map(self) -> list:
        """Return 2D list of current sugar levels."""
        return [[self.cells[y][x].sugar for x in range(self.size)]
                for y in range(self.size)]

    def get_capacity_map(self) -> list:
        """Return 2D list of sugar capacities."""
        return [[self.cells[y][x].capacity for x in range(self.size)]
                for y in range(self.size)]

    def get_pollution_map(self) -> list:
        """Return 2D list of pollution levels."""
        return [[self.cells[y][x].pollution for x in range(self.size)]
                for y in range(self.size)]


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the Sugarscape simulation."""

    def __init__(self, config: Optional[SugarscapeConfig] = None, **kwargs):
        if config is None:
            config = SugarscapeConfig(**kwargs)
        self.config = config

        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)

        Agent.reset_id_counter()

        # Initialize grid and agents
        self.grid = SugarscapeGrid(config)
        self.agents: list[Agent] = []
        self._place_initial_agents()

        # Metrics over time
        self.tick = 0
        self.population_history = [len(self.agents)]
        self.gini_history = [self._compute_gini()]
        self.mean_wealth_history = [self._mean_wealth()]
        self.median_wealth_history = [self._median_wealth()]
        self.mean_metabolism_history = [self._mean_metabolism()]
        self.mean_vision_history = [self._mean_vision()]
        self.total_sugar_history = [self._total_sugar_on_grid()]
        self.deaths_this_tick = 0
        self.births_this_tick = 0

    def _place_initial_agents(self):
        """Place agents randomly on unoccupied cells."""
        cfg = self.config
        available = []
        for y in range(cfg.grid_size):
            for x in range(cfg.grid_size):
                available.append((x, y))
        random.shuffle(available)

        num = min(cfg.num_agents, len(available))
        for i in range(num):
            x, y = available[i]
            vision = random.randint(cfg.vision_min, cfg.vision_max)
            metabolism = random.randint(cfg.metabolism_min, cfg.metabolism_max)
            sugar = random.randint(cfg.endowment_min, cfg.endowment_max)
            agent = Agent(x, y, vision, metabolism, float(sugar), cfg)
            if cfg.max_agent_age > 0:
                agent.max_age = random.randint(60, cfg.max_agent_age)
            self.agents.append(agent)
            self.grid.get_cell(x, y).agent = agent

    def step(self):
        """Execute one time step of the simulation."""
        self.deaths_this_tick = 0
        self.births_this_tick = 0

        # 1. Shuffle agent order (asynchronous update)
        random.shuffle(self.agents)

        # 2. Each agent moves and gathers
        for agent in self.agents:
            if not agent.alive:
                continue
            self._agent_move_and_gather(agent)

        # 3. Each agent consumes sugar (metabolism)
        for agent in self.agents:
            if not agent.alive:
                continue
            agent.sugar -= agent.metabolism
            agent.age += 1

            # Pollution from consumption
            if self.config.pollution:
                cell = self.grid.get_cell(agent.x, agent.y)
                cell.pollution += self.config.pollution_consumption * agent.metabolism

            # Death check
            died = agent.sugar <= 0
            if not died and agent.max_age > 0:
                died = agent.age >= agent.max_age
            if died:
                agent.alive = False
                self.grid.get_cell(agent.x, agent.y).agent = None
                self.deaths_this_tick += 1

        # 4. Reproduction
        if self.config.reproduction:
            self._reproduction_step()

        # 5. Cultural tag exchange
        if self.config.cultural_tags:
            self._cultural_exchange()

        # 6. Remove dead agents
        self.agents = [a for a in self.agents if a.alive]

        # 7. Regrow sugar
        self.grid.regrow()

        # 8. Diffuse pollution
        if self.config.pollution:
            self.grid.diffuse_pollution()

        # 9. Record metrics
        self.tick += 1
        self.population_history.append(len(self.agents))
        self.gini_history.append(self._compute_gini())
        self.mean_wealth_history.append(self._mean_wealth())
        self.median_wealth_history.append(self._median_wealth())
        self.mean_metabolism_history.append(self._mean_metabolism())
        self.mean_vision_history.append(self._mean_vision())
        self.total_sugar_history.append(self._total_sugar_on_grid())

    def _agent_move_and_gather(self, agent: Agent):
        """Agent looks in 4 cardinal directions, moves to the richest
        visible empty cell, and gathers sugar there."""
        best_x, best_y = agent.x, agent.y
        best_sugar = -1.0
        best_dist = 0

        # Look in each cardinal direction up to vision distance
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for dist in range(1, agent.vision + 1):
                nx = (agent.x + dx * dist) % self.config.grid_size
                ny = (agent.y + dy * dist) % self.config.grid_size
                cell = self.grid.get_cell(nx, ny)

                if cell.agent is not None and cell.agent is not agent:
                    continue  # occupied

                # Effective sugar (reduced by pollution if enabled)
                effective = cell.sugar
                if self.config.pollution and cell.pollution > 0:
                    effective = cell.sugar / (1.0 + cell.pollution)

                # Prefer higher sugar, then closer distance
                if (effective > best_sugar or
                        (effective == best_sugar and dist < best_dist)):
                    best_sugar = effective
                    best_x, best_y = nx, ny
                    best_dist = dist

        # Move agent
        self.grid.get_cell(agent.x, agent.y).agent = None
        agent.x = best_x
        agent.y = best_y
        self.grid.get_cell(best_x, best_y).agent = agent

        # Gather sugar
        cell = self.grid.get_cell(best_x, best_y)
        gathered = cell.sugar
        agent.sugar += gathered

        # Pollution from gathering
        if self.config.pollution:
            cell.pollution += self.config.pollution_production * gathered

        cell.sugar = 0

    def _reproduction_step(self):
        """Agents with sugar above threshold reproduce by splitting wealth."""
        cfg = self.config
        new_agents = []

        for agent in self.agents:
            if not agent.alive:
                continue
            if agent.sugar < cfg.reproduction_threshold:
                continue

            # Find an empty neighboring cell
            empty = self._find_empty_neighbor(agent.x, agent.y)
            if empty is None:
                continue

            nx, ny = empty
            # Split sugar
            child_sugar = agent.sugar / 2.0
            agent.sugar = agent.sugar / 2.0

            # Child inherits parent traits with some variation
            vision = max(1, min(cfg.vision_max,
                                agent.vision + random.choice([-1, 0, 0, 1])))
            metabolism = max(1, min(cfg.metabolism_max,
                                    agent.metabolism + random.choice([-1, 0, 0, 1])))

            child = Agent(nx, ny, vision, metabolism, child_sugar, cfg)
            if cfg.max_agent_age > 0:
                child.max_age = random.randint(60, cfg.max_agent_age)

            # Copy cultural tags with possible mutation
            if agent.cultural_tags is not None:
                child.cultural_tags = list(agent.cultural_tags)
                # Mutate one random bit
                if random.random() < 0.1:
                    idx = random.randint(0, len(child.cultural_tags) - 1)
                    child.cultural_tags[idx] = 1 - child.cultural_tags[idx]

            self.grid.get_cell(nx, ny).agent = child
            new_agents.append(child)
            self.births_this_tick += 1

        self.agents.extend(new_agents)

    def _cultural_exchange(self):
        """Agents influence their neighbors' cultural tags."""
        for agent in self.agents:
            if not agent.alive or agent.cultural_tags is None:
                continue
            # Pick a random neighbor
            neighbors = self._get_neighbors(agent.x, agent.y)
            for nx, ny in neighbors:
                cell = self.grid.get_cell(nx, ny)
                if cell.agent is not None and cell.agent.cultural_tags is not None:
                    other = cell.agent
                    # Pick a random tag position
                    idx = random.randint(0, len(agent.cultural_tags) - 1)
                    # Agent influences neighbor
                    other.cultural_tags[idx] = agent.cultural_tags[idx]
                    break

    def _find_empty_neighbor(self, x: int, y: int) -> Optional[tuple]:
        """Find a random empty adjacent cell."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx = (x + dx) % self.config.grid_size
            ny = (y + dy) % self.config.grid_size
            if self.grid.get_cell(nx, ny).agent is None:
                return (nx, ny)
        return None

    def _get_neighbors(self, x: int, y: int) -> list:
        """Get coordinates of 4 cardinal neighbors."""
        size = self.config.grid_size
        return [
            ((x + 1) % size, y),
            ((x - 1) % size, y),
            (x, (y + 1) % size),
            (x, (y - 1) % size),
        ]

    def run(self, progress_callback=None):
        """Run the full simulation."""
        for t in range(self.config.max_ticks):
            self.step()
            if len(self.agents) == 0:
                break
            if progress_callback and t % 50 == 0:
                progress_callback(t, self.config.max_ticks)

    # -----------------------------------------------------------------------
    # Metrics
    # -----------------------------------------------------------------------

    def _compute_gini(self) -> float:
        """Compute Gini coefficient of agent sugar holdings."""
        if len(self.agents) == 0:
            return 0.0
        wealths = sorted(a.sugar for a in self.agents if a.alive)
        n = len(wealths)
        if n == 0:
            return 0.0
        total = sum(wealths)
        if total <= 0:
            return 0.0
        weighted_sum = sum((2 * (i + 1) - n - 1) * w for i, w in enumerate(wealths))
        gini = weighted_sum / (n * total)
        return max(0.0, min(1.0, gini))

    def _mean_wealth(self) -> float:
        living = [a.sugar for a in self.agents if a.alive]
        return float(np.mean(living)) if living else 0.0

    def _median_wealth(self) -> float:
        living = [a.sugar for a in self.agents if a.alive]
        return float(np.median(living)) if living else 0.0

    def _mean_metabolism(self) -> float:
        living = [a.metabolism for a in self.agents if a.alive]
        return float(np.mean(living)) if living else 0.0

    def _mean_vision(self) -> float:
        living = [a.vision for a in self.agents if a.alive]
        return float(np.mean(living)) if living else 0.0

    def _total_sugar_on_grid(self) -> float:
        total = 0.0
        for y in range(self.config.grid_size):
            for x in range(self.config.grid_size):
                total += self.grid.cells[y][x].sugar
        return total

    def get_wealth_distribution(self, bins: int = 20) -> tuple:
        """Return histogram of agent wealth."""
        wealths = [a.sugar for a in self.agents if a.alive]
        if not wealths:
            return [], []
        counts, edges = np.histogram(wealths, bins=bins)
        centers = [(edges[i] + edges[i + 1]) / 2.0 for i in range(len(counts))]
        return centers, counts.tolist()

    def get_agent_data(self) -> list:
        """Return list of agent dicts for export/visualization."""
        return [
            {
                'id': a.id,
                'x': a.x,
                'y': a.y,
                'sugar': round(a.sugar, 1),
                'vision': a.vision,
                'metabolism': a.metabolism,
                'age': a.age,
                'tribe': a.tribe,
            }
            for a in self.agents if a.alive
        ]

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        living = [a for a in self.agents if a.alive]
        wealths = [a.sugar for a in living]

        stats = {
            'num_ticks': self.tick,
            'grid_size': self.config.grid_size,
            'initial_agents': self.config.num_agents,
            'final_population': len(living),
            'population_change': len(living) - self.config.num_agents,
            'mean_wealth': float(np.mean(wealths)) if wealths else 0.0,
            'median_wealth': float(np.median(wealths)) if wealths else 0.0,
            'std_wealth': float(np.std(wealths)) if wealths else 0.0,
            'min_wealth': float(min(wealths)) if wealths else 0.0,
            'max_wealth': float(max(wealths)) if wealths else 0.0,
            'gini_coefficient': self.gini_history[-1] if self.gini_history else 0.0,
            'mean_vision': float(np.mean([a.vision for a in living])) if living else 0.0,
            'mean_metabolism': float(np.mean([a.metabolism for a in living])) if living else 0.0,
            'mean_age': float(np.mean([a.age for a in living])) if living else 0.0,
            'total_sugar_on_grid': self._total_sugar_on_grid(),
            'reproduction_enabled': self.config.reproduction,
            'pollution_enabled': self.config.pollution,
            'cultural_tags_enabled': self.config.cultural_tags,
        }
        return stats

    def get_timeseries_data(self) -> dict:
        """Return time series data suitable for CSV export."""
        n = len(self.population_history)
        return {
            'tick': list(range(n)),
            'population': self.population_history,
            'gini': self.gini_history,
            'mean_wealth': self.mean_wealth_history,
            'median_wealth': self.median_wealth_history,
            'mean_metabolism': self.mean_metabolism_history,
            'mean_vision': self.mean_vision_history,
            'total_grid_sugar': self.total_sugar_history,
        }

    def get_grid_state(self) -> dict:
        """Return current grid state for visualization."""
        sugar_map = self.grid.get_sugar_map()
        capacity_map = self.grid.get_capacity_map()
        agents = self.get_agent_data()
        return {
            'sugar': sugar_map,
            'capacity': capacity_map,
            'agents': agents,
            'tick': self.tick,
        }


if __name__ == '__main__':
    print("Running Sugarscape simulation...")
    config = SugarscapeConfig(
        num_agents=250,
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
