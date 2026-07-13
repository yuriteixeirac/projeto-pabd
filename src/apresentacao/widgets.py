from __future__ import annotations

from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import ttk


def criar_tabela(
    master: tk.Widget,
    colunas: list[tuple[str, str, int, str]],
    altura: int = 15,
) -> tuple[ttk.Frame, ttk.Treeview]:
    frame = ttk.Frame(master)
    tabela = ttk.Treeview(
        frame,
        columns=[coluna[0] for coluna in colunas],
        show="headings",
        selectmode="browse",
        height=altura,
    )
    barra = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)

    for identificador, titulo, largura, alinhamento in colunas:
        tabela.heading(identificador, text=titulo)
        tabela.column(
            identificador,
            width=largura,
            minwidth=60,
            anchor=alinhamento,
            stretch=True,
        )

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tabela.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")
    return frame, tabela


def limpar_tabela(tabela: ttk.Treeview) -> None:
    itens = tabela.get_children()
    if itens:
        tabela.delete(*itens)


def limpar_selecao(tabela: ttk.Treeview) -> None:
    for item in tabela.selection():
        tabela.selection_remove(item)


def obter_item_selecionado(tabela: ttk.Treeview) -> tuple[str, ...] | None:
    selecionados = tabela.selection()
    if not selecionados:
        return None
    return tabela.item(selecionados[0], "values")


def obter_id_selecionado(tabela: ttk.Treeview) -> int | None:
    selecionados = tabela.selection()
    if not selecionados:
        return None

    item_id = selecionados[0]
    try:
        return int(item_id)
    except ValueError:
        valores = tabela.item(item_id, "values")
        return int(valores[0]) if valores else None


def somente_digitos(valor: object) -> str:
    return "".join(caractere for caractere in str(valor) if caractere.isdigit())


def formatar_cpf(cpf: object) -> str:
    digitos = somente_digitos(cpf)
    if len(digitos) != 11:
        return str(cpf)
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def formatar_valor(valor: object) -> str:
    try:
        return f"{Decimal(str(valor)):.2f}"
    except (InvalidOperation, ValueError):
        return str(valor)


def formatar_data(valor: object) -> str:
    if hasattr(valor, "isoformat"):
        return valor.isoformat()
    return str(valor)


def criar_datepicker(
    master: tk.Widget,
    date_var: tk.StringVar,
    date_pattern: str = "yyyy-mm-dd",
    width: int = 14,
) -> ttk.Frame:
    from ttkbootstrap.widgets import DateEntry as TbDateEntry
    from datetime import date, datetime

    fmt = "%Y-%m-%d" if date_pattern == "yyyy-mm-dd" else "%d/%m/%Y"

    try:
        inicio = datetime.strptime(date_var.get().strip(), fmt) if date_var.get().strip() else None
    except (ValueError, TypeError):
        inicio = None

    picker = TbDateEntry(master, dateformat=fmt, startdate=inicio, bootstyle="info", width=width)

    def _atualizar_var(*_: object) -> None:
        try:
            dt = picker.get_date()
            date_var.set(dt.strftime(fmt))
        except Exception:
            pass

    picker.bind("<<DateEntrySelected>>", _atualizar_var)

    def _monitorar_var(*_: object) -> None:
        val = date_var.get().strip()
        if not val:
            picker.entry.delete(0, "end")
            return
        try:
            picker.set_date(datetime.strptime(val, fmt))
        except (ValueError, TypeError):
            pass

    date_var.trace_add("write", _monitorar_var)

    if inicio:
        date_var.set(inicio.strftime(fmt))

    return picker
