from typing import Optional

import mysql.connector

from src.dominio import Reserva


class ReservaRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, reserva: Reserva) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO reserva (quarto_id, usuario_id, cliente_id, data_checkin, data_checkout, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                reserva.quarto_id,
                reserva.usuario_id,
                reserva.cliente_id,
                reserva.data_checkin,
                reserva.data_checkout,
                reserva.status,
            ),
        )
        self.conexao.commit()

        novo_id = int(cursor.lastrowid)
        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Reserva]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, quarto_id, usuario_id, cliente_id, data_checkin, data_checkout, status FROM reserva ORDER BY id"
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [
            Reserva(
                id=linha["id"],
                quarto_id=linha["quarto_id"],
                usuario_id=linha["usuario_id"],
                cliente_id=linha["cliente_id"],
                data_checkin=linha["data_checkin"],
                data_checkout=linha["data_checkout"],
                status=linha["status"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_reserva: int) -> Optional[Reserva]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, quarto_id, usuario_id, cliente_id, data_checkin, data_checkout, status FROM reserva WHERE id = %s",
            (id_reserva,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if linha is None:
            return None

        return Reserva(
            id=linha["id"],
            quarto_id=linha["quarto_id"],
            usuario_id=linha["usuario_id"],
            cliente_id=linha["cliente_id"],
            data_checkin=linha["data_checkin"],
            data_checkout=linha["data_checkout"],
            status=linha["status"],
        )

    def atualizar(self, reserva: Reserva) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE reserva SET quarto_id = %s, usuario_id = %s, cliente_id = %s, data_checkin = %s, data_checkout = %s, status = %s WHERE id = %s",
            (
                reserva.quarto_id,
                reserva.usuario_id,
                reserva.cliente_id,
                reserva.data_checkin,
                reserva.data_checkout,
                reserva.status,
                reserva.id,
            ),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados

    def remover(self, id_reserva: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM reserva WHERE id = %s",
            (id_reserva,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0
        cursor.close()

        return afetados
