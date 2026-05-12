from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime
import os
import json

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def process_message(user_text):
    hoje = datetime.now().strftime("%d/%m/%y")

    config = types.GenerateContentConfig(
        system_instruction = f"Você trabalha para um sistema de finanças pessoas, preciso que identifique e separe a mensagem em categoria, tipo(despesa, receita), descrição, data de hoje, valor, forma de pagamento(crédito, pix).",
        response_mime_type = "application/json",
    ) 

    response = client.models.generate_content(
        model = "models/gemini-2.5-flash",
        contents = f"Data de hoje: {hoje}\nMensagem: {user_text}",
        config = config
    )

    return json.loads(response.text)

