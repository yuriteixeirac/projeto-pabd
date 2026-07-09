from collections.abc import Sequence
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import delete

from src.dominio import Cliente


class ClienteRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, session: sessionmaker[Session]) -> None:
        self.session = session

    def adicionar(self, cliente: Cliente) -> int:
        with self.session() as session:
            session.add(cliente)
            session.commit()
            session.refresh(cliente)

            return cliente.id    # type: ignore

    def listar_todos(self) -> Sequence[Cliente]:
        with self.session() as session:
            resultado = session.execute(
                select(Cliente).order_by(Cliente.id)
            )

            return resultado.scalars().all()

    def buscar_por_id(self, id_cliente: int) -> Optional[Cliente]:
        with self.session() as session:
            resultado = session.execute(
                select(Cliente).where(Cliente.id == id_cliente)
            )

            return resultado.scalars().one_or_none()

    def buscar_por_cpf(self, cpf: str) -> Optional[Cliente]:
        with self.session() as session:
            resultado = session.execute(
                select(Cliente).where(Cliente.cpf == cpf)
            )

            return resultado.scalars().one_or_none()

    def atualizar(self, cliente: Cliente) -> bool:
        with self.session() as session:
            resultado = session.execute(
                select(Cliente).where(Cliente.id == cliente.id)
            ).scalars().one_or_none()

            if not resultado:
                return False

            resultado.nome_completo = cliente.nome_completo
            resultado.cpf = cliente.cpf

            session.commit()
            return True

    def remover(self, id_cliente: int) -> bool:
        with self.session() as session:
            resultado = session.execute(
                delete(Cliente).where(Cliente.id == id_cliente)
            )
            session.commit()

            return resultado.rowcount > 0
