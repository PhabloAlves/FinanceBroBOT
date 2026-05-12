from fastapi import APIRouter, Request
from app.services.ai_handler import process_message
from app.services.google_sheets import save_sheet, get_daily_summary
from app.services.telegram import send_message

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    data =  await request.json()
    message = data.get("message", {})
    text = message.get("text", {})
    user = message.get("from", {}).get("username", "desconhecido")

    print("--------- Mensagem Recebida ---------")
    print(f"Nova mensagem -> {user} : {text}")

    result = {
        'categoria': 'alimentacao',
        'tipo': 'despesa',
        'descricao': 'lanche ifood',
        'data': '12/05/2026',
        'valor': 100.00,
        'forma_pagamento': 'pix'
    }
    
    save_sheet(result)
    summary = get_daily_summary()
    await send_message(summary)
    print("mensagem separada:", result)

    return {"ok": True}