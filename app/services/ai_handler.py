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
        "Você trabalha para um sistema de finanças pessoais. Extraia os dados da mensagem "
        "e responda APENAS com um objeto JSON contendo exatamente estas chaves:\n"
        '- "categoria": string (ex: "alimentação", "transporte", "salário"); se não identificar, use "Outros"\n'
        '- "tipo": string, "despesa" ou "receita"\n'
        '- "descricao": string; se não identificar, use a própria mensagem\n'
        '- "data": string no formato "dd/mm/aaaa" (use a data de hoje se não houver data na mensagem)\n'
        '- "valor": número (sem símbolo de moeda, use ponto como separador decimal); se não identificar, use 0\n'
        '- "forma_pagamento": string, uma de "crédito", "pix", "débito" ou "dinheiro"; se não identificar, use "não informado"\n'
        "NUNCA omita uma chave: se um dado não estiver na mensagem, preencha com o valor padrão indicado acima.\n"
        f"{tipo_instrucao}"
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

    if not isinstance(result, dict):
        return None

    padroes = {
        "categoria": "Outros",
        "tipo": tipo or "despesa",
        "descricao": user_text,
        "data": hoje,
        "valor": 0,
        "forma_pagamento": "não informado",
    }
    for chave, padrao in padroes.items():
        if not result.get(chave):
            result[chave] = padrao

    if tipo:
        result["tipo"] = tipo

    return result
