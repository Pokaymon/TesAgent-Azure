import requests
import schedule
import time
import os
from dotenv import load_dotenv
from utils.parser import parse_note
from utils.ia_parser import parse_note_with_ai

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
HEADERS = {"Content-Type": "application/json"}
TOKEN = None

def login():
    global HEADERS, TOKEN
    print("→ Autenticando agente...")
    try:
        response = requests.post(f"{BASE_URL}/api/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        if response.status_code == 200:
            TOKEN = response.json().get("token")
            HEADERS["Authorization"] = f"Bearer {TOKEN}"
            print("→ Autenticación exitosa.")
        else:
            print(f"→ Error al autenticar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"→ Excepción en login: {e}")

def is_sync_enabled():
    try:
        response = requests.get(f"{BASE_URL}/api/syncro", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get("state", False)
        else:
            print(f"→ Error al verificar sincronización: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"→ Excepción al verificar sincronización: {e}")
        return False

def get_notes():
    response = requests.get(f"{BASE_URL}/api/notes", headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def get_user_pockets():
    response = requests.get(f"{BASE_URL}/pocket", headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def create_transaction(pocket_id, amount, description="Ingreso hecho por Tes Agent"):
    data = {
        "pocket_id": pocket_id,
        "type": "income",
        "amount": f"{amount:.2f}",
        "description": description
    }
    response = requests.post(f"{BASE_URL}/transactions", headers=HEADERS, json=data)
    print(f"→ Transacción enviada: {response.status_code} - {response.text}")

def process_notes():
    print("→ Verificando estado de sincronización...")
    if not is_sync_enabled():
        print("→ Sincronización desactivada. No se realizará ningún proceso.")
        return

    print("→ Sincronización activa. Procesando notas...")
    notes = get_notes()
    print(f"→ Notas obtenidas: {notes}")

    pockets = get_user_pockets()
    print(f"→ Pockets obtenidos: {pockets}")

    for note in notes:
        print(f"→ Revisando nota: {note['title']}")
        monto, nombre_pocket = parse_note(note.get("content", ""))
        if not monto or not nombre_pocket:
          monto, nombre_pocket = parse_note_with_ai(note.get("content", ""))
        print(f"→ Resultado parseo: monto={monto}, pocket={nombre_pocket}")

        if monto and nombre_pocket:
            pocket = next((p for p in pockets if p['name'].lower() == nombre_pocket.lower()), None)
            if pocket:
                create_transaction(pocket['id'], monto, description=note['title'])
            else:
                print(f"→  No se encontró pocket '{nombre_pocket}'")

# 🔐 Iniciar sesión antes de programar tareas
login()

# 🕓 Programar ejecución automática
# schedule.every().day.at("10:30").do(process_notes)
schedule.every(1).minutes.do(process_notes)

print("■ Agente iniciado. Esperando ejecución...")
while True:
    schedule.run_pending()
    time.sleep(60)

