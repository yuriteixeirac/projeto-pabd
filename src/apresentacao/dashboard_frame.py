from __future__ import annotations

from datetime import date

import tkinter as tk
from tkinter import ttk

from src.apresentacao.base import TelaBase
from src.apresentacao.widgets import criar_tabela, formatar_valor, limpar_tabela


class DashboardFrame(TelaBase):
    def __init__(self, app: object, master: tk.Widget) -> None:
        super().__init__(app, master)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Dashboard", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )

        cards = ttk.Frame(self)
        cards.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self._criar_cards(cards)

        ttk.Label(self, text="Ultimas reservas", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 4)
        )
        tabela1_frame, self.tabela_ultimas = criar_tabela(
            self,
            [
                ("id", "ID", 60, "center"),
                ("cliente", "Cliente", 200, "w"),
                ("quarto", "Quarto", 100, "center"),
                ("checkin", "Check-in", 110, "center"),
                ("checkout", "Checkout", 110, "center"),
                ("status", "Status", 110, "center"),
            ],
            altura=8,
        )
        tabela1_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 8))

        ttk.Label(self, text="Proximos check-ins (7 dias)", font=("Helvetica", 10, "bold")).grid(
            row=2, column=1, sticky="w", padx=(8, 0), pady=(0, 4)
        )
        tabela2_frame, self.tabela_checkins = criar_tabela(
            self,
            [
                ("id", "ID", 60, "center"),
                ("cliente", "Cliente", 200, "w"),
                ("quarto", "Quarto", 100, "center"),
                ("checkin", "Check-in", 110, "center"),
                ("checkout", "Checkout", 110, "center"),
                ("status", "Status", 110, "center"),
            ],
            altura=8,
        )
        tabela2_frame.grid(row=3, column=1, sticky="nsew", padx=(8, 0))

        self.executar(self._atualizar)

    def _criar_cards(self, parent: ttk.Frame) -> None:
        self.card_reservas = ttk.LabelFrame(parent, text="Reservas Hoje", padding=12)
        self.card_reservas.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.label_reservas = ttk.Label(
            self.card_reservas, font=("Helvetica", 28, "bold"), style="primary.TLabel"
        )
        self.label_reservas.pack(anchor="center")

        self.card_ocupados = ttk.LabelFrame(parent, text="Quartos Ocupados", padding=12)
        self.card_ocupados.grid(row=0, column=1, sticky="nsew", padx=(6, 6))
        self.label_ocupados = ttk.Label(
            self.card_ocupados, font=("Helvetica", 28, "bold"), style="primary.TLabel"
        )
        self.label_ocupados.pack(anchor="center")

        self.card_pendentes = ttk.LabelFrame(parent, text="Pendentes", padding=12)
        self.card_pendentes.grid(row=0, column=2, sticky="nsew", padx=(6, 6))
        self.label_pendentes = ttk.Label(
            self.card_pendentes, font=("Helvetica", 28, "bold"), style="warning.TLabel"
        )
        self.label_pendentes.pack(anchor="center")

        self.card_faturamento = ttk.LabelFrame(parent, text="Faturamento do Mes", padding=12)
        self.card_faturamento.grid(row=0, column=3, sticky="nsew", padx=(6, 0))
        self.label_faturamento = ttk.Label(
            self.card_faturamento, font=("Helvetica", 28, "bold"), style="success.TLabel"
        )
        self.label_faturamento.pack(anchor="center")

    def _atualizar(self) -> None:
        hoje = date.today()
        reservas_hoje = self.app.servicos.reserva.contar_reservas_ativas_hoje(self.usuario_atual)
        ocupados = self.app.servicos.quarto.contar_ocupados(self.usuario_atual)
        pendentes = self.app.servicos.reserva.contar_pendentes(self.usuario_atual)
        faturamento = self.app.servicos.reserva.faturamento_mes(self.usuario_atual, hoje.year, hoje.month)

        self.label_reservas.config(text=str(reservas_hoje))
        self.label_ocupados.config(text=str(ocupados))
        self.label_pendentes.config(text=str(pendentes))
        self.label_faturamento.config(text=formatar_valor(faturamento))

        self._preencher_tabela_checkins()
        self._preencher_tabela_ultimas()

    def _preencher_tabela_ultimas(self) -> None:
        limpar_tabela(self.tabela_ultimas)
        reservas = self.app.servicos.reserva.ultimas_reservas(self.usuario_atual)
        for r in reservas:
            self.tabela_ultimas.insert(
                "", "end", iid=str(r["id"]),
                values=(
                    r["id"], r["cliente_nome"], r["quarto_codigo"],
                    r["data_checkin"].isoformat(), r["data_checkout"].isoformat(),
                    r["status"],
                ),
            )

    def _preencher_tabela_checkins(self) -> None:
        limpar_tabela(self.tabela_checkins)
        reservas = self.app.servicos.reserva.proximos_checkins(self.usuario_atual)
        for r in reservas:
            self.tabela_checkins.insert(
                "", "end", iid=str(r["id"]),
                values=(
                    r["id"], r["cliente_nome"], r["quarto_codigo"],
                    r["data_checkin"].isoformat(), r["data_checkout"].isoformat(),
                    r["status"],
                ),
            )
