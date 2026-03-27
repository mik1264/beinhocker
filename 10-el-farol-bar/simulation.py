"""
El Farol Bar Problem Simulation
Based on Arthur (1994) "Inductive Reasoning and Bounded Rationality"
As described in Beinhocker, The Origin of Wealth, Chapter 6

Implements the El Farol Bar Problem where:
- N agents decide each week whether to attend a bar
- Bar is enjoyable if <= threshold attend, overcrowded if > threshold
- Each agent maintains a pool of prediction strategies
- Agents use the strategy that has performed best recently
- No equilibrium exists -- attendance oscillates endogenously
"""

import random
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Callable


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Simulation configuration parameters."""
    num_agents: int = 100
    num_ticks: int = 200
    threshold: int = 60
    num_strategies: int = 10
    memory_length: int = 10
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Prediction Strategies
# ---------------------------------------------------------------------------

def make_last_week_mirror() -> dict:
    """Go if last week's attendance was below threshold."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        return history[-1] < threshold

    return {'name': 'last-week-mirror', 'predict': predict, 'score': 0.0}


def make_mean_of_n(n: int) -> dict:
    """Go if the mean of last N weeks was below threshold."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        window = history[-n:]
        return np.mean(window) < threshold

    return {'name': f'mean-of-{n}', 'predict': predict, 'score': 0.0}


def make_trend() -> dict:
    """Go if attendance has been trending down (extrapolate the trend)."""
    def predict(history: List[int], threshold: int) -> bool:
        if len(history) < 2:
            return random.random() < 0.5
        trend = history[-1] - history[-2]
        projected = history[-1] + trend
        return projected < threshold

    return {'name': 'trend', 'predict': predict, 'score': 0.0}


def make_contrarian() -> dict:
    """Do the opposite of what last week's attendance suggests."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        return history[-1] >= threshold  # go when it was crowded (expect others to stay away)

    return {'name': 'contrarian', 'predict': predict, 'score': 0.0}


def make_random(go_prob: float) -> dict:
    """Go with a fixed probability."""
    def predict(history: List[int], threshold: int) -> bool:
        return random.random() < go_prob

    return {'name': f'random-{go_prob:.0%}', 'predict': predict, 'score': 0.0}


def make_threshold_rule(fixed_threshold: int) -> dict:
    """Go if last week's attendance was below a fixed personal threshold."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        return history[-1] < fixed_threshold

    return {'name': f'threshold-{fixed_threshold}', 'predict': predict, 'score': 0.0}


def make_periodic(period: int) -> dict:
    """Go every N-th week (cycle strategy)."""
    counter = {'tick': 0}

    def predict(history: List[int], threshold: int) -> bool:
        counter['tick'] += 1
        return (counter['tick'] % period) == 0

    return {'name': f'periodic-{period}', 'predict': predict, 'score': 0.0}


def make_weighted_average() -> dict:
    """Go if exponentially weighted average of recent attendance < threshold."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        alpha = 0.3
        ema = history[0]
        for val in history[1:]:
            ema = alpha * val + (1 - alpha) * ema
        return ema < threshold

    return {'name': 'weighted-avg', 'predict': predict, 'score': 0.0}


def make_cycle_detector() -> dict:
    """Look for a 2-week cycle pattern and predict accordingly."""
    def predict(history: List[int], threshold: int) -> bool:
        if len(history) < 4:
            return random.random() < 0.5
        # Check if there's an alternating pattern
        last4 = history[-4:]
        above = [x >= threshold for x in last4]
        if above[-2] == above[-4] and above[-1] == above[-3]:
            # Pattern detected, predict opposite of last week
            return above[-1]  # if last was crowded, predict less (so go)
        return last4[-1] < threshold

    return {'name': 'cycle-detector', 'predict': predict, 'score': 0.0}


def make_median_rule() -> dict:
    """Go if median of last 5 weeks was below threshold."""
    def predict(history: List[int], threshold: int) -> bool:
        if not history:
            return random.random() < 0.5
        window = history[-5:]
        return np.median(window) < threshold

    return {'name': 'median-5', 'predict': predict, 'score': 0.0}


def generate_strategy_pool(num_strategies: int, threshold: int) -> list:
    """Generate a random pool of prediction strategies for an agent.

    Each agent gets a diverse but randomly selected subset of strategies.
    """
    all_strategies = [
        make_last_week_mirror,
        lambda: make_mean_of_n(3),
        lambda: make_mean_of_n(5),
        lambda: make_mean_of_n(8),
        make_trend,
        make_contrarian,
        lambda: make_random(0.4),
        lambda: make_random(0.5),
        lambda: make_random(0.6),
        lambda: make_threshold_rule(threshold - 10),
        lambda: make_threshold_rule(threshold),
        lambda: make_threshold_rule(threshold + 10),
        lambda: make_periodic(2),
        lambda: make_periodic(3),
        lambda: make_periodic(5),
        make_weighted_average,
        make_cycle_detector,
        make_median_rule,
    ]

    pool = []
    # Ensure diversity: pick from available templates, with replacement if needed
    indices = list(range(len(all_strategies)))
    for _ in range(num_strategies):
        idx = random.choice(indices)
        pool.append(all_strategies[idx]())
    return pool


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class Agent:
    """An agent who decides each week whether to attend the bar.

    Maintains a pool of prediction strategies and uses the one
    that has performed best recently.
    """

    def __init__(self, agent_id: int, num_strategies: int, threshold: int):
        self.agent_id = agent_id
        self.threshold = threshold
        self.strategies = generate_strategy_pool(num_strategies, threshold)
        self.active_strategy: Optional[dict] = None
        self.attending = False
        self.attendance_history: List[bool] = []

    def decide(self, history: List[int]) -> bool:
        """Decide whether to attend the bar this week.

        Uses the strategy with the highest cumulative score.
        """
        # Select best-performing strategy
        self.active_strategy = max(self.strategies, key=lambda s: s['score'])
        self.attending = self.active_strategy['predict'](history, self.threshold)
        self.attendance_history.append(self.attending)
        return self.attending

    def update_scores(self, actual_attendance: int):
        """Update strategy scores based on what actually happened.

        A strategy scores +1 if its prediction would have been correct:
        - Predicted "go" and attendance <= threshold (good decision)
        - Predicted "don't go" and attendance > threshold (good decision)
        """
        for strategy in self.strategies:
            # What would this strategy have predicted?
            # The active strategy already made its prediction, but we need
            # to know what each strategy would have done
            would_go = strategy == self.active_strategy and self.attending
            if strategy != self.active_strategy:
                # Re-evaluate: this is a simplification -- in Arthur's model
                # strategies are scored on accuracy of the attendance prediction
                # We approximate by scoring if the decision would have been right
                would_go = strategy == self.active_strategy

            # Score based on whether attending was a good idea
            good_to_go = actual_attendance <= self.threshold

            # For the active strategy, we know the decision
            if strategy == self.active_strategy:
                if (self.attending and good_to_go) or (not self.attending and not good_to_go):
                    strategy['score'] += 1.0
                else:
                    strategy['score'] -= 1.0
            else:
                # For inactive strategies, simulate what they would have done
                # We use a lightweight scoring: just track if they'd have been right
                # about the attendance level relative to threshold
                if good_to_go:
                    # Attendance was low -- strategies that predict "go" were right
                    strategy['score'] += 0.5
                else:
                    # Attendance was high -- strategies that predict "don't go" were right
                    strategy['score'] += 0.5

    def update_scores_accurate(self, history: List[int], actual_attendance: int):
        """More accurate scoring: re-run each strategy's prediction.

        This is closer to Arthur's original model where all strategies
        are evaluated against the outcome each period.
        """
        good_to_go = actual_attendance <= self.threshold

        for strategy in self.strategies:
            # What would this strategy have predicted with the history
            # available BEFORE this week's decision?
            would_go = strategy['predict'](history, self.threshold)

            if (would_go and good_to_go) or (not would_go and not good_to_go):
                strategy['score'] += 1.0
            else:
                strategy['score'] -= 1.0


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the El Farol Bar Problem simulation."""

    def __init__(self, config: Optional[Config] = None, **kwargs):
        if config is None:
            config = Config(**kwargs)
        self.config = config

        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)

        # Create agents
        self.agents = [
            Agent(agent_id=i, num_strategies=config.num_strategies,
                  threshold=config.threshold)
            for i in range(config.num_agents)
        ]

        # History tracking
        self.attendance_history: List[int] = []
        self.strategy_usage: List[dict] = []  # per-tick strategy name counts
        self.mean_accuracy: List[float] = []
        self.tick = 0

        # Initialize with some random history to bootstrap strategies
        for _ in range(config.memory_length):
            self.attendance_history.append(
                random.randint(
                    int(config.num_agents * 0.3),
                    int(config.num_agents * 0.7)
                )
            )

    def step(self):
        """Execute one time step (week) of the simulation."""
        # 1. Each agent decides whether to attend
        history_snapshot = list(self.attendance_history)
        decisions = []
        for agent in self.agents:
            decisions.append(agent.decide(history_snapshot))

        # 2. Count attendance
        attendance = sum(decisions)
        self.attendance_history.append(attendance)

        # 3. Update all strategy scores (using accurate method)
        for agent in self.agents:
            agent.update_scores_accurate(history_snapshot, attendance)

        # 4. Track strategy usage
        usage = {}
        for agent in self.agents:
            if agent.active_strategy:
                name = agent.active_strategy['name']
                usage[name] = usage.get(name, 0) + 1
        self.strategy_usage.append(usage)

        # 5. Track mean prediction accuracy
        correct = 0
        total = len(self.agents)
        good_to_go = attendance <= self.config.threshold
        for agent in self.agents:
            if (agent.attending and good_to_go) or (not agent.attending and not good_to_go):
                correct += 1
        self.mean_accuracy.append(correct / total if total > 0 else 0.0)

        self.tick += 1

    def run(self, progress_callback=None):
        """Run the full simulation."""
        for t in range(self.config.num_ticks):
            self.step()
            if progress_callback and t % 50 == 0:
                progress_callback(t, self.config.num_ticks)

    def get_simulation_attendance(self) -> List[int]:
        """Return only the attendance from simulation ticks (not bootstrap)."""
        return self.attendance_history[self.config.memory_length:]

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        sim_attendance = self.get_simulation_attendance()
        att_arr = np.array(sim_attendance)
        threshold = self.config.threshold

        # Basic attendance stats
        mean_att = float(np.mean(att_arr))
        std_att = float(np.std(att_arr))
        min_att = int(np.min(att_arr))
        max_att = int(np.max(att_arr))
        median_att = float(np.median(att_arr))

        # Threshold crossing analysis
        above_threshold = int(np.sum(att_arr > threshold))
        below_or_equal = int(np.sum(att_arr <= threshold))
        pct_above = above_threshold / len(att_arr) * 100

        # Oscillation analysis
        crossings = 0
        for i in range(1, len(att_arr)):
            if (att_arr[i] > threshold) != (att_arr[i - 1] > threshold):
                crossings += 1
        crossing_rate = crossings / (len(att_arr) - 1) if len(att_arr) > 1 else 0.0

        # Autocorrelation (lag-1)
        if len(att_arr) > 1:
            ac1 = float(np.corrcoef(att_arr[:-1], att_arr[1:])[0, 1])
        else:
            ac1 = 0.0

        # Strategy distribution
        final_usage = self.strategy_usage[-1] if self.strategy_usage else {}

        # Mean accuracy over simulation
        mean_acc = float(np.mean(self.mean_accuracy)) if self.mean_accuracy else 0.0

        # Volatility (coefficient of variation)
        cv = std_att / mean_att if mean_att > 0 else 0.0

        # Runs test: count consecutive runs above/below threshold
        runs = 1
        for i in range(1, len(att_arr)):
            if (att_arr[i] > threshold) != (att_arr[i - 1] > threshold):
                runs += 1
        mean_run_length = len(att_arr) / runs if runs > 0 else len(att_arr)

        stats = {
            'num_ticks': self.tick,
            'num_agents': self.config.num_agents,
            'threshold': threshold,
            'num_strategies': self.config.num_strategies,
            'mean_attendance': mean_att,
            'std_attendance': std_att,
            'min_attendance': min_att,
            'max_attendance': max_att,
            'median_attendance': median_att,
            'coeff_variation': cv,
            'weeks_above_threshold': above_threshold,
            'weeks_at_or_below': below_or_equal,
            'pct_above_threshold': pct_above,
            'threshold_crossings': crossings,
            'crossing_rate': crossing_rate,
            'mean_run_length': mean_run_length,
            'autocorrelation_lag1': ac1,
            'mean_accuracy': mean_acc,
            'final_strategy_usage': final_usage,
        }
        return stats

    def get_timeseries_data(self) -> dict:
        """Return time series data suitable for visualization."""
        sim_attendance = self.get_simulation_attendance()
        n = len(sim_attendance)

        # Collect all strategy names across all ticks
        all_names = set()
        for usage in self.strategy_usage:
            all_names.update(usage.keys())
        all_names = sorted(all_names)

        # Build strategy time series
        strategy_ts = {name: [] for name in all_names}
        for usage in self.strategy_usage:
            for name in all_names:
                strategy_ts[name].append(usage.get(name, 0))

        return {
            'tick': list(range(n)),
            'attendance': sim_attendance,
            'threshold': [self.config.threshold] * n,
            'accuracy': self.mean_accuracy[:n],
            'strategy_usage': strategy_ts,
            'strategy_names': all_names,
        }


if __name__ == '__main__':
    print("Running El Farol Bar Problem simulation...")
    config = Config(num_agents=100, num_ticks=200, seed=42)
    sim = Simulation(config=config)
    sim.run(progress_callback=lambda t, n: print(f"  tick {t}/{n}"))
    stats = sim.get_statistics()
    print("\nResults:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        elif isinstance(v, dict):
            print(f"  {k}:")
            for sk, sv in v.items():
                print(f"    {sk}: {sv}")
        else:
            print(f"  {k}: {v}")
