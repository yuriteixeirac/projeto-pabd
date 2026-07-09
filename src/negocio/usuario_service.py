import hashlib
from typing import Optional

from sqlalchemy.exc import IntegrityError

from src.dados.usuario_repository import UsuarioRepository
from src.dominio import Usuario
from src.negocio.autorizacao import exigir_admin


class UsuarioService:
    """Regras de negocio para usuarios e autenticacao."""

    def __init__(self, repositorio: UsuarioRepository) -> None:
        self.repositorio = repositorio

    def autenticar(self, login: str, senha: str) -> Optional[Usuario]:
        login_normalizado = login.strip()
        if not login_normalizado or not senha:
            return None

        usuario = self.repositorio.buscar_por_login(login_normalizado)
        if usuario is None or usuario.senha != self._gerar_hash_senha(senha):
            return None

        usuario.senha = None
        return usuario

    def cadastrar_usuario(
        self,
        login: str,
        senha: str,
        nome_completo: str,
        cargo: str,
        usuario_atual: Usuario,
    ) -> Usuario:
        exigir_admin(usuario_atual)
        usuario = Usuario(
            login=self._normalizar_login(login),
            senha=self._normalizar_senha(senha),
            nome_completo=self._normalizar_nome(nome_completo),
            cargo=self._normalizar_cargo(cargo),
        )

        try:
            usuario.id = self.repositorio.adicionar(usuario)
        except IntegrityError as erro:
            raise ValueError("Login ja cadastrado.") from erro

        usuario.senha = None
        return usuario

    def listar_usuarios(self, usuario_atual: Usuario) -> list[Usuario]:
        exigir_admin(usuario_atual)
        return self.repositorio.listar_todos()

    def buscar_usuario_por_id(
        self, id_usuario: int, usuario_atual: Usuario
    ) -> Optional[Usuario]:
        exigir_admin(usuario_atual)
        self._validar_id(id_usuario)
        return self.repositorio.buscar_por_id(id_usuario)

    def atualizar_usuario(
        self,
        id_usuario: int,
        login: str,
        nome_completo: str,
        cargo: str,
        usuario_atual: Usuario,
        senha: Optional[str] = None,
    ) -> bool:
        exigir_admin(usuario_atual)
        self._validar_id(id_usuario)

        usuario = Usuario(
            id=id_usuario,
            login=self._normalizar_login(login),
            nome_completo=self._normalizar_nome(nome_completo),
            cargo=self._normalizar_cargo(cargo),
            senha=self._normalizar_senha(senha) if senha else None,
        )

        try:
            return self.repositorio.atualizar(usuario)
        except IntegrityError as erro:
            raise ValueError("Login ja cadastrado.") from erro

    def remover_usuario(self, id_usuario: int, usuario_atual: Usuario) -> bool:
        exigir_admin(usuario_atual)
        self._validar_id(id_usuario)

        try:
            return self.repositorio.remover(id_usuario)
        except IntegrityError as erro:
            raise ValueError("Usuario possui reservas vinculadas e nao pode ser removido.") from erro

    @staticmethod
    def _validar_id(id_usuario: int) -> None:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

    @staticmethod
    def _normalizar_login(login: str) -> str:
        login_normalizado = login.strip()
        if not login_normalizado:
            raise ValueError("O login nao pode ficar vazio.")
        return login_normalizado

    @staticmethod
    def _normalizar_nome(nome_completo: str) -> str:
        nome = nome_completo.strip()
        if not nome:
            raise ValueError("O nome completo nao pode ficar vazio.")
        return nome

    @staticmethod
    def _normalizar_cargo(cargo: str) -> str:
        if cargo not in ("admin", "atendente"):
            raise ValueError("O cargo deve ser admin ou atendente.")
        return cargo

    @staticmethod
    def _normalizar_senha(senha: str) -> str:
        if not senha:
            raise ValueError("A senha nao pode ficar vazia.")
        return UsuarioService._gerar_hash_senha(senha)

    @staticmethod
    def _gerar_hash_senha(senha: str) -> str:
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()
