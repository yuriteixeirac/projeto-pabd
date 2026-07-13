from collections.abc import Sequence
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import delete, exists

from src.dominio import Quarto
from src.dominio.reserva import Reserva


class QuartoRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, session: sessionmaker[Session]) -> None:
        self.session = session

    def adicionar(self, quarto: Quarto) -> int:
        with self.session() as session:
            session.add(quarto)
            session.commit()
            session.refresh(quarto)

            return quarto.id    # type: ignore

    def listar_todos(self) -> Sequence[Quarto]:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto).order_by(Quarto.id)
            )

            return resultado.scalars().all()

    def buscar_por_id(self, id_quarto: int) -> Optional[Quarto]:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto).where(Quarto.id == id_quarto)
            )

            return resultado.scalars().one_or_none()

    def buscar_por_codigo(self, codigo: str) -> Optional[Quarto]:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto).where(Quarto.codigo == codigo)
            )

            return resultado.scalars().one_or_none()

    def listar_disponiveis(self, data_checkin: date, data_checkout: date) -> Sequence[Quarto]:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto)
                .where(
                    ~exists(
                        select(1)
                        .select_from(Reserva)
                        .where(
                            Reserva.quarto_id == Quarto.id,
                            Reserva.status.in_(["pendente", "confirmada"]),
                            Reserva.data_checkin < data_checkout,
                            Reserva.data_checkout > data_checkin,
                        )
                    )
                )
                .order_by(Quarto.codigo)
            )

            return resultado.scalars().all()

    def atualizar(self, quarto: Quarto) -> bool:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto).where(Quarto.id == quarto.id)
            ).scalars().one_or_none()

            if not resultado:
                return False

            resultado.codigo = quarto.codigo
            resultado.capacidade = quarto.capacidade
            resultado.valor = quarto.valor
            resultado.descricao = quarto.descricao
            resultado.tipo = quarto.tipo

            session.commit()
        return True

    def remover(self, id_quarto: int) -> bool:
        with self.session() as session:
            resultado = session.execute(
                delete(Quarto).where(Quarto.id == id_quarto)
            )
            session.commit()

            return resultado.rowcount > 0
