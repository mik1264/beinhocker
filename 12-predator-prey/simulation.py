"""
Predator-Prey / Lotka-Volterra Simulation

Two variants:
  A) Classic ODE (Lotka-Volterra equations solved via Euler integration)
  B) Spatial agent-based model on a 2D grid with grass, rabbits, and foxes

Demonstrates endogenous oscillations arising from simple interaction rules --
populations cycle without any external forcing. Beinhocker (Ch 8, p.168) uses
this as a canonical example of far-from-equilibrium dynamics in complex
adaptive systems.

References:
  - Lotka, "Elements of Physical Biology" (1925)
  - Volterra, "Variazioni e fluttuazioni del numero d'individui in specie
    animali conviventi" (1926)
  - Beinhocker, "The Origin of Wealth" (2006), Chapter 8
"""

import random
import math
import csv
import json
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
#  A) Classic ODE Lotka-Volterra
# ---------------------------------------------------------------------------

@dataclass
class ODEConfig:
    alpha: float = 1.0       # prey birth rate
    beta: float = 0.1        # predation rate
    delta: float = 0.075     # predator efficiency (conversion of prey to predator births)
    gamma: float = 1.5       # predator death rate
    initial_prey: float = 40.0
    initial_predators: float = 9.0
    dt: float = 0.01         # Euler integration time step
    ticks: int = 500         # number of recorded steps (each = 1 time unit)


@dataclass
class ODERecord:
    tick: int
    time: float
    prey: float
    predators: float


class LotkaVolterraODE:
    """Classic Lotka-Volterra solved by RK4 integration for numerical stability."""

    def __init__(self, config: Optional[ODEConfig] = None):
        self.config = config or ODEConfig()
        self.x = self.config.initial_prey       # prey
        self.y = self.config.initial_predators   # predators
        self.time = 0.0
        self.tick = 0
        self.history: list[ODERecord] = []
        # Record initial state
        self.history.append(ODERecord(0, 0.0, self.x, self.y))

    def _derivatives(self, x: float, y: float) -> tuple[float, float]:
        cfg = self.config
        dx = cfg.alpha * x - cfg.beta * x * y
        dy = cfg.delta * x * y - cfg.gamma * y
        return dx, dy

    def step(self):
        """Advance by one time unit using RK4 sub-steps."""
        cfg = self.config
        sub_steps = int(1.0 / cfg.dt)
        h = cfg.dt
        for _ in range(sub_steps):
            # RK4
            k1x, k1y = self._derivatives(self.x, self.y)
            k2x, k2y = self._derivatives(self.x + 0.5*h*k1x, self.y + 0.5*h*k1y)
            k3x, k3y = self._derivatives(self.x + 0.5*h*k2x, self.y + 0.5*h*k2y)
            k4x, k4y = self._derivatives(self.x + h*k3x, self.y + h*k3y)

            self.x += (h / 6.0) * (k1x + 2*k2x + 2*k3x + k4x)
            self.y += (h / 6.0) * (k1y + 2*k2y + 2*k3y + k4y)
            # Clamp to non-negative
            self.x = max(self.x, 0.0)
            self.y = max(self.y, 0.0)
            self.time += h

        self.tick += 1
        self.history.append(ODERecord(self.tick, round(self.time, 4), self.x, self.y))

    def run(self, ticks: Optional[int] = None, callback=None):
        ticks = ticks or self.config.ticks
        for t in range(ticks):
            self.step()
            if callback:
                callback(self.tick, self.x, self.y)
        return self.history

    def detect_period(self) -> Optional[float]:
        """Estimate oscillation period from prey peaks."""
        if len(self.history) < 10:
            return None
        prey_vals = [r.prey for r in self.history]
        peaks = []
        for i in range(1, len(prey_vals) - 1):
            if prey_vals[i] > prey_vals[i - 1] and prey_vals[i] > prey_vals[i + 1]:
                peaks.append(self.history[i].time)
        if len(peaks) < 2:
            return None
        intervals = [peaks[i + 1] - peaks[i] for i in range(len(peaks) - 1)]
        return sum(intervals) / len(intervals)

    def get_history_json(self) -> list[dict]:
        return [
            {"tick": r.tick, "time": r.time, "prey": round(r.prey, 4),
             "predators": round(r.predators, 4)}
            for r in self.history
        ]

    def save_csv(self, filepath: str):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "time", "prey", "predators"])
            for r in self.history:
                writer.writerow([r.tick, f"{r.time:.4f}", f"{r.prey:.4f}", f"{r.predators:.4f}"])

    def save_json(self, filepath: str):
        data = {
            "model": "ode",
            "params": {
                "alpha": self.config.alpha,
                "beta": self.config.beta,
                "delta": self.config.delta,
                "gamma": self.config.gamma,
                "initial_prey": self.config.initial_prey,
                "initial_predators": self.config.initial_predators,
                "dt": self.config.dt,
            },
            "history": self.get_history_json(),
            "oscillation_period": self.detect_period(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
#  B) Spatial Agent-Based Model
# ---------------------------------------------------------------------------

@dataclass
class SpatialConfig:
    grid_size: int = 50
    initial_prey: int = 200
    initial_predators: int = 30
    grass_regrow_time: int = 8        # ticks for grass to regrow
    prey_gain_from_food: int = 5      # energy gained by eating grass
    predator_gain_from_food: int = 5  # energy gained by eating prey
    prey_reproduce: float = 0.08      # probability of reproduction per tick
    predator_reproduce: float = 0.02  # probability of reproduction per tick
    predator_starve: int = 10         # initial max energy for predators
    prey_initial_energy: int = 5      # initial energy for prey
    seed: Optional[int] = None
    ticks: int = 500


@dataclass
class Agent:
    x: int
    y: int
    energy: int
    agent_type: str  # "prey" or "predator"
    age: int = 0


@dataclass
class SpatialRecord:
    tick: int
    prey_count: int
    predator_count: int
    grass_count: int
    grass_fraction: float


class PredatorPreySpatial:
    """
    2D grid world with grass, prey (rabbits), and predators (foxes).

    Grass grows on every cell and regrows after being eaten.
    Prey eat grass, gain energy, move randomly, reproduce stochastically.
    Predators eat prey, gain energy, move toward nearest prey, reproduce,
    and starve if energy runs out.
    """

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def __init__(self, config: Optional[SpatialConfig] = None):
        self.config = config or SpatialConfig()
        cfg = self.config
        self.rng = random.Random(cfg.seed)
        self.size = cfg.grid_size
        self.tick = 0
        self.history: list[SpatialRecord] = []

        # Grass grid: 0 = alive grass, positive int = ticks until regrowth
        self.grass = [[0] * self.size for _ in range(self.size)]

        # Agent lists
        self.prey_agents: list[Agent] = []
        self.predator_agents: list[Agent] = []

        self._initialize()

    def _initialize(self):
        cfg = self.config
        # Place prey randomly
        for _ in range(cfg.initial_prey):
            x = self.rng.randint(0, self.size - 1)
            y = self.rng.randint(0, self.size - 1)
            energy = self.rng.randint(1, 2 * cfg.prey_initial_energy)
            self.prey_agents.append(Agent(x, y, energy, "prey"))

        # Place predators randomly
        for _ in range(cfg.initial_predators):
            x = self.rng.randint(0, self.size - 1)
            y = self.rng.randint(0, self.size - 1)
            energy = self.rng.randint(1, 2 * cfg.predator_starve)
            self.predator_agents.append(Agent(x, y, energy, "predator"))

        # Record initial state
        gc = sum(1 for row in self.grass for cell in row if cell == 0)
        total = self.size * self.size
        self.history.append(SpatialRecord(
            0, len(self.prey_agents), len(self.predator_agents),
            gc, gc / total,
        ))

    def _wrap(self, v: int) -> int:
        return v % self.size

    def _move_random(self, agent: Agent):
        dx, dy = self.rng.choice(self.DIRECTIONS)
        agent.x = self._wrap(agent.x + dx)
        agent.y = self._wrap(agent.y + dy)

    def _move_toward_prey(self, predator: Agent):
        """Move predator toward nearest prey within a short detection radius, or randomly."""
        best_dist = float('inf')
        best_dx, best_dy = 0, 0
        found = False

        # Only detect prey within immediate neighborhood (Manhattan distance <= 2)
        detection_radius = 2
        for prey in self.prey_agents:
            # Toroidal distance
            dx = prey.x - predator.x
            dy = prey.y - predator.y
            if abs(dx) > self.size // 2:
                dx = dx - self.size if dx > 0 else dx + self.size
            if abs(dy) > self.size // 2:
                dy = dy - self.size if dy > 0 else dy + self.size
            dist = abs(dx) + abs(dy)
            if dist < best_dist and dist <= detection_radius:
                best_dist = dist
                best_dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
                best_dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
                found = True

        if found and best_dist > 0:
            # Move one step toward prey
            if self.rng.random() < 0.5 and best_dx != 0:
                predator.x = self._wrap(predator.x + best_dx)
            elif best_dy != 0:
                predator.y = self._wrap(predator.y + best_dy)
            else:
                predator.x = self._wrap(predator.x + best_dx)
        else:
            # Random movement when no prey detected
            self._move_random(predator)

    def step(self):
        """Execute one tick of the spatial simulation."""
        self.tick += 1
        cfg = self.config

        # --- Grass regrowth ---
        for r in range(self.size):
            for c in range(self.size):
                if self.grass[r][c] > 0:
                    self.grass[r][c] -= 1

        # --- Prey actions ---
        new_prey = []
        self.rng.shuffle(self.prey_agents)
        for prey in self.prey_agents:
            # Move
            self._move_random(prey)
            prey.energy -= 1
            prey.age += 1

            # Eat grass
            if self.grass[prey.y][prey.x] == 0:
                prey.energy += cfg.prey_gain_from_food
                self.grass[prey.y][prey.x] = cfg.grass_regrow_time

            # Reproduce
            if self.rng.random() < cfg.prey_reproduce:
                prey.energy = prey.energy // 2
                child = Agent(prey.x, prey.y, prey.energy, "prey")
                new_prey.append(child)

        # Remove dead prey (energy <= 0)
        self.prey_agents = [p for p in self.prey_agents if p.energy > 0]
        self.prey_agents.extend(new_prey)

        # --- Build prey location map for predator hunting ---
        prey_map: dict[tuple[int, int], list[Agent]] = {}
        for p in self.prey_agents:
            key = (p.x, p.y)
            if key not in prey_map:
                prey_map[key] = []
            prey_map[key].append(p)

        # --- Predator actions ---
        new_predators = []
        eaten_prey: set[int] = set()  # ids of eaten prey
        self.rng.shuffle(self.predator_agents)
        for pred in self.predator_agents:
            # Move toward prey
            self._move_toward_prey(pred)
            pred.energy -= 1
            pred.age += 1

            # Eat prey at current location
            key = (pred.x, pred.y)
            if key in prey_map and prey_map[key]:
                victim = prey_map[key].pop()
                eaten_prey.add(id(victim))
                pred.energy += cfg.predator_gain_from_food

            # Reproduce
            if self.rng.random() < cfg.predator_reproduce:
                pred.energy = pred.energy // 2
                child = Agent(pred.x, pred.y, pred.energy, "predator")
                new_predators.append(child)

        # Remove dead predators and eaten prey
        self.predator_agents = [p for p in self.predator_agents if p.energy > 0]
        self.predator_agents.extend(new_predators)
        self.prey_agents = [p for p in self.prey_agents if id(p) not in eaten_prey]

        # Record
        gc = sum(1 for row in self.grass for cell in row if cell == 0)
        total = self.size * self.size
        self.history.append(SpatialRecord(
            self.tick,
            len(self.prey_agents),
            len(self.predator_agents),
            gc,
            gc / total,
        ))

    def run(self, ticks: Optional[int] = None, callback=None):
        ticks = ticks or self.config.ticks
        for t in range(ticks):
            self.step()
            if callback:
                callback(self.tick, len(self.prey_agents), len(self.predator_agents))
            # Stop early if both populations die
            if len(self.prey_agents) == 0 and len(self.predator_agents) == 0:
                break
        return self.history

    def detect_period(self) -> Optional[float]:
        """Estimate oscillation period from prey population peaks."""
        if len(self.history) < 20:
            return None
        vals = [r.prey_count for r in self.history]
        # Simple smoothing
        smooth = vals[:]
        for i in range(2, len(vals) - 2):
            smooth[i] = sum(vals[i - 2:i + 3]) / 5

        peaks = []
        for i in range(2, len(smooth) - 2):
            if smooth[i] > smooth[i - 1] and smooth[i] > smooth[i + 1] and smooth[i] > 10:
                peaks.append(i)

        if len(peaks) < 2:
            return None
        intervals = [peaks[j + 1] - peaks[j] for j in range(len(peaks) - 1)]
        return sum(intervals) / len(intervals)

    def get_grid_state(self) -> dict:
        """Return grid state for visualization."""
        # Build occupancy grid
        grid = [[0] * self.size for _ in range(self.size)]
        # 0 = empty/dead grass, 1 = grass, 2 = prey, 3 = predator
        for r in range(self.size):
            for c in range(self.size):
                if self.grass[r][c] == 0:
                    grid[r][c] = 1  # live grass
        for p in self.prey_agents:
            grid[p.y][p.x] = 2
        for p in self.predator_agents:
            grid[p.y][p.x] = 3
        return {"grid": grid, "size": self.size}

    def get_history_json(self) -> list[dict]:
        return [
            {
                "tick": r.tick,
                "prey": r.prey_count,
                "predators": r.predator_count,
                "grass": r.grass_count,
                "grass_fraction": round(r.grass_fraction, 4),
            }
            for r in self.history
        ]

    def save_csv(self, filepath: str):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "prey", "predators", "grass", "grass_fraction"])
            for r in self.history:
                writer.writerow([r.tick, r.prey_count, r.predator_count,
                                 r.grass_count, f"{r.grass_fraction:.4f}"])

    def save_json(self, filepath: str):
        data = {
            "model": "spatial",
            "params": {
                "grid_size": self.config.grid_size,
                "initial_prey": self.config.initial_prey,
                "initial_predators": self.config.initial_predators,
                "grass_regrow_time": self.config.grass_regrow_time,
                "prey_gain_from_food": self.config.prey_gain_from_food,
                "predator_gain_from_food": self.config.predator_gain_from_food,
                "prey_reproduce": self.config.prey_reproduce,
                "predator_reproduce": self.config.predator_reproduce,
                "predator_starve": self.config.predator_starve,
                "seed": self.config.seed,
            },
            "history": self.get_history_json(),
            "oscillation_period": self.detect_period(),
            "final_grid": self.get_grid_state(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
