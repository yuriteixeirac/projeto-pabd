from __future__ import annotations

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class ConexaoFactory:
    """
    Factory responsavel por criar conexoes.

    Neste exemplo, deixamos a criacao concentrada em um unico lugar.
    Se no futuro a aplicacao trocar de MySQL para outro banco,
    a mudanca comeca por aqui.
    """

    @staticmethod
    def criar_conexao(
        tipo_banco: str = "mysql", **configuracao
    ) -> mysql.connector.MySQLConnection:
        if tipo_banco != "mysql":
            raise ValueError(f"Tipo de banco nao suportado: {tipo_banco}")

        conexao = mysql.connector.connect(
            host=configuracao.get("host", "localhost"),
            port=int(configuracao.get("porta", 3306)),
            user=configuracao.get("usuario", os.getenv("DB_USER")),
            password=configuracao.get("senha", os.getenv("DB_SENHA")),
            database=configuracao.get("banco", "tung_tung"),
        )
        return conexao
