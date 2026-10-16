from .constraints import is_valid

def objective(state, check_fragile=True):
    if not is_valid(state, check_fragile):
        return 0
    
    return state.total_value()