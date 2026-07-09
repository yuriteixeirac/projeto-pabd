from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from src.dados.conexao_factory import ConexaoFactory


class ConexaoSingleton:
    """
    Singleton responsavel por manter uma unica conexao ativa.

    A primeira chamada cria a conexao usando a Factory.
    As proximas chamadas reaproveitam a mesma conexao.
    """

    _conexao: Optional[sessionmaker[Session]] = None

    @classmethod
    def obter_conexao(
        cls, tipo_banco: str = "mysql"
    ) -> sessionmaker[Session]:
        if cls._conexao is None:
            cls._conexao = ConexaoFactory.criar_conexao(
                tipo_banco=tipo_banco,
            )
        return cls._conexao
