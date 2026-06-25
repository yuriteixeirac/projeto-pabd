from typing import Optional

import mysql.connector

from src.dominio import Quarto


class QuartoRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, quarto: Quarto) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO quarto (codigo, capacidade, valor) VALUES (%s, %s, %s)",
            (quarto.codigo, quarto.capacidade, quarto.valor),
        )
        self.conexao.commit()

        novo_id = int(cursor.lastrowid)
        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Quarto]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, codigo, capacidade, valor FROM quarto ORDER BY id"
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [
            Quarto(
                id=linha["id"],
                codigo=linha["codigo"],
                capacidade=linha["capacidade"],
                valor=linha["valor"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_quarto: int) -> Optional[Quarto]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, codigo, capacidade, valor FROM quarto WHERE id = %s",
            (id_quarto,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if linha is None:
            return None

        return Quarto(
            id=linha["id"],
            codigo=linha["codigo"],
            capacidade=linha["capacidade"],
            valor=linha["valor"],
        )

    def atualizar(self, quarto: Quarto) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE quarto SET codigo = %s, capacidade = %s, valor = %s WHERE id = %s",
            (quarto.codigo, quarto.capacidade, quarto.valor, quarto.id),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados

    def remover(self, id_quarto: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM quarto WHERE id = %s",
            (id_quarto,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados
