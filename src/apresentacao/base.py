from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.dominio import Usuario


class TelaBase(ttk.Frame):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(master, padding=12)
        self.app = app

    @property
    def usuario_atual(self) -> Usuario:
        usuario = self.app.usuario_atual
        if usuario is None:
            raise PermissionError("Usuario autenticado requerido.")
        return usuario

    def executar(self, acao: Callable[[], None]) -> None:
        try:
            acao()
        except Exception as erro:
            self.app.exibir_erro(erro)


class AcessoRestritoFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, titulo: str, mensagem: str) -> None:
        super().__init__(master, padding=24)
        ttk.Label(self, text=titulo, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text=mensagem).pack(anchor="w", pady=(8, 0))
