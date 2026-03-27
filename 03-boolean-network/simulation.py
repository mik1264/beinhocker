"""
Boolean Network Organization / Complexity Catastrophe Simulation

Models Kauffman's random Boolean networks (RBNs) to demonstrate:
- Phase transitions between ordered and chaotic regimes
- The complexity catastrophe in NK fitness landscapes
- How network topology (random, lattice, hierarchy, small-world) affects dynamics
- Edge of chaos as the regime where adaptation is maximized

Based on:
- Kauffman, S.A. (1993). The Origins of Order.
- Derrida, B. & Weisbuch, G. (1986). Random Networks of Automata.
- Beinhocker, E. (2006). The Origin of Wealth, Chapter 8.
"""

import random
import math
import csv
import json
from collections import Counter
from typing import Optional


class Node:
    """A single node in a Boolean network."""

    __slots__ = ("index", "state", "inputs", "truth_table", "bias")

    def __init__(self, index: int, K: int, bias: float = 0.5):
        self.index = index
        self.state = random.randint(0, 1)
        self.inputs: list[int] = []  # indices of input nodes
        self.bias = bias
        # Truth table: 2^K Boolean outputs, biased by p
        self.truth_table = [1 if random.random() < bias else 0 for _ in range(2**K)]

    def compute_next(self, input_states: list[int]) -> int:
        """Compute next state from input states using truth table lookup."""
        idx = 0
        for k, s in enumerate(input_states):
            idx += s << k
        return self.truth_table[idx]


class Network:
    """A Boolean network with N nodes, connectivity K, and configurable topology."""

    def __init__(
        self,
        N: int = 100,
        K: int = 2,
        bias: float = 0.5,
        topology: str = "random",
        hierarchy_depth: int = 3,
        branching_factor: int = 3,
        rewire_prob: float = 0.1,
        seed: Optional[int] = None,
    ):
        if seed is not None:
            random.seed(seed)

        self.N = N
        self.K = K
        self.bias = bias
        self.topology = topology
        self.hierarchy_depth = hierarchy_depth
        self.branching_factor = branching_factor
        self.rewire_prob = rewire_prob
        self.tick = 0

        # Create nodes
        self.nodes = [Node(i, K, bias) for i in range(N)]

        # Wire topology
        self._wire_topology()

    def _wire_topology(self):
        """Wire input connections based on selected topology."""
        if self.topology == "random":
            self._wire_random()
        elif self.topology == "lattice":
            self._wire_lattice()
        elif self.topology == "hierarchy":
            self._wire_hierarchy()
        elif self.topology == "small-world":
            self._wire_small_world()
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

    def _wire_random(self):
        """Each node gets K random inputs (standard Kauffman model)."""
        for node in self.nodes:
            candidates = [i for i in range(self.N) if i != node.index]
            node.inputs = random.sample(candidates, min(self.K, len(candidates)))

    def _wire_lattice(self):
        """Ring lattice: each node gets K nearest neighbors as inputs."""
        for node in self.nodes:
            inputs = []
            for j in range(1, self.K // 2 + 1):
                inputs.append((node.index + j) % self.N)
                inputs.append((node.index - j) % self.N)
            # If K is odd, add one more
            if self.K % 2 == 1:
                inputs.append((node.index + self.K // 2 + 1) % self.N)
            node.inputs = inputs[: self.K]

    def _wire_hierarchy(self):
        """Tree-structured hierarchy with dense intra-module and sparse inter-module connections."""
        depth = self.hierarchy_depth
        bf = self.branching_factor
        num_leaves = bf**depth
        # Assign nodes to leaf modules
        module_size = max(1, self.N // num_leaves)

        def get_module(node_idx):
            return min(node_idx // module_size, num_leaves - 1)

        # Group nodes by module
        modules: dict[int, list[int]] = {}
        for i in range(self.N):
            m = get_module(i)
            modules.setdefault(m, []).append(i)

        for node in self.nodes:
            my_module = get_module(node.index)
            siblings = [x for x in modules.get(my_module, []) if x != node.index]
            other_nodes = [x for x in range(self.N) if get_module(x) != my_module]

            inputs = []
            # Mostly intra-module connections
            intra_k = max(1, int(self.K * 0.7))
            inter_k = self.K - intra_k

            if siblings:
                inputs.extend(random.sample(siblings, min(intra_k, len(siblings))))
            if other_nodes and inter_k > 0:
                inputs.extend(random.sample(other_nodes, min(inter_k, len(other_nodes))))

            # Fill remaining slots if needed
            while len(inputs) < self.K:
                candidates = [i for i in range(self.N) if i != node.index and i not in inputs]
                if not candidates:
                    break
                inputs.append(random.choice(candidates))

            node.inputs = inputs[: self.K]

    def _wire_small_world(self):
        """Watts-Strogatz small-world: ring lattice + random rewiring."""
        # Start with lattice
        self._wire_lattice()
        # Rewire with probability beta
        for node in self.nodes:
            new_inputs = []
            for inp in node.inputs:
                if random.random() < self.rewire_prob:
                    candidates = [
                        i
                        for i in range(self.N)
                        if i != node.index and i not in new_inputs
                    ]
                    if candidates:
                        new_inputs.append(random.choice(candidates))
                    else:
                        new_inputs.append(inp)
                else:
                    new_inputs.append(inp)
            node.inputs = new_inputs

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def get_state(self) -> tuple[int, ...]:
        """Return current network state as a tuple."""
        return tuple(n.state for n in self.nodes)

    def set_state(self, state: tuple[int, ...] | list[int]):
        """Set network state from a sequence."""
        for i, s in enumerate(state):
            self.nodes[i].state = s

    def randomize_state(self):
        """Set all nodes to random states."""
        for node in self.nodes:
            node.state = random.randint(0, 1)

    # ------------------------------------------------------------------
    # Dynamics
    # ------------------------------------------------------------------

    def step(self) -> tuple[int, ...]:
        """Synchronous update: compute all next states, then apply."""
        next_states = []
        for node in self.nodes:
            input_states = [self.nodes[i].state for i in node.inputs]
            next_states.append(node.compute_next(input_states))
        for i, node in enumerate(self.nodes):
            node.state = next_states[i]
        self.tick += 1
        return self.get_state()

    def run(self, steps: int) -> list[tuple[int, ...]]:
        """Run for multiple steps, returning state history."""
        history = [self.get_state()]
        for _ in range(steps):
            self.step()
            history.append(self.get_state())
        return history

    # ------------------------------------------------------------------
    # Perturbation analysis
    # ------------------------------------------------------------------

    def perturb(self, node_index: int):
        """Flip a single node's state."""
        self.nodes[node_index].state = 1 - self.nodes[node_index].state

    def measure_cascade(
        self, node_index: int, steps: int = 50
    ) -> dict:
        """Flip one node and measure how the perturbation propagates.

        Returns cascade size, Hamming distance time series, and affected nodes.
        """
        # Save original state
        original_state = self.get_state()

        # Run unperturbed trajectory
        unperturbed = [original_state]
        self.set_state(original_state)
        for _ in range(steps):
            self.step()
            unperturbed.append(self.get_state())

        # Run perturbed trajectory
        self.set_state(original_state)
        self.perturb(node_index)
        perturbed = [self.get_state()]
        for _ in range(steps):
            self.step()
            perturbed.append(self.get_state())

        # Compute Hamming distances
        hamming_series = []
        affected_nodes: set[int] = set()
        for t in range(len(unperturbed)):
            h = _hamming(unperturbed[t], perturbed[t])
            hamming_series.append(h)
            for i in range(self.N):
                if unperturbed[t][i] != perturbed[t][i]:
                    affected_nodes.add(i)

        # Restore original state
        self.set_state(original_state)

        return {
            "source_node": node_index,
            "cascade_size": len(affected_nodes),
            "max_hamming": max(hamming_series),
            "final_hamming": hamming_series[-1],
            "hamming_series": hamming_series,
            "affected_nodes": sorted(affected_nodes),
        }

    def cascade_analysis(
        self, num_perturbations: int = 50, steps: int = 50
    ) -> dict:
        """Run multiple single-bit perturbations and aggregate cascade statistics."""
        cascade_sizes = []
        max_hammings = []
        final_hammings = []
        all_hamming_series = []

        for _ in range(num_perturbations):
            self.randomize_state()
            # Let network settle a bit
            for _ in range(20):
                self.step()
            node_idx = random.randint(0, self.N - 1)
            result = self.measure_cascade(node_idx, steps)
            cascade_sizes.append(result["cascade_size"])
            max_hammings.append(result["max_hamming"])
            final_hammings.append(result["final_hamming"])
            all_hamming_series.append(result["hamming_series"])

        # Cascade size distribution
        size_counts = Counter(cascade_sizes)

        return {
            "cascade_sizes": cascade_sizes,
            "mean_cascade_size": sum(cascade_sizes) / len(cascade_sizes),
            "max_cascade_size": max(cascade_sizes),
            "mean_max_hamming": sum(max_hammings) / len(max_hammings),
            "mean_final_hamming": sum(final_hammings) / len(final_hammings),
            "size_distribution": dict(sorted(size_counts.items())),
            "hamming_series": all_hamming_series,
        }

    # ------------------------------------------------------------------
    # Attractor detection
    # ------------------------------------------------------------------

    def find_attractor(self, max_steps: int = 10000) -> dict:
        """Find attractor from current state using state history tracking."""
        seen: dict[tuple[int, ...], int] = {}
        state = self.get_state()
        for t in range(max_steps):
            state_key = state
            if state_key in seen:
                cycle_length = t - seen[state_key]
                transient_length = seen[state_key]
                return {
                    "cycle_length": cycle_length,
                    "transient_length": transient_length,
                    "found": True,
                }
            seen[state_key] = t
            self.step()
            state = self.get_state()
        return {"cycle_length": None, "transient_length": None, "found": False}

    def attractor_search(
        self, num_trials: int = 50, max_steps: int = 5000
    ) -> dict:
        """Search for attractors from multiple random initial states."""
        cycle_lengths = []
        transient_lengths = []
        unique_attractors: set[tuple[int, ...]] = set()

        for _ in range(num_trials):
            self.randomize_state()
            result = self.find_attractor(max_steps)
            if result["found"]:
                cycle_lengths.append(result["cycle_length"])
                transient_lengths.append(result["transient_length"])
                # Record the attractor state for uniqueness counting
                unique_attractors.add(self.get_state())

        if not cycle_lengths:
            return {
                "num_trials": num_trials,
                "attractors_found": 0,
                "unique_attractors": 0,
                "mean_cycle_length": None,
                "median_cycle_length": None,
                "max_cycle_length": None,
                "mean_transient_length": None,
                "cycle_lengths": [],
            }

        cycle_lengths_sorted = sorted(cycle_lengths)
        mid = len(cycle_lengths_sorted) // 2
        median = (
            cycle_lengths_sorted[mid]
            if len(cycle_lengths_sorted) % 2 == 1
            else (cycle_lengths_sorted[mid - 1] + cycle_lengths_sorted[mid]) / 2
        )

        return {
            "num_trials": num_trials,
            "attractors_found": len(cycle_lengths),
            "unique_attractors": len(unique_attractors),
            "mean_cycle_length": sum(cycle_lengths) / len(cycle_lengths),
            "median_cycle_length": median,
            "max_cycle_length": max(cycle_lengths),
            "mean_transient_length": sum(transient_lengths) / len(transient_lengths),
            "cycle_lengths": cycle_lengths,
        }

    # ------------------------------------------------------------------
    # Derrida parameter and sensitivity
    # ------------------------------------------------------------------

    def derrida_parameter(self, num_pairs: int = 200) -> float:
        """Compute the Derrida coefficient (average sensitivity).

        Measures how a single-bit perturbation spreads after one time step.
        lambda < 1 => ordered, lambda = 1 => critical, lambda > 1 => chaotic.
        """
        total_spread = 0
        for _ in range(num_pairs):
            # Random initial state
            s1 = tuple(random.randint(0, 1) for _ in range(self.N))
            # Flip one random bit
            flip_idx = random.randint(0, self.N - 1)
            s2 = list(s1)
            s2[flip_idx] = 1 - s2[flip_idx]
            s2 = tuple(s2)

            # Evolve both one step
            self.set_state(s1)
            self.step()
            s1_next = self.get_state()

            self.set_state(s2)
            self.step()
            s2_next = self.get_state()

            total_spread += _hamming(s1_next, s2_next)

        return total_spread / num_pairs

    def derrida_curve(
        self, num_pairs: int = 200, num_distances: int = 20
    ) -> list[tuple[float, float]]:
        """Compute the full Derrida curve: d_out vs d_in for various initial distances."""
        curve = []
        for d_frac_idx in range(1, num_distances + 1):
            d_in = max(1, int(self.N * d_frac_idx / num_distances))
            d_out_total = 0
            for _ in range(num_pairs):
                s1 = tuple(random.randint(0, 1) for _ in range(self.N))
                # Create s2 by flipping d_in random bits
                flip_indices = random.sample(range(self.N), min(d_in, self.N))
                s2 = list(s1)
                for idx in flip_indices:
                    s2[idx] = 1 - s2[idx]
                s2 = tuple(s2)

                self.set_state(s1)
                self.step()
                s1_next = self.get_state()

                self.set_state(s2)
                self.step()
                s2_next = self.get_state()

                d_out_total += _hamming(s1_next, s2_next) / self.N

            curve.append((d_in / self.N, d_out_total / num_pairs))
        return curve

    # ------------------------------------------------------------------
    # Phase diagram
    # ------------------------------------------------------------------

    def classify_regime(self, num_pairs: int = 100) -> str:
        """Classify the current network as ordered, critical, or chaotic."""
        lam = self.derrida_parameter(num_pairs)
        normalized = lam  # Already in units of "number of bits changed"
        # Derrida coefficient: compare spread to initial perturbation (1 bit)
        if normalized < 0.8:
            return "ordered"
        elif normalized > 1.2:
            return "chaotic"
        else:
            return "critical"


def compute_phase_diagram(
    N: int = 50,
    K_values: Optional[list[int]] = None,
    bias_values: Optional[list[float]] = None,
    topology: str = "random",
    num_pairs: int = 100,
    num_repeats: int = 3,
) -> list[dict]:
    """Sweep K and bias to compute phase diagram.

    Returns list of dicts with K, bias, derrida_parameter, and classification.
    """
    if K_values is None:
        K_values = list(range(1, 8))
    if bias_values is None:
        bias_values = [round(0.1 + 0.05 * i, 2) for i in range(17)]  # 0.1 to 0.9

    results = []
    total = len(K_values) * len(bias_values)
    done = 0

    for K in K_values:
        for bias in bias_values:
            derrida_sum = 0
            for _ in range(num_repeats):
                net = Network(N=N, K=K, bias=bias, topology=topology)
                net.randomize_state()
                d = net.derrida_parameter(num_pairs)
                derrida_sum += d
            avg_derrida = derrida_sum / num_repeats

            if avg_derrida < 0.8:
                classification = "ordered"
            elif avg_derrida > 1.2:
                classification = "chaotic"
            else:
                classification = "critical"

            # Theoretical prediction: lambda = 2K * p * (1-p)
            theoretical = 2 * K * bias * (1 - bias)

            results.append(
                {
                    "K": K,
                    "bias": bias,
                    "derrida_parameter": round(avg_derrida, 4),
                    "theoretical_lambda": round(theoretical, 4),
                    "classification": classification,
                }
            )
            done += 1
            if done % 10 == 0:
                print(f"  Phase diagram: {done}/{total} complete")

    return results


# ------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------


def _hamming(s1: tuple[int, ...], s2: tuple[int, ...]) -> int:
    """Compute Hamming distance between two states."""
    return sum(a != b for a, b in zip(s1, s2))


def save_results_csv(results: list[dict], filepath: str):
    """Save a list of dicts to CSV."""
    if not results:
        return
    keys = results[0].keys()
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


def save_results_json(data: dict, filepath: str):
    """Save results dict to JSON, handling non-serializable types."""

    def default(obj):
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, tuple):
            return list(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=default)


# ------------------------------------------------------------------
# Convenience runners
# ------------------------------------------------------------------


def run_full_analysis(
    N: int = 50,
    K: int = 2,
    bias: float = 0.5,
    topology: str = "random",
    seed: Optional[int] = None,
) -> dict:
    """Run a complete analysis on a single network configuration."""
    net = Network(N=N, K=K, bias=bias, topology=topology, seed=seed)

    print(f"Network: N={N}, K={K}, bias={bias}, topology={topology}")
    print(f"Theoretical lambda = 2*K*p*(1-p) = {2*K*bias*(1-bias):.3f}")

    # Derrida parameter
    print("\nComputing Derrida parameter...")
    derrida = net.derrida_parameter(200)
    regime = net.classify_regime(200)
    print(f"  Derrida parameter: {derrida:.3f}")
    print(f"  Regime: {regime}")

    # Attractor search
    print("\nSearching for attractors...")
    net.randomize_state()
    attractor_stats = net.attractor_search(num_trials=30, max_steps=5000)
    print(f"  Attractors found: {attractor_stats['attractors_found']}/{attractor_stats['num_trials']}")
    if attractor_stats["mean_cycle_length"] is not None:
        print(f"  Mean cycle length: {attractor_stats['mean_cycle_length']:.1f}")
        print(f"  Max cycle length: {attractor_stats['max_cycle_length']}")

    # Cascade analysis
    print("\nAnalyzing cascades...")
    cascade_stats = net.cascade_analysis(num_perturbations=30, steps=30)
    print(f"  Mean cascade size: {cascade_stats['mean_cascade_size']:.1f}")
    print(f"  Max cascade size: {cascade_stats['max_cascade_size']}")
    print(f"  Mean final Hamming: {cascade_stats['mean_final_hamming']:.1f}")

    # Derrida curve
    print("\nComputing Derrida curve...")
    curve = net.derrida_curve(num_pairs=100, num_distances=10)
    print("  d_in -> d_out:")
    for d_in, d_out in curve:
        print(f"    {d_in:.2f} -> {d_out:.2f}")

    return {
        "parameters": {
            "N": N,
            "K": K,
            "bias": bias,
            "topology": topology,
        },
        "derrida_parameter": derrida,
        "theoretical_lambda": 2 * K * bias * (1 - bias),
        "regime": regime,
        "attractor_stats": attractor_stats,
        "cascade_stats": cascade_stats,
        "derrida_curve": curve,
    }


if __name__ == "__main__":
    # Quick demo
    print("=" * 60)
    print("Boolean Network Simulation - Quick Demo")
    print("=" * 60)

    # Ordered regime (K=1)
    print("\n--- Ordered Regime (K=1) ---")
    run_full_analysis(N=50, K=1, bias=0.5, topology="random", seed=42)

    # Critical regime (K=2)
    print("\n--- Critical Regime (K=2) ---")
    run_full_analysis(N=50, K=2, bias=0.5, topology="random", seed=42)

    # Chaotic regime (K=4)
    print("\n--- Chaotic Regime (K=4) ---")
    run_full_analysis(N=50, K=4, bias=0.5, topology="random", seed=42)
