from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime
import os
import json

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def process_message(user_text, tipo: str = None):
    hoje = datetime.now().strftime("%d/%m/%Y")

    tipo_instrucao = f" O tipo já foi definido pelo usuário como '{tipo}', não precisa identificar." if tipo else " Identifique se é despesa ou receita."

    config = types.GenerateContentConfig(
        system_instruction=f"Você trabalha para um sistema de finanças pessoais. Extraia da mensagem: categoria, tipo (despesa ou receita), descrição, data, valor e forma de pagamento (crédito, pix, débito, dinheiro).{tipo_instrucao}",
        response_mime_type="application/json",
    )

    response = await client.aio.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"Data de hoje: {hoje}\nMensagem: {user_text}",
        config=config
    )

    result = json.loads(response.text)

    if tipo:
        result["tipo"] = tipo

    return result
