import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"🔑 API_KEY cargada: {API_KEY}")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

def parse_note_with_ai(note_text):
    prompt = (
        "Extrae el monto (como número decimal) y el nombre de la billetera de esta instrucción financiera. "
        "Ejemplo de respuesta JSON: {\"amount\": 1500.0, \"pocket\": \"Ahorros\"}. "
        f"Instrucción: \"{note_text}\""
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tesmoney.ddnsfree.com"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(body),
            timeout=15
        )
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed.get("amount"), parsed.get("pocket")
        else:
            print(f"⚠️ Respuesta inesperada de IA: {data}")
            return None, None
    except Exception as e:
        print(f"❌ Error al consultar IA: {e}")
        return None, None

