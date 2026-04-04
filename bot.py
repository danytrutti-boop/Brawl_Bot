import requests
import os
from datetime import datetime, timezone

# Recupera i dati dai Secrets di GitHub
TAG = os.getenv('PLAYER_TAG')
TOKEN = os.getenv('BRAWL_TOKEN')
TOPIC = os.getenv('NTFY_TOPIC')

def check_battle_log():
    url = f"https://api.brawlstars.com/v1/players/%23{TAG}/battlelog"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            battles = response.json().get('items', [])
            if not battles:
                return
            
            # Prendi l'ultima partita fatta
            last_battle = battles[0]
            battle_time_str = last_battle['battleTime']
            # Formato: 20240520T100000.000Z
            battle_time = datetime.strptime(battle_time_str, '%Y%m%dT%H%M%S.%fZ').replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            
            # Calcola quanti minuti fa è stata fatta la partita
            diff = (now - battle_time).total_seconds() / 60
            
            print(f"Ultima partita rilevata: {diff:.1f} minuti fa")
            
            # Se la partita è avvenuta negli ultimi 15 minuti, invia notifica
            if diff < 15:
                mode = last_battle['event'].get('mode', 'partita')
                msg = f"🚨 GIOCATORE ATTIVO! Ha appena giocato a {mode}."
                requests.post(f"https://ntfy.sh/{TOPIC}", data=msg.encode('utf-8'))
                print("Notifica inviata!")
        else:
            print(f"Errore API: {response.status_code}")
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    check_battle_log()
