"""
Prisoner's Dilemma & Evolution of Cooperation Simulation
Based on Axelrod's tournaments and Beinhocker's "The Origin of Wealth" (2006)

Implements an iterated Prisoner's Dilemma with evolutionary dynamics:
- Multiple classic strategies (TFT, Pavlov, Grudger, etc.)
- Spatial variant: agents on a toroidal grid, play neighbors, replicate locally
- Non-spatial variant: round-robin tournament with proportional replication
- Configurable payoff matrix and noise
- Evolutionary dynamics with mutation
- Tracks cooperation rate, strategy populations, payoffs, and spatial patterns

References:
  - Axelrod, "The Evolution of Cooperation" (1984)
  - Nowak & May, "Evolutionary Games and Spatial Chaos" (Nature, 1992)
  - Beinhocker, "The Origin of Wealth" (2006), Chapter 9
"""

import random
import math
import copy
import csv
import json
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum


# ---------------------------------------------------------------------------
# Strategy Types
# ---------------------------------------------------------------------------

class StrategyType(Enum):
    """Enumeration of available strategies."""
    ALWAYS_COOPERATE = "always_cooperate"
    ALWAYS_DEFECT = "always_defect"
    TIT_FOR_TAT = "tit_for_tat"
    GENEROUS_TFT = "generous_tft"
    PAVLOV = "pavlov"
    RANDOM = "random"
    GRUDGER = "grudger"

    @property
    def short_name(self) -> str:
        names = {
            "always_cooperate": "AllC",
            "always_defect": "AllD",
            "tit_for_tat": "TFT",
            "generous_tft": "GTFT",
            "pavlov": "Pavlov",
            "random": "Random",
            "grudger": "Grudger",
        }
        return names[self.value]

    @property
    def color(self) -> str:
        """Color associated with this strategy for visualization."""
        colors = {
            "always_cooperate": "#00cc66",
            "always_defect": "#ff4444",
            "tit_for_tat": "#4488ff",
            "generous_tft": "#44ccff",
            "pavlov": "#ffaa00",
            "random": "#888888",
            "grudger": "#cc44ff",
        }
        return colors[self.value]


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

COOPERATE = 0
DEFECT = 1


# ---------------------------------------------------------------------------
# Payoff Matrix
# ---------------------------------------------------------------------------

@dataclass
class PayoffMatrix:
    """Prisoner's Dilemma payoff matrix.

    Standard notation:
        T = Temptation (defect vs cooperator)
        R = Reward (mutual cooperation)
        P = Punishment (mutual defection)
        S = Sucker (cooperate vs defector)

    Must satisfy: T > R > P > S and 2R > T + S
    """
    T: float = 5.0   # Temptation to defect
    R: float = 3.0   # Reward for mutual cooperation
    P: float = 1.0   # Punishment for mutual defection
    S: float = 0.0   # Sucker's payoff

    def payoff(self, my_action: int, opponent_action: int) -> float:
        """Return payoff for my_action given opponent_action."""
        if my_action == COOPERATE and opponent_action == COOPERATE:
            return self.R
        elif my_action == COOPERATE and opponent_action == DEFECT:
            return self.S
        elif my_action == DEFECT and opponent_action == COOPERATE:
            return self.T
        else:  # both defect
            return self.P

    def is_valid(self) -> bool:
        """Check if the payoff matrix satisfies PD conditions."""
        return (self.T > self.R > self.P > self.S and
                2 * self.R > self.T + self.S)


# ---------------------------------------------------------------------------
# Strategy Implementations
# ---------------------------------------------------------------------------

class Strategy:
    """Base strategy that decides cooperate or defect."""

    def __init__(self, strategy_type: StrategyType, noise: float = 0.0,
                 rng: Optional[np.random.Generator] = None):
        self.strategy_type = strategy_type
        self.noise = noise
        self.rng = rng or np.random.default_rng()
        self.opponent_history: dict[int, list[int]] = {}
        self.my_history: dict[int, list[int]] = {}
        self.grudge_set: set[int] = set()  # for Grudger

    def reset_for_match(self, opponent_id: int):
        """Reset per-opponent memory for a new iterated match."""
        self.opponent_history[opponent_id] = []
        self.my_history[opponent_id] = []

    def decide(self, opponent_id: int) -> int:
        """Choose an action, then apply noise."""
        action = self._decide_impl(opponent_id)
        # Noise: flip action with probability noise
        if self.noise > 0 and self.rng.random() < self.noise:
            action = 1 - action
        return action

    def _decide_impl(self, opponent_id: int) -> int:
        """Pure strategy decision (before noise)."""
        st = self.strategy_type
        opp_hist = self.opponent_history.get(opponent_id, [])
        my_hist = self.my_history.get(opponent_id, [])

        if st == StrategyType.ALWAYS_COOPERATE:
            return COOPERATE

        elif st == StrategyType.ALWAYS_DEFECT:
            return DEFECT

        elif st == StrategyType.TIT_FOR_TAT:
            if len(opp_hist) == 0:
                return COOPERATE
            return opp_hist[-1]

        elif st == StrategyType.GENEROUS_TFT:
            if len(opp_hist) == 0:
                return COOPERATE
            if opp_hist[-1] == DEFECT:
                # Forgive with probability ~1/3
                return COOPERATE if self.rng.random() < 0.33 else DEFECT
            return COOPERATE

        elif st == StrategyType.PAVLOV:
            # Win-Stay, Lose-Shift
            if len(opp_hist) == 0:
                return COOPERATE
            last_my = my_hist[-1] if my_hist else COOPERATE
            last_opp = opp_hist[-1]
            # "Win" = got R or T, "Lose" = got S or P
            if last_my == last_opp:  # CC -> R (win) or DD -> P (lose)
                if last_my == COOPERATE:
                    return COOPERATE  # got R, stay
                else:
                    return COOPERATE  # got P, shift
            else:
                if last_my == COOPERATE:
                    return DEFECT  # got S, shift
                else:
                    return DEFECT  # got T, stay

        elif st == StrategyType.RANDOM:
            return COOPERATE if self.rng.random() < 0.5 else DEFECT

        elif st == StrategyType.GRUDGER:
            if opponent_id in self.grudge_set:
                return DEFECT
            if len(opp_hist) > 0 and DEFECT in opp_hist:
                self.grudge_set.add(opponent_id)
                return DEFECT
            return COOPERATE

        return COOPERATE

    def record(self, opponent_id: int, my_action: int, opp_action: int):
        """Record the outcome of a round."""
        if opponent_id not in self.opponent_history:
            self.opponent_history[opponent_id] = []
            self.my_history[opponent_id] = []
        self.opponent_history[opponent_id].append(opp_action)
        self.my_history[opponent_id].append(my_action)

    def clone(self) -> 'Strategy':
        """Create a fresh copy of this strategy (no memory)."""
        return Strategy(self.strategy_type, self.noise, self.rng)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """An agent on the grid or in the tournament."""
    id: int
    strategy: Strategy
    fitness: float = 0.0
    games_played: int = 0
    total_cooperations: int = 0
    total_actions: int = 0
    row: int = 0
    col: int = 0

    @property
    def strategy_type(self) -> StrategyType:
        return self.strategy.strategy_type

    @property
    def cooperation_rate(self) -> float:
        if self.total_actions == 0:
            return 0.0
        return self.total_cooperations / self.total_actions

    @property
    def average_payoff(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.fitness / self.games_played

    def reset_fitness(self):
        """Reset fitness for a new generation."""
        self.fitness = 0.0
        self.games_played = 0
        self.total_cooperations = 0
        self.total_actions = 0


# ---------------------------------------------------------------------------
# Tick Record
# ---------------------------------------------------------------------------

@dataclass
class TickRecord:
    """One generation of simulation data."""
    generation: int
    cooperation_rate: float
    average_payoff: float
    strategy_counts: dict  # StrategyType.value -> count
    strategy_fractions: dict  # StrategyType.value -> fraction
    grid_state: Optional[list] = None  # 2D array of strategy type values


# ---------------------------------------------------------------------------
# Spatial Simulation (Grid-based)
# ---------------------------------------------------------------------------

class SpatialSimulation:
    """Grid-based iterated Prisoner's Dilemma with local interactions.

    Agents sit on a toroidal grid and play their neighbors. After all games,
    each cell adopts the strategy of its most successful neighbor (or itself).
    Mutation can introduce random strategy changes.

    Based on Nowak & May (1992) and Beinhocker's coverage.
    """

    def __init__(self, grid_size: int = 50, rounds_per_match: int = 10,
                 noise: float = 0.0, mutation_rate: float = 0.001,
                 payoff_matrix: Optional[PayoffMatrix] = None,
                 strategy_mix: Optional[dict] = None,
                 neighborhood: str = "moore",
                 generations: int = 200,
                 seed: Optional[int] = None):
        self.grid_size = grid_size
        self.rounds_per_match = rounds_per_match
        self.noise = noise
        self.mutation_rate = mutation_rate
        self.payoff_matrix = payoff_matrix or PayoffMatrix()
        self.neighborhood = neighborhood  # "moore" (8) or "von_neumann" (4)
        self.generations = generations

        self.rng = np.random.default_rng(seed)
        if seed is not None:
            random.seed(seed)

        # Default strategy mix
        if strategy_mix is None:
            strategy_mix = {
                StrategyType.ALWAYS_COOPERATE: 0.15,
                StrategyType.ALWAYS_DEFECT: 0.15,
                StrategyType.TIT_FOR_TAT: 0.20,
                StrategyType.GENEROUS_TFT: 0.10,
                StrategyType.PAVLOV: 0.15,
                StrategyType.RANDOM: 0.10,
                StrategyType.GRUDGER: 0.15,
            }
        self.initial_strategy_mix = strategy_mix

        # Build grid
        self.grid: list[list[Agent]] = []
        self.next_id = 0
        self._init_grid()

        # Metrics
        self.history: list[TickRecord] = []
        self.current_generation = 0

    def _init_grid(self):
        """Initialize the grid with agents drawn from the strategy mix."""
        types = list(self.initial_strategy_mix.keys())
        weights = [self.initial_strategy_mix[t] for t in types]
        total_w = sum(weights)
        probs = [w / total_w for w in weights]

        self.grid = []
        for r in range(self.grid_size):
            row = []
            for c in range(self.grid_size):
                st = self.rng.choice(types, p=probs)
                strategy = Strategy(st, self.noise, self.rng)
                agent = Agent(
                    id=self.next_id,
                    strategy=strategy,
                    row=r,
                    col=c,
                )
                self.next_id += 1
                row.append(agent)
            self.grid.append(row)

    def _get_neighbors(self, row: int, col: int) -> list[Agent]:
        """Get neighbors using toroidal boundary conditions."""
        neighbors = []
        if self.neighborhood == "moore":
            offsets = [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1),           (0, 1),
                       (1, -1),  (1, 0),  (1, 1)]
        else:  # von_neumann
            offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]

        for dr, dc in offsets:
            nr = (row + dr) % self.grid_size
            nc = (col + dc) % self.grid_size
            neighbors.append(self.grid[nr][nc])
        return neighbors

    def _play_match(self, agent1: Agent, agent2: Agent):
        """Play an iterated PD match between two agents."""
        agent1.strategy.reset_for_match(agent2.id)
        agent2.strategy.reset_for_match(agent1.id)

        for _ in range(self.rounds_per_match):
            a1 = agent1.strategy.decide(agent2.id)
            a2 = agent2.strategy.decide(agent1.id)

            p1 = self.payoff_matrix.payoff(a1, a2)
            p2 = self.payoff_matrix.payoff(a2, a1)

            agent1.fitness += p1
            agent2.fitness += p2
            agent1.games_played += 1
            agent2.games_played += 1

            if a1 == COOPERATE:
                agent1.total_cooperations += 1
            if a2 == COOPERATE:
                agent2.total_cooperations += 1
            agent1.total_actions += 1
            agent2.total_actions += 1

            agent1.strategy.record(agent2.id, a1, a2)
            agent2.strategy.record(agent1.id, a2, a1)

    def step(self) -> TickRecord:
        """Execute one generation: play, evaluate, reproduce."""
        # Reset fitness
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.grid[r][c].reset_fitness()

        # Play matches with all neighbors
        played = set()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                agent = self.grid[r][c]
                for neighbor in self._get_neighbors(r, c):
                    pair = (min(agent.id, neighbor.id), max(agent.id, neighbor.id))
                    if pair not in played:
                        self._play_match(agent, neighbor)
                        played.add(pair)

        # Collect metrics before reproduction
        record = self._collect_metrics()

        # Reproduction: each cell adopts best neighbor's strategy
        new_grid_strategies = []
        for r in range(self.grid_size):
            row_strategies = []
            for c in range(self.grid_size):
                agent = self.grid[r][c]
                neighbors = self._get_neighbors(r, c)
                candidates = [agent] + neighbors

                # Select the strategy of the agent with highest average payoff
                best = max(candidates, key=lambda a: a.average_payoff)
                new_type = best.strategy_type

                # Mutation
                if self.mutation_rate > 0 and self.rng.random() < self.mutation_rate:
                    all_types = list(StrategyType)
                    new_type = self.rng.choice(all_types)

                row_strategies.append(new_type)
            new_grid_strategies.append(row_strategies)

        # Apply new strategies
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                old_agent = self.grid[r][c]
                new_type = new_grid_strategies[r][c]
                if new_type != old_agent.strategy_type:
                    new_strategy = Strategy(new_type, self.noise, self.rng)
                    old_agent.strategy = new_strategy
                    old_agent.id = self.next_id
                    self.next_id += 1

        self.history.append(record)
        self.current_generation += 1
        return record

    def _collect_metrics(self) -> TickRecord:
        """Collect metrics for the current generation."""
        total_coop = 0
        total_actions = 0
        total_payoff = 0.0
        total_games = 0
        strategy_counts = {st.value: 0 for st in StrategyType}

        grid_state = []
        for r in range(self.grid_size):
            row_state = []
            for c in range(self.grid_size):
                agent = self.grid[r][c]
                total_coop += agent.total_cooperations
                total_actions += agent.total_actions
                total_payoff += agent.fitness
                total_games += agent.games_played
                strategy_counts[agent.strategy_type.value] += 1
                row_state.append(agent.strategy_type.value)
            grid_state.append(row_state)

        total_agents = self.grid_size * self.grid_size
        coop_rate = total_coop / max(total_actions, 1)
        avg_payoff = total_payoff / max(total_games, 1)

        strategy_fractions = {
            k: v / total_agents for k, v in strategy_counts.items()
        }

        return TickRecord(
            generation=self.current_generation,
            cooperation_rate=coop_rate,
            average_payoff=avg_payoff,
            strategy_counts=strategy_counts,
            strategy_fractions=strategy_fractions,
            grid_state=grid_state,
        )

    def run(self, progress_callback: Optional[Callable] = None) -> list[TickRecord]:
        """Run the full simulation."""
        for g in range(self.generations):
            self.step()
            if progress_callback and g % 10 == 0:
                progress_callback(g, self.generations)
        return self.history

    def get_grid_state(self) -> list[list[str]]:
        """Return current grid as 2D array of strategy type values."""
        return [[self.grid[r][c].strategy_type.value
                 for c in range(self.grid_size)]
                for r in range(self.grid_size)]

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        if not self.history:
            return {}

        coop_rates = [r.cooperation_rate for r in self.history]
        avg_payoffs = [r.average_payoff for r in self.history]
        final = self.history[-1]

        return {
            "generations": self.current_generation,
            "grid_size": self.grid_size,
            "noise": self.noise,
            "mutation_rate": self.mutation_rate,
            "rounds_per_match": self.rounds_per_match,
            "final_cooperation_rate": final.cooperation_rate,
            "mean_cooperation_rate": float(np.mean(coop_rates)),
            "final_average_payoff": final.average_payoff,
            "mean_average_payoff": float(np.mean(avg_payoffs)),
            "final_strategy_fractions": final.strategy_fractions,
            "payoff_matrix": {
                "T": self.payoff_matrix.T,
                "R": self.payoff_matrix.R,
                "P": self.payoff_matrix.P,
                "S": self.payoff_matrix.S,
            },
        }


# ---------------------------------------------------------------------------
# Non-Spatial (Tournament) Simulation
# ---------------------------------------------------------------------------

class TournamentSimulation:
    """Round-robin tournament with proportional replication.

    Each generation:
    1. All strategies play all other strategies in iterated PD
    2. Fitness = total payoff across all matches
    3. Next generation: strategies replicate proportional to fitness
    4. Mutation can change a small fraction of strategies

    Based on Axelrod's computer tournaments.
    """

    def __init__(self, population_size: int = 100,
                 rounds_per_match: int = 20,
                 noise: float = 0.0,
                 mutation_rate: float = 0.01,
                 payoff_matrix: Optional[PayoffMatrix] = None,
                 strategy_mix: Optional[dict] = None,
                 generations: int = 200,
                 seed: Optional[int] = None):
        self.population_size = population_size
        self.rounds_per_match = rounds_per_match
        self.noise = noise
        self.mutation_rate = mutation_rate
        self.payoff_matrix = payoff_matrix or PayoffMatrix()
        self.generations = generations

        self.rng = np.random.default_rng(seed)
        if seed is not None:
            random.seed(seed)

        # Default strategy mix
        if strategy_mix is None:
            strategy_mix = {
                StrategyType.ALWAYS_COOPERATE: 0.15,
                StrategyType.ALWAYS_DEFECT: 0.15,
                StrategyType.TIT_FOR_TAT: 0.20,
                StrategyType.GENEROUS_TFT: 0.10,
                StrategyType.PAVLOV: 0.15,
                StrategyType.RANDOM: 0.10,
                StrategyType.GRUDGER: 0.15,
            }
        self.initial_strategy_mix = strategy_mix

        # Create population
        self.population: list[Agent] = []
        self._init_population()

        # Metrics
        self.history: list[TickRecord] = []
        self.current_generation = 0
        self.next_id = self.population_size

    def _init_population(self):
        """Initialize population according to strategy mix."""
        types = list(self.initial_strategy_mix.keys())
        weights = [self.initial_strategy_mix[t] for t in types]
        total_w = sum(weights)
        probs = [w / total_w for w in weights]

        for i in range(self.population_size):
            st = self.rng.choice(types, p=probs)
            strategy = Strategy(st, self.noise, self.rng)
            agent = Agent(id=i, strategy=strategy)
            self.population.append(agent)

    def _play_match(self, agent1: Agent, agent2: Agent):
        """Play an iterated PD match between two agents."""
        agent1.strategy.reset_for_match(agent2.id)
        agent2.strategy.reset_for_match(agent1.id)

        for _ in range(self.rounds_per_match):
            a1 = agent1.strategy.decide(agent2.id)
            a2 = agent2.strategy.decide(agent1.id)

            p1 = self.payoff_matrix.payoff(a1, a2)
            p2 = self.payoff_matrix.payoff(a2, a1)

            agent1.fitness += p1
            agent2.fitness += p2
            agent1.games_played += 1
            agent2.games_played += 1

            if a1 == COOPERATE:
                agent1.total_cooperations += 1
            if a2 == COOPERATE:
                agent2.total_cooperations += 1
            agent1.total_actions += 1
            agent2.total_actions += 1

            agent1.strategy.record(agent2.id, a1, a2)
            agent2.strategy.record(agent1.id, a2, a1)

    def step(self) -> TickRecord:
        """Execute one generation: tournament + replication."""
        # Reset fitness
        for agent in self.population:
            agent.reset_fitness()

        # Round-robin tournament (sample-based for large populations)
        n = len(self.population)
        if n <= 50:
            # Full round-robin
            for i in range(n):
                for j in range(i + 1, n):
                    self._play_match(self.population[i], self.population[j])
        else:
            # Sample opponents: each agent plays ~20 random opponents
            opponents_per_agent = min(20, n - 1)
            for i in range(n):
                indices = self.rng.choice(
                    [j for j in range(n) if j != i],
                    size=opponents_per_agent,
                    replace=False
                )
                for j in indices:
                    self._play_match(self.population[i], self.population[j])

        # Collect metrics
        record = self._collect_metrics()

        # Replication: proportional to fitness
        fitnesses = np.array([a.average_payoff for a in self.population])
        # Shift to make all positive
        min_fit = fitnesses.min()
        if min_fit < 0:
            fitnesses = fitnesses - min_fit + 0.01
        else:
            fitnesses = fitnesses + 0.01  # avoid zero

        total_fit = fitnesses.sum()
        probs = fitnesses / total_fit

        # Sample next generation
        indices = self.rng.choice(n, size=n, p=probs)
        new_population = []
        for idx in indices:
            parent = self.population[idx]
            new_type = parent.strategy_type

            # Mutation
            if self.mutation_rate > 0 and self.rng.random() < self.mutation_rate:
                all_types = list(StrategyType)
                new_type = self.rng.choice(all_types)

            new_strategy = Strategy(new_type, self.noise, self.rng)
            new_agent = Agent(id=self.next_id, strategy=new_strategy)
            self.next_id += 1
            new_population.append(new_agent)

        self.population = new_population
        self.history.append(record)
        self.current_generation += 1
        return record

    def _collect_metrics(self) -> TickRecord:
        """Collect metrics for the current generation."""
        total_coop = sum(a.total_cooperations for a in self.population)
        total_actions = sum(a.total_actions for a in self.population)
        total_payoff = sum(a.fitness for a in self.population)
        total_games = sum(a.games_played for a in self.population)

        strategy_counts = {st.value: 0 for st in StrategyType}
        for agent in self.population:
            strategy_counts[agent.strategy_type.value] += 1

        n = len(self.population)
        coop_rate = total_coop / max(total_actions, 1)
        avg_payoff = total_payoff / max(total_games, 1)

        strategy_fractions = {k: v / n for k, v in strategy_counts.items()}

        return TickRecord(
            generation=self.current_generation,
            cooperation_rate=coop_rate,
            average_payoff=avg_payoff,
            strategy_counts=strategy_counts,
            strategy_fractions=strategy_fractions,
        )

    def run(self, progress_callback: Optional[Callable] = None) -> list[TickRecord]:
        """Run the full simulation."""
        for g in range(self.generations):
            self.step()
            if progress_callback and g % 10 == 0:
                progress_callback(g, self.generations)
        return self.history

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        if not self.history:
            return {}

        coop_rates = [r.cooperation_rate for r in self.history]
        avg_payoffs = [r.average_payoff for r in self.history]
        final = self.history[-1]

        return {
            "mode": "tournament",
            "generations": self.current_generation,
            "population_size": self.population_size,
            "noise": self.noise,
            "mutation_rate": self.mutation_rate,
            "rounds_per_match": self.rounds_per_match,
            "final_cooperation_rate": final.cooperation_rate,
            "mean_cooperation_rate": float(np.mean(coop_rates)),
            "final_average_payoff": final.average_payoff,
            "mean_average_payoff": float(np.mean(avg_payoffs)),
            "final_strategy_fractions": final.strategy_fractions,
            "payoff_matrix": {
                "T": self.payoff_matrix.T,
                "R": self.payoff_matrix.R,
                "P": self.payoff_matrix.P,
                "S": self.payoff_matrix.S,
            },
        }


# ---------------------------------------------------------------------------
# Convenience: unified Simulation wrapper
# ---------------------------------------------------------------------------

class Simulation:
    """Unified interface for both spatial and tournament modes."""

    def __init__(self, mode: str = "spatial", grid_size: int = 50,
                 population_size: int = 100, rounds_per_match: int = 10,
                 noise: float = 0.0, mutation_rate: float = 0.001,
                 payoff_T: float = 5.0, payoff_R: float = 3.0,
                 payoff_P: float = 1.0, payoff_S: float = 0.0,
                 strategy_mix: Optional[dict] = None,
                 neighborhood: str = "moore",
                 generations: int = 200,
                 seed: Optional[int] = None):
        self.mode = mode
        payoff = PayoffMatrix(T=payoff_T, R=payoff_R, P=payoff_P, S=payoff_S)

        if mode == "spatial":
            self.sim = SpatialSimulation(
                grid_size=grid_size,
                rounds_per_match=rounds_per_match,
                noise=noise,
                mutation_rate=mutation_rate,
                payoff_matrix=payoff,
                strategy_mix=strategy_mix,
                neighborhood=neighborhood,
                generations=generations,
                seed=seed,
            )
        else:
            self.sim = TournamentSimulation(
                population_size=population_size,
                rounds_per_match=rounds_per_match,
                noise=noise,
                mutation_rate=mutation_rate,
                payoff_matrix=payoff,
                strategy_mix=strategy_mix,
                generations=generations,
                seed=seed,
            )

    def step(self) -> TickRecord:
        return self.sim.step()

    def run(self, progress_callback=None) -> list[TickRecord]:
        return self.sim.run(progress_callback)

    def get_statistics(self) -> dict:
        return self.sim.get_statistics()

    @property
    def history(self):
        return self.sim.history

    def to_csv(self, filename: str):
        """Write simulation history to CSV."""
        if not self.history:
            return

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["generation", "cooperation_rate", "average_payoff"]
            for st in StrategyType:
                header.append(f"frac_{st.short_name}")
            writer.writerow(header)

            for r in self.history:
                row = [
                    r.generation,
                    f"{r.cooperation_rate:.4f}",
                    f"{r.average_payoff:.4f}",
                ]
                for st in StrategyType:
                    row.append(f"{r.strategy_fractions.get(st.value, 0):.4f}")
                writer.writerow(row)

    def to_json(self) -> dict:
        """Export full simulation state as JSON-serializable dict."""
        stats = self.get_statistics()
        return {
            "params": stats,
            "history": [
                {
                    "generation": r.generation,
                    "cooperation_rate": round(r.cooperation_rate, 4),
                    "average_payoff": round(r.average_payoff, 4),
                    "strategy_fractions": {
                        k: round(v, 4) for k, v in r.strategy_fractions.items()
                    },
                }
                for r in self.history
            ],
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running Prisoner's Dilemma simulation (spatial mode)...")
    sim = Simulation(mode="spatial", grid_size=30, generations=50, seed=42,
                     noise=0.01, mutation_rate=0.001)
    sim.run(progress_callback=lambda g, n: print(f"  generation {g}/{n}"))
    stats = sim.get_statistics()
    print("\nResults:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        elif isinstance(v, dict):
            print(f"  {k}:")
            for k2, v2 in v.items():
                if isinstance(v2, float):
                    print(f"    {k2}: {v2:.4f}")
                else:
                    print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")
