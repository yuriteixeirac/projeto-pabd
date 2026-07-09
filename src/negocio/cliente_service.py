from typing import Optional

from sqlalchemy.exc import IntegrityError

from src.dados.cliente_repository import ClienteRepository
from src.dominio import Cliente, Usuario
from src.negocio.autorizacao import exigir_autenticado


class ClienteService:
    """Regras de negocio para clientes."""

    def __init__(self, repositorio: ClienteRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_cliente(
        self, nome_completo: str, cpf: str, usuario_atual: Usuario
    ) -> Cliente:
        exigir_autenticado(usuario_atual)
        cliente = Cliente(
            nome_completo=self._normalizar_nome(nome_completo),
            cpf=self._normalizar_cpf(cpf),
        )

        try:
            cliente.id = self.repositorio.adicionar(cliente)
        except IntegrityError as erro:
            raise ValueError("CPF ja cadastrado.") from erro

        return cliente

    def listar_clientes(self, usuario_atual: Usuario) -> list[Cliente]:
        exigir_autenticado(usuario_atual)
        return self.repositorio.listar_todos()

    def buscar_cliente_por_id(
        self, id_cliente: int, usuario_atual: Usuario
    ) -> Optional[Cliente]:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_cliente)
        return self.repositorio.buscar_por_id(id_cliente)

    def atualizar_cliente(
        self, id_cliente: int, nome_completo: str, cpf: str, usuario_atual: Usuario
    ) -> bool:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_cliente)

        cliente = Cliente(
            id=id_cliente,
            nome_completo=self._normalizar_nome(nome_completo),
            cpf=self._normalizar_cpf(cpf),
        )

        try:
            return self.repositorio.atualizar(cliente)
        except IntegrityError as erro:
            raise ValueError("CPF ja cadastrado.") from erro

    def remover_cliente(self, id_cliente: int, usuario_atual: Usuario) -> bool:
        exigir_autenticado(usuario_atual)
        self._validar_id(id_cliente)

        try:
            return self.repositorio.remover(id_cliente)
        except IntegrityError as erro:
            raise ValueError("Cliente possui reservas vinculadas e nao pode ser removido.") from erro

    @staticmethod
    def _validar_id(id_registro: int) -> None:
        if id_registro <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

    @staticmethod
    def _normalizar_nome(nome_completo: str) -> str:
        nome = nome_completo.strip()
        if not nome:
            raise ValueError("O nome completo nao pode ficar vazio.")
        return nome

    @staticmethod
    def _normalizar_cpf(cpf: str) -> str:
        cpf_normalizado = "".join(caractere for caractere in cpf if caractere.isdigit())
        if len(cpf_normalizado) != 11:
            raise ValueError("O CPF deve conter 11 digitos.")
        return cpf_normalizado
