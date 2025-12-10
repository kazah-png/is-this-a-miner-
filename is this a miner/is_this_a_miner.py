# "is this a miner?" - ASCII crypto simulator
# © 2025 KAZAH
#
# Nota: Este programa NO mina criptomonedas reales, NO accede a tus datos,
# y NO es un virus. Es sólo un juego de simulación en texto.

import os
import random
import json
import math
import time
from collections import deque
from datetime import date

SAVE_FILE = "is_this_a_miner_save.json"

# ===========================
#   CONFIGURACIÓN PRINCIPAL
# ===========================

COINS_CONFIG = {
    "BTC":  {"price": 45000.0, "vol": 0.035, "reward": 0.00008},
    "ETH":  {"price": 2600.0,  "vol": 0.04,  "reward": 0.0009},
    "USDT": {"price": 1.0,     "vol": 0.005, "reward": 0.0},   # stable, no se mina
    "BNB":  {"price": 350.0,   "vol": 0.045, "reward": 0.0003},
    "XRP":  {"price": 1.2,     "vol": 0.06,  "reward": 0.005},
    "SOL":  {"price": 120.0,   "vol": 0.07,  "reward": 0.001},
    "USDC": {"price": 1.0,     "vol": 0.004, "reward": 0.0},
    "DOGE": {"price": 0.25,    "vol": 0.09,  "reward": 0.03},
    "TRX":  {"price": 0.12,    "vol": 0.06,  "reward": 0.01},
    "ADA":  {"price": 0.8,     "vol": 0.06,  "reward": 0.008},
    "LTC":  {"price": 130.0,   "vol": 0.05,  "reward": 0.0007},
    "BCH":  {"price": 300.0,   "vol": 0.055, "reward": 0.0004},
    "XLM":  {"price": 0.3,     "vol": 0.07,  "reward": 0.01},
    "AVAX": {"price": 40.0,    "vol": 0.07,  "reward": 0.002},
    "LINK": {"price": 20.0,    "vol": 0.06,  "reward": 0.002},
    "MATIC":{"price": 1.5,     "vol": 0.065, "reward": 0.009},
    "DOT":  {"price": 10.0,    "vol": 0.06,  "reward": 0.004},
    "UNI":  {"price": 8.0,     "vol": 0.06,  "reward": 0.004},
    "SHIB": {"price": 0.00003, "vol": 0.12,  "reward": 200.0},
    "TON":  {"price": 7.0,     "vol": 0.065, "reward": 0.003},
}

PRICE_HISTORY = {
    symbol: deque(maxlen=80)
    for symbol in COINS_CONFIG.keys()
}
for sym, data in COINS_CONFIG.items():
    PRICE_HISTORY[sym].append(data["price"])

# ===========================
#   ESTADO DEL JUGADOR
# ===========================

player = {
    "fiat": 0.0,
    "hash_rate_base": 1.0,
    "electricity_cost_base": 1.0,
    "tax_rate_base": 0.05,
    "wallet": {sym: 0.0 for sym in COINS_CONFIG.keys()},
    "ticks_played": 0,
    "unlocked_coins": ["BTC", "ETH", "DOGE"],
    "prestige_level": 0,
    "prestige_points": 0,
    "permanent_upgrades": {
        "hash_multiplier": 0,        # +10% hash por nivel
        "tax_reduction": 0,          # -2% impuestos absolutos por nivel
        "electricity_reduction": 0,  # -5% coste electricidad por nivel
        "better_events": 0,          # mejores probabilidades eventos
        "extra_unlocks": 0,          # arranque con más monedas
    },
    # Bots de trading automáticos (IDs activos)
    "trading_bots": [],             # se compran con puntos de prestigio
}

# ===========================
#   MISIONES
# ===========================

missions_state = {
    "daily": [],
    "weekly": [],
    "monthly": [],
    "unlock": [],
    "last_daily_reset": None,
    "last_weekly_reset": None,
    "last_monthly_reset": None,
}

# ===========================
#   MEJORAS TEMPORALES
# ===========================

UPGRADES = [
    {"name": "CPU overclock (+1 hash)", "hash_gain": 1.0, "cost": 100.0,
     "desc": "Overclock básico pero estable."},
    {"name": "GPU gamer (+5 hash)", "hash_gain": 5.0, "cost": 450.0,
     "desc": "Tu gráfica por fin hace algo útil."},
    {"name": "Rig de 6 GPUs (+20 hash)", "hash_gain": 20.0, "cost": 1600.0,
     "desc": "Un rig de segunda mano que aún aguanta."},
    {"name": "Granja minera (+100 hash)", "hash_gain": 100.0, "cost": 7500.0,
     "desc": "Nave industrial llena de rigs."},
    {"name": "Data center (+500 hash)", "hash_gain": 500.0, "cost": 32000.0,
     "desc": "Infraestructura profesional."},
    {"name": "IA de optimización (+1500 hash)", "hash_gain": 1500.0, "cost": 90000.0,
     "desc": "Algoritmo que exprime cada watt."},
]

UTILITY_UPGRADES = [
    {"name": "Contratar electricista", "effect": "reduce_electricity", "amount": 0.2, "cost": 1500.0,
     "desc": "Optimiza el cableado y baja la factura."},
    {"name": "Paneles solares", "effect": "reduce_electricity", "amount": 0.3, "cost": 5000.0,
     "desc": "Energía renovable para tu granja."},
    {"name": "Asesor fiscal", "effect": "reduce_taxes", "amount": 0.3, "cost": 8000.0,
     "desc": "Reduce tus impuestos legales."},
]

UNLOCK_UPGRADES = [
    {"name": "Desbloquear altcoins populares", "cost": 2000.0,
     "unlocks": ["BNB", "XRP", "SOL", "USDC"],
     "desc": "Acceso a grandes altcoins."},
    {"name": "DeFi y ecosistema", "cost": 7000.0,
     "unlocks": ["TRX", "ADA", "LTC", "BCH"],
     "desc": "Te metes en proyectos de ecosistema."},
    {"name": "GameFi & Meme season", "cost": 12000.0,
     "unlocks": ["XLM", "AVAX", "LINK", "MATIC", "DOT", "UNI", "SHIB", "TON"],
     "desc": "Ahora sí, season de memes y GameFi."},
]

# ===========================
#   MEJORAS PERMANENTES (PRESTIGIO)
# ===========================

PERMANENT_UPGRADES = [
    {"key": "hash_multiplier", "name": "Hash global +10%", "cost_points": 1,
     "desc": "Aumenta tu hash base un 10% para todas las runs."},
    {"key": "tax_reduction", "name": "Impuestos -2% absolutos", "cost_points": 1,
     "desc": "Vendes con menos mordida de Hacienda."},
    {"key": "electricity_reduction", "name": "Electricidad -5%", "cost_points": 1,
     "desc": "Menos coste fijo de energía por tick."},
    {"key": "better_events", "name": "Mejores eventos de mercado", "cost_points": 2,
     "desc": "Sube la probabilidad de bull runs y reduce crashes."},
    {"key": "extra_unlocks", "name": "Start avanzado", "cost_points": 2,
     "desc": "Empiezas con algunas altcoins extra desbloqueadas."},
]

# ===========================
#   BOTS DE TRADING (PRESTIGIO)
# ===========================

BOTS_CATALOG = [
    {
        "id": "btc_dca",
        "name": "Bot DCA BTC",
        "points_cost": 2,
        "desc": "Cada tick invierte el 2% de tu fiat en BTC (si tienes >$500)."
    },
    {
        "id": "vol_scalper",
        "name": "Bot Scalper de Volatilidad",
        "points_cost": 3,
        "desc": "Vende 10% de una cripto si sube >15% en un tick, y compra si baja >15%."
    },
    {
        "id": "stable_rebalancer",
        "name": "Bot Rebalanceador a Stable",
        "points_cost": 3,
        "desc": "Si tu portfolio sube mucho, rebalancea parte a USDT automáticamente."
    },
]

# ===========================
#   UTILIDADES BÁSICAS
# ===========================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header_text():
    return r"""
  ██╗███████╗    ███████╗████████╗██╗  ██╗██╗   ██╗
  ██║██╔════╝    ██╔════╝╚══██╔══╝██║ ██╔╝╚██╗ ██╔╝
  ██║███████╗    ███████╗   ██║   █████╔╝  ╚████╔╝ 
  ██║╚════██║    ╚════██║   ██║   ██╔═██╗   ╚██╔╝  
  ██║███████║    ███████║   ██║   ██║  ██╗   ██║   
  ╚═╝╚══════╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

             "is this a miner?" - Crypto Simulator
                       © 2025 KAZAH
    """


def effective_hash_rate():
    base = player["hash_rate_base"]
    mult_from_perm = 1.0 + player["permanent_upgrades"]["hash_multiplier"] * 0.10
    mult_from_prestige = 1.0 + player["prestige_level"] * 0.5
    return base * mult_from_perm * mult_from_prestige


def effective_electricity_cost():
    base = player["electricity_cost_base"]
    base *= (1.0 - player["permanent_upgrades"]["electricity_reduction"] * 0.05)
    if base < 0:
        base = 0
    return base


def effective_tax_rate():
    base = player["tax_rate_base"]
    base -= player["permanent_upgrades"]["tax_reduction"] * 0.02
    if base < 0:
        base = 0
    return base


def total_portfolio_value():
    total = player["fiat"]
    for sym, amount in player["wallet"].items():
        total += amount * COINS_CONFIG[sym]["price"]
    return total


def market_sentiment_bar():
    history = list(PRICE_HISTORY["BTC"])
    if len(history) < 2:
        return "[----------] neutro"
    start = history[0]
    end = history[-1]
    change = (end - start) / max(start, 1e-9)
    slots = 10
    val = (change + 0.5) / 1.0
    val = max(0.0, min(1.0, val))
    filled = int(round(val * slots))
    bar = "[" + "#" * filled + "-" * (slots - filled) + "]"
    if change > 0.1:
        label = "alcista"
    elif change < -0.1:
        label = "bajista"
    else:
        label = "lateral"
    return f"{bar} {label} ({change*100:+.1f}%)"


def short_price_ticker():
    top = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE"]
    parts = []
    for s in top:
        p = COINS_CONFIG[s]["price"]
        parts.append(f"{s}: {p:,.2f}")
    return " | ".join(parts)


def show_missions_brief():
    def summarize(lst, label):
        active = [m for m in lst if not m["claimed"]]
        if not active:
            return f"{label}: todas completadas ✅"
        parts = []
        for m in active[:2]:
            if m["type"] in ("mine_ticks", "mine_coin"):
                parts.append(f"- {m['name']} ({m['progress']:.2f}/{m['target']})")
            elif m["type"] == "reach_portfolio":
                parts.append(f"- {m['name']} (actual: {m['progress']:.2f})")
            else:
                parts.append(f"- {m['name']}")
        return f"{label}:\n " + "\n ".join(parts)

    print("Misiones (resumen):")
    print(summarize(missions_state["daily"], "Diarias"))
    print(summarize(missions_state["weekly"], "Semanales"))
    print(summarize(missions_state["monthly"], "Mensuales"))
    print(summarize(missions_state["unlock"], "Desbloqueo"))


def bots_summary():
    if not player["trading_bots"]:
        return "Bots activos: ninguno"
    names = []
    for bot in BOTS_CATALOG:
        if bot["id"] in player["trading_bots"]:
            names.append(bot["name"])
    if not names:
        return "Bots activos: ninguno"
    return "Bots activos: " + ", ".join(names)


def show_dashboard(extra_lines=None):
    clear()
    print(header_text())
    print(f"Fecha real: {date.today().isoformat()}   Ticks jugados: {player['ticks_played']}")
    print("-" * 80)
    print(f"Prestigio: {player['prestige_level']}   Puntos de prestigio: {player['prestige_points']}")
    print(f"Hash efectivo: {effective_hash_rate():.2f} H/s   "
          f"Electricidad/tick: ${effective_electricity_cost():.2f}   "
          f"Impuestos: {effective_tax_rate()*100:.1f}%")
    print(f"Valor total portfolio: ${total_portfolio_value():,.2f}")
    print("-" * 80)
    print("Mercado (BTC histórico):", market_sentiment_bar())
    print("Ticker:", short_price_ticker())
    print("-" * 80)
    print("Wallet (criptos desbloqueadas):")
    for sym in player["unlocked_coins"]:
        amount = player["wallet"][sym]
        price = COINS_CONFIG[sym]["price"]
        value = amount * price
        print(f"  {sym:5s}  {amount:,.8f}  x ${price:,.4f}  = ${value:,.2f}")
    print("-" * 80)
    show_missions_brief()
    print("-" * 80)
    print(bots_summary())
    if extra_lines:
        print("-" * 80)
        for line in extra_lines:
            print(line)
    print("-" * 80)
    print("Disclaimer: Este juego es sólo una simulación. No mina criptomonedas reales,")
    print("no accede a información sensible ni actúa como virus. © KAZAH")
    print("-" * 80)


# ===========================
#   INTRO TIPO VIRUS + DISCLAIMER
# ===========================

def intro_sequence():
    clear()
    print("Cargando módulo: system32_hook.dll ...")
    time.sleep(0.6)
    print("Iniciando escaneo de discos... [C:] [D:] [E:]")
    time.sleep(0.7)
    print("Encontrando claves privadas... (0/∞)")
    time.sleep(0.8)
    print("Inyectando minero en procesos críticos...")
    time.sleep(0.9)
    print("\n>>> ESPERA...")
    time.sleep(1.2)
    clear()
    print(header_text())
    print("TRANQUILO/A 😄")
    print("\nEste programa *NO* es un virus, *NO* mina nada real,")
    print("*NO* accede a tus archivos ni a datos personales.")
    print("\nEs simplemente un simulador de minería y trading de criptomonedas")
    print("en modo texto para divertirse / experimentar.")
    print("\nSi cierras esta ventana, el programa se detiene y ya está.")
    print("\n© 2025 KAZAH\n")
    input("Pulsa Enter para comenzar el juego...")

# ===========================
#   GUARDAR / CARGAR
# ===========================

def save_game():
    data = {
        "player": player,
        "coins": COINS_CONFIG,
        "missions": missions_state,
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        input("Partida guardada correctamente. Pulsa Enter para continuar...")
    except Exception as e:
        input(f"Error al guardar: {e}. Pulsa Enter para continuar...")


def load_game():
    global player, COINS_CONFIG, missions_state
    if not os.path.exists(SAVE_FILE):
        input("No hay partida guardada. Pulsa Enter para continuar...")
        return
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        player = data["player"]
        for sym, info in data["coins"].items():
            if sym in COINS_CONFIG:
                COINS_CONFIG[sym]["price"] = info["price"]
        missions_state = data.get("missions", missions_state)
        input("Partida cargada correctamente. Pulsa Enter para continuar...")
    except Exception as e:
        input(f"Error al cargar: {e}. Pulsa Enter para continuar...")

# ===========================
#   MISIONES
# ===========================

def mission_template_daily():
    v1 = 200 + random.randint(0, 300)
    v2 = 5000 + random.randint(0, 10000)
    return [
        {"id": "d_ticks", "scope": "daily", "name": f"Minar {v1} ticks",
         "type": "mine_ticks", "target": v1, "progress": 0, "completed": False, "claimed": False,
         "reward_points": 1},
        {"id": "d_portfolio", "scope": "daily", "name": f"Alcanzar ${v2} de valor total",
         "type": "reach_portfolio", "target": v2, "progress": 0, "completed": False, "claimed": False,
         "reward_points": 1},
    ]


def mission_template_weekly():
    v1 = 2000 + random.randint(0, 2000)
    v2 = 0.01 + random.random() * 0.05
    return [
        {"id": "w_ticks", "scope": "weekly", "name": f"Minar {v1} ticks totales",
         "type": "mine_ticks", "target": v1, "progress": 0, "completed": False, "claimed": False,
         "reward_points": 2},
        {"id": "w_btc", "scope": "weekly", "name": f"Acumular {v2:.4f} BTC",
         "type": "mine_coin", "coin": "BTC", "target": v2, "progress": 0, "completed": False,
         "claimed": False, "reward_points": 2},
    ]


def mission_template_monthly():
    v1 = 100000 + random.randint(0, 100000)
    return [
        {"id": "m_portfolio", "scope": "monthly", "name": f"Alcanzar ${v1} de valor total",
         "type": "reach_portfolio", "target": v1, "progress": 0, "completed": False, "claimed": False,
         "reward_points": 3},
    ]


def mission_template_unlock():
    return [
        {"id": "u_unlock_alt", "scope": "unlock",
         "name": "Desbloquear al menos 1 pack de altcoins",
         "type": "unlock_any", "target": 1, "progress": 0, "completed": False, "claimed": False,
         "reward_points": 1},
    ]


def reset_missions_if_needed():
    today = date.today()
    today_str = today.isoformat()

    if missions_state["last_daily_reset"] != today_str:
        missions_state["daily"] = mission_template_daily()
        missions_state["last_daily_reset"] = today_str

    week_id = f"{today.isocalendar().year}-W{today.isocalendar().week}"
    if missions_state["last_weekly_reset"] != week_id:
        missions_state["weekly"] = mission_template_weekly()
        missions_state["last_weekly_reset"] = week_id

    month_id = f"{today.year}-{today.month}"
    if missions_state["last_monthly_reset"] != month_id:
        missions_state["monthly"] = mission_template_monthly()
        missions_state["last_monthly_reset"] = month_id

    if not missions_state["unlock"]:
        missions_state["unlock"] = mission_template_unlock()


def update_missions_on_event(event_type, data=None):
    if data is None:
        data = {}
    all_lists = (
        missions_state["daily"] +
        missions_state["weekly"] +
        missions_state["monthly"] +
        missions_state["unlock"]
    )
    for m in all_lists:
        if m["completed"]:
            continue
        mtype = m["type"]
        if mtype == "mine_ticks" and event_type == "ticks_mined":
            m["progress"] += data.get("ticks", 0)
        elif mtype == "reach_portfolio" and event_type == "portfolio_check":
            val = data.get("value", 0)
            if val > m.get("progress", 0):
                m["progress"] = val
        elif mtype == "mine_coin" and event_type == "coin_mined":
            if data.get("coin") == m.get("coin"):
                m["progress"] += data.get("amount", 0)
        elif mtype == "unlock_any" and event_type == "coin_pack_unlocked":
            m["progress"] = 1

        if mtype in ("mine_ticks", "mine_coin"):
            if m["progress"] >= m["target"]:
                m["completed"] = True
        elif mtype == "reach_portfolio":
            if m["progress"] >= m["target"]:
                m["completed"] = True
        elif mtype == "unlock_any":
            if m["progress"] >= m["target"]:
                m["completed"] = True


def claim_completed_missions():
    all_lists = [
        ("Diarias", missions_state["daily"]),
        ("Semanales", missions_state["weekly"]),
        ("Mensuales", missions_state["monthly"]),
        ("Desbloqueo", missions_state["unlock"]),
    ]
    gained = 0
    for _, lst in all_lists:
        for m in lst:
            if m["completed"] and not m["claimed"]:
                player["prestige_points"] += m["reward_points"]
                gained += m["reward_points"]
                m["claimed"] = True
    show_dashboard([f"Has reclamado {gained} puntos de prestigio en total."])
    input("Pulsa Enter para continuar...")


def missions_menu():
    while True:
        show_dashboard()
        print("=== MENÚ DE MISIONES ===")
        print("1. Ver misiones completas y reclamar puntos")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "0":
            return
        elif choice == "1":
            claim_completed_missions()

# ===========================
#   MERCADO Y PRECIOS
# ===========================

def apply_market_events():
    roll = random.random()
    better = player["permanent_upgrades"]["better_events"]
    good_bias = better * 0.01

    if roll < 0.03 + good_bias:
        factor = random.uniform(1.05, 1.35)
        for sym in COINS_CONFIG:
            COINS_CONFIG[sym]["price"] *= factor
        print("\n*** EVENTO: BULL RUN GLOBAL 🚀! Los precios suben fuerte. ***")
    elif roll < 0.06:
        factor = random.uniform(0.6, 0.85)
        for sym in COINS_CONFIG:
            COINS_CONFIG[sym]["price"] *= factor
        print("\n*** EVENTO: CRASH DEL MERCADO 💥! Todo se viene abajo. ***")
    elif roll < 0.09:
        sym = random.choice(list(COINS_CONFIG.keys()))
        factor = random.uniform(0.5, 0.8)
        COINS_CONFIG[sym]["price"] *= factor
        print(f"\n*** EVENTO: FUD sobre {sym}! Su precio cae fuerte. ***")
    elif roll < 0.12 + good_bias:
        sym = random.choice(list(COINS_CONFIG.keys()))
        factor = random.uniform(1.2, 1.6)
        COINS_CONFIG[sym]["price"] *= factor
        print(f"\n*** EVENTO: NOTICIA POSITIVA en {sym}! Su precio despega. ***")


def realistic_price_step(price, vol):
    mu = 0.0
    sigma = vol
    change = random.gauss(mu, sigma)
    new_price = price * math.exp(change)
    if new_price < 0.00000001:
        new_price = 0.00000001
    return new_price

# ===========================
#   BOTS DE TRADING
# ===========================

def run_trading_bots():
    """Ejecuta la lógica de todos los bots activos."""
    if not player["trading_bots"]:
        return

    # Bot DCA BTC: invierte 2% del fiat si hay > 500$
    if "btc_dca" in player["trading_bots"]:
        if player["fiat"] > 500:
            fiat_to_spend = player["fiat"] * 0.02
            price = COINS_CONFIG["BTC"]["price"]
            btc_amount = fiat_to_spend / price
            player["fiat"] -= fiat_to_spend
            player["wallet"]["BTC"] += btc_amount

    # Bot Scalper de Volatilidad
    if "vol_scalper" in player["trading_bots"]:
        for sym in player["unlocked_coins"]:
            history = list(PRICE_HISTORY[sym])
            if len(history) < 2:
                continue
            last = history[-1]
            prev = history[-2]
            change = (last - prev) / max(prev, 1e-9)
            # Subida fuerte -> vende 10% de la posición
            if change > 0.15:
                amount = player["wallet"][sym] * 0.10
                if amount > 0:
                    gross = amount * last
                    tax = gross * effective_tax_rate()
                    net = gross - tax
                    player["wallet"][sym] -= amount
                    player["fiat"] += net
            # Bajada fuerte -> compra 3% del fiat disponible
            elif change < -0.15 and player["fiat"] > 200:
                fiat_to_spend = player["fiat"] * 0.03
                buy_amount = fiat_to_spend / last
                player["fiat"] -= fiat_to_spend
                player["wallet"][sym] += buy_amount

    # Bot Rebalanceador a Stable
    if "stable_rebalancer" in player["trading_bots"]:
        total_val = total_portfolio_value()
        if total_val > 20000:  # sólo actúa si ya tienes algo decente
            # Si fiat < 20% del total, vende un poco a USDT
            if player["fiat"] < total_val * 0.2:
                for sym in player["unlocked_coins"]:
                    if sym in ("USDT", "USDC"):
                        continue
                    amount = player["wallet"][sym]
                    if amount <= 0:
                        continue
                    sell_amount = amount * 0.05  # 5% de cada cripto
                    price = COINS_CONFIG[sym]["price"]
                    gross = sell_amount * price
                    tax = gross * effective_tax_rate()
                    net = gross - tax
                    player["wallet"][sym] -= sell_amount
                    # Convertimos a USDT directamente
                    usdt_price = COINS_CONFIG["USDT"]["price"]
                    usdt_amount = net / usdt_price
                    player["wallet"]["USDT"] += usdt_amount

# ===========================
#   UPDATE TICKS (PRECIOS + MINADO + BOTS)
# ===========================

def update_prices_and_mine(ticks=1):
    for _ in range(ticks):
        player["ticks_played"] += 1
        reset_missions_if_needed()
        apply_market_events()

        hr = effective_hash_rate()

        for sym, data in COINS_CONFIG.items():
            old_price = data["price"]
            new_price = realistic_price_step(old_price, data["vol"])
            data["price"] = new_price
            PRICE_HISTORY[sym].append(new_price)

            if data["reward"] > 0 and sym in player["unlocked_coins"]:
                mined = hr * data["reward"] * random.uniform(0.8, 1.2)
                player["wallet"][sym] += mined
                update_missions_on_event("coin_mined", {"coin": sym, "amount": mined})

        # Bots de trading automáticos (después de actualizar precios)
        run_trading_bots()

        # Coste de electricidad
        player["fiat"] -= effective_electricity_cost()
        if player["fiat"] < -1_000_000:
            player["fiat"] = -1_000_000

        update_missions_on_event("ticks_mined", {"ticks": 1})
        update_missions_on_event("portfolio_check", {"value": total_portfolio_value()})

# ===========================
#   MERCADO: COMPRAR / VENDER
# ===========================

def select_unlocked_coin(prompt="Selecciona cripto: "):
    symbols = list(player["unlocked_coins"])
    for i, sym in enumerate(symbols, start=1):
        print(f"{i}. {sym} (precio: ${COINS_CONFIG[sym]['price']:.4f})")
    print("0. Cancelar")
    choice = input(f"\n{prompt}").strip()
    if choice == "0":
        return None
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(symbols):
            return None
        return symbols[idx]
    except:
        return None


def sell_crypto():
    show_dashboard()
    print("=== VENDER CRIPTO ===\n")
    sym = select_unlocked_coin()
    if sym is None:
        input("Operación cancelada. Pulsa Enter...")
        return

    max_amount = player["wallet"][sym]
    print(f"\nTienes {max_amount:.12f} {sym}")
    amount_str = input("¿Cuánto quieres vender? (número o 'todo'): ").strip().lower()
    if amount_str == "todo":
        amount = max_amount
    else:
        try:
            amount = float(amount_str)
        except:
            input("Cantidad inválida. Pulsa Enter...")
            return

    if amount <= 0 or amount > max_amount:
        input("Cantidad fuera de rango. Pulsa Enter...")
        return

    price = COINS_CONFIG[sym]["price"]
    gross = amount * price
    tax_rate = effective_tax_rate()
    tax = gross * tax_rate
    net = gross - tax

    player["wallet"][sym] -= amount
    player["fiat"] += net

    show_dashboard([f"Has vendido {amount:.8f} {sym} por ${net:.2f} (impuestos ${tax:.2f})."])
    input("Pulsa Enter para continuar...")


def buy_crypto():
    show_dashboard()
    print("=== COMPRAR CRIPTO ===\n")
    sym = select_unlocked_coin(prompt="¿Qué cripto quieres comprar?: ")
    if sym is None:
        input("Operación cancelada. Pulsa Enter...")
        return

    print(f"\nDinero disponible: ${player['fiat']:.2f}")
    amount_str = input("¿Cuánto fiat quieres gastar?: ").strip()
    try:
        fiat_to_spend = float(amount_str)
    except:
        input("Cantidad inválida. Pulsa Enter...")
        return

    if fiat_to_spend <= 0 or fiat_to_spend > player["fiat"]:
        input("Cantidad fuera de rango. Pulsa Enter...")
        return

    price = COINS_CONFIG[sym]["price"]
    crypto_amount = fiat_to_spend / price
    player["fiat"] -= fiat_to_spend
    player["wallet"][sym] += crypto_amount

    show_dashboard([f"Has comprado {crypto_amount:.8f} {sym}."])
    input("Pulsa Enter para continuar...")


def market_menu():
    while True:
        show_dashboard()
        print("=== MERCADO ===")
        print("1. Vender cripto por fiat")
        print("2. Comprar cripto con fiat")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "1":
            sell_crypto()
        elif choice == "2":
            buy_crypto()
        else:
            return

# ===========================
#   MEJORAS TEMPORALES
# ===========================

def hash_upgrades_menu():
    show_dashboard()
    print("=== MEJORAS DE HASH RATE (RUN ACTUAL) ===\n")
    for i, u in enumerate(UPGRADES, start=1):
        print(f"{i}. {u['name']:<30} | +{u['hash_gain']:<6.1f} hash | Coste: ${u['cost']:<10.2f}")
        print(f"   -> {u['desc']}")
    print("0. Volver")
    choice = input("\nOpción: ").strip()
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        u = UPGRADES[idx]
    except:
        input("Opción inválida. Pulsa Enter...")
        return
    if player["fiat"] < u["cost"]:
        input("No tienes suficiente dinero. Pulsa Enter...")
        return
    player["fiat"] -= u["cost"]
    player["hash_rate_base"] += u["hash_gain"]
    show_dashboard([f"Has comprado {u['name']}."])
    input("Pulsa Enter para continuar...")


def utility_upgrades_menu():
    show_dashboard()
    print("=== MEJORAS DE UTILIDAD (RUN ACTUAL) ===\n")
    for i, u in enumerate(UTILITY_UPGRADES, start=1):
        print(f"{i}. {u['name']:<30} | Efecto: {u['effect']} {u['amount']*100:.0f}% | Coste: ${u['cost']:.2f}")
        print(f"   -> {u['desc']}")
    print("0. Volver")
    choice = input("\nOpción: ").strip()
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        u = UTILITY_UPGRADES[idx]
    except:
        input("Opción inválida. Pulsa Enter...")
        return
    if player["fiat"] < u["cost"]:
        input("No tienes suficiente dinero. Pulsa Enter...")
        return
    player["fiat"] -= u["cost"]
    if u["effect"] == "reduce_electricity":
        player["electricity_cost_base"] *= (1 - u["amount"])
        if player["electricity_cost_base"] < 0:
            player["electricity_cost_base"] = 0
        msg = f"Nuevo coste base de electricidad: ${player['electricity_cost_base']:.2f}"
    elif u["effect"] == "reduce_taxes":
        player["tax_rate_base"] *= (1 - u["amount"])
        if player["tax_rate_base"] < 0:
            player["tax_rate_base"] = 0
        msg = f"Nuevo tipo impositivo base: {player['tax_rate_base']*100:.1f}%"
    else:
        msg = "Mejora aplicada."
    show_dashboard([msg])
    input("Pulsa Enter para continuar...")


def unlocks_menu():
    show_dashboard()
    print("=== DESBLOQUEO DE NUEVAS CRIPTOS (RUN ACTUAL) ===\n")
    for i, u in enumerate(UNLOCK_UPGRADES, start=1):
        already_unlocked = all(sym in player["unlocked_coins"] for sym in u["unlocks"])
        status = "(YA DESBLOQUEADAS)" if already_unlocked else ""
        print(f"{i}. {u['name']} {status}")
        print(f"   Coste: ${u['cost']:.2f}")
        print(f"   Desbloquea: {', '.join(u['unlocks'])}")
        print(f"   -> {u['desc']}\n")
    print("0. Volver")
    choice = input("Opción: ").strip()
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        u = UNLOCK_UPGRADES[idx]
    except:
        input("Opción inválida. Pulsa Enter...")
        return
    already_unlocked = all(sym in player["unlocked_coins"] for sym in u["unlocks"])
    if already_unlocked:
        input("Ya tienes todas estas criptos desbloqueadas. Pulsa Enter...")
        return
    if player["fiat"] < u["cost"]:
        input("No tienes suficiente dinero. Pulsa Enter...")
        return
    player["fiat"] -= u["cost"]
    for sym in u["unlocks"]:
        if sym not in player["unlocked_coins"]:
            player["unlocked_coins"].append(sym)
    update_missions_on_event("coin_pack_unlocked", {})
    show_dashboard(["Nuevas criptos desbloqueadas."])
    input("Pulsa Enter para continuar...")


def upgrades_menu():
    while True:
        show_dashboard()
        print("=== TIENDA DE MEJORAS (RUN ACTUAL) ===")
        print("1. Mejoras de hash rate (hardware)")
        print("2. Mejoras de utilidad (electricidad / impuestos)")
        print("3. Desbloquear nuevas criptos")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "1":
            hash_upgrades_menu()
        elif choice == "2":
            utility_upgrades_menu()
        elif choice == "3":
            unlocks_menu()
        else:
            return

# ===========================
#   GRÁFICOS ASCII
# ===========================

def draw_price_graph(symbol):
    show_dashboard()
    print(f"=== GRÁFICO ASCII DE {symbol} ===\n")
    history = list(PRICE_HISTORY[symbol])
    if not history:
        input("No hay datos suficientes. Pulsa Enter...")
        return
    max_price = max(history)
    min_price = min(history)
    span = max_price - min_price if max_price != min_price else 1.0
    max_width = 60
    for price in history:
        norm = (price - min_price) / span
        bar_len = int(norm * max_width)
        bar = "#" * bar_len if bar_len > 0 else "."
        print(f"{price:12.6f} | {bar}")
    print(f"\nMin: {min_price:.6f}  Max: {max_price:.6f}")
    input("\nPulsa Enter para volver...")


def graphs_menu():
    while True:
        show_dashboard()
        print("=== GRÁFICOS DE PRECIOS ===\n")
        print("Elige una cripto para ver su gráfico ASCII:\n")
        symbols = list(player["unlocked_coins"])
        for i, sym in enumerate(symbols, start=1):
            print(f"{i}. {sym}")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "0":
            return
        try:
            idx = int(choice) - 1
            symbol = symbols[idx]
        except:
            input("Opción inválida. Pulsa Enter...")
            continue
        draw_price_graph(symbol)

# ===========================
#   PRESTIGIO + BOTS (PUNTOS)
# ===========================

def do_prestige_reset():
    total_val = total_portfolio_value()
    points_gained = int(total_val // 50000)
    if points_gained <= 0:
        show_dashboard(["Tu valor es demasiado bajo para conseguir puntos de prestigio (mín ~50k)."])
        input("Pulsa Enter...")
        return
    player["prestige_points"] += points_gained
    player["prestige_level"] += 1

    player["fiat"] = 0.0
    player["wallet"] = {sym: 0.0 for sym in COINS_CONFIG.keys()}
    player["hash_rate_base"] = 1.0
    player["electricity_cost_base"] = 1.0
    player["tax_rate_base"] = 0.05
    player["ticks_played"] = 0
    player["unlocked_coins"] = ["BTC", "ETH", "DOGE"]

    missions_state["daily"] = []
    missions_state["weekly"] = []
    missions_state["monthly"] = []
    missions_state["unlock"] = []

    show_dashboard([
        f"Has hecho PRESTIGIO. Nuevo nivel: {player['prestige_level']}.",
        f"Has ganado {points_gained} puntos de prestigio (total: {player['prestige_points']}).",
    ])
    input("Pulsa Enter para continuar...")


def permanent_upgrades_menu():
    while True:
        show_dashboard()
        print("=== MEJORAS PERMANENTES DE PRESTIGIO ===")
        print(f"Puntos disponibles: {player['prestige_points']}")
        for i, u in enumerate(PERMANENT_UPGRADES, start=1):
            key = u["key"]
            level = player["permanent_upgrades"].get(key, 0)
            print(f"{i}. {u['name']} (nivel actual: {level})  Coste: {u['cost_points']} puntos")
            print(f"   -> {u['desc']}")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "0":
            return
        try:
            idx = int(choice) - 1
            u = PERMANENT_UPGRADES[idx]
        except:
            input("Opción inválida. Pulsa Enter...")
            continue
        if player["prestige_points"] < u["cost_points"]:
            input("No tienes puntos suficientes. Pulsa Enter...")
            continue
        player["prestige_points"] -= u["cost_points"]
        key = u["key"]
        player["permanent_upgrades"][key] = player["permanent_upgrades"].get(key, 0) + 1
        if key == "extra_unlocks":
            extras = ["BNB", "XRP", "SOL", "USDC", "TRX", "ADA"]
            for sym in extras:
                if sym not in player["unlocked_coins"]:
                    player["unlocked_coins"].append(sym)
        show_dashboard([f"Has subido de nivel la mejora permanente: {u['name']}"])
        input("Pulsa Enter para continuar...")


def trading_bots_menu():
    while True:
        show_dashboard()
        print("=== BOTS DE TRADING (PRESTIGIO) ===")
        print(f"Puntos de prestigio disponibles: {player['prestige_points']}")
        print("Bots disponibles:")
        for i, bot in enumerate(BOTS_CATALOG, start=1):
            owned = bot["id"] in player["trading_bots"]
            status = "ACTIVO" if owned else f"Disponible (coste: {bot['points_cost']} pts)"
            print(f"{i}. {bot['name']} [{status}]")
            print(f"   -> {bot['desc']}")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "0":
            return
        try:
            idx = int(choice) - 1
            bot = BOTS_CATALOG[idx]
        except:
            input("Opción inválida. Pulsa Enter...")
            continue
        if bot["id"] in player["trading_bots"]:
            input("Ya tienes este bot. Pulsa Enter...")
            continue
        if player["prestige_points"] < bot["points_cost"]:
            input("No tienes puntos de prestigio suficientes. Pulsa Enter...")
            continue
        player["prestige_points"] -= bot["points_cost"]
        player["trading_bots"].append(bot["id"])
        show_dashboard([f"Has comprado y activado el bot: {bot['name']}"])
        input("Pulsa Enter para continuar...")


def prestige_menu():
    while True:
        show_dashboard()
        print("=== MENÚ DE PRESTIGIO ===")
        total_val = total_portfolio_value()
        print(f"Valor total actual (fiat+cripto): ${total_val:,.2f}")
        print(f"Nivel de prestigio: {player['prestige_level']}   Puntos disponibles: {player['prestige_points']}")
        print("Multiplicador hash por prestigio: x{:.2f}".format(1 + player['prestige_level'] * 0.5))
        print()
        print("1. Reiniciar run (hacer PRESTIGIO y ganar puntos)")
        print("2. Gastar puntos en mejoras PERMANENTES")
        print("3. Comprar / gestionar bots de trading (automatización)")
        print("0. Volver")
        choice = input("\nOpción: ").strip()
        if choice == "1":
            do_prestige_reset()
        elif choice == "2":
            permanent_upgrades_menu()
        elif choice == "3":
            trading_bots_menu()
        else:
            return

# ===========================
#   MENÚ PRINCIPAL
# ===========================

def main_menu():
    reset_missions_if_needed()
    while True:
        show_dashboard()
        print("=== MENÚ PRINCIPAL ===")
        print("1. Minar (1 tick)")
        print("2. Minar x10 ticks")
        print("3. Minar x100 ticks")
        print("4. Mercado (comprar/vender)")
        print("5. Tienda de mejoras (run actual)")
        print("6. Ver gráficos de precios")
        print("7. Misiones (detalles / reclamar puntos)")
        print("8. Prestigio (reset + mejoras + bots)")
        print("9. Guardar partida")
        print("10. Cargar partida")
        print("0. Salir")
        choice = input("\nOpción: ").strip()
        if choice == "1":
            update_prices_and_mine(ticks=1)
        elif choice == "2":
            update_prices_and_mine(ticks=10)
        elif choice == "3":
            update_prices_and_mine(ticks=100)
        elif choice == "4":
            market_menu()
        elif choice == "5":
            upgrades_menu()
        elif choice == "6":
            graphs_menu()
        elif choice == "7":
            missions_menu()
        elif choice == "8":
            prestige_menu()
        elif choice == "9":
            save_game()
        elif choice == "10":
            load_game()
        elif choice == "0":
            show_dashboard(["Gracias por jugar a 'is this a miner?'."])
            break
        else:
            input("Opción inválida. Pulsa Enter...")

# ===========================
#   ENTRYPOINT
# ===========================

if __name__ == "__main__":
    intro_sequence()
    main_menu()
