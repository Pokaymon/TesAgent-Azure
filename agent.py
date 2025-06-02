import requests
import schedule
import time
import os
from dotenv import load_dotenv
from utils.parser import parse_note
from utils.ia_parser import parse_note_with_ai

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
AGENT_SECRET = os.getenv("AGENT_SECRET")
HEADERS = {"Content-Type": "application/json"}

def get_users_with_sync_enabled():
    try:
        response = requests.get(
            f"{BASE_URL}/api/agent/users",
            headers={"x-agent-secret": AGENT_SECRET}
        )
        if response.status_code == 200:
            users = response.json()
            return [u for u in users if u.get("syncro_enabled") and u.get("token")]
        else:
            print(f"❌ Error al obtener usuarios: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Excepción al obtener usuarios: {e}")
        return []

def get_notes(token):
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/notes", headers=headers)
    return response.json() if response.status_code == 200 else []

def get_user_pockets(token):
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/pocket", headers=headers)
    return response.json() if response.status_code == 200 else []

def create_transaction(token, pocket_id, amount, description):
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    data = {
        "pocket_id": pocket_id,
        "type": "income",
        "amount": f"{amount:.2f}",
        "description": description
    }
    response = requests.post(f"{BASE_URL}/transactions", headers=headers, json=data)
    print(f"→ Transacción: {response.status_code} - {response.text}")

def process_user(user):
    email = user.get("email")
    token = user.get("token")

    print(f"\n🧠 Procesando para usuario: {email}")
    notes = get_notes(token)
    pockets = get_user_pockets(token)

    for note in notes:
        print(f"→ Revisando nota: {note['title']}")
        monto, nombre_pocket = parse_note(note.get("content", ""))
        if not monto or not nombre_pocket:
            monto, nombre_pocket = parse_note_with_ai(note.get("content", ""))
        print(f"→ Resultado: monto={monto}, pocket={nombre_pocket}")

        if monto and nombre_pocket:
            pocket = next((p for p in pockets if p['name'].lower() == nombre_pocket.lower()), None)
            if pocket:
                create_transaction(token, pocket['id'], monto, description=note['title'])
            else:
                print(f"⚠️ No se encontró pocket '{nombre_pocket}'")

def process_all_users():
    print("📡 Verificando usuarios sincronizados...")
    users = get_users_with_sync_enabled()
    print(f"✔ Usuarios sincronizados encontrados: {len(users)}")
    for user in users:
        process_user(user)

# 🕓 Programar ejecución automática
# schedule.every().day.at("10:30").do(process_notes)
schedule.every(1).minutes.do(process_all_users)

print("🚀 Agente Microservicio iniciado. Esperando tareas...")
while True:
    schedule.run_pending()
    time.sleep(60)

