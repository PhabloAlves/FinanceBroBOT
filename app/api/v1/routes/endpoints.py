from fastapi import APIRouter, Request
from app.services.ai_handler import process_message
from app.services.finance_db import save_transaction, set_renda, clear_data, get_resume
from app.services.telegram import send_message

router = APIRouter()

COMMANDS = (
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
    user_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")

    if not text.startswith("/") or not user_id:
        return {"ok": True}

    if text.startswith("/despesa") or text.startswith("/receita"):
        tipo = "despesa" if text.startswith("/despesa") else "receita"
        descricao = text.split(" ", 1)[1] if " " in text else ""
        if not descricao:
            await send_message(chat_id, f"❌ Use: /{tipo} descrição valor forma_pagamento")
            return {"ok": True}
        result = await process_message(descricao, tipo=tipo)
        await save_transaction(result, user_id)
        emoji = "🔴" if tipo == "despesa" else "🟢"
        await send_message(chat_id, f"{emoji} Salvo: {result.get('descricao')} | {result.get('categoria')} | R$ {result.get('valor')} | {result.get('forma_pagamento')}")

    elif text.startswith("/setrenda"):
        partes = text.split(" ")
        if len(partes) < 2:
            await send_message(chat_id, "❌ Use: /setrenda 3000")
            return {"ok": True}
        await set_renda(partes[1], user_id)
        await send_message(chat_id, f"✅ Renda mensal definida: R$ {partes[1]}")

    elif text == "/resumo":
        await send_message(chat_id, await get_resume(user_id))

    elif text == "/cleardata":
        await clear_data(user_id)
        await send_message(chat_id, "🗑 Todos os lançamentos foram apagados.")

    else:
        await send_message(chat_id, COMMANDS)

    return {"ok": True}
