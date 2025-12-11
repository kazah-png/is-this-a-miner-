# "is this a miner?" - GUI crypto simulator
# © 2025 KAZAH
#
# Nota: Este programa NO mina criptomonedas reales, NO accede a tus datos,
# y NO es un virus. Es sólo un juego de simulación.

import os
import json
import math
import random
from collections import deque
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

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

LAST_EVENTS = deque(maxlen=10)

STAKING_CONFIG = {
    "ETH":   {"rate": 0.00015, "duration": 800},
    "ADA":   {"rate": 0.00018, "duration": 900},
    "SOL":   {"rate": 0.00016, "duration": 800},
    "MATIC": {"rate": 0.00018, "duration": 900},
    "DOT":   {"rate": 0.00017, "duration": 900},
}

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
        "hash_multiplier": 0,
        "tax_reduction": 0,
        "electricity_reduction": 0,
        "better_events": 0,
        "extra_unlocks": 0,
    },
    "trading_bots": [],
    "auto_mining": False,
    "auto_ticks_per_step": 10,
    "hack_protection": 0.0,
    "hardware_protection": 0.0,
    "stakes": [],
}

missions_state = {
    "daily": [],
    "weekly": [],
    "monthly": [],
    "unlock": [],
    "last_daily_reset": None,
    "last_weekly_reset": None,
    "last_monthly_reset": None,
}

UPGRADES = [
    {"name": "CPU overclock (+1 hash)", "hash_gain": 1.0, "cost": 100.0,
     "desc": "Aumenta un poco tu potencia de minado."},
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
     "desc": "Baja la factura eléctrica."},
    {"name": "Paneles solares", "effect": "reduce_electricity", "amount": 0.3, "cost": 5000.0,
     "desc": "Energía renovable para tu granja."},
    {"name": "Asesor fiscal", "effect": "reduce_taxes", "amount": 0.3, "cost": 8000.0,
     "desc": "Pagas menos impuestos al vender."},
    {"name": "Seguro cibernético", "effect": "hack_protect", "amount": 0.5, "cost": 8000.0,
     "desc": "Reduce pérdidas por hackeos."},
    {"name": "Contrato de mantenimiento", "effect": "hardware_protect", "amount": 0.5, "cost": 6000.0,
     "desc": "Reduce fallos de hardware."},
]

UNLOCK_UPGRADES = [
    {"name": "Altcoins populares", "cost": 2000.0,
     "unlocks": ["BNB", "XRP", "SOL", "USDC"],
     "desc": "Acceso a grandes altcoins."},
    {"name": "DeFi y ecosistema", "cost": 7000.0,
     "unlocks": ["TRX", "ADA", "LTC", "BCH"],
     "desc": "Te metes en ecosistemas potentes."},
    {"name": "GameFi & Meme season", "cost": 12000.0,
     "unlocks": ["XLM", "AVAX", "LINK", "MATIC", "DOT", "UNI", "SHIB", "TON"],
     "desc": "Season de memes y GameFi."},
]

PERMANENT_UPGRADES = [
    {"key": "hash_multiplier", "name": "Hash global +10%", "cost_points": 1,
     "desc": "Más potencia base en todas las partidas."},
    {"key": "tax_reduction", "name": "Impuestos -2% absolutos", "cost_points": 1,
     "desc": "Pagas menos impuestos al vender."},
    {"key": "electricity_reduction", "name": "Electricidad -5%", "cost_points": 1,
     "desc": "Menos coste fijo de energía."},
    {"key": "better_events", "name": "Mejores eventos de mercado", "cost_points": 2,
     "desc": "Más bull runs, menos crashes."},
    {"key": "extra_unlocks", "name": "Inicio avanzado", "cost_points": 2,
     "desc": "Empiezas con altcoins extra."},
]

BOTS_CATALOG = [
    {
        "id": "btc_dca",
        "name": "Bot DCA BTC",
        "points_cost": 2,
        "desc": "Invierte 2% del fiat en BTC cada tick si tienes >$500.",
    },
    {
        "id": "vol_scalper",
        "name": "Bot Scalper de Volatilidad",
        "points_cost": 3,
        "desc": "Opera en subidas/bajadas fuertes.",
    },
    {
        "id": "stable_rebalancer",
        "name": "Bot Rebalanceador a Stable",
        "points_cost": 3,
        "desc": "Va pasando parte a USDT cuando subes mucho.",
    },
]

# ===========================
#   LÓGICA DEL JUEGO
# ===========================

def effective_hash_rate():
    base = player["hash_rate_base"]
    mult_from_perm = 1.0 + player["permanent_upgrades"]["hash_multiplier"] * 0.10
    mult_from_prestige = 1.0 + player["prestige_level"] * 0.5
    return base * mult_from_perm * mult_from_prestige


def effective_electricity_cost():
    base = player["electricity_cost_base"]
    base *= (1.0 - player["permanent_upgrades"]["electricity_reduction"] * 0.05)
    return max(base, 0.0)


def effective_tax_rate():
    base = player["tax_rate_base"]
    base -= player["permanent_upgrades"]["tax_reduction"] * 0.02
    return max(base, 0.0)


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
    return f"{bar} {change*100:+.1f}% ({label})"


def short_price_ticker():
    top = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE"]
    parts = []
    for s in top:
        p = COINS_CONFIG[s]["price"]
        parts.append(f"{s}: {p:,.2f}")
    return " | ".join(parts)


def missions_summary_text():
    def summarize(lst, label):
        active = [m for m in lst if not m["claimed"]]
        if not active:
            return f"{label}: todas completadas ✅\n"
        parts = [f"{label}:\n"]
        for m in active[:3]:
            if m["type"] in ("mine_ticks", "mine_coin"):
                parts.append(f" - {m['name']} ({m['progress']:.2f}/{m['target']})")
            elif m["type"] == "reach_portfolio":
                parts.append(f" - {m['name']} (actual: {m['progress']:.2f})")
            else:
                parts.append(f" - {m['name']}")
        return "\n".join(parts) + "\n"

    text = ""
    text += summarize(missions_state["daily"], "Diarias")
    text += summarize(missions_state["weekly"], "Semanales")
    text += summarize(missions_state["monthly"], "Mensuales")
    text += summarize(missions_state["unlock"], "Desbloqueo")
    return text.strip()


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


def staking_summary():
    if not player["stakes"]:
        return "Staking activo: ninguno"
    by_coin = {}
    for s in player["stakes"]:
        by_coin.setdefault(s["coin"], 0.0)
        by_coin[s["coin"]] += s["amount"]
    parts = [f"{c}: {amt:.4f}" for c, amt in by_coin.items()]
    return "Staking activo: " + ", ".join(parts)


def ensure_player_defaults():
    player.setdefault("trading_bots", [])
    player.setdefault("auto_mining", False)
    player.setdefault("auto_ticks_per_step", 10)
    player.setdefault("hack_protection", 0.0)
    player.setdefault("hardware_protection", 0.0)
    player.setdefault("stakes", [])


# ---------- Guardar / Cargar ----------

def save_game():
    data = {
        "player": player,
        "coins": COINS_CONFIG,
        "missions": missions_state,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game():
    global missions_state
    if not os.path.exists(SAVE_FILE):
        raise FileNotFoundError("No hay partida guardada.")
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    player.update(data["player"])
    ensure_player_defaults()
    for sym, info in data["coins"].items():
        if sym in COINS_CONFIG:
            COINS_CONFIG[sym]["price"] = info["price"]
    missions_state.update(data.get("missions", missions_state))


# ---------- Misiones ----------

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
        {"id": "w_ticks", "scope": "weekly", "name": f"Minar {v1} ticks acumulados",
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
        missions_state["daily"]
        + missions_state["weekly"]
        + missions_state["monthly"]
        + missions_state["unlock"]
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
    gained = 0
    all_lists = (
        missions_state["daily"]
        + missions_state["weekly"]
        + missions_state["monthly"]
        + missions_state["unlock"]
    )
    for m in all_lists:
        if m["completed"] and not m["claimed"]:
            player["prestige_points"] += m["reward_points"]
            gained += m["reward_points"]
            m["claimed"] = True
    return gained


# ---------- Mercado y precios ----------

def apply_market_events():
    roll = random.random()
    better = player["permanent_upgrades"]["better_events"]
    good_bias = better * 0.01

    if roll < 0.03 + good_bias:
        factor = random.uniform(1.05, 1.35)
        for sym in COINS_CONFIG:
            COINS_CONFIG[sym]["price"] *= factor
        LAST_EVENTS.append("BULL RUN global 🚀 Los precios suben fuerte.")
    elif roll < 0.06:
        factor = random.uniform(0.6, 0.85)
        for sym in COINS_CONFIG:
            COINS_CONFIG[sym]["price"] *= factor
        LAST_EVENTS.append("CRASH del mercado 💥 Todo se desploma.")
    elif roll < 0.09:
        sym = random.choice(list(COINS_CONFIG.keys()))
        factor = random.uniform(0.5, 0.8)
        COINS_CONFIG[sym]["price"] *= factor
        LAST_EVENTS.append(f"FUD sobre {sym}, su precio cae.")
    elif roll < 0.12 + good_bias:
        sym = random.choice(list(COINS_CONFIG.keys()))
        factor = random.uniform(1.2, 1.6)
        COINS_CONFIG[sym]["price"] *= factor
        LAST_EVENTS.append(f"Noticias positivas en {sym}, su precio despega.")


def realistic_price_step(price, vol):
    mu = 0.0
    sigma = vol
    change = random.gauss(mu, sigma)
    new_price = price * math.exp(change)
    return max(new_price, 0.00000001)


# ---------- Eventos personales ----------

def player_events():
    roll = random.random()
    prot_hw = player.get("hardware_protection", 0.0)
    prot_hack = player.get("hack_protection", 0.0)

    # Fallo de hardware
    if roll < 0.002:
        severity = random.uniform(0.05, 0.25)
        effective = severity * (1 - prot_hw)
        if effective <= 0.01:
            return
        loss = player["hash_rate_base"] * effective
        player["hash_rate_base"] -= loss
        player["hash_rate_base"] = max(player["hash_rate_base"], 0.1)
        LAST_EVENTS.append(f"Fallo de hardware 🛠 pierdes {loss:.1f} de hash.")
    # Hackeo
    elif roll < 0.004:
        severity = random.uniform(0.1, 0.4)
        effective = severity * (1 - prot_hack)
        if effective <= 0.02:
            return
        if random.random() < 0.5 and player["fiat"] > 0:
            loss = player["fiat"] * effective
            player["fiat"] -= loss
            LAST_EVENTS.append(f"Hackeo 💻 pierdes ${loss:.2f} de fiat.")
        else:
            coins_with_balance = [s for s, a in player["wallet"].items() if a > 0]
            if not coins_with_balance:
                return
            sym = random.choice(coins_with_balance)
            loss = player["wallet"][sym] * effective
            player["wallet"][sym] -= loss
            LAST_EVENTS.append(f"Hackeo 💻 roban {loss:.8f} {sym}.")
    # Evento positivo
    elif roll < 0.005:
        bonus = random.uniform(200, 1500) * (1 + player["prestige_level"] * 0.2)
        player["fiat"] += bonus
        LAST_EVENTS.append(f"Recompensa inesperada 🎁 recibes ${bonus:.2f}.")


# ---------- Staking ----------

def process_stakes():
    if not player["stakes"]:
        return
    finished = []
    for s in player["stakes"]:
        if s["remaining_ticks"] <= 0:
            finished.append(s)
            continue
        gain = s["amount"] * s["rate_per_tick"]
        player["wallet"][s["coin"]] += gain
        s["remaining_ticks"] -= 1
        if s["remaining_ticks"] <= 0:
            finished.append(s)
    for s in finished:
        LAST_EVENTS.append(f"Staking completado ⛓ {s['amount']:.4f} {s['coin']}.")
    player["stakes"] = [s for s in player["stakes"] if s["remaining_ticks"] > 0]


def create_stake(sym, amount):
    if sym not in STAKING_CONFIG:
        raise ValueError("Esa moneda no admite staking.")
    if sym not in player["unlocked_coins"]:
        raise ValueError("No tienes esa moneda desbloqueada.")
    if amount <= 0:
        raise ValueError("Cantidad inválida.")
    if player["wallet"][sym] < amount:
        raise ValueError("No tienes suficiente saldo.")
    conf = STAKING_CONFIG[sym]
    stake = {
        "coin": sym,
        "amount": amount,
        "remaining_ticks": conf["duration"],
        "rate_per_tick": conf["rate"],
    }
    player["stakes"].append(stake)
    LAST_EVENTS.append(
        f"Inicias staking de {amount:.4f} {sym} por {conf['duration']} ticks."
    )


# ---------- Bots ----------

def run_trading_bots():
    if not player["trading_bots"]:
        return

    if "btc_dca" in player["trading_bots"]:
        if player["fiat"] > 500:
            fiat_to_spend = player["fiat"] * 0.02
            price = COINS_CONFIG["BTC"]["price"]
            btc_amount = fiat_to_spend / price
            player["fiat"] -= fiat_to_spend
            player["wallet"]["BTC"] += btc_amount

    if "vol_scalper" in player["trading_bots"]:
        for sym in player["unlocked_coins"]:
            history = list(PRICE_HISTORY[sym])
            if len(history) < 2:
                continue
            last = history[-1]
            prev = history[-2]
            change = (last - prev) / max(prev, 1e-9)
            if change > 0.15:
                amount = player["wallet"][sym] * 0.10
                if amount > 0:
                    gross = amount * last
                    tax = gross * effective_tax_rate()
                    net = gross - tax
                    player["wallet"][sym] -= amount
                    player["fiat"] += net
            elif change < -0.15 and player["fiat"] > 200:
                fiat_to_spend = player["fiat"] * 0.03
                buy_amount = fiat_to_spend / last
                player["fiat"] -= fiat_to_spend
                player["wallet"][sym] += buy_amount

    if "stable_rebalancer" in player["trading_bots"]:
        total_val = total_portfolio_value()
        if total_val > 20000:
            if player["fiat"] < total_val * 0.2:
                for sym in player["unlocked_coins"]:
                    if sym in ("USDT", "USDC"):
                        continue
                    amount = player["wallet"][sym]
                    if amount <= 0:
                        continue
                    sell_amount = amount * 0.05
                    price = COINS_CONFIG[sym]["price"]
                    gross = sell_amount * price
                    tax = gross * effective_tax_rate()
                    net = gross - tax
                    player["wallet"][sym] -= sell_amount
                    usdt_price = COINS_CONFIG["USDT"]["price"]
                    usdt_amount = net / usdt_price
                    player["wallet"]["USDT"] += usdt_amount


# ---------- Ciclo de tick ----------

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

        process_stakes()
        run_trading_bots()

        player["fiat"] -= effective_electricity_cost()
        player["fiat"] = max(player["fiat"], -1_000_000)

        player_events()

        update_missions_on_event("ticks_mined", {"ticks": 1})
        update_missions_on_event("portfolio_check", {"value": total_portfolio_value()})


# ---------- Acciones: mercado / mejoras / prestigio ----------

def sell_crypto(sym, amount):
    if sym not in player["unlocked_coins"]:
        raise ValueError("Moneda no desbloqueada.")
    if amount <= 0:
        raise ValueError("Cantidad inválida.")
    max_amount = player["wallet"][sym]
    if amount > max_amount:
        raise ValueError("No tienes tanta cripto.")
    price = COINS_CONFIG[sym]["price"]
    gross = amount * price
    tax = gross * effective_tax_rate()
    net = gross - tax
    player["wallet"][sym] -= amount
    player["fiat"] += net
    return f"Vendidos {amount:.8f} {sym} por ${net:.2f} (impuestos ${tax:.2f})."


def buy_crypto(sym, fiat_to_spend):
    if sym not in player["unlocked_coins"]:
        raise ValueError("Moneda no desbloqueada.")
    if fiat_to_spend <= 0:
        raise ValueError("Cantidad inválida.")
    if fiat_to_spend > player["fiat"]:
        raise ValueError("No tienes tanto dinero.")
    price = COINS_CONFIG[sym]["price"]
    crypto_amount = fiat_to_spend / price
    player["fiat"] -= fiat_to_spend
    player["wallet"][sym] += crypto_amount
    return f"Comprados {crypto_amount:.8f} {sym}."


def buy_hash_upgrade(index):
    if index < 0 or index >= len(UPGRADES):
        raise ValueError("Selección inválida.")
    u = UPGRADES[index]
    if player["fiat"] < u["cost"]:
        raise ValueError("No tienes suficiente dinero.")
    player["fiat"] -= u["cost"]
    player["hash_rate_base"] += u["hash_gain"]
    return f"Has comprado: {u['name']}"


def buy_utility_upgrade(index):
    if index < 0 or index >= len(UTILITY_UPGRADES):
        raise ValueError("Selección inválida.")
    u = UTILITY_UPGRADES[index]
    if player["fiat"] < u["cost"]:
        raise ValueError("No tienes suficiente dinero.")
    player["fiat"] -= u["cost"]
    if u["effect"] == "reduce_electricity":
        player["electricity_cost_base"] *= (1 - u["amount"])
        return "Nuevo coste de electricidad ajustado."
    elif u["effect"] == "reduce_taxes":
        player["tax_rate_base"] *= (1 - u["amount"])
        return "Nuevo tipo impositivo ajustado."
    elif u["effect"] == "hack_protect":
        player["hack_protection"] = min(1.0, player["hack_protection"] + u["amount"])
        return "Mayor protección contra hackeos."
    elif u["effect"] == "hardware_protect":
        player["hardware_protection"] = min(1.0, player["hardware_protection"] + u["amount"])
        return "Mayor protección de hardware."
    else:
        return "Mejora aplicada."


def buy_unlock_upgrade(index):
    if index < 0 or index >= len(UNLOCK_UPGRADES):
        raise ValueError("Selección inválida.")
    u = UNLOCK_UPGRADES[index]
    already_unlocked = all(sym in player["unlocked_coins"] for sym in u["unlocks"])
    if already_unlocked:
        raise ValueError("Ya tienes esas monedas.")
    if player["fiat"] < u["cost"]:
        raise ValueError("No tienes suficiente dinero.")
    player["fiat"] -= u["cost"]
    for sym in u["unlocks"]:
        if sym not in player["unlocked_coins"]:
            player["unlocked_coins"].append(sym)
    update_missions_on_event("coin_pack_unlocked", {})
    return "Nuevas criptos desbloqueadas."


def do_prestige_reset():
    total_val = total_portfolio_value()
    points_gained = int(total_val // 50000)
    if points_gained <= 0:
        raise ValueError("Valor demasiado bajo para prestigio (mínimo ~50k).")
    player["prestige_points"] += points_gained
    player["prestige_level"] += 1

    player["fiat"] = 0.0
    player["wallet"] = {sym: 0.0 for sym in COINS_CONFIG.keys()}
    player["hash_rate_base"] = 1.0
    player["electricity_cost_base"] = 1.0
    player["tax_rate_base"] = 0.05
    player["ticks_played"] = 0
    player["unlocked_coins"] = ["BTC", "ETH", "DOGE"]
    player["stakes"] = []
    LAST_EVENTS.clear()

    missions_state["daily"] = []
    missions_state["weekly"] = []
    missions_state["monthly"] = []
    missions_state["unlock"] = []

    return points_gained, player["prestige_level"]


def buy_permanent_upgrade(index):
    if index < 0 or index >= len(PERMANENT_UPGRADES):
        raise ValueError("Selección inválida.")
    u = PERMANENT_UPGRADES[index]
    if player["prestige_points"] < u["cost_points"]:
        raise ValueError("No tienes suficientes puntos de prestigio.")
    player["prestige_points"] -= u["cost_points"]
    key = u["key"]
    player["permanent_upgrades"][key] = player["permanent_upgrades"].get(key, 0) + 1
    if key == "extra_unlocks":
        extras = ["BNB", "XRP", "SOL", "USDC", "TRX", "ADA"]
        for sym in extras:
            if sym not in player["unlocked_coins"]:
                player["unlocked_coins"].append(sym)
    return f"Subes de nivel la mejora permanente: {u['name']}"


def buy_bot(index):
    if index < 0 or index >= len(BOTS_CATALOG):
        raise ValueError("Selección inválida.")
    bot = BOTS_CATALOG[index]
    if bot["id"] in player["trading_bots"]:
        raise ValueError("Ese bot ya está activo.")
    if player["prestige_points"] < bot["points_cost"]:
        raise ValueError("No tienes suficientes puntos de prestigio.")
    player["prestige_points"] -= bot["points_cost"]
    player["trading_bots"].append(bot["id"])
    return f"Has comprado y activado el bot: {bot['name']}"


# ===========================
#   INTERFAZ GRÁFICA (Tkinter)
# ===========================

class MinerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("is this a miner? – © KAZAH")
        self.root.geometry("1100x650")

        self.date_var = tk.StringVar()
        self.ticks_var = tk.StringVar()
        self.prestige_var = tk.StringVar()
        self.hash_var = tk.StringVar()
        self.energy_var = tk.StringVar()
        self.tax_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.sentiment_var = tk.StringVar()
        self.ticker_var = tk.StringVar()
        self.bots_var = tk.StringVar()
        self.staking_var = tk.StringVar()

        self.auto_ticks_var = tk.IntVar(value=10)
        self.auto_running = False

        self.build_layout()
        reset_missions_if_needed()
        self.update_ui()
        self.show_intro_popup()

    def show_intro_popup(self):
        messagebox.showinfo(
            "is this a miner?",
            "Tranquilo/a 😄\n\n"
            "Este programa NO es un virus, NO mina criptomonedas reales y NO accede a tus datos.\n"
            "Es solo un simulador visual de minería y trading de criptomonedas.\n\n"
            "Consejo: usa los botones de abajo para minar o activar el auto-minado,\n"
            "y explora las pestañas para ver mercado, mejoras, misiones, prestigio y staking."
        )

    def build_layout(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(side=tk.TOP, fill=tk.X)

        # Top labels
        ttk.Label(top, textvariable=self.date_var).grid(row=0, column=0, sticky="w")
        ttk.Label(top, textvariable=self.ticks_var).grid(row=0, column=1, sticky="w", padx=(15, 0))
        ttk.Label(top, textvariable=self.prestige_var).grid(row=0, column=2, sticky="w", padx=(15, 0))

        ttk.Label(top, textvariable=self.hash_var).grid(row=1, column=0, sticky="w")
        ttk.Label(top, textvariable=self.energy_var).grid(row=1, column=1, sticky="w", padx=(15, 0))
        ttk.Label(top, textvariable=self.tax_var).grid(row=1, column=2, sticky="w", padx=(15, 0))
        ttk.Label(top, textvariable=self.total_var, font=("TkDefaultFont", 10, "bold")).grid(
            row=1, column=3, sticky="w", padx=(15, 0)
        )

        ttk.Label(top, textvariable=self.sentiment_var).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Label(top, textvariable=self.ticker_var).grid(row=2, column=2, columnspan=2, sticky="w")

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.page_dashboard = ttk.Frame(self.notebook)
        self.page_market = ttk.Frame(self.notebook)
        self.page_upgrades = ttk.Frame(self.notebook)
        self.page_missions = ttk.Frame(self.notebook)
        self.page_prestige = ttk.Frame(self.notebook)
        self.page_staking = ttk.Frame(self.notebook)
        self.page_help = ttk.Frame(self.notebook)

        self.notebook.add(self.page_dashboard, text="Dashboard")
        self.notebook.add(self.page_market, text="Mercado")
        self.notebook.add(self.page_upgrades, text="Mejoras")
        self.notebook.add(self.page_missions, text="Misiones")
        self.notebook.add(self.page_prestige, text="Prestigio")
        self.notebook.add(self.page_staking, text="Staking")
        self.notebook.add(self.page_help, text="Ayuda")

        self.build_dashboard_tab()
        self.build_market_tab()
        self.build_upgrades_tab()
        self.build_missions_tab()
        self.build_prestige_tab()
        self.build_staking_tab()
        self.build_help_tab()

        # Bottom controls
        bottom = ttk.Frame(self.root, padding=5)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(bottom, text="Minar 1 tick", command=lambda: self.mine_ticks(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="Minar x10", command=lambda: self.mine_ticks(10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="Minar x100", command=lambda: self.mine_ticks(100)).pack(side=tk.LEFT, padx=2)

        ttk.Label(bottom, text="Auto-minado ticks/ciclo:").pack(side=tk.LEFT, padx=(15, 2))
        tk.Spinbox(bottom, from_=1, to=1000, textvariable=self.auto_ticks_var, width=5).pack(side=tk.LEFT)
        self.auto_btn = ttk.Button(bottom, text="Iniciar auto-minado", command=self.toggle_auto)
        self.auto_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom, text="Guardar", command=self.on_save).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bottom, text="Cargar", command=self.on_load).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bottom, text="Salir", command=self.root.destroy).pack(side=tk.RIGHT, padx=2)

    # ---------- Dashboard TAB ----------

    def build_dashboard_tab(self):
        frame = self.page_dashboard

        # Wallet
        wallet_frame = ttk.LabelFrame(frame, text="Wallet (monedas desbloqueadas)")
        wallet_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.wallet_tree = ttk.Treeview(wallet_frame, columns=("amount", "price", "value"), show="headings", height=15)
        self.wallet_tree.heading("amount", text="Cantidad")
        self.wallet_tree.heading("price", text="Precio actual")
        self.wallet_tree.heading("value", text="Valor ($)")
        self.wallet_tree.column("amount", width=150)
        self.wallet_tree.column("price", width=120)
        self.wallet_tree.column("value", width=120)
        self.wallet_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Eventos + info extra
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, textvariable=self.bots_var).pack(anchor="w", padx=5, pady=(5, 0))
        ttk.Label(right_frame, textvariable=self.staking_var).pack(anchor="w", padx=5, pady=(0, 5))

        ttk.Label(right_frame, text="Misiones (resumen):").pack(anchor="w", padx=5)
        self.missions_text = tk.Text(right_frame, height=8, width=50, state="disabled")
        self.missions_text.pack(fill=tk.BOTH, expand=False, padx=5, pady=(0, 5))

        ttk.Label(right_frame, text="Eventos recientes:").pack(anchor="w", padx=5)
        self.events_list = tk.Listbox(right_frame, height=10)
        self.events_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

    # ---------- Mercado TAB ----------

    def build_market_tab(self):
        frame = self.page_market

        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top, text="Moneda:").grid(row=0, column=0, sticky="w")
        self.market_coin_var = tk.StringVar()
        self.market_coin_combo = ttk.Combobox(top, textvariable=self.market_coin_var, state="readonly", width=10)
        self.market_coin_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(top, text="Cantidad FIAT (para comprar):").grid(row=1, column=0, sticky="w")
        self.buy_amount_var = tk.DoubleVar(value=100.0)
        ttk.Entry(top, textvariable=self.buy_amount_var, width=12).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(top, text="Cantidad CRYPTO (para vender):").grid(row=2, column=0, sticky="w")
        self.sell_amount_var = tk.DoubleVar(value=0.0)
        ttk.Entry(top, textvariable=self.sell_amount_var, width=12).grid(row=2, column=1, sticky="w", padx=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Comprar cripto", command=self.on_buy_crypto).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Vender cripto", command=self.on_sell_crypto).pack(side=tk.LEFT, padx=5)

        info = ttk.LabelFrame(frame, text="Información")
        info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.market_info_label = ttk.Label(info, text="Selecciona una moneda para ver su precio actual.")
        self.market_info_label.pack(anchor="w", padx=5, pady=5)

        self.market_coin_combo.bind("<<ComboboxSelected>>", lambda e: self.update_market_info())

    # ---------- Mejoras TAB ----------

    def build_upgrades_tab(self):
        frame = self.page_upgrades

        # Hash upgrades
        hash_frame = ttk.LabelFrame(frame, text="Mejoras de potencia de minado (run actual)")
        hash_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.hash_list = tk.Listbox(hash_frame, height=10)
        for u in UPGRADES:
            self.hash_list.insert(tk.END, f"{u['name']} | +{u['hash_gain']} hash | ${u['cost']:.2f}")
        self.hash_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(hash_frame, text="Comprar mejora seleccionada", command=self.on_buy_hash_upgrade).pack(pady=5)

        # Utility upgrades
        util_frame = ttk.LabelFrame(frame, text="Mejoras de utilidad (run actual)")
        util_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.util_list = tk.Listbox(util_frame, height=10)
        for u in UTILITY_UPGRADES:
            self.util_list.insert(tk.END, f"{u['name']} | ${u['cost']:.2f} | {u['desc']}")
        self.util_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(util_frame, text="Comprar mejora seleccionada", command=self.on_buy_utility_upgrade).pack(pady=5)

        # Unlock upgrades
        unlock_frame = ttk.LabelFrame(frame, text="Desbloqueo de nuevas criptomonedas")
        unlock_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.unlock_list = tk.Listbox(unlock_frame, height=10)
        for u in UNLOCK_UPGRADES:
            self.unlock_list.insert(tk.END, f"{u['name']} | ${u['cost']:.2f} | {', '.join(u['unlocks'])}")
        self.unlock_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(unlock_frame, text="Comprar pack seleccionado", command=self.on_buy_unlock_upgrade).pack(pady=5)

    # ---------- Misiones TAB ----------

    def build_missions_tab(self):
        frame = self.page_missions
        ttk.Label(frame, text="Misiones activas y progreso:").pack(anchor="w", padx=5, pady=5)

        self.missions_full_text = tk.Text(frame, state="disabled")
        self.missions_full_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        ttk.Button(frame, text="Reclamar misiones completadas", command=self.on_claim_missions).pack(pady=5)

    # ---------- Prestigio TAB ----------

    def build_prestige_tab(self):
        frame = self.page_prestige

        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)

        self.prestige_info_label = ttk.Label(top, text="")
        self.prestige_info_label.pack(anchor="w", pady=2)

        ttk.Button(top, text="Hacer PRESTIGIO (reset)", command=self.on_prestige).pack(anchor="w", pady=5)

        # Permanent upgrades
        perm_frame = ttk.LabelFrame(frame, text="Mejoras permanentes (prestigio)")
        perm_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.perm_list = tk.Listbox(perm_frame, height=10)
        for u in PERMANENT_UPGRADES:
            self.perm_list.insert(tk.END, f"{u['name']} | Coste: {u['cost_points']} pts")
        self.perm_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(perm_frame, text="Comprar mejora seleccionada", command=self.on_buy_perm_upgrade).pack(pady=5)

        # Bots
        bots_frame = ttk.LabelFrame(frame, text="Bots de trading (prestigio)")
        bots_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.bots_list = tk.Listbox(bots_frame, height=10)
        for b in BOTS_CATALOG:
            self.bots_list.insert(tk.END, f"{b['name']} | Coste: {b['points_cost']} pts")
        self.bots_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(bots_frame, text="Comprar bot seleccionado", command=self.on_buy_bot).pack(pady=5)

    # ---------- Staking TAB ----------

    def build_staking_tab(self):
        frame = self.page_staking

        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top, text="Moneda para staking:").grid(row=0, column=0, sticky="w")
        self.stake_coin_var = tk.StringVar()
        self.stake_coin_combo = ttk.Combobox(top, textvariable=self.stake_coin_var, state="readonly", width=10)
        self.stake_coin_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(top, text="Cantidad a asignar:").grid(row=1, column=0, sticky="w")
        self.stake_amount_var = tk.DoubleVar(value=0.0)
        ttk.Entry(top, textvariable=self.stake_amount_var, width=12).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Button(top, text="Iniciar staking", command=self.on_start_stake).grid(row=2, column=0, columnspan=2, pady=5)

        info = ttk.LabelFrame(frame, text="Staking activo")
        info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stake_info_text = tk.Text(info, state="disabled")
        self.stake_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ---------- Help TAB ----------

    def build_help_tab(self):
        frame = self.page_help
        text = tk.Text(frame, state="normal", wrap="word")
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        help_text = (
            "AYUDA RÁPIDA – 'is this a miner?'\n\n"
            "• Este juego es un simulador de minería y trading de criptomonedas.\n"
            "• NO mina criptomonedas reales, NO toca tus archivos ni tus datos.\n\n"
            "CÓMO SE JUEGA:\n"
            "1. Usa los botones de abajo para minar 1, 10 o 100 ticks.\n"
            "2. Activa el auto-minado para que el juego avance solo.\n"
            "3. En la pestaña 'Mercado' compras/vendes criptos.\n"
            "4. En 'Mejoras' subes potencia, bajas costes y desbloqueas nuevas monedas.\n"
            "5. En 'Misiones' ves objetivos que dan puntos de prestigio.\n"
            "6. En 'Prestigio' reinicias la partida a cambio de mejoras permanentes.\n"
            "7. En 'Staking' obtienes intereses adicionales en ciertas criptos.\n\n"
            "CONCEPTOS:\n"
            "• TICK: un paso de tiempo simulado. Al avanzar ticks se mina y cambian precios.\n"
            "• FIAT: dinero normal (dólares) para comprar mejoras y criptos.\n"
            "• PRESTIGIO: al ser rico, puedes reiniciar y conseguir puntos para bonus permanentes.\n\n"
            "Si algo da error, revisa los mensajes emergentes (ventanas pequeñas) que explican qué pasa."
        )
        text.insert("1.0", help_text)
        text.configure(state="disabled")

    # ======================
    #   UI ACTIONS
    # ======================

    def update_ui(self):
        self.date_var.set(f"Hoy: {date.today().isoformat()}")
        self.ticks_var.set(f"Ticks jugados: {player['ticks_played']}")
        self.prestige_var.set(
            f"Prestigio: {player['prestige_level']} | Puntos: {player['prestige_points']}"
        )
        self.hash_var.set(f"Hash efectivo: {effective_hash_rate():.2f} H/s")
        self.energy_var.set(f"Electricidad/tick: ${effective_electricity_cost():.2f}")
        self.tax_var.set(f"Impuestos: {effective_tax_rate()*100:.1f}%")
        self.total_var.set(f"Valor total portfolio: ${total_portfolio_value():,.2f}")

        self.sentiment_var.set("Mercado BTC: " + market_sentiment_bar())
        self.ticker_var.set("Ticker: " + short_price_ticker())
        self.bots_var.set(bots_summary())
        self.staking_var.set(staking_summary())

        # Wallet tree
        for item in self.wallet_tree.get_children():
            self.wallet_tree.delete(item)
        for sym in player["unlocked_coins"]:
            amount = player["wallet"][sym]
            price = COINS_CONFIG[sym]["price"]
            value = amount * price
            self.wallet_tree.insert(
                "", tk.END,
                values=(f"{amount:,.8f}", f"${price:,.4f}", f"${value:,.2f}")
            )

        # Missions summary in dashboard
        self.missions_text.configure(state="normal")
        self.missions_text.delete("1.0", tk.END)
        self.missions_text.insert("1.0", missions_summary_text())
        self.missions_text.configure(state="disabled")

        # Events list
        self.events_list.delete(0, tk.END)
        for e in LAST_EVENTS:
            self.events_list.insert(tk.END, e)

        # Market coin choices
        unlocked = list(player["unlocked_coins"])
        self.market_coin_combo["values"] = unlocked
        if self.market_coin_var.get() not in unlocked:
            self.market_coin_var.set(unlocked[0] if unlocked else "")

        # Staking coins
        eligible = [c for c in STAKING_CONFIG.keys() if c in player["unlocked_coins"]]
        self.stake_coin_combo["values"] = eligible
        if eligible and self.stake_coin_var.get() not in eligible:
            self.stake_coin_var.set(eligible[0])
        elif not eligible:
            self.stake_coin_var.set("")

        # Missions full view
        self.missions_full_text.configure(state="normal")
        self.missions_full_text.delete("1.0", tk.END)
        self.missions_full_text.insert("1.0", missions_summary_text())
        self.missions_full_text.configure(state="disabled")

        # Prestige info label
        self.prestige_info_label.config(
            text=f"Valor total actual: ${total_portfolio_value():,.2f}  |  "
                 f"Prestigio: {player['prestige_level']}  |  Puntos: {player['prestige_points']}"
        )

        # Staking info text
        self.stake_info_text.configure(state="normal")
        self.stake_info_text.delete("1.0", tk.END)
        if player["stakes"]:
            for s in player["stakes"]:
                self.stake_info_text.insert(
                    tk.END,
                    f"{s['coin']} - cantidad base: {s['amount']:.4f}, ticks restantes: {s['remaining_ticks']}\n"
                )
        else:
            self.stake_info_text.insert(tk.END, "No tienes staking activo.")
        self.stake_info_text.configure(state="disabled")

        # Auto button text
        self.auto_btn.config(text="Detener auto-minado" if self.auto_running else "Iniciar auto-minado")

        # Market info
        self.update_market_info()

    # ----- Buttons -----

    def mine_ticks(self, n):
        update_prices_and_mine(ticks=n)
        self.update_ui()

    def toggle_auto(self):
        self.auto_running = not self.auto_running
        if self.auto_running:
            self.auto_step()
        self.update_ui()

    def auto_step(self):
        if not self.auto_running:
            return
        ticks = self.auto_ticks_var.get()
        if ticks <= 0:
            ticks = 1
        update_prices_and_mine(ticks=ticks)
        self.update_ui()
        self.root.after(500, self.auto_step)

    def on_save(self):
        try:
            save_game()
            messagebox.showinfo("Guardar", "Partida guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def on_load(self):
        try:
            load_game()
            messagebox.showinfo("Cargar", "Partida cargada correctamente.")
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def update_market_info(self):
        sym = self.market_coin_var.get()
        if not sym:
            self.market_info_label.config(text="Selecciona una moneda.")
            return
        price = COINS_CONFIG[sym]["price"]
        amount = player["wallet"][sym]
        value = amount * price
        self.market_info_label.config(
            text=f"{sym}: precio actual ${price:.4f} | en tu wallet: {amount:.8f} "
                 f"({value:.2f} $)"
        )

    def on_buy_crypto(self):
        sym = self.market_coin_var.get()
        try:
            fiat_to_spend = float(self.buy_amount_var.get())
            msg = buy_crypto(sym, fiat_to_spend)
            messagebox.showinfo("Comprar cripto", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error al comprar", str(e))

    def on_sell_crypto(self):
        sym = self.market_coin_var.get()
        try:
            amount = float(self.sell_amount_var.get())
            msg = sell_crypto(sym, amount)
            messagebox.showinfo("Vender cripto", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error al vender", str(e))

    def on_buy_hash_upgrade(self):
        idx = self.hash_list.curselection()
        if not idx:
            messagebox.showwarning("Mejora hash", "Selecciona una mejora primero.")
            return
        i = idx[0]
        try:
            msg = buy_hash_upgrade(i)
            messagebox.showinfo("Mejora hash", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de mejora", str(e))

    def on_buy_utility_upgrade(self):
        idx = self.util_list.curselection()
        if not idx:
            messagebox.showwarning("Mejora utilidad", "Selecciona una mejora primero.")
            return
        i = idx[0]
        try:
            msg = buy_utility_upgrade(i)
            messagebox.showinfo("Mejora utilidad", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de mejora", str(e))

    def on_buy_unlock_upgrade(self):
        idx = self.unlock_list.curselection()
        if not idx:
            messagebox.showwarning("Desbloqueo", "Selecciona un pack primero.")
            return
        i = idx[0]
        try:
            msg = buy_unlock_upgrade(i)
            messagebox.showinfo("Desbloqueo", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de desbloqueo", str(e))

    def on_claim_missions(self):
        gained = claim_completed_missions()
        if gained > 0:
            messagebox.showinfo("Misiones", f"Has reclamado {gained} puntos de prestigio.")
        else:
            messagebox.showinfo("Misiones", "No hay misiones pendientes de reclamar.")
        self.update_ui()

    def on_prestige(self):
        try:
            pts, level = do_prestige_reset()
            messagebox.showinfo(
                "Prestigio",
                f"Has hecho PRESTIGIO.\n"
                f"Puntos ganados: {pts}\n"
                f"Nuevo nivel de prestigio: {level}"
            )
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de prestigio", str(e))

    def on_buy_perm_upgrade(self):
        idx = self.perm_list.curselection()
        if not idx:
            messagebox.showwarning("Mejora permanente", "Selecciona una mejora primero.")
            return
        i = idx[0]
        try:
            msg = buy_permanent_upgrade(i)
            messagebox.showinfo("Mejora permanente", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de mejora permanente", str(e))

    def on_buy_bot(self):
        idx = self.bots_list.curselection()
        if not idx:
            messagebox.showwarning("Bots", "Selecciona un bot primero.")
            return
        i = idx[0]
        try:
            msg = buy_bot(i)
            messagebox.showinfo("Bots", msg)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de bot", str(e))

    def on_start_stake(self):
        sym = self.stake_coin_var.get()
        if not sym:
            messagebox.showwarning("Staking", "No hay monedas elegibles desbloqueadas.")
            return
        try:
            amount = float(self.stake_amount_var.get())
            create_stake(sym, amount)
            messagebox.showinfo("Staking", f"Staking iniciado en {sym} por cantidad {amount:.4f}.")
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error de staking", str(e))


# ===========================
#   ENTRYPOINT
# ===========================

if __name__ == "__main__":
    ensure_player_defaults()
    reset_missions_if_needed()

    root = tk.Tk()
    app = MinerGUI(root)
    root.mainloop()
