from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from src.apresentacao.base import TelaBase
from src.apresentacao.widgets import (
    criar_datepicker,
    criar_tabela,
    formatar_data,
    formatar_valor,
    limpar_selecao,
    limpar_tabela,
    obter_id_selecionado,
)


class ReservaFrame(TelaBase):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(app, master)
        self.reserva_id: int | None = None
        self.cliente_var = tk.StringVar()
        self.quarto_var = tk.StringVar()
        self.checkin_var = tk.StringVar()
        self.checkout_var = tk.StringVar()
        self.filtro_status_var = tk.StringVar()
        self.filtro_cliente_var = tk.StringVar()
        self._filtro_clientes_por_rotulo: dict[str, int] = {}

        self.clientes_por_rotulo: dict[str, int] = {}
        self.quartos_por_rotulo: dict[str, int] = {}
        self.rotulo_cliente_por_id: dict[int, str] = {}
        self.rotulo_quarto_por_id: dict[int, str] = {}
        self.reservas_por_id: dict[int, dict[str, object]] = {}

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Reservas", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        filtros = ttk.LabelFrame(self, text="Filtros")
        filtros.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        filtros.grid_columnconfigure(6, weight=1)

        ttk.Label(filtros, text="Check-in").grid(row=0, column=0, sticky="w")
        self.filtro_checkin_var = tk.StringVar()
        self.filtro_checkin = criar_datepicker(filtros, self.filtro_checkin_var, width=14)
        self.filtro_checkin.grid(row=0, column=1, padx=(6, 12), pady=6)

        ttk.Label(filtros, text="Checkout").grid(row=0, column=2, sticky="w")
        self.filtro_checkout_var = tk.StringVar()
        self.filtro_checkout = criar_datepicker(filtros, self.filtro_checkout_var, width=14)
        self.filtro_checkout.grid(row=0, column=3, padx=(6, 12), pady=6)

        ttk.Label(filtros, text="Status").grid(row=0, column=4, sticky="w")
        self.filtro_status = ttk.Combobox(
            filtros,
            textvariable=self.filtro_status_var,
            values=("", "pendente", "confirmada", "cancelada", "finalizada"),
            state="readonly",
            width=14,
        )
        self.filtro_status.grid(row=0, column=5, padx=(6, 12), pady=6)

        ttk.Label(filtros, text="Cliente").grid(row=1, column=0, sticky="w")
        self.filtro_cliente = ttk.Combobox(
            filtros, textvariable=self.filtro_cliente_var, state="readonly", width=30
        )
        self.filtro_cliente.grid(row=1, column=1, columnspan=2, sticky="w", padx=(6, 12), pady=6)

        ttk.Button(
            filtros,
            text="Filtrar",
            style="info.TButton",
            command=lambda: self.executar(self.aplicar_filtro),
        ).grid(row=1, column=3, sticky="w", padx=(0, 8))
        ttk.Button(
            filtros,
            text="Limpar filtros",
            style="secondary.TButton",
            command=self.limpar_filtros,
        ).grid(row=1, column=4, sticky="w")

        self.filtro_status_label = ttk.Label(filtros, text="")
        self.filtro_status_label.grid(row=2, column=0, columnspan=7, sticky="w", padx=(0, 8), pady=(0, 6))

        tabela_frame, self.tabela = criar_tabela(
            self,
            [
                ("id", "ID", 70, "center"),
                ("cliente", "Cliente", 220, "w"),
                ("quarto", "Quarto", 100, "center"),
                ("checkin", "Check-in", 110, "center"),
                ("checkout", "Checkout", 110, "center"),
                ("valor", "Valor total", 120, "e"),
                ("status", "Status", 110, "center"),
                ("usuario", "Criada por", 180, "w"),
            ],
        )
        tabela_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        self.tabela.bind("<<TreeviewSelect>>", lambda _evento: self._selecionar())

        formulario = ttk.LabelFrame(self, text="Nova reserva")
        formulario.grid(row=2, column=1, sticky="nsew")
        formulario.grid_columnconfigure(0, weight=1)

        ttk.Label(formulario, text="Cliente").grid(row=0, column=0, sticky="w")
        self.cliente_combo = ttk.Combobox(
            formulario, textvariable=self.cliente_var, state="readonly"
        )
        self.cliente_combo.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(formulario, text="Quarto").grid(row=2, column=0, sticky="w")
        self.quarto_combo = ttk.Combobox(
            formulario, textvariable=self.quarto_var, state="readonly"
        )
        self.quarto_combo.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(formulario, text="Check-in").grid(
            row=4, column=0, sticky="w"
        )
        self.checkin_date = criar_datepicker(formulario, self.checkin_var)
        self.checkin_date.grid(row=5, column=0, sticky="ew", pady=(2, 10))
        ttk.Label(formulario, text="Checkout").grid(
            row=6, column=0, sticky="w"
        )
        self.checkout_date = criar_datepicker(formulario, self.checkout_var)
        self.checkout_date.grid(row=7, column=0, sticky="ew", pady=(2, 12))

        ttk.Button(
            formulario,
            text="Criar reserva",
            style="success.TButton",
            command=lambda: self.executar(self.criar_reserva),
        ).grid(row=8, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Confirmar selecionada",
            style="success.TButton",
            command=lambda: self.executar(self.confirmar),
        ).grid(row=9, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Cancelar selecionada",
            style="danger.TButton",
            command=lambda: self.executar(self.cancelar),
        ).grid(row=10, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(
            formulario,
            text="Finalizar hospedagem",
            style="warning.TButton",
            command=lambda: self.executar(self.finalizar),
        ).grid(row=11, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(formulario, text="Nova", style="secondary.TButton", command=self.limpar).grid(
            row=12, column=0, sticky="ew", pady=(0, 6)
        )
        ttk.Button(
            formulario,
            text="Recarregar",
            style="secondary.TButton",
            command=lambda: self.executar(self.recarregar),
        ).grid(row=13, column=0, sticky="ew")

        self.executar(self.recarregar)

    def recarregar(self) -> None:
        limpar_tabela(self.tabela)
        self.reservas_por_id.clear()

        self._carregar_opcoes()
        reservas = self.app.servicos.reserva.listar_reservas(self.usuario_atual)
        self._preencher_reservas(reservas)
        self.filtro_status_label.config(text=f"{len(reservas)} reserva(s) no total.")

    def aplicar_filtro(self) -> None:
        limpar_tabela(self.tabela)
        self.reservas_por_id.clear()

        from datetime import date

        checkin_str = self.filtro_checkin_var.get().strip()
        checkout_str = self.filtro_checkout_var.get().strip()
        checkin = date.fromisoformat(checkin_str) if checkin_str else None
        checkout = date.fromisoformat(checkout_str) if checkout_str else None
        status = self.filtro_status_var.get() or None

        cliente_rotulo = self.filtro_cliente_var.get()
        cliente_id = self._filtro_clientes_por_rotulo.get(cliente_rotulo) if cliente_rotulo else None

        reservas = self.app.servicos.reserva.listar_reservas_filtradas(
            self.usuario_atual, checkin, checkout, status, cliente_id
        )
        self._preencher_reservas(reservas)
        self.filtro_status_label.config(
            text=f"{len(reservas)} reserva(s) encontrada(s)."
        )

    def limpar_filtros(self) -> None:
        self.filtro_checkin_var.set("")
        self.filtro_checkout_var.set("")
        self.filtro_status_var.set("")
        self.filtro_cliente_var.set("")
        self.recarregar()

    def _preencher_reservas(self, reservas: list[dict[str, object]]) -> None:
        for reserva in reservas:
            reserva_id = int(reserva["id"])
            self.reservas_por_id[reserva_id] = reserva
            self.tabela.insert(
                "",
                "end",
                iid=str(reserva_id),
                values=(
                    reserva_id,
                    reserva["cliente_nome"],
                    reserva["quarto_codigo"],
                    formatar_data(reserva["data_checkin"]),
                    formatar_data(reserva["data_checkout"]),
                    formatar_valor(reserva["valor_total"]),
                    reserva["status"],
                    reserva["usuario_nome"],
                ),
            )

    def _carregar_opcoes(self) -> None:
        clientes = self.app.servicos.cliente.listar_clientes(self.usuario_atual)
        quartos = self.app.servicos.quarto.listar_quartos(self.usuario_atual)

        self.clientes_por_rotulo.clear()
        self.quartos_por_rotulo.clear()
        self.rotulo_cliente_por_id.clear()
        self.rotulo_quarto_por_id.clear()
        self._filtro_clientes_por_rotulo.clear()

        rotulos_clientes: list[str] = []
        for cliente in clientes:
            rotulo = f"{cliente.id} - {cliente.nome_completo}"
            rotulos_clientes.append(rotulo)
            self.clientes_por_rotulo[rotulo] = int(cliente.id)
            self.rotulo_cliente_por_id[int(cliente.id)] = rotulo
            self._filtro_clientes_por_rotulo[rotulo] = int(cliente.id)

        rotulos_quartos: list[str] = []
        for quarto in quartos:
            rotulo = f"{quarto.id} - {quarto.codigo} ({quarto.capacidade} pessoa(s))"
            rotulos_quartos.append(rotulo)
            self.quartos_por_rotulo[rotulo] = int(quarto.id)
            self.rotulo_quarto_por_id[int(quarto.id)] = rotulo

        self.cliente_combo.configure(values=rotulos_clientes)
        self.quarto_combo.configure(values=rotulos_quartos)

        filtro_rotulos = [""] + rotulos_clientes
        self.filtro_cliente.configure(values=filtro_rotulos)

    def _selecionar(self) -> None:
        reserva_id = obter_id_selecionado(self.tabela)
        if reserva_id is None:
            return

        reserva = self.reservas_por_id.get(reserva_id)
        if reserva is None:
            return

        self.reserva_id = reserva_id
        self.cliente_var.set(
            self.rotulo_cliente_por_id.get(int(reserva["cliente_id"]), "")
        )
        self.quarto_var.set(
            self.rotulo_quarto_por_id.get(int(reserva["quarto_id"]), "")
        )
        self.checkin_var.set(formatar_data(reserva["data_checkin"]))
        self.checkout_var.set(formatar_data(reserva["data_checkout"]))

    def criar_reserva(self) -> None:
        cliente_id = self._id_cliente_selecionado()
        quarto_id = self._id_quarto_selecionado()

        self.app.servicos.reserva.criar_reserva(
            cliente_id,
            quarto_id,
            self.checkin_var.get(),
            self.checkout_var.get(),
            self.usuario_atual,
        )

        self.limpar()
        self.recarregar()
        messagebox.showinfo("Reservas", "Reserva criada como pendente.", parent=self)

    def confirmar(self) -> None:
        reserva_id = self._id_reserva_selecionada()
        self.app.servicos.reserva.confirmar_reserva(reserva_id, self.usuario_atual)
        self.recarregar()
        messagebox.showinfo("Reservas", "Reserva confirmada.", parent=self)

    def cancelar(self) -> None:
        reserva_id = self._id_reserva_selecionada()
        if not messagebox.askyesno(
            "Reservas", "Cancelar a reserva selecionada?", parent=self
        ):
            return
        self.app.servicos.reserva.cancelar_reserva(reserva_id, self.usuario_atual)
        self.recarregar()
        messagebox.showinfo("Reservas", "Reserva cancelada.", parent=self)

    def finalizar(self) -> None:
        reserva_id = self._id_reserva_selecionada()
        self.app.servicos.reserva.finalizar_hospedagem(reserva_id, self.usuario_atual)
        self.recarregar()
        messagebox.showinfo("Reservas", "Hospedagem finalizada.", parent=self)

    def limpar(self) -> None:
        self.reserva_id = None
        self.cliente_var.set("")
        self.quarto_var.set("")
        self.checkin_var.set("")
        self.checkout_var.set("")
        limpar_selecao(self.tabela)

    def _id_cliente_selecionado(self) -> int:
        rotulo = self.cliente_var.get()
        if rotulo not in self.clientes_por_rotulo:
            raise ValueError("Selecione um cliente.")
        return self.clientes_por_rotulo[rotulo]

    def _id_quarto_selecionado(self) -> int:
        rotulo = self.quarto_var.get()
        if rotulo not in self.quartos_por_rotulo:
            raise ValueError("Selecione um quarto.")
        return self.quartos_por_rotulo[rotulo]

    def _id_reserva_selecionada(self) -> int:
        reserva_id = obter_id_selecionado(self.tabela)
        if reserva_id is None:
            raise ValueError("Selecione uma reserva.")
        return reserva_id
