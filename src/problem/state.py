import random
from dataclasses import dataclass, replace
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .package import Package
from .truck import Truck

@dataclass(frozen=True)
class State:
    packages: Tuple[Package, ...]  
    truck: Truck

    def __post_init__(self) -> None:
        if not isinstance(self.packages, tuple):
            object.__setattr__(self, "packages", tuple(self.packages))

        ids = [p.id for p in self.packages]
        if len(ids) != len(set(ids)):
            raise ValueError("ID paket tidak boleh duplikat.")

    def __len__(self) -> int:
        return len(self.packages)

    def inside(self) -> List[Package]:
        return [p for p in self.packages if p.is_placed]

    def outside(self) -> List[Package]:
        return [p for p in self.packages if not p.is_placed]

    def total_value(self) -> int:
        return sum(p.value for p in self.packages if p.is_placed)

    def total_weight(self) -> int:
        return sum(p.weight for p in self.packages if p.is_placed)

    def index_of(self, package_id: str) -> int:
        for i, p in enumerate(self.packages):
            if p.id == package_id:
                return i
            
        raise KeyError(f"Paket {package_id!r} tidak ditemukan.")

    def move(self, i: int, position: Optional[Tuple[int, int, int]]) -> "State":
        return self._replace_packages({i: _relocate(self.packages[i], position)})

    def swap(self, i: int, j: int) -> "State":
        if i == j:
            raise ValueError("Tidak bisa menukar paket dengan dirinya sendiri.")
        
        a, b = self.packages[i], self.packages[j]
        
        return self._replace_packages({
            i: _relocate(a, b.position),
            j: _relocate(b, a.position),
        })

    def rotate(self, i: int, axis: str) -> "State":
        return self._replace_packages({i: self.packages[i].rotate(axis)})

    def _replace_packages(self, changes: Dict[int, Package]) -> "State":
        new_packages = list(self.packages)
        
        for i, p in changes.items():
            new_packages[i] = p
        return replace(self, packages=tuple(new_packages))
    
    def objective_function(self) -> int:
        from .constraints import get_constraints
        
        constraint = get_constraints(self, check_fragile=False)
        
        if constraint["overlap"] > 0 or constraint["floating"] > 0 or constraint["fragile"] > 0 or constraint["weight"] > 0:
            return 0
        
        wasted_value =  sum(p.value for p in self.packages if not self.truck.contains(p))
        return self.total_value() - wasted_value
    
    @classmethod
    def random(
        cls,
        packages: Iterable[Package],
        truck: Truck,
        rng: Optional[random.Random] = None,
        p_inside: float = 0.5,
    ) -> "State":
        from .constraints import is_valid
        rng = rng or random.Random()
        max_attempts = 100 # ganti ganti aja ges

        init_pack = tuple(p.remove().get_rotation(rng.randrange(len(Package.ORIENTATIONS))) for p in packages)

        state = cls(packages=init_pack, truck=truck)

        order = list(range(len(state.packages)))
        rng.shuffle(order)

        truck_width, truck_length, truck_height = truck.dimensions

        for i in order:
            if rng.random() >= p_inside:
                continue

            package = state.packages[i]

            if state.total_weight() + package.weight > truck.max_capacity:
                continue


            fit_rotation = [rotation for rotation in range(len(Package.ORIENTATIONS)) if truck.fit(package.get_rotation(rotation).get_dimensions)]

            if not fit_rotation:
                continue

            for _ in range(max_attempts):
                oriented = package.get_rotation(rng.choice(fit_rotation))

                w, l, h = oriented.get_dimensions

                support_levels = {0}

                for other in state.inside():
                    if not other.is_fragile:
                        support_levels.add(other.get_bounds()[5])

                valid_levels = sorted(z for z in support_levels if z + h <= truck_height)

                x = rng.randint(0, truck_width - w)
                y = rng.randint(0, truck_length - l)
                z = rng.choice(valid_levels)

                cand_package = list(state.packages)
                cand_package[i] = oriented.place(x, y, z)

                candidate = cls(packages=tuple(cand_package), truck=truck,)

                if is_valid(candidate, check_fragile=False):
                    state = candidate
                    break
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "truck": self.truck.to_dict(),
            "packages": [p.to_dict() for p in self.packages],
            "total_value": self.total_value(),
            "total_weight": self.total_weight(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        return cls(
            packages=tuple(Package.from_dict(p) for p in data["packages"]),
            truck=Truck.from_dict(data["truck"]),
        )


def _relocate(package: Package, position: Optional[Tuple[int, int, int]]) -> Package:
    if position is None:
        return package.remove()
    return package.place(*position)