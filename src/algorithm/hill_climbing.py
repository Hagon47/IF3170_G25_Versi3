import random
import time
from typing import Any, Dict, Optional, Tuple

from problem import State, get_all_neighbor, get_random_neighbor, is_valid, objective


def validate_input(initial_state: State, max_iterations: int, check_fragile: bool) -> None:
    if type(max_iterations) is not int or max_iterations < 0:
        raise ValueError("Max iterasi harus integer >= 0.")
    if not is_valid(initial_state, check_fragile):
        raise ValueError("State awal harus memenuhi constraint!")


def best_neighbor(state: State, check_fragile: bool, num: int, rng: Optional[random.Random] = None) -> Optional[Tuple[State, int]]:
    neighbors = get_all_neighbor(state, check_fragile)
    if not neighbors:
        return None

    scores = [objective(candidate, num, check_fragile) for _, candidate in neighbors]
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




def hc_steepest_accent(initial_state: State, num: int, max_iterations: int = 1000, check_fragile: bool = True) -> Dict[str, Any]:
    validate_input(initial_state, max_iterations, check_fragile)
    start_time = time.perf_counter()
    current_state = initial_state
    current_value = objective(current_state, num, check_fragile)
    obj_values = [current_value]

    for _ in range(max_iterations):
        neighbor = best_neighbor(current_state, check_fragile, num)
        if neighbor is None:
            break

        next_state, next_value = neighbor
        if next_value <= current_value:
            break

        current_state, current_value = next_state, next_value
        obj_values.append(current_value)

    end_time = time.perf_counter()
    duration = end_time - start_time

    return {
        "algorithm": "hc_steepest_accent",
        "initial_state": initial_state,
        "initial_value": obj_values[0],
        "final_state": current_state,
        "final_value": current_value,
        "objective_values": obj_values,
        "iterations": len(obj_values) - 1,
        "max_iterations": max_iterations,
        "duration": duration
    }



def hc_sideways_move(initial_state: State, num: int, max_sideways: int = 100, max_iterations: int = 1000, check_fragile: bool = True) -> Dict[str, Any]:
    validate_input(initial_state, max_iterations, check_fragile)
    if type(max_sideways) is not int or max_sideways < 0:
        raise ValueError("max_sideways harus berupa integer >= 0.")

    start_time = time.perf_counter()
    rng = random.Random()
    cur_state = initial_state
    cur_val = objective(cur_state, num, check_fragile)
    obj_values = [cur_val]
    sideways_count = 0

    for _ in range(max_iterations):
        neighbor = best_neighbor(cur_state, check_fragile, num, rng)
        if neighbor is None:
            break

        next_state, next_value = neighbor
        if next_value < cur_val:
            break

        if next_value == cur_val:
            if sideways_count >= max_sideways:
                break
            sideways_count += 1

        cur_state, cur_val = next_state, next_value
        obj_values.append(cur_val)

        if max_sideways > 0 and sideways_count == max_sideways:
            break

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "hc_sideways_move",
        "initial_state": initial_state,
        "initial_value": obj_values[0],
        "final_state": cur_state,
        "final_value": cur_val,
        "objective_values": obj_values,
        "iterations": len(obj_values) - 1,
        "max_iterations": max_iterations,
        "max_sideways": max_sideways,
        "sideways_count": sideways_count,
        "duration": duration
    }


def hc_stochastic(initial_state: State, num : int, max_iterations: int = 1000, check_fragile: bool = True) -> Dict[str, Any]:
    validate_input(initial_state, max_iterations, check_fragile)
    start_time = time.perf_counter()
    rng = random.Random()
    cur_state = initial_state
    cur_val = objective(cur_state, num, check_fragile)
    obj_values = [cur_val]

    for _ in range(max_iterations):
        if cur_state.packages:
            neighbor = get_random_neighbor(cur_state, rng, check_fragile=check_fragile)
        else:
            neighbor = None
            
        if neighbor is not None:
            _, next_state = neighbor
            next_value = objective(next_state, num, check_fragile)
            if next_value > cur_val:
                cur_state, cur_val = next_state, next_value

        obj_values.append(cur_val)

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "hc_stochastic",
        "initial_state": initial_state,
        "initial_value": obj_values[0],
        "final_state": cur_state,
        "final_value": cur_val,
        "objective_values": obj_values,
        "iterations": len(obj_values) - 1,
        "max_iterations": max_iterations,
        "duration": duration
    }


def hc_random_restart(initial_state: State, num: int, max_restarts: int = 10, max_iterations: int = 1000, check_fragile: bool = True) -> Dict[str, Any]:
    validate_input(initial_state, max_iterations, check_fragile)
    if type(max_restarts) is not int or max_restarts < 0:
        raise ValueError("max_restarts harus integer >= 0.")

    start_time = time.perf_counter()
    cur_state = initial_state
    initial_value = objective(initial_state, num, check_fragile)
    best_state = initial_state
    best_val = initial_value
    restart_count = 0
    iterations_in_restarts = []
    obj_values = []

    for restart in range(max_restarts + 1):
        if restart > 0:
            cur_state = State.random(initial_state.packages, initial_state.truck)
            restart_count += 1

        result = hc_steepest_accent(cur_state, num=num, max_iterations=max_iterations, check_fragile=check_fragile) # seinget gw random restart itu pake SA dl?
        iterations_in_restarts.append(result["iterations"])
        obj_values.append(result["objective_values"])

        if result["final_value"] > best_val:
            best_state = result["final_state"]
            best_val = result["final_value"]

    duration = time.perf_counter() - start_time

    return {
        "algorithm": "hc_random_restart",
        "initial_state": initial_state,
        "initial_value": initial_value,
        "final_state": best_state,
        "final_value": best_val,
        "objective_values": obj_values,
        "iterations": sum(iterations_in_restarts),
        "iterations_in_restarts": iterations_in_restarts,
        "restart_count": restart_count,
        "max_restarts": max_restarts,
        "max_iterations": max_iterations,
        "duration": duration
    }
