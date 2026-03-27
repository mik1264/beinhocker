"""
Punctuated Equilibrium Ecosystem Simulation

Based on the Jain-Krishna model of evolving autocatalytic networks,
combined with elements from the Bak-Sneppen model of self-organized criticality.

Species interact through a directed weighted graph where edge weights represent
catalytic (positive) or inhibitory (negative) interactions. The least-fit species
is replaced each tick, potentially triggering cascade extinctions when keystone
species are lost.

References:
  - Jain & Krishna, "Large Extinctions in an Evolutionary Model" (PNAS, 2002)
  - Bak & Sneppen, "Punctuated Equilibrium and Criticality" (PRL, 1993)
  - Beinhocker, "The Origin of Wealth" (2006), Chapter on punctuated equilibrium
"""

import random
import math
import csv
import json
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Phase(Enum):
    RANDOM = "random"
    GROWTH = "growth"
    ORGANIZED = "organized"
    PUNCTUATION = "punctuation"


@dataclass
class Species:
    id: int
    fitness: float = 0.0
    age: int = 0
    is_keystone: bool = False

    def classify(self, max_age: int) -> str:
        if self.age < 5:
            return "new"
        elif self.is_keystone:
            return "keystone"
        elif self.age > max_age * 0.5:
            return "established"
        else:
            return "growing"


@dataclass
class CascadeEvent:
    tick: int
    trigger_species: int
    size: int  # number of species lost
    phase_before: Phase
    phase_after: Phase


@dataclass
class TickRecord:
    tick: int
    species_count: int
    mean_fitness: float
    max_fitness: float
    min_fitness: float
    density: float
    clustering: float
    largest_component: int
    num_keystones: int
    phase: str
    cascade_size: int
    diversity: float


class Ecosystem:
    """
    Directed weighted graph of N interacting species.

    Positive edge weights represent mutualism/catalysis/dependency.
    Negative edge weights represent competition/predation/inhibition.

    Fitness of each species is determined by incoming edge weights from
    connected species, weighted by those species' own fitness.
    """

    def __init__(
        self,
        n_species: int = 100,
        connection_prob: float = 0.05,
        weight_range: tuple = (-1.0, 1.0),
        seed: Optional[int] = None,
    ):
        self.n_species = n_species
        self.connection_prob = connection_prob
        self.weight_range = weight_range
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)

        # Adjacency matrix: weights[i][j] = weight of edge from j -> i
        # (j catalyzes/affects i)
        self.weights = np.zeros((n_species, n_species))
        self.species = []
        self.tick = 0
        self.history: list[TickRecord] = []
        self.cascades: list[CascadeEvent] = []
        self.phase = Phase.RANDOM
        self.phase_history: list[tuple[int, Phase]] = []

        # Running stats for phase detection
        self._recent_fitness: list[float] = []
        self._recent_diversity: list[float] = []

        self._initialize()

    def _initialize(self):
        """Create initial random species and connections."""
        self.species = [Species(id=i) for i in range(self.n_species)]

        # Random directed weighted graph
        for i in range(self.n_species):
            for j in range(self.n_species):
                if i == j:
                    continue  # no self-loops
                if self.rng.random() < self.connection_prob:
                    w = self.rng.uniform(*self.weight_range)
                    self.weights[i][j] = w

        # Initial fitness computation
        self._compute_all_fitness()

    def _compute_all_fitness(self):
        """Compute fitness for all species based on incoming connections."""
        for i in range(self.n_species):
            self.species[i].fitness = self._compute_fitness(i)

    def _compute_fitness(self, species_idx: int) -> float:
        """
        Fitness based on incoming edge weights, weighted by source species fitness.
        Positive edges = mutualism/catalysis (help).
        Negative edges = competition/predation (harm).
        Species with many strong positive incoming links from fit species thrive.
        Normalized to [0, 1] via sigmoid with a scaling factor to spread the
        distribution and make cascades meaningful.
        """
        incoming = self.weights[species_idx]
        raw = 0.0
        n_positive = 0
        for j in range(self.n_species):
            if incoming[j] != 0 and j != species_idx:
                source_fitness = self.species[j].fitness if self.species[j].fitness > 0 else 0.01
                raw += incoming[j] * source_fitness
                if incoming[j] > 0:
                    n_positive += 1

        # Scale factor: amplify enough that network structure matters
        # but not so much that fitness is always near 0 or 1
        scale = 2.0
        if n_positive == 0:
            raw -= 0.5  # mild penalty for having no supporters

        return 1.0 / (1.0 + math.exp(-raw * scale))

    def _identify_keystones(self):
        """
        Identify keystone species: those whose removal would cause
        the largest cascade of fitness drops.

        A species is keystone if many others depend heavily on it
        (high outgoing positive weight to high-fitness species).
        """
        keystoneness = np.zeros(self.n_species)
        for i in range(self.n_species):
            # Sum of outgoing positive weights to other species
            outgoing_positive = 0.0
            dependent_count = 0
            for j in range(self.n_species):
                if self.weights[j][i] > 0:
                    outgoing_positive += self.weights[j][i] * self.species[j].fitness
                    dependent_count += 1
            # Keystoneness = outgoing support * own fitness * number of dependents
            keystoneness[i] = outgoing_positive * self.species[i].fitness * math.sqrt(max(dependent_count, 1))

        # Top 10% are keystones
        threshold = np.percentile(keystoneness, 90)
        for i in range(self.n_species):
            self.species[i].is_keystone = keystoneness[i] >= threshold and threshold > 0

    def _detect_phase(self) -> Phase:
        """
        Detect current ecosystem phase:
        - RANDOM: low mean fitness, high variance
        - GROWTH: rising mean fitness
        - ORGANIZED: high mean fitness, low variance, stable
        - PUNCTUATION: sharp fitness drop (cascade happening)
        """
        fitnesses = [s.fitness for s in self.species]
        mean_f = np.mean(fitnesses)
        std_f = np.std(fitnesses)

        self._recent_fitness.append(mean_f)
        if len(self._recent_fitness) > 50:
            self._recent_fitness = self._recent_fitness[-50:]

        if len(self._recent_fitness) < 5:
            return Phase.RANDOM

        recent_mean = np.mean(self._recent_fitness[-10:])
        older_mean = np.mean(self._recent_fitness[-20:-10]) if len(self._recent_fitness) >= 20 else recent_mean

        # Punctuation: sharp drop
        if len(self._recent_fitness) >= 3:
            if self._recent_fitness[-1] < self._recent_fitness[-2] * 0.85:
                return Phase.PUNCTUATION

        # Organized: high fitness, low variance
        if mean_f > 0.6 and std_f < 0.15:
            return Phase.ORGANIZED

        # Growth: rising trend
        if recent_mean > older_mean * 1.02:
            return Phase.GROWTH

        return Phase.RANDOM

    def _compute_density(self) -> float:
        """Fraction of possible edges that exist."""
        n = self.n_species
        max_edges = n * (n - 1)
        actual_edges = np.count_nonzero(self.weights)
        return actual_edges / max_edges if max_edges > 0 else 0

    def _compute_clustering(self) -> float:
        """
        Average local clustering coefficient (treating as undirected).
        """
        # Convert to binary adjacency (undirected)
        adj = ((self.weights != 0) | (self.weights.T != 0)).astype(float)
        np.fill_diagonal(adj, 0)

        clustering_sum = 0.0
        count = 0
        for i in range(self.n_species):
            neighbors = np.where(adj[i] > 0)[0]
            k = len(neighbors)
            if k < 2:
                continue
            # Count edges between neighbors
            subgraph = adj[np.ix_(neighbors, neighbors)]
            triangles = np.sum(subgraph)
            possible = k * (k - 1)
            clustering_sum += triangles / possible
            count += 1

        return clustering_sum / count if count > 0 else 0

    def _largest_component_size(self) -> int:
        """Size of largest weakly connected component."""
        adj = (self.weights != 0) | (self.weights.T != 0)
        visited = set()
        largest = 0

        for start in range(self.n_species):
            if start in visited:
                continue
            # BFS
            component = set()
            queue = [start]
            while queue:
                node = queue.pop()
                if node in component:
                    continue
                component.add(node)
                visited.add(node)
                for neighbor in range(self.n_species):
                    if adj[node][neighbor] and neighbor not in component:
                        queue.append(neighbor)
            largest = max(largest, len(component))

        return largest

    def _compute_diversity(self) -> float:
        """Shannon diversity based on fitness distribution (binned)."""
        fitnesses = [s.fitness for s in self.species]
        # Bin into 10 categories
        bins = [0] * 10
        for f in fitnesses:
            idx = min(int(f * 10), 9)
            bins[idx] += 1

        total = sum(bins)
        if total == 0:
            return 0
        entropy = 0.0
        for count in bins:
            if count > 0:
                p = count / total
                entropy -= p * math.log(p)
        # Normalize by max entropy
        max_entropy = math.log(10)
        return entropy / max_entropy if max_entropy > 0 else 0

    def step(self) -> int:
        """
        Execute one tick of evolution.
        Returns the cascade size (0 if no cascade).
        """
        self.tick += 1

        # Age all species
        for s in self.species:
            s.age += 1

        # Identify keystones before replacement
        self._identify_keystones()

        # Find least-fit species
        min_fitness = float('inf')
        min_idx = 0
        for i, s in enumerate(self.species):
            if s.fitness < min_fitness:
                min_fitness = s.fitness
                min_idx = i

        was_keystone = self.species[min_idx].is_keystone

        # Save pre-removal fitness for cascade detection
        pre_fitness = {i: self.species[i].fitness for i in range(self.n_species)}

        # Replace least-fit species with new random species
        self._replace_species(min_idx)

        # Always check for cascade (fitness drops after network perturbation)
        cascade_size = self._propagate_cascade(pre_fitness, excluded={min_idx})

        # Detect phase
        old_phase = self.phase
        self.phase = self._detect_phase()
        if self.phase != old_phase:
            self.phase_history.append((self.tick, self.phase))

        # Record cascade
        if cascade_size > 0:
            self.cascades.append(CascadeEvent(
                tick=self.tick,
                trigger_species=min_idx,
                size=cascade_size,
                phase_before=old_phase,
                phase_after=self.phase,
            ))

        # Record tick
        fitnesses = [s.fitness for s in self.species]
        record = TickRecord(
            tick=self.tick,
            species_count=self.n_species,
            mean_fitness=float(np.mean(fitnesses)),
            max_fitness=float(np.max(fitnesses)),
            min_fitness=float(np.min(fitnesses)),
            density=self._compute_density(),
            clustering=self._compute_clustering() if self.tick % 10 == 0 else (self.history[-1].clustering if self.history else 0),
            largest_component=self._largest_component_size() if self.tick % 10 == 0 else (self.history[-1].largest_component if self.history else self.n_species),
            num_keystones=sum(1 for s in self.species if s.is_keystone),
            phase=self.phase.value,
            cascade_size=cascade_size,
            diversity=self._compute_diversity(),
        )
        self.history.append(record)

        return cascade_size

    def _replace_species(self, idx: int, perturb_neighbors: bool = True):
        """
        Replace species at idx with a new random species.
        Optionally perturb neighbors (Bak-Sneppen style).
        """
        # Find neighbors before clearing connections
        neighbors = set()
        if perturb_neighbors:
            for j in range(self.n_species):
                if j == idx:
                    continue
                if self.weights[idx][j] != 0 or self.weights[j][idx] != 0:
                    neighbors.add(j)

        # Create new species
        self.species[idx] = Species(id=idx, age=0)

        # Clear old connections
        self.weights[idx, :] = 0
        self.weights[:, idx] = 0

        # Create new random connections
        for j in range(self.n_species):
            if j == idx:
                continue
            if self.rng.random() < self.connection_prob:
                self.weights[idx][j] = self.rng.uniform(*self.weight_range)
            if self.rng.random() < self.connection_prob:
                self.weights[j][idx] = self.rng.uniform(*self.weight_range)

        # Perturb some neighbor connections (Bak-Sneppen mechanism)
        if perturb_neighbors:
            for nb in neighbors:
                # Randomly rewire some connections of neighbors
                for j in range(self.n_species):
                    if j == nb:
                        continue
                    if self.weights[nb][j] != 0 and self.rng.random() < 0.08:
                        # Rewire this edge
                        self.weights[nb][j] = self.rng.uniform(*self.weight_range)

        # Recompute all fitness
        self._compute_all_fitness()

    def _propagate_cascade(self, pre_fitness: dict, excluded: set = None) -> int:
        """
        Check if any species suffered major fitness drops after perturbation.
        Species whose fitness dropped by more than 40% relative to before,
        AND whose absolute fitness is below a viability threshold, get replaced.
        This can cascade as further replacements change the network.
        """
        if excluded is None:
            excluded = set()
        total_removed = 0
        max_iterations = 20

        for _ in range(max_iterations):
            to_remove = []
            for i, s in enumerate(self.species):
                if i in excluded or s.age == 0:
                    continue
                old_f = pre_fitness.get(i, 0.5)
                if old_f > 0.25:
                    drop = (old_f - s.fitness) / old_f
                    # Species that lost >50% fitness and are now below 0.3 are replaced
                    if drop > 0.5 and s.fitness < 0.3:
                        to_remove.append(i)

            if not to_remove:
                break

            pre_fitness_round = {i: self.species[i].fitness for i in range(self.n_species)}
            for idx in to_remove:
                excluded.add(idx)
                self._replace_species(idx)
                total_removed += 1
            # Update pre_fitness for next iteration
            pre_fitness = pre_fitness_round

        return total_removed

    def remove_species(self, idx: int) -> int:
        """
        Manually remove a specific species (for cascade testing).
        Returns total cascade size.
        """
        pre_fitness = {i: self.species[i].fitness for i in range(self.n_species)}
        self._replace_species(idx)
        cascade_size = 1 + self._propagate_cascade(pre_fitness, excluded={idx})
        return cascade_size

    def cascade_test(self) -> list[tuple[int, int, bool]]:
        """
        Systematically test removing each species and measuring cascade size.
        Returns list of (species_id, cascade_size, was_keystone).

        NOTE: This is non-destructive - restores state after each test.
        """
        results = []
        # Save state
        saved_weights = self.weights.copy()
        saved_species = [
            Species(id=s.id, fitness=s.fitness, age=s.age, is_keystone=s.is_keystone)
            for s in self.species
        ]

        self._identify_keystones()

        for i in range(self.n_species):
            was_keystone = self.species[i].is_keystone
            cascade_size = self.remove_species(i)
            results.append((i, cascade_size, was_keystone))

            # Restore state
            self.weights = saved_weights.copy()
            self.species = [
                Species(id=s.id, fitness=s.fitness, age=s.age, is_keystone=s.is_keystone)
                for s in saved_species
            ]

        return results

    def run(self, ticks: int, callback=None) -> list[TickRecord]:
        """Run simulation for given number of ticks."""
        for t in range(ticks):
            cascade_size = self.step()
            if callback:
                callback(self.tick, cascade_size, self.phase)
        return self.history

    def get_state_json(self) -> dict:
        """Export current state as JSON-serializable dict for visualization."""
        nodes = []
        for i, s in enumerate(self.species):
            nodes.append({
                "id": i,
                "fitness": round(s.fitness, 4),
                "age": s.age,
                "is_keystone": bool(s.is_keystone),
                "category": s.classify(max(sp.age for sp in self.species) if self.species else 1),
            })

        edges = []
        for i in range(self.n_species):
            for j in range(self.n_species):
                if self.weights[i][j] != 0:
                    edges.append({
                        "source": j,
                        "target": i,
                        "weight": round(float(self.weights[i][j]), 4),
                    })

        fitnesses = [s.fitness for s in self.species]
        return {
            "tick": self.tick,
            "phase": self.phase.value,
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "mean_fitness": round(float(np.mean(fitnesses)), 4),
                "max_fitness": round(float(np.max(fitnesses)), 4),
                "min_fitness": round(float(np.min(fitnesses)), 4),
                "density": round(self._compute_density(), 4),
                "diversity": round(self._compute_diversity(), 4),
                "num_keystones": sum(1 for s in self.species if s.is_keystone),
                "species_count": self.n_species,
            },
        }

    def get_history_json(self) -> list[dict]:
        """Export history as JSON-serializable list."""
        return [
            {
                "tick": r.tick,
                "species_count": r.species_count,
                "mean_fitness": round(r.mean_fitness, 4),
                "max_fitness": round(r.max_fitness, 4),
                "min_fitness": round(r.min_fitness, 4),
                "density": round(r.density, 4),
                "clustering": round(r.clustering, 4),
                "largest_component": r.largest_component,
                "num_keystones": r.num_keystones,
                "phase": r.phase,
                "cascade_size": r.cascade_size,
                "diversity": round(r.diversity, 4),
            }
            for r in self.history
        ]

    def get_cascade_distribution(self) -> dict[int, int]:
        """Get frequency distribution of cascade sizes."""
        dist: dict[int, int] = {}
        for c in self.cascades:
            if c.size > 0:
                dist[c.size] = dist.get(c.size, 0) + 1
        return dict(sorted(dist.items()))

    def save_csv(self, filepath: str):
        """Save history to CSV file."""
        if not self.history:
            return
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick", "species_count", "mean_fitness", "max_fitness",
                "min_fitness", "density", "clustering", "largest_component",
                "num_keystones", "phase", "cascade_size", "diversity",
            ])
            for r in self.history:
                writer.writerow([
                    r.tick, r.species_count, f"{r.mean_fitness:.4f}",
                    f"{r.max_fitness:.4f}", f"{r.min_fitness:.4f}",
                    f"{r.density:.4f}", f"{r.clustering:.4f}",
                    r.largest_component, r.num_keystones,
                    r.phase, r.cascade_size, f"{r.diversity:.4f}",
                ])

    def save_json(self, filepath: str):
        """Save full state and history to JSON file."""
        data = {
            "params": {
                "n_species": self.n_species,
                "connection_prob": self.connection_prob,
                "weight_range": list(self.weight_range),
            },
            "state": self.get_state_json(),
            "history": self.get_history_json(),
            "cascades": [
                {
                    "tick": c.tick,
                    "trigger_species": c.trigger_species,
                    "size": c.size,
                    "phase_before": c.phase_before.value,
                    "phase_after": c.phase_after.value,
                }
                for c in self.cascades
            ],
            "cascade_distribution": self.get_cascade_distribution(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
