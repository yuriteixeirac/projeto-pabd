from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    nome_completo: str
    cpf: str
    id: Optional[int] = None
