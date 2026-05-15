from fastapi import APIRouter, Request, Header
from app.services.ai_handler import process_message
from app.services.finance_db import save_transaction, set_renda, clear_data, get_resume, user_exists, create_user
from app.services.telegram import send_message
from dotenv import load_dotenv
import os

load_dotenv()

WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET")

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

ONBOARDING = (
    "👋 Bem-vindo ao FinanceBro!\n\n"
    "Eu vou te ajudar a controlar suas finanças pelo Telegram.\n\n"
    "📌 Para começar, defina sua renda mensal:\n"
    "/setrenda 3000\n\n"
    "Depois é só registrar seus gastos e receitas:\n"
    "/despesa lanche ifood 50 pix\n"
    "/receita salário 3000 transferencia\n\n"
    "Digite /ajuda para ver todos os comandos."
)

@router.post("/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(default=None)):
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        return {"ok": False}

    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "") or ""
    user_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")

    if not user_id:
        return {"ok": True}

    if not await user_exists(user_id):
        await create_user(user_id)
        await send_message(chat_id, ONBOARDING)
        return {"ok": True}

    if not text.startswith("/"):
        return {"ok": True}

    if text.startswith("/despesa") or text.startswith("/receita"):
        tipo = "despesa" if text.startswith("/despesa") else "receita"
        descricao = text.split(" ", 1)[1] if " " in text else ""
        if not descricao:
            await send_message(chat_id, f"❌ Use: /{tipo} descrição valor forma_pagamento")
            return {"ok": True}
        result = await process_message(descricao, tipo=tipo)
        if not result:
            await send_message(chat_id, "❌ Não consegui entender a mensagem. Tente novamente.")
            return {"ok": True}
        await save_transaction(result, user_id)
        emoji = "🔴" if tipo == "despesa" else "🟢"
        await send_message(chat_id, f"{emoji} Salvo: {result.get('descricao')} | {result.get('categoria')} | R$ {result.get('valor')} | {result.get('forma_pagamento')}")

    elif text.startswith("/setrenda"):
        partes = text.split(" ")
        if len(partes) < 2:
            await send_message(chat_id, "❌ Use: /setrenda 3000")
            return {"ok": True}
        try:
            valor = float(partes[1].replace(",", "."))
            if valor <= 0:
                raise ValueError
        except ValueError:
            await send_message(chat_id, "❌ Valor inválido. Use um número positivo. Ex: /setrenda 3000")
            return {"ok": True}
        await set_renda(valor, user_id)
        await send_message(chat_id, f"✅ Renda mensal definida: R$ {valor:.2f}")

    elif text == "/resumo":
        await send_message(chat_id, await get_resume(user_id))

    elif text == "/cleardata":
        await clear_data(user_id)
        await send_message(chat_id, "🗑 Todos os lançamentos foram apagados.")

    else:
        await send_message(chat_id, COMMANDS)

    return {"ok": True}
