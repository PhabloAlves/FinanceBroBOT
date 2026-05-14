import gspread
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def save_sheet(data: dict):
    client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))
    sheet = client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1
    sheet.append_row([
        data.get("data"),
        data.get("categoria"),
        data.get("tipo"),
        data.get("descricao"),
        data.get("valor"),
        data.get("forma_pagamento"),
    ])
    return {"ok": True}

def get_daily_summary():
   
    hoje = datetime.now().strftime("%d/%m/%Y")

    client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))
    sheet = client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1
    registros = sheet.get_all_records()

    do_dia = [r for r in registros if r.get("Data") == hoje]

    if not do_dia:
        return f"Nenhum lançamento registrado hoje ({hoje})."

    total_despesas = sum(float(str(r["Valor"]).replace("R$", "").replace(",", ".").strip()) for r in do_dia if r.get("Tipo") == "despesa")
    total_receitas = sum(float(str(r["Valor"]).replace("R$", "").replace(",", ".").strip()) for r in do_dia if r.get("Tipo") == "receita")


    total_mes_despesas = sheet.acell("G2").value
    total_mes_receitas = sheet.acell("H2").value

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

    return "\n".join(linhas)


def set_renda(monthlyIncome):
    client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))
    sheet = client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1
    sheet.update([[monthlyIncome]], "I2")
    return {"ok": True}
    
def clear_data():
    client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))
    sheet = client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1
    sheet.update([[0]], "I2")
    sheet.update([[0]], "G2")
    sheet.update([[0]], "H2")
    sheet.batch_clear(["A3:F1000"])

def get_resume():
    mes_atual = datetime.now().strftime("%m/%Y")

    client = gspread.service_account(filename=os.path.join(BASE_DIR, "credentials.json"))
    sheet = client.open_by_key(os.environ.get("GOOGLE_SHEET_ID")).sheet1
    registros = sheet.get_all_records()

    do_mes = [r for r in registros if str(r.get("Data", "")).endswith(mes_atual)]

    renda = sheet.acell("I2").value or "0"
    total_despesas = sheet.acell("G2").value
    total_receitas = sheet.acell("H2").value
    saldo = float(renda) - float(total_despesas)

    import calendar
    hoje = datetime.now()
    ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)[1]
    ultimo_dia = hoje.replace(day=ultimo_dia_num)
    dias_restantes = (ultimo_dia - hoje).days + 1
    sugestao_diaria = saldo / dias_restantes if dias_restantes > 0 else 0

    linhas = [f"📊 Resumo de {mes_atual}\n"]
    linhas.append(f"💰 Renda mensal: R$ {renda}")
    linhas.append(f"🔴 Total despesas: R$ {total_despesas}")
    linhas.append(f"🟢 Total receitas: R$ {total_receitas}")
    linhas.append(f"💵 Saldo disponível: R$ {saldo}")
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

