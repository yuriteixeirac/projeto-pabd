from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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
        tipo_banco: str = "mysql",
    ) -> sessionmaker[Session]:
        if tipo_banco != "mysql":
            raise ValueError(f"Tipo de banco nao suportado: {tipo_banco}")

        host=os.getenv("DB_HOST", "127.0.0.1")
        port=int(os.getenv("DB_PORTA", 3306))
        user=os.getenv("DB_USER", "root")
        password=os.getenv("DB_SENHA", "labinfo")
        database=os.getenv("DB_NOME", "aplicacao")

        DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(DATABASE_URL)
        session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

        return session_local
