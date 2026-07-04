from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from src.apresentacao.base import TelaBase
from src.apresentacao.widgets import (
    criar_tabela,
    formatar_cpf,
    limpar_selecao,
    limpar_tabela,
    obter_item_selecionado,
    somente_digitos,
)


class ClienteFrame(TelaBase):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(app, master)
        self.cliente_id: int | None = None
        self.nome_var = tk.StringVar()
        self.cpf_var = tk.StringVar()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Clientes", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        tabela_frame, self.tabela = criar_tabela(
            self,
            [
                ("id", "ID", 70, "center"),
                ("nome", "Nome completo", 300, "w"),
                ("cpf", "CPF", 140, "center"),
            ],
        )
        tabela_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.tabela.bind("<<TreeviewSelect>>", lambda _evento: self._selecionar())

        formulario = ttk.LabelFrame(self, text="Cadastro")
        formulario.grid(row=1, column=1, sticky="nsew")
        formulario.grid_columnconfigure(0, weight=1)

        ttk.Label(formulario, text="Nome completo").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.nome_var).grid(
            row=1, column=0, sticky="ew", pady=(2, 10)
        )
        ttk.Label(formulario, text="CPF").grid(row=2, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.cpf_var).grid(
            row=3, column=0, sticky="ew", pady=(2, 12)
        )

        ttk.Button(
            formulario, text="Salvar", command=lambda: self.executar(self.salvar)
        ).grid(row=4, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(formulario, text="Novo", command=self.limpar).grid(
            row=5, column=0, sticky="ew", pady=(0, 6)
        )
        ttk.Button(
            formulario,
            text="Remover",
            command=lambda: self.executar(self.remover),
        ).grid(row=6, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Recarregar",
            command=lambda: self.executar(self.recarregar),
        ).grid(row=7, column=0, sticky="ew")

        self.executar(self.recarregar)

    def recarregar(self) -> None:
        limpar_tabela(self.tabela)
        for cliente in self.app.servicos.cliente.listar_clientes(self.usuario_atual):
            self.tabela.insert(
                "",
                "end",
                iid=str(cliente.id),
                values=(cliente.id, cliente.nome_completo, formatar_cpf(cliente.cpf)),
            )

    def _selecionar(self) -> None:
        selecionado = obter_item_selecionado(self.tabela)
        if selecionado is None:
            return

        self.cliente_id = int(selecionado[0])
        self.nome_var.set(selecionado[1])
        self.cpf_var.set(somente_digitos(selecionado[2]))

    def salvar(self) -> None:
        if self.cliente_id is None:
            self.app.servicos.cliente.cadastrar_cliente(
                self.nome_var.get(), self.cpf_var.get(), self.usuario_atual
            )
            mensagem = "Cliente cadastrado."
        else:
            self.app.servicos.cliente.atualizar_cliente(
                self.cliente_id,
                self.nome_var.get(),
                self.cpf_var.get(),
                self.usuario_atual,
            )
            mensagem = "Cliente atualizado."

        self.limpar()
        self.recarregar()
        messagebox.showinfo("Clientes", mensagem, parent=self)

    def remover(self) -> None:
        if self.cliente_id is None:
            raise ValueError("Selecione um cliente para remover.")
        if not messagebox.askyesno(
            "Clientes", "Remover o cliente selecionado?", parent=self
        ):
            return

        self.app.servicos.cliente.remover_cliente(self.cliente_id, self.usuario_atual)
        self.limpar()
        self.recarregar()
        messagebox.showinfo("Clientes", "Cliente removido.", parent=self)

    def limpar(self) -> None:
        self.cliente_id = None
        self.nome_var.set("")
        self.cpf_var.set("")
        limpar_selecao(self.tabela)
