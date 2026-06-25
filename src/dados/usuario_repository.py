from typing import Optional

import mysql.connector

from src.dominio import Usuario


class UsuarioRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, usuario: Usuario) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO usuario (login, senha, nome_completo, cargo) VALUES (%s, %s, %s, %s)",
            (usuario.login, usuario.senha, usuario.nome_completo, usuario.cargo),
        )
        self.conexao.commit()

        novo_id = int(cursor.lastrowid)
        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Usuario]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, login, nome_completo, cargo FROM usuario ORDER BY id"
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [
            Usuario(
                id=linha["id"],
                login=linha["login"],
                nome_completo=linha["nome_completo"],
                cargo=linha["cargo"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_usuario: int) -> Optional[Usuario]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, login, nome_completo, cargo FROM usuario WHERE id = %s",
            (id_usuario,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if linha is None:
            return None

        return Usuario(
            id=linha["id"],
            nome_completo=linha["nome_completo"],
            login=linha["login"],
            cargo=linha["cargo"],
        )

    def atualizar(self, usuario: Usuario) -> bool:
        cursor = self.conexao.cursor()
        if usuario.senha is None:
            cursor.execute(
                "UPDATE usuario SET nome_completo = %s, login = %s, cargo = %s WHERE id = %s",
                (
                    usuario.nome_completo,
                    usuario.login,
                    usuario.cargo,
                    usuario.id,
                ),
            )
        else:
            cursor.execute(
                "UPDATE usuario SET nome_completo = %s, login = %s, cargo = %s, senha = %s WHERE id = %s",
                (
                    usuario.nome_completo,
                    usuario.login,
                    usuario.cargo,
                    usuario.senha,
                    usuario.id,
                ),
            )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados

    def remover(self, id_usuario: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM usuario WHERE id = %s",
            (id_usuario,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados
