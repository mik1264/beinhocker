"""
Strategy as Evolution: Portfolio-Based Competition Simulation

Based on Beinhocker's "The Origin of Wealth" (2006), Chapter 15.

Beinhocker argues that strategy is not about finding the one right answer
but about creating a portfolio of experiments. Firms compete by allocating
resources across strategic experiments targeting different market niches.
The fitness landscape shifts over time as consumer preferences change.

Three strategic archetypes:
  - Exploiters: concentrate resources on best-performing experiments
  - Explorers: spread resources widely, high mutation rate
  - Adaptive: mix of both, shift allocation based on performance feedback

Key finding: adaptive firms that maintain a portfolio of experiments
outperform both pure exploiters (efficient but fragile) and pure
explorers (robust but inefficient), especially in volatile markets.

References:
  - Beinhocker, "The Origin of Wealth" (2006), Ch. 15
  - March, "Exploration and Exploitation in Organizational Learning" (1991)
  - Levinthal & March, "The Myopia of Learning" (1993)
  - Gavetti & Levinthal, "Looking Forward and Looking Backward" (2000)
"""

import random
import csv
import json
import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimConfig:
    """Configuration for the strategy simulation."""
    num_firms: int = 30
    num_niches: int = 5
    ticks: int = 300
    shift_rate: float = 0.05        # probability a niche landscape shifts per tick
    exploiter_frac: float = 0.33    # fraction of firms that are exploiters
    explorer_frac: float = 0.33     # fraction that are explorers (rest are adaptive)
    experiments_per_firm: int = 6    # number of strategic experiments each firm holds
    mutation_rate: float = 0.1       # rate at which explorers generate new experiments
    resource_budget: float = 1.0     # total resource each firm allocates per tick
    exit_threshold: float = 0.15     # bottom fraction of firms that exit each tick
    seed: Optional[int] = None


@dataclass
class Experiment:
    """A strategic experiment / business initiative targeting a niche."""
    niche: int                       # which market niche this targets
    capability: float                # how well the firm executes in this niche [0,1]
    resources: float = 0.0           # fraction of firm resources allocated
    age: int = 0
    cumulative_fitness: float = 0.0


@dataclass
class Firm:
    """A firm competing via a portfolio of strategic experiments."""
    id: int
    firm_type: str                   # "exploiter", "explorer", or "adaptive"
    experiments: list                 # list of Experiment objects
    market_share: float = 0.0
    total_fitness: float = 0.0
    age: int = 0
    cumulative_fitness: float = 0.0
    alive: bool = True


@dataclass
class TickRecord:
    """One tick of simulation data for output."""
    tick: int
    # Survival counts by type
    exploiter_count: int
    explorer_count: int
    adaptive_count: int
    total_firms: int
    # Market share by type
    exploiter_share: float
    explorer_share: float
    adaptive_share: float
    # Fitness
    mean_fitness: float
    best_fitness: float
    exploiter_mean_fitness: float
    explorer_mean_fitness: float
    adaptive_mean_fitness: float
    # Concentration (HHI)
    hhi: float
    # Portfolio diversity (average niche coverage per firm)
    avg_portfolio_diversity: float
    # Niche coverage (fraction of niches with at least one firm)
    niche_coverage: float
    # Number of niche shifts this tick
    niche_shifts: int
    # Adaptation speed (how fast firms reallocate after shifts)
    avg_adaptation_speed: float


class NicheLandscape:
    """
    Market niches with shifting fitness landscapes.

    Each niche has an "ideal capability" that drifts over time.
    A firm's fitness in a niche depends on how close its capability
    is to the niche's ideal, weighted by resources allocated.
    """

    def __init__(self, num_niches: int, shift_rate: float, rng: random.Random):
        self.num_niches = num_niches
        self.shift_rate = shift_rate
        self.rng = rng
        # Each niche has an ideal capability value in [0,1]
        self.ideals = [rng.random() for _ in range(num_niches)]
        # Track how much each niche shifted this tick
        self.shifts_this_tick = 0
        # Niche attractiveness (market size) -- varies
        self.attractiveness = [0.5 + 0.5 * rng.random() for _ in range(num_niches)]
        self.total_shifts = 0

    def step(self):
        """Advance niche landscapes by one tick. Some niches may shift."""
        self.shifts_this_tick = 0
        for i in range(self.num_niches):
            if self.rng.random() < self.shift_rate:
                # Shift the ideal capability for this niche
                delta = self.rng.gauss(0, 0.15)
                self.ideals[i] = max(0.0, min(1.0, self.ideals[i] + delta))
                self.shifts_this_tick += 1
                self.total_shifts += 1
            # Attractiveness also drifts slowly
            if self.rng.random() < self.shift_rate * 0.5:
                delta = self.rng.gauss(0, 0.05)
                self.attractiveness[i] = max(0.2, min(1.0, self.attractiveness[i] + delta))

    def evaluate(self, experiment: Experiment) -> float:
        """
        Evaluate an experiment's fitness in its target niche.
        Fitness = attractiveness * gaussian_match(capability, ideal) * resources
        """
        niche = experiment.niche
        ideal = self.ideals[niche]
        attract = self.attractiveness[niche]
        # Gaussian match: closer capability to ideal = higher fitness
        distance = abs(experiment.capability - ideal)
        match_score = math.exp(-8.0 * distance * distance)
        return attract * match_score * experiment.resources


class StrategySimulation:
    """
    Main simulation engine for Strategy as Evolution.

    Each tick:
    1. Niche landscapes may shift
    2. Firms allocate resources across their experiments
    3. Fitness evaluated for all experiments
    4. Firms update based on feedback (type-dependent)
    5. Selection: worst firms exit, replaced by new entrants
    6. Metrics recorded
    """

    def __init__(self, config: SimConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.landscape = NicheLandscape(config.num_niches, config.shift_rate, self.rng)
        self.firms: list[Firm] = []
        self.history: list[TickRecord] = []
        self.current_tick = 0
        self.next_id = 0
        self.total_exits = 0
        self.total_entries = 0

        # Create initial firms
        self._create_initial_firms()

    def _create_initial_firms(self):
        """Create the initial population of firms."""
        n = self.config.num_firms
        n_exploiters = int(n * self.config.exploiter_frac)
        n_explorers = int(n * self.config.explorer_frac)
        n_adaptive = n - n_exploiters - n_explorers

        for _ in range(n_exploiters):
            self.firms.append(self._make_firm("exploiter"))
        for _ in range(n_explorers):
            self.firms.append(self._make_firm("explorer"))
        for _ in range(n_adaptive):
            self.firms.append(self._make_firm("adaptive"))

        # Shuffle so types are mixed
        self.rng.shuffle(self.firms)

    def _make_firm(self, firm_type: str) -> Firm:
        """Create a new firm with a random portfolio of experiments."""
        experiments = []
        for _ in range(self.config.experiments_per_firm):
            exp = Experiment(
                niche=self.rng.randint(0, self.config.num_niches - 1),
                capability=self.rng.random(),
                resources=1.0 / self.config.experiments_per_firm,
            )
            experiments.append(exp)

        firm = Firm(
            id=self.next_id,
            firm_type=firm_type,
            experiments=experiments,
        )
        self.next_id += 1
        return firm

    def _allocate_resources(self, firm: Firm, fitnesses: list[float]):
        """
        Allocate resources across experiments based on firm type.

        Exploiters: concentrate on the best experiment.
        Explorers: spread resources evenly.
        Adaptive: weighted allocation based on performance, with some exploration.
        """
        n_exp = len(firm.experiments)
        if n_exp == 0:
            return

        total_budget = self.config.resource_budget

        if firm.firm_type == "exploiter":
            # Put 70% on the best, distribute 30% among the rest
            if max(fitnesses) > 0:
                best_idx = fitnesses.index(max(fitnesses))
                for i, exp in enumerate(firm.experiments):
                    if i == best_idx:
                        exp.resources = total_budget * 0.7
                    else:
                        exp.resources = total_budget * 0.3 / max(n_exp - 1, 1)
            else:
                # No information yet -- spread evenly
                for exp in firm.experiments:
                    exp.resources = total_budget / n_exp

        elif firm.firm_type == "explorer":
            # Spread resources roughly evenly with slight randomness
            shares = [1.0 + self.rng.random() * 0.3 for _ in range(n_exp)]
            total_shares = sum(shares)
            for i, exp in enumerate(firm.experiments):
                exp.resources = total_budget * shares[i] / total_shares

        else:  # adaptive
            # Weighted by past fitness, but with a floor for exploration
            floor = 0.1 / n_exp  # minimum allocation per experiment
            if sum(fitnesses) > 0:
                weights = [max(f, 0.001) for f in fitnesses]
                total_w = sum(weights)
                for i, exp in enumerate(firm.experiments):
                    adaptive_share = (1.0 - floor * n_exp) * weights[i] / total_w + floor
                    exp.resources = total_budget * adaptive_share
            else:
                for exp in firm.experiments:
                    exp.resources = total_budget / n_exp

    def _mutate_portfolio(self, firm: Firm):
        """
        Mutate a firm's portfolio based on type.

        Explorers: high mutation rate -- frequently add/modify experiments.
        Adaptive: moderate mutation -- occasionally try new things.
        Exploiters: low mutation -- rarely change what works.
        """
        if firm.firm_type == "explorer":
            rate = self.config.mutation_rate * 2.0
        elif firm.firm_type == "adaptive":
            rate = self.config.mutation_rate
        else:
            rate = self.config.mutation_rate * 0.2

        for exp in firm.experiments:
            if self.rng.random() < rate:
                # Mutate: shift capability or retarget niche
                if self.rng.random() < 0.3:
                    # Retarget to a different niche
                    exp.niche = self.rng.randint(0, self.config.num_niches - 1)
                    exp.capability = self.rng.random()
                    exp.age = 0
                    exp.cumulative_fitness = 0.0
                else:
                    # Tweak capability
                    delta = self.rng.gauss(0, 0.1)
                    exp.capability = max(0.0, min(1.0, exp.capability + delta))

    def _compute_portfolio_diversity(self, firm: Firm) -> float:
        """Compute how many distinct niches a firm covers, normalized."""
        niches_covered = len(set(exp.niche for exp in firm.experiments))
        return niches_covered / self.config.num_niches

    def _compute_adaptation_speed(self, firm: Firm) -> float:
        """
        Measure how quickly a firm reallocates after niche shifts.
        Higher values mean more responsive resource reallocation.
        """
        if len(firm.experiments) < 2:
            return 0.0
        resources = [exp.resources for exp in firm.experiments]
        # Coefficient of variation of resource allocation
        mean_r = sum(resources) / len(resources)
        if mean_r == 0:
            return 0.0
        variance = sum((r - mean_r) ** 2 for r in resources) / len(resources)
        cv = math.sqrt(variance) / mean_r
        return cv

    def step(self) -> TickRecord:
        """Execute one simulation tick."""
        # 1. Advance niche landscapes
        self.landscape.step()

        # 2-3. Evaluate fitness and allocate resources
        for firm in self.firms:
            if not firm.alive:
                continue

            # Evaluate current fitness of each experiment
            fitnesses = [self.landscape.evaluate(exp) for exp in firm.experiments]

            # Allocate resources based on type and past performance
            self._allocate_resources(firm, fitnesses)

            # Re-evaluate with new resource allocation
            fitnesses = [self.landscape.evaluate(exp) for exp in firm.experiments]

            # Update firm fitness
            firm.total_fitness = sum(fitnesses)
            firm.cumulative_fitness += firm.total_fitness
            firm.age += 1

            # Update experiment ages and cumulative fitness
            for i, exp in enumerate(firm.experiments):
                exp.age += 1
                exp.cumulative_fitness += fitnesses[i]

        # 4. Mutate portfolios
        for firm in self.firms:
            if firm.alive:
                self._mutate_portfolio(firm)

        # 5. Selection: compute market shares and cull worst performers
        alive_firms = [f for f in self.firms if f.alive]
        total_fitness = sum(f.total_fitness for f in alive_firms)

        if total_fitness > 0:
            for firm in alive_firms:
                firm.market_share = firm.total_fitness / total_fitness
        else:
            for firm in alive_firms:
                firm.market_share = 1.0 / len(alive_firms) if alive_firms else 0.0

        # Exit: remove bottom fraction
        if len(alive_firms) > 3:
            alive_firms.sort(key=lambda f: f.total_fitness)
            n_exit = max(1, int(len(alive_firms) * self.config.exit_threshold))
            for firm in alive_firms[:n_exit]:
                firm.alive = False
                self.total_exits += 1

            # Replace with new firms (same type distribution as original)
            for _ in range(n_exit):
                r = self.rng.random()
                if r < self.config.exploiter_frac:
                    ftype = "exploiter"
                elif r < self.config.exploiter_frac + self.config.explorer_frac:
                    ftype = "explorer"
                else:
                    ftype = "adaptive"
                new_firm = self._make_firm(ftype)
                self.firms.append(new_firm)
                self.total_entries += 1

        # Remove dead firms from list
        self.firms = [f for f in self.firms if f.alive]

        # 6. Compute metrics
        alive_firms = self.firms
        n_total = len(alive_firms)

        type_counts = {"exploiter": 0, "explorer": 0, "adaptive": 0}
        type_shares = {"exploiter": 0.0, "explorer": 0.0, "adaptive": 0.0}
        type_fitness = {"exploiter": [], "explorer": [], "adaptive": []}

        for firm in alive_firms:
            type_counts[firm.firm_type] += 1
            type_shares[firm.firm_type] += firm.market_share
            type_fitness[firm.firm_type].append(firm.total_fitness)

        all_fitness = [f.total_fitness for f in alive_firms]
        mean_fit = sum(all_fitness) / n_total if n_total > 0 else 0.0
        best_fit = max(all_fitness) if all_fitness else 0.0

        def safe_mean(lst):
            return sum(lst) / len(lst) if lst else 0.0

        # HHI (Herfindahl-Hirschman Index) for market concentration
        hhi = sum(f.market_share ** 2 for f in alive_firms) if alive_firms else 0.0

        # Average portfolio diversity
        diversities = [self._compute_portfolio_diversity(f) for f in alive_firms]
        avg_diversity = safe_mean(diversities)

        # Niche coverage: fraction of niches with at least one firm
        covered_niches = set()
        for firm in alive_firms:
            for exp in firm.experiments:
                covered_niches.add(exp.niche)
        niche_cov = len(covered_niches) / self.config.num_niches if self.config.num_niches > 0 else 0.0

        # Average adaptation speed
        speeds = [self._compute_adaptation_speed(f) for f in alive_firms]
        avg_speed = safe_mean(speeds)

        record = TickRecord(
            tick=self.current_tick,
            exploiter_count=type_counts["exploiter"],
            explorer_count=type_counts["explorer"],
            adaptive_count=type_counts["adaptive"],
            total_firms=n_total,
            exploiter_share=type_shares["exploiter"],
            explorer_share=type_shares["explorer"],
            adaptive_share=type_shares["adaptive"],
            mean_fitness=mean_fit,
            best_fitness=best_fit,
            exploiter_mean_fitness=safe_mean(type_fitness["exploiter"]),
            explorer_mean_fitness=safe_mean(type_fitness["explorer"]),
            adaptive_mean_fitness=safe_mean(type_fitness["adaptive"]),
            hhi=hhi,
            avg_portfolio_diversity=avg_diversity,
            niche_coverage=niche_cov,
            niche_shifts=self.landscape.shifts_this_tick,
            avg_adaptation_speed=avg_speed,
        )

        self.history.append(record)
        self.current_tick += 1
        return record

    def run(self, callback=None) -> list[TickRecord]:
        """Run the full simulation."""
        for t in range(self.config.ticks):
            record = self.step()
            if callback:
                callback(t + 1, self.config.ticks, record)
        return self.history

    def get_summary(self) -> dict:
        """Return summary statistics of the simulation."""
        if not self.history:
            return {}

        last = self.history[-1]
        all_mean = [r.mean_fitness for r in self.history]
        all_best = [r.best_fitness for r in self.history]

        # Survival analysis: count how many of each type at end vs start
        first = self.history[0]

        # Average fitness by type over all ticks
        exp_fit = [r.exploiter_mean_fitness for r in self.history if r.exploiter_count > 0]
        exr_fit = [r.explorer_mean_fitness for r in self.history if r.explorer_count > 0]
        ada_fit = [r.adaptive_mean_fitness for r in self.history if r.adaptive_count > 0]

        def safe_mean(lst):
            return sum(lst) / len(lst) if lst else 0.0

        return {
            "ticks": self.config.ticks,
            "final_firms": last.total_firms,
            "final_exploiters": last.exploiter_count,
            "final_explorers": last.explorer_count,
            "final_adaptive": last.adaptive_count,
            "final_exploiter_share": round(last.exploiter_share, 4),
            "final_explorer_share": round(last.explorer_share, 4),
            "final_adaptive_share": round(last.adaptive_share, 4),
            "mean_fitness_avg": round(safe_mean(all_mean), 4),
            "best_fitness_final": round(last.best_fitness, 4),
            "mean_fitness_final": round(last.mean_fitness, 4),
            "exploiter_avg_fitness": round(safe_mean(exp_fit), 4),
            "explorer_avg_fitness": round(safe_mean(exr_fit), 4),
            "adaptive_avg_fitness": round(safe_mean(ada_fit), 4),
            "hhi_final": round(last.hhi, 4),
            "avg_portfolio_diversity": round(last.avg_portfolio_diversity, 4),
            "niche_coverage": round(last.niche_coverage, 4),
            "total_niche_shifts": self.landscape.total_shifts,
            "total_exits": self.total_exits,
            "total_entries": self.total_entries,
        }

    def to_csv(self, filename: str):
        """Write simulation history to CSV."""
        if not self.history:
            return

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            header = [
                "tick", "exploiter_count", "explorer_count", "adaptive_count",
                "total_firms", "exploiter_share", "explorer_share", "adaptive_share",
                "mean_fitness", "best_fitness",
                "exploiter_mean_fitness", "explorer_mean_fitness", "adaptive_mean_fitness",
                "hhi", "avg_portfolio_diversity", "niche_coverage",
                "niche_shifts", "avg_adaptation_speed",
            ]
            writer.writerow(header)

            for r in self.history:
                row = [
                    r.tick, r.exploiter_count, r.explorer_count, r.adaptive_count,
                    r.total_firms,
                    f"{r.exploiter_share:.4f}", f"{r.explorer_share:.4f}", f"{r.adaptive_share:.4f}",
                    f"{r.mean_fitness:.4f}", f"{r.best_fitness:.4f}",
                    f"{r.exploiter_mean_fitness:.4f}", f"{r.explorer_mean_fitness:.4f}",
                    f"{r.adaptive_mean_fitness:.4f}",
                    f"{r.hhi:.4f}", f"{r.avg_portfolio_diversity:.4f}",
                    f"{r.niche_coverage:.4f}",
                    r.niche_shifts, f"{r.avg_adaptation_speed:.4f}",
                ]
                writer.writerow(row)

    def to_json(self) -> dict:
        """Export full simulation state as JSON-serializable dict."""
        return {
            "params": {
                "num_firms": self.config.num_firms,
                "num_niches": self.config.num_niches,
                "ticks": self.config.ticks,
                "shift_rate": self.config.shift_rate,
                "exploiter_frac": self.config.exploiter_frac,
                "explorer_frac": self.config.explorer_frac,
                "experiments_per_firm": self.config.experiments_per_firm,
                "mutation_rate": self.config.mutation_rate,
                "exit_threshold": self.config.exit_threshold,
                "seed": self.config.seed,
            },
            "summary": self.get_summary(),
            "history": [
                {
                    "tick": r.tick,
                    "exploiter_count": r.exploiter_count,
                    "explorer_count": r.explorer_count,
                    "adaptive_count": r.adaptive_count,
                    "total_firms": r.total_firms,
                    "exploiter_share": round(r.exploiter_share, 4),
                    "explorer_share": round(r.explorer_share, 4),
                    "adaptive_share": round(r.adaptive_share, 4),
                    "mean_fitness": round(r.mean_fitness, 4),
                    "best_fitness": round(r.best_fitness, 4),
                    "exploiter_mean_fitness": round(r.exploiter_mean_fitness, 4),
                    "explorer_mean_fitness": round(r.explorer_mean_fitness, 4),
                    "adaptive_mean_fitness": round(r.adaptive_mean_fitness, 4),
                    "hhi": round(r.hhi, 4),
                    "avg_portfolio_diversity": round(r.avg_portfolio_diversity, 4),
                    "niche_coverage": round(r.niche_coverage, 4),
                    "niche_shifts": r.niche_shifts,
                    "avg_adaptation_speed": round(r.avg_adaptation_speed, 4),
                }
                for r in self.history
            ],
            "niche_ideals": [round(x, 4) for x in self.landscape.ideals],
            "niche_attractiveness": [round(x, 4) for x in self.landscape.attractiveness],
        }
