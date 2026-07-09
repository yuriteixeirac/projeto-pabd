from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from src.dominio.base import Base


class Quarto(Base):
    __tablename__ = "quarto"

    id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), primary_key=True)
    codigo: so.Mapped[str] = so.mapped_column(sa.String(16), unique=True)
    capacidade: so.Mapped[int] = so.mapped_column(sa.Integer())
    valor: so.Mapped[Decimal] = so.mapped_column(sa.DECIMAL(10, 2))
