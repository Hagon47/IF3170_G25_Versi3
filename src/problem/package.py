from dataclasses import dataclass, replace
from typing import Any, ClassVar, Dict, List, Optional, Tuple

@dataclass(frozen=True)
class Package:
    id: str
    dimensions: Tuple[int, int, int] #(w,l,h)
    value: int
    weight: int
    is_fragile: bool
    eta: int
    
    position: Optional[Tuple[int, int, int]] = None  #(x,y,z)
    rotation: int = 0  

    ORIENTATIONS: ClassVar[List[Tuple[int, int, int]]] = [
        (0, 1, 2),  #(w,l,h) 
        (0, 2, 1),  #(w,h,l)
        (1, 0, 2),  #(l,w,h)
        (1, 2, 0),  #(l,h,w)
        (2, 0, 1),  #(h,w,l)
        (2, 1, 0),  #(h,l,w)
    ]

    ROTATION_SWAP: ClassVar[Dict[str, Tuple[int, int]]] = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}

    def __post_init__(self) -> None:
        if len(self.dimensions) != 3 or min(self.dimensions) <= 0:
            raise ValueError(f"Dimensi packet {self.id} harus 3 bilangan positif.")
        
        if not (0 <= self.rotation < len(self.ORIENTATIONS)):
            raise ValueError("Indeks orientasi harus bernilai antara 0 dan 5.")
        
        if self.position is not None and len(self.position) != 3:
            raise ValueError("Posisi harus (x,y,z).")
        
    @property
    def get_dimensions(self) -> Tuple[int, int, int]:
        currentDimension = self.dimensions
        mapping = self.ORIENTATIONS[self.rotation]
        return (currentDimension[mapping[0]], currentDimension[mapping[1]], currentDimension[mapping[2]])

    def get_bounds(self) -> Optional[Tuple[int, int, int, int, int, int]]:
        if not self.is_placed:
            return None
        
        x, y, z = self.position
        w, l, h = self.get_dimensions
        return (x, y, z, x + w, y + l, z + h)

    def get_rotation(self, idx: int) -> "Package":
        return replace(self, rotation=idx)
    
    @property
    def is_placed(self) -> bool:
        return self.position is not None

    @property
    def volume(self) -> int:
        w, l, h = self.dimensions
        return w * l * h

    def get_orientation(self) -> Dict[str, str]:
        label = {}
        for axis_idx, dim_idx in enumerate(self.ORIENTATIONS[self.rotation]):
            label["wlh"[dim_idx]] = "xyz"[axis_idx]
            
        return {k: label[k] for k in "wlh"}

    def place(self, x: int, y: int, z: int) -> "Package":
        return replace(self, position=(int(x), int(y), int(z)))

    def remove(self) -> "Package":
        return replace(self, position=None)

    def rotate(self, axis: str) -> "Package":
        if axis not in self.ROTATION_SWAP:
            raise ValueError(f"Sumbu tidak valid: {axis!r} (pilih 'x', 'y', atau 'z')")
        
        mapping = list(self.ORIENTATIONS[self.rotation])
        a, b = self.ROTATION_SWAP[axis]
        mapping[a], mapping[b] = mapping[b], mapping[a]
        return replace(self, rotation=self.ORIENTATIONS.index(tuple(mapping)))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Package":
        dimensions = data["dimensions"]
        position = data.get("position")
        return cls(
            id=str(data["id"]),
            dimensions=(int(dimensions["w"]), int(dimensions["l"]), int(dimensions["h"])),
            value=data["value"],
            weight=data["weight"],
            is_fragile=bool(data.get("is_fragile", data.get("isFragile", False))),
            eta=int(data.get("eta", data.get("ETA", 0))),
            position=tuple(position) if position is not None else None,
            rotation=int(data.get("rotation", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        w, l, h = self.dimensions
        return {
            "id": self.id,
            "dimensions": {"w": w, "l": l, "h": h},
            "value": self.value,
            "weight": self.weight,
            "is_fragile": self.is_fragile,
            "eta": self.eta,
            "position": list(self.position) if self.position else None,
            "rotation": self.rotation,
            "orientation": self.get_orientation(),
        }
