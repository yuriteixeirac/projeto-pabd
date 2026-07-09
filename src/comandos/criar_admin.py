from __future__ import annotations

import hashlib
import sys
from pathlib import Path

if __package__ in (None, ""):
    raiz_projeto = Path(__file__).resolve().parents[2]
    if str(raiz_projeto) not in sys.path:
        sys.path.insert(0, str(raiz_projeto))

from src.dados.conexao_factory import ConexaoFactory
from src.dados.usuario_repository import UsuarioRepository
from src.dominio import Usuario


def criar_admin():
    session = ConexaoFactory.criar_conexao()
    user_repository = UsuarioRepository(session)

    print("Insira os dados do usuário abaixo")

    login = input("Login: ")
    senha = input("Senha: ")
    nome_completo = input("Nome completo: ")

    usuario = Usuario(
        login=login,
        senha=hashlib.sha256(senha.encode("utf-8")).hexdigest(),
        nome_completo=nome_completo,
        cargo="admin"
    )

    try:
        user_repository.adicionar(usuario)
    except Exception:
        print("Erro de integridade. Use outro login.")
        return

    print("Usuário criado com sucesso!")


if __name__ == "__main__":
    criar_admin()
