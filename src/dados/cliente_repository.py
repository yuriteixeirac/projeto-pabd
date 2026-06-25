from typing import Optional

import mysql.connector

from src.dominio import Cliente


class ClienteRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, cliente: Cliente) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO cliente (nome_completo, cpf) VALUES (%s, %s)",
            (cliente.nome_completo, cliente.cpf),
        )
        self.conexao.commit()

        novo_id = int(cursor.lastrowid)
        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Cliente]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome_completo, cpf FROM cliente ORDER BY id"
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [
            Cliente(
                id=linha["id"],
                nome_completo=linha["nome_completo"],
                cpf=linha["cpf"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_cliente: int) -> Optional[Cliente]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome_completo, cpf FROM cliente WHERE id = %s",
            (id_cliente,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if linha is None:
            return None

        return Cliente(
            id=linha["id"],
            nome_completo=linha["nome_completo"],
            cpf=linha["cpf"],
        )

    def atualizar(self, cliente: Cliente) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE cliente SET nome_completo = %s, cpf = %s WHERE id = %s",
            (cliente.nome_completo, cliente.cpf, cliente.id),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados

    def remover(self, id_cliente: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM cliente WHERE id = %s",
            (id_cliente,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados
