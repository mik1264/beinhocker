"""
Business Plan Evolution Simulation

Based on Beinhocker's "The Origin of Wealth" Chapter 14 (pp.302-319):
Business Plans as the evolutionary units ("DNA") of the economy.

Key framework -- Wealth creation requires three G-R Conditions:
  1. Irreversibility -- transformations must be thermodynamically irreversible
  2. Entropy reduction -- must reduce entropy locally (create order)
  3. Fitness -- must produce artifacts/actions fit for human purposes

Each Business Plan encodes three components:
  - Physical Technology (PT): how to make things (production efficiency)
  - Social Technology (ST): how to organize people (coordination efficiency)
  - Strategy: market positioning and resource allocation

Fitness is multiplicative: PT_fitness x ST_fitness x market_fit
All three must be good -- a brilliant product with terrible organization fails,
and a well-run company making the wrong product also fails.

Evolution: successful BPs replicate with mutation/crossover, unsuccessful die.
Creative destruction emerges naturally as superior BPs displace incumbents.

References:
  - Beinhocker, "The Origin of Wealth" (2006), Chapter 14
  - Kauffman, "The Origins of Order" (1993) -- NK landscapes
  - Nelson & Winter, "An Evolutionary Theory of Economic Change" (1982)
  - Schumpeter, "Capitalism, Socialism and Democracy" (1942)
"""

import random
import math
import csv
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimConfig:
    """Configuration for the Business Plan evolution simulation."""
    population: int = 50            # Number of business plans
    ticks: int = 300                # Simulation duration
    pt_length: int = 8              # Physical Technology bit-string length
    st_length: int = 8              # Social Technology bit-string length
    strategy_length: int = 8        # Strategy bit-string length
    k_epistasis: int = 3            # Epistatic interactions within each component
    mutation_rate: float = 0.05     # Probability of bit flip per locus
    crossover_rate: float = 0.3     # Probability of crossover during replication
    preference_shift_rate: float = 0.02  # Rate at which market preferences change
    entry_rate: float = 0.03        # Probability of new BP entering per tick
    exit_fraction: float = 0.10     # Bottom fraction culled each tick
    seed: Optional[int] = None

    @property
    def total_length(self) -> int:
        return self.pt_length + self.st_length + self.strategy_length


@dataclass
class DestructionEvent:
    """Records a creative destruction event."""
    tick: int
    destroyed_id: int
    destroyer_id: int
    old_fitness: float
    new_fitness: float


@dataclass
class TickRecord:
    tick: int
    population: int
    total_wealth: float
    mean_fitness: float
    best_fitness: float
    mean_pt_fitness: float
    mean_st_fitness: float
    mean_strategy_fitness: float
    diversity: float
    gini: float
    destructions: int
    entries: int
    innovations: int


class NKComponent:
    """
    NK Fitness Landscape for a single component (PT, ST, or Strategy).

    N = number of binary loci
    K = epistatic interactions per locus (ruggedness)
    """

    def __init__(self, n: int, k: int, rng: random.Random):
        self.n = n
        self.k = min(k, n - 1)
        self.rng = rng

        # For each locus, choose K other loci that interact with it
        self.interactions: list[list[int]] = []
        for i in range(n):
            others = [j for j in range(n) if j != i]
            partners = sorted(rng.sample(others, self.k)) if self.k > 0 else []
            self.interactions.append(partners)

        # Fitness contribution table for each locus
        self.fitness_tables: list[dict[tuple, float]] = []
        for i in range(n):
            table = {}
            num_combos = 2 ** (self.k + 1)
            for combo_idx in range(num_combos):
                bits = tuple((combo_idx >> b) & 1 for b in range(self.k + 1))
                table[bits] = rng.random()
            self.fitness_tables.append(table)

    def fitness(self, bits: list[int]) -> float:
        """Compute fitness of a bit-string of length N. Returns value in [0, 1]."""
        total = 0.0
        for i in range(self.n):
            key_bits = [bits[i]]
            for partner in self.interactions[i]:
                key_bits.append(bits[partner])
            key = tuple(key_bits)
            total += self.fitness_tables[i][key]
        return total / self.n


class MarketEnvironment:
    """
    The market environment with consumer preferences that shift over time.

    Preferences are encoded as a target bit-string of strategy_length.
    Market fit is based on how closely a BP's strategy matches the demand.
    """

    def __init__(self, strategy_length: int, shift_rate: float, rng: random.Random):
        self.strategy_length = strategy_length
        self.shift_rate = shift_rate
        self.rng = rng
        # Initialize random preference vector
        self.preferences = [rng.randint(0, 1) for _ in range(strategy_length)]

    def shift(self):
        """Randomly shift some preferences each tick."""
        for i in range(self.strategy_length):
            if self.rng.random() < self.shift_rate:
                self.preferences[i] = 1 - self.preferences[i]

    def market_fit(self, strategy_bits: list[int]) -> float:
        """
        How well does a strategy match current market preferences?
        Returns value in (0, 1] -- never exactly 0 so multiplicative fitness
        doesn't annihilate everything.
        """
        if self.strategy_length == 0:
            return 1.0
        matches = sum(a == b for a, b in zip(strategy_bits, self.preferences))
        raw = matches / self.strategy_length
        # Map [0,1] to [0.1, 1.0] so even mismatched BPs have some minimal fitness
        return 0.1 + 0.9 * raw


class BusinessPlan:
    """
    A Business Plan -- the 'DNA' of the economy.

    Encodes three components as bit-strings:
      - Physical Technology (PT): production efficiency
      - Social Technology (ST): coordination efficiency
      - Strategy: market positioning
    """

    _next_id = 0

    def __init__(self, pt_bits: list[int], st_bits: list[int], strategy_bits: list[int]):
        self.id = BusinessPlan._next_id
        BusinessPlan._next_id += 1
        self.pt_bits = pt_bits
        self.st_bits = st_bits
        self.strategy_bits = strategy_bits
        self.age = 0
        self.market_share = 0.0

        # Fitness components (set externally)
        self.pt_fitness = 0.0
        self.st_fitness = 0.0
        self.strategy_fitness = 0.0
        self.total_fitness = 0.0

    @property
    def genome(self) -> list[int]:
        return self.pt_bits + self.st_bits + self.strategy_bits

    def copy_genome(self):
        return self.pt_bits.copy(), self.st_bits.copy(), self.strategy_bits.copy()

    @staticmethod
    def reset_id_counter():
        BusinessPlan._next_id = 0


class BusinessPlanSimulation:
    """
    Main simulation: a population of Business Plans evolves on a fitness landscape.

    Fitness = PT_fitness x ST_fitness x market_fit (multiplicative).
    Selection is proportional to fitness. Replication includes mutation and crossover.
    Creative destruction: low-fitness BPs die, new entrants can appear.
    """

    def __init__(self, config: SimConfig = None):
        if config is None:
            config = SimConfig()
        self.config = config

        BusinessPlan.reset_id_counter()
        self.rng = random.Random(config.seed)

        # Create NK landscapes for PT and ST components
        self.pt_landscape = NKComponent(config.pt_length, config.k_epistasis, self.rng)
        self.st_landscape = NKComponent(config.st_length, config.k_epistasis, self.rng)

        # Market environment for strategy fitness
        self.market = MarketEnvironment(config.strategy_length, config.preference_shift_rate, self.rng)

        self.population: list[BusinessPlan] = []
        self.tick = 0

        self.history: list[TickRecord] = []
        self.destruction_events: list[DestructionEvent] = []

        # Aggregate counters
        self.total_destructions = 0
        self.total_entries = 0
        self.total_innovations = 0

        self._initialize_population()

    def _random_bits(self, length: int) -> list[int]:
        return [self.rng.randint(0, 1) for _ in range(length)]

    def _initialize_population(self):
        """Create initial population of random Business Plans."""
        for _ in range(self.config.population):
            bp = BusinessPlan(
                pt_bits=self._random_bits(self.config.pt_length),
                st_bits=self._random_bits(self.config.st_length),
                strategy_bits=self._random_bits(self.config.strategy_length),
            )
            self._evaluate(bp)
            self.population.append(bp)
        self._compute_market_shares()

    def _evaluate(self, bp: BusinessPlan):
        """Evaluate the fitness of a business plan."""
        bp.pt_fitness = self.pt_landscape.fitness(bp.pt_bits)
        bp.st_fitness = self.st_landscape.fitness(bp.st_bits)
        bp.strategy_fitness = self.market.market_fit(bp.strategy_bits)
        # Multiplicative fitness -- all three must be good
        bp.total_fitness = bp.pt_fitness * bp.st_fitness * bp.strategy_fitness

    def _compute_market_shares(self):
        """Compute market shares proportional to fitness."""
        total_fitness = sum(bp.total_fitness for bp in self.population)
        if total_fitness <= 0:
            share = 1.0 / max(len(self.population), 1)
            for bp in self.population:
                bp.market_share = share
        else:
            for bp in self.population:
                bp.market_share = bp.total_fitness / total_fitness

    def _hamming_distance(self, a: list[int], b: list[int]) -> int:
        return sum(x != y for x, y in zip(a, b))

    def _population_diversity(self) -> float:
        """Average pairwise Hamming distance across full genomes, normalized to [0,1]."""
        if len(self.population) < 2:
            return 0.0
        total_dist = 0.0
        count = 0
        sample = self.population[:60]  # Cap for performance
        total_len = self.config.total_length
        for i in range(len(sample)):
            for j in range(i + 1, len(sample)):
                total_dist += self._hamming_distance(
                    sample[i].genome, sample[j].genome
                )
                count += 1
        return (total_dist / count) / total_len if count > 0 else 0.0

    def _gini_coefficient(self) -> float:
        """Compute Gini coefficient of market share distribution."""
        if len(self.population) < 2:
            return 0.0
        shares = sorted(bp.market_share for bp in self.population)
        n = len(shares)
        numerator = sum((2 * (i + 1) - n - 1) * shares[i] for i in range(n))
        denominator = n * sum(shares)
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _mutate(self, bits: list[int]) -> list[int]:
        """Apply random mutations to a bit-string."""
        mutated = bits.copy()
        for i in range(len(mutated)):
            if self.rng.random() < self.config.mutation_rate:
                mutated[i] = 1 - mutated[i]
        return mutated

    def _crossover(self, parent1_bits: list[int], parent2_bits: list[int]) -> list[int]:
        """Uniform crossover between two bit-strings."""
        child = []
        for i in range(len(parent1_bits)):
            if self.rng.random() < 0.5:
                child.append(parent1_bits[i])
            else:
                child.append(parent2_bits[i])
        return child

    def _select_parent(self) -> BusinessPlan:
        """Fitness-proportional selection (roulette wheel)."""
        total = sum(bp.total_fitness for bp in self.population)
        if total <= 0:
            return self.rng.choice(self.population)
        r = self.rng.random() * total
        cumulative = 0.0
        for bp in self.population:
            cumulative += bp.total_fitness
            if cumulative >= r:
                return bp
        return self.population[-1]

    def _replicate(self, parent: BusinessPlan) -> BusinessPlan:
        """Create offspring from a parent BP with mutation and optional crossover."""
        pt, st, strat = parent.copy_genome()

        # Crossover with another parent
        if self.rng.random() < self.config.crossover_rate and len(self.population) > 1:
            other = self._select_parent()
            while other.id == parent.id and len(self.population) > 1:
                other = self._select_parent()
            o_pt, o_st, o_strat = other.copy_genome()
            pt = self._crossover(pt, o_pt)
            st = self._crossover(st, o_st)
            strat = self._crossover(strat, o_strat)

        # Mutation
        pt = self._mutate(pt)
        st = self._mutate(st)
        strat = self._mutate(strat)

        child = BusinessPlan(pt_bits=pt, st_bits=st, strategy_bits=strat)
        self._evaluate(child)
        return child

    def _create_entrant(self) -> BusinessPlan:
        """Create a new entrant BP -- either random or recombined from existing."""
        if self.population and self.rng.random() < 0.5:
            # Recombine from two existing BPs
            p1 = self._select_parent()
            p2 = self._select_parent()
            pt1, st1, strat1 = p1.copy_genome()
            pt2, st2, strat2 = p2.copy_genome()
            pt = self._crossover(pt1, pt2)
            st = self._crossover(st1, st2)
            strat = self._crossover(strat1, strat2)
            pt = self._mutate(pt)
            st = self._mutate(st)
            strat = self._mutate(strat)
        else:
            # Fully random
            pt = self._random_bits(self.config.pt_length)
            st = self._random_bits(self.config.st_length)
            strat = self._random_bits(self.config.strategy_length)

        bp = BusinessPlan(pt_bits=pt, st_bits=st, strategy_bits=strat)
        self._evaluate(bp)
        return bp

    def step(self) -> TickRecord:
        """Execute one tick of the simulation."""
        self.tick += 1
        innovations = 0
        destructions = 0
        entries = 0

        # 1. Shift market preferences
        self.market.shift()

        # 2. Re-evaluate all BPs (market may have shifted)
        for bp in self.population:
            old_fitness = bp.total_fitness
            self._evaluate(bp)
            bp.age += 1

        # 3. Compute market shares
        self._compute_market_shares()

        # 4. Selection and replication: replace bottom fraction with offspring of top
        self.population.sort(key=lambda bp: bp.total_fitness)
        n_cull = max(1, int(len(self.population) * self.config.exit_fraction))

        # Record destruction events
        culled = self.population[:n_cull]
        survivors = self.population[n_cull:]

        if survivors:
            best_bp = survivors[-1]  # highest fitness
            for bp in culled:
                self.destruction_events.append(DestructionEvent(
                    tick=self.tick,
                    destroyed_id=bp.id,
                    destroyer_id=best_bp.id,
                    old_fitness=bp.total_fitness,
                    new_fitness=best_bp.total_fitness,
                ))
        destructions = len(culled)

        # Create offspring to replace culled BPs
        offspring = []
        for _ in range(n_cull):
            parent = self._select_parent()
            child = self._replicate(parent)
            if child.total_fitness > parent.total_fitness:
                innovations += 1
            offspring.append(child)

        self.population = survivors + offspring

        # 5. New entrants
        if self.rng.random() < self.config.entry_rate:
            entrant = self._create_entrant()
            self.population.append(entrant)
            entries += 1

        # 6. Recompute shares after population change
        self._compute_market_shares()

        # 7. Record statistics
        self.total_destructions += destructions
        self.total_entries += entries
        self.total_innovations += innovations

        fitnesses = [bp.total_fitness for bp in self.population]
        pt_fitnesses = [bp.pt_fitness for bp in self.population]
        st_fitnesses = [bp.st_fitness for bp in self.population]
        strat_fitnesses = [bp.strategy_fitness for bp in self.population]

        n = len(self.population)
        total_wealth = sum(bp.total_fitness * bp.market_share for bp in self.population)
        # Scale wealth by population size for a meaningful total
        total_wealth *= n

        record = TickRecord(
            tick=self.tick,
            population=n,
            total_wealth=total_wealth,
            mean_fitness=sum(fitnesses) / n if n > 0 else 0.0,
            best_fitness=max(fitnesses) if fitnesses else 0.0,
            mean_pt_fitness=sum(pt_fitnesses) / n if n > 0 else 0.0,
            mean_st_fitness=sum(st_fitnesses) / n if n > 0 else 0.0,
            mean_strategy_fitness=sum(strat_fitnesses) / n if n > 0 else 0.0,
            diversity=self._population_diversity(),
            gini=self._gini_coefficient(),
            destructions=destructions,
            entries=entries,
            innovations=innovations,
        )
        self.history.append(record)
        return record

    def run(self, ticks: int = None, callback=None) -> list[TickRecord]:
        """Run the simulation for the specified number of ticks."""
        if ticks is None:
            ticks = self.config.ticks
        for t in range(ticks):
            record = self.step()
            if callback:
                callback(self.tick, ticks, record)
        return self.history

    def get_state_json(self) -> dict:
        """Export current state for visualization."""
        bps_data = []
        for bp in self.population:
            bps_data.append({
                "id": bp.id,
                "pt_fitness": round(bp.pt_fitness, 4),
                "st_fitness": round(bp.st_fitness, 4),
                "strategy_fitness": round(bp.strategy_fitness, 4),
                "total_fitness": round(bp.total_fitness, 4),
                "market_share": round(bp.market_share, 6),
                "age": bp.age,
                "pt_bits": bp.pt_bits,
                "st_bits": bp.st_bits,
                "strategy_bits": bp.strategy_bits,
            })

        fitnesses = [bp.total_fitness for bp in self.population]
        n = len(self.population)
        return {
            "tick": self.tick,
            "business_plans": bps_data,
            "market_preferences": self.market.preferences,
            "stats": {
                "population": n,
                "total_wealth": round(sum(bp.total_fitness * bp.market_share for bp in self.population) * n, 4),
                "mean_fitness": round(sum(fitnesses) / n, 4) if n > 0 else 0.0,
                "best_fitness": round(max(fitnesses), 4) if fitnesses else 0.0,
                "mean_pt_fitness": round(sum(bp.pt_fitness for bp in self.population) / n, 4) if n > 0 else 0.0,
                "mean_st_fitness": round(sum(bp.st_fitness for bp in self.population) / n, 4) if n > 0 else 0.0,
                "mean_strategy_fitness": round(sum(bp.strategy_fitness for bp in self.population) / n, 4) if n > 0 else 0.0,
                "diversity": round(self._population_diversity(), 4),
                "gini": round(self._gini_coefficient(), 4),
                "total_destructions": self.total_destructions,
                "total_entries": self.total_entries,
                "total_innovations": self.total_innovations,
            },
        }

    def get_history_json(self) -> list[dict]:
        """Export history for visualization."""
        return [
            {
                "tick": r.tick,
                "population": r.population,
                "total_wealth": round(r.total_wealth, 4),
                "mean_fitness": round(r.mean_fitness, 4),
                "best_fitness": round(r.best_fitness, 4),
                "mean_pt_fitness": round(r.mean_pt_fitness, 4),
                "mean_st_fitness": round(r.mean_st_fitness, 4),
                "mean_strategy_fitness": round(r.mean_strategy_fitness, 4),
                "diversity": round(r.diversity, 4),
                "gini": round(r.gini, 4),
                "destructions": r.destructions,
                "entries": r.entries,
                "innovations": r.innovations,
            }
            for r in self.history
        ]

    def save_csv(self, filepath: str):
        """Save history to CSV."""
        if not self.history:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "population", "total_wealth", "mean_fitness", "best_fitness",
                "mean_pt_fitness", "mean_st_fitness", "mean_strategy_fitness",
                "diversity", "gini", "destructions", "entries", "innovations",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, r.population,
                    f"{r.total_wealth:.4f}", f"{r.mean_fitness:.4f}", f"{r.best_fitness:.4f}",
                    f"{r.mean_pt_fitness:.4f}", f"{r.mean_st_fitness:.4f}",
                    f"{r.mean_strategy_fitness:.4f}",
                    f"{r.diversity:.4f}", f"{r.gini:.4f}",
                    r.destructions, r.entries, r.innovations,
                ])

    def save_json(self, filepath: str):
        """Save full state and history to JSON."""
        data = {
            "config": {
                "population": self.config.population,
                "ticks": self.config.ticks,
                "pt_length": self.config.pt_length,
                "st_length": self.config.st_length,
                "strategy_length": self.config.strategy_length,
                "k_epistasis": self.config.k_epistasis,
                "mutation_rate": self.config.mutation_rate,
                "crossover_rate": self.config.crossover_rate,
                "preference_shift_rate": self.config.preference_shift_rate,
                "seed": self.config.seed,
            },
            "state": self.get_state_json(),
            "history": self.get_history_json(),
            "destruction_events": [
                {
                    "tick": e.tick,
                    "destroyed_id": e.destroyed_id,
                    "destroyer_id": e.destroyer_id,
                    "old_fitness": round(e.old_fitness, 4),
                    "new_fitness": round(e.new_fitness, 4),
                }
                for e in self.destruction_events
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
