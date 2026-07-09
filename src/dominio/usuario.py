from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from src.dominio.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), primary_key=True)
    login: so.Mapped[str] = so.mapped_column(sa.String(256), unique=True, nullable=False)
    senha: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False)

    nome_completo: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    cargo: so.Mapped[str] = so.mapped_column(sa.Enum("admin", "atendente"))
