from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from src.apresentacao.base import TelaBase
from src.apresentacao.widgets import (
    criar_datepicker,
    criar_tabela,
    formatar_valor,
    limpar_selecao,
    limpar_tabela,
    obter_item_selecionado,
)


class QuartoFrame(TelaBase):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(app, master)
        self.quarto_id: int | None = None
        self.codigo_var = tk.StringVar()
        self.capacidade_var = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.descricao_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value="casal")
        self.checkin_var = tk.StringVar()
        self.checkout_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Informe o periodo para consultar disponibilidade."
        )
        self.eh_admin = self.usuario_atual.cargo == "admin"

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Quartos", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        disponibilidade = ttk.LabelFrame(self, text="Disponibilidade")
        disponibilidade.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        disponibilidade.grid_columnconfigure(4, weight=1)

        ttk.Label(disponibilidade, text="Check-in").grid(
            row=0, column=0, sticky="w"
        )
        self.checkin_date = criar_datepicker(disponibilidade, self.checkin_var, width=14)
        self.checkin_date.grid(row=0, column=1, padx=(6, 12), pady=6)
        ttk.Label(disponibilidade, text="Checkout").grid(
            row=0, column=2, sticky="w"
        )
        self.checkout_date = criar_datepicker(disponibilidade, self.checkout_var, width=14)
        self.checkout_date.grid(row=0, column=3, padx=(6, 12), pady=6)
        ttk.Button(
            disponibilidade,
            text="Consultar",
            style="info.TButton",
            command=lambda: self.executar(self.consultar_disponibilidade),
        ).grid(row=0, column=4, sticky="w", padx=(0, 8))
        ttk.Button(
            disponibilidade,
            text="Todos",
            style="secondary.TButton",
            command=lambda: self.executar(self.recarregar),
        ).grid(row=0, column=5, sticky="w")
        ttk.Label(disponibilidade, textvariable=self.status_var).grid(
            row=1, column=0, columnspan=6, sticky="w", padx=(0, 8), pady=(0, 6)
        )

        tabela_frame, self.tabela = criar_tabela(
            self,
            [
                ("id", "ID", 70, "center"),
                ("codigo", "Codigo", 100, "center"),
                ("capacidade", "Capacidade", 120, "center"),
                ("valor", "Valor", 120, "e"),
                ("tipo", "Tipo", 100, "center"),
            ],
        )
        tabela_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        self.tabela.bind("<<TreeviewSelect>>", lambda _evento: self._selecionar())

        formulario = ttk.LabelFrame(self, text="Cadastro")
        formulario.grid(row=2, column=1, sticky="nsew")
        formulario.grid_columnconfigure(0, weight=1)

        estado = "normal" if self.eh_admin else "disabled"
        ttk.Label(formulario, text="Codigo").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.codigo_var, state=estado).grid(
            row=1, column=0, sticky="ew", pady=(2, 10)
        )
        ttk.Label(formulario, text="Capacidade").grid(row=2, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.capacidade_var, state=estado).grid(
            row=3, column=0, sticky="ew", pady=(2, 10)
        )
        ttk.Label(formulario, text="Valor").grid(row=4, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.valor_var, state=estado).grid(
            row=5, column=0, sticky="ew", pady=(2, 8)
        )
        ttk.Label(formulario, text="Tipo").grid(row=6, column=0, sticky="w")
        ttk.Combobox(
            formulario,
            textvariable=self.tipo_var,
            values=("solteiro", "casal", "suite"),
            state="readonly" if estado == "disabled" else "normal",
        ).grid(row=7, column=0, sticky="ew", pady=(2, 8))
        ttk.Label(formulario, text="Descricao").grid(row=8, column=0, sticky="w")
        ttk.Entry(formulario, textvariable=self.descricao_var, state=estado).grid(
            row=9, column=0, sticky="ew", pady=(2, 12)
        )

        ttk.Button(
            formulario,
            text="Salvar",
            style="success.TButton",
            command=lambda: self.executar(self.salvar),
            state=estado,
        ).grid(row=10, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(formulario, text="Novo", style="secondary.TButton", command=self.limpar, state=estado).grid(
            row=11, column=0, sticky="ew", pady=(0, 6)
        )
        ttk.Button(
            formulario,
            text="Remover",
            style="danger.TButton",
            command=lambda: self.executar(self.remover),
            state=estado,
        ).grid(row=12, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Recarregar",
            style="secondary.TButton",
            command=lambda: self.executar(self.recarregar),
        ).grid(row=13, column=0, sticky="ew")

        if not self.eh_admin:
            ttk.Label(
                formulario,
                text="Cadastro e edicao disponiveis apenas para administradores.",
                style="secondary.TLabel",
                wraplength=220,
            ).grid(row=14, column=0, sticky="w", pady=(12, 0))

        self.executar(self.recarregar)

    def recarregar(self) -> None:
        limpar_tabela(self.tabela)
        quartos = self.app.servicos.quarto.listar_quartos(self.usuario_atual)
        self._preencher_tabela(quartos)
        self.status_var.set("Listando todos os quartos.")

    def consultar_disponibilidade(self) -> None:
        limpar_tabela(self.tabela)
        quartos = self.app.servicos.quarto.listar_quartos_disponiveis(
            self.checkin_var.get(), self.checkout_var.get(), self.usuario_atual
        )
        self._preencher_tabela(quartos)
        self.status_var.set(f"{len(quartos)} quarto(s) disponivel(is) no periodo.")

    def _preencher_tabela(self, quartos: list[object]) -> None:
        for quarto in quartos:
            self.tabela.insert(
                "",
                "end",
                iid=str(quarto.id),
                values=(
                    quarto.id,
                    quarto.codigo,
                    quarto.capacidade,
                    formatar_valor(quarto.valor),
                    quarto.tipo,
                ),
            )

    def _selecionar(self) -> None:
        selecionado = obter_item_selecionado(self.tabela)
        if selecionado is None:
            return

        self.quarto_id = int(selecionado[0])
        self.codigo_var.set(selecionado[1])
        self.capacidade_var.set(selecionado[2])
        self.valor_var.set(selecionado[3].replace(".", ","))
        self.tipo_var.set(selecionado[4])
        self.descricao_var.set("")

    def salvar(self) -> None:
        if self.quarto_id is None:
            self.app.servicos.quarto.cadastrar_quarto(
                self.codigo_var.get(),
                self.capacidade_var.get(),
                self.valor_var.get(),
                self.usuario_atual,
                self.descricao_var.get(),
                self.tipo_var.get(),
            )
            mensagem = "Quarto cadastrado."
        else:
            self.app.servicos.quarto.atualizar_quarto(
                self.quarto_id,
                self.codigo_var.get(),
                self.capacidade_var.get(),
                self.valor_var.get(),
                self.usuario_atual,
                self.descricao_var.get(),
                self.tipo_var.get(),
            )
            mensagem = "Quarto atualizado."

        self.limpar()
        self.recarregar()
        messagebox.showinfo("Quartos", mensagem, parent=self)

    def remover(self) -> None:
        if self.quarto_id is None:
            raise ValueError("Selecione um quarto para remover.")
        if not messagebox.askyesno(
            "Quartos", "Remover o quarto selecionado?", parent=self
        ):
            return

        self.app.servicos.quarto.remover_quarto(self.quarto_id, self.usuario_atual)
        self.limpar()
        self.recarregar()
        messagebox.showinfo("Quartos", "Quarto removido.", parent=self)

    def limpar(self) -> None:
        self.quarto_id = None
        self.codigo_var.set("")
        self.capacidade_var.set("")
        self.valor_var.set("")
        self.descricao_var.set("")
        self.tipo_var.set("casal")
        limpar_selecao(self.tabela)
