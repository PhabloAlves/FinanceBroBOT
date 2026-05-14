import gspread
from dotenv import load_dotenv
from datetime import datetime
import calendar
import asyncio
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))

def _sheet():
    return _client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1


async def save_sheet(data: dict):
    await asyncio.to_thread(lambda: _sheet().append_row([
        data.get("data"),
        data.get("categoria"),
        data.get("tipo"),
        data.get("descricao"),
        data.get("valor"),
        data.get("forma_pagamento"),
    ]))
    return {"ok": True}


async def get_daily_summary():
    hoje = datetime.now().strftime("%d/%m/%Y")

    def _run():
        sheet = _sheet()
        registros = sheet.get_all_records()
        values = sheet.batch_get(["G2", "H2", "J2"])
        return registros, values

    registros, values = await asyncio.to_thread(_run)
    do_dia = [r for r in registros if r.get("Data") == hoje]

    if not do_dia:
        return f"Nenhum lançamento registrado hoje ({hoje})."

    total_despesas = sum(float(str(r["Valor"]).replace("R$", "").replace(",", ".").strip()) for r in do_dia if r.get("Tipo") == "despesa")
    total_receitas = sum(float(str(r["Valor"]).replace("R$", "").replace(",", ".").strip()) for r in do_dia if r.get("Tipo") == "receita")

    total_mes_despesas = values[0][0][0] if values[0] else "0"
    total_mes_receitas = values[1][0][0] if values[1] else "0"
    saldo_atual = values[2][0][0] if values[2] else "0"

    linhas = [f"📅 Resumo do dia {hoje}\n"]
    for r in do_dia:
        emoji = "🔴" if r.get("Tipo") == "despesa" else "🟢"
        linhas.append(f"{emoji} {r['Descrição']} | {r['Categoria']} | {r['Valor']} | {r['Forma de Pagamento']}")

    linhas.append(f"\n📊 Hoje")
    linhas.append(f"  🔴 Despesas: R$ {total_despesas:.2f}")
    linhas.append(f"  🟢 Receitas: R$ {total_receitas:.2f}")
    linhas.append(f"\n📆 Mês")
    linhas.append(f"  🔴 Despesas: {total_mes_despesas}")
    linhas.append(f"  🟢 Receitas: {total_mes_receitas}")
    linhas.append(f"  💵 Saldo atual: {saldo_atual}")

    return "\n".join(linhas)


async def set_renda(monthlyIncome):
    await asyncio.to_thread(lambda: _sheet().update([[monthlyIncome]], "I2"))
    return {"ok": True}


async def clear_data():
    def _run():
        sheet = _sheet()
        sheet.update([[0]], "I2")
        sheet.batch_clear(["A3:F1000"])
    await asyncio.to_thread(_run)


async def get_resume():
    mes_atual = datetime.now().strftime("%m/%Y")

    def _run():
        sheet = _sheet()
        registros = sheet.get_all_records()
        values = sheet.batch_get(["G2", "H2", "I2", "J2"])
        return registros, values

    registros, values = await asyncio.to_thread(_run)
    do_mes = [r for r in registros if str(r.get("Data", "")).endswith(mes_atual)]

    total_despesas = values[0][0][0] if values[0] else "0"
    total_receitas = values[1][0][0] if values[1] else "0"
    renda = values[2][0][0] if values[2] else "0"
    saldo_atual = float(str(values[3][0][0]).replace("R$", "").replace(",", ".").strip()) if values[3] else 0.0

    hoje = datetime.now()
    ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)[1]
    ultimo_dia = hoje.replace(day=ultimo_dia_num)
    dias_restantes = (ultimo_dia - hoje).days + 1
    sugestao_diaria = saldo_atual / dias_restantes if dias_restantes > 0 else 0

    linhas = [f"📊 Resumo de {mes_atual}\n"]
    linhas.append(f"💰 Renda mensal: R$ {renda}")
    linhas.append(f"🔴 Total despesas: R$ {total_despesas}")
    linhas.append(f"🟢 Total receitas: R$ {total_receitas}")
    linhas.append(f"💵 Saldo atual: R$ {saldo_atual:.2f}")
    linhas.append(f"📆 Dias restantes no mês: {dias_restantes}")
    linhas.append(f"💡 Sugestão por dia: R$ {sugestao_diaria:.2f}\n")

    categorias: dict = {}
    for r in do_mes:
        if r.get("Tipo") == "despesa":
            cat = r.get("Categoria", "Outros")
            valor = float(str(r["Valor"]).replace("R$", "").replace(",", ".").strip())
            categorias[cat] = categorias.get(cat, 0) + valor

    if categorias:
        linhas.append("🗂 Por categoria:")
        for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            linhas.append(f"  • {cat}: R$ {valor:.2f}")

    return "\n".join(linhas)
