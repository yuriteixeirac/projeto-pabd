from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError

from src.dados.quarto_repository import QuartoRepository
from src.dados.reserva_repository import ReservaRepository
from src.dominio import Quarto, Usuario
from src.negocio.autorizacao import exigir_admin, exigir_autenticado


class QuartoService:
    """Regras de negocio para quartos."""

    def __init__(
        self,
        repositorio: QuartoRepository,
        reserva_repository: ReservaRepository,
    ) -> None:
        self.repositorio = repositorio
        self.reserva_repository = reserva_repository

    def cadastrar_quarto(
        self,
        codigo: str,
        capacidade: int,
        valor: Decimal | str | float,
        usuario_atual: Usuario,
    ) -> Quarto:
        exigir_admin(usuario_atual)
        quarto = Quarto(
            codigo=self._normalizar_codigo(codigo),
            capacidade=self._normalizar_capacidade(capacidade),
            valor=self._normalizar_valor(valor),
        )

        try:
            quarto.id = self.repositorio.adicionar(quarto)
        except IntegrityError as erro:
            raise ValueError("Codigo de quarto ja cadastrado.") from erro

        return quarto

    def listar_quartos(self, usuario_atual: Usuario) -> list[Quarto]:
        exigir_autenticado(usuario_atual)
        return self.repositorio.listar_todos()

    def listar_quartos_disponiveis(
        self,
        data_checkin: date | str,
        data_checkout: date | str,
        usuario_atual: Usuario,
    ) -> list[Quarto]:
        exigir_autenticado(usuario_atual)
        checkin, checkout = self._normalizar_periodo(data_checkin, data_checkout)
        return self.repositorio.listar_disponiveis(checkin, checkout)

    def buscar_quarto_por_id(self, id_quarto: int, usuario_atual: Usuario) -> Quarto | None:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_quarto)
        return self.repositorio.buscar_por_id(id_quarto)

    def atualizar_quarto(
        self,
        id_quarto: int,
        codigo: str,
        capacidade: int,
        valor: Decimal | str | float,
        usuario_atual: Usuario,
    ) -> bool:
        exigir_admin(usuario_atual)
        self._validar_id(id_quarto)

        quarto = Quarto(
            id=id_quarto,
            codigo=self._normalizar_codigo(codigo),
            capacidade=self._normalizar_capacidade(capacidade),
            valor=self._normalizar_valor(valor),
        )

        try:
            return self.repositorio.atualizar(quarto)
        except IntegrityError as erro:
            raise ValueError("Codigo de quarto ja cadastrado.") from erro

    def remover_quarto(self, id_quarto: int, usuario_atual: Usuario) -> bool:
        exigir_admin(usuario_atual)
        self._validar_id(id_quarto)

        try:
            return self.repositorio.remover(id_quarto)
        except IntegrityError as erro:
            raise ValueError("Quarto possui reservas vinculadas e nao pode ser removido.") from erro

    def quarto_disponivel(
        self,
        id_quarto: int,
        data_checkin: date | str,
        data_checkout: date | str,
        usuario_atual: Usuario,
    ) -> bool:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_quarto)
        checkin, checkout = self._normalizar_periodo(data_checkin, data_checkout)
        return not self.reserva_repository.existe_conflito(id_quarto, checkin, checkout)

    @staticmethod
    def _validar_id(id_registro: int) -> None:
        if id_registro <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

    @staticmethod
    def _normalizar_codigo(codigo: str) -> str:
        codigo_normalizado = codigo.strip().upper()
        if not codigo_normalizado:
            raise ValueError("O codigo do quarto nao pode ficar vazio.")
        if len(codigo_normalizado) > 4:
            raise ValueError("O codigo do quarto deve ter no maximo 4 caracteres.")
        return codigo_normalizado

    @staticmethod
    def _normalizar_capacidade(capacidade: int) -> int:
        capacidade_normalizada = int(capacidade)
        if capacidade_normalizada <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        return capacidade_normalizada

    @staticmethod
    def _normalizar_valor(valor: Decimal | str | float) -> Decimal:
        try:
            valor_normalizado = Decimal(str(valor).strip().replace(",", "."))
        except InvalidOperation as erro:
            raise ValueError("O valor do quarto deve ser numerico.") from erro

        if valor_normalizado < 0:
            raise ValueError("O valor do quarto nao pode ser negativo.")
        return valor_normalizado

    @staticmethod
    def _normalizar_periodo(
        data_checkin: date | str, data_checkout: date | str
    ) -> tuple[date, date]:
        checkin = QuartoService._normalizar_data(data_checkin, "check-in")
        checkout = QuartoService._normalizar_data(data_checkout, "checkout")

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
