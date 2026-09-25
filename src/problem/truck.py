from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .package import Package


@dataclass(frozen=True)
class Truck:
    dimensions: Tuple[int, int, int] 
    max_capacity: int  

    def __post_init__(self) -> None:
        if len(self.dimensions) != 3 or min(self.dimensions) <= 0:
            raise ValueError("Dimensi truck harus 3 bilangan positif.")

        if self.max_capacity < 0:
            raise ValueError("Kapasitas truck harus >= 0.")

    @property
    def volume(self) -> int:
        w, l, h = self.dimensions
        return w * l * h

    def fit(self, size: Tuple[int, int, int]) -> bool:
        w, l, h = size
        truck_width, truck_length, truck_height = self.dimensions
        return w <= truck_width and l <= truck_length and h <= truck_height

    def contain(self, package: Package) -> bool:
        bounds = package.get_bounds()
        if bounds is None:
            return False

        x1, y1, z1, x2, y2, z2 = bounds
        truck_width, truck_length, truck_height = self.dimensions
        return x1 >= 0 and y1 >= 0 and z1 >= 0 and x2 <= truck_width and y2 <= truck_length and z2 <= truck_height

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Truck":
        dimensions = data["dimensions"]
        return cls(
            dimensions=(int(dimensions["w"]), int(dimensions["l"]), int(dimensions["h"])),
            max_capacity=data.get("max_capacity", data.get("maxCapacity")),
        )

    def to_dict(self) -> Dict[str, Any]:
        w, l, h = self.dimensions
        return {
            "dimensions": {"w": w, "l": l, "h": h},
            "max_capacity": self.max_capacity,
        }