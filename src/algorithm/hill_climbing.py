import random
import time
from typing import Any, Dict, Optional, Tuple

from src.problem import State, get_all_neighbor, get_random_neighbor, is_valid, objective


def validate_input(initial_state: State, max_iterations: int, check_fragile: bool) -> None:
    if type(max_iterations) is not int or max_iterations < 0:
        raise ValueError("Max iterasi harus integer >= 0.")
    if not is_valid(initial_state, check_fragile):
        raise ValueError("State awal harus memenuhi constraint!")


def best_neighbor(state: State, check_fragile: bool, rng: Optional[random.Random] = None) -> Optional[Tuple[State, int]]:
    neighbors = get_all_neighbor(state, check_fragile)
    if not neighbors:
        return None

    scores = [objective(candidate, check_fragile) for _, candidate in neighbors]
    best_val = max(scores)
    best_states = []
    for i in range(len(neighbors)):
        if scores[i] == best_val:
            candidate = neighbors[i][1]
            best_states.append(candidate)

    if rng is not None:
        best_state = rng.choice(best_states)
    else:
        best_state = best_states[0]
    return best_state, best_val


def hc_steepest_accent(initial_state: State, max_iterations: int = 1000, check_fragile: bool = True) -> Dict[str, Any]:
    validate_input(initial_state, max_iterations, check_fragile)
    start_time = time.perf_counter()
    current_state = initial_state
    current_value = objective(current_state, check_fragile)
    obj_values = [current_value]

    for _ in range(max_iterations):
        neighbor = best_neighbor(current_state, check_fragile)
        if neighbor is None:
            break

        next_state, next_value = neighbor
        if next_value <= current_value:
            break

        current_state, current_value = next_state, next_value
        obj_values.append(current_value)

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "hc_steepest_accent",
        "initial_state": initial_state,
        "initial_value": obj_values[0],
        "final_state": current_state,
        "final_value": current_value,
        "objective_history": obj_values,
        "iterations": len(obj_values) - 1,
        "max_iterations": max_iterations,
        "duration": duration
    }


