from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from src.dominio.base import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), primary_key=True)
    nome_completo: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    cpf: so.Mapped[str] = so.mapped_column(sa.String(11), unique=True, nullable=False)
