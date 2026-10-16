from typing import Dict, List, Tuple
from .state import State

Bounds = Tuple[int, int, int, int, int, int]

def _overlap_1d(a1: int, a2: int, b1: int, b2: int) -> bool:
    return a1 < b2 and b1 < a2

def _overlap_2d(a: Bounds, b: Bounds) -> bool:
    return _overlap_1d(a[0], a[3], b[0], b[3]) and _overlap_1d(a[1], a[4], b[1], b[4])

def _overlap_3d(a: Bounds, b: Bounds) -> bool:
    return _overlap_2d(a, b) and _overlap_1d(a[2], a[5], b[2], b[5])

def _is_supported_by(top: Bounds, bottom: Bounds) -> bool:
    return top[2] == bottom[5] and _overlap_2d(top, bottom)

def _is_above(top: Bounds, bottom: Bounds) -> bool:
    return top[2] >= bottom[5] and _overlap_2d(top, bottom)

def get_constraints(state: State, check_fragile: bool = True) -> Dict[str, int]:
    placed = state.inside()
    bounds: List[Bounds] = [p.get_bounds() for p in placed]
    
    n = len(placed)

    out_of_bounds = sum(1 for p in placed if not state.truck.contain(p))

    overlap_count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if _overlap_3d(bounds[i], bounds[j]):
                overlap_count += 1

    floating_count = 0
    for i in range(n):
        if bounds[i][2] == 0:
            continue
        
        supported = any(j != i and _is_supported_by(bounds[i], bounds[j]) for j in range(n))
        
        if not supported:
            floating_count += 1

    is_on_top = _is_above if check_fragile else _is_supported_by
    
    fragile_count = 0
    for j in range(n):
        if not placed[j].is_fragile:
            continue
        
        for i in range(n):
            if i != j and is_on_top(bounds[i], bounds[j]):
                fragile_count += 1

    weight = 1 if state.total_weight() > state.truck.max_capacity else 0

    return {
        "out_of_bounds": out_of_bounds,
        "overlap": overlap_count,
        "floating": floating_count,
        "fragile": fragile_count,
        "weight": weight,
    }

def get_total_penalty(state: State, check_fragile: bool = True) -> int:
    return sum(get_constraints(state, check_fragile).values())

def get_overweight(state: State) -> int:
    return max(0, state.total_weight() - state.truck.max_capacity)

def is_valid(state: State, check_fragile: bool = True) -> bool:
    return get_total_penalty(state, check_fragile) == 0