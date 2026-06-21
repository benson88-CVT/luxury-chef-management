import json
import os
import urllib.request
import urllib.parse

def invia_telegram(testo):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Errore: Credenziali Telegram non trouvate nei Secrets.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': testo,
        'parse_mode': 'HTML'  # Passiamo a HTML che è molto più stabile
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
    
    # Testo pulito in HTML - Impossibile da rompere per Telegram
    messaggio = (
        f"<b>📊 NUOVO PREVENTIVO GENERATO</b>\n"
        f"🍽 <b>Menu:</b> {menu['nome_menu']}\n"
        f"👥 <b>Ospiti:</b> {ospiti}\n"
        f"-----------------------------\n"
        f"💰 <b>Materie Prime:</b> {costo_cibo}€\n"
        f"👨‍🍳 <b>Cuochi Extra:</b> {cuochi_extra} ({costo_personale}€)\n"
        f"📉 <b>Costi Vivi Totali:</b> {costi_vivi_totali}€\n"
        f"📈 <b>Tuo Guadagno Netto:</b> {config['guadagno_minimo_gestore']}€\n"
        f"-----------------------------\n"
        f"🚀 <b>PREZZO FINALE CLIENTE:</b> <b>{round(prezzo_cliente_finale, 2)}€</b>\n"
        f"💵 <b>Quota a persona:</b> {round(prezzo_cliente_finale / ospiti, 2)}€"
    )
    
    print(messaggio)
    invia_telegram(messaggio)

if __name__ == "__main__":
    import sys
    ospiti_input = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    menu_input = sys.argv[2] if len(sys.argv) > 2 else "menu-pesce"
    
    calcola(ospiti_input, menu_input)
