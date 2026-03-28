"""
Public Policy Simulation
========================
Models an economy where different policy regimes affect evolutionary dynamics
among competing firms on a fitness landscape. Based on Beinhocker Ch.18:
"Policy in a Complex World" -- the argument that policy should enable
evolutionary fitness rather than engineer specific outcomes.

Core mechanics:
  - N firms evolve on an NK-style fitness landscape
  - Firms innovate (mutation), compete for market share, can fail and be replaced
  - Policy levers modify entry barriers, compliance costs, mutation rates,
    market share caps, and safety net strength
  - Different policy regimes (presets) combine these levers

Key metrics:
  - GDP (total output), innovation rate, inequality (Gini), firm turnover,
    unemployment, long-run growth rate

References:
  - Beinhocker (2006), The Origin of Wealth, Chapter 18
  - Kauffman (1993), NK fitness landscapes
  - Nelson & Winter (1982), Evolutionary Theory of Economic Change
"""

from __future__ import annotations

import random
import math
import csv
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Configuration for the public policy simulation."""
    # Economy size
    num_firms: int = 50
    num_ticks: int = 500

    # Fitness landscape
    genome_length: int = 12          # bits in firm's strategy genome
    landscape_k: int = 3             # epistatic interactions (NK model)
    landscape_ruggedness: float = 0.5  # 0=smooth, 1=maximally rugged

    # Firm dynamics
    base_mutation_rate: float = 0.05   # per-locus mutation probability
    crossover_rate: float = 0.1        # probability of crossover per tick
    base_entry_cost: float = 0.3       # cost to enter market (fraction of initial capital)
    base_operating_cost: float = 0.05  # per-tick operating cost fraction

    # Policy levers (0.0 to 1.0 scale)
    regulation: float = 0.3           # raises entry barriers and compliance cost
    tax_rate: float = 0.2             # fraction of output redistributed
    innovation_subsidy: float = 0.0   # boosts mutation rate
    competition_limit: float = 1.0    # max market share (1.0 = no limit, 0.1 = 10% cap)
    safety_net: float = 0.3           # how quickly failed firms' workers re-enter

    # Random seed
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Fitness Landscape (NK model)
# ---------------------------------------------------------------------------

class FitnessLandscape:
    """NK fitness landscape for firm strategies.

    Each firm has a binary genome of length N. Fitness of each locus depends
    on K other loci, creating epistatic interactions that control ruggedness.
    """

    def __init__(self, n: int, k: int, ruggedness: float, rng: random.Random):
        self.n = n
        self.k = min(k, n - 1)
        self.rng = rng
        self.ruggedness = ruggedness

        # For each locus, which other loci affect its fitness contribution
        self.interactions: List[List[int]] = []
        for i in range(n):
            others = [j for j in range(n) if j != i]
            rng.shuffle(others)
            self.interactions.append(others[:self.k])

        # Fitness lookup tables: for each locus, map (locus_val, interacting_vals) -> fitness
        # With K interactions, there are 2^(K+1) possible input combinations
        self.tables: List[Dict[tuple, float]] = []
        for i in range(n):
            table = {}
            num_combos = 2 ** (self.k + 1)
            for combo_int in range(num_combos):
                bits = tuple((combo_int >> b) & 1 for b in range(self.k + 1))
                # Mix smooth and rugged components
                smooth = sum(bits) / (self.k + 1)
                rugged = rng.random()
                table[bits] = (1.0 - ruggedness) * smooth + ruggedness * rugged
            self.tables.append(table)

    def evaluate(self, genome: List[int]) -> float:
        """Compute fitness of a genome (0 to 1)."""
        total = 0.0
        for i in range(self.n):
            key_bits = [genome[i]]
            for j in self.interactions[i]:
                key_bits.append(genome[j])
            key = tuple(key_bits)
            total += self.tables[i].get(key, 0.5)
        return total / self.n

    def get_local_optima_count(self, sample_size: int = 200) -> int:
        """Estimate number of local optima by sampling random genomes."""
        optima = 0
        for _ in range(sample_size):
            genome = [self.rng.randint(0, 1) for _ in range(self.n)]
            fitness = self.evaluate(genome)
            is_optimum = True
            for i in range(self.n):
                neighbor = genome.copy()
                neighbor[i] = 1 - neighbor[i]
                if self.evaluate(neighbor) > fitness:
                    is_optimum = False
                    break
            if is_optimum:
                optima += 1
        return optima


# ---------------------------------------------------------------------------
# Firm
# ---------------------------------------------------------------------------

class Firm:
    """A firm competing on the fitness landscape.

    Each firm has a binary genome (strategy), fitness, capital, output,
    and market share. Policy affects costs, innovation rates, and survival.
    """

    def __init__(self, firm_id: int, genome: List[int], fitness: float,
                 capital: float, rng: random.Random):
        self.id = firm_id
        self.genome = genome
        self.fitness = fitness
        self.capital = capital
        self.output = 0.0
        self.market_share = 0.0
        self.age = 0
        self.alive = True
        self.rng = rng

        # Track innovation events
        self.innovations = 0
        self.last_innovation_tick = -1

    def mutate(self, mutation_rate: float, landscape: FitnessLandscape) -> bool:
        """Attempt mutation on genome. Returns True if fitness improved."""
        old_fitness = self.fitness
        old_genome = self.genome.copy()
        mutated = False

        for i in range(len(self.genome)):
            if self.rng.random() < mutation_rate:
                self.genome[i] = 1 - self.genome[i]
                mutated = True

        if mutated:
            new_fitness = landscape.evaluate(self.genome)
            if new_fitness >= old_fitness:
                self.fitness = new_fitness
                if new_fitness > old_fitness + 0.01:
                    self.innovations += 1
                    return True
                return False
            else:
                # Revert (firms keep beneficial mutations only)
                self.genome = old_genome
                self.fitness = old_fitness
                return False
        return False

    def crossover(self, other: 'Firm', landscape: FitnessLandscape,
                  rng: random.Random) -> Optional[List[int]]:
        """Single-point crossover with another firm. Returns child genome or None."""
        point = rng.randint(1, len(self.genome) - 1)
        child_genome = self.genome[:point] + other.genome[point:]
        child_fitness = landscape.evaluate(child_genome)
        # Only produce offspring if fit enough
        if child_fitness >= min(self.fitness, other.fitness):
            return child_genome
        return None


# ---------------------------------------------------------------------------
# Policy Regime
# ---------------------------------------------------------------------------

@dataclass
class PolicyRegime:
    """Defines a policy regime as a set of lever values."""
    name: str
    regulation: float
    tax_rate: float
    innovation_subsidy: float
    competition_limit: float
    safety_net: float

    def entry_barrier(self) -> float:
        """Effective entry cost multiplier from regulation."""
        return 1.0 + self.regulation * 2.0  # regulation 0->1x, 1->3x

    def compliance_cost(self) -> float:
        """Per-tick compliance cost from regulation."""
        return self.regulation * 0.03

    def effective_mutation_rate(self, base_rate: float) -> float:
        """Mutation rate boosted by innovation subsidies."""
        return base_rate * (1.0 + self.innovation_subsidy * 2.0)

    def redistribution_amount(self, total_output: float) -> float:
        """Tax revenue available for redistribution."""
        return total_output * self.tax_rate

    def max_market_share(self) -> float:
        """Maximum allowed market share per firm."""
        return self.competition_limit

    def respawn_probability(self) -> float:
        """Probability of a failed firm re-entering (safety net)."""
        return 0.02 + self.safety_net * 0.08  # 2%-10%


# ---------------------------------------------------------------------------
# Preset Regimes
# ---------------------------------------------------------------------------

REGIMES: Dict[str, PolicyRegime] = {
    "laissez-faire": PolicyRegime(
        name="laissez-faire",
        regulation=0.05,
        tax_rate=0.05,
        innovation_subsidy=0.0,
        competition_limit=1.0,
        safety_net=0.1,
    ),
    "social-democrat": PolicyRegime(
        name="social-democrat",
        regulation=0.4,
        tax_rate=0.45,
        innovation_subsidy=0.3,
        competition_limit=0.25,
        safety_net=0.8,
    ),
    "innovation-state": PolicyRegime(
        name="innovation-state",
        regulation=0.15,
        tax_rate=0.25,
        innovation_subsidy=0.7,
        competition_limit=0.4,
        safety_net=0.5,
    ),
    "protectionist": PolicyRegime(
        name="protectionist",
        regulation=0.8,
        tax_rate=0.35,
        innovation_subsidy=0.05,
        competition_limit=0.5,
        safety_net=0.4,
    ),
    "adaptive": PolicyRegime(
        name="adaptive",
        regulation=0.3,
        tax_rate=0.2,
        innovation_subsidy=0.2,
        competition_limit=0.4,
        safety_net=0.5,
    ),
}


# ---------------------------------------------------------------------------
# Tick Record
# ---------------------------------------------------------------------------

@dataclass
class TickRecord:
    """One tick of simulation data."""
    tick: int
    gdp: float
    innovation_rate: float
    gini: float
    firm_turnover: float       # fraction of firms that entered/exited this tick
    unemployment: float        # fraction of firm slots that are dead
    num_alive: int
    num_firms: int
    mean_fitness: float
    max_fitness: float
    mean_market_share: float
    max_market_share: float
    hhi: float                 # Herfindahl-Hirschman Index
    total_tax_revenue: float
    mean_age: float
    growth_rate: float         # GDP growth vs previous tick


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the public policy simulation."""

    def __init__(self, config: Optional[Config] = None,
                 regime: Optional[PolicyRegime] = None):
        self.config = config or Config()
        c = self.config

        # Set up RNG
        if c.seed is not None:
            random.seed(c.seed)
        self.rng = random.Random(c.seed)

        # Build fitness landscape
        self.landscape = FitnessLandscape(
            c.genome_length, c.landscape_k, c.landscape_ruggedness, self.rng
        )

        # Set policy regime
        if regime:
            self.regime = regime
        else:
            self.regime = PolicyRegime(
                name="custom",
                regulation=c.regulation,
                tax_rate=c.tax_rate,
                innovation_subsidy=c.innovation_subsidy,
                competition_limit=c.competition_limit,
                safety_net=c.safety_net,
            )

        # Create initial firms
        self.firms: List[Firm] = []
        self.next_firm_id = 0
        for _ in range(c.num_firms):
            self._create_firm(initial=True)

        # State
        self.tick = 0
        self.history: List[TickRecord] = []
        self.prev_gdp = 0.0
        self.total_entries = 0
        self.total_exits = 0
        self.cumulative_innovations = 0

        # For adaptive regime
        self._adaptive_history: List[Dict] = []

    def _create_firm(self, initial: bool = False, parent_genome: Optional[List[int]] = None) -> Firm:
        """Create a new firm (either initial or entrant)."""
        c = self.config

        if parent_genome:
            genome = parent_genome.copy()
            # Small mutation on entry
            for i in range(len(genome)):
                if self.rng.random() < 0.1:
                    genome[i] = 1 - genome[i]
        else:
            genome = [self.rng.randint(0, 1) for _ in range(c.genome_length)]

        fitness = self.landscape.evaluate(genome)

        if initial:
            capital = 1.0
        else:
            # Entry cost affected by regulation
            entry_cost = c.base_entry_cost * self.regime.entry_barrier()
            capital = max(0.3, 1.0 - entry_cost)

        firm = Firm(self.next_firm_id, genome, fitness, capital, self.rng)
        self.next_firm_id += 1
        self.firms.append(firm)
        return firm

    def _compute_gini(self, values: List[float]) -> float:
        """Compute Gini coefficient."""
        if not values or len(values) < 2:
            return 0.0
        vals = sorted([max(v, 0.0) for v in values])
        n = len(vals)
        total = sum(vals)
        if total == 0:
            return 0.0
        weighted_sum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(vals))
        return max(0.0, min(1.0, weighted_sum / (n * total)))

    def _compute_hhi(self, shares: List[float]) -> float:
        """Compute Herfindahl-Hirschman Index."""
        return sum(s * s for s in shares) if shares else 0.0

    def _adapt_policy(self):
        """For 'adaptive' regime: adjust policy based on economic indicators."""
        if len(self.history) < 20:
            return

        recent = self.history[-20:]
        avg_growth = sum(r.growth_rate for r in recent) / len(recent)
        avg_gini = sum(r.gini for r in recent) / len(recent)
        avg_unemployment = sum(r.unemployment for r in recent) / len(recent)
        avg_innovation = sum(r.innovation_rate for r in recent) / len(recent)

        # Adjust regulation: reduce if growth is low, increase if inequality is high
        if avg_growth < 0.005:
            self.regime.regulation = max(0.05, self.regime.regulation - 0.02)
        elif avg_gini > 0.5:
            self.regime.regulation = min(0.6, self.regime.regulation + 0.01)

        # Adjust tax rate: increase if inequality is high, decrease if growth is low
        if avg_gini > 0.45:
            self.regime.tax_rate = min(0.5, self.regime.tax_rate + 0.01)
        elif avg_growth < 0.003 and self.regime.tax_rate > 0.1:
            self.regime.tax_rate = max(0.1, self.regime.tax_rate - 0.01)

        # Adjust innovation subsidy: increase if innovation is low
        if avg_innovation < 0.1:
            self.regime.innovation_subsidy = min(0.6, self.regime.innovation_subsidy + 0.02)
        elif avg_innovation > 0.3:
            self.regime.innovation_subsidy = max(0.0, self.regime.innovation_subsidy - 0.01)

        # Adjust safety net: increase if unemployment is high
        if avg_unemployment > 0.2:
            self.regime.safety_net = min(0.9, self.regime.safety_net + 0.02)
        elif avg_unemployment < 0.05:
            self.regime.safety_net = max(0.1, self.regime.safety_net - 0.01)

        # Adjust competition limit: tighten if HHI is high
        avg_hhi = sum(r.hhi for r in recent) / len(recent)
        if avg_hhi > 0.15:
            self.regime.competition_limit = max(0.15, self.regime.competition_limit - 0.02)
        elif avg_hhi < 0.05:
            self.regime.competition_limit = min(1.0, self.regime.competition_limit + 0.01)

    def step(self) -> TickRecord:
        """Execute one tick of the simulation."""
        self.tick += 1
        c = self.config
        regime = self.regime

        # Adaptive policy adjustment
        if regime.name == "adaptive":
            self._adapt_policy()

        alive_firms = [f for f in self.firms if f.alive]
        n_alive = len(alive_firms)

        if n_alive == 0:
            # Even with zero alive, attempt respawns (safety net / new entrants)
            entries_this_tick = 0
            dead_firms = [f for f in self.firms if not f.alive]
            respawn_prob = regime.respawn_probability()
            for firm in dead_firms:
                if self.rng.random() < respawn_prob:
                    new_genome = [self.rng.randint(0, 1) for _ in range(c.genome_length)]
                    firm.genome = new_genome
                    firm.fitness = self.landscape.evaluate(new_genome)
                    entry_cost = c.base_entry_cost * regime.entry_barrier()
                    firm.capital = max(0.3, 1.0 - entry_cost) + regime.safety_net * 0.2
                    firm.alive = True
                    firm.age = 0
                    firm.output = 0.0
                    firm.market_share = 0.0
                    firm.innovations = 0
                    entries_this_tick += 1
                    self.total_entries += 1
            turnover = entries_this_tick / c.num_firms
            return self._record_tick(0, turnover)

        # 1. Innovation: mutation and crossover
        mutation_rate = regime.effective_mutation_rate(c.base_mutation_rate)
        innovations_this_tick = 0

        for firm in alive_firms:
            if firm.mutate(mutation_rate, self.landscape):
                innovations_this_tick += 1
                firm.last_innovation_tick = self.tick

        # Crossover: random pairs
        if len(alive_firms) >= 2 and self.rng.random() < c.crossover_rate:
            parents = self.rng.sample(alive_firms, 2)
            child_genome = parents[0].crossover(parents[1], self.landscape, self.rng)
            if child_genome and len(self.firms) < c.num_firms * 1.5:
                # Only spawn via crossover if there's a dead slot
                dead_firms = [f for f in self.firms if not f.alive]
                if dead_firms:
                    # Reuse slot
                    df = dead_firms[0]
                    df.genome = child_genome
                    df.fitness = self.landscape.evaluate(child_genome)
                    df.capital = max(0.3, 1.0 - c.base_entry_cost * regime.entry_barrier())
                    df.alive = True
                    df.age = 0
                    df.output = 0.0
                    df.market_share = 0.0
                    df.innovations = 0
                    self.total_entries += 1

        self.cumulative_innovations += innovations_this_tick

        # 2. Compute output and market shares
        # Output = fitness * capital * (1 - compliance_cost)
        compliance = regime.compliance_cost()
        for firm in alive_firms:
            raw_output = firm.fitness * firm.capital * (1.0 - compliance)
            firm.output = max(0.0, raw_output)

        total_output = sum(f.output for f in alive_firms if f.alive)

        # Market shares (fitness-proportional)
        alive_firms = [f for f in self.firms if f.alive]  # refresh
        if total_output > 0:
            for firm in alive_firms:
                firm.market_share = firm.output / total_output
        else:
            for firm in alive_firms:
                firm.market_share = 1.0 / max(len(alive_firms), 1)

        # 3. Apply competition policy (cap market share)
        max_share = regime.max_market_share()
        if max_share < 1.0:
            excess_total = 0.0
            capped_firms = []
            uncapped_firms = []
            for firm in alive_firms:
                if firm.market_share > max_share:
                    excess_total += firm.market_share - max_share
                    firm.market_share = max_share
                    capped_firms.append(firm)
                else:
                    uncapped_firms.append(firm)
            # Redistribute excess to uncapped firms proportionally
            if uncapped_firms and excess_total > 0:
                uncapped_total = sum(f.market_share for f in uncapped_firms)
                if uncapped_total > 0:
                    for firm in uncapped_firms:
                        firm.market_share += excess_total * (firm.market_share / uncapped_total)

        # 4. Tax and redistribute
        tax_revenue = regime.redistribution_amount(total_output)
        post_tax_output = total_output - tax_revenue

        # Redistribute: public goods boost (all firms) + safety net (stored)
        public_goods_share = 0.6  # 60% of tax goes to public goods
        safety_net_share = 0.4    # 40% to safety net

        public_goods_boost = (tax_revenue * public_goods_share) / max(len(alive_firms), 1)

        for firm in alive_firms:
            # Post-tax output
            firm_output_after_tax = firm.output * (1.0 - regime.tax_rate)
            # Add public goods benefit
            firm.capital += (firm_output_after_tax + public_goods_boost) * 0.01
            # Operating costs
            firm.capital -= c.base_operating_cost * firm.capital
            # Age
            firm.age += 1

        # 5. Firm failure (low capital or very low fitness)
        exits_this_tick = 0
        for firm in alive_firms:
            if firm.capital < 0.1 or (firm.fitness < 0.15 and firm.age > 10):
                firm.alive = False
                firm.output = 0.0
                firm.market_share = 0.0
                exits_this_tick += 1
                self.total_exits += 1

        # 6. Entry of new firms (respawning dead slots via safety net)
        entries_this_tick = 0
        dead_firms = [f for f in self.firms if not f.alive]
        respawn_prob = regime.respawn_probability()

        for firm in dead_firms:
            if self.rng.random() < respawn_prob:
                # New entrant: random genome, affected by entry barriers
                new_genome = [self.rng.randint(0, 1) for _ in range(c.genome_length)]
                # Sometimes inherit from a successful firm (knowledge spillover)
                top_firms = sorted([f for f in self.firms if f.alive],
                                   key=lambda f: f.fitness, reverse=True)
                if top_firms and self.rng.random() < 0.3:
                    parent = self.rng.choice(top_firms[:max(1, len(top_firms) // 4)])
                    # Partial inheritance with mutation
                    for i in range(c.genome_length):
                        if self.rng.random() < 0.5:
                            new_genome[i] = parent.genome[i]
                        if self.rng.random() < 0.15:
                            new_genome[i] = 1 - new_genome[i]

                firm.genome = new_genome
                firm.fitness = self.landscape.evaluate(new_genome)
                entry_cost = c.base_entry_cost * regime.entry_barrier()
                firm.capital = max(0.3, 1.0 - entry_cost)
                # Safety net: higher safety net gives entrants more capital
                firm.capital += regime.safety_net * 0.2
                firm.alive = True
                firm.age = 0
                firm.output = 0.0
                firm.market_share = 0.0
                firm.innovations = 0
                entries_this_tick += 1
                self.total_entries += 1

        turnover = (entries_this_tick + exits_this_tick) / c.num_firms

        return self._record_tick(innovations_this_tick, turnover)

    def _record_tick(self, innovations: int, turnover: float) -> TickRecord:
        """Record metrics for this tick."""
        alive = [f for f in self.firms if f.alive]
        n_alive = len(alive)
        c = self.config

        gdp = sum(f.output for f in alive) if alive else 0.0
        unemployment = 1.0 - n_alive / c.num_firms

        shares = [f.market_share for f in alive] if alive else []
        outputs = [f.output for f in alive] if alive else []
        fitnesses = [f.fitness for f in alive] if alive else []
        ages = [f.age for f in alive] if alive else []

        gini = self._compute_gini(outputs)
        hhi = self._compute_hhi(shares)

        mean_fitness = sum(fitnesses) / len(fitnesses) if fitnesses else 0.0
        max_fitness = max(fitnesses) if fitnesses else 0.0
        mean_share = sum(shares) / len(shares) if shares else 0.0
        max_share = max(shares) if shares else 0.0
        mean_age = sum(ages) / len(ages) if ages else 0.0

        growth_rate = (gdp - self.prev_gdp) / max(self.prev_gdp, 0.001) if self.prev_gdp > 0 else 0.0
        self.prev_gdp = gdp

        innovation_rate = innovations / max(n_alive, 1)
        tax_rev = self.regime.redistribution_amount(gdp)

        record = TickRecord(
            tick=self.tick,
            gdp=gdp,
            innovation_rate=innovation_rate,
            gini=gini,
            firm_turnover=turnover,
            unemployment=unemployment,
            num_alive=n_alive,
            num_firms=c.num_firms,
            mean_fitness=mean_fitness,
            max_fitness=max_fitness,
            mean_market_share=mean_share,
            max_market_share=max_share,
            hhi=hhi,
            total_tax_revenue=tax_rev,
            mean_age=mean_age,
            growth_rate=growth_rate,
        )
        self.history.append(record)
        return record

    def run(self, progress_callback=None) -> List[TickRecord]:
        """Run the full simulation."""
        for t in range(self.config.num_ticks):
            record = self.step()
            if progress_callback:
                progress_callback(t, self.config.num_ticks, record)
        return self.history

    def get_statistics(self) -> dict:
        """Compute summary statistics."""
        if not self.history:
            return {}

        gdps = [r.gdp for r in self.history]
        innovations = [r.innovation_rate for r in self.history]
        ginis = [r.gini for r in self.history]
        turnovers = [r.firm_turnover for r in self.history]
        unemployments = [r.unemployment for r in self.history]
        fitnesses = [r.mean_fitness for r in self.history]
        hhis = [r.hhi for r in self.history]
        growth_rates = [r.growth_rate for r in self.history[10:]]  # skip initial

        # Long-run growth: GDP in last 100 ticks vs first 100 ticks
        if len(gdps) > 200:
            early_gdp = sum(gdps[:100]) / 100
            late_gdp = sum(gdps[-100:]) / 100
            long_run_growth = (late_gdp - early_gdp) / max(early_gdp, 0.001)
        else:
            long_run_growth = 0.0

        stats = {
            "regime": self.regime.name,
            "num_ticks": len(self.history),
            "num_firms": self.config.num_firms,
            "mean_gdp": sum(gdps) / len(gdps),
            "final_gdp": gdps[-1],
            "peak_gdp": max(gdps),
            "long_run_growth": long_run_growth,
            "mean_innovation_rate": sum(innovations) / len(innovations),
            "total_innovations": self.cumulative_innovations,
            "mean_gini": sum(ginis) / len(ginis),
            "final_gini": ginis[-1],
            "mean_turnover": sum(turnovers) / len(turnovers),
            "mean_unemployment": sum(unemployments) / len(unemployments),
            "max_unemployment": max(unemployments),
            "mean_fitness": sum(fitnesses) / len(fitnesses),
            "final_fitness": fitnesses[-1],
            "mean_hhi": sum(hhis) / len(hhis),
            "mean_growth_rate": sum(growth_rates) / len(growth_rates) if growth_rates else 0.0,
            "total_entries": self.total_entries,
            "total_exits": self.total_exits,
            "firms_alive_at_end": self.history[-1].num_alive,
        }

        # Final adaptive policy state
        if self.regime.name == "adaptive":
            stats["final_regulation"] = round(self.regime.regulation, 3)
            stats["final_tax_rate"] = round(self.regime.tax_rate, 3)
            stats["final_innovation_subsidy"] = round(self.regime.innovation_subsidy, 3)
            stats["final_competition_limit"] = round(self.regime.competition_limit, 3)
            stats["final_safety_net"] = round(self.regime.safety_net, 3)

        return stats

    def to_json(self) -> dict:
        """Export full simulation as JSON-serializable dict."""
        return {
            "config": {
                "num_firms": self.config.num_firms,
                "num_ticks": self.config.num_ticks,
                "genome_length": self.config.genome_length,
                "landscape_k": self.config.landscape_k,
                "seed": self.config.seed,
            },
            "regime": {
                "name": self.regime.name,
                "regulation": self.regime.regulation,
                "tax_rate": self.regime.tax_rate,
                "innovation_subsidy": self.regime.innovation_subsidy,
                "competition_limit": self.regime.competition_limit,
                "safety_net": self.regime.safety_net,
            },
            "history": [
                {
                    "tick": r.tick,
                    "gdp": round(r.gdp, 4),
                    "innovation_rate": round(r.innovation_rate, 4),
                    "gini": round(r.gini, 4),
                    "firm_turnover": round(r.firm_turnover, 4),
                    "unemployment": round(r.unemployment, 4),
                    "num_alive": r.num_alive,
                    "mean_fitness": round(r.mean_fitness, 4),
                    "max_fitness": round(r.max_fitness, 4),
                    "hhi": round(r.hhi, 4),
                    "growth_rate": round(r.growth_rate, 6),
                    "mean_age": round(r.mean_age, 1),
                }
                for r in self.history
            ],
            "statistics": self.get_statistics(),
        }

    def save_json(self, filepath: str):
        """Save simulation results to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_json(), f, indent=2)

    def save_csv(self, filepath: str):
        """Save simulation history to CSV file."""
        if not self.history:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "gdp", "innovation_rate", "gini", "firm_turnover",
                "unemployment", "num_alive", "mean_fitness", "max_fitness",
                "mean_market_share", "max_market_share", "hhi",
                "total_tax_revenue", "mean_age", "growth_rate",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, f"{r.gdp:.4f}", f"{r.innovation_rate:.4f}",
                    f"{r.gini:.4f}", f"{r.firm_turnover:.4f}",
                    f"{r.unemployment:.4f}", r.num_alive,
                    f"{r.mean_fitness:.4f}", f"{r.max_fitness:.4f}",
                    f"{r.mean_market_share:.4f}", f"{r.max_market_share:.4f}",
                    f"{r.hhi:.4f}", f"{r.total_tax_revenue:.4f}",
                    f"{r.mean_age:.1f}", f"{r.growth_rate:.6f}",
                ])
