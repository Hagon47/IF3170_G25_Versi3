from . import state

from .constraints import _is_above, is_valid

def objective(state, num, check_fragile=True):
    match num:
        case 1:
            return objective_1(state, check_fragile)
        case 2:
            return objective_2(state, check_fragile)
        case 3:
            return objective_3(state, check_fragile)
        case _:
            return objective_1(state, check_fragile)

def objective_1(state, check_fragile=True):
    if not is_valid(state, check_fragile):
        return 0
    
    return state.total_value()

def objective_2(state, check_fragile=True):
    if not is_valid(state, check_fragile):
        return float("-inf")

    penalty_weight = 5 # bole diubah
    diff_sum = 0
    packages = state.inside()
    bounds = [package.get_bounds() for package in packages]

    for i in range(len(packages)):
        for j in range(len(packages)):
            if i == j:
                continue

            if packages[j].eta > packages[i].eta and _is_above(bounds[j], bounds[i]):
                diff_sum += packages[j].eta - packages[i].eta

    return state.total_value() - (diff_sum * penalty_weight)

def objective_3(state, check_fragile=True):
    if not is_valid(state, check_fragile):
        return 0
    
    return state.total_value() / state.total_weight()