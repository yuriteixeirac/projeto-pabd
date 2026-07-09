from collections.abc import Sequence
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import delete

from src.dominio import Usuario


class UsuarioRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, session: sessionmaker[Session]) -> None:
        self.session = session

    def adicionar(self, usuario: Usuario) -> int:
        with self.session() as session:
            session.add(usuario)
            session.commit()
            session.refresh(usuario)

            return usuario.id    # type: ignore

    def listar_todos(self) -> Sequence[Usuario]:
        with self.session() as session:
            resultado = session.execute(
                select(Usuario.id, Usuario.login, Usuario.nome_completo, Usuario.cargo)
                .order_by(Usuario.id)
            )

            return [
                Usuario(
                    id=linha.id,
                    login=linha.login,
                    nome_completo=linha.nome_completo,
                    cargo=linha.cargo,
                )
                for linha in resultado
            ]

    def buscar_por_id(self, id_usuario: int) -> Optional[Usuario]:
        with self.session() as session:
            resultado = session.execute(
                select(Usuario.id, Usuario.login, Usuario.nome_completo, Usuario.cargo)
                .where(Usuario.id == id_usuario)
            ).one_or_none()

            if resultado is None:
                return None

            return Usuario(
                id=resultado.id,
                login=resultado.login,
                nome_completo=resultado.nome_completo,
                cargo=resultado.cargo,
            )

    def buscar_por_login(self, login: str) -> Optional[Usuario]:
        with self.session() as session:
            resultado = session.execute(
                select(Usuario).where(Usuario.login == login)
            )

            return resultado.scalars().one_or_none()

    def atualizar(self, usuario: Usuario) -> bool:
        with self.session() as session:
            resultado = session.execute(
                select(Usuario).where(Usuario.id == usuario.id)
            ).scalars().one_or_none()

            if not resultado:
                return False

            resultado.nome_completo = usuario.nome_completo
            resultado.login = usuario.login
            resultado.cargo = usuario.cargo
            if usuario.senha is not None:
                resultado.senha = usuario.senha

            session.commit()
            return True

    def remover(self, id_usuario: int) -> bool:
        with self.session() as session:
            resultado = session.execute(
                delete(Usuario).where(Usuario.id == id_usuario)
            )
            session.commit()

            return resultado.rowcount > 0
