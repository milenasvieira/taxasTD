import os
import requests
import json
import time
import logging
import random
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# ========= CONFIGURAÇÕES =========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Símbolos: converte string separada por vírgula em lista
symbols_str = os.getenv("SYMBOLS", "tesouro-selic-01032031,tesouro-prefixado-com-juros-semestrais-01012037,tesouro-ipca-com-juros-semestrais-15082060")
SYMBOLS = [s.strip() for s in symbols_str.split(",") if s.strip()]

API_URL = "https://brapi.dev/api/v2/treasury/indicators"
STATE_FILE = "last_rates.json"
# =================================

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------- FUNÇÕES DE MOCK ----------
def generate_mock_rates(previous_state=None):
    """
    Gera dados mockados com variação aleatória.
    Se houver estado anterior, usa-o como base.
    """
    base_rates = {
        "Tesouro Selic 2031": {"buyRate": 13.50, "sellRate": 13.45, "maturity": "01/03/2031", "price": 1000.00},
        "Tesouro Prefixado c/ Juros Sem. 2037": {"buyRate": 12.80, "sellRate": 12.75, "maturity": "01/01/2037", "price": 950.00},
        "Tesouro IPCA+ c/ Juros Sem. 2060": {"buyRate": 6.20, "sellRate": 6.15, "maturity": "15/08/2060", "price": 1200.00}
    }

    if previous_state:
        for name in base_rates:
            if name in previous_state:
                delta = random.uniform(-0.02, 0.05)
                new_rate = previous_state[name]['buyRate'] + delta
                new_rate = max(0.5, min(25.0, new_rate))
                base_rates[name]['buyRate'] = round(new_rate, 4)
                base_rates[name]['sellRate'] = round(new_rate - 0.05, 4)
                base_rates[name]['price'] = round(1000 + random.uniform(-50, 50), 2)

    mock_results = []
    for idx, (name, data) in enumerate(base_rates.items()):
        symbol = SYMBOLS[idx] if idx < len(SYMBOLS) else f"unknown-{idx}"
        mock_results.append({
            "symbol": symbol,
            "shortName": name,
            "buyRate": data['buyRate'],
            "sellRate": data['sellRate'],
            "maturityDate": data['maturity'],
            "buyPrice": data['price'],
            "rateInfo": {"description": "Taxa de compra"}
        })
    return {"results": mock_results}

# ---------- FUNÇÃO PRINCIPAL DE OBTENÇÃO DE DADOS ----------
def get_current_rates():
    if MOCK_MODE:
        logging.info("🔮 Usando dados MOCKADOS (variação aleatória).")
        previous = load_state()
        previous_rates = {name: data for name, data in previous.items()}
        mock_data = generate_mock_rates(previous_rates)
        rates = {}
        for item in mock_data['results']:
            name = item.get('shortName') or item.get('name') or item['symbol']
            rates[name] = {
                'symbol': item['symbol'],
                'buyRate': float(item['buyRate']),
                'sellRate': float(item['sellRate']),
                'maturity': item['maturityDate'],
                'price': float(item['buyPrice']),
                'rateInfo': item.get('rateInfo', {})
            }
        return rates
    else:
        params = {"symbols": ",".join(SYMBOLS)}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            response = requests.get(API_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = {}
            for item in data.get('results', []):
                name = item.get('shortName') or item.get('name') or item['symbol']
                rates[name] = {
                    'symbol': item['symbol'],
                    'buyRate': float(item.get('buyRate', 0)),
                    'sellRate': float(item.get('sellRate', 0)),
                    'maturity': item.get('maturityDate', 'N/A'),
                    'price': float(item.get('buyPrice', 0)),
                    'rateInfo': item.get('rateInfo', {})
                }
            return rates
        except Exception as e:
            logging.error(f"Erro na API brapi.dev: {e}")
            return None

# ---------- FUNÇÕES AUXILIARES ----------
def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=payload, timeout=5).raise_for_status()
    except Exception as e:
        logging.error(f"Falha no envio: {e}")

def check_alerts(current, previous):
    alerts = []
    for name, data in current.items():
        if name not in previous:
            continue
        curr = data['buyRate']
        prev = previous[name]['buyRate']
        if curr > prev + 0.001:
            diff = curr - prev
            rate_type = data.get('rateInfo', {}).get('description', 'taxa')
            alerts.append(
                f"📈 <b>{name}</b>\n"
                f"{rate_type}: {curr:.4f}% (antes {prev:.4f}%)\n"
                f"Aumento: <b>{diff:.4f} p.p.</b>\n"
                f"Venc: {data['maturity']} | Preço: R$ {data['price']:.2f}"
            )
    return alerts

# ---------- LOOP PRINCIPAL ----------
def main():
    logging.info(f"Iniciando monitor - {'MOCK' if MOCK_MODE else 'REAL'} mode")
    logging.info(f"Títulos monitorados: {', '.join(SYMBOLS)}")
    logging.info(f"Intervalo de checagem: {CHECK_INTERVAL}s")
    previous = load_state()
    
    while True:
        logging.info("Buscando taxas...")
        current = get_current_rates()
        if current is None:
            logging.warning("Falha ao obter dados. Tentando novamente no próximo ciclo.")
            time.sleep(CHECK_INTERVAL)
            continue
        
        alerts = check_alerts(current, previous)
        if alerts:
            msg = "🚨 <b>AUMENTO NAS TAXAS!</b>\n\n" + "\n\n".join(alerts)
            send_alert(msg)
            logging.info(f"{len(alerts)} alerta(s) enviado(s).")
        else:
            logging.info("Nenhum aumento relevante detectado.")
        
        save_state(current)
        previous = current
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()