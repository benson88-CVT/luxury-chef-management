import json
import os
import urllib.request
import urllib.parse

def invia_telegram(testo):
    # Recupera i dati sensibili salvati nei GitHub Secrets
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Errore: Credenziali Telegram non trovate nei Secrets.")
        return

    # Prepara la richiesta per l'API di Telegram
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': testo,
        'parse_mode': 'Markdown'
    }
    
    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    
    try:
        with urllib.request.urlopen(req) as response:
            print("🚀 Messaggio inviato correttamente su Telegram!")
    except Exception as e:
        print(f"❌ Errore durante l'invio su Telegram: {e}")

def calcola(ospiti, tipo_menu):
    with open('config_business.json', 'r') as f:
        config = json.load(f)
        
    try:
        with open(f'menus/{tipo_menu}.json', 'r') as f:
            menu = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Errore: Il menu '{tipo_menu}' non esiste.")
        return

    costo_cibo = ospiti * menu['food_cost_per_pax']
    
    cuochi_extra = 0
    for scaglione in menu['scaglioni_personale']:
        if ospiti <= scaglione['fino_a']:
            cuochi_extra = scaglione['cuochi_extra']
            break
            
    costo_personale = cuochi_extra * config['costo_cuoco_extra']
    costi_vivi_totali = costo_cibo + costo_personale
    prezzo_pulito = costi_vivi_totali + config['guadagno_minimo_gestore']
    prezzo_cliente_finale = prezzo_pulito * config['moltiplicatore_tasse']
    
    # Prepariamo il testo formattato elegante da mandare sul telefono
    messaggio = (
        f"📊 *NUOVO PREVENTIVO GENERATO*\n"
        f"🍽️ *Menu:* {menu['nome_menu']}\n"
        f"👥 *Ospiti:* {ospiti}\n"
        f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        f"💰 *Materie Prime:* {costo_cibo}€\n"
        f"👨‍🍳 *Cuochi Extra:* {cuochi_extra} ({costo_personale}€)\n"
        f"📉 *Costi Vivi Totali:* {costi_vivi_totali}€\n"
        f"📈 *Tuo Guadagno Netto:* {config['guadagno_minimo_gestore']}€\n"
        f"_____________________________\n"
        f"🚀 *PREZZO FINALE CLIENTE:* *{round(prezzo_cliente_finale, 2)}€*\n"
        f"💵 *Quota a persona:* {round(prezzo_cliente_finale / ospiti, 2)}€"
    )
    
    # Stampa sul terminale di GitHub e invia sullo smartphone
    print(messaggio)
    invia_telegram(messaggio)

if __name__ == "__main__":
    # Prendiamo i dati passati da GitHub Actions o usiamo il test standard
    import sys
    ospiti_input = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    menu_input = sys.argv[2] if len(sys.argv) > 2 else "menu-pesce"
    
    calcola(ospiti_input, menu_input)
