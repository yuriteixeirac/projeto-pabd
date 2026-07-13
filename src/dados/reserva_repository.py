from datetime import date
from typing import Optional

import sqlalchemy as sa
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
                    Quarto.valor.label("quarto_valor"),
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

    def listar_filtradas(
        self,
        data_checkin: date | None = None,
        data_checkout: date | None = None,
        status: str | None = None,
        cliente_id: int | None = None,
    ) -> list[dict[str, object]]:
        with self.session() as session:
            consulta = select(
                Reserva.id,
                Reserva.quarto_id,
                Quarto.codigo.label("quarto_codigo"),
                Quarto.valor.label("quarto_valor"),
                Reserva.usuario_id,
                Usuario.nome_completo.label("usuario_nome"),
                Reserva.cliente_id,
                Cliente.nome_completo.label("cliente_nome"),
                Reserva.data_checkin,
                Reserva.data_checkout,
                Reserva.status,
            ).join(Quarto, Quarto.id == Reserva.quarto_id
            ).join(Usuario, Usuario.id == Reserva.usuario_id
            ).join(Cliente, Cliente.id == Reserva.cliente_id)

            if data_checkin is not None:
                consulta = consulta.where(Reserva.data_checkin >= data_checkin)
            if data_checkout is not None:
                consulta = consulta.where(Reserva.data_checkout <= data_checkout)
            if status is not None and status != "":
                consulta = consulta.where(Reserva.status == status)
            if cliente_id is not None:
                consulta = consulta.where(Reserva.cliente_id == cliente_id)

            consulta = consulta.order_by(Reserva.data_checkin, Reserva.id)
            resultado = session.execute(consulta)
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

    def contar_ativas_por_periodo(self, data: date) -> int:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva.id).where(
                    Reserva.status.in_(["pendente", "confirmada"]),
                    Reserva.data_checkin <= data,
                    Reserva.data_checkout > data,
                )
            )
            return len(resultado.all())

    def contar_pendentes(self) -> int:
        with self.session() as session:
            resultado = session.execute(
                select(Reserva.id).where(Reserva.status == "pendente")
            )
            return len(resultado.all())

    def faturamento_mes(self, ano: int, mes: int) -> float:
        with self.session() as session:
            resultado = session.execute(
                select(Quarto.valor)
                .select_from(Reserva)
                .join(Quarto, Quarto.id == Reserva.quarto_id)
                .where(
                    Reserva.status.in_(["confirmada", "finalizada"]),
                    sa.extract("year", Reserva.data_checkin) == ano,
                    sa.extract("month", Reserva.data_checkin) == mes,
                )
            )
            total = 0.0
            for (valor,) in resultado:
                total += float(valor)
            return total

    def ultimas_reservas(self, limite: int = 5) -> list[dict[str, object]]:
        with self.session() as session:
            resultado = session.execute(
                select(
                    Reserva.id,
                    Cliente.nome_completo.label("cliente_nome"),
                    Quarto.codigo.label("quarto_codigo"),
                    Reserva.data_checkin,
                    Reserva.data_checkout,
                    Reserva.status,
                )
                .join(Quarto, Quarto.id == Reserva.quarto_id)
                .join(Cliente, Cliente.id == Reserva.cliente_id)
                .order_by(Reserva.id.desc())
                .limit(limite)
            )
            return [dict(linha._mapping) for linha in resultado]

    def proximos_checkins(self, dias: int = 7) -> list[dict[str, object]]:
        from datetime import timedelta
        hoje = date.today()
        with self.session() as session:
            resultado = session.execute(
                select(
                    Reserva.id,
                    Cliente.nome_completo.label("cliente_nome"),
                    Quarto.codigo.label("quarto_codigo"),
                    Reserva.data_checkin,
                    Reserva.data_checkout,
                    Reserva.status,
                )
                .join(Quarto, Quarto.id == Reserva.quarto_id)
                .join(Cliente, Cliente.id == Reserva.cliente_id)
                .where(
                    Reserva.status.in_(["pendente", "confirmada"]),
                    Reserva.data_checkin >= hoje,
                    Reserva.data_checkin <= hoje + timedelta(days=dias),
                )
                .order_by(Reserva.data_checkin)
            )
            return [dict(linha._mapping) for linha in resultado]

    def remover(self, id_reserva: int) -> bool:
        with self.session() as session:
            resultado = session.execute(
                delete(Reserva).where(Reserva.id == id_reserva)
            )
            session.commit()

            return resultado.rowcount > 0
