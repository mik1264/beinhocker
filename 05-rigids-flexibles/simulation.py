"""
Rigids vs Flexibles: Organizational Adaptation Simulation

Based on Harrington's "Rigidity of Social Systems" (JPE, 1999) and
Beinhocker's "The Origin of Wealth" (2006).

Models a hierarchical organization where agents are either "Rigid" (always
play their born strategy) or "Flexible" (observe the environment and adapt).
Promotion is tournament-based: best performers advance, worst exit. The
environment switches between A-favored and B-favored states following a
punctuated equilibrium or random pattern.

Key finding: rigid agents dominate during stability but create organizational
fragility at regime changes. The optimal fraction of flexible agents balances
steady-state efficiency against transition resilience.

References:
  - Harrington, "Rigidity of Social Systems" (JPE, 1999)
  - March, "Exploration and Exploitation in Organizational Learning" (1991)
  - Tushman & O'Reilly, "The Ambidextrous Organization" (1996)
  - Beinhocker, "The Origin of Wealth" (2006)
"""

import random
import csv
import json
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    """An individual in the organizational hierarchy."""
    id: int
    agent_type: str           # "rigid" or "flexible"
    fixed_strategy: str       # "A" or "B" -- rigids always play this
    experience: float = 0.0
    level: int = 0
    performance_history: list = field(default_factory=list)
    age: int = 0

    def choose_strategy(self, env_state: str, noise: float, rng: np.random.Generator) -> str:
        """Decide which strategy to play this tick."""
        if self.agent_type == "rigid":
            return self.fixed_strategy
        else:
            # Flexible agents observe the environment with noise
            if rng.random() < noise:
                # Misread the environment
                return "B" if env_state == "A" else "A"
            return env_state

    def get_performance(self, env_state: str, noise: float,
                        experience_weight: float, rng: np.random.Generator) -> float:
        """Calculate this tick's performance score."""
        chosen = self.choose_strategy(env_state, noise, rng)
        match_score = 1.0 if chosen == env_state else 0.0
        # Log-saturating experience bonus: caps around ~0.5 at weight=0.1
        exp_bonus = experience_weight * math.log1p(self.experience)
        return match_score + exp_bonus

    def tick_experience(self, experience_rate_rigid: float = 1.0,
                        experience_rate_flexible: float = 0.5):
        """Accumulate experience. Rigids gain faster due to consistency."""
        if self.agent_type == "rigid":
            self.experience += experience_rate_rigid
        else:
            self.experience += experience_rate_flexible
        self.age += 1


@dataclass
class TickRecord:
    """One tick of simulation data for output."""
    tick: int
    env_state: str
    env_just_switched: bool
    org_performance: float
    rigid_count: int
    flexible_count: int
    rigid_fraction: float
    # Per-level rigid fractions (serialized as JSON list)
    level_rigid_fractions: list
    # Top-level composition
    top_level_rigid_fraction: float
    # Performance by type
    rigid_avg_performance: float
    flexible_avg_performance: float
    # Transition metrics
    ticks_since_switch: int
    adaptation_score: float


class Environment:
    """
    Two-state Markov environment: A-favored or B-favored.

    In punctuated mode, stable periods are drawn from a geometric distribution
    with mean = stability parameter. In random mode, each tick independently
    selects state with equal probability.
    """

    def __init__(self, stability: float = 100.0, mode: str = "punctuated",
                 rng: np.random.Generator = None):
        self.stability = max(stability, 1.0)
        self.mode = mode
        self.rng = rng or np.random.default_rng()
        self.state = self.rng.choice(["A", "B"])
        self.ticks_in_state = 0
        self.next_switch_at = self._draw_duration() if mode == "punctuated" else None
        self.switch_history: list[int] = []
        self.just_switched = False

    def _draw_duration(self) -> int:
        """Draw the next stable period duration from geometric distribution."""
        return max(1, int(self.rng.geometric(1.0 / self.stability)))

    def step(self, tick: int):
        """Advance the environment one tick."""
        self.ticks_in_state += 1
        self.just_switched = False

        if self.mode == "punctuated":
            if self.ticks_in_state >= self.next_switch_at:
                self._switch(tick)
        else:
            # Random mode: switch with probability 1/stability each tick
            if self.rng.random() < 1.0 / self.stability:
                self._switch(tick)

    def _switch(self, tick: int):
        """Switch environment state."""
        self.state = "B" if self.state == "A" else "A"
        self.switch_history.append(tick)
        self.ticks_in_state = 0
        self.just_switched = True
        if self.mode == "punctuated":
            self.next_switch_at = self._draw_duration()


class Hierarchy:
    """
    Multi-level organizational hierarchy with tournament-based promotion.

    Level 0 is the bottom (most agents), level L-1 is the top (fewest agents).
    Each level has branching_factor times fewer agents than the one below.
    """

    def __init__(self, levels: int = 4, branching_factor: int = 3,
                 rigid_fraction: float = 0.5, rng: np.random.Generator = None):
        self.levels = levels
        self.branching_factor = branching_factor
        self.rng = rng or np.random.default_rng()
        self.next_id = 0

        # Build hierarchy: level 0 has B^(L-1) agents, level 1 has B^(L-2), etc.
        self.agents_by_level: dict[int, list[Agent]] = {}
        for level in range(levels):
            count = branching_factor ** (levels - 1 - level)
            agents = []
            for _ in range(count):
                agents.append(self._make_agent(level, rigid_fraction))
            self.agents_by_level[level] = agents

    def _make_agent(self, level: int, rigid_fraction: float) -> Agent:
        """Create a new random agent."""
        agent_type = "rigid" if self.rng.random() < rigid_fraction else "flexible"
        fixed_strategy = self.rng.choice(["A", "B"])
        agent = Agent(
            id=self.next_id,
            agent_type=agent_type,
            fixed_strategy=fixed_strategy,
            level=level
        )
        self.next_id += 1
        return agent

    def total_agents(self) -> int:
        return sum(len(agents) for agents in self.agents_by_level.values())

    def level_size(self, level: int) -> int:
        return len(self.agents_by_level[level])

    def all_agents(self) -> list[Agent]:
        result = []
        for level in range(self.levels):
            result.extend(self.agents_by_level[level])
        return result

    def get_rigid_fraction(self, level: Optional[int] = None) -> float:
        """Get fraction of rigid agents at a given level, or overall."""
        if level is not None:
            agents = self.agents_by_level[level]
        else:
            agents = self.all_agents()
        if not agents:
            return 0.0
        return sum(1 for a in agents if a.agent_type == "rigid") / len(agents)

    def promote_and_exit(self, performances: dict[int, float],
                         rigid_fraction_new: float = 0.5):
        """
        Tournament-based promotion:
        1. At each level (bottom to top-1), find the best performer
        2. Promote them up one level, replacing the worst performer there
        3. The worst at the bottom level exits; a new random agent enters
        """
        # At each level pair (l, l+1), promote best from l, demote worst from l+1
        for level in range(self.levels - 1):
            lower = self.agents_by_level[level]
            upper = self.agents_by_level[level + 1]

            if not lower or not upper:
                continue

            # Find best performer in lower level
            best_lower = max(lower, key=lambda a: performances.get(a.id, 0.0))
            # Find worst performer in upper level
            worst_upper = min(upper, key=lambda a: performances.get(a.id, 0.0))

            # Promote: move best_lower up, worst_upper down
            lower.remove(best_lower)
            upper.remove(worst_upper)

            best_lower.level = level + 1
            worst_upper.level = level

            upper.append(best_lower)
            lower.append(worst_upper)

        # At the bottom level, remove worst performer, add new random agent
        bottom = self.agents_by_level[0]
        if bottom:
            worst_bottom = min(bottom, key=lambda a: performances.get(a.id, 0.0))
            bottom.remove(worst_bottom)
            new_agent = self._make_agent(0, rigid_fraction_new)
            bottom.append(new_agent)


class Simulation:
    """
    Main simulation engine for Rigids vs Flexibles.

    Each tick:
    1. Environment may switch state
    2. All agents evaluate performance against current environment
    3. Experience accumulates
    4. Tournament-based promotion/demotion
    5. Metrics recorded
    """

    def __init__(self, levels: int = 4, branching_factor: int = 3,
                 ticks: int = 500, stability: float = 100.0,
                 rigid_fraction: float = 0.5, experience_weight: float = 0.1,
                 noise: float = 0.1, mode: str = "punctuated",
                 experience_rate_rigid: float = 1.0,
                 experience_rate_flexible: float = 0.5,
                 seed: Optional[int] = None):
        self.ticks = ticks
        self.experience_weight = experience_weight
        self.noise = noise
        self.rigid_fraction = rigid_fraction
        self.experience_rate_rigid = experience_rate_rigid
        self.experience_rate_flexible = experience_rate_flexible

        self.rng = np.random.default_rng(seed)
        self.env = Environment(stability=stability, mode=mode, rng=self.rng)
        self.hierarchy = Hierarchy(
            levels=levels, branching_factor=branching_factor,
            rigid_fraction=rigid_fraction, rng=self.rng
        )

        self.history: list[TickRecord] = []
        self.current_tick = 0
        self.ticks_since_switch = 0

    def step(self) -> TickRecord:
        """Execute one simulation tick."""
        # 1. Advance environment
        self.env.step(self.current_tick)

        if self.env.just_switched:
            self.ticks_since_switch = 0
        else:
            self.ticks_since_switch += 1

        env_state = self.env.state

        # 2. Evaluate all agents' performance
        performances: dict[int, float] = {}
        rigid_perfs = []
        flexible_perfs = []

        for agent in self.hierarchy.all_agents():
            perf = agent.get_performance(env_state, self.noise,
                                         self.experience_weight, self.rng)
            performances[agent.id] = perf
            agent.performance_history.append(perf)

            if agent.agent_type == "rigid":
                rigid_perfs.append(perf)
            else:
                flexible_perfs.append(perf)

            # 3. Accumulate experience
            agent.tick_experience(self.experience_rate_rigid,
                                  self.experience_rate_flexible)

        # 4. Promotion tournament
        self.hierarchy.promote_and_exit(performances, self.rigid_fraction)

        # 5. Compute metrics
        all_agents = self.hierarchy.all_agents()
        total = len(all_agents)
        rigid_count = sum(1 for a in all_agents if a.agent_type == "rigid")
        flexible_count = total - rigid_count
        rigid_frac = rigid_count / total if total > 0 else 0.0

        org_performance = sum(performances.values()) / total if total > 0 else 0.0

        level_rigid_fracs = []
        for level in range(self.hierarchy.levels):
            level_rigid_fracs.append(self.hierarchy.get_rigid_fraction(level))

        top_rigid_frac = self.hierarchy.get_rigid_fraction(
            self.hierarchy.levels - 1)

        rigid_avg = np.mean(rigid_perfs) if rigid_perfs else 0.0
        flexible_avg = np.mean(flexible_perfs) if flexible_perfs else 0.0

        # Adaptation score: rolling average performance over last 10 ticks
        recent_perfs = [r.org_performance for r in self.history[-9:]]
        recent_perfs.append(org_performance)
        adaptation_score = np.mean(recent_perfs)

        record = TickRecord(
            tick=self.current_tick,
            env_state=env_state,
            env_just_switched=self.env.just_switched,
            org_performance=org_performance,
            rigid_count=rigid_count,
            flexible_count=flexible_count,
            rigid_fraction=rigid_frac,
            level_rigid_fractions=level_rigid_fracs,
            top_level_rigid_fraction=top_rigid_frac,
            rigid_avg_performance=float(rigid_avg),
            flexible_avg_performance=float(flexible_avg),
            ticks_since_switch=self.ticks_since_switch,
            adaptation_score=adaptation_score,
        )
        self.history.append(record)
        self.current_tick += 1
        return record

    def run(self) -> list[TickRecord]:
        """Run the full simulation."""
        for _ in range(self.ticks):
            self.step()
        return self.history

    def get_transition_analysis(self) -> list[dict]:
        """Analyze performance around each environment switch."""
        transitions = []
        switch_ticks = self.env.switch_history

        for switch_tick in switch_ticks:
            # Look at performance 10 ticks before and 20 ticks after
            window_before = 10
            window_after = 20

            before_start = max(0, switch_tick - window_before)
            after_end = min(len(self.history), switch_tick + window_after)

            if before_start >= len(self.history) or switch_tick >= len(self.history):
                continue

            before_perfs = [self.history[t].org_performance
                           for t in range(before_start, min(switch_tick, len(self.history)))]
            after_perfs = [self.history[t].org_performance
                          for t in range(switch_tick, after_end)]

            before_avg = np.mean(before_perfs) if before_perfs else 0.0
            after_avg = np.mean(after_perfs) if after_perfs else 0.0

            # Performance drop = pre-switch avg minus post-switch avg
            perf_drop = float(before_avg - after_avg)

            # Recovery time: how many ticks after switch until performance
            # returns to 90% of pre-switch level
            recovery_ticks = 0
            threshold = float(before_avg) * 0.9
            for i, t in enumerate(range(switch_tick, after_end)):
                if self.history[t].org_performance >= threshold:
                    recovery_ticks = i
                    break
            else:
                recovery_ticks = after_end - switch_tick

            transitions.append({
                "switch_tick": switch_tick,
                "before_avg_performance": float(before_avg),
                "after_avg_performance": float(after_avg),
                "performance_drop": perf_drop,
                "recovery_ticks": recovery_ticks,
                "rigid_fraction_at_switch": self.history[min(switch_tick, len(self.history) - 1)].rigid_fraction,
            })

        return transitions

    def to_csv(self, filename: str):
        """Write simulation history to CSV."""
        if not self.history:
            return

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            header = [
                "tick", "env_state", "env_just_switched",
                "org_performance", "rigid_count", "flexible_count",
                "rigid_fraction", "top_level_rigid_fraction",
                "rigid_avg_performance", "flexible_avg_performance",
                "ticks_since_switch", "adaptation_score",
            ]
            # Add per-level columns
            for level in range(self.hierarchy.levels):
                header.append(f"level_{level}_rigid_fraction")
            writer.writerow(header)

            for r in self.history:
                row = [
                    r.tick, r.env_state, int(r.env_just_switched),
                    f"{r.org_performance:.4f}", r.rigid_count, r.flexible_count,
                    f"{r.rigid_fraction:.4f}", f"{r.top_level_rigid_fraction:.4f}",
                    f"{r.rigid_avg_performance:.4f}",
                    f"{r.flexible_avg_performance:.4f}",
                    r.ticks_since_switch, f"{r.adaptation_score:.4f}",
                ]
                for frac in r.level_rigid_fractions:
                    row.append(f"{frac:.4f}")
                writer.writerow(row)

    def to_json(self) -> dict:
        """Export full simulation state as JSON-serializable dict."""
        transitions = self.get_transition_analysis()

        return {
            "params": {
                "levels": self.hierarchy.levels,
                "branching_factor": self.hierarchy.branching_factor,
                "ticks": self.ticks,
                "stability": self.env.stability,
                "rigid_fraction_initial": self.rigid_fraction,
                "experience_weight": self.experience_weight,
                "noise": self.noise,
                "mode": self.env.mode,
            },
            "total_agents": self.hierarchy.total_agents(),
            "level_sizes": [self.hierarchy.level_size(l)
                           for l in range(self.hierarchy.levels)],
            "history": [
                {
                    "tick": r.tick,
                    "env_state": r.env_state,
                    "env_just_switched": r.env_just_switched,
                    "org_performance": round(r.org_performance, 4),
                    "rigid_count": r.rigid_count,
                    "flexible_count": r.flexible_count,
                    "rigid_fraction": round(r.rigid_fraction, 4),
                    "level_rigid_fractions": [round(f, 4)
                                              for f in r.level_rigid_fractions],
                    "top_level_rigid_fraction": round(
                        r.top_level_rigid_fraction, 4),
                    "rigid_avg_performance": round(r.rigid_avg_performance, 4),
                    "flexible_avg_performance": round(
                        r.flexible_avg_performance, 4),
                    "ticks_since_switch": r.ticks_since_switch,
                    "adaptation_score": round(r.adaptation_score, 4),
                }
                for r in self.history
            ],
            "transitions": transitions,
            "agents": [
                {
                    "id": a.id,
                    "type": a.agent_type,
                    "strategy": a.fixed_strategy,
                    "level": a.level,
                    "experience": round(a.experience, 2),
                    "age": a.age,
                }
                for a in self.hierarchy.all_agents()
            ],
            "env_switches": self.env.switch_history,
        }


def run_sweep(levels: int = 4, branching_factor: int = 3,
              ticks: int = 500, stability: float = 100.0,
              experience_weight: float = 0.1, noise: float = 0.1,
              mode: str = "punctuated", seed: Optional[int] = None,
              steps: int = 11) -> list[dict]:
    """
    Sweep over rigid_fraction from 0.0 to 1.0 and measure outcomes.

    Returns list of dicts with rigid_fraction, avg_performance,
    avg_transition_cost, avg_recovery_time, etc.
    """
    results = []
    fractions = np.linspace(0.0, 1.0, steps)
    base_seed = seed if seed is not None else random.randint(0, 2**31)

    for rf in fractions:
        sim = Simulation(
            levels=levels, branching_factor=branching_factor,
            ticks=ticks, stability=stability,
            rigid_fraction=rf, experience_weight=experience_weight,
            noise=noise, mode=mode, seed=base_seed
        )
        sim.run()

        transitions = sim.get_transition_analysis()
        avg_perf = np.mean([r.org_performance for r in sim.history])

        avg_drop = 0.0
        avg_recovery = 0.0
        if transitions:
            avg_drop = np.mean([t["performance_drop"] for t in transitions])
            avg_recovery = np.mean([t["recovery_ticks"]
                                    for t in transitions])

        # Steady-state performance: average during stable periods
        # (ticks_since_switch > 20)
        stable_perfs = [r.org_performance for r in sim.history
                        if r.ticks_since_switch > 20]
        steady_perf = np.mean(stable_perfs) if stable_perfs else avg_perf

        results.append({
            "rigid_fraction": round(float(rf), 2),
            "avg_performance": round(float(avg_perf), 4),
            "steady_state_performance": round(float(steady_perf), 4),
            "avg_transition_cost": round(float(avg_drop), 4),
            "avg_recovery_ticks": round(float(avg_recovery), 1),
            "num_transitions": len(transitions),
            "final_rigid_fraction": round(
                sim.history[-1].rigid_fraction, 4) if sim.history else rf,
        })

    return results
