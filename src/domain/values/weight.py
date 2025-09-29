from dataclasses import dataclass


@dataclass(frozen=True)
class Weight:
    weight: int

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError("weight must be positive")
