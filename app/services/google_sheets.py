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

