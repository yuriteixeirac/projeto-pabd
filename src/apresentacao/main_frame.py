from __future__ import annotations

from tkinter import ttk

from src.apresentacao.base import AcessoRestritoFrame
from src.apresentacao.cliente_frame import ClienteFrame
from src.apresentacao.quarto_frame import QuartoFrame
from src.apresentacao.reserva_frame import ReservaFrame
from src.apresentacao.usuario_frame import UsuarioFrame


class MainFrame(ttk.Frame):
    def __init__(self, app: object) -> None:
        super().__init__(app, padding=12)
        self.app = app

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cabecalho = ttk.Frame(self)
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        cabecalho.grid_columnconfigure(0, weight=1)

        usuario = self.app.usuario_atual
        nome_usuario = usuario.nome_completo if usuario else "Usuario"
        cargo = usuario.cargo if usuario else "sem cargo"

        ttk.Label(
            cabecalho,
            text="Sistema de Administracao de Hotel",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(cabecalho, text=f"Logado como {nome_usuario} ({cargo})").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Button(cabecalho, text="Sair", command=self.app.sair).grid(
            row=0, column=1, rowspan=2, sticky="e"
        )

        abas = ttk.Notebook(self)
        abas.grid(row=1, column=0, sticky="nsew")

        abas.add(ClienteFrame(self.app, abas), text="Clientes")
        abas.add(QuartoFrame(self.app, abas), text="Quartos")
        abas.add(ReservaFrame(self.app, abas), text="Reservas")

        if usuario and usuario.cargo == "admin":
            abas.add(UsuarioFrame(self.app, abas), text="Usuarios")
        else:
            abas.add(
                AcessoRestritoFrame(
                    abas,
                    "Usuarios",
                    "Somente administradores podem gerenciar usuarios.",
                ),
                text="Usuarios",
            )
