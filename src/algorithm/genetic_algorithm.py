import random
import time
from typing import Any, Dict, List, Optional, Tuple

from problem import State, get_random_neighbor, is_valid, objective

MUTATION_PROB = 0.3

def initial_population(packages, truck, population_size: int, rng: random.Random) -> List[State]:
    return [State.random(packages, truck, rng) for _ in range(population_size)]

def fitness_function(individual: State, num: int) -> int:
    return objective(individual, num)

def fitness_percentage(fitness_values: List[int]) -> List[float]:
    total_fitness = sum(fitness_values)

    if total_fitness == 0:
        return [1 / len(fitness_values)] * len(fitness_values)

    return [fitness / total_fitness for fitness in fitness_values]

def roulette_wheel(probabilities: List[float], rng: random.Random) -> int:
    roulette_result = rng.random()

    cumulative = 0.0
    for index, percentage in enumerate(probabilities):
        cumulative += percentage
        
        if roulette_result <= cumulative:
            return index

    return len(probabilities) - 1 

def selection(population: List[State], probabilities: List[float], rng: random.Random) -> List[Tuple[State, State]]:
    total_pairs = (len(population) + 1) // 2

    selected_parents = []
    for _ in range(total_pairs):
        parent1 = population[roulette_wheel(probabilities, rng)]
        parent2 = population[roulette_wheel(probabilities, rng)]
        selected_parents.append((parent1, parent2))

    return selected_parents

def crossover(parent1: State, parent2: State, rng: random.Random) -> Tuple[State, State]:
    total_genes = len(parent1.packages)

    if total_genes < 2:
        return parent1, parent2

    crossover_point = rng.randint(1, total_genes - 1)

    genes_child1 = parent1.packages[:crossover_point] + parent2.packages[crossover_point:]
    genes_child2 = parent2.packages[:crossover_point] + parent1.packages[crossover_point:]

    child1 = repair(genes_child1, genes_child2, parent1)
    child2 = repair(genes_child2, genes_child1, parent1)
    
    return child1, child2

def repair(genes, backup_genes, reference: State) -> State:
    def base_height(package) -> float: #nilai z paket
        return package.position[2] if package.is_placed else float("inf")

    insert_order = sorted(range(len(genes)), key=lambda i: base_height(genes[i]))

    child = State(tuple(p.remove() for p in reference.packages), reference.truck)

    for i in insert_order:
        for gene in (genes[i], backup_genes[i]):
            if not gene.is_placed:
                continue

            trial_state = child._replace_packages({i: gene})
            
            if is_valid(trial_state):
                child = trial_state
                break

    return child

def mutation(child: State, rng: random.Random, mutation_prob: float = MUTATION_PROB) -> State:
    if rng.random() < mutation_prob:
        result = get_random_neighbor(child, rng)

        if result is not None:
            _, mutated_child = result
            return mutated_child

    return child

def genetic_algorithm(
    packages,
    truck,
    num: int,
    population_size: int = 30, #bebas
    generations: int = 50, #bebas
    seed: Optional[int] = None,
    verbose: bool = True,
    log_every: int = 10,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    start_time = time.perf_counter()
    
    population = initial_population(packages, truck, population_size, rng)

    initial_best = max(population, key=lambda x: fitness_function(x, num))
    best_state = initial_best
    best_value = fitness_function(initial_best, num)

    best_objective: List[int] = []
    mean_objective: List[float] = []

    for iteration in range(generations + 1):
        fitness_values = [fitness_function(individual, num) for individual in population]
        probabilities = fitness_percentage(fitness_values)

        current_best_index = max(range(population_size), key=lambda i: fitness_values[i])
        current_best_value = fitness_values[current_best_index]
        current_mean_value = sum(fitness_values) / population_size

        best_objective.append(current_best_value)
        mean_objective.append(current_mean_value)

        if current_best_value > best_value:
            best_state, best_value = population[current_best_index], current_best_value

        if verbose and iteration % log_every == 0:
            print(f"[Genetic Algorithm] Generasi {iteration:3d} | max = {current_best_value} | rata-rata = {current_mean_value:.1f}")

        if iteration == generations:
            break

        selected_parents = selection(population, probabilities, rng)

        new_population: List[State] = []
        for parent1, parent2 in selected_parents:
            child1, child2 = crossover(parent1, parent2, rng)

            new_population.append(mutation(child1, rng))
            new_population.append(mutation(child2, rng))

        population = new_population[:population_size]

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "genetic_algorithm",
        "population_size": population_size,
        "generations": generations,
        "mutation_prob": MUTATION_PROB,
        "seed": seed,
        "initial_state": initial_best,
        "initial_value": fitness_function(initial_best),
        "final_state": best_state,
        "final_value": best_value,
        "best_objective": best_objective,
        "mean_objective": mean_objective,
        "duration": duration,
    }