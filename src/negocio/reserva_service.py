from datetime import date

from sqlalchemy.exc import IntegrityError

from src.dados.cliente_repository import ClienteRepository
from src.dados.quarto_repository import QuartoRepository
from src.dados.reserva_repository import ReservaRepository
from src.dominio import Reserva, Usuario
from src.negocio.autorizacao import exigir_autenticado


class ReservaService:
    """Regras de negocio para reservas."""

    def __init__(
        self,
        repositorio: ReservaRepository,
        cliente_repository: ClienteRepository,
        quarto_repository: QuartoRepository,
    ) -> None:
        self.repositorio = repositorio
        self.cliente_repository = cliente_repository
        self.quarto_repository = quarto_repository

    def criar_reserva(
        self,
        cliente_id: int,
        quarto_id: int,
        data_checkin: date | str,
        data_checkout: date | str,
        usuario_atual: Usuario,
    ) -> Reserva:
        usuario = exigir_autenticado(usuario_atual)
        self._validar_id(cliente_id, "cliente")
        self._validar_id(quarto_id, "quarto")
        checkin, checkout = self._normalizar_periodo(data_checkin, data_checkout)

        if self.cliente_repository.buscar_por_id(cliente_id) is None:
            raise ValueError("Cliente nao encontrado.")
        if self.quarto_repository.buscar_por_id(quarto_id) is None:
            raise ValueError("Quarto nao encontrado.")
        if self.repositorio.existe_conflito(quarto_id, checkin, checkout):
            raise ValueError("Quarto indisponivel para o periodo informado.")

        reserva = Reserva(
            quarto_id=quarto_id,
            usuario_id=usuario.id,
            cliente_id=cliente_id,
            data_checkin=checkin,
            data_checkout=checkout,
            status="pendente",
        )

        try:
            reserva.id = self.repositorio.adicionar(reserva)
        except IntegrityError as erro:
            raise ValueError("Nao foi possivel cadastrar a reserva.") from erro

        return reserva

    def listar_reservas(self, usuario_atual: Usuario) -> list[dict[str, object]]:
        exigir_autenticado(usuario_atual)
        return self.repositorio.listar_detalhadas()

    def buscar_reserva_por_id(self, id_reserva: int, usuario_atual: Usuario) -> Reserva | None:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_reserva, "reserva")
        return self.repositorio.buscar_por_id(id_reserva)

    def confirmar_reserva(self, id_reserva: int, usuario_atual: Usuario) -> bool:
        exigir_autenticado(usuario_atual)
        reserva = self._obter_reserva_existente(id_reserva)

        if reserva.status != "pendente":
            raise ValueError("Apenas reservas pendentes podem ser confirmadas.")
        if self.repositorio.existe_conflito(
            reserva.quarto_id,
            reserva.data_checkin,
            reserva.data_checkout,
            reserva_ignorada_id=reserva.id,
        ):
            raise ValueError("Quarto indisponivel para confirmar esta reserva.")

        return self.repositorio.atualizar_status(id_reserva, "confirmada")

    def cancelar_reserva(self, id_reserva: int, usuario_atual: Usuario) -> bool:
        exigir_autenticado(usuario_atual)
        reserva = self._obter_reserva_existente(id_reserva)

        if reserva.status == "finalizada":
            raise ValueError("Reservas finalizadas nao podem ser canceladas.")
        if reserva.status == "cancelada":
            raise ValueError("Reserva ja esta cancelada.")

        return self.repositorio.atualizar_status(id_reserva, "cancelada")

    def finalizar_hospedagem(self, id_reserva: int, usuario_atual: Usuario) -> bool:
        exigir_autenticado(usuario_atual)
        reserva = self._obter_reserva_existente(id_reserva)

        if reserva.status != "confirmada":
            raise ValueError("Apenas reservas confirmadas podem ser finalizadas.")

        return self.repositorio.atualizar_status(id_reserva, "finalizada")

    def _obter_reserva_existente(self, id_reserva: int) -> Reserva:
        self._validar_id(id_reserva, "reserva")
        reserva = self.repositorio.buscar_por_id(id_reserva)
        if reserva is None:
            raise ValueError("Reserva nao encontrada.")
        return reserva

    @staticmethod
    def _validar_id(id_registro: int, nome_registro: str) -> None:
        if id_registro <= 0:
            raise ValueError(f"O ID do {nome_registro} deve ser um numero inteiro positivo.")

    @staticmethod
    def _normalizar_periodo(
        data_checkin: date | str, data_checkout: date | str
    ) -> tuple[date, date]:
        checkin = ReservaService._normalizar_data(data_checkin, "check-in")
        checkout = ReservaService._normalizar_data(data_checkout, "checkout")

        if checkout <= checkin:
            raise ValueError("A data de checkout deve ser posterior a data de check-in.")
        return checkin, checkout

    @staticmethod
    def _normalizar_data(valor: date | str, nome_campo: str) -> date:
        if isinstance(valor, date):
            return valor

        if isinstance(valor, str):
            try:
                return date.fromisoformat(valor.strip())
            except ValueError as erro:
                raise ValueError(
                    f"A data de {nome_campo} deve estar no formato AAAA-MM-DD."
                ) from erro

        raise ValueError(f"A data de {nome_campo} e invalida.")
