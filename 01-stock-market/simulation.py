"""
SFI Artificial Stock Market Simulation
Based on Arthur, Holland, LeBaron, Palmer, Tayler (1997)
"Asset Pricing Under Endogenous Expectations in an Artificial Stock Market"

Implements the Santa Fe Institute Artificial Stock Market with:
- Heterogeneous agents using condition-action forecasting rules
- Genetic algorithm evolution of trading strategies
- Call market clearing mechanism
- AR(1) dividend process
"""

import random
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Forecasting Rule
# ---------------------------------------------------------------------------

@dataclass
class ForecastRule:
    """A condition-action forecasting rule.

    Condition: 12-element ternary array (0, 1, 2=don't-care)
    Action: linear forecast E[p+d] = a*(p+d) + b
    """
    condition: list  # length-12 ternary values
    a: float         # slope of linear forecast
    b: float         # intercept of linear forecast
    variance: float = 4.0   # tracked forecast variance
    fitness: float = 0.0
    age: int = 0

    @property
    def specificity(self):
        return sum(1 for bit in self.condition if bit != 2)

    def matches(self, market_state: list) -> bool:
        for cond_bit, state_bit in zip(self.condition, market_state):
            if cond_bit == 2:  # don't care
                continue
            if cond_bit != state_bit:
                return False
        return True

    def forecast(self, price_plus_dividend: float) -> float:
        return self.a * price_plus_dividend + self.b

    def update_fitness(self, specificity_penalty: float = 0.005):
        self.fitness = -self.variance - specificity_penalty * self.specificity


# ---------------------------------------------------------------------------
# Stock (Dividend Process)
# ---------------------------------------------------------------------------

class Stock:
    """A stock paying stochastic dividends following an AR(1) process.

    d_t = d_bar + rho * (d_{t-1} - d_bar) + epsilon
    epsilon ~ N(0, sigma_d^2)
    """

    def __init__(self, d_bar: float = 10.0, rho: float = 0.95,
                 sigma_d: float = 0.0743**0.5, interest_rate: float = 0.10):
        self.d_bar = d_bar
        self.rho = rho
        self.sigma_d = sigma_d
        self.interest_rate = interest_rate
        self.dividend = d_bar
        self.fundamental_value = d_bar / interest_rate  # = 100
        self.price = self.fundamental_value
        self.price_history = [self.price]
        self.dividend_history = [self.dividend]
        self.return_history = []
        self.volume_history = []

    def next_dividend(self) -> float:
        epsilon = random.gauss(0, self.sigma_d)
        self.dividend = self.d_bar + self.rho * (self.dividend - self.d_bar) + epsilon
        self.dividend = max(self.dividend, 0.001)  # ensure positive
        self.dividend_history.append(self.dividend)
        self.fundamental_value = self.dividend / self.interest_rate
        return self.dividend

    def record_price(self, price: float):
        old_price = self.price
        self.price = price
        self.price_history.append(price)
        if old_price > 0:
            ret = (price + self.dividend - old_price * (1 + self.interest_rate)) / old_price
            self.return_history.append(ret)
        else:
            self.return_history.append(0.0)

    def record_volume(self, volume: float):
        self.volume_history.append(volume)

    def moving_average(self, window: int) -> float:
        prices = self.price_history
        if len(prices) < window:
            return np.mean(prices)
        return np.mean(prices[-window:])


# ---------------------------------------------------------------------------
# Market State Encoder
# ---------------------------------------------------------------------------

def encode_market_state(stock: Stock) -> list:
    """Encode the current market state as a 12-bit binary vector.

    Bits 0-5: Fundamental descriptors (price/fundamental_value thresholds)
    Bits 6-9: Technical descriptors (price vs moving averages)
    Bits 10-11: Control bits (always 1 and 0)
    """
    p = stock.price
    fv = stock.fundamental_value
    ratio = p / fv if fv > 0 else 1.0

    state = [
        1 if ratio > 0.25 else 0,
        1 if ratio > 0.50 else 0,
        1 if ratio > 0.75 else 0,
        1 if ratio > 0.875 else 0,
        1 if ratio > 1.00 else 0,
        1 if ratio > 1.125 else 0,
        1 if p > stock.moving_average(5) else 0,
        1 if p > stock.moving_average(10) else 0,
        1 if p > stock.moving_average(100) else 0,
        1 if p > stock.moving_average(500) else 0,
        1,  # control: always 1
        0,  # control: always 0
    ]
    return state


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class Agent:
    """A trading agent maintaining a population of forecasting rules.

    Uses CARA utility: U(W) = -exp(-lambda * W)
    Demand: x = (E[p+d] - p*(1+r)) / (lambda * var)
    """

    def __init__(self, agent_id: int, cash: float, shares: float,
                 num_rules: int = 100, risk_aversion: float = 0.5,
                 interest_rate: float = 0.10, learning: bool = True):
        self.agent_id = agent_id
        self.cash = cash
        self.shares = shares
        self.num_rules = num_rules
        self.risk_aversion = risk_aversion
        self.interest_rate = interest_rate
        self.learning = learning
        self.rules = self._init_rules(num_rules) if learning else self._init_rules(1)
        self.active_rule: Optional[ForecastRule] = None
        self.wealth_history = []

    def _init_rules(self, n: int) -> list:
        rules = []
        for _ in range(n):
            condition = []
            for _ in range(12):
                r = random.random()
                if r < 0.90:
                    condition.append(2)  # don't care
                elif r < 0.95:
                    condition.append(0)
                else:
                    condition.append(1)
            a = random.uniform(0.7, 1.2)
            b = random.uniform(-10.0, 19.0)
            variance = random.uniform(1.0, 8.0)
            rule = ForecastRule(condition=condition, a=a, b=b, variance=variance)
            rule.update_fitness()
            rules.append(rule)
        return rules

    @property
    def wealth(self) -> float:
        return self.cash + self.shares * self._last_price if hasattr(self, '_last_price') else self.cash

    def select_rule(self, market_state: list) -> Optional[ForecastRule]:
        active_rules = [r for r in self.rules if r.matches(market_state)]
        if not active_rules:
            # Fallback: use least specific rule
            active_rules = sorted(self.rules, key=lambda r: r.specificity)[:1]
        # Select best by fitness
        self.active_rule = max(active_rules, key=lambda r: r.fitness)
        return self.active_rule

    def compute_demand(self, price: float, dividend: float) -> float:
        if self.active_rule is None:
            return 0.0
        pd = price + dividend
        expected = self.active_rule.forecast(pd)
        excess_return = expected - price * (1 + self.interest_rate)
        var = max(self.active_rule.variance, 0.5)  # floor prevents extreme positions
        demand = excess_return / (self.risk_aversion * var)
        # Clamp demand per trade
        demand = max(-5.0, min(5.0, demand))
        # Position limits
        max_long = 10.0
        max_short = -5.0
        desired_shares = self.shares + demand
        desired_shares = max(max_short, min(max_long, desired_shares))
        demand = desired_shares - self.shares
        return demand

    def update_rule_accuracy(self, actual_price_plus_div: float, theta: float = 0.1):
        for rule in self.rules:
            if rule == self.active_rule:
                # Only update the rule that was actually used
                predicted = rule.forecast(actual_price_plus_div)
                error = actual_price_plus_div - predicted
                rule.variance = (1 - theta) * rule.variance + theta * (error ** 2)
                rule.update_fitness()
            rule.age += 1

    def evolve_rules(self, mutation_rate: float = 0.03, crossover_prob: float = 0.3):
        if not self.learning or len(self.rules) < 5:
            return
        # Sort by fitness
        self.rules.sort(key=lambda r: r.fitness, reverse=True)
        n = len(self.rules)
        n_keep = int(n * 0.8)
        n_replace = n - n_keep
        survivors = self.rules[:n_keep]
        new_rules = []
        for _ in range(n_replace):
            if random.random() < crossover_prob and len(survivors) >= 2:
                # Crossover
                p1, p2 = random.sample(survivors[:max(n_keep, 2)], 2)
                child = self._crossover(p1, p2)
            else:
                # Clone and mutate
                parent = random.choice(survivors[:max(n_keep // 2, 1)])
                child = self._clone_rule(parent)
            self._mutate(child, mutation_rate)
            child.update_fitness()
            new_rules.append(child)
        self.rules = survivors + new_rules

    def _crossover(self, p1: ForecastRule, p2: ForecastRule) -> ForecastRule:
        # Uniform crossover on condition bits
        condition = []
        for c1, c2 in zip(p1.condition, p2.condition):
            condition.append(c1 if random.random() < 0.5 else c2)
        # Parameter crossover: three equiprobable methods
        method = random.randint(0, 2)
        if method == 0:
            a, b = p1.a, p1.b
        elif method == 1:
            a, b = p2.a, p2.b
        else:
            a, b = (p1.a + p2.a) / 2, (p1.b + p2.b) / 2
        variance = (p1.variance + p2.variance) / 2
        return ForecastRule(condition=condition, a=a, b=b, variance=variance)

    def _clone_rule(self, parent: ForecastRule) -> ForecastRule:
        return ForecastRule(
            condition=list(parent.condition),
            a=parent.a, b=parent.b,
            variance=parent.variance
        )

    def _mutate(self, rule: ForecastRule, mutation_rate: float):
        # Mutate condition bits
        for i in range(len(rule.condition)):
            if random.random() < mutation_rate:
                rule.condition[i] = random.choice([0, 1, 2])
        # Mutate parameters
        if random.random() < mutation_rate:
            rule.a += random.gauss(0, 0.05)
            rule.a = max(0.0, min(2.0, rule.a))
        if random.random() < mutation_rate:
            rule.b += random.gauss(0, 2.0)
            rule.b = max(-30.0, min(30.0, rule.b))

    def record_wealth(self, price: float):
        self._last_price = price
        self.wealth_history.append(self.cash + self.shares * price)


# ---------------------------------------------------------------------------
# Market Clearing
# ---------------------------------------------------------------------------

def clear_market(agents: list, stock: Stock) -> tuple:
    """Find clearing price using bisection on aggregate excess demand.

    Returns (clearing_price, volume).
    """
    total_shares = sum(a.shares for a in agents)
    dividend = stock.dividend

    def excess_demand(price):
        total = 0.0
        for agent in agents:
            total += agent.compute_demand(price, dividend)
        return total

    # Bisection to find clearing price
    p_low = max(stock.price * 0.5, 0.01)
    p_high = stock.price * 1.5 + 10.0

    # Expand bounds if needed
    for _ in range(10):
        ed_low = excess_demand(p_low)
        ed_high = excess_demand(p_high)
        if ed_low > 0 and ed_high < 0:
            break
        if ed_low <= 0:
            p_low = max(p_low * 0.5, 0.001)
        if ed_high >= 0:
            p_high = p_high * 2.0
    else:
        # If we can't bracket, use midpoint
        return stock.price, 0.0

    # Bisection
    for _ in range(100):
        p_mid = (p_low + p_high) / 2.0
        ed = excess_demand(p_mid)
        if abs(ed) < 0.001:
            break
        if ed > 0:
            p_low = p_mid
        else:
            p_high = p_mid

    clearing_price = (p_low + p_high) / 2.0
    clearing_price = max(clearing_price, 0.01)

    # Pay dividends on pre-trade holdings, then execute trades
    volume = 0.0
    for agent in agents:
        # Dividend income on current shares (before trading)
        agent.cash += agent.shares * dividend

    for agent in agents:
        demand = agent.compute_demand(clearing_price, dividend)
        cost = demand * clearing_price
        agent.shares += demand
        agent.cash -= cost
        volume += abs(demand)

    return clearing_price, volume / 2.0  # volume = half of total absolute demand


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    """Orchestrates the SFI Artificial Stock Market simulation."""

    def __init__(self, num_agents: int = 100, num_ticks: int = 2000,
                 learning: bool = True, num_rules: int = 100,
                 mutation_rate: float = 0.03, crossover_prob: float = 0.3,
                 ga_interval: float = 250.0, risk_aversion: float = 0.5,
                 interest_rate: float = 0.10, d_bar: float = 10.0,
                 rho: float = 0.95, sigma_d: float = 0.0743**0.5,
                 seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.num_agents = num_agents
        self.num_ticks = num_ticks
        self.learning = learning
        self.mutation_rate = mutation_rate
        self.crossover_prob = crossover_prob
        self.ga_interval = ga_interval

        # Create stock
        self.stock = Stock(d_bar=d_bar, rho=rho, sigma_d=sigma_d,
                           interest_rate=interest_rate)

        # Create agents with equal initial endowments
        initial_shares = 1.0  # each agent starts with 1 share
        initial_cash = self.stock.fundamental_value * 2  # moderate cash buffer
        self.agents = []
        for i in range(num_agents):
            agent = Agent(
                agent_id=i, cash=initial_cash, shares=initial_shares,
                num_rules=num_rules, risk_aversion=risk_aversion,
                interest_rate=interest_rate, learning=learning
            )
            self.agents.append(agent)

        # Metrics
        self.tick = 0
        self.gini_history = []

    def step(self):
        """Execute one time step of the simulation."""
        # 1. Generate new dividend
        self.stock.next_dividend()

        # 2. Encode market state
        market_state = encode_market_state(self.stock)

        # 3. Each agent selects best matching rule
        for agent in self.agents:
            agent.select_rule(market_state)

        # 4. Clear market
        clearing_price, volume = clear_market(self.agents, self.stock)

        # 5. Record price and volume
        self.stock.record_price(clearing_price)
        self.stock.record_volume(volume)

        # 6. Update rule accuracies
        actual_pd = clearing_price + self.stock.dividend
        for agent in self.agents:
            agent.update_rule_accuracy(actual_pd)
            agent.record_wealth(clearing_price)

        # 7. Evolve rules (stochastic GA invocation per agent)
        if self.learning:
            ga_prob = 1.0 / self.ga_interval
            for agent in self.agents:
                if random.random() < ga_prob:
                    agent.evolve_rules(
                        mutation_rate=self.mutation_rate,
                        crossover_prob=self.crossover_prob
                    )

        # 8. Track Gini coefficient
        self.gini_history.append(self.compute_gini())
        self.tick += 1

    def run(self, progress_callback=None):
        """Run the full simulation."""
        for t in range(self.num_ticks):
            self.step()
            if progress_callback and t % 100 == 0:
                progress_callback(t, self.num_ticks)

    def compute_gini(self) -> float:
        wealths = [a.wealth for a in self.agents]
        n = len(wealths)
        if n == 0:
            return 0.0
        # Shift to handle negatives (relative Gini)
        min_w = min(wealths)
        if min_w < 0:
            wealths = [w - min_w + 1.0 for w in wealths]
        wealths.sort()
        total = sum(wealths)
        if total == 0:
            return 0.0
        weighted_sum = 0.0
        for i, w in enumerate(wealths):
            weighted_sum += (2 * (i + 1) - n - 1) * w
        gini = weighted_sum / (n * total)
        return max(0.0, min(1.0, gini))

    def get_statistics(self) -> dict:
        """Compute summary statistics for the simulation run."""
        prices = self.stock.price_history
        returns = self.stock.return_history
        volumes = self.stock.volume_history
        dividends = self.stock.dividend_history

        # Returns statistics
        if len(returns) > 1:
            returns_arr = np.array(returns)
            mean_return = np.mean(returns_arr)
            std_return = np.std(returns_arr)
            # Excess kurtosis
            if std_return > 0:
                kurtosis = float(np.mean(((returns_arr - mean_return) / std_return) ** 4) - 3.0)
            else:
                kurtosis = 0.0
            skewness = float(np.mean(((returns_arr - mean_return) / max(std_return, 1e-10)) ** 3))

            # Autocorrelation of returns (lag-1)
            if len(returns_arr) > 1:
                ac1 = float(np.corrcoef(returns_arr[:-1], returns_arr[1:])[0, 1])
            else:
                ac1 = 0.0

            # Volatility clustering: autocorrelation of |returns|
            abs_returns = np.abs(returns_arr)
            if len(abs_returns) > 1:
                vol_ac1 = float(np.corrcoef(abs_returns[:-1], abs_returns[1:])[0, 1])
            else:
                vol_ac1 = 0.0

            # Simple power-law test: tail index estimation (Hill estimator)
            sorted_abs = np.sort(abs_returns)[::-1]
            k = max(int(len(sorted_abs) * 0.05), 5)  # top 5% of observations
            if k > 1 and sorted_abs[k - 1] > 0:
                tail_index = 1.0 / np.mean(np.log(sorted_abs[:k] / sorted_abs[k - 1]))
            else:
                tail_index = float('nan')
        else:
            mean_return = std_return = kurtosis = skewness = 0.0
            ac1 = vol_ac1 = 0.0
            tail_index = float('nan')

        # Wealth distribution
        final_wealths = [a.wealth for a in self.agents]

        stats = {
            'num_ticks': self.tick,
            'num_agents': self.num_agents,
            'mode': 'learning' if self.learning else 'rational',
            'final_price': prices[-1] if prices else 0.0,
            'mean_price': float(np.mean(prices)),
            'std_price': float(np.std(prices)),
            'mean_return': mean_return,
            'std_return': std_return,
            'annualized_volatility': std_return * (252 ** 0.5),
            'kurtosis': kurtosis,
            'skewness': skewness,
            'return_autocorrelation_lag1': ac1,
            'volatility_clustering_ac1': vol_ac1,
            'tail_index': tail_index,
            'mean_volume': float(np.mean(volumes)) if volumes else 0.0,
            'mean_dividend': float(np.mean(dividends)),
            'final_fundamental_value': self.stock.fundamental_value,
            'gini_coefficient': self.gini_history[-1] if self.gini_history else 0.0,
            'mean_wealth': float(np.mean(final_wealths)),
            'std_wealth': float(np.std(final_wealths)),
            'min_wealth': float(np.min(final_wealths)),
            'max_wealth': float(np.max(final_wealths)),
        }
        return stats

    def get_timeseries_data(self) -> dict:
        """Return time series data suitable for CSV export."""
        n = len(self.stock.price_history)
        ticks = list(range(n))
        returns = [0.0] + self.stock.return_history  # pad to match length
        volumes = [0.0] + self.stock.volume_history if len(self.stock.volume_history) < n else self.stock.volume_history
        dividends = self.stock.dividend_history
        gini = [0.0] + self.gini_history if len(self.gini_history) < n else self.gini_history

        # Ensure all arrays same length
        min_len = min(len(ticks), len(self.stock.price_history),
                      len(returns), len(dividends))

        return {
            'tick': ticks[:min_len],
            'price': self.stock.price_history[:min_len],
            'return': returns[:min_len],
            'volume': (volumes[:min_len] if len(volumes) >= min_len
                       else volumes + [0.0] * (min_len - len(volumes))),
            'dividend': dividends[:min_len],
            'fundamental_value': [d / self.stock.interest_rate
                                  for d in dividends[:min_len]],
            'gini': (gini[:min_len] if len(gini) >= min_len
                     else gini + [0.0] * (min_len - len(gini))),
        }


if __name__ == '__main__':
    print("Running SFI Artificial Stock Market simulation...")
    sim = Simulation(num_agents=25, num_ticks=1000, learning=True, seed=42)
    sim.run(progress_callback=lambda t, n: print(f"  tick {t}/{n}"))
    stats = sim.get_statistics()
    print("\nResults:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
