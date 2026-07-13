from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LoginFrame(ttk.Frame):
    def __init__(self, app: object) -> None:
        super().__init__(app, padding=32)
        self.app = app
        self.login_var = tk.StringVar()
        self.senha_var = tk.StringVar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        painel = ttk.Frame(self, padding=28)
        painel.grid(row=0, column=0)

        ttk.Label(painel, text="Hotel Tung Tung", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            painel, text="Entre para gerenciar reservas, clientes e quartos."
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        ttk.Label(painel, text="Login").grid(row=2, column=0, sticky="w")
        entrada_login = ttk.Entry(painel, textvariable=self.login_var, width=34)
        entrada_login.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 10))

        ttk.Label(painel, text="Senha").grid(row=4, column=0, sticky="w")
        entrada_senha = ttk.Entry(
            painel, textvariable=self.senha_var, show="*", width=34
        )
        entrada_senha.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(2, 16))
        entrada_senha.bind("<Return>", lambda _evento: self.entrar())

        ttk.Button(
            painel,
            text="Entrar",
            style="primary.TButton",
            command=self.entrar,
        ).grid(row=6, column=0, columnspan=2, sticky="ew")

        entrada_login.focus_set()

    def entrar(self) -> None:
        try:
            usuario = self.app.servicos.usuario.autenticar(
                self.login_var.get(), self.senha_var.get()
            )
        except Exception as erro:
            self.app.exibir_erro(erro)
            return

        if usuario is None:
            messagebox.showerror("Login", "Login ou senha invalidos.", parent=self)
            return

        self.senha_var.set("")
        self.app.abrir_sistema(usuario)
