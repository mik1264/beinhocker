"""
Technology Evolution / Innovation Simulation on NK Fitness Landscapes

Based on Beinhocker's "The Origin of Wealth" coverage of how technologies evolve
through combinatorial search on rugged fitness landscapes. Firms explore the
landscape using different strategies (random search, local hill-climbing,
long-jump adaptation, recombination) while subject to creative destruction
and S-curve dynamics.

Key concepts:
  - NK Fitness Landscape: N binary technology dimensions with K epistatic
    interdependencies create a tunably rugged landscape
  - Search strategies: random, local (hill-climbing), long-jump, recombination
  - S-curve dynamics: technologies start slow, accelerate, then plateau
  - Creative destruction: superior technologies render old ones obsolete
  - Combinatorial innovation: new tech emerges by combining existing modules

References:
  - Kauffman, "The Origins of Order" (1993) -- NK landscapes
  - Beinhocker, "The Origin of Wealth" (2006), Chapters 9-12
  - Schumpeter, "Capitalism, Socialism and Democracy" (1942) -- creative destruction
  - Fleming & Sorenson, "Technology as a complex adaptive system" (2001)
"""

import random
import math
import csv
import json
import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SearchStrategy(Enum):
    RANDOM = "random"
    LOCAL = "local"
    LONG_JUMP = "long_jump"
    RECOMBINATION = "recombination"


class TechPhase(Enum):
    """Phase of a technology's S-curve lifecycle."""
    EMERGING = "emerging"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINING = "declining"


@dataclass
class SimConfig:
    """Configuration for the technology evolution simulation."""
    n: int = 12                         # Number of technology dimensions (bits)
    k: int = 4                          # Epistatic interdependencies (0..N-1)
    num_firms: int = 30                 # Number of firms
    ticks: int = 500                    # Simulation duration
    mutation_rate: float = 0.05         # Probability of random bit flip per dimension
    rd_budget: float = 0.3             # Fraction of fitness reinvested in R&D
    exploration_rate: float = 0.3       # Fraction of R&D spent on exploration vs exploitation
    entry_rate: float = 0.02            # Probability of new firm entering per tick
    exit_threshold: float = 0.15        # Firms below this relative fitness exit
    recombination_rate: float = 0.1     # Probability of recombination per tick for recomb firms
    long_jump_distance: int = 3         # Number of bits flipped in long-jump
    strategy_mix: dict = field(default_factory=lambda: {
        "random": 0.15,
        "local": 0.40,
        "long_jump": 0.25,
        "recombination": 0.20,
    })
    seed: Optional[int] = None


@dataclass
class Technology:
    """A technology represented as a bit-string on the NK landscape."""
    genome: list[int]           # Binary string of length N
    fitness: float = 0.0
    age: int = 0
    phase: TechPhase = TechPhase.EMERGING
    peak_fitness: float = 0.0   # Highest fitness achieved (for S-curve tracking)
    cumulative_adopters: int = 0


@dataclass
class Firm:
    """A firm that searches the technology landscape."""
    id: int
    strategy: SearchStrategy
    technology: Technology
    rd_budget: float = 0.0
    age: int = 0
    alive: bool = True
    innovations: int = 0        # Count of fitness improvements found
    peak_fitness: float = 0.0


@dataclass
class SCurveEvent:
    """Records an S-curve transition."""
    tick: int
    firm_id: int
    old_phase: str
    new_phase: str
    fitness: float


@dataclass
class DestructionEvent:
    """Records a creative destruction event."""
    tick: int
    destroyed_firm_id: int
    destroyer_firm_id: int
    old_fitness: float
    new_fitness: float


@dataclass
class TickRecord:
    tick: int
    num_firms: int
    best_fitness: float
    mean_fitness: float
    median_fitness: float
    tech_diversity: float           # Hamming diversity among technologies
    strategy_counts: dict           # Count of firms per strategy
    firms_entered: int
    firms_exited: int
    innovations_this_tick: int
    scurve_transitions: int
    dominant_strategy: str
    mean_age: float


class NKLandscape:
    """
    NK Fitness Landscape.

    N = number of binary loci (technology dimensions)
    K = number of epistatic interactions per locus (ruggedness)

    When K=0, the landscape is smooth (Mt. Fuji).
    When K=N-1, the landscape is fully random (maximally rugged).
    """

    def __init__(self, n: int, k: int, rng: random.Random):
        self.n = n
        self.k = min(k, n - 1)  # K cannot exceed N-1
        self.rng = rng

        # For each locus i, choose K other loci that interact with it
        self.interactions: list[list[int]] = []
        for i in range(n):
            others = [j for j in range(n) if j != i]
            partners = sorted(rng.sample(others, self.k)) if self.k > 0 else []
            self.interactions.append(partners)

        # Fitness contribution table for each locus
        # For locus i, the fitness depends on its own value plus K partner values
        # Total combinations = 2^(K+1)
        self.fitness_tables: list[dict[tuple, float]] = []
        for i in range(n):
            table = {}
            num_combos = 2 ** (self.k + 1)
            for combo_idx in range(num_combos):
                bits = tuple((combo_idx >> b) & 1 for b in range(self.k + 1))
                table[bits] = rng.random()
            self.fitness_tables.append(table)

    def fitness(self, genome: list[int]) -> float:
        """Compute fitness of a genome (bit string of length N)."""
        total = 0.0
        for i in range(self.n):
            # Build the key: locus i value + partner values
            key_bits = [genome[i]]
            for partner in self.interactions[i]:
                key_bits.append(genome[partner])
            key = tuple(key_bits)
            total += self.fitness_tables[i][key]
        return total / self.n  # Normalize to [0, 1]

    def neighbors(self, genome: list[int]) -> list[list[int]]:
        """Return all 1-bit Hamming neighbors."""
        result = []
        for i in range(self.n):
            neighbor = genome.copy()
            neighbor[i] = 1 - neighbor[i]
            result.append(neighbor)
        return result

    def get_2d_projection(self, resolution: int = 32) -> list[list[float]]:
        """
        Create a 2D fitness heatmap by varying the first two dimensions
        across a grid, while keeping other dimensions at a reference point.

        For visualization: maps 2 continuous axes (via Gray-code-like interpolation)
        onto the discrete landscape.
        """
        # Use first two bits as axes, average over all combos of remaining bits
        heatmap = []
        n_remaining = self.n - 2
        # Sample a subset of remaining bit configurations to average over
        if n_remaining <= 8:
            remaining_configs = list(itertools.product([0, 1], repeat=n_remaining))
        else:
            remaining_configs = []
            for _ in range(64):
                config = [self.rng.randint(0, 1) for _ in range(n_remaining)]
                remaining_configs.append(config)

        for row in range(resolution):
            row_data = []
            bit0 = 1 if row >= resolution // 2 else 0
            for col in range(resolution):
                bit1 = 1 if col >= resolution // 2 else 0
                # Average fitness across remaining configurations
                total_f = 0.0
                for remaining in remaining_configs:
                    genome = [bit0, bit1] + list(remaining)
                    total_f += self.fitness(genome)
                avg_f = total_f / len(remaining_configs)
                row_data.append(round(avg_f, 4))
            heatmap.append(row_data)
        return heatmap


class TechEvolutionSimulation:
    """
    Main simulation: firms search an NK fitness landscape using
    different strategies, subject to creative destruction and S-curve dynamics.
    """

    def __init__(self, config: SimConfig = None):
        if config is None:
            config = SimConfig()
        self.config = config

        self.rng = random.Random(config.seed)
        self.landscape = NKLandscape(config.n, config.k, self.rng)

        self.firms: list[Firm] = []
        self.dead_firms: list[Firm] = []
        self.tick = 0
        self.next_firm_id = 0

        self.history: list[TickRecord] = []
        self.scurve_events: list[SCurveEvent] = []
        self.destruction_events: list[DestructionEvent] = []

        # Track the global best technology ever found
        self.global_best_fitness = 0.0
        self.global_best_genome: list[int] = []

        # Total innovations and destruction counters
        self.total_innovations = 0
        self.total_destructions = 0
        self.total_entries = 0
        self.total_exits = 0

        self._initialize_firms()

    def _initialize_firms(self):
        """Create initial population of firms with random technologies."""
        strategy_list = []
        for strat_name, fraction in self.config.strategy_mix.items():
            count = max(1, int(self.config.num_firms * fraction))
            strategy = SearchStrategy(strat_name)
            strategy_list.extend([strategy] * count)

        # Pad or trim to exact num_firms
        while len(strategy_list) < self.config.num_firms:
            strategy_list.append(self.rng.choice(list(SearchStrategy)))
        self.rng.shuffle(strategy_list)
        strategy_list = strategy_list[:self.config.num_firms]

        for i in range(self.config.num_firms):
            genome = [self.rng.randint(0, 1) for _ in range(self.config.n)]
            fitness = self.landscape.fitness(genome)
            tech = Technology(genome=genome, fitness=fitness, peak_fitness=fitness)
            firm = Firm(
                id=self.next_firm_id,
                strategy=strategy_list[i],
                technology=tech,
                rd_budget=self.config.rd_budget,
                peak_fitness=fitness,
            )
            self.firms.append(firm)
            self.next_firm_id += 1

            if fitness > self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best_genome = genome.copy()

    def _random_genome(self) -> list[int]:
        return [self.rng.randint(0, 1) for _ in range(self.config.n)]

    def _hamming_distance(self, a: list[int], b: list[int]) -> int:
        return sum(x != y for x, y in zip(a, b))

    def _tech_diversity(self) -> float:
        """Average pairwise Hamming distance normalized to [0,1]."""
        if len(self.firms) < 2:
            return 0.0
        total_dist = 0.0
        count = 0
        firms = self.firms[:50]  # Cap for performance
        for i in range(len(firms)):
            for j in range(i + 1, len(firms)):
                total_dist += self._hamming_distance(
                    firms[i].technology.genome,
                    firms[j].technology.genome,
                )
                count += 1
        return (total_dist / count) / self.config.n if count > 0 else 0.0

    def _classify_scurve_phase(self, firm: Firm) -> TechPhase:
        """
        Determine S-curve phase based on fitness trajectory.
        - Emerging: low fitness, early age
        - Growth: fitness rising, middle age
        - Mature: fitness near peak, old age
        - Declining: fitness dropping relative to global best
        """
        tech = firm.technology
        relative_fitness = tech.fitness / max(self.global_best_fitness, 0.001)

        if tech.age < 10:
            if relative_fitness < 0.5:
                return TechPhase.EMERGING
            else:
                return TechPhase.GROWTH

        if tech.fitness < tech.peak_fitness * 0.8 and tech.age > 20:
            return TechPhase.DECLINING

        if relative_fitness > 0.85 and tech.age > 15:
            return TechPhase.MATURE

        if tech.fitness > tech.peak_fitness * 0.9:
            return TechPhase.GROWTH

        return TechPhase.EMERGING

    def _search_random(self, firm: Firm) -> Optional[list[int]]:
        """Random search: try a completely random technology."""
        return self._random_genome()

    def _search_local(self, firm: Firm) -> Optional[list[int]]:
        """Local hill-climbing: try all 1-bit neighbors, pick the best."""
        neighbors = self.landscape.neighbors(firm.technology.genome)
        best_genome = None
        best_fitness = firm.technology.fitness
        for neighbor in neighbors:
            f = self.landscape.fitness(neighbor)
            if f > best_fitness:
                best_fitness = f
                best_genome = neighbor
        return best_genome

    def _search_long_jump(self, firm: Firm) -> Optional[list[int]]:
        """Long-jump adaptation: flip several bits at once."""
        genome = firm.technology.genome.copy()
        positions = self.rng.sample(
            range(self.config.n),
            min(self.config.long_jump_distance, self.config.n),
        )
        for pos in positions:
            genome[pos] = 1 - genome[pos]
        return genome

    def _search_recombination(self, firm: Firm) -> Optional[list[int]]:
        """Recombination: combine technology with another firm's technology."""
        if len(self.firms) < 2:
            return None
        other = self.rng.choice(self.firms)
        while other.id == firm.id and len(self.firms) > 1:
            other = self.rng.choice(self.firms)

        # Uniform crossover
        child = []
        for i in range(self.config.n):
            if self.rng.random() < 0.5:
                child.append(firm.technology.genome[i])
            else:
                child.append(other.technology.genome[i])
        return child

    def _apply_mutation(self, genome: list[int]) -> list[int]:
        """Apply random mutations."""
        mutated = genome.copy()
        for i in range(len(mutated)):
            if self.rng.random() < self.config.mutation_rate:
                mutated[i] = 1 - mutated[i]
        return mutated

    def _firm_search(self, firm: Firm) -> bool:
        """
        Have a firm search for a new technology.
        Returns True if an innovation (fitness improvement) was found.
        """
        # Choose search method based on strategy
        if firm.strategy == SearchStrategy.RANDOM:
            candidate = self._search_random(firm)
        elif firm.strategy == SearchStrategy.LOCAL:
            candidate = self._search_local(firm)
        elif firm.strategy == SearchStrategy.LONG_JUMP:
            candidate = self._search_long_jump(firm)
        elif firm.strategy == SearchStrategy.RECOMBINATION:
            candidate = self._search_recombination(firm)
        else:
            candidate = None

        if candidate is None:
            return False

        # Apply mutation
        candidate = self._apply_mutation(candidate)

        # Evaluate
        new_fitness = self.landscape.fitness(candidate)

        # For local strategy: only accept improvements
        # For others: accept with probability based on fitness difference
        accept = False
        if firm.strategy == SearchStrategy.LOCAL:
            accept = new_fitness > firm.technology.fitness
        elif firm.strategy == SearchStrategy.RANDOM:
            # Accept if better, or with small probability if worse
            if new_fitness > firm.technology.fitness:
                accept = True
            else:
                accept = self.rng.random() < 0.05
        else:
            # Long-jump and recombination: accept if better
            accept = new_fitness > firm.technology.fitness

        if accept:
            old_fitness = firm.technology.fitness
            firm.technology.genome = candidate
            firm.technology.fitness = new_fitness
            firm.technology.age = 0  # Reset tech age on new innovation
            if new_fitness > firm.technology.peak_fitness:
                firm.technology.peak_fitness = new_fitness
            if new_fitness > firm.peak_fitness:
                firm.peak_fitness = new_fitness
            firm.innovations += 1

            # Update global best
            if new_fitness > self.global_best_fitness:
                self.global_best_fitness = new_fitness
                self.global_best_genome = candidate.copy()

            return True

        return False

    def _creative_destruction(self) -> tuple[int, int]:
        """
        Creative destruction: firms with significantly better technology
        can push inferior firms out of the market.
        Returns (firms_entered, firms_exited).
        """
        if not self.firms:
            return 0, 0

        firms_exited = 0
        mean_fitness = sum(f.technology.fitness for f in self.firms) / len(self.firms)
        best_fitness = max(f.technology.fitness for f in self.firms)

        # Exit: firms far below the frontier are destroyed
        threshold = max(
            mean_fitness * self.config.exit_threshold / 0.15,
            best_fitness * self.config.exit_threshold,
        )
        to_remove = []
        for firm in self.firms:
            if firm.technology.fitness < threshold and firm.age > 5:
                # Probability of exit increases with fitness gap
                gap = (threshold - firm.technology.fitness) / max(threshold, 0.001)
                if self.rng.random() < gap * 0.5:
                    to_remove.append(firm)

        for firm in to_remove:
            firm.alive = False
            self.dead_firms.append(firm)
            self.firms.remove(firm)
            firms_exited += 1

            # Find the best firm as the "destroyer"
            if self.firms:
                best_firm = max(self.firms, key=lambda f: f.technology.fitness)
                self.destruction_events.append(DestructionEvent(
                    tick=self.tick,
                    destroyed_firm_id=firm.id,
                    destroyer_firm_id=best_firm.id,
                    old_fitness=firm.technology.fitness,
                    new_fitness=best_firm.technology.fitness,
                ))

        # Entry: new firms enter with some probability
        firms_entered = 0
        if self.rng.random() < self.config.entry_rate or len(self.firms) < self.config.num_firms * 0.5:
            # New entrant with random strategy
            strategies = list(SearchStrategy)
            strategy = self.rng.choice(strategies)

            # New entrant can either start with random tech or recombine from existing
            if self.firms and self.rng.random() < 0.6:
                # Recombine from two existing firms
                parent1 = self.rng.choice(self.firms)
                parent2 = self.rng.choice(self.firms)
                genome = []
                for i in range(self.config.n):
                    if self.rng.random() < 0.5:
                        genome.append(parent1.technology.genome[i])
                    else:
                        genome.append(parent2.technology.genome[i])
                genome = self._apply_mutation(genome)
            else:
                genome = self._random_genome()

            fitness = self.landscape.fitness(genome)
            tech = Technology(genome=genome, fitness=fitness, peak_fitness=fitness)
            new_firm = Firm(
                id=self.next_firm_id,
                strategy=strategy,
                technology=tech,
                rd_budget=self.config.rd_budget,
                peak_fitness=fitness,
            )
            self.firms.append(new_firm)
            self.next_firm_id += 1
            firms_entered += 1

        self.total_entries += firms_entered
        self.total_exits += firms_exited
        return firms_entered, firms_exited

    def step(self) -> TickRecord:
        """Execute one tick of the simulation."""
        self.tick += 1
        innovations_this_tick = 0
        scurve_transitions = 0

        # Age all firms and their technologies
        for firm in self.firms:
            firm.age += 1
            firm.technology.age += 1

        # Each firm searches
        for firm in self.firms:
            if self._firm_search(firm):
                innovations_this_tick += 1
                self.total_innovations += 1

        # Update S-curve phases
        for firm in self.firms:
            old_phase = firm.technology.phase
            new_phase = self._classify_scurve_phase(firm)
            if new_phase != old_phase:
                firm.technology.phase = new_phase
                scurve_transitions += 1
                self.scurve_events.append(SCurveEvent(
                    tick=self.tick,
                    firm_id=firm.id,
                    old_phase=old_phase.value,
                    new_phase=new_phase.value,
                    fitness=firm.technology.fitness,
                ))

        # Creative destruction
        firms_entered, firms_exited = self._creative_destruction()
        self.total_destructions += firms_exited

        # Record tick
        strategy_counts = {}
        for strat in SearchStrategy:
            strategy_counts[strat.value] = sum(
                1 for f in self.firms if f.strategy == strat
            )

        fitnesses = [f.technology.fitness for f in self.firms] if self.firms else [0.0]
        sorted_f = sorted(fitnesses)
        median_f = sorted_f[len(sorted_f) // 2]
        dominant = max(strategy_counts, key=strategy_counts.get) if strategy_counts else "none"

        record = TickRecord(
            tick=self.tick,
            num_firms=len(self.firms),
            best_fitness=max(fitnesses),
            mean_fitness=sum(fitnesses) / len(fitnesses),
            median_fitness=median_f,
            tech_diversity=self._tech_diversity(),
            strategy_counts=strategy_counts,
            firms_entered=firms_entered,
            firms_exited=firms_exited,
            innovations_this_tick=innovations_this_tick,
            scurve_transitions=scurve_transitions,
            dominant_strategy=dominant,
            mean_age=sum(f.age for f in self.firms) / max(len(self.firms), 1),
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
        firms_data = []
        for firm in self.firms:
            # Compute a 2D position from the genome for visualization
            # Use first N/2 bits for x, second N/2 bits for y
            half = self.config.n // 2
            x_bits = firm.technology.genome[:half]
            y_bits = firm.technology.genome[half:]
            x = sum(b * (2 ** i) for i, b in enumerate(x_bits)) / (2 ** half - 1) if half > 0 else 0.5
            y = sum(b * (2 ** i) for i, b in enumerate(y_bits)) / (2 ** half - 1) if half > 0 else 0.5

            firms_data.append({
                "id": firm.id,
                "strategy": firm.strategy.value,
                "fitness": round(firm.technology.fitness, 4),
                "genome": firm.technology.genome,
                "x": round(x, 4),
                "y": round(y, 4),
                "age": firm.age,
                "tech_age": firm.technology.age,
                "phase": firm.technology.phase.value,
                "innovations": firm.innovations,
                "peak_fitness": round(firm.peak_fitness, 4),
                "alive": firm.alive,
            })

        fitnesses = [f.technology.fitness for f in self.firms] if self.firms else [0.0]
        strategy_counts = {}
        phase_counts = {}
        for strat in SearchStrategy:
            strategy_counts[strat.value] = sum(1 for f in self.firms if f.strategy == strat)
        for phase in TechPhase:
            phase_counts[phase.value] = sum(1 for f in self.firms if f.technology.phase == phase)

        return {
            "tick": self.tick,
            "firms": firms_data,
            "stats": {
                "num_firms": len(self.firms),
                "best_fitness": round(max(fitnesses), 4),
                "mean_fitness": round(sum(fitnesses) / len(fitnesses), 4),
                "global_best_fitness": round(self.global_best_fitness, 4),
                "tech_diversity": round(self._tech_diversity(), 4),
                "total_innovations": self.total_innovations,
                "total_destructions": self.total_destructions,
                "total_entries": self.total_entries,
                "total_exits": self.total_exits,
                "strategy_counts": strategy_counts,
                "phase_counts": phase_counts,
            },
        }

    def get_history_json(self) -> list[dict]:
        """Export history for visualization."""
        return [
            {
                "tick": r.tick,
                "num_firms": r.num_firms,
                "best_fitness": round(r.best_fitness, 4),
                "mean_fitness": round(r.mean_fitness, 4),
                "median_fitness": round(r.median_fitness, 4),
                "tech_diversity": round(r.tech_diversity, 4),
                "strategy_counts": r.strategy_counts,
                "firms_entered": r.firms_entered,
                "firms_exited": r.firms_exited,
                "innovations_this_tick": r.innovations_this_tick,
                "scurve_transitions": r.scurve_transitions,
                "dominant_strategy": r.dominant_strategy,
                "mean_age": round(r.mean_age, 2),
            }
            for r in self.history
        ]

    def get_landscape_heatmap(self, resolution: int = 32) -> list[list[float]]:
        """Get 2D projection of the fitness landscape for visualization."""
        return self.landscape.get_2d_projection(resolution)

    def save_csv(self, filepath: str):
        """Save history to CSV."""
        if not self.history:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "num_firms", "best_fitness", "mean_fitness",
                "median_fitness", "tech_diversity", "firms_entered",
                "firms_exited", "innovations", "scurve_transitions",
                "dominant_strategy", "mean_age",
                "random_count", "local_count", "long_jump_count", "recombination_count",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, r.num_firms,
                    f"{r.best_fitness:.4f}", f"{r.mean_fitness:.4f}",
                    f"{r.median_fitness:.4f}", f"{r.tech_diversity:.4f}",
                    r.firms_entered, r.firms_exited,
                    r.innovations_this_tick, r.scurve_transitions,
                    r.dominant_strategy, f"{r.mean_age:.2f}",
                    r.strategy_counts.get("random", 0),
                    r.strategy_counts.get("local", 0),
                    r.strategy_counts.get("long_jump", 0),
                    r.strategy_counts.get("recombination", 0),
                ])

    def save_json(self, filepath: str):
        """Save full state and history to JSON."""
        data = {
            "config": {
                "n": self.config.n,
                "k": self.config.k,
                "num_firms": self.config.num_firms,
                "mutation_rate": self.config.mutation_rate,
                "rd_budget": self.config.rd_budget,
                "exploration_rate": self.config.exploration_rate,
                "seed": self.config.seed,
            },
            "state": self.get_state_json(),
            "history": self.get_history_json(),
            "scurve_events": [
                {
                    "tick": e.tick,
                    "firm_id": e.firm_id,
                    "old_phase": e.old_phase,
                    "new_phase": e.new_phase,
                    "fitness": round(e.fitness, 4),
                }
                for e in self.scurve_events
            ],
            "destruction_events": [
                {
                    "tick": e.tick,
                    "destroyed_firm_id": e.destroyed_firm_id,
                    "destroyer_firm_id": e.destroyer_firm_id,
                    "old_fitness": round(e.old_fitness, 4),
                    "new_fitness": round(e.new_fitness, 4),
                }
                for e in self.destruction_events
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
