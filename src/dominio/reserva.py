from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional


StatusReserva = Literal["pendente", "confirmada", "cancelada", "finalizada"]


@dataclass
class Reserva:
    quarto_id: int
    usuario_id: int
    cliente_id: int
    data_checkin: date
    data_checkout: date
    status: StatusReserva = "pendente"
    id: Optional[int] = None
