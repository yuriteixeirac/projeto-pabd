from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Quarto:
    codigo: str
    capacidade: int
    valor: Decimal
    id: Optional[int] = None
