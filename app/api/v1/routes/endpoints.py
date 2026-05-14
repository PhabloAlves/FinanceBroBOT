from fastapi import APIRouter, Request
from app.services.ai_handler import process_message
from app.services.google_sheets import save_sheet, get_daily_summary, set_renda, clear_data, get_resume
from app.services.telegram import send_message

router = APIRouter()

def get_commands():
    return (
        "🤖 Comandos disponíveis:\n\n"
        "/despesa lanche ifood 50 pix — registra uma despesa\n"
        "/receita salário 3000 pix — registra uma receita\n"
        "/resumo — resumo mensal completo\n"
        "/setrenda 3000 — define sua renda mensal\n"
        "/cleardata — apaga todos os lançamentos\n"
        "/ajuda — exibe este menu"
    )

@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "") or ""
    user = message.get("from", {}).get("username", "desconhecido")

    if text.startswith("/"):
        if text.startswith("/despesa") or text.startswith("/receita"):
            tipo = "despesa" if text.startswith("/despesa") else "receita"
            descricao = text.split(" ", 1)[1] if " " in text else ""
            if not descricao:
                await send_message(f"❌ Use: /{tipo} descrição valor forma_pagamento")
                return {"ok": True}
            result = process_message(descricao, tipo=tipo)
            save_sheet(result)
            emoji = "🔴" if tipo == "despesa" else "🟢"
            await send_message(f"{emoji} Salvo: {result.get('descricao')} | {result.get('categoria')} | R$ {result.get('valor')} | {result.get('forma_pagamento')}")

        elif text.startswith("/setrenda"):
            partes = text.split(" ")
            if len(partes) < 2:
                await send_message("❌ Use: /setrenda 3000")
                return {"ok": True}
            set_renda(partes[1])
            await send_message(f"✅ Renda mensal definida: R$ {partes[1]}")

        elif text == "/resumo":
            resumo = get_resume()
            await send_message(resumo)

        elif text == "/cleardata":
            clear_data()
            await send_message("🗑 Todos os lançamentos foram apagados.")

        elif text in ("/ajuda", "/help"):
            await send_message(get_commands())

        else:
            await send_message(get_commands())

        return {"ok": True}

    return {"ok": True}
