from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style

from src.apresentacao.login_frame import LoginFrame
from src.apresentacao.main_frame import MainFrame
from src.dominio import Usuario


def executar_interface(servicos: object) -> None:
    app = HotelApp(servicos)
    app.mainloop()


class HotelApp(tk.Tk):
    def __init__(self, servicos: object) -> None:
        super().__init__()
        self.servicos = servicos
        self.usuario_atual: Usuario | None = None
        self._frame_atual: ttk.Frame | None = None

        self.title("Hotel Tung Tung")
        self.geometry("1100x700")
        self.minsize(960, 620)
        self._configurar_estilo()
        self.mostrar_login()

    def _configurar_estilo(self) -> None:
        self.style = Style(theme="flatly")

        self.style.configure("Titulo.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Subtitulo.TLabel", font=("Helvetica", 11, "bold"))

        self.style.configure("Treeview", rowheight=28)
        self.style.map(
            "Treeview",
            background=[("selected", "#0d6efd")],
            foreground=[("selected", "white")],
        )

    def mostrar_login(self) -> None:
        self.usuario_atual = None
        self._trocar_frame(LoginFrame(self))

    def abrir_sistema(self, usuario: Usuario) -> None:
        self.usuario_atual = usuario
        self._trocar_frame(MainFrame(self))

    def sair(self) -> None:
        self.mostrar_login()

    def _trocar_frame(self, frame: ttk.Frame) -> None:
        if self._frame_atual is not None:
            self._frame_atual.destroy()

        self._frame_atual = frame
        self._frame_atual.pack(fill="both", expand=True)

    def exibir_erro(self, erro: Exception) -> None:
        titulo = "Acesso negado" if isinstance(erro, PermissionError) else "Erro"
        mensagem = str(erro) or "Nao foi possivel concluir a operacao."
        messagebox.showerror(titulo, mensagem, parent=self)
