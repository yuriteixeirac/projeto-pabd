from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import delete

from src.dominio import Cliente, Quarto, Reserva, Usuario


class ReservaRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, session: sessionmaker[Session]) -> None:
        self.session = session

    def adicionar(self, reserva: Reserva) -> int:
        with self.session() as session:
            session.add(reserva)
            session.commit()
            session.refresh(reserva)

            return reserva.id    # type: ignore

    def listar_todos(self) -> list[Reserva]:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva).order_by(Reserva.data_checkin, Reserva.id)
            )

            return resultado.scalars().all()

    def listar_detalhadas(self) -> list[dict[str, object]]:
        with self.session() as session:
            resultado = session.execute(
                select(
                    Reserva.id,
                    Reserva.quarto_id,
                    Quarto.codigo.label("quarto_codigo"),
                    Reserva.usuario_id,
                    Usuario.nome_completo.label("usuario_nome"),
                    Reserva.cliente_id,
                    Cliente.nome_completo.label("cliente_nome"),
                    Reserva.data_checkin,
                    Reserva.data_checkout,
                    Reserva.status,
                )
                .join(Quarto, Quarto.id == Reserva.quarto_id)
                .join(Usuario, Usuario.id == Reserva.usuario_id)
                .join(Cliente, Cliente.id == Reserva.cliente_id)
                .order_by(Reserva.data_checkin, Reserva.id)
            )

            return [dict(linha._mapping) for linha in resultado]

    def buscar_por_id(self, id_reserva: int) -> Optional[Reserva]:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva).where(Reserva.id == id_reserva)
            )

            return resultado.scalars().one_or_none()

    def existe_conflito(
        self,
        quarto_id: int,
        data_checkin: date,
        data_checkout: date,
        reserva_ignorada_id: Optional[int] = None,
    ) -> bool:
        with self.session() as session:
            consulta = select(Reserva.id).where(
                Reserva.quarto_id == quarto_id,
                Reserva.status.in_(["pendente", "confirmada"]),
                Reserva.data_checkin < data_checkout,
                Reserva.data_checkout > data_checkin,
            )

            if reserva_ignorada_id is not None:
                consulta = consulta.where(Reserva.id != reserva_ignorada_id)

            resultado = session.execute(consulta.limit(1))

            return resultado.scalar_one_or_none() is not None

    def atualizar_status(self, id_reserva: int, status: str) -> bool:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva).where(Reserva.id == id_reserva)
            ).scalars().one_or_none()

            if not resultado:
                return False

            resultado.status = status
            session.commit()
            return True

    def atualizar(self, reserva: Reserva) -> bool:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva).where(Reserva.id == reserva.id)
            ).scalars().one_or_none()

            if not resultado:
                return False

            resultado.quarto_id = reserva.quarto_id
            resultado.usuario_id = reserva.usuario_id
            resultado.cliente_id = reserva.cliente_id
            resultado.data_checkin = reserva.data_checkin
            resultado.data_checkout = reserva.data_checkout
            resultado.status = reserva.status

            session.commit()
            return True

    def remover(self, id_reserva: int) -> bool:
        with self.session() as session:
            resultado = session.execute(
                delete(Reserva).where(Reserva.id == id_reserva)
            )
            session.commit()

            return resultado.rowcount > 0
