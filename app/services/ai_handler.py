from groq import AsyncGroq
from dotenv import load_dotenv
from datetime import datetime
import os
import json

load_dotenv()

client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def process_message(user_text, tipo: str = None):
    hoje = datetime.now().strftime("%d/%m/%Y")

    tipo_instrucao = f" O tipo já foi definido pelo usuário como '{tipo}', não precisa identificar." if tipo else " Identifique se é despesa ou receita."

    system_instruction = (
        "Você trabalha para um sistema de finanças pessoais. Extraia da mensagem: "
        "categoria, tipo (despesa ou receita), descrição, data, valor e forma de pagamento "
        f"(crédito, pix, débito, dinheiro).{tipo_instrucao} "
        "Responda apenas com um objeto JSON."
    )

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Data de hoje: {hoje}\nMensagem: {user_text}"},
        ],
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError, IndexError):
        return None

    if tipo:
        result["tipo"] = tipo

    return result
