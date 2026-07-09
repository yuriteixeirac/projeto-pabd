from datetime import date, datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from src.dominio.base import Base


class Reserva(Base):
    __tablename__ = "reserva"

    id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), primary_key=True)
    quarto_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("quarto.id"))
    usuario_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("usuario.id"))
    cliente_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("cliente.id"))
    data_checkin: so.Mapped[date] = so.mapped_column(sa.Date(), default=lambda: datetime.now().date())
    data_checkout: so.Mapped[date] = so.mapped_column(sa.Date())
    status: so.Mapped[str] = so.mapped_column(sa.Enum(*["pendente", "confirmada", "cancelada", "finalizada"]))

    quarto: so.Mapped["Quarto"] = so.relationship("Quarto")
    usuario: so.Mapped["Usuario"] = so.relationship("Usuario")
    cliente: so.Mapped["Cliente"] = so.relationship("Cliente")
