"""
Integrated Economy Simulation
==============================
A cross-model simulation linking supply chains (Beer Game), stock markets
(SFI model), ecosystem dynamics (Punctuated Equilibrium), and organizational
adaptation (Rigids vs Flexibles) into a single coherent economy.

Core idea: An economy of N firms, each with a stock price, supply chain
position, internal organization (rigid/flexible leadership), and technology
fitness. Shocks propagate through multiple channels simultaneously:
  - Supply chain disruptions amplify via the bullwhip effect
  - Stock prices react to firm fundamentals and contagion
  - Firm failures cascade through a dependency network
  - Organizational rigidity determines recovery speed
  - Technology disruptions periodically reshape the landscape

References:
  - Arthur et al. (1997), SFI Artificial Stock Market
  - Sterman (1989), Beer Distribution Game
  - Jain & Krishna (2002), Punctuated Equilibrium
  - Harrington (1999), Rigidity of Social Systems
  - Beinhocker (2006), The Origin of Wealth
"""

from __future__ import annotations

import random
import math
import csv
import json
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Configuration for the integrated economy simulation."""
    # Economy size
    num_firms: int = 40
    num_ticks: int = 500

    # Supply chain
    supply_chain_length: int = 4      # echelons in the chain
    base_demand: float = 10.0
    bullwhip_alpha: float = 0.4       # inventory adjustment strength
    bullwhip_beta: float = 0.2        # supply line adjustment strength
    demand_smoothing: float = 0.3     # exponential smoothing theta

    # Stock market
    initial_stock_price: float = 100.0
    price_noise_std: float = 0.02     # daily noise in returns
    mean_reversion_speed: float = 0.05
    sentiment_momentum: float = 0.7   # how much past sentiment carries

    # Ecosystem / dependency network
    dependency_prob: float = 0.08     # probability of dependency edge
    cascade_threshold: float = 0.4    # health below which firm may fail
    failure_contagion: float = 0.2    # health loss per failed dependency

    # Organization
    initial_flexible_fraction: float = 0.4
    rigid_efficiency_bonus: float = 0.15   # rigids are more efficient in steady state
    flexible_adaptation_speed: float = 0.3  # how fast flexibles adapt
    rigid_adaptation_speed: float = 0.05    # how slow rigids adapt

    # Technology disruption
    tech_disruption_prob: float = 0.005     # per-tick probability of disruption
    tech_disruption_severity: float = 0.6   # how much old tech fitness drops
    tech_adoption_speed_flexible: float = 0.15
    tech_adoption_speed_rigid: float = 0.03

    # Random seed
    seed: Optional[int] = None


class EconomyPhase(Enum):
    NORMAL = "normal"
    SUPPLY_SHOCK = "supply_shock"
    TECH_DISRUPTION = "tech_disruption"
    MARKET_CRASH = "market_crash"
    RECOVERY = "recovery"


# ---------------------------------------------------------------------------
# Firm
# ---------------------------------------------------------------------------

class Firm:
    """A firm in the integrated economy.

    Each firm has:
    - A supply chain position (0=downstream/retail, 3=upstream/production)
    - A stock price driven by fundamentals and sentiment
    - Internal organization (mix of rigid/flexible leadership)
    - Technology fitness that determines productive capacity
    - Health: composite measure of viability
    """

    def __init__(self, firm_id: int, config: Config, rng: random.Random):
        self.id = firm_id
        self.config = config
        self.rng = rng

        # Supply chain position (cyclically assigned across echelons)
        self.supply_chain_pos = firm_id % config.supply_chain_length
        # Per-firm demand share: total demand split among firms in each echelon
        firms_per_echelon = max(config.num_firms / config.supply_chain_length, 1)
        self._per_firm_demand = config.base_demand / firms_per_echelon
        self.inventory = self._per_firm_demand * 3.0
        self.backlog = 0.0
        self.expected_demand = self._per_firm_demand
        self.last_order = self._per_firm_demand
        self.supply_line = self._per_firm_demand * 2.0

        # Stock market
        self.stock_price = config.initial_stock_price * (0.8 + rng.random() * 0.4)
        self.fundamental_value = self.stock_price
        self.sentiment = 0.0  # [-1, 1]

        # Organization
        self.flexible_fraction = config.initial_flexible_fraction
        self.organizational_fitness = 0.5 + rng.random() * 0.3

        # Technology
        self.tech_fitness = 0.5 + rng.random() * 0.4
        self.tech_generation = 0  # which tech generation the firm is on

        # Health (composite)
        self.health = self._compute_health()
        self.alive = True
        self.age = 0
        self.output = self._per_firm_demand  # production/throughput

        # Dependencies (set externally)
        self.suppliers: List[int] = []
        self.customers: List[int] = []

        # History
        self.price_history: List[float] = [self.stock_price]
        self.health_history: List[float] = [self.health]
        self.output_history: List[float] = [self.output]

    def _compute_health(self) -> float:
        """Composite health: weighted average of supply chain, org, and tech."""
        # Effective inventory ratio (1.0 = ideal)
        ideal_inv = self._per_firm_demand * 3.0
        inv_ratio = min(self.inventory / max(ideal_inv, 0.1), 2.0) / 2.0
        backlog_penalty = min(self.backlog / max(self._per_firm_demand, 0.1), 1.0)
        supply_health = max(0.0, inv_ratio - 0.3 * backlog_penalty)

        health = (
            0.25 * supply_health +
            0.25 * self.organizational_fitness +
            0.30 * self.tech_fitness +
            0.20 * min(self.stock_price / max(self.config.initial_stock_price, 1.0), 1.5) / 1.5
        )
        return max(0.0, min(1.0, health))

    def update_health(self):
        self.health = self._compute_health()
        self.health_history.append(self.health)


# ---------------------------------------------------------------------------
# Dependency Network
# ---------------------------------------------------------------------------

class DependencyNetwork:
    """Directed graph of firm dependencies.

    An edge from firm A to firm B means B depends on A (A supplies to B).
    When A fails, B suffers contagion damage.
    """

    def __init__(self, num_firms: int, dependency_prob: float, rng: random.Random):
        self.num_firms = num_firms
        self.adjacency: Dict[int, List[int]] = {i: [] for i in range(num_firms)}
        self.reverse: Dict[int, List[int]] = {i: [] for i in range(num_firms)}

        for i in range(num_firms):
            for j in range(num_firms):
                if i != j and rng.random() < dependency_prob:
                    self.adjacency[i].append(j)  # i supplies to j
                    self.reverse[j].append(i)     # j depends on i

    def get_dependents(self, firm_id: int) -> List[int]:
        """Firms that depend on firm_id."""
        return self.adjacency.get(firm_id, [])

    def get_suppliers(self, firm_id: int) -> List[int]:
        """Firms that firm_id depends on."""
        return self.reverse.get(firm_id, [])

    def get_edges(self) -> List[Tuple[int, int]]:
        """Return all edges as (supplier, dependent) pairs."""
        edges = []
        for supplier, dependents in self.adjacency.items():
            for dependent in dependents:
                edges.append((supplier, dependent))
        return edges


# ---------------------------------------------------------------------------
# Market (simplified stock market)
# ---------------------------------------------------------------------------

class Market:
    """Simplified stock market that prices firms based on fundamentals + sentiment."""

    def __init__(self, config: Config, rng: random.Random):
        self.config = config
        self.rng = rng
        self.market_index_history: List[float] = []
        self.volume_history: List[float] = []
        self.market_sentiment = 0.0

    def update_prices(self, firms: List[Firm], cascade_stress: float = 0.0):
        """Update all firm stock prices based on fundamentals and sentiment.

        cascade_stress: [0, 1] measure of current ecosystem stress
        """
        # Market-wide sentiment: momentum + mean reversion + cascade fear
        sentiment_innovation = self.rng.gauss(0, 0.1)
        fear_factor = -cascade_stress * 0.5
        self.market_sentiment = (
            self.config.sentiment_momentum * self.market_sentiment +
            (1 - self.config.sentiment_momentum) * (sentiment_innovation + fear_factor)
        )
        self.market_sentiment = max(-1.0, min(1.0, self.market_sentiment))

        total_volume = 0.0
        for firm in firms:
            if not firm.alive:
                firm.stock_price = 0.0
                firm.price_history.append(0.0)
                continue

            # Fundamental value: based on output relative to expected per-firm share
            # Normalized so that initial conditions yield ~initial_stock_price
            output_ratio = min(firm.output / max(firm._per_firm_demand, 0.01), 2.0)
            # Use sqrt to compress the quality multiplier range:
            # at initial conditions (tech~0.7, org~0.65), quality ~ 0.87 -> price stays close
            quality = math.sqrt(firm.tech_fitness * (0.5 + 0.5 * firm.organizational_fitness))
            firm.fundamental_value = (
                self.config.initial_stock_price * output_ratio * quality
            )

            # Price adjustment: mean reversion to fundamental + noise + sentiment
            price_return = (
                self.config.mean_reversion_speed * (firm.fundamental_value - firm.stock_price) / max(firm.stock_price, 1.0) +
                self.rng.gauss(0, self.config.price_noise_std) +
                0.03 * self.market_sentiment +
                0.02 * firm.sentiment
            )

            firm.stock_price *= (1.0 + price_return)
            firm.stock_price = max(firm.stock_price, 0.01)
            firm.price_history.append(firm.stock_price)

            # Volume proxy: absolute price change
            total_volume += abs(price_return) * firm.stock_price

        # Market index: average stock price
        alive_firms = [f for f in firms if f.alive]
        if alive_firms:
            index = sum(f.stock_price for f in alive_firms) / len(alive_firms)
        else:
            index = 0.0
        self.market_index_history.append(index)
        self.volume_history.append(total_volume)


# ---------------------------------------------------------------------------
# Supply Chain Engine
# ---------------------------------------------------------------------------

class SupplyChainEngine:
    """Manages supply chain dynamics across all firms using Beer Game mechanics."""

    def __init__(self, config: Config, rng: random.Random):
        self.config = config
        self.rng = rng
        self.demand_history: List[float] = []
        self.current_demand = config.base_demand
        self.stress_history: List[float] = []

    def apply_demand_shock(self, multiplier: float):
        """Apply a demand shock (multiplier > 1 = demand spike)."""
        self.current_demand = self.config.base_demand * multiplier

    def step(self, firms: List[Firm]):
        """Process one tick of supply chain dynamics.

        Implements a simplified Beer Game bullwhip mechanism:
        - Downstream firms face consumer demand
        - Orders propagate upstream with amplification
        - Inventory and backlog track fill rates
        """
        self.demand_history.append(self.current_demand)

        # Group firms by supply chain position
        by_position: Dict[int, List[Firm]] = {}
        for firm in firms:
            if not firm.alive:
                continue
            pos = firm.supply_chain_pos
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(firm)

        # Process from downstream (0) to upstream (supply_chain_length - 1)
        incoming_demand = self.current_demand
        total_stress = 0.0
        n_alive = sum(1 for f in firms if f.alive)

        for pos in range(self.config.supply_chain_length):
            if pos not in by_position:
                continue
            for firm in by_position[pos]:
                # Receive "shipment" (production from upstream)
                received = min(firm.supply_line * 0.5, firm.last_order)
                firm.inventory += received
                firm.supply_line = max(0.0, firm.supply_line - received)

                # Face demand (from downstream or consumer)
                demand = incoming_demand / max(len(by_position[pos]), 1)
                firm.expected_demand += self.config.demand_smoothing * (demand - firm.expected_demand)

                # Fill orders
                total_demand = firm.backlog + demand
                shipped = min(firm.inventory, total_demand)
                firm.inventory -= shipped
                firm.backlog = total_demand - shipped
                firm.output = shipped

                # Sterman's anchor-and-adjust ordering
                desired_inventory = firm.expected_demand * 3.0
                desired_supply_line = firm.expected_demand * 2.0
                inv_adj = self.config.bullwhip_alpha * (desired_inventory - (firm.inventory - firm.backlog))
                sl_adj = self.config.bullwhip_beta * (desired_supply_line - firm.supply_line)
                order = max(0.0, firm.expected_demand + inv_adj + sl_adj)

                # Organizational effect: flexible firms smooth orders more
                if firm.flexible_fraction > 0.5:
                    smoothing = 0.3 * firm.flexible_fraction
                    order = (1 - smoothing) * order + smoothing * firm.expected_demand
                firm.last_order = order
                firm.supply_line += order

                # Track stress
                if firm.backlog > firm.expected_demand * 0.5:
                    total_stress += 1.0

                firm.output_history.append(firm.output)

            # Amplified demand propagates upstream (bullwhip)
            avg_order = np.mean([f.last_order for f in by_position[pos]]) if by_position[pos] else incoming_demand
            incoming_demand = avg_order * 1.1  # slight amplification

        stress_ratio = total_stress / max(n_alive, 1)
        self.stress_history.append(stress_ratio)


# ---------------------------------------------------------------------------
# Technology Engine
# ---------------------------------------------------------------------------

class TechnologyEngine:
    """Manages technology generations and disruption events."""

    def __init__(self, config: Config, rng: random.Random):
        self.config = config
        self.rng = rng
        self.current_generation = 0
        self.disruption_history: List[int] = []

    def step(self, firms: List[Firm], tick: int, force_disruption: bool = False) -> bool:
        """Process one tick of technology dynamics. Returns True if disruption occurred."""
        disrupted = False

        # Check for new technology disruption
        if force_disruption or self.rng.random() < self.config.tech_disruption_prob:
            self.current_generation += 1
            self.disruption_history.append(tick)
            disrupted = True

            # Existing firms' tech fitness drops (old tech becomes less valuable)
            for firm in firms:
                if not firm.alive:
                    continue
                gen_gap = self.current_generation - firm.tech_generation
                if gen_gap > 0:
                    penalty = self.config.tech_disruption_severity * (1 - 0.5 ** gen_gap)
                    firm.tech_fitness *= (1.0 - penalty)
                    firm.tech_fitness = max(0.05, firm.tech_fitness)
                    # Sentiment drops on disruption
                    firm.sentiment -= 0.3

        # All firms gradually adapt to current technology
        for firm in firms:
            if not firm.alive:
                continue
            gen_gap = self.current_generation - firm.tech_generation
            if gen_gap > 0:
                # Adaptation speed depends on organizational flexibility
                speed = (
                    firm.flexible_fraction * self.config.tech_adoption_speed_flexible +
                    (1 - firm.flexible_fraction) * self.config.tech_adoption_speed_rigid
                )
                firm.tech_fitness += speed * (1.0 - firm.tech_fitness)
                firm.tech_fitness = min(1.0, firm.tech_fitness)

                # If tech fitness has recovered, update generation
                if firm.tech_fitness > 0.8:
                    firm.tech_generation = self.current_generation

        return disrupted


# ---------------------------------------------------------------------------
# Organization Engine
# ---------------------------------------------------------------------------

class OrganizationEngine:
    """Manages organizational dynamics (Rigids vs Flexibles)."""

    def __init__(self, config: Config, rng: random.Random):
        self.config = config
        self.rng = rng

    def step(self, firms: List[Firm], is_crisis: bool):
        """Update organizational dynamics.

        During stability: rigid leadership gradually increases (more efficient).
        During crisis: flexible firms adapt faster, rigid firms suffer.
        """
        for firm in firms:
            if not firm.alive:
                continue

            if is_crisis:
                # Crisis: flexible fraction increases as rigid leaders fail
                if firm.flexible_fraction < 0.8:
                    firm.flexible_fraction += 0.02 * (1.0 - firm.health)
                # Organizational fitness based on adaptability
                firm.organizational_fitness += (
                    self.config.flexible_adaptation_speed * firm.flexible_fraction *
                    (1.0 - firm.organizational_fitness)
                )
                # Rigid component drags down during crisis
                firm.organizational_fitness -= (
                    0.1 * (1.0 - firm.flexible_fraction) * (1.0 - firm.health)
                )
            else:
                # Stability: rigid leadership creeps up (efficiency advantage)
                if firm.flexible_fraction > 0.2:
                    firm.flexible_fraction -= 0.005
                # Organizational fitness improves slowly
                firm.organizational_fitness += (
                    0.02 * (1.0 - firm.organizational_fitness) +
                    self.config.rigid_efficiency_bonus * (1.0 - firm.flexible_fraction) * 0.01
                )

            firm.organizational_fitness = max(0.0, min(1.0, firm.organizational_fitness))
            firm.flexible_fraction = max(0.0, min(1.0, firm.flexible_fraction))


# ---------------------------------------------------------------------------
# Cascade Engine
# ---------------------------------------------------------------------------

class CascadeEngine:
    """Manages firm failures and cascade propagation through the dependency network."""

    def __init__(self, config: Config, network: DependencyNetwork):
        self.config = config
        self.network = network
        self.cascade_sizes: List[int] = []
        self.failures_per_tick: List[int] = []

    def step(self, firms: List[Firm]) -> int:
        """Check for firm failures and propagate cascades. Returns cascade size."""
        failed_this_tick: List[int] = []

        # Phase 1: identify firms below failure threshold
        for firm in firms:
            if not firm.alive:
                continue
            if firm.health < self.config.cascade_threshold:
                # Probability of failure increases as health drops
                fail_prob = (self.config.cascade_threshold - firm.health) / self.config.cascade_threshold
                if random.random() < fail_prob:
                    failed_this_tick.append(firm.id)

        # Phase 2: propagate cascade
        all_failed = set(failed_this_tick)
        frontier = list(failed_this_tick)
        max_rounds = 10

        for _ in range(max_rounds):
            if not frontier:
                break
            next_frontier = []
            for fid in frontier:
                # Damage dependents
                for dep_id in self.network.get_dependents(fid):
                    dep_firm = firms[dep_id]
                    if not dep_firm.alive or dep_id in all_failed:
                        continue
                    dep_firm.health -= self.config.failure_contagion
                    dep_firm.sentiment -= 0.2
                    dep_firm.stock_price *= 0.95  # price shock
                    if dep_firm.health < self.config.cascade_threshold * 0.8:
                        next_frontier.append(dep_id)
                        all_failed.add(dep_id)
            frontier = next_frontier

        # Kill failed firms
        for fid in all_failed:
            firms[fid].alive = False
            firms[fid].stock_price = 0.0
            firms[fid].output = 0.0

        cascade_size = len(all_failed)
        self.cascade_sizes.append(cascade_size)
        self.failures_per_tick.append(cascade_size)

        return cascade_size


# ---------------------------------------------------------------------------
# Tick Record
# ---------------------------------------------------------------------------

@dataclass
class TickRecord:
    """One tick of simulation data."""
    tick: int
    phase: str
    gdp: float
    market_index: float
    gini: float
    unemployment: float  # fraction of failed firms
    supply_chain_stress: float
    mean_health: float
    mean_tech_fitness: float
    mean_flex_fraction: float
    cascade_size: int
    num_alive: int
    num_firms: int
    consumer_demand: float
    market_sentiment: float
    tech_generation: int


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the integrated economy simulation."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        c = self.config

        if c.seed is not None:
            random.seed(c.seed)
            np.random.seed(c.seed)
        self.rng = random.Random(c.seed)

        # Create firms
        self.firms = [Firm(i, c, self.rng) for i in range(c.num_firms)]

        # Build dependency network
        self.network = DependencyNetwork(c.num_firms, c.dependency_prob, self.rng)
        for i, firm in enumerate(self.firms):
            firm.suppliers = self.network.get_suppliers(i)
            firm.customers = self.network.get_dependents(i)

        # Engines
        self.market = Market(c, self.rng)
        self.supply_chain = SupplyChainEngine(c, self.rng)
        self.tech_engine = TechnologyEngine(c, self.rng)
        self.org_engine = OrganizationEngine(c, self.rng)
        self.cascade_engine = CascadeEngine(c, self.network)

        # State
        self.tick = 0
        self.phase = EconomyPhase.NORMAL
        self.history: List[TickRecord] = []
        self.phase_history: List[Tuple[int, str]] = []
        self.events: List[Dict] = []

        # Scenario queue: list of (tick, event_type, params)
        self.scheduled_events: List[Tuple[int, str, dict]] = []

    def schedule_event(self, tick: int, event_type: str, params: Optional[dict] = None):
        """Schedule a scenario event at a specific tick."""
        self.scheduled_events.append((tick, event_type, params or {}))
        self.scheduled_events.sort(key=lambda x: x[0])

    def _process_scheduled_events(self):
        """Process any events scheduled for the current tick."""
        while self.scheduled_events and self.scheduled_events[0][0] <= self.tick:
            _, event_type, params = self.scheduled_events.pop(0)
            self._trigger_event(event_type, params)

    def _trigger_event(self, event_type: str, params: dict):
        """Trigger a scenario event."""
        if event_type == "supply_shock":
            multiplier = params.get("multiplier", 2.5)
            self.supply_chain.apply_demand_shock(multiplier)
            self.phase = EconomyPhase.SUPPLY_SHOCK
            self.events.append({"tick": self.tick, "type": "supply_shock", "multiplier": multiplier})

        elif event_type == "demand_normalize":
            self.supply_chain.current_demand = self.config.base_demand
            if self.phase == EconomyPhase.SUPPLY_SHOCK:
                self.phase = EconomyPhase.RECOVERY

        elif event_type == "tech_disruption":
            self.tech_engine.step(self.firms, self.tick, force_disruption=True)
            self.phase = EconomyPhase.TECH_DISRUPTION
            self.events.append({"tick": self.tick, "type": "tech_disruption",
                                "generation": self.tech_engine.current_generation})

        elif event_type == "market_panic":
            # Sudden sentiment crash: severe price drops + health damage
            self.market.market_sentiment = -0.95
            for firm in self.firms:
                if firm.alive:
                    firm.sentiment = -0.6 - self.rng.random() * 0.4
                    firm.stock_price *= 0.4 + self.rng.random() * 0.3
                    firm.organizational_fitness *= 0.7  # org disruption from panic
                    firm.health *= 0.8  # direct health impact
            self.phase = EconomyPhase.MARKET_CRASH
            self.events.append({"tick": self.tick, "type": "market_panic"})

    def step(self) -> TickRecord:
        """Execute one tick of the integrated simulation."""
        self.tick += 1

        # Process scheduled events
        self._process_scheduled_events()

        # Detect crisis state
        alive_firms = [f for f in self.firms if f.alive]
        n_alive = len(alive_firms)
        if n_alive == 0:
            return self._record_tick(0)

        avg_health = np.mean([f.health for f in alive_firms])
        is_crisis = avg_health < 0.45 or self.phase in (
            EconomyPhase.MARKET_CRASH, EconomyPhase.TECH_DISRUPTION, EconomyPhase.SUPPLY_SHOCK
        )

        # 1. Supply chain dynamics
        self.supply_chain.step(self.firms)

        # 2. Technology evolution
        self.tech_engine.step(self.firms, self.tick)

        # 3. Organizational dynamics
        self.org_engine.step(self.firms, is_crisis)

        # 4. Update health
        for firm in self.firms:
            if firm.alive:
                firm.update_health()
                firm.age += 1

        # 5. Cascade check
        cascade_size = self.cascade_engine.step(self.firms)

        # 6. Market pricing (after cascades, so failures are reflected)
        cascade_stress = cascade_size / max(n_alive, 1)
        supply_stress = self.supply_chain.stress_history[-1] if self.supply_chain.stress_history else 0
        total_stress = min(1.0, cascade_stress + supply_stress * 0.5)
        self.market.update_prices(self.firms, total_stress)

        # 7. Respawn failed firms (new entrants) - with low probability
        for firm in self.firms:
            if not firm.alive and self.rng.random() < 0.02:
                self._respawn_firm(firm)

        # 8. Phase detection
        self._detect_phase()

        # 9. Record
        return self._record_tick(cascade_size)

    def _respawn_firm(self, firm: Firm):
        """Respawn a failed firm as a new entrant."""
        firm.alive = True
        firm.stock_price = self.config.initial_stock_price * 0.5
        firm.health = 0.4
        firm.inventory = firm._per_firm_demand * 2.0
        firm.backlog = 0.0
        firm.expected_demand = firm._per_firm_demand
        firm.supply_line = firm._per_firm_demand
        firm.last_order = firm._per_firm_demand
        firm.tech_fitness = 0.6
        firm.tech_generation = self.tech_engine.current_generation
        firm.organizational_fitness = 0.5
        firm.flexible_fraction = 0.5 + self.rng.random() * 0.3  # new entrants are flexible
        firm.sentiment = 0.0
        firm.age = 0
        firm.output = firm._per_firm_demand * 0.5

    def _detect_phase(self):
        """Detect the current economy phase.

        Uses a cooldown to prevent immediate recovery after event triggers.
        """
        alive = [f for f in self.firms if f.alive]
        if not alive:
            self.phase = EconomyPhase.MARKET_CRASH
            return

        avg_health = np.mean([f.health for f in alive])
        unemployment = 1.0 - len(alive) / self.config.num_firms
        stress = self.supply_chain.stress_history[-1] if self.supply_chain.stress_history else 0

        old_phase = self.phase

        # Don't override phase within 20 ticks of a triggered event
        if self.events:
            last_event_tick = max(e["tick"] for e in self.events)
            if self.tick - last_event_tick < 20:
                # Still allow escalation to worse phases
                if unemployment > 0.3:
                    self.phase = EconomyPhase.MARKET_CRASH
                if self.phase != old_phase:
                    self.phase_history.append((self.tick, self.phase.value))
                return

        # Check for recovery
        if self.phase in (EconomyPhase.MARKET_CRASH, EconomyPhase.TECH_DISRUPTION, EconomyPhase.SUPPLY_SHOCK):
            if avg_health > 0.55 and unemployment < 0.15 and stress < 0.2:
                self.phase = EconomyPhase.RECOVERY
        elif self.phase == EconomyPhase.RECOVERY:
            if avg_health > 0.65 and unemployment < 0.08:
                self.phase = EconomyPhase.NORMAL

        # Detect new crises
        if unemployment > 0.3:
            self.phase = EconomyPhase.MARKET_CRASH
        elif stress > 0.5 and self.phase == EconomyPhase.NORMAL:
            self.phase = EconomyPhase.SUPPLY_SHOCK

        if self.phase != old_phase:
            self.phase_history.append((self.tick, self.phase.value))

    def _record_tick(self, cascade_size: int) -> TickRecord:
        """Record metrics for this tick."""
        alive = [f for f in self.firms if f.alive]
        n_alive = len(alive)

        gdp = sum(f.output for f in alive) if alive else 0.0
        unemployment = 1.0 - n_alive / self.config.num_firms
        gini = self._compute_gini([f.stock_price for f in alive]) if alive else 0.0
        mean_health = float(np.mean([f.health for f in alive])) if alive else 0.0
        mean_tech = float(np.mean([f.tech_fitness for f in alive])) if alive else 0.0
        mean_flex = float(np.mean([f.flexible_fraction for f in alive])) if alive else 0.0
        stress = self.supply_chain.stress_history[-1] if self.supply_chain.stress_history else 0.0
        market_index = self.market.market_index_history[-1] if self.market.market_index_history else 0.0

        record = TickRecord(
            tick=self.tick,
            phase=self.phase.value,
            gdp=gdp,
            market_index=market_index,
            gini=gini,
            unemployment=unemployment,
            supply_chain_stress=stress,
            mean_health=mean_health,
            mean_tech_fitness=mean_tech,
            mean_flex_fraction=mean_flex,
            cascade_size=cascade_size,
            num_alive=n_alive,
            num_firms=self.config.num_firms,
            consumer_demand=self.supply_chain.current_demand,
            market_sentiment=self.market.market_sentiment,
            tech_generation=self.tech_engine.current_generation,
        )
        self.history.append(record)
        return record

    @staticmethod
    def _compute_gini(values: List[float]) -> float:
        """Compute Gini coefficient of a list of non-negative values."""
        if not values or len(values) < 2:
            return 0.0
        vals = sorted([max(v, 0.0) for v in values])
        n = len(vals)
        total = sum(vals)
        if total == 0:
            return 0.0
        weighted_sum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(vals))
        return max(0.0, min(1.0, weighted_sum / (n * total)))

    def run(self, progress_callback=None) -> List[TickRecord]:
        """Run the full simulation."""
        for t in range(self.config.num_ticks):
            record = self.step()
            if progress_callback and t % 50 == 0:
                progress_callback(t, self.config.num_ticks, record)
        return self.history

    def get_statistics(self) -> dict:
        """Compute summary statistics."""
        if not self.history:
            return {}

        gdps = [r.gdp for r in self.history]
        indices = [r.market_index for r in self.history]
        ginis = [r.gini for r in self.history]
        cascades = [r.cascade_size for r in self.history if r.cascade_size > 0]
        unemployment = [r.unemployment for r in self.history]

        stats = {
            "num_ticks": len(self.history),
            "num_firms": self.config.num_firms,
            "mean_gdp": float(np.mean(gdps)),
            "std_gdp": float(np.std(gdps)),
            "final_gdp": gdps[-1],
            "peak_gdp": max(gdps),
            "trough_gdp": min(gdps),
            "mean_market_index": float(np.mean(indices)),
            "final_market_index": indices[-1],
            "mean_gini": float(np.mean(ginis)),
            "final_gini": ginis[-1],
            "mean_unemployment": float(np.mean(unemployment)),
            "max_unemployment": max(unemployment),
            "total_cascades": len(cascades),
            "mean_cascade_size": float(np.mean(cascades)) if cascades else 0.0,
            "max_cascade_size": max(cascades) if cascades else 0,
            "tech_disruptions": len(self.tech_engine.disruption_history),
            "phase_transitions": len(self.phase_history),
            "final_phase": self.history[-1].phase,
            "firms_alive_at_end": self.history[-1].num_alive,
        }
        return stats

    def get_network_state(self) -> dict:
        """Get current network state for visualization."""
        nodes = []
        for firm in self.firms:
            nodes.append({
                "id": firm.id,
                "alive": firm.alive,
                "health": round(firm.health, 3),
                "stock_price": round(firm.stock_price, 2),
                "tech_fitness": round(firm.tech_fitness, 3),
                "flex_fraction": round(firm.flexible_fraction, 3),
                "supply_chain_pos": firm.supply_chain_pos,
                "output": round(firm.output, 2),
                "age": firm.age,
            })

        edges = []
        for supplier, dependent in self.network.get_edges():
            edges.append({
                "source": supplier,
                "target": dependent,
                "active": self.firms[supplier].alive and self.firms[dependent].alive,
            })

        return {"nodes": nodes, "edges": edges}

    def to_json(self) -> dict:
        """Export full simulation as JSON-serializable dict."""
        return {
            "config": {
                "num_firms": self.config.num_firms,
                "num_ticks": self.config.num_ticks,
                "supply_chain_length": self.config.supply_chain_length,
                "base_demand": self.config.base_demand,
                "dependency_prob": self.config.dependency_prob,
                "seed": self.config.seed,
            },
            "history": [
                {
                    "tick": r.tick,
                    "phase": r.phase,
                    "gdp": round(r.gdp, 2),
                    "market_index": round(r.market_index, 2),
                    "gini": round(r.gini, 4),
                    "unemployment": round(r.unemployment, 4),
                    "supply_chain_stress": round(r.supply_chain_stress, 4),
                    "mean_health": round(r.mean_health, 4),
                    "mean_tech_fitness": round(r.mean_tech_fitness, 4),
                    "mean_flex_fraction": round(r.mean_flex_fraction, 4),
                    "cascade_size": r.cascade_size,
                    "num_alive": r.num_alive,
                    "consumer_demand": round(r.consumer_demand, 2),
                    "market_sentiment": round(r.market_sentiment, 4),
                    "tech_generation": r.tech_generation,
                }
                for r in self.history
            ],
            "events": self.events,
            "phase_transitions": self.phase_history,
            "network": self.get_network_state(),
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
                "tick", "phase", "gdp", "market_index", "gini", "unemployment",
                "supply_chain_stress", "mean_health", "mean_tech_fitness",
                "mean_flex_fraction", "cascade_size", "num_alive", "consumer_demand",
                "market_sentiment", "tech_generation",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, r.phase, f"{r.gdp:.2f}", f"{r.market_index:.2f}",
                    f"{r.gini:.4f}", f"{r.unemployment:.4f}",
                    f"{r.supply_chain_stress:.4f}", f"{r.mean_health:.4f}",
                    f"{r.mean_tech_fitness:.4f}", f"{r.mean_flex_fraction:.4f}",
                    r.cascade_size, r.num_alive, f"{r.consumer_demand:.2f}",
                    f"{r.market_sentiment:.4f}", r.tech_generation,
                ])


# ---------------------------------------------------------------------------
# Scenario Presets
# ---------------------------------------------------------------------------

def create_normal_scenario(config: Optional[Config] = None) -> Simulation:
    """Normal operations: no scheduled disruptions."""
    sim = Simulation(config)
    return sim


def create_supply_shock_scenario(config: Optional[Config] = None) -> Simulation:
    """Supply chain shock scenario: demand spike at tick 100, normalize at 150."""
    sim = Simulation(config)
    sim.schedule_event(100, "supply_shock", {"multiplier": 2.5})
    sim.schedule_event(150, "demand_normalize")
    return sim


def create_tech_disruption_scenario(config: Optional[Config] = None) -> Simulation:
    """Technology disruption scenario: major tech shift at tick 150."""
    sim = Simulation(config)
    sim.schedule_event(150, "tech_disruption")
    return sim


def create_market_crash_scenario(config: Optional[Config] = None) -> Simulation:
    """Market crash scenario: supply shock + panic + tech disruption cascade."""
    sim = Simulation(config)
    sim.schedule_event(80, "supply_shock", {"multiplier": 2.0})
    sim.schedule_event(120, "market_panic")
    sim.schedule_event(160, "tech_disruption")
    sim.schedule_event(200, "demand_normalize")
    return sim


def create_stress_test_scenario(config: Optional[Config] = None) -> Simulation:
    """Repeated shocks to test resilience."""
    sim = Simulation(config)
    sim.schedule_event(50, "supply_shock", {"multiplier": 1.8})
    sim.schedule_event(100, "demand_normalize")
    sim.schedule_event(150, "tech_disruption")
    sim.schedule_event(250, "market_panic")
    sim.schedule_event(300, "supply_shock", {"multiplier": 2.2})
    sim.schedule_event(350, "demand_normalize")
    sim.schedule_event(400, "tech_disruption")
    return sim


SCENARIOS = {
    "normal": create_normal_scenario,
    "supply_shock": create_supply_shock_scenario,
    "tech_disruption": create_tech_disruption_scenario,
    "market_crash": create_market_crash_scenario,
    "stress_test": create_stress_test_scenario,
}


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running Integrated Economy simulation (normal scenario)...")
    config = Config(num_firms=30, num_ticks=300, seed=42)
    sim = create_market_crash_scenario(config)
    sim.run(progress_callback=lambda t, n, r: print(
        f"  tick {t:4d}/{n}  phase={r.phase:16s}  GDP={r.gdp:7.1f}  "
        f"index={r.market_index:6.1f}  alive={r.num_alive:3d}  cascade={r.cascade_size}"
    ))

    stats = sim.get_statistics()
    print("\nResults:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
