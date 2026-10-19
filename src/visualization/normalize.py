from typing import Any, Dict, List, Optional, Tuple
from problem import State, objective


Series = List[Tuple[str, List[float]]] 

def format_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "-"

    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"

    return f"{seconds:.2f} s"

def to_state(data: Any) -> State:
    if isinstance(data, State):
        return data

    if isinstance(data, dict):
        return State.from_dict(data)

    raise TypeError(f"State harus berupa State atau dict, bukan {type(data).__name__}.")

def _get_required(result: Dict[str, Any], key: str) -> Any:
    if key not in result:
        raise KeyError(f"Hasil algoritma {result.get('algorithm')!r} tidak memiliki key {key!r}.")

    return result[key]

def _get_existing(result: Dict[str, Any], keys: Tuple[str, ...]) -> Dict[str, Any]:
    return {key: result[key] for key in keys if key in result}

def _hill_climbing(result: Dict[str, Any]) -> Tuple[Series, str, Dict[str, Any]]:
    #ini buat yg steepest ascent, sideways move, stochastic
    obj_vals = [("Objective", list(_get_required(result, "objective_values")))]
    x_label = "Iterasi" if result["algorithm"] == "hc_stochastic" else "Langkah"
    
    info = _get_existing(result, ("iterations", "max_iterations", "sideways_count", "max_sideways"))

    return obj_vals, x_label, info

def _random_restart(result: Dict[str, Any]) -> Tuple[Series, str, Dict[str, Any]]:
    obj_vals = _get_required(result, "objective_values")
    obj_vals_per_iteration = [("Run awal" if i == 0 else f"Restart {i}", list(run)) for i, run in enumerate(obj_vals)]
    info = _get_existing(result, ("restart_count", "max_restarts", "iterations_in_restarts", "iterations", "max_iterations"))

    return obj_vals_per_iteration, "Langkah", info

def _simulated_annealing(result: Dict[str, Any]) -> Tuple[Series, str, Dict[str, Any], List[float]]:
    history = list(_get_required(result, "objective_history"))
    series = [("Objective", history)]
    
    info = _get_existing(result, ("stuck_frequency", "seed"))
    info["iterations"] = len(history) - 1

    acceptance = list(result.get("acceptance_history", []))[1:]

    return series, "Iterasi", info, acceptance

def _genetic_algorithm(result: Dict[str, Any]) -> Tuple[Series, str, Dict[str, Any]]:
    list_genetic = [
        ("Maksimum", list(_get_required(result, "best_objective"))),
        ("Rata-rata", list(_get_required(result, "mean_objective"))),
    ]
    
    info = _get_existing(result, ("population_size", "generations", "mutation_prob", "seed"))

    return list_genetic, "Generasi", info

def normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, dict):
        raise TypeError("Hasil algoritma harus berupa dict.")

    algorithm = result.get("algorithm")
    acceptance: Optional[List[float]] = None

    if algorithm == "hc_steepest_accent":
        label = "Hill-Climbing Steepest Ascent"
        obj_vals, x_label, info = _hill_climbing(result)

    elif algorithm == "hc_sideways_move":
        label = "Hill-Climbing Sideways Move"
        obj_vals, x_label, info = _hill_climbing(result)

    elif algorithm == "hc_stochastic":
        label = "Hill-Climbing Stochastic"
        obj_vals, x_label, info = _hill_climbing(result)

    elif algorithm == "hc_random_restart":
        label = "Hill-Climbing Random Restart"
        obj_vals, x_label, info = _random_restart(result)

    elif algorithm == "simulated_annealing":
        label = "Simulated Annealing"
        obj_vals, x_label, info, acceptance = _simulated_annealing(result)

    elif algorithm == "genetic_algorithm":
        label = "Genetic Algorithm"
        obj_vals, x_label, info = _genetic_algorithm(result)

    else:
        raise ValueError(f"Algoritma {algorithm!r} tidak ada.")

    initial_state = to_state(_get_required(result, "initial_state"))
    final_state = to_state(_get_required(result, "final_state"))

    initial_value = result.get("initial_value")
    
    if initial_value is None:
        initial_value = objective(initial_state)

    final_value = result.get("final_value")
    
    if final_value is None:
        final_value = objective(final_state)

    return {
        "algorithm": algorithm,
        "label": label,
        "duration": result.get("duration"),
        "initial_state": initial_state,
        "final_state": final_state,
        "initial_value": initial_value,
        "final_value": final_value,
        "series": obj_vals,
        "x_label": x_label,
        "acceptance": acceptance,
        "info": info,
    }