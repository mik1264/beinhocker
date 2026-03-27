"""
Beer Distribution Game Simulation
==================================
Implementation of the classic MIT Beer Distribution Game (Forrester, 1960).

Models a 4-echelon supply chain (Retailer → Wholesaler → Distributor → Brewery)
with Sterman's (1989) empirically-derived anchor-and-adjust ordering heuristic.

Key references:
- Forrester, J.W. (1961). Industrial Dynamics. MIT Press.
- Sterman, J.D. (1989). Modeling Managerial Behavior: Misperceptions of Feedback
  in a Dynamic Decision Making Experiment. Management Science, 35(3), 321-339.
"""

from __future__ import annotations

import csv
import math
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HOLDING_COST = 0.50   # $/case/week
BACKLOG_COST = 1.00   # $/case/week

ROLE_NAMES = ["Retailer", "Wholesaler", "Distributor", "Brewery"]


# ---------------------------------------------------------------------------
# Demand patterns
# ---------------------------------------------------------------------------

def step_demand(tick: int, step_tick: int = 5, low: int = 4, high: int = 8) -> int:
    """Classic beer game demand: constant `low` then step to `high`."""
    return low if tick < step_tick else high


def constant_demand(tick: int, value: int = 4) -> int:
    return value


def ramp_demand(tick: int, start: int = 4, increase: float = 0.5) -> int:
    return max(0, round(start + increase * tick))


def sine_demand(tick: int, mean: int = 8, amplitude: int = 4, period: int = 20) -> int:
    return max(0, round(mean + amplitude * math.sin(2 * math.pi * tick / period)))


DEMAND_PATTERNS = {
    "step": step_demand,
    "constant": constant_demand,
    "ramp": ramp_demand,
    "sine": sine_demand,
}


# ---------------------------------------------------------------------------
# SupplyChainAgent
# ---------------------------------------------------------------------------

class SupplyChainAgent:
    """A single echelon in the beer supply chain."""

    def __init__(
        self,
        name: str,
        position: int,
        initial_inventory: int = 12,
        shipping_delay: int = 2,
        order_delay: int = 1,
        alpha: float = 0.5,
        beta: float = 0.2,
        theta: float = 0.2,
        desired_inventory: int = 12,
    ):
        self.name = name
        self.position = position  # 0=Retailer .. 3=Brewery

        # State
        self.inventory: int = initial_inventory
        self.backlog: int = 0
        self.expected_demand: float = 4.0
        self.desired_inventory: int = desired_inventory

        # Parameters for anchor-and-adjust
        self.alpha = alpha    # inventory adjustment weight
        self.beta = beta      # supply line adjustment weight
        self.theta = theta    # demand smoothing factor

        # Pipeline: deques model shipping/production delays
        self.shipping_delay = shipping_delay
        self.order_delay = order_delay
        self.incoming_pipeline: deque = deque([4] * shipping_delay)   # beer in transit TO this agent
        self.order_pipeline: deque = deque([4] * order_delay)         # orders in transit FROM this agent

        # Tracking
        self.last_order: int = 4
        self.last_incoming_order: int = 4
        self.cumulative_cost: float = 0.0

        # History (per-tick records)
        self.history_inventory: List[int] = []
        self.history_backlog: List[int] = []
        self.history_orders: List[int] = []
        self.history_incoming_orders: List[int] = []
        self.history_cost: List[float] = []
        self.history_effective_inventory: List[int] = []
        self.history_supply_line: List[int] = []

    @property
    def effective_inventory(self) -> int:
        """Inventory minus backlog (can be negative)."""
        return self.inventory - self.backlog

    @property
    def supply_line(self) -> int:
        """Total beer in incoming pipeline (on order, not yet received)."""
        return sum(self.incoming_pipeline)

    @property
    def desired_supply_line(self) -> float:
        """Desired supply line = expected_demand * total_delay."""
        total_delay = self.shipping_delay + self.order_delay
        return self.expected_demand * total_delay

    def receive_shipment(self) -> int:
        """Receive beer from the incoming pipeline (oldest shipment arrives)."""
        received = self.incoming_pipeline.popleft()
        self.inventory += received
        return received

    def receive_order(self) -> int:
        """Get the incoming order (from the order pipeline)."""
        order = self.order_pipeline.popleft()
        self.last_incoming_order = order
        return order

    def fill_order(self, order: int) -> int:
        """Attempt to fill an incoming order. Returns amount shipped."""
        total_demand = self.backlog + order
        shipped = min(self.inventory, total_demand)
        self.inventory -= shipped
        self.backlog = total_demand - shipped
        return shipped

    def update_expected_demand(self, observed_demand: int) -> None:
        """Exponential smoothing of demand."""
        self.expected_demand += self.theta * (observed_demand - self.expected_demand)

    def decide_order_behavioral(self) -> int:
        """Sterman's anchor-and-adjust heuristic.

        Order = expected_demand
              + alpha * (desired_inventory - effective_inventory)
              + beta  * (desired_supply_line - actual_supply_line)
        """
        anchor = self.expected_demand
        inv_adj = self.alpha * (self.desired_inventory - self.effective_inventory)
        sl_adj = self.beta * (self.desired_supply_line - self.supply_line)
        order = anchor + inv_adj + sl_adj
        order = max(0, round(order))
        self.last_order = order
        return order

    def decide_order_rational(self) -> int:
        """Optimal ordering: pass-through with gentle inventory correction.

        The true optimal for the beer game is close to ordering exactly what
        you receive, with a small correction toward desired inventory. This
        avoids the amplification that aggressive correction creates.
        """
        inv_position = self.effective_inventory + self.supply_line
        target = self.desired_inventory + self.desired_supply_line
        gap = target - inv_position
        # Spread correction over the total pipeline delay to avoid amplification
        total_delay = max(1, self.shipping_delay + self.order_delay)
        correction = gap / total_delay
        order = max(0, round(self.last_incoming_order + correction))
        self.last_order = order
        return order

    def calculate_cost(self) -> float:
        """Calculate this tick's holding + backlog cost."""
        cost = HOLDING_COST * self.inventory + BACKLOG_COST * self.backlog
        self.cumulative_cost += cost
        return cost

    def record_history(self) -> None:
        """Save current state to history."""
        self.history_inventory.append(self.inventory)
        self.history_backlog.append(self.backlog)
        self.history_orders.append(self.last_order)
        self.history_incoming_orders.append(self.last_incoming_order)
        self.history_cost.append(self.cumulative_cost)
        self.history_effective_inventory.append(self.effective_inventory)
        self.history_supply_line.append(self.supply_line)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

@dataclass
class SimulationConfig:
    """Configuration for a Beer Game simulation run."""
    ticks: int = 36
    demand_pattern: str = "step"
    demand_kwargs: dict = field(default_factory=dict)
    shipping_delay: int = 2
    order_delay: int = 1
    alpha: float = 0.5
    beta: float = 0.2
    theta: float = 0.2
    initial_inventory: int = 12
    desired_inventory: int = 12
    rational: bool = False
    information_sharing: bool = False


@dataclass
class SimulationResults:
    """Results from a completed simulation run."""
    agents: List[SupplyChainAgent]
    demand_history: List[int]
    config: SimulationConfig

    @property
    def total_cost(self) -> float:
        return sum(a.cumulative_cost for a in self.agents)

    def agent_costs(self) -> List[Tuple[str, float]]:
        return [(a.name, a.cumulative_cost) for a in self.agents]

    def bullwhip_ratios(self) -> List[Tuple[str, float]]:
        """Variance ratio of orders placed vs orders received for each agent."""
        ratios = []
        for agent in self.agents:
            if not agent.history_orders or not agent.history_incoming_orders:
                ratios.append((agent.name, 0.0))
                continue
            var_out = _variance(agent.history_orders)
            var_in = _variance(agent.history_incoming_orders)
            ratio = var_out / var_in if var_in > 0 else 0.0
            ratios.append((agent.name, ratio))
        return ratios

    def to_csv(self, filepath: str) -> None:
        """Export simulation results to CSV."""
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["tick", "consumer_demand"]
            for agent in self.agents:
                prefix = agent.name
                header.extend([
                    f"{prefix}_inventory",
                    f"{prefix}_backlog",
                    f"{prefix}_effective_inventory",
                    f"{prefix}_order",
                    f"{prefix}_incoming_order",
                    f"{prefix}_supply_line",
                    f"{prefix}_cumulative_cost",
                ])
            writer.writerow(header)

            for t in range(self.config.ticks):
                row = [t, self.demand_history[t]]
                for agent in self.agents:
                    row.extend([
                        agent.history_inventory[t],
                        agent.history_backlog[t],
                        agent.history_effective_inventory[t],
                        agent.history_orders[t],
                        agent.history_incoming_orders[t],
                        agent.history_supply_line[t],
                        round(agent.history_cost[t], 2),
                    ])
                writer.writerow(row)


def _variance(values: List[int]) -> float:
    """Compute variance of a list of values."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / (len(values) - 1)


class Simulation:
    """Runs the Beer Distribution Game simulation."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.demand_fn = DEMAND_PATTERNS[self.config.demand_pattern]

        # Create the 4 agents: Retailer(0), Wholesaler(1), Distributor(2), Brewery(3)
        self.agents: List[SupplyChainAgent] = []
        for i, name in enumerate(ROLE_NAMES):
            agent = SupplyChainAgent(
                name=name,
                position=i,
                initial_inventory=self.config.initial_inventory,
                shipping_delay=self.config.shipping_delay,
                order_delay=self.config.order_delay,
                alpha=self.config.alpha,
                beta=self.config.beta,
                theta=self.config.theta,
                desired_inventory=self.config.desired_inventory,
            )
            self.agents.append(agent)

        self.demand_history: List[int] = []
        self.tick = 0

    def run(self) -> SimulationResults:
        """Execute the full simulation."""
        for t in range(self.config.ticks):
            self.tick = t
            self._step(t)
        return SimulationResults(
            agents=self.agents,
            demand_history=self.demand_history,
            config=self.config,
        )

    def _step(self, t: int) -> None:
        """Execute one tick of the simulation.

        Order of operations (per Sterman/JASSS model):
        1. Receive shipments (advance shipping pipeline)
        2. Receive and fill orders
        3. Update demand expectations
        4. Place orders (anchor-and-adjust or rational)
        5. Calculate costs
        6. Record history
        """
        agents = self.agents
        consumer_demand = self.demand_fn(t, **self.config.demand_kwargs)
        self.demand_history.append(consumer_demand)

        # --- Step 1: Receive shipments ---
        for agent in agents:
            agent.receive_shipment()

        # --- Step 2: Receive and fill orders ---
        # Orders flow downstream: consumer → retailer → wholesaler → distributor → brewery
        # Beer flows upstream:   brewery → distributor → wholesaler → retailer → consumer
        incoming_orders = [0] * 4

        # Retailer receives consumer demand
        incoming_orders[0] = consumer_demand

        # Other agents receive orders from downstream (from order pipeline)
        for i in range(1, 4):
            incoming_orders[i] = agents[i].receive_order()

        # Fill orders and determine shipments
        shipments = [0] * 4
        for i, agent in enumerate(agents):
            if i == 0:
                # Retailer: fill consumer demand directly
                agent.last_incoming_order = consumer_demand
                shipments[i] = agent.fill_order(consumer_demand)
            else:
                shipments[i] = agent.fill_order(incoming_orders[i])

        # Ship beer into downstream agent's incoming pipeline
        # agents[0] (Retailer) ships to consumer (not modeled)
        # agents[1] (Wholesaler) ships to Retailer
        # agents[2] (Distributor) ships to Wholesaler
        # agents[3] (Brewery) ships to Distributor
        for i in range(1, 4):
            agents[i - 1].incoming_pipeline.append(shipments[i])

        # Brewery's incoming pipeline gets filled by "production" (unlimited raw materials)
        # The brewery's own order becomes production, delivered after shipping_delay
        # This will be set after order decision below

        # --- Step 3: Update demand expectations ---
        for i, agent in enumerate(agents):
            if self.config.information_sharing and i > 0:
                # With information sharing, all agents see consumer demand
                agent.update_expected_demand(consumer_demand)
            else:
                agent.update_expected_demand(agent.last_incoming_order)

        # --- Step 4: Place orders ---
        orders = [0] * 4
        for i, agent in enumerate(agents):
            if self.config.rational:
                orders[i] = agent.decide_order_rational()
            else:
                orders[i] = agent.decide_order_behavioral()

        # Orders go into the upstream agent's order pipeline
        # Retailer's order → Wholesaler's order pipeline
        # Wholesaler's order → Distributor's order pipeline
        # Distributor's order → Brewery's order pipeline
        for i in range(3):
            agents[i + 1].order_pipeline.append(orders[i])

        # Brewery's order = production start → goes into its own incoming pipeline after delay
        agents[3].incoming_pipeline.append(orders[3])

        # --- Step 5: Calculate costs ---
        for agent in agents:
            agent.calculate_cost()

        # --- Step 6: Record history ---
        for agent in agents:
            agent.record_history()


# ---------------------------------------------------------------------------
# Convenience runner
# ---------------------------------------------------------------------------

def run_comparison(config_behavioral: SimulationConfig,
                   config_rational: Optional[SimulationConfig] = None) -> Tuple[SimulationResults, SimulationResults]:
    """Run behavioral and rational simulations for comparison."""
    if config_rational is None:
        import copy
        config_rational = copy.deepcopy(config_behavioral)
        config_rational.rational = True

    sim_b = Simulation(config_behavioral)
    sim_r = Simulation(config_rational)
    return sim_b.run(), sim_r.run()


def print_results(results: SimulationResults, label: str = "") -> None:
    """Print a summary of simulation results."""
    if label:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}")

    print(f"\nTotal system cost: ${results.total_cost:,.2f}")
    print(f"\nPer-agent costs:")
    for name, cost in results.agent_costs():
        print(f"  {name:12s}: ${cost:>8,.2f}")

    print(f"\nBullwhip amplification ratios (Var(orders_out)/Var(orders_in)):")
    for name, ratio in results.bullwhip_ratios():
        print(f"  {name:12s}: {ratio:>6.2f}")

    print(f"\nFinal state:")
    for agent in results.agents:
        print(f"  {agent.name:12s}: inventory={agent.inventory:>3d}, "
              f"backlog={agent.backlog:>3d}, "
              f"supply_line={agent.supply_line:>3d}")


if __name__ == "__main__":
    # Quick demo run
    config = SimulationConfig(ticks=36)
    results = Simulation(config).run()
    print_results(results, "Beer Distribution Game — Behavioral (Sterman Heuristic)")
