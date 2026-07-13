from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from src.apresentacao.base import TelaBase
from src.apresentacao.widgets import (
    criar_tabela,
    limpar_selecao,
    limpar_tabela,
    obter_item_selecionado,
)


class UsuarioFrame(TelaBase):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(app, master)
        self.usuario_id: int | None = None
        self.login_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.cargo_var = tk.StringVar(value="atendente")
        self.senha_var = tk.StringVar()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Usuarios", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        tabela_frame, self.tabela = criar_tabela(
            self,
            [
                ("id", "ID", 70, "center"),
                ("login", "Login", 160, "w"),
                ("nome", "Nome completo", 260, "w"),
                ("cargo", "Cargo", 120, "center"),
            ],
        )
        tabela_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.tabela.bind("<<TreeviewSelect>>", lambda _evento: self._selecionar())

        formulario = ttk.LabelFrame(self, text="Cadastro")
        formulario.grid(row=1, column=1, sticky="nsew")
        formulario.grid_columnconfigure(0, weight=1)

        ttk.Label(formulario, text="Login").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.login_var).grid(
            row=1, column=0, sticky="ew", pady=(2, 10)
        )
        ttk.Label(formulario, text="Nome completo").grid(row=2, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.nome_var).grid(
            row=3, column=0, sticky="ew", pady=(2, 10)
        )
        ttk.Label(formulario, text="Cargo").grid(row=4, column=0, sticky="w")
        ttk.Combobox(
            formulario,
            textvariable=self.cargo_var,
            values=("admin", "atendente"),
            state="readonly",
        ).grid(row=5, column=0, sticky="ew", pady=(2, 10))
        ttk.Label(formulario, text="Senha").grid(row=6, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.senha_var, show="*").grid(
            row=7, column=0, sticky="ew", pady=(2, 4)
        )
        ttk.Label(
            formulario,
                text="Obrigatoria para novo usuario. Em edicoes, deixe em branco para manter.",
            style="secondary.TLabel",
            wraplength=240,
        ).grid(row=8, column=0, sticky="w", pady=(0, 12))

        ttk.Button(
            formulario,
            text="Salvar",
            style="success.TButton",
            command=lambda: self.executar(self.salvar),
        ).grid(row=9, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(formulario, text="Novo", style="secondary.TButton", command=self.limpar).grid(
            row=10, column=0, sticky="ew", pady=(0, 6)
        )
        ttk.Button(
            formulario,
            text="Remover",
            style="danger.TButton",
            command=lambda: self.executar(self.remover),
        ).grid(row=11, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Recarregar",
            style="secondary.TButton",
            command=lambda: self.executar(self.recarregar),
        ).grid(row=12, column=0, sticky="ew")

        self.executar(self.recarregar)

    def recarregar(self) -> None:
        limpar_tabela(self.tabela)
        for usuario in self.app.servicos.usuario.listar_usuarios(self.usuario_atual):
            self.tabela.insert(
                "",
                "end",
                iid=str(usuario.id),
                values=(
                    usuario.id,
                    usuario.login,
                    usuario.nome_completo,
                    usuario.cargo,
                ),
            )

    def _selecionar(self) -> None:
        selecionado = obter_item_selecionado(self.tabela)
        if selecionado is None:
            return

        self.usuario_id = int(selecionado[0])
        self.login_var.set(selecionado[1])
        self.nome_var.set(selecionado[2])
        self.cargo_var.set(selecionado[3])
        self.senha_var.set("")

    def salvar(self) -> None:
        if self.usuario_id is None:
            self.app.servicos.usuario.cadastrar_usuario(
                self.login_var.get(),
                self.senha_var.get(),
                self.nome_var.get(),
                self.cargo_var.get(),
                self.usuario_atual,
            )
            mensagem = "Usuario cadastrado."
        else:
            senha = self.senha_var.get() or None
            self.app.servicos.usuario.atualizar_usuario(
                self.usuario_id,
                self.login_var.get(),
                self.nome_var.get(),
                self.cargo_var.get(),
                self.usuario_atual,
                senha=senha,
            )
            mensagem = "Usuario atualizado."

        self.limpar()
        self.recarregar()
        messagebox.showinfo("Usuarios", mensagem, parent=self)

    def remover(self) -> None:
        if self.usuario_id is None:
            raise ValueError("Selecione um usuario para remover.")
        if not messagebox.askyesno(
            "Usuarios", "Remover o usuario selecionado?", parent=self
        ):
            return

        removendo_usuario_logado = self.usuario_id == self.usuario_atual.id
        self.app.servicos.usuario.remover_usuario(self.usuario_id, self.usuario_atual)
        self.limpar()
        self.recarregar()

        if removendo_usuario_logado:
            messagebox.showinfo(
                "Usuarios", "Usuario removido. A sessao sera encerrada.", parent=self
            )
            self.app.sair()
            return

        messagebox.showinfo("Usuarios", "Usuario removido.", parent=self)

    def limpar(self) -> None:
        self.usuario_id = None
        self.login_var.set("")
        self.nome_var.set("")
        self.cargo_var.set("atendente")
        self.senha_var.set("")
        limpar_selecao(self.tabela)
