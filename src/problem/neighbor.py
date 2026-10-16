import random
from typing import Dict, List, Optional, Tuple

from .constraints import is_valid
from .state import State


Position = Tuple[int, int, int]
Move = tuple
Neighbor = Tuple[Move, State]
SUMBU_KOORDINAT = ("x", "y", "z")

def get_candidate(state: State, i: int) -> List[Optional[Position]]:
    package = state.packages[i]
    w, l, h = package.get_dimensions
    truck_width, truck_length, truck_height = state.truck.dimensions

    points = {(0, 0, 0)}
    for k, other in enumerate(state.packages):
        if k == i or not other.is_placed:
            continue
        
        x1, y1, z1, x2, y2, z2 = other.get_bounds()
        
        points.add((x2, y1, z1))  #di kanan paket 
        points.add((x1, y2, z1))  #di depan paket
        points.add((x2, y1, 0))   #di kanan, tapi di alas truk nya 
        points.add((x1, y2, 0))   #di depan, tapi di alas truk nya
        
        if not other.is_fragile:
            points.add((x1, y1, z2))  #di atas paket lain tp ga fragile 

    valid_positions: List[Optional[Position]] = [
        (x, y, z) for (x, y, z) in points
        
        if x + w <= truck_width and y + l <= truck_length and z + h <= truck_height and (x, y, z) != package.position
    ]

    if package.is_placed:
        valid_positions.append(None)  
        
    return valid_positions

def get_all_neighbor(state: State, check_fragile: bool = True) -> List[Neighbor]:
    #ini buat hill climbing kecuali si stochastic
    found: Dict[State, Move] = {}

    def collect_neighbor(move: Move, candidate: State) -> None:
        if candidate != state and candidate not in found and is_valid(candidate, check_fragile):
            found[candidate] = move

    n = len(state.packages)

    #Menukar dua paket, baik di dalam maupun di luar truk
    for i in range(n):
        for j in range(i + 1, n):
            if state.packages[i].is_placed or state.packages[j].is_placed:
                collect_neighbor(("swap", i, j), state.swap(i, j))

    #Memindahkan sebuah paket ke suatu koordinat yang berbeda
    for i in range(n):
        for pos in get_candidate(state, i):
            collect_neighbor(("move", i, pos), state.move(i, pos))

    #Merotasi paket 90° terhadap sumbu x, y, atau z
    for i in range(n):
        if state.packages[i].is_placed:
            for axis in SUMBU_KOORDINAT:
                collect_neighbor(("rotate", i, axis), state.rotate(i, axis))

    return [(move, s) for s, move in found.items()]


def get_random_neighbor(
    state: State,
    rng: Optional[random.Random] = None,
    max_attempts: int = 200,
    check_fragile: bool = True,
) -> Optional[Neighbor]:
    #ini buat stochastic, sa, sama ga
    
    rng = rng or random.Random()
    n = len(state.packages)
    inside = [i for i in range(n) if state.packages[i].is_placed]

    for _ in range(max_attempts):
        move_type = rng.choice(("swap", "move", "rotate"))

        if move_type == "swap":
            if n < 2 or not inside:
                continue
            
            i = rng.choice(inside)  #minimal satu paket di dalem
            j = rng.choice([k for k in range(n) if k != i])
            move, candidate = ("swap", i, j), state.swap(i, j)

        elif move_type == "move":
            i = rng.randrange(n)
            valid_positions = get_candidate(state, i)
            
            if not valid_positions:
                continue
            
            pos = rng.choice(valid_positions)
            move, candidate = ("move", i, pos), state.move(i, pos)

        else:  #rotate
            if not inside:
                continue
            
            i = rng.choice(inside)
            axis = rng.choice(SUMBU_KOORDINAT)
            move, candidate = ("rotate", i, axis), state.rotate(i, axis)

        if candidate != state and is_valid(candidate, check_fragile):
            return move, candidate

    return None