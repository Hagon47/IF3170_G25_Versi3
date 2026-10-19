import math
import random
import time
from typing import Any, Dict, Iterable, List, Optional

from src.problem import Package, State, Truck, get_random_neighbor, objective

def exponential_cooling(T_start, alpha, iteration):
    return T_start * (alpha ** iteration)

def validate_parameters(
    initial_temperature: float,
    cooling_rate: float,
    minimum_temperature: float,
    max_iterations: int,
) -> None:
    if initial_temperature <= 0:
        raise ValueError("initial_temperature harus lebih besar dari 0.")
    if minimum_temperature < 0:
        raise ValueError("minimum_temperature tidak boleh negatif.")
    if initial_temperature <= minimum_temperature:
        raise ValueError(
            "initial_temperature harus lebih besar dari minimum_temperature."
        )
    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate harus berada di antara 0 dan 1.")
    if max_iterations < 1:
        raise ValueError("max_iterations harus minimal 1.")


def acceptance_probability(
    current_value: int, candidate_value: int, temperature: float
) -> float:
    if temperature <= 0:
        raise ValueError("temperature harus lebih besar dari 0.")
    if candidate_value >= current_value:
        return 1.0
    return math.exp((candidate_value - current_value) / temperature)


def simulated_annealing(
    packages: Iterable[Package],
    truck: Truck,
    initial_temperature: float = 100.0,
    cooling_rate: float = 0.99,
    minimum_temperature: float = 0.1,
    max_iterations: int = 10000,
    seed: Optional[int] = None,
    check_fragile: bool = True,
    verbose: bool = True,
    log_every: int = 100,
) -> Dict[str, Any]:
    validate_parameters(
        initial_temperature,
        cooling_rate,
        minimum_temperature,
        max_iterations,
    )
    if log_every < 1:
        raise ValueError("log_every harus minimal 1.")

    rng = random.Random(seed)
    package_list = tuple(packages)
    start_time = time.perf_counter()

    current_state = State.random(package_list, truck, rng)
    initial_state = current_state
    current_value = objective(current_state, check_fragile)
    best_state = current_state
    best_value = current_value
    objective_history: List[int] = [best_value]
    acceptance_factor_history: List[float] = [1.0]
    stuck_frequency = 0

    temperature = initial_temperature
    iteration = 0

    while (
        package_list
        and temperature > minimum_temperature
        and iteration < max_iterations
    ):
        if iteration >= max_iterations:
            break

        iteration += 1
        acceptance_factor = 1.0
        neighbor = (
            get_random_neighbor(current_state, rng, check_fragile=check_fragile)
            if package_list
            else None
        )

        if neighbor is not None:
            _, candidate_state = neighbor
            candidate_value = objective(candidate_state, check_fragile)
            probability = acceptance_probability(
                current_value, candidate_value, temperature
            )
            acceptance_factor = probability

            if rng.random() < probability:
                current_state = candidate_state
                current_value = candidate_value

                if current_value > best_value:
                    best_state = current_state
                    best_value = current_value

        is_stuck = best_value == objective_history[-1]
        if is_stuck:
            stuck_frequency += 1

        objective_history.append(current_value)
        acceptance_factor_history.append(acceptance_factor)

        if verbose and iteration % log_every == 0:
            print(
                f"[Simulated Annealing] Iterasi {iteration:5d} | "
                f"suhu = {temperature:.4f} | "
                f"nilai saat ini = {current_value} | "
                f"nilai terbaik = {best_value}"
            )

        temperature = exponential_cooling(
            initial_temperature, cooling_rate, iteration
        )

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "simulated_annealing",
        "seed": seed,
        "initial_state": initial_state,
        "final_state": current_state,
        "final_value": current_value,
        "best_state": best_state,
        "best_value": best_value,
        "objective_history": objective_history,
        "acceptance_factor_history": acceptance_factor_history,
        "e_delta_E_over_T": acceptance_factor_history,
        "acceptance_probability_history": acceptance_factor_history,
        "stuck_frequency": stuck_frequency,
        "duration": duration,
    }