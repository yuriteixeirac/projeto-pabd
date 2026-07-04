from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    raiz_projeto = Path(__file__).resolve().parents[1]
    if str(raiz_projeto) not in sys.path:
        sys.path.insert(0, str(raiz_projeto))

from src.dados.cliente_repository import ClienteRepository
from src.dados.conexao_singleton import ConexaoSingleton
from src.dados.quarto_repository import QuartoRepository
from src.dados.reserva_repository import ReservaRepository
from src.dados.usuario_repository import UsuarioRepository
from src.negocio.cliente_service import ClienteService
from src.negocio.quarto_service import QuartoService
from src.negocio.reserva_service import ReservaService
from src.negocio.usuario_service import UsuarioService


@dataclass
class ServicosAplicacao:
    usuario: UsuarioService
    cliente: ClienteService
    quarto: QuartoService
    reserva: ReservaService


def criar_servicos() -> ServicosAplicacao:
    conexao = ConexaoSingleton.obter_conexao()

    usuario_repository = UsuarioRepository(conexao)
    cliente_repository = ClienteRepository(conexao)
    quarto_repository = QuartoRepository(conexao)
    reserva_repository = ReservaRepository(conexao)

    return ServicosAplicacao(
        usuario=UsuarioService(usuario_repository),
        cliente=ClienteService(cliente_repository),
        quarto=QuartoService(quarto_repository, reserva_repository),
        reserva=ReservaService(
            reserva_repository, cliente_repository, quarto_repository
        ),
    )


def principal() -> None:
    try:
        servicos = criar_servicos()

        from src.apresentacao import executar_interface

        executar_interface(servicos)
    finally:
        ConexaoSingleton.fechar_conexao()


if __name__ == "__main__":
    principal()
