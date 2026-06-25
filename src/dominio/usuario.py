from dataclasses import dataclass
from typing import Literal, Optional

Cargo = Literal["admin", "atendente"]


@dataclass
class Usuario:
    login: str
    nome_completo: str
    cargo: Cargo
    id: Optional[int] = None
    senha: Optional[str] = None
