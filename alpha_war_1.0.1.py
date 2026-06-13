# ALPHA WAR BOT v2.0 — آپدیت کامل

import json
import os
import random
import time
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

BOT_TOKEN = "76218504:VTXSBxEL5CoQ2by62OujSrT8F5J1J53d0Cg"
DATA_FILE = "alpha_war.json"
CLANS_FILE = "alpha_clans.json"
COLLECT_COOLDOWN = 3600
SPIN_COOLDOWN = 86400
CLAN_WAR_COOLDOWN = 86400
ADMIN_ID = 1321221876
MAX_CLAN_MEMBERS = 10

# ═══════════════════════════════════════════════════
#  نیروها (کامل‌تر — شامل جادوگر و نیروهای جدید)
# ═══════════════════════════════════════════════════
UNITS = {
    "سرباز":       {"emoji": "🗡️", "attack": 12,  "defense": 6,   "cost": 80,   "min_level": 1, "magic": False},
    "کماندار":     {"emoji": "🏹", "attack": 18,  "defense": 4,   "cost": 120,  "min_level": 1, "magic": False},
    "سواره‌نظام":  {"emoji": "🐴", "attack": 25,  "defense": 10,  "cost": 200,  "min_level": 2, "magic": False},
    "توپخانه":     {"emoji": "💣", "attack": 50,  "defense": 3,   "cost": 400,  "min_level": 3, "magic": False},
    "محافظ":       {"emoji": "🛡️", "attack": 6,   "defense": 25,  "cost": 180,  "min_level": 2, "magic": False},
    "نینجا":        {"emoji": "🥷", "attack": 35,  "defense": 8,   "cost": 350,  "min_level": 3, "magic": False, "hidden": True, "hidden_bonus": 30, "desc": "نیروی مخفی — ۳۰٪ شانس دور زدن ۴۰٪ دفاع دشمن"},
    "اژدها":       {"emoji": "🐉", "attack": 80,  "defense": 30,  "cost": 1000, "min_level": 5, "magic": False},
    # نیروهای جدید
    "تیرانداز ویژه": {"emoji": "🎯", "attack": 30, "defense": 6,  "cost": 280,  "min_level": 2, "magic": False},
    "سپرپوش":      {"emoji": "🔰", "attack": 8,   "defense": 40,  "cost": 320,  "min_level": 3, "magic": False},
    "غول جنگی":    {"emoji": "👹", "attack": 65,  "defense": 20,  "cost": 750,  "min_level": 4, "magic": False},
    # نیروهای جادویی
    "جادوگر":      {"emoji": "🧙", "attack": 45,  "defense": 5,   "cost": 500,  "min_level": 3, "magic": True, "spell": "آتش‌گوی", "spell_bonus": 30},
    "شمن":         {"emoji": "🔮", "attack": 35,  "defense": 12,  "cost": 420,  "min_level": 3, "magic": True, "spell": "طوفان یخ", "spell_bonus": 20},
    "الهه جنگ":   {"emoji": "⚡", "attack": 90,  "defense": 15,  "cost": 1200, "min_level": 6, "magic": True, "spell": "صاعقه", "spell_bonus": 50},
    # نیروهای ویژه کریستالی
    "اژدهای کهن":     {"emoji": "🐲", "attack": 150, "defense": 60,  "cost": 0, "crystal_cost": 80,  "min_level": 1, "magic": False, "crystal_unit": True},
    "جادوگر اعظم":    {"emoji": "🧙‍♂️","attack": 120, "defense": 30,  "cost": 0, "crystal_cost": 60,  "min_level": 1, "magic": True,  "crystal_unit": True, "spell": "آتش کیهانی", "spell_bonus": 70},
    "غول افسانه‌ای":  {"emoji": "👾", "attack": 130, "defense": 80,  "cost": 0, "crystal_cost": 70,  "min_level": 1, "magic": False, "crystal_unit": True},
    "کماندار سلطنتی": {"emoji": "🏹", "attack": 100, "defense": 20,  "cost": 0, "crystal_cost": 50,  "min_level": 1, "magic": False, "crystal_unit": True},
}

# ═══════════════════════════════════════════════════
#  تأسیسات (شامل تأسیسات جدید تولید منابع)
# ═══════════════════════════════════════════════════
BUILDINGS = {
    "پادگان":        {"emoji": "🏯", "levels": {1: {"cost": 200, "desc": "+8% حمله",    "atk_bonus": 8},  2: {"cost": 400, "desc": "+18% حمله", "atk_bonus": 18}, 3: {"cost": 700, "desc": "+30% حمله", "atk_bonus": 30}}},
    "معدن آلفا":     {"emoji": "⛏️", "levels": {1: {"cost": 250, "desc": "+60 کوین",    "mine_bonus": 60},2: {"cost": 500, "desc": "+120 کوین", "mine_bonus": 120},3: {"cost": 900, "desc": "+200 کوین", "mine_bonus": 200}}},
    "دیوار دفاعی":   {"emoji": "🧱", "levels": {1: {"cost": 200, "desc": "+10 دفاع",    "def_bonus": 10}, 2: {"cost": 400, "desc": "+25 دفاع",  "def_bonus": 25}, 3: {"cost": 700, "desc": "+45 دفاع",  "def_bonus": 45}}},
    "برج دیده‌بان":  {"emoji": "🗼", "levels": {1: {"cost": 150, "desc": "اطلاعات دشمن","win_bonus": 0},  2: {"cost": 350, "desc": "+5% شانس برد","win_bonus": 5}, 3: {"cost": 650, "desc": "+12% شانس برد","win_bonus": 12}}},
    "بازار":         {"emoji": "🏪", "levels": {1: {"cost": 200, "desc": "+15% درآمد",   "income": 15},    2: {"cost": 400, "desc": "+30% درآمد",  "income": 30},    3: {"cost": 700, "desc": "+50% درآمد",  "income": 50}}},
    # تأسیسات جدید
    "چاه نفت":       {"emoji": "🛢️", "type": "resource", "resource": "نفت",   "levels": {1: {"cost": 400, "desc": "تولید نفت",   "rate": 5,  "capacity": 20},  2: {"cost": 800,  "desc": "تولید بیشتر", "rate": 12, "capacity": 50},  3: {"cost": 1400, "desc": "تولید حداکثر", "rate": 25, "capacity": 100}}},
    "معدن طلا":      {"emoji": "🪙", "type": "resource", "resource": "طلا",   "levels": {1: {"cost": 350, "desc": "تولید طلا",   "rate": 4,  "capacity": 15},  2: {"cost": 700,  "desc": "تولید بیشتر", "rate": 10, "capacity": 40},  3: {"cost": 1200, "desc": "تولید حداکثر", "rate": 20, "capacity": 80}}},
    "معدن مس":       {"emoji": "🔶", "type": "resource", "resource": "مس",    "levels": {1: {"cost": 300, "desc": "تولید مس",    "rate": 6,  "capacity": 25},  2: {"cost": 600,  "desc": "تولید بیشتر", "rate": 14, "capacity": 60},  3: {"cost": 1000, "desc": "تولید حداکثر", "rate": 28, "capacity": 120}}},
    "کارخانه قیر":   {"emoji": "⬛", "type": "resource", "resource": "قیر",   "levels": {1: {"cost": 450, "desc": "تولید قیر",   "rate": 3,  "capacity": 12},  2: {"cost": 900,  "desc": "تولید بیشتر", "rate": 8,  "capacity": 30},  3: {"cost": 1600, "desc": "تولید حداکثر", "rate": 16, "capacity": 60}}},
}

# قیمت فروش هر منبع به آلفاکوین
RESOURCE_SELL_PRICE = {
    "نفت": 15,
    "طلا": 20,
    "مس":  12,
    "قیر": 18,
}

# ═══════════════════════════════════════════════════
#  سیستم کریستال
# ═══════════════════════════════════════════════════
CRYSTAL_SHIELDS = {
    "دیوار_آهنین_12h": {"name": "دیوار آهنین ۱۲ ساعته", "emoji": "🔩", "cost": 30,  "duration": 43200},
    "دیوار_آهنین_24h": {"name": "دیوار آهنین ۲۴ ساعته", "emoji": "🔩", "cost": 50,  "duration": 86400},
    "دیوار_آهنین_3d":  {"name": "دیوار آهنین ۳ روزه",   "emoji": "🔩", "cost": 120, "duration": 259200},
    "دیوار_آهنین_7d":  {"name": "دیوار آهنین ۷ روزه",   "emoji": "🔩", "cost": 250, "duration": 604800},
}

# جادوهای کریستالی قابل خرید (در نبرد استفاده میشن)
CRYSTAL_BATTLE_SPELLS = {
    "گوی_آتش": {"name": "گوی آتش",  "emoji": "🔮", "cost": 35, "spell_key": "گوی آتش",  "desc": "+60% حمله در نبرد بعدی"},
    "زهر_سمی":  {"name": "زهر سمی",  "emoji": "☠️", "cost": 35, "spell_key": "زهر سمی",  "desc": "-40% دفاع دشمن در نبرد بعدی"},
    "سردی":     {"name": "سردی",     "emoji": "🧊", "cost": 40, "spell_key": "سردی",     "desc": "-30% دفاع دشمن + +20% حمله در نبرد بعدی"},
}

CRYSTAL_SPELLS = {
    "طلسم_اژدها":  {"name": "طلسم نگهبان اژدها", "emoji": "🐉", "cost": 40,  "type": "def_boost",  "value": 50, "duration": 7200,  "desc": "+50% دفاع برای ۲ ساعت"},
    "مهر_جنگاور":  {"name": "مهر جنگاوران",       "emoji": "⚔️", "cost": 40,  "type": "atk_boost",  "value": 50, "duration": 7200,  "desc": "+50% حمله برای ۲ ساعت"},
    "کتاب_تجربه":  {"name": "کتاب تجربه",          "emoji": "📖", "cost": 35,  "type": "xp_boost",   "value": 2,  "duration": 86400, "desc": "×۲ XP برای ۲۴ ساعت"},
    "صندوق_افسانه":{"name": "صندوق افسانه‌ای",    "emoji": "🗝️", "cost": 60,  "type": "loot_box",   "value": 0,  "duration": 0,     "desc": "جوایز تصادفی افسانه‌ای"},
}

CRYSTAL_BOOSTS = {
    "بوست_کوین":    {"name": "بوست درآمد ×۲",        "emoji": "💰", "cost": 45, "type": "coin_boost",   "value": 2, "duration": 86400,  "desc": "×۲ درآمد /collect برای ۲۴ ساعت"},
    "بوست_xp":      {"name": "بوست XP ×۲",           "emoji": "⭐", "cost": 45, "type": "xp_boost",     "value": 2, "duration": 86400,  "desc": "×۲ XP برای ۲۴ ساعت"},
    "بوست_منابع":   {"name": "بوست تولید منابع ×۲",  "emoji": "⛏️", "cost": 55, "type": "res_boost",    "value": 2, "duration": 86400,  "desc": "×۲ تولید منابع برای ۲۴ ساعت"},
    "بوست_ساخت":    {"name": "کاهش زمان ساخت",       "emoji": "⚡", "cost": 50, "type": "build_boost",  "value": 0, "duration": 86400,  "desc": "ساخت و ارتقا فوری برای ۲۴ ساعت"},
}

REGIONS = {
    "دشت آتش":     {"emoji": "🌋", "bonus": "+20% حمله",        "atk": 20, "def": 0,  "min_level": 1},
    "جنگل تاریک":  {"emoji": "🌲", "bonus": "+20% دفاع",        "atk": 0,  "def": 20, "min_level": 1},
    "کوه یخ":      {"emoji": "🏔️", "bonus": "+30% درآمد",       "atk": 0,  "def": 0,  "min_level": 3, "income": 30},
    "دریای طوفان": {"emoji": "🌊", "bonus": "+15% حمله و دفاع", "atk": 15, "def": 15, "min_level": 5},
    "قلعه مرکزی":  {"emoji": "🏰", "bonus": "+50% همه چیز",     "atk": 50, "def": 50, "min_level": 10},
}

CLAN_REGIONS = {
    1: {"name": "دشت مرزی",      "emoji": "🌾", "difficulty": "آسان",       "desc": "اولین منطقه — مناسب برای شروع",      "atk_bonus": 5,  "def_bonus": 5,  "income_bonus": 10, "enemy_power": 100,  "reward": 200},
    2: {"name": "جنگل سرخ",      "emoji": "🌲", "difficulty": "متوسط",      "desc": "جنگل خطرناک — دفاع قوی‌تر",          "atk_bonus": 10, "def_bonus": 15, "income_bonus": 20, "enemy_power": 250,  "reward": 400},
    3: {"name": "کوه‌های آتشین", "emoji": "🌋", "difficulty": "سخت",        "desc": "آتشفشان — حمله بالا",                "atk_bonus": 20, "def_bonus": 10, "income_bonus": 30, "enemy_power": 500,  "reward": 700},
    4: {"name": "دریای طوفان",   "emoji": "🌊", "difficulty": "خیلی سخت",  "desc": "طوفان دریایی — همه چیز قوی‌تر",      "atk_bonus": 30, "def_bonus": 30, "income_bonus": 40, "enemy_power": 900,  "reward": 1200},
    5: {"name": "قلعه اژدها",    "emoji": "🐉", "difficulty": "افسانه‌ای",  "desc": "قلب تاریکی — فقط قوی‌ترین‌ها",      "atk_bonus": 50, "def_bonus": 50, "income_bonus": 60, "enemy_power": 1500, "reward": 2000},
}

SPIN_PRIZES = [
    {"name": "100 آلفاکوین",    "emoji": "🪙", "type": "coin",   "value": 100,  "weight": 25},
    {"name": "300 آلفاکوین",    "emoji": "💰", "type": "coin",   "value": 300,  "weight": 18},
    {"name": "500 آلفاکوین",    "emoji": "💎", "type": "coin",   "value": 500,  "weight": 10},
    {"name": "1000 آلفاکوین",   "emoji": "👑", "type": "coin",   "value": 1000, "weight": 4},
    {"name": "5 سرباز رایگان",  "emoji": "🗡️", "type": "unit",  "value": "سرباز",    "count": 5,  "weight": 15},
    {"name": "3 کماندار",       "emoji": "🏹", "type": "unit",   "value": "کماندار",  "count": 3,  "weight": 10},
    {"name": "50 کماندار",      "emoji": "🏹", "type": "unit",   "value": "کماندار",  "count": 50, "weight": 3},
    {"name": "+20 HP پایگاه",   "emoji": "❤️", "type": "hp",    "value": 20,   "weight": 10},
    {"name": "شانس دوباره!",    "emoji": "🔄", "type": "respin", "value": 0,    "weight": 5},
]

DAILY_MISSIONS = [
    {"id": "collect3", "desc": "3 بار آلفاکوین جمع کن",  "target": 3, "type": "collect", "reward": 200},
    {"id": "attack2",  "desc": "2 بار حمله کن",           "target": 2, "type": "attack",  "reward": 300},
    {"id": "buy5",     "desc": "5 واحد نظامی بخر",        "target": 5, "type": "buy",     "reward": 250},
    {"id": "win1",     "desc": "1 جنگ ببر",               "target": 1, "type": "win",     "reward": 400},
    {"id": "spin1",    "desc": "گردونه رو بچرخون",        "target": 1, "type": "spin",    "reward": 150},
]

SPELLS = {
    "آتش‌گوی":      {"emoji": "🔥", "desc": "+30% حمله در این نبرد", "atk_bonus_pct": 30},
    "طوفان یخ":     {"emoji": "❄️", "desc": "-20% دفاع دشمن",       "def_reduce_pct": 20},
    "صاعقه":        {"emoji": "⚡", "desc": "+50% حمله در این نبرد", "atk_bonus_pct": 50},
    "آتش کیهانی":   {"emoji": "☄️", "desc": "+70% حمله در این نبرد", "atk_bonus_pct": 70},
    "سایه مرگ":     {"emoji": "🥷", "desc": "+55% حمله در این نبرد", "atk_bonus_pct": 55, "crystal_spell": True},
    "ضربه مرگبار":  {"emoji": "💥", "desc": "+100% حمله در این نبرد", "atk_bonus_pct": 100},
    # جادوهای کریستالی قابل خرید
    "گوی آتش":      {"emoji": "🔮", "desc": "+60% حمله در این نبرد", "atk_bonus_pct": 60, "crystal_spell": True},
    "زهر سمی":      {"emoji": "☠️", "desc": "-40% دفاع دشمن",       "def_reduce_pct": 40, "crystal_spell": True},
    "سردی":         {"emoji": "🧊", "desc": "-30% دفاع دشمن + +20% حمله", "def_reduce_pct": 30, "atk_bonus_pct": 20, "crystal_spell": True},
}

# ═══════════════════════════════════════════════════
#  توابع پایه
# ═══════════════════════════════════════════════════
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_clans():
    if os.path.exists(CLANS_FILE):
        with open(CLANS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_clans(clans):
    with open(CLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(clans, f, ensure_ascii=False, indent=2)

def get_player(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "name": "", "username": "", "alpha_coin": 500, "army": {},
            "buildings": {}, "region": "دشت آتش",
            "wins": 0, "losses": 0, "hp": 100,
            "level": 1, "xp": 0,
            "daily": {"date": "", "missions": {}, "collected": 0},
            "last_collect": 0, "last_spin": 0,
            "selected_unit": "", "banned": False, "clan": "",
            "resources": {},
            "last_res_collect": {},
            "use_spell": False,
        }
    if isinstance(data[uid].get("buildings"), list):
        data[uid]["buildings"] = {}
    data[uid].setdefault("resources", {})
    data[uid].setdefault("last_res_collect", {})
    data[uid].setdefault("use_spell", False)
    data[uid].setdefault("username", "")
    data[uid].setdefault("crystal", 0)
    data[uid].setdefault("shield_until", 0)
    data[uid].setdefault("active_boosts", {})
    data[uid].setdefault("crystal_spell", None)  # جادوی کریستالی فعال برای نبرد بعدی
    return data[uid]

def get_level_title(level):
    if level >= 10: return "👑 ارباب جنگ"
    if level >= 8:  return "🐉 فرمانده افسانه‌ای"
    if level >= 5:  return "🏆 فرمانده"
    if level >= 3:  return "🗡️ سردار"
    if level >= 2:  return "⚔️ جنگجو"
    return "🪖 سرباز تازه‌کار"

def add_xp(player, amount):
    # بوست XP کریستالی
    boosts = player.get("active_boosts", {})
    if "xp_boost" in boosts and boosts["xp_boost"] > time.time():
        amount = amount * 2
    player["xp"] = player.get("xp", 0) + amount
    needed = player.get("level", 1) * 200
    if player["xp"] >= needed:
        player["level"] = player.get("level", 1) + 1
        player["xp"] -= needed
        player["alpha_coin"] += 300
        return True
    return False

def get_attack_power(player):
    base = sum(UNITS[u]["attack"] * c for u, c in player.get("army", {}).items() if u in UNITS)
    bonus = 0
    lvl = player.get("buildings", {}).get("پادگان", 0)
    if lvl > 0:
        bonus = BUILDINGS["پادگان"]["levels"][lvl]["atk_bonus"]
    region = REGIONS.get(player.get("region", "دشت آتش"), {})
    clan_bonus = player.get("clan_atk_bonus", 0)
    return int(base * (1 + (bonus + region.get("atk", 0) + clan_bonus) / 100))

def get_defense_power(player):
    base = sum(UNITS[u]["defense"] * c for u, c in player.get("army", {}).items() if u in UNITS)
    bonus = 0
    lvl = player.get("buildings", {}).get("دیوار دفاعی", 0)
    if lvl > 0:
        bonus = BUILDINGS["دیوار دفاعی"]["levels"][lvl]["def_bonus"]
    region = REGIONS.get(player.get("region", "دشت آتش"), {})
    clan_bonus = player.get("clan_def_bonus", 0)
    return int(base * (1 + (region.get("def", 0) + clan_bonus) / 100) + bonus)

def has_magic_unit(player):
    """آیا بازیکن نیروی جادویی دارد؟"""
    for unit, count in player.get("army", {}).items():
        if unit in UNITS and UNITS[unit].get("magic") and count > 0:
            return True
    return False

def get_spell_bonus(player):
    """قوی‌ترین جادوی موجود رو برگردان"""
    best_bonus = 0
    best_spell = None
    best_unit = None
    for unit, count in player.get("army", {}).items():
        if unit in UNITS and UNITS[unit].get("magic") and count > 0:
            bonus = UNITS[unit].get("spell_bonus", 0)
            if bonus > best_bonus:
                best_bonus = bonus
                best_spell = UNITS[unit].get("spell")
                best_unit = unit
    return best_unit, best_spell, best_bonus

def apply_clan_bonuses(player, clans):
    cname = player.get("clan", "")
    if cname and cname in clans:
        clan = clans[cname]
        region_lvl = clan.get("region_level", 1)
        r = CLAN_REGIONS.get(region_lvl, CLAN_REGIONS[1])
        player["clan_atk_bonus"] = r["atk_bonus"]
        player["clan_def_bonus"] = r["def_bonus"]
        player["clan_income_bonus"] = r["income_bonus"]
    else:
        player["clan_atk_bonus"] = 0
        player["clan_def_bonus"] = 0
        player["clan_income_bonus"] = 0

def check_daily_reset(player):
    today = str(date.today())
    if player["daily"].get("date") != today:
        mission = random.choice(DAILY_MISSIONS)
        player["daily"] = {
            "date": today,
            "missions": {mission["id"]: {"mission": mission, "progress": 0, "done": False}},
            "collected": 0,
        }

def update_mission(player, mtype, amount=1):
    for mid, mdata in player["daily"].get("missions", {}).items():
        if mdata["mission"]["type"] == mtype and not mdata["done"]:
            mdata["progress"] += amount
            if mdata["progress"] >= mdata["mission"]["target"]:
                mdata["done"] = True
                return mdata["mission"]["reward"]
    return 0

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m} دقیقه و {s} ثانیه"

def calc_casualties(army, loss_pct):
    lost = {}
    for unit, count in army.items():
        lose = min(max(1, int(count * loss_pct)), count)
        if lose > 0:
            lost[unit] = lose
    return lost

def apply_casualties(army, lost):
    for unit, count in lost.items():
        army[unit] = max(0, army.get(unit, 0) - count)
    return {u: c for u, c in army.items() if c > 0}

def damage_buildings(player):
    damaged = []
    buildings = player.get("buildings", {})
    for bname, lvl in list(buildings.items()):
        if lvl > 0 and random.random() < 0.4:
            buildings[bname] = lvl - 1
            damaged.append(bname)
            if buildings[bname] == 0:
                del buildings[bname]
    return damaged

def spin_wheel():
    weights = [p["weight"] for p in SPIN_PRIZES]
    return random.choices(SPIN_PRIZES, weights=weights, k=1)[0]

# ═══════════════════════════════════════════════════
#  محاسبه منابع انباشته شده
# ═══════════════════════════════════════════════════
def get_pending_resources(player):
    """محاسبه منابع تولید شده از آخرین جمع‌آوری"""
    now = time.time()
    pending = {}
    for bname, binfo in BUILDINGS.items():
        if binfo.get("type") != "resource":
            continue
        res_name = binfo["resource"]
        lvl = player.get("buildings", {}).get(bname, 0)
        if lvl <= 0:
            continue
        rate = binfo["levels"][lvl]["rate"]       # واحد در ساعت
        capacity = binfo["levels"][lvl]["capacity"]
        last_time = player.get("last_res_collect", {}).get(bname, player.get("last_collect", now))
        elapsed_hours = (now - last_time) / 3600
        amount = min(int(rate * elapsed_hours), capacity)
        # بوست منابع کریستالی
        if player.get("active_boosts", {}).get("res_boost", 0) > now:
            amount = min(amount * 2, capacity)
        if amount > 0:
            pending[bname] = {"resource": res_name, "amount": amount, "sell_price": RESOURCE_SELL_PRICE.get(res_name, 10)}
    return pending

# ═══════════════════════════════════════════════════
#  شاپ
# ═══════════════════════════════════════════════════
def shop_buy_text(p):
    return (
        f"🛒 فروشگاه — خرید نیرو\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🪙 آلفاکوین: {p['alpha_coin']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"یه نیرو انتخاب کن:"
    )

def shop_buy_kb(p):
    keyboard = []
    for unit, stats in UNITS.items():
        if stats.get("crystal_unit"):
            continue  # نیروهای کریستالی در شاپ معمولی نباشن
        if stats["min_level"] <= p.get("level", 1):
            count = p["army"].get(unit, 0)
            magic_tag = " ✨جادو" if stats.get("magic") else ""
            keyboard.append([InlineKeyboardButton(
                f"{stats['emoji']} {unit} ×{count}{magic_tag} | ⚔️{stats['attack']} 🛡️{stats['defense']} — {stats['cost']}🪙",
                callback_data=f"shop_buy_{unit}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"🔒 {unit} — سطح {stats['min_level']} نیاز",
                callback_data="locked"
            )])
    keyboard.append([InlineKeyboardButton("💰 فروش منابع", callback_data="shop_sell"),
                     InlineKeyboardButton("❌ بستن", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

def shop_sell_text(p):
    pending = get_pending_resources(p)
    text = (
        f"💰 فروشگاه — فروش منابع\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🪙 آلفاکوین: {p['alpha_coin']}\n"
        f"━━━━━━━━━━━━━━━\n"
    )
    if pending:
        text += "منابع آماده فروش:\n"
        for bname, info in pending.items():
            total_coin = info["amount"] * info["sell_price"]
            text += f"  {BUILDINGS[bname]['emoji']} {info['resource']}: {info['amount']} واحد → {total_coin}🪙\n"
    else:
        text += "⚠️ هیچ منبعی برای فروش نداری!\n(تأسیسات تولید منابع بساز)"
    text += "━━━━━━━━━━━━━━━"
    return text

def shop_sell_kb(p):
    pending = get_pending_resources(p)
    keyboard = []
    for bname, info in pending.items():
        total_coin = info["amount"] * info["sell_price"]
        keyboard.append([InlineKeyboardButton(
            f"{BUILDINGS[bname]['emoji']} فروش {info['resource']} ({info['amount']} واحد) → +{total_coin}🪙",
            callback_data=f"shop_sell_{bname}"
        )])
    if pending:
        keyboard.append([InlineKeyboardButton("💵 فروش همه", callback_data="shop_sell_all")])
    keyboard.append([InlineKeyboardButton("🛒 خرید نیرو", callback_data="shop_buy"),
                     InlineKeyboardButton("❌ بستن", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════
#  /collect — شامل منابع
# ═══════════════════════════════════════════════════
def do_collect(p):
    now = time.time()
    if now - p.get("last_collect", 0) < COLLECT_COOLDOWN:
        remaining = COLLECT_COOLDOWN - (now - p.get("last_collect", 0))
        # بررسی آیا منابع pending دارد (collect مجزا)
        pending = get_pending_resources(p)
        if pending:
            lines = ["⛏️ جمع‌آوری آلفاکوین هنوز آماده نیست\n━━━━━━━━━━━━━━━"]
            lines.append(f"⏳ تا collect بعدی: {format_time(remaining)}\n")
            lines.append("📦 اما منابع زیر انباشته شدن:")
            for bname, info in pending.items():
                lines.append(f"  {BUILDINGS[bname]['emoji']} {info['resource']}: {info['amount']} واحد")
            lines.append("\nبرای فروش: /shop → فروش منابع")
            return "\n".join(lines)
        return f"⏳ معادن هنوز پر نشدن!\nتا جمع‌آوری بعدی: {format_time(remaining)}"

    base = random.randint(50, 120)
    mine_lvl = p.get("buildings", {}).get("معدن آلفا", 0)
    mine_bonus = BUILDINGS["معدن آلفا"]["levels"][mine_lvl]["mine_bonus"] if mine_lvl > 0 else 0
    market_lvl = p.get("buildings", {}).get("بازار", 0)
    market_pct = BUILDINGS["بازار"]["levels"][market_lvl]["income"] if market_lvl > 0 else 0
    region = REGIONS.get(p.get("region", "دشت آتش"), {})
    clan_income = p.get("clan_income_bonus", 0)
    market_bonus = int(base * (market_pct + region.get("income", 0) + clan_income) / 100)

    # درآمد بر اساس زمان افلاین
    elapsed = now - p.get("last_collect", 0)
    hours_offline = elapsed / 3600
    time_bonus = 0
    if hours_offline > 1.5:
        time_bonus = int(min(hours_offline - 1, 5) * 20)  # هر ساعت اضافه = 20 کوین (حداکثر 5 ساعت)

    total = base + mine_bonus + market_bonus + time_bonus

    # بوست کریستالی ×۲ درآمد
    boosts = p.get("active_boosts", {})
    now2 = time.time()
    if "coin_boost" in boosts and boosts["coin_boost"] > now2:
        total = total * 2

    p["alpha_coin"] += total
    p["last_collect"] = now
    p["daily"]["collected"] = p["daily"].get("collected", 0) + 1
    mission_reward = update_mission(p, "collect")
    xp_up = add_xp(p, 10)
    if mission_reward:
        p["alpha_coin"] += mission_reward

    msgs = ["سربازانت با غنیمت برگشتن!", "معادن امروز پربار بودن!", "خزانه امپراتوری پر شد!", "قافله از راه رسید!"]
    text = f"⛏️ {random.choice(msgs)}\n━━━━━━━━━━━━━━━\n💰 پایه: +{base} کوین\n"
    if mine_bonus: text += f"⛏️ معدن: +{mine_bonus} کوین\n"
    if market_bonus: text += f"🏪 بازار/منطقه: +{market_bonus} کوین\n"
    if time_bonus: text += f"⏰ درآمد آفلاین ({hours_offline:.1f}h): +{time_bonus} کوین\n"
    text += f"━━━━━━━━━━━━━━━\n✅ مجموع: +{total} کوین\n🪙 خزانه: {p['alpha_coin']}\n⏳ جمع‌آوری بعدی: 1 ساعت دیگه"
    if mission_reward: text += f"\n🏅 مأموریت انجام شد! +{mission_reward} کوین"
    if xp_up: text += f"\n🆙 سطح {p['level']} رسیدی! +300 کوین"

    # وضعیت منابع در پایان
    pending = get_pending_resources(p)
    if pending:
        text += "\n\n📦 منابع انباشته:\n"
        for bname, info in pending.items():
            text += f"  {BUILDINGS[bname]['emoji']} {info['resource']}: {info['amount']} واحد\n"
        text += "برای فروش: /shop"
    return text

def do_spin(p):
    now = time.time()
    if now - p.get("last_spin", 0) < SPIN_COOLDOWN:
        return f"🎡 گردونه امروز چرخیده!\nفردا برگرد — {format_time(SPIN_COOLDOWN - (now - p.get('last_spin',0)))} مانده"
    prize = spin_wheel()
    p["last_spin"] = now
    update_mission(p, "spin")
    slots = random.sample(["🎰","💎","🪙","⚔️","🛡️","🐉","🏆","💰","❤️"], 3)
    result = ""
    if prize["type"] == "coin":
        p["alpha_coin"] += prize["value"]
        result = f"💰 +{prize['value']} آلفاکوین!\n🪙 خزانه: {p['alpha_coin']}"
    elif prize["type"] == "unit":
        p["army"][prize["value"]] = p["army"].get(prize["value"], 0) + prize.get("count", 1)
        result = f"⚔️ {prize.get('count',1)}x {prize['value']} به ارتشت پیوست!"
    elif prize["type"] == "hp":
        p["hp"] = min(100, p["hp"] + prize["value"])
        result = f"❤️ +{prize['value']} HP!\nسلامت: {p['hp']}/100"
    elif prize["type"] == "respin":
        prize2 = spin_wheel()
        result = "🔄 شانس دوباره!\n"
        if prize2["type"] == "coin":
            p["alpha_coin"] += prize2["value"]
            result += f"💰 +{prize2['value']} آلفاکوین!"
        elif prize2["type"] == "unit":
            p["army"][prize2["value"]] = p["army"].get(prize2["value"], 0) + prize2.get("count", 1)
            result += f"⚔️ {prize2.get('count',1)}x {prize2['value']}!"
        elif prize2["type"] == "hp":
            p["hp"] = min(100, p["hp"] + prize2["value"])
            result += f"❤️ +{prize2['value']} HP!"
        else:
            result += f"💰 +{prize2.get('value',0)} آلفاکوین!"
    add_xp(p, 20)
    return f"🎡 گردونه روزانه!\n━━━━━━━━━━━━━━━\n[ {slots[0]} | {slots[1]} | {slots[2]} ]\n━━━━━━━━━━━━━━━\n{prize['emoji']} {prize['name']}\n\n{result}"

def spin_prizes_text():
    lines = ["🎡 جوایز گردونه روزانه:\n━━━━━━━━━━━━━━━"]
    for pr in SPIN_PRIZES:
        lines.append(f"{pr['emoji']} {pr['name']}")
    lines.append("━━━━━━━━━━━━━━━\nروزی یه بار می‌تونی بچرخونی!")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════
#  نبرد (شامل جادو)
# ═══════════════════════════════════════════════════
def do_battle(p, defender, selected, target_name, use_magic=False):
    # بررسی سپر محافظ مدافع
    now = time.time()
    if defender.get("shield_until", 0) > now:
        rem = int((defender["shield_until"] - now) / 3600)
        return f"🛡️ هدف زیر سپر محافظته!\n⏳ {rem} ساعت دیگه سپرش تموم میشه."

    atk_power = get_attack_power(p)
    def_power = get_defense_power(defender)

    # بوست بوست‌های فعال
    boosts = p.get("active_boosts", {})
    if "atk_boost" in boosts and boosts["atk_boost"] > now:
        atk_power = int(atk_power * 1.5)
    def_boosts = defender.get("active_boosts", {})
    if "def_boost" in def_boosts and def_boosts["def_boost"] > now:
        def_power = int(def_power * 1.5)

    # نینجا — مخفی‌کاری: ۳۰٪ شانس دور زدن دفاع
    ninja_count = p.get("army", {}).get("نینجا", 0)
    ninja_text = ""
    if ninja_count > 0 and random.random() < 0.30:
        bypass = int(def_power * 0.40)
        def_power = max(1, def_power - bypass)
        ninja_text = f"🥷 نینجاها دفاع دشمن رو دور زدن! (-{bypass} دفاع)\n"

    spell_text = ""
    # جادو از نیروهای جادویی
    if use_magic and has_magic_unit(p):
        magic_unit, spell_name, spell_bonus = get_spell_bonus(p)
        if spell_name and spell_name in SPELLS:
            spell_info = SPELLS[spell_name]
            if "atk_bonus_pct" in spell_info:
                bonus_val = int(atk_power * spell_info["atk_bonus_pct"] / 100)
                atk_power += bonus_val
                spell_text = f"✨ جادو فعال: {spell_info['emoji']} {spell_name} (+{bonus_val} حمله)\n"
            if "def_reduce_pct" in spell_info:
                reduce_val = int(def_power * spell_info["def_reduce_pct"] / 100)
                def_power = max(1, def_power - reduce_val)
                spell_text += f"✨ جادو دفاع دشمن: -{reduce_val}\n"

    # جادوی کریستالی یک‌بار مصرف
    crystal_spell_key = p.get("crystal_spell")
    if crystal_spell_key and crystal_spell_key in SPELLS:
        csp = SPELLS[crystal_spell_key]
        if "atk_bonus_pct" in csp:
            bonus_val = int(atk_power * csp["atk_bonus_pct"] / 100)
            atk_power += bonus_val
            spell_text += f"{csp['emoji']} جادوی کریستالی {crystal_spell_key}: +{bonus_val} حمله\n"
        if "def_reduce_pct" in csp:
            reduce_val = int(def_power * csp["def_reduce_pct"] / 100)
            def_power = max(1, def_power - reduce_val)
            spell_text += f"{csp['emoji']} جادوی کریستالی {crystal_spell_key}: -{reduce_val} دفاع دشمن\n"
        p["crystal_spell"] = None  # یک‌بار مصرف

    tower_lvl = p.get("buildings", {}).get("برج دیده‌بان", 0)
    win_bonus = BUILDINGS["برج دیده‌بان"]["levels"][tower_lvl]["win_bonus"] if tower_lvl > 0 else 0
    atk_roll = atk_power + random.randint(0, 40) + int(atk_power * win_bonus / 100)
    def_roll = def_power + random.randint(0, 30)
    unit_info = UNITS.get(selected, {})
    unit_emoji = unit_info.get("emoji", "⚔️")

    if atk_roll > def_roll:
        loot = min(random.randint(60, 200), max(0, defender["alpha_coin"] - 50))
        defender["alpha_coin"] = max(50, defender["alpha_coin"] - loot)
        p["alpha_coin"] += loot
        p["wins"] += 1
        defender["losses"] = defender.get("losses", 0) + 1
        hp_damage = random.randint(10, 25)
        defender["hp"] = max(0, defender.get("hp", 100) - hp_damage)
        lost_units = calc_casualties(p["army"], random.uniform(0.10, 0.20))
        # تضمین حداقل یه تلفات در پیروزی
        if not lost_units and p["army"]:
            rnd_unit = random.choice([u for u, c in p["army"].items() if c > 0])
            lost_units = {rnd_unit: 1}
        p["army"] = apply_casualties(p["army"], lost_units)
        damaged_buildings = damage_buildings(defender)
        update_mission(p, "attack")
        update_mission(p, "win")
        xp_up = add_xp(p, 50)
        win_msgs = ["ارتشت مثل طوفان وارد شد!", "دشمن جرات مقاومت نداشت!", "پرچم آلفا بر فراز دشمن!"]
        result = (
            f"⚔️ گزارش نبرد\n━━━━━━━━━━━━━━━\n"
            f"🎯 هدف: {target_name}\n{unit_emoji} واحد: {selected}\n"
            f"{ninja_text}{spell_text}"
            f"━━━━━━━━━━━━━━━\n🎉 {random.choice(win_msgs)}\n\n"
            f"⚔️ حمله: {atk_roll} vs 🛡️ دفاع: {def_roll}\n"
            f"💰 غنیمت: +{loot} کوین\n💥 آسیب به دشمن: -{hp_damage} HP\n"
        )
        if lost_units:
            result += "💀 تلفات تو: " + " | ".join(f"{UNITS[u]['emoji']}{u}×{c}" for u, c in lost_units.items() if u in UNITS) + "\n"
        if damaged_buildings:
            result += f"🏚️ تأسیسات دشمن آسیب دید: {', '.join(damaged_buildings)}\n"
        result += f"━━━━━━━━━━━━━━━\n🏆 کل پیروزی‌ها: {p['wins']}\n🪙 خزانه: {p['alpha_coin']}"
        if xp_up: result += f"\n🆙 سطح {p['level']}! +300 کوین"
    else:
        p["losses"] += 1
        hp_damage = random.randint(15, 30)
        p["hp"] = max(0, p.get("hp", 100) - hp_damage)
        lost_units = calc_casualties(p["army"], random.uniform(0.20, 0.40))
        p["army"] = apply_casualties(p["army"], lost_units)
        update_mission(p, "attack")
        lose_msgs = ["دشمن خیلی قوی‌تر بود!", "دفاع دشمن تسخیرناپذیر بود!", "این بار شانس با تو نبود!"]
        result = (
            f"⚔️ گزارش نبرد\n━━━━━━━━━━━━━━━\n"
            f"🎯 هدف: {target_name}\n{unit_emoji} واحد: {selected}\n"
            f"{ninja_text}{spell_text}"
            f"━━━━━━━━━━━━━━━\n💀 {random.choice(lose_msgs)}\n\n"
            f"⚔️ حمله: {atk_roll} vs 🛡️ دفاع: {def_roll}\n"
            f"💔 آسیب به پایگاه تو: -{hp_damage} HP\n"
        )
        if lost_units:
            result += "💀 تلفات تو: " + " | ".join(f"{UNITS[u]['emoji']}{u}×{c}" for u, c in lost_units.items() if u in UNITS) + "\n"
        result += f"━━━━━━━━━━━━━━━\n📉 کل شکست‌ها: {p['losses']}\n❤️ سلامت: {p['hp']}/100"
    if p["hp"] <= 0:
        p["hp"] = 100
        p["army"] = {}
        result += "\n\n☠️ پایگاهت نابود شد! ارتشت از دست رفت."
    return result

# ═══════════════════════════════════════════════════
#  متن‌ها
# ═══════════════════════════════════════════════════
def build_profile_text(p, clans=None):
    atk = get_attack_power(p)
    def_ = get_defense_power(p)
    title = get_level_title(p.get("level", 1))
    needed_xp = p.get("level", 1) * 200
    region_info = REGIONS.get(p.get("region", "دشت آتش"), {})
    now = time.time()
    collect_status = "آماده!" if now - p.get("last_collect", 0) >= COLLECT_COOLDOWN else f"⏳ {format_time(COLLECT_COOLDOWN - (now - p.get('last_collect',0)))}"
    spin_status = "آماده!" if now - p.get("last_spin", 0) >= SPIN_COOLDOWN else f"⏳ {format_time(SPIN_COOLDOWN - (now - p.get('last_spin',0)))}"
    buildings_lines = []
    for b, lvl in p.get("buildings", {}).items():
        if lvl > 0 and b in BUILDINGS:
            desc = BUILDINGS[b]["levels"][lvl]["desc"]
            buildings_lines.append(f"  {BUILDINGS[b]['emoji']} {b} سطح {lvl} — {desc}")
    buildings_text = "\n".join(buildings_lines) + "\n" if buildings_lines else "  هنوز تأسیساتی نداری\n"
    cname = p.get("clan", "")
    clan_text = f"🏰 کلن: {cname}"
    if cname and clans and cname in clans:
        r = CLAN_REGIONS.get(clans[cname].get("region_level", 1), CLAN_REGIONS[1])
        clan_text += f" | منطقه: {r['emoji']} {r['name']}"
    else:
        clan_text = "🏰 کلن: ندارم"

    magic_text = ""
    if has_magic_unit(p):
        _, spell_name, spell_bonus = get_spell_bonus(p)
        magic_text = f"✨ جادو: {spell_name} (+{spell_bonus}% حمله)\n"

    now_t = time.time()
    shield_text = ""
    if p.get("shield_until", 0) > now_t:
        rem_h = int((p["shield_until"] - now_t) / 3600)
        rem_m = int(((p["shield_until"] - now_t) % 3600) / 60)
        shield_text = f"🔩 دیوار آهنین فعال: {rem_h}h {rem_m}m مانده\n"

    crystal_spell_text = ""
    if p.get("crystal_spell"):
        cs = SPELLS.get(p["crystal_spell"], {})
        crystal_spell_text = f"🔮 جادوی کریستالی: {cs.get('emoji','')} {p['crystal_spell']} (نبرد بعدی)\n"

    boost_text = ""
    boosts = p.get("active_boosts", {})
    for bkey, bexpire in boosts.items():
        if bexpire > now_t:
            rem_h = int((bexpire - now_t) / 3600)
            labels = {"coin_boost": "💰 بوست درآمد ×۲", "xp_boost": "⭐ بوست XP ×۲",
                      "res_boost": "⛏️ بوست منابع ×۲", "build_boost": "⚡ بوست ساخت",
                      "atk_boost": "⚔️ بوست حمله +۵۰%", "def_boost": "🛡️ بوست دفاع +۵۰%"}
            boost_text += f"{labels.get(bkey, bkey)}: {rem_h}h مانده\n"

    return (
        f"👤 {p['name']}\n{title} — سطح {p.get('level',1)}\n"
        f"⭐ تجربه: {p.get('xp',0)}/{needed_xp}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🪙 آلفاکوین: {p['alpha_coin']}\n"
        f"💎 کریستال: {p.get('crystal', 0)}\n"
        f"❤️ سلامت پایگاه: {p['hp']}/100\n"
        f"⚔️ قدرت حمله: {atk}\n"
        f"🛡️ قدرت دفاع: {def_}\n"
        f"🗡️ کل سربازان: {sum(p['army'].values())}\n"
        f"{magic_text}"
        f"🏆 برد: {p['wins']} | باخت: {p['losses']}\n"
        f"🗺️ منطقه: {region_info.get('emoji','')} {p.get('region','')}\n"
        f"{clan_text}\n"
        f"{shield_text}"
        f"{crystal_spell_text}"
        f"{boost_text}"
        f"⛏️ جمع‌آوری: {collect_status}\n"
        f"🎡 گردونه: {spin_status}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏗️ تأسیسات:\n{buildings_text}"
    )

def build_leaderboard(data, chat_id=None):
    """لیدربرد بر اساس حمله + دفاع. اگه chat_id داده شد فقط همون چت رو نشون میده."""
    players_raw = [
        (uid, p) for uid, p in data.items()
        if p.get("name") and not p.get("banned")
    ]
    if chat_id:
        # فیلتر: فقط بازیکنانی که در همون گفتگو پیام دادن (بر اساس clan یا chat_id)
        # در این بات، chat_id == user_id برای PV. برای گروه باید جداگانه ذخیره شود.
        # فعلا اگه chat_id منفی (گروه) بود فقط UID های موجود در data که clan دارند
        pass

    players = []
    for uid, p in players_raw:
        atk = get_attack_power(p)
        def_ = get_defense_power(p)
        power = atk + def_
        players.append((p["name"], atk, def_, power, p.get("level", 1), p["wins"]))
    players.sort(key=lambda x: x[3], reverse=True)

    text = "🏆 لیدربرد Alpha War\n(بر اساس قدرت حمله + دفاع)\n━━━━━━━━━━━━━━━\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, atk, def_, power, level, wins) in enumerate(players[:10]):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {name} | سطح {level} | ⚔️{atk} 🛡️{def_} | {wins} برد\n"
    return text if players else text + "هنوز کسی ثبت‌نام نکرده!"

def build_clan_leaderboard(clans):
    """لیدربرد کلن‌ها بر اساس امتیاز"""
    clan_list = [(cname, c.get("score", 0), len(c.get("members", [])), c.get("wars_won", 0))
                 for cname, c in clans.items()]
    clan_list.sort(key=lambda x: x[1], reverse=True)
    text = "🏆 لیدربرد کلن‌ها\n(بر اساس امتیاز)\n━━━━━━━━━━━━━━━\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (cname, score, members, wars_won) in enumerate(clan_list[:10]):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {cname} | 🏆{score}pts | 👥{members} | ⚔️{wars_won} جنگ برده\n"
    return text if clan_list else text + "هنوز کلنی وجود نداره!"

# ═══════════════════════════════════════════════════
#  کلن
# ═══════════════════════════════════════════════════
def clan_info_text(p, clans, uid):
    cname = p.get("clan", "")
    if cname and cname in clans:
        clan = clans[cname]
        r = CLAN_REGIONS.get(clan.get("region_level", 1), CLAN_REGIONS[1])
        is_leader = clan["leader"] == uid
        now = time.time()
        war_ready = now - clan.get("last_war", 0) >= CLAN_WAR_COOLDOWN
        war_status = "آماده جنگ!" if war_ready else f"⏳ {format_time(CLAN_WAR_COOLDOWN - (now - clan.get('last_war',0)))}"
        pending_text = ""
        if clan.get("pending_requests"):
            pending_text = f"\n📬 درخواست عضویت: {len(clan['pending_requests'])} نفر"
        return (
            f"🏰 کلن: {cname}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"نقش: {'👑 رهبر' if is_leader else '⚔️ عضو'}\n"
            f"اعضا: {len(clan['members'])}/{MAX_CLAN_MEMBERS}\n"
            f"امتیاز: {clan.get('score', 0)}\n"
            f"جنگ‌های برده: {clan.get('wars_won', 0)}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🗺️ منطقه کلن: {r['emoji']} {r['name']} (سطح {clan.get('region_level',1)})\n"
            f"سختی: {r['difficulty']}\n"
            f"بوف‌ها: ⚔️+{r['atk_bonus']}% | 🛡️+{r['def_bonus']}% | 💰+{r['income_bonus']}%\n"
            f"⚔️ کلن وار: {war_status}"
            f"{pending_text}\n"
            f"━━━━━━━━━━━━━━━"
        )
    return "🏰 کلن\n━━━━━━━━━━━━━━━\nهنوز عضو کلنی نیستی!"

def clan_kb(p, clans, uid):
    cname = p.get("clan", "")
    keyboard = []
    if cname and cname in clans:
        clan = clans[cname]
        is_leader = clan["leader"] == uid
        keyboard.append([InlineKeyboardButton("👥 لیست اعضا", callback_data="clan_members")])
        keyboard.append([InlineKeyboardButton("⚔️ کلن وار", callback_data="clan_war"),
                         InlineKeyboardButton("🗺️ مناطق کلن", callback_data="clan_regions")])
        if is_leader:
            keyboard.append([InlineKeyboardButton("📬 درخواست‌های عضویت", callback_data="clan_requests")])
            keyboard.append([InlineKeyboardButton("⚔️ درخواست وار", callback_data="clan_war_request")])
            keyboard.append([InlineKeyboardButton("🗑️ حذف کلن", callback_data="clan_delete")])
        else:
            keyboard.append([InlineKeyboardButton("🚪 خروج از کلن", callback_data="clan_leave")])
    else:
        keyboard.append([InlineKeyboardButton("➕ ساخت کلن", callback_data="clan_create")])
        keyboard.append([InlineKeyboardButton("🔍 جستجو کلن", callback_data="clan_search")])
        keyboard.append([InlineKeyboardButton("📋 لیست کلن‌ها", callback_data="clan_list")])
    keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════
#  کلن وار — کیبورد با نمایش نیروهای هدف
# ═══════════════════════════════════════════════════
def build_clanwar_kb(clans, data, my_clan_name, enemy_clan_name, uid):
    enemy_clan = clans.get(enemy_clan_name, {})
    keyboard = []
    for member_id in enemy_clan.get("members", []):
        if member_id in data:
            m = data[member_id]
            atk = get_attack_power(m)
            def_ = get_defense_power(m)
            # نمایش خلاصه نیروها
            army_summary = " ".join(
                f"{UNITS[u]['emoji']}×{c}" for u, c in m.get("army", {}).items() if u in UNITS and c > 0
            ) or "بدون نیرو"
            keyboard.append([InlineKeyboardButton(
                f"🎯 {m.get('name', '?')} | ⚔️{atk} 🛡️{def_}",
                callback_data=f"cw_target_{member_id}"
            )])
    war_data = clans[my_clan_name].get("war_data", {})
    scores = war_data.get("scores", {})
    keyboard.append([InlineKeyboardButton(
        f"📊 امتیاز | ما: {scores.get(my_clan_name,0)} — حریف: {scores.get(enemy_clan_name,0)}",
        callback_data="cw_scores"
    )])
    keyboard.append([InlineKeyboardButton("🔄 تازه‌سازی", callback_data="cw_refresh")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

def build_cw_unit_kb(target_id, p_attacker):
    """کیبورد انتخاب نیرو برای حمله در کلن وار"""
    keyboard = []
    for unit, count in p_attacker.get("army", {}).items():
        if unit in UNITS and count > 0:
            stats = UNITS[unit]
            magic_tag = "✨" if stats.get("magic") else ""
            keyboard.append([InlineKeyboardButton(
                f"{magic_tag}{stats['emoji']} {unit} ×{count} | ⚔️{stats['attack']*count}",
                callback_data=f"cw_atk_{target_id}_{unit}"
            )])
    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

def get_clanwar_status(clans, cname, data):
    clan = clans.get(cname, {})
    if not clan.get("war_active"):
        return None, None
    war_data = clan.get("war_data", {})
    c1 = war_data.get("clan1")
    c2 = war_data.get("clan2")
    enemy = c2 if c1 == cname else c1
    start = war_data.get("start_time", 0)
    duration = war_data.get("duration", 7200)
    if time.time() - start > duration:
        return "ended", war_data
    return enemy, war_data

async def end_clan_war(clans, data, cname, ctx):
    clan = clans.get(cname, {})
    war_data = clan.get("war_data", {})
    c1 = war_data.get("clan1")
    c2 = war_data.get("clan2")
    if not c1 or not c2: return
    scores = war_data.get("scores", {})
    s1 = scores.get(c1, 0)
    s2 = scores.get(c2, 0)
    winner = c1 if s1 >= s2 else c2
    for cn in [c1, c2]:
        cl = clans.get(cn, {})
        pts = scores.get(cn, 0)
        treasury = pts
        per_member = pts // 10
        cl["treasury"] = cl.get("treasury", 0) + treasury
        if cn == winner:
            cl["wars_won"] = cl.get("wars_won", 0) + 1
            cl["score"] = cl.get("score", 0) + 100
        for member_id in cl.get("members", []):
            if member_id in data:
                data[member_id]["alpha_coin"] += per_member
        cl["war_active"] = False
        cl["war_data"] = {}
        cl["war_id"] = ""
        cl["last_war"] = time.time()
        cl["war_request"] = None
    save_data(data)
    save_clans(clans)
    for cn in [c1, c2]:
        cl = clans.get(cn, {})
        pts = scores.get(cn, 0)
        per_member = pts // 10
        result_text = (
            f"⚔️ پایان کلن وار!\n━━━━━━━━━━━━━━━\n"
            f"🏰 {c1} {scores.get(c1,0)} — {scores.get(c2,0)} 🏰 {c2}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{'🎉 کلنت برنده شد!' if cn == winner else '💀 کلنت بازنده شد!'}\n"
            f"💰 هر عضو +{per_member} آلفاکوین گرفت!"
        )
        for member_id in cl.get("members", []):
            try:
                await ctx.bot.send_message(chat_id=int(member_id), text=result_text)
            except:
                pass

# ═══════════════════════════════════════════════════
#  دستورات
# ═══════════════════════════════════════════════════
def start_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 پروفایل", callback_data="m_profile"),
         InlineKeyboardButton("⚔️ ارتش", callback_data="m_army")],
        [InlineKeyboardButton("🛒 شاپ", callback_data="m_shop"),
         InlineKeyboardButton("🏗️ تأسیسات", callback_data="m_build")],
        [InlineKeyboardButton("⛏️ جمع‌آوری", callback_data="m_collect"),
         InlineKeyboardButton("🎡 گردونه", callback_data="m_spin")],
        [InlineKeyboardButton("💎 کریستال", callback_data="m_crystal"),
         InlineKeyboardButton("🗺️ نقشه", callback_data="m_map")],
        [InlineKeyboardButton("🏅 مأموریت", callback_data="m_mission"),
         InlineKeyboardButton("🏰 کلن", callback_data="m_clan")],
        [InlineKeyboardButton("🏆 لیدربرد", callback_data="m_leaderboard"),
         InlineKeyboardButton("👥 دعوت (+700🪙)", callback_data="m_invite")],
        [InlineKeyboardButton("📖 راهنما", callback_data="m_help")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = str(update.effective_user.id)
    player = get_player(data, update.effective_user.id)
    player["name"] = update.effective_user.first_name
    player["username"] = (update.effective_user.username or "").lower()
    check_daily_reset(player)

    # سیستم دعوت
    invite_bonus_text = ""
    if ctx.args and ctx.args[0].startswith("inv_"):
        inviter_id = ctx.args[0][4:]
        if inviter_id != uid and inviter_id in data and not data[uid].get("invited_by"):
            data[uid]["invited_by"] = inviter_id
            data[inviter_id]["alpha_coin"] = data[inviter_id].get("alpha_coin", 0) + 700
            data[inviter_id].setdefault("invites", 0)
            data[inviter_id]["invites"] += 1
            inviter_name = data[inviter_id].get("name", "یه فرمانده")
            invite_bonus_text = f"\n🎁 از طریق دعوت {inviter_name} وارد شدی!"
            try:
                await ctx.bot.send_message(
                    chat_id=int(inviter_id),
                    text=f"🎉 {player['name']} با لینک دعوت تو وارد بازی شد!\n🪙 +700 آلفاکوین جایزه گرفتی!"
                )
            except:
                pass

    save_data(data)
    text = (
        "╔══════════════════╗\n"
        "      ⚔️  ALPHA WAR  ⚔️\n"
        "╚══════════════════╝\n\n"
        f"فرمانده {player['name']}، خوش اومدی!\n\n"
        "🌍 امپراتوریت رو بساز\n"
        "⚔️ ارتش قدرتمند جمع کن\n"
        "✨ جادو یاد بگیر و دشمن رو نابود کن\n"
        "🏰 کلن بساز و کلن وار کن!\n"
        "🛒 از /shop نیرو بخر و منابع بفروش!\n"
        "👥 دوستات رو دعوت کن، کوین بگیر!"
        f"{invite_bonus_text}"
    )
    await update.message.reply_text(text, reply_markup=start_kb())

async def invite_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)
    uid = str(update.effective_user.id)
    bot_username = (await ctx.bot.get_me()).username
    invite_link = f"https://ble.ir/{bot_username}?start=inv_{uid}"
    invites_count = p.get("invites", 0)
    await update.message.reply_text(
        f"👥 سیستم دعوت Alpha War\n━━━━━━━━━━━━━━━\n"
        f"🎁 به ازای هر دعوت: +700 آلفاکوین\n"
        f"📊 دعوت‌های تو: {invites_count} نفر\n"
        f"💰 درآمد دعوت: {invites_count * 700} آلفاکوین\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔗 لینک دعوت تو:\n{invite_link}"
    )

async def addcrystal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
        amount = int(ctx.args[1])
        data[target_id]["crystal"] = data[target_id].get("crystal", 0) + amount
        save_data(data)
        await update.message.reply_text(f"✅ {amount} کریستال به {data[target_id]['name']} اضافه شد!")
        try:
            await ctx.bot.send_message(int(target_id), f"💎 {amount} کریستال به حسابت اضافه شد!\nموجودی: {data[target_id]['crystal']} 💎")
        except: pass
    except: await update.message.reply_text("فرمت: /addcrystal [@نام یا آیدی] [مقدار]")

async def subcrystal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
        amount = int(ctx.args[1])
        data[target_id]["crystal"] = max(0, data[target_id].get("crystal", 0) - amount)
        save_data(data)
        await update.message.reply_text(f"✅ {amount} کریستال از {data[target_id]['name']} کم شد!\nموجودی: {data[target_id]['crystal']} 💎")
    except: await update.message.reply_text("فرمت: /subcrystal [@نام یا آیدی] [مقدار]")

async def viewcrystal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        if ctx.args:
            target_id = resolve_uid(data, ctx.args[0])
            if not target_id or target_id not in data:
                await update.message.reply_text("❌ بازیکن پیدا نشد!"); return
            p2 = data[target_id]
            await update.message.reply_text(f"💎 کریستال {p2['name']}: {p2.get('crystal', 0)}\n🪙 آلفاکوین: {p2.get('alpha_coin', 0)}")
        else:
            lines = ["💎 موجودی کریستال همه بازیکنان:\n━━━━━━━━━━━━━━━"]
            for uid2, p2 in sorted(data.items(), key=lambda x: x[1].get("crystal", 0), reverse=True)[:15]:
                if p2.get("name"):
                    lines.append(f"👤 {p2['name']}: {p2.get('crystal', 0)}💎 | {p2.get('alpha_coin', 0)}🪙")
            await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

async def fullreset_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأیید ریست کامل", callback_data="adm_confirm_fullreset")],
        [InlineKeyboardButton("❌ لغو", callback_data="close")],
    ])
    await update.message.reply_text(
        "⚠️ هشدار!\nاین عملیات همه داده‌های بازیکنان، کلن‌ها، نیروها و ساختمان‌ها را پاک می‌کند.\nمطمئنی؟",
        reply_markup=kb
    )

async def shop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    apply_clan_bonuses(p, clans)
    save_data(data)
    await update.message.reply_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))

async def crystalshop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)
    save_data(data)
    await update.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

def crystalshop_text(p):
    return (
        f"💎 فروشگاه کریستال\n━━━━━━━━━━━━━━━\n"
        f"💎 کریستال شما: {p.get('crystal', 0)}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"برای خرید کریستال با ادمین تماس بگیرید.\n"
        f"بخش مورد نظر رو انتخاب کن:"
    )

def crystalshop_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔩 دیوار آهنین", callback_data="cshop_shields"),
         InlineKeyboardButton("🔮 جادوها",       callback_data="cshop_spells")],
        [InlineKeyboardButton("🐲 نیروهای ویژه", callback_data="cshop_units"),
         InlineKeyboardButton("⚡ بوست‌ها",      callback_data="cshop_boosts")],
        [InlineKeyboardButton("💳 خرید کریستال", callback_data="cshop_buy_crystal")],
        [InlineKeyboardButton("❌ بستن",          callback_data="close")],
    ])

async def addcrystal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        amount = int(ctx.args[1])
        data[target_id]["crystal"] = data[target_id].get("crystal", 0) + amount
        save_data(data)
        await update.message.reply_text(f"✅ {amount} کریستال به {data[target_id]['name']} اضافه شد!")
        try:
            await ctx.bot.send_message(
                chat_id=int(target_id),
                text=f"💎 {amount} کریستال به حسابت اضافه شد!\nموجودی: {data[target_id]['crystal']} کریستال"
            )
        except:
            pass
    except:
        await update.message.reply_text("فرمت: /addcrystal [@نام یا آیدی] [مقدار]")

async def shop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    apply_clan_bonuses(p, clans)
    await update.message.reply_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))

async def build_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)
    text = f"🏗️ تأسیسات\n━━━━━━━━━━━━━━━\n🪙 آلفاکوین: {p['alpha_coin']}\n\n"
    for bname, binfo in BUILDINGS.items():
        lvl = p.get("buildings", {}).get(bname, 0)
        if lvl > 0:
            desc = binfo["levels"][lvl]["desc"]
            text += f"{binfo['emoji']} {bname}: سطح {lvl} — {desc}\n"
    text += "━━━━━━━━━━━━━━━\nانتخاب کن:"
    keyboard = []
    for bname, binfo in BUILDINGS.items():
        current_lvl = p.get("buildings", {}).get(bname, 0)
        max_lvl = max(binfo["levels"].keys())
        if current_lvl >= max_lvl:
            keyboard.append([InlineKeyboardButton(f"✅ {binfo['emoji']} {bname} — حداکثر", callback_data="maxlevel")])
        else:
            next_lvl = current_lvl + 1
            next_cost = binfo["levels"][next_lvl]["cost"]
            label = "ساخت" if current_lvl == 0 else f"ارتقا سطح {next_lvl}"
            keyboard.append([InlineKeyboardButton(
                f"{binfo['emoji']} {bname} | {label} — {next_cost}🪙",
                callback_data=f"b_{bname}"
            )])
    keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def collect_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    check_daily_reset(p)
    apply_clan_bonuses(p, clans)
    result = do_collect(p)
    save_data(data)
    await update.message.reply_text(result)

async def spin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)
    now = time.time()
    if now - p.get("last_spin", 0) < SPIN_COOLDOWN:
        rem = SPIN_COOLDOWN - (now - p.get("last_spin", 0))
        await update.message.reply_text(f"🎡 گردونه امروز چرخیده!\nفردا برگرد — {format_time(rem)} مانده")
        return
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎡 بچرخون!", callback_data="spin_go")],
                                [InlineKeyboardButton("❌ بستن", callback_data="close")]])
    await update.message.reply_text(spin_prizes_text(), reply_markup=kb)

async def attack_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    apply_clan_bonuses(p, clans)

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        if not target_user:
            await update.message.reply_text("❌ نمیتونم هدف رو شناسایی کنم!")
            return
        target_id = str(target_user.id)
        uid = str(update.effective_user.id)
        if target_id == uid:
            await update.message.reply_text("⚠️ نمیتونی به خودت حمله کنی!")
            return
        if target_id not in data:
            await update.message.reply_text(f"❌ {target_user.first_name} در Alpha War نیست!")
            return
        selected = p.get("selected_unit", "")
        if not selected or selected not in UNITS:
            await update.message.reply_text("⚠️ اول /attack بزن و واحد نظامیت رو انتخاب کن!")
            return
        if get_attack_power(p) == 0:
            await update.message.reply_text("❌ ارتشت خالیه!")
            return
        defender = data[target_id]
        apply_clan_bonuses(defender, clans)
        use_magic = p.get("use_spell", False)
        result = do_battle(p, defender, selected, target_user.first_name, use_magic=use_magic)
        p["selected_unit"] = ""
        p["use_spell"] = False
        save_data(data)
        await update.message.reply_text(result)
        return

    if get_attack_power(p) == 0:
        await update.message.reply_text("❌ ارتشت خالیه! از /shop نیرو بخر.")
        return

    keyboard = []
    for unit, stats in UNITS.items():
        count = p["army"].get(unit, 0)
        if count > 0:
            magic_tag = "✨" if stats.get("magic") else ""
            keyboard.append([InlineKeyboardButton(
                f"{magic_tag}{stats['emoji']} {unit} × {count} | ⚔️{stats['attack']*count}",
                callback_data=f"sel_{unit}"
            )])
    if has_magic_unit(p):
        use_magic = p.get("use_spell", False)
        magic_label = "✨ جادو: روشن" if use_magic else "🔮 جادو: خاموش"
        keyboard.append([InlineKeyboardButton(magic_label, callback_data="toggle_magic")])
    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="close")])
    current = p.get("selected_unit", "")
    status = f"واحد فعلی: {UNITS[current]['emoji']} {current}" if current and current in UNITS else "هنوز انتخاب نکردی"
    magic_status = "✨ جادو فعال" if p.get("use_spell") else ""
    await update.message.reply_text(
        f"⚔️ آماده‌باش!\n━━━━━━━━━━━━━━━\n1. واحد انتخاب کن\n2. روی پیام دشمن ریپلای بزن\n3. بنویس /attack\n\n📌 {status}\n{magic_status}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def spell_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)

    # اگه ریپلای روی پیام دشمنه — جادو رو پرتاب کن
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        if not target_user:
            await update.message.reply_text("❌ نمیتونم هدف رو شناسایی کنم!")
            return
        target_id = str(target_user.id)
        uid = str(update.effective_user.id)
        if target_id == uid:
            await update.message.reply_text("⚠️ نمیتونی به خودت جادو بزنی!")
            return
        if target_id not in data:
            await update.message.reply_text(f"❌ {target_user.first_name} در Alpha War نیست!")
            return
        if not has_magic_unit(p) and not p.get("crystal_spell"):
            await update.message.reply_text("❌ نیروی جادویی یا جادوی کریستالی نداری!\nاز /crystalshop جادو بخر.")
            return
        selected = p.get("selected_unit", "")
        if not selected or selected not in UNITS:
            # اگه واحد انتخاب نشده، اولین واحد جادویی رو انتخاب کن
            for uname, stats in UNITS.items():
                if p["army"].get(uname, 0) > 0 and stats.get("magic"):
                    selected = uname
                    break
            if not selected:
                selected = next((u for u, c in p["army"].items() if c > 0), "")
        if not selected:
            await update.message.reply_text("❌ ارتشت خالیه!")
            return
        defender = data[target_id]
        result = do_battle(p, defender, selected, target_user.first_name, use_magic=True)
        p["selected_unit"] = ""
        p["use_spell"] = False
        save_data(data)
        await update.message.reply_text(result)
        return

    # بدون ریپلای — نمایش منوی جادو
    if not has_magic_unit(p) and not p.get("crystal_spell"):
        await update.message.reply_text(
            "❌ نیروی جادویی یا جادوی کریستالی نداری!\n"
            "از /shop نیروی جادویی بخر یا از /crystalshop جادوی کریستالی."
        )
        return

    keyboard = []
    for unit, stats in UNITS.items():
        if p["army"].get(unit, 0) > 0 and stats.get("magic"):
            spell = stats.get("spell", "")
            spell_info = SPELLS.get(spell, {})
            keyboard.append([InlineKeyboardButton(
                f"✨ {stats['emoji']} {unit} — {spell_info.get('emoji','')} {spell}",
                callback_data=f"sel_{unit}"
            )])

    if p.get("crystal_spell"):
        cs = SPELLS.get(p["crystal_spell"], {})
        keyboard.append([InlineKeyboardButton(
            f"🔮 جادوی کریستالی: {cs.get('emoji','')} {p['crystal_spell']} (آماده)",
            callback_data="spell_use_crystal"
        )])

    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="close")])

    lines = ["✨ حمله جادویی\n━━━━━━━━━━━━━━━"]
    if has_magic_unit(p):
        _, spell_name, spell_bonus = get_spell_bonus(p)
        lines.append(f"جادوی فعال: {spell_name} (+{spell_bonus}% حمله)")
    if p.get("crystal_spell"):
        lines.append(f"🔮 جادوی کریستالی: {p['crystal_spell']} (یک‌بار مصرف)")
    lines.append("\n1. واحد انتخاب کن\n2. روی پیام دشمن ریپلای بزن\n3. بنویس /spell")

    await update.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(keyboard))

async def clanwar_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    uid = str(update.effective_user.id)
    cname = p.get("clan", "")
    if not cname or cname not in clans:
        await update.message.reply_text("❌ عضو کلنی نیستی! با /clan کلن بساز یا بپیوند.")
        return
    clan = clans[cname]
    if not clan.get("war_active"):
        if clan.get("in_queue"):
            await update.message.reply_text("🔍 در صف کلن وار هستی، منتظر حریف باش...")
        else:
            await update.message.reply_text("❌ الان جنگ کلنی نیست!\nاز /clan منوی کلن وار رو بزن.")
        return
    enemy_name, war_data = get_clanwar_status(clans, cname, data)
    if enemy_name == "ended":
        await end_clan_war(clans, data, cname, ctx)
        await update.message.reply_text("⏰ زمان جنگ تموم شد!")
        return
    if not enemy_name:
        await update.message.reply_text("❌ اطلاعات جنگ پیدا نشد!")
        return
    scores = war_data.get("scores", {})
    start_time = war_data.get("start_time", 0)
    duration = war_data.get("duration", 7200)
    remaining = max(0, duration - (time.time() - start_time))
    h = int(remaining // 3600)
    m = int((remaining % 3600) // 60)
    text = (
        f"⚔️ جنگ فعال — {cname} علیه {enemy_name}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 امتیاز: ما {scores.get(cname,0)} — حریف {scores.get(enemy_name,0)}\n"
        f"⏳ زمان باقی‌مانده: {h}h {m}m\n\n"
        f"🎯 روی نام دشمن بزن تا نیروهاشو ببینی و حمله کنی:"
    )
    if remaining <= 0:
        await end_clan_war(clans, data, cname, ctx)
        await update.message.reply_text("⏰ زمان جنگ تموم شد!")
        return
    keyboard = build_clanwar_kb(clans, data, cname, enemy_name, uid)
    await update.message.reply_text(text, reply_markup=keyboard)

async def clan_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    p = get_player(data, update.effective_user.id)
    uid = str(update.effective_user.id)
    await update.message.reply_text(clan_info_text(p, clans, uid), reply_markup=clan_kb(p, clans, uid))

async def mission_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    p = get_player(data, update.effective_user.id)
    check_daily_reset(p)
    save_data(data)
    text = "🏅 مأموریت روزانه:\n━━━━━━━━━━━━━━━\n"
    for mid, mdata in p["daily"].get("missions", {}).items():
        m = mdata["mission"]
        done = mdata["done"]
        status = "✅ انجام شد!" if done else f"{mdata['progress']}/{m['target']}"
        text += f"📌 {m['desc']}\n   جایزه: {m['reward']} کوین | {status}\n\n"
    await update.message.reply_text(text)

async def leaderboard_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clans = load_clans()
    chat_id = update.effective_chat.id
    is_group = chat_id < 0

    keyboard = [
        [InlineKeyboardButton("👤 لیدربرد بازیکنان", callback_data="lb_players"),
         InlineKeyboardButton("🏰 لیدربرد کلن‌ها", callback_data="lb_clans")],
        [InlineKeyboardButton("❌ بستن", callback_data="close")]
    ]
    text = "🏆 لیدربرد Alpha War\nانتخاب کن:"
    if is_group:
        text += f"\n(در این گروه نمایش داده می‌شه)"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # بخش اول: دستورات
    text1 = (
        "📖 راهنمای Alpha War\n━━━━━━━━━━━━━━━\n\n"
        "🕹️ دستورات:\n"
        "/start — منوی اصلی\n"
        "/shop — خرید نیرو و فروش منابع\n"
        "/crystalshop — فروشگاه کریستال\n"
        "/build — ساخت و ارتقا تأسیسات\n"
        "/attack — حمله به بازیکن\n"
        "/collect — جمع‌آوری آلفاکوین\n"
        "/spin — گردونه روزانه\n"
        "/mission — مأموریت‌های روزانه\n"
        "/invite — لینک دعوت (+700🪙)\n"
        "/clan — مدیریت کلن\n"
        "/clanwar — جنگ کلن‌ها\n"
        "/leaderboard — لیدربرد\n"
        "/help — راهنما\n"
    )
    await update.message.reply_text(text1)

    # بخش دوم: نیروها
    text2 = "⚔️ نیروهای معمولی (با آلفاکوین):\n━━━━━━━━━━━━━━━\n"
    for uname, u in UNITS.items():
        if not u.get("crystal_unit"):
            magic = f" | ✨ جادو: {u.get('spell','')}" if u.get("magic") else ""
            hidden = f" | 🥷 مخفی‌کار: {u.get('desc','')}" if u.get("hidden") else ""
            lock = f" | 🔒 سطح {u['min_level']}" if u["min_level"] > 1 else ""
            text2 += f"{u['emoji']} {uname}: ⚔️{u['attack']} 🛡️{u['defense']} — {u['cost']}🪙{magic}{hidden}{lock}\n"

    text2 += "\n💎 نیروهای کریستالی:\n━━━━━━━━━━━━━━━\n"
    for uname, u in UNITS.items():
        if u.get("crystal_unit"):
            magic = f" | ✨ {u.get('spell','')}" if u.get("magic") else ""
            text2 += f"{u['emoji']} {uname}: ⚔️{u['attack']} 🛡️{u['defense']} — {u['crystal_cost']}💎{magic}\n"
    await update.message.reply_text(text2)

    # بخش سوم: جادوها و کریستال
    text3 = "✨ جادوها:\n━━━━━━━━━━━━━━━\n"
    for sname, s in SPELLS.items():
        tag = " (کریستالی)" if s.get("crystal_spell") else ""
        text3 += f"{s['emoji']} {sname}{tag}: {s['desc']}\n"

    text3 += "\n🔩 دیوار آهنین (کریستالی):\n━━━━━━━━━━━━━━━\n"
    for sid, s in CRYSTAL_SHIELDS.items():
        text3 += f"{s['emoji']} {s['name']}: {s['cost']}💎\n"

    text3 += "\n⚡ بوست‌های کریستالی:\n━━━━━━━━━━━━━━━\n"
    for bid, b in CRYSTAL_BOOSTS.items():
        text3 += f"{b['emoji']} {b['name']}: {b['desc']} — {b['cost']}💎\n"

    text3 += "\n📦 آیتم‌های کریستالی:\n━━━━━━━━━━━━━━━\n"
    for sid, s in CRYSTAL_SPELLS.items():
        text3 += f"{s['emoji']} {s['name']}: {s['desc']} — {s['cost']}💎\n"
    for sid, s in CRYSTAL_BATTLE_SPELLS.items():
        text3 += f"{s['emoji']} {s['name']}: {s['desc']} — {s['cost']}💎 (یک‌بار مصرف)\n"

    text3 += (
        "\n💎 کریستال چیه؟\n━━━━━━━━━━━━━━━\n"
        "کریستال ارز ویژه بازیه.\n"
        "برای خرید: /crystalshop → خرید کریستال\n"
        "یا با ادمین تماس بگیر."
    )
    await update.message.reply_text(text3)

async def admin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("🪙 اضافه کوین",    callback_data="adm_addcoin"),
         InlineKeyboardButton("💎 اضافه کریستال", callback_data="adm_addcrystal")],
        [InlineKeyboardButton("💎 کم کریستال",    callback_data="adm_subcrystal"),
         InlineKeyboardButton("🔍 موجودی کریستال",callback_data="adm_viewcrystal")],
        [InlineKeyboardButton("📊 آمار",          callback_data="adm_stats"),
         InlineKeyboardButton("📢 پیام همگانی",   callback_data="adm_broadcast")],
        [InlineKeyboardButton("🚫 بن",            callback_data="adm_ban"),
         InlineKeyboardButton("✅ رفع بن",         callback_data="adm_unban")],
        [InlineKeyboardButton("❤️ ریست HP",       callback_data="adm_resethp"),
         InlineKeyboardButton("🔄 ریست بازیکن",   callback_data="adm_resetplayer")],
        [InlineKeyboardButton("💣 ریست کامل بازی",callback_data="adm_fullreset")],
        [InlineKeyboardButton("❌ بستن",           callback_data="close")],
    ]
    await update.message.reply_text("👑 پنل مدیریت Alpha War\n━━━━━━━━━━━━━━━", reply_markup=InlineKeyboardMarkup(keyboard))

def resolve_uid(data, arg):
    """آرگومان میتونه عدد یا @username باشه"""
    if arg.startswith("@"):
        username = arg[1:].lower()
        for uid, p in data.items():
            if p.get("username", "").lower() == username:
                return uid
        return None
    return arg

async def addcoin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        amount = int(ctx.args[1])
        data[target_id]["alpha_coin"] += amount
        save_data(data)
        await update.message.reply_text(f"✅ {amount} کوین به {data[target_id]['name']} اضافه شد!")
    except:
        await update.message.reply_text("فرمت: /addcoin [@نام یا آیدی] [مقدار]")

async def ban_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        data[target_id]["banned"] = True
        save_data(data)
        await update.message.reply_text(f"🚫 {data[target_id]['name']} بن شد!")
    except:
        await update.message.reply_text("فرمت: /ban [@نام یا آیدی]")

async def unban_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        data[target_id]["banned"] = False
        save_data(data)
        await update.message.reply_text(f"✅ بن {data[target_id]['name']} برداشته شد!")
    except:
        await update.message.reply_text("فرمت: /unban [@نام یا آیدی]")

async def resethp_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        data[target_id]["hp"] = 100
        save_data(data)
        await update.message.reply_text(f"❤️ HP {data[target_id]['name']} ریست شد!")
    except:
        await update.message.reply_text("فرمت: /resethp [@نام یا آیدی]")

async def resetplayer_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        data = load_data()
        target_id = resolve_uid(data, ctx.args[0])
        if not target_id or target_id not in data:
            await update.message.reply_text("❌ بازیکن پیدا نشد!")
            return
        name = data[target_id].get("name", target_id)
        data[target_id] = {
            "name": name, "alpha_coin": 500, "army": {},
            "buildings": {}, "region": "دشت آتش",
            "wins": 0, "losses": 0, "hp": 100,
            "level": 1, "xp": 0,
            "daily": {"date": "", "missions": {}, "collected": 0},
            "last_collect": 0, "last_spin": 0,
            "selected_unit": "", "banned": False, "clan": "",
            "resources": {}, "last_res_collect": {}, "use_spell": False,
        }
        save_data(data)
        await update.message.reply_text(f"🔄 بازی {name} کاملاً ریست شد!")
    except Exception as e:
        await update.message.reply_text(f"فرمت: /resetplayer [@نام یا آیدی]\nخطا: {e}")

async def broadcast_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not ctx.args:
        await update.message.reply_text("فرمت: /broadcast [پیام]")
        return
    message = " ".join(ctx.args)
    data = load_data()
    success = 0
    for uid in data:
        try:
            await ctx.bot.send_message(chat_id=int(uid), text=f"📢 پیام از مدیریت Alpha War:\n━━━━━━━━━━━━━━━\n{message}")
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ پیام به {success} نفر ارسال شد!")

# ═══════════════════════════════════════════════════
#  Button Handler
# ═══════════════════════════════════════════════════
async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cb = query.data
    data = load_data()
    clans = load_clans()
    uid = str(query.from_user.id)
    p = get_player(data, query.from_user.id)
    p["username"] = (query.from_user.username or "").lower()
    check_daily_reset(p)
    apply_clan_bonuses(p, clans)

    if p.get("banned"):
        await query.answer("حساب شما مسدود شده!", show_alert=True)
        return
    if cb == "close":
        await query.answer()
        await query.message.delete()
        return
    if cb in ["locked", "maxlevel"]:
        await query.answer("در دسترس نیست!", show_alert=True)
        return

    # برای همه callback های غیر از cbuy_ و adm_ و shop_sell_ که خودشان answer میدن، اینجا answer میدیم
    if not cb.startswith("cbuy_") and not cb.startswith("adm_") and not cb.startswith("shop_sell_") and cb != "shop_sell_all" and cb != "toggle_magic" and not cb.startswith("cwar_") and not cb.startswith("cw_"):
        try:
            await query.answer()
        except:
            pass

    # ── منوی اصلی ──────────────────────────────────
    if cb == "m_profile":
        await query.message.reply_text(build_profile_text(p, clans))
    elif cb == "m_army":
        if not p["army"] or all(v == 0 for v in p["army"].values()):
            await query.message.reply_text("⚠️ ارتش تو خالیه!\nبا /shop نیرو بخر.")
        else:
            text = "⚔️ ارتش من:\n━━━━━━━━━━━━━━━\n"
            for unit, count in p["army"].items():
                if count > 0 and unit in UNITS:
                    u = UNITS[unit]
                    magic_tag = " ✨جادو" if u.get("magic") else ""
                    text += f"{u['emoji']} {unit}{magic_tag} × {count}\n   ⚔️{u['attack']*count} | 🛡️{u['defense']*count}\n"
            text += f"━━━━━━━━━━━━━━━\nکل ⚔️: {get_attack_power(p)} | کل 🛡️: {get_defense_power(p)}"
            await query.message.reply_text(text)
    elif cb == "m_shop":
        await query.message.reply_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))
    elif cb == "m_build":
        await build_cmd.__wrapped__(query, ctx) if hasattr(build_cmd, "__wrapped__") else None
        # inline build
        text = f"🏗️ تأسیسات\n━━━━━━━━━━━━━━━\n🪙 آلفاکوین: {p['alpha_coin']}\n\n"
        for bname, binfo in BUILDINGS.items():
            lvl = p.get("buildings", {}).get(bname, 0)
            if lvl > 0:
                desc = binfo["levels"][lvl]["desc"]
                text += f"{binfo['emoji']} {bname}: سطح {lvl} — {desc}\n"
        text += "━━━━━━━━━━━━━━━\nانتخاب کن:"
        keyboard = []
        for bname, binfo in BUILDINGS.items():
            current_lvl = p.get("buildings", {}).get(bname, 0)
            max_lvl = max(binfo["levels"].keys())
            if current_lvl >= max_lvl:
                keyboard.append([InlineKeyboardButton(f"✅ {binfo['emoji']} {bname} — حداکثر", callback_data="maxlevel")])
            else:
                next_lvl = current_lvl + 1
                next_cost = binfo["levels"][next_lvl]["cost"]
                label = "ساخت" if current_lvl == 0 else f"ارتقا سطح {next_lvl}"
                keyboard.append([InlineKeyboardButton(
                    f"{binfo['emoji']} {bname} | {label} — {next_cost}🪙",
                    callback_data=f"b_{bname}"
                )])
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif cb == "m_collect":
        result = do_collect(p)
        save_data(data)
        await query.message.reply_text(result)
    elif cb == "m_spin":
        now2 = time.time()
        if now2 - p.get("last_spin", 0) < SPIN_COOLDOWN:
            rem = SPIN_COOLDOWN - (now2 - p.get("last_spin", 0))
            await query.message.reply_text(f"🎡 گردونه امروز چرخیده!\nفردا برگرد — {format_time(rem)} مانده")
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎡 بچرخون!", callback_data="spin_go")],
                                        [InlineKeyboardButton("❌ بستن", callback_data="close")]])
            await query.message.reply_text(spin_prizes_text(), reply_markup=kb)
    elif cb == "m_map":
        player_level = p.get("level", 1)
        keyboard = []
        for region, info in REGIONS.items():
            if info["min_level"] <= player_level:
                current = " — فعلی" if p.get("region") == region else ""
                keyboard.append([InlineKeyboardButton(f"{info['emoji']} {region} | {info['bonus']}{current}", callback_data=f"region_{region}")])
            else:
                keyboard.append([InlineKeyboardButton(f"🔒 {info['emoji']} {region} — سطح {info['min_level']}", callback_data="locked")])
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await query.message.reply_text("🗺️ نقشه مناطق\nانتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif cb == "m_mission":
        text = "🏅 مأموریت روزانه:\n━━━━━━━━━━━━━━━\n"
        for mid, mdata in p["daily"].get("missions", {}).items():
            m = mdata["mission"]
            done = mdata["done"]
            status = "✅ انجام شد!" if done else f"{mdata['progress']}/{m['target']}"
            text += f"📌 {m['desc']}\n   جایزه: {m['reward']} کوین | {status}\n\n"
        await query.message.reply_text(text)
    elif cb == "m_clan":
        await query.message.reply_text(clan_info_text(p, clans, uid), reply_markup=clan_kb(p, clans, uid))
    elif cb == "m_leaderboard":
        keyboard = [
            [InlineKeyboardButton("👤 بازیکنان", callback_data="lb_players"),
             InlineKeyboardButton("🏰 کلن‌ها", callback_data="lb_clans")],
            [InlineKeyboardButton("❌ بستن", callback_data="close")]
        ]
        await query.message.reply_text("🏆 لیدربرد:\nانتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif cb == "m_crystal":
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())
    elif cb == "m_help":
        await query.message.reply_text("دستور /help رو بزن تا راهنمای کامل ببینی!")
    elif cb == "m_invite":
        bot_username = (await ctx.bot.get_me()).username
        invite_link = f"https://ble.ir/{bot_username}?start=inv_{uid}"
        invites_count = p.get("invites", 0)
        await query.message.reply_text(
            f"👥 سیستم دعوت Alpha War\n━━━━━━━━━━━━━━━\n"
            f"🎁 به ازای هر دعوت: +700 آلفاکوین\n"
            f"📊 دعوت‌های تو: {invites_count} نفر\n"
            f"💰 درآمد دعوت: {invites_count * 700} آلفاکوین\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 لینک دعوت تو:\n{invite_link}"
        )

    # ── لیدربرد ────────────────────────────────────
    elif cb == "lb_players":
        chat_id = query.message.chat_id
        await query.message.reply_text(build_leaderboard(data, chat_id))
    elif cb == "lb_clans":
        await query.message.reply_text(build_clan_leaderboard(clans))

    # ── شاپ — خرید ──────────────────────────────────
    elif cb == "shop_buy":
        try:
            await query.edit_message_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))
        except:
            await query.message.reply_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))

    elif cb.startswith("shop_buy_"):
        unit = cb[9:]
        if unit not in UNITS: return
        cost = UNITS[unit]["cost"]
        if p["alpha_coin"] < cost:
            await query.answer(f"آلفاکوین کافی نداری! نیاز: {cost}", show_alert=True)
            return
        p["alpha_coin"] -= cost
        p["army"][unit] = p["army"].get(unit, 0) + 1
        mission_reward = update_mission(p, "buy")
        xp_up = add_xp(p, 15)
        if mission_reward: p["alpha_coin"] += mission_reward
        save_data(data)
        notif = f"✅ {UNITS[unit]['emoji']} {unit} به ارتش پیوست!"
        if mission_reward: notif += f" +{mission_reward} کوین"
        if xp_up: notif += f" | سطح {p['level']}!"
        try:
            await query.edit_message_text(shop_buy_text(p), reply_markup=shop_buy_kb(p))
        except:
            pass
        await query.answer(notif, show_alert=True)

    # ── شاپ — فروش ──────────────────────────────────
    elif cb == "shop_sell":
        try:
            await query.edit_message_text(shop_sell_text(p), reply_markup=shop_sell_kb(p))
        except:
            await query.message.reply_text(shop_sell_text(p), reply_markup=shop_sell_kb(p))

    elif cb == "shop_sell_all":
        pending = get_pending_resources(p)
        if not pending:
            await query.answer("چیزی برای فروش نداری!", show_alert=True)
            return
        total_coin = 0
        for bname, info in pending.items():
            total_coin += info["amount"] * info["sell_price"]
            p.setdefault("last_res_collect", {})[bname] = time.time()
        p["alpha_coin"] += total_coin
        save_data(data)
        await query.answer(f"✅ همه فروخته شد! +{total_coin}🪙", show_alert=False)
        data = load_data()
        p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(shop_sell_text(p), reply_markup=shop_sell_kb(p))

    elif cb.startswith("shop_sell_"):
        bname = cb[10:]
        pending = get_pending_resources(p)
        if bname not in pending:
            await query.answer("چیزی برای فروش نداری!", show_alert=True)
            return
        info = pending[bname]
        total_coin = info["amount"] * info["sell_price"]
        p["alpha_coin"] += total_coin
        p.setdefault("last_res_collect", {})[bname] = time.time()
        save_data(data)
        await query.answer(f"✅ {info['resource']} فروخته شد! +{total_coin}🪙", show_alert=False)
        data = load_data()
        p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(shop_sell_text(p), reply_markup=shop_sell_kb(p))

    # ── تأسیسات ────────────────────────────────────
    elif cb.startswith("b_"):
        bname = cb[2:]
        if bname not in BUILDINGS: return
        current_lvl = p.get("buildings", {}).get(bname, 0)
        next_lvl = current_lvl + 1
        max_lvl = max(BUILDINGS[bname]["levels"].keys())
        if current_lvl >= max_lvl:
            await query.answer("حداکثر سطح!", show_alert=True)
            return
        cost = BUILDINGS[bname]["levels"][next_lvl]["cost"]
        if p["alpha_coin"] < cost:
            await query.answer(f"آلفاکوین کافی نداری! نیاز: {cost}", show_alert=True)
            return
        p["alpha_coin"] -= cost
        p["buildings"][bname] = next_lvl
        if BUILDINGS[bname].get("type") == "resource":
            p.setdefault("last_res_collect", {})[bname] = time.time()
        add_xp(p, 30)
        save_data(data)
        action = "ساخته شد" if next_lvl == 1 else f"ارتقا به سطح {next_lvl}"
        desc = BUILDINGS[bname]["levels"][next_lvl]["desc"]
        # بازسازی پیام تأسیسات با اطلاعات جدید
        text2 = f"🏗️ تأسیسات\n━━━━━━━━━━━━━━━\n🪙 آلفاکوین: {p['alpha_coin']}\n\n"
        for bn, bi in BUILDINGS.items():
            lv = p.get("buildings", {}).get(bn, 0)
            if lv > 0:
                text2 += f"{bi['emoji']} {bn}: سطح {lv} — {bi['levels'][lv]['desc']}\n"
        text2 += f"\n✅ {BUILDINGS[bname]['emoji']} {bname} {action}!\n━━━━━━━━━━━━━━━\nانتخاب کن:"
        kb2 = []
        for bn, bi in BUILDINGS.items():
            clv = p.get("buildings", {}).get(bn, 0)
            mlv = max(bi["levels"].keys())
            if clv >= mlv:
                kb2.append([InlineKeyboardButton(f"✅ {bi['emoji']} {bn} — حداکثر", callback_data="maxlevel")])
            else:
                nlv = clv + 1
                nc = bi["levels"][nlv]["cost"]
                lbl = "ساخت" if clv == 0 else f"ارتقا سطح {nlv}"
                kb2.append([InlineKeyboardButton(f"{bi['emoji']} {bn} | {lbl} — {nc}🪙", callback_data=f"b_{bn}")])
        kb2.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        try:
            await query.edit_message_text(text2, reply_markup=InlineKeyboardMarkup(kb2))
        except:
            await query.message.reply_text(text2, reply_markup=InlineKeyboardMarkup(kb2))
        await query.answer(f"✅ {desc}", show_alert=False)

    # ── گردونه ──────────────────────────────────────
    elif cb == "spin_go":
        result = do_spin(p)
        save_data(data)
        try:
            await query.edit_message_text(result)
        except:
            await query.message.reply_text(result)

    # ── جادو ────────────────────────────────────────
    elif cb == "spell_use_crystal":
        p["use_spell"] = True
        save_data(data)
        await query.answer("🔮 جادوی کریستالی آماده‌ست! روی پیام دشمن ریپلای بزن و /spell بزن.", show_alert=True)

    elif cb == "toggle_magic":
        p["use_spell"] = not p.get("use_spell", False)
        save_data(data)
        status = "✨ روشن" if p["use_spell"] else "خاموش"
        await query.answer(f"جادو {status} شد!", show_alert=True)
        # refresh keyboard
        keyboard = []
        for unit, stats in UNITS.items():
            count = p["army"].get(unit, 0)
            if count > 0:
                magic_tag = "✨" if stats.get("magic") else ""
                keyboard.append([InlineKeyboardButton(
                    f"{magic_tag}{stats['emoji']} {unit} × {count} | ⚔️{stats['attack']*count}",
                    callback_data=f"sel_{unit}"
                )])
        if has_magic_unit(p):
            use_magic = p.get("use_spell", False)
            magic_label = "✨ جادو: روشن" if use_magic else "🔮 جادو: خاموش"
            keyboard.append([InlineKeyboardButton(magic_label, callback_data="toggle_magic")])
        keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="close")])
        try:
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
        except:
            pass

    # ── انتخاب واحد ────────────────────────────────
    elif cb.startswith("sel_"):
        unit = cb[4:]
        p["selected_unit"] = unit
        save_data(data)
        magic_note = ""
        if UNITS.get(unit, {}).get("magic"):
            spell = UNITS[unit].get("spell", "")
            magic_note = f"\n✨ این نیرو جادوی '{spell}' داره! برای استفاده جادو رو روشن کن."
        await query.edit_message_text(f"✅ واحد انتخاب شد: {UNITS[unit]['emoji']} {unit}\n\nحالا روی پیام دشمنت ریپلای بزن و /attack بنویس!{magic_note}")

    # ── منطقه ──────────────────────────────────────
    elif cb.startswith("region_"):
        region = cb[7:]
        p["region"] = region
        save_data(data)
        r = REGIONS[region]
        await query.edit_message_text(f"🗺️ به {r['emoji']} {region} رفتی!\n📌 بونوس: {r['bonus']}")

    # ── کلن ────────────────────────────────────────
    elif cb == "clan_create":
        ctx.user_data["action"] = "create_clan"
        await query.edit_message_text("🏰 ساخت کلن جدید\n━━━━━━━━━━━━━━━\nاسم کلنت رو بنویس:\n(بین 3 تا 20 حرف)")

    elif cb == "clan_search":
        ctx.user_data["action"] = "search_clan"
        await query.edit_message_text("🔍 جستجوی کلن\n━━━━━━━━━━━━━━━\nاسم کلن مورد نظرت رو بنویس:")

    elif cb == "clan_list":
        if not clans:
            await query.edit_message_text("هنوز کلنی وجود نداره! با /clan کلن بساز.")
            return
        keyboard = []
        for cname, clan in list(clans.items())[:8]:
            members = len(clan["members"])
            if members < MAX_CLAN_MEMBERS:
                r = CLAN_REGIONS.get(clan.get("region_level", 1), CLAN_REGIONS[1])
                keyboard.append([InlineKeyboardButton(
                    f"🏰 {cname} | {members}/{MAX_CLAN_MEMBERS} | {r['emoji']} {r['name']}",
                    callback_data=f"crequest_{cname}"
                )])
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await query.edit_message_text("📋 کلن‌های موجود:\n(برای درخواست عضویت بزن)", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cb.startswith("crequest_"):
        # ارسال درخواست عضویت به رهبر کلن
        cname = cb[9:]
        if cname not in clans:
            await query.edit_message_text("❌ این کلن وجود نداره!")
            return
        if p.get("clan"):
            await query.answer("اول از کلن فعلیت خارج شو!", show_alert=True)
            return
        clan = clans[cname]
        if len(clan["members"]) >= MAX_CLAN_MEMBERS:
            await query.answer("این کلن پر شده!", show_alert=True)
            return
        # ثبت درخواست
        if "pending_requests" not in clan:
            clan["pending_requests"] = []
        if uid in clan["pending_requests"]:
            await query.answer("قبلاً درخواست دادی! منتظر تأیید رهبر باش.", show_alert=True)
            return
        clan["pending_requests"].append(uid)
        save_clans(clans)
        # اطلاع به رهبر
        leader_id = clan["leader"]
        try:
            await ctx.bot.send_message(
                chat_id=int(leader_id),
                text=f"📬 درخواست عضویت جدید!\n━━━━━━━━━━━━━━━\n👤 {p['name']} (آیدی: {uid})\nمیخواد به کلن {cname} بپیونده.\n\nبرای مدیریت درخواست‌ها: /clan → درخواست‌های عضویت"
            )
        except:
            pass
        await query.edit_message_text(f"✅ درخواست عضویت به کلن {cname} ارسال شد!\nمنتظر تأیید رهبر باش.")

    elif cb == "clan_requests":
        # فقط رهبر
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر میتونه ببینه!", show_alert=True)
            return
        requests = clan.get("pending_requests", [])
        if not requests:
            await query.edit_message_text("📭 درخواست عضویتی نداری!")
            return
        keyboard = []
        for req_uid in requests:
            req_name = data.get(req_uid, {}).get("name", req_uid)
            req_lvl = data.get(req_uid, {}).get("level", 1)
            req_atk = get_attack_power(data.get(req_uid, {})) if req_uid in data else 0
            keyboard.append([
                InlineKeyboardButton(f"✅ {req_name} (سطح {req_lvl} | ⚔️{req_atk})", callback_data=f"clan_accept_{req_uid}"),
                InlineKeyboardButton("❌", callback_data=f"clan_reject_{req_uid}")
            ])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="m_clan")])
        await query.edit_message_text(f"📬 درخواست‌های عضویت کلن {cname}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cb.startswith("clan_accept_"):
        req_uid = cb[12:]
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر!", show_alert=True)
            return
        requests = clan.get("pending_requests", [])
        if req_uid not in requests:
            await query.answer("این درخواست دیگه معتبر نیست!", show_alert=True)
            return
        if len(clan["members"]) >= MAX_CLAN_MEMBERS:
            await query.answer("کلن پر شده!", show_alert=True)
            return
        clan["members"].append(req_uid)
        clan["pending_requests"] = [r for r in requests if r != req_uid]
        if req_uid in data:
            data[req_uid]["clan"] = cname
        save_data(data)
        save_clans(clans)
        req_name = data.get(req_uid, {}).get("name", req_uid)
        # اطلاع به بازیکن
        try:
            await ctx.bot.send_message(chat_id=int(req_uid), text=f"✅ درخواستت قبول شد! به کلن {cname} پیوستی! 🎉")
        except:
            pass
        await query.answer(f"✅ {req_name} به کلن پیوست!", show_alert=True)
        # refresh
        requests2 = clan.get("pending_requests", [])
        if not requests2:
            await query.edit_message_text("📭 درخواست دیگه‌ای نداری!")
        else:
            keyboard = []
            for r_uid in requests2:
                r_name = data.get(r_uid, {}).get("name", r_uid)
                r_lvl = data.get(r_uid, {}).get("level", 1)
                r_atk = get_attack_power(data.get(r_uid, {})) if r_uid in data else 0
                keyboard.append([
                    InlineKeyboardButton(f"✅ {r_name} (سطح {r_lvl} | ⚔️{r_atk})", callback_data=f"clan_accept_{r_uid}"),
                    InlineKeyboardButton("❌", callback_data=f"clan_reject_{r_uid}")
                ])
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="m_clan")])
            await query.edit_message_text(f"📬 درخواست‌های عضویت:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cb.startswith("clan_reject_"):
        req_uid = cb[12:]
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid: return
        clan["pending_requests"] = [r for r in clan.get("pending_requests", []) if r != req_uid]
        save_clans(clans)
        req_name = data.get(req_uid, {}).get("name", req_uid)
        await query.answer(f"❌ {req_name} رد شد!", show_alert=True)
        try:
            await ctx.bot.send_message(chat_id=int(req_uid), text=f"❌ متأسفانه درخواستت برای کلن {cname} رد شد.")
        except:
            pass

    elif cb == "clan_leave":
        cname = p.get("clan", "")
        if not cname:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        if cname in clans:
            clans[cname]["members"] = [m for m in clans[cname]["members"] if m != uid]
            if not clans[cname]["members"]:
                del clans[cname]
            save_clans(clans)
        p["clan"] = ""
        save_data(data)
        await query.edit_message_text(f"🚪 از کلن {cname} خارج شدی!")

    elif cb == "clan_delete":
        cname = p.get("clan", "")
        if cname in clans and clans[cname]["leader"] == uid:
            for member_id in clans[cname]["members"]:
                if member_id in data:
                    data[member_id]["clan"] = ""
            del clans[cname]
            p["clan"] = ""
            save_data(data)
            save_clans(clans)
            await query.edit_message_text(f"🗑️ کلن {cname} حذف شد!")

    elif cb == "clan_members":
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        text = f"👥 اعضای کلن {cname}:\n━━━━━━━━━━━━━━━\n"
        for member_id in clan["members"]:
            if member_id in data:
                m = data[member_id]
                role = "👑" if member_id == clan["leader"] else "⚔️"
                atk = get_attack_power(m)
                def_ = get_defense_power(m)
                text += f"{role} {m['name']} | سطح {m.get('level',1)} | ⚔️{atk} 🛡️{def_} | {m['wins']} برد\n"
        await query.edit_message_text(text)

    elif cb == "clan_regions":
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        current_lvl = clan.get("region_level", 1)
        is_leader = clan["leader"] == uid
        text = f"🗺️ مناطق کلن {cname}:\n━━━━━━━━━━━━━━━\n"
        keyboard = []
        for lvl, r in CLAN_REGIONS.items():
            current = " — فعلی" if lvl == current_lvl else ""
            text += (
                f"{r['emoji']} سطح {lvl}: {r['name']}{current}\n"
                f"   سختی: {r['difficulty']}\n"
                f"   بوف: ⚔️+{r['atk_bonus']}% | 🛡️+{r['def_bonus']}% | 💰+{r['income_bonus']}%\n"
                f"   جایزه کلن وار: {r['reward']} کوین\n\n"
            )
            if is_leader and lvl != current_lvl:
                keyboard.append([InlineKeyboardButton(
                    f"{'🔓' if lvl <= current_lvl + 1 else '🔒'} انتقال به {r['emoji']} {r['name']}",
                    callback_data=f"cregion_{lvl}"
                )])
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard) if is_leader else None)

    elif cb.startswith("cregion_"):
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر!", show_alert=True)
            return
        new_lvl = int(cb[8:])
        current_lvl = clan.get("region_level", 1)
        if new_lvl > current_lvl + 1:
            await query.answer("باید مناطق قبلی رو اول فتح کنی!", show_alert=True)
            return
        total_power = sum(get_attack_power(data[m]) for m in clan["members"] if m in data)
        required = CLAN_REGIONS[new_lvl]["enemy_power"]
        if total_power < required:
            await query.answer(f"قدرت کلن کافی نیست! نیاز: {required} | داری: {total_power}", show_alert=True)
            return
        clan["region_level"] = new_lvl
        save_clans(clans)
        r = CLAN_REGIONS[new_lvl]
        await query.edit_message_text(
            f"✅ کلن {cname} به منطقه {r['emoji']} {r['name']} منتقل شد!\n"
            f"بوف جدید: ⚔️+{r['atk_bonus']}% | 🛡️+{r['def_bonus']}% | 💰+{r['income_bonus']}%"
        )

    # ── درخواست وار (فقط رهبر) ─────────────────────
    elif cb == "clan_war_request":
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر کلن میتونه درخواست وار بده!", show_alert=True)
            return
        if clan.get("war_active"):
            await query.answer("کلنت الان در جنگه!", show_alert=True)
            return
        now = time.time()
        if now - clan.get("last_war", 0) < CLAN_WAR_COOLDOWN:
            remaining = CLAN_WAR_COOLDOWN - (now - clan.get("last_war", 0))
            await query.answer(f"⏳ هنوز {format_time(remaining)} تا جنگ بعدی!", show_alert=True)
            return
        # نمایش کلن‌های موجود برای درخواست
        keyboard = []
        for cn, cl in clans.items():
            if cn != cname and not cl.get("war_active") and not cl.get("in_queue"):
                score = cl.get("score", 0)
                members = len(cl.get("members", []))
                keyboard.append([InlineKeyboardButton(
                    f"🏰 {cn} | {members} عضو | 🏆{score}pts",
                    callback_data=f"cwar_req_{cn}"
                )])
        if not keyboard:
            await query.edit_message_text("❌ الان کلن دیگه‌ای برای چالش وجود نداره!")
            return
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await query.edit_message_text("⚔️ درخواست کلن وار\nکدوم کلن رو میخای به جنگ دعوت کنی?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cb.startswith("cwar_req_"):
        target_clan_name = cb[9:]
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر!", show_alert=True)
            return
        if target_clan_name not in clans:
            await query.answer("این کلن دیگه وجود نداره!", show_alert=True)
            return
        target_clan = clans[target_clan_name]
        target_leader_id = target_clan["leader"]
        # ذخیره درخواست
        target_clan.setdefault("war_requests", [])
        if cname in target_clan.get("war_requests", []):
            await query.answer("قبلاً درخواست دادی! منتظر باش.", show_alert=True)
            return
        target_clan["war_requests"].append(cname)
        save_clans(clans)
        # اطلاع به رهبر کلن هدف
        try:
            accept_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ قبول", callback_data=f"cwar_accept_{cname}"),
                InlineKeyboardButton("❌ رد", callback_data=f"cwar_decline_{cname}")
            ]])
            await ctx.bot.send_message(
                chat_id=int(target_leader_id),
                text=f"⚔️ درخواست کلن وار!\n━━━━━━━━━━━━━━━\n🏰 کلن {cname} میخواد باهات بجنگه!\n\nقبول میکنی؟",
                reply_markup=accept_kb
            )
        except:
            pass
        await query.edit_message_text(f"✅ درخواست وار به کلن {target_clan_name} ارسال شد!\nمنتظر پاسخ رهبرشون باش.")

    elif cb.startswith("cwar_accept_"):
        challenger_name = cb[12:]
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر!", show_alert=True)
            return
        if challenger_name not in clans:
            await query.answer("کلن چالش‌دهنده دیگه وجود نداره!", show_alert=True)
            return
        # شروع جنگ
        challenger_clan = clans[challenger_name]
        war_id = f"{int(time.time())}"
        war_data = {
            "clan1": challenger_name,
            "clan2": cname,
            "start_time": time.time(),
            "duration": 7200,
            "scores": {challenger_name: 0, cname: 0},
            "attacked": {},
        }
        clans[cname]["war_active"] = True
        clans[cname]["war_id"] = war_id
        clans[cname]["war_data"] = war_data
        clans[cname]["war_requests"] = [r for r in clan.get("war_requests", []) if r != challenger_name]
        clans[challenger_name]["war_active"] = True
        clans[challenger_name]["war_id"] = war_id
        clans[challenger_name]["war_data"] = war_data
        save_clans(clans)
        for member_id in clan["members"] + challenger_clan["members"]:
            try:
                my_cn = cname if member_id in clan["members"] else challenger_name
                enemy_cn = challenger_name if member_id in clan["members"] else cname
                keyboard = build_clanwar_kb(clans, data, my_cn, enemy_cn, member_id)
                await ctx.bot.send_message(
                    chat_id=int(member_id),
                    text=f"⚔️ کلن وار شروع شد!\n━━━━━━━━━━━━━━━\n🏰 {challenger_name} vs 🏰 {cname}\n⏳ مدت: 2 ساعت\n\nدستور /clanwar",
                )
            except:
                pass
        await query.edit_message_text(f"✅ جنگ با کلن {challenger_name} شروع شد!")

    elif cb.startswith("cwar_decline_"):
        challenger_name = cb[13:]
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if clan["leader"] != uid: return
        clan["war_requests"] = [r for r in clan.get("war_requests", []) if r != challenger_name]
        save_clans(clans)
        challenger_leader = clans.get(challenger_name, {}).get("leader")
        if challenger_leader:
            try:
                await ctx.bot.send_message(chat_id=int(challenger_leader), text=f"❌ کلن {cname} درخواست وارت رو رد کرد!")
            except:
                pass
        await query.edit_message_text(f"❌ درخواست وار کلن {challenger_name} رد شد.")

    elif cb == "clan_war":
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        if clan["leader"] != uid:
            await query.answer("فقط رهبر کلن میتونه جنگ شروع کنه!", show_alert=True)
            return
        if clan.get("war_active"):
            await query.answer("کلنت الان در جنگه!", show_alert=True)
            return
        if clan.get("in_queue"):
            clan["in_queue"] = False
            save_clans(clans)
            await query.edit_message_text("✅ از صف کلن وار خارج شدی!")
            return
        # matchmaking خودکار
        enemy_name = None
        for cn, cl in clans.items():
            if cn != cname and cl.get("in_queue") and not cl.get("war_active"):
                enemy_name = cn
                break
        if enemy_name:
            enemy_clan = clans[enemy_name]
            clans[cname]["in_queue"] = False
            clans[enemy_name]["in_queue"] = False
            war_id = f"{int(time.time())}"
            war_data = {
                "clan1": cname, "clan2": enemy_name,
                "start_time": time.time(), "duration": 7200,
                "scores": {cname: 0, enemy_name: 0},
                "attacked": {},
            }
            clans[cname]["war_active"] = True
            clans[cname]["war_id"] = war_id
            clans[cname]["war_data"] = war_data
            clans[enemy_name]["war_active"] = True
            clans[enemy_name]["war_id"] = war_id
            clans[enemy_name]["war_data"] = war_data
            save_clans(clans)
            for member_id in clan["members"] + enemy_clan["members"]:
                try:
                    my_cn = cname if member_id in clan["members"] else enemy_name
                    enemy_cn = enemy_name if member_id in clan["members"] else cname
                    await ctx.bot.send_message(
                        chat_id=int(member_id),
                        text=f"⚔️ کلن وار شروع شد!\n🏰 {cname} vs 🏰 {enemy_name}\n⏳ 2 ساعت\n\nدستور /clanwar",
                    )
                except:
                    pass
            await query.edit_message_text(f"⚔️ جنگ با کلن {enemy_name} شروع شد!\nدستور /clanwar رو بزن.")
        else:
            clans[cname]["in_queue"] = True
            save_clans(clans)
            await query.edit_message_text("🔍 وارد صف کلن وار شدی!\nمنتظر حریف هستیم...\n\nیا از 'درخواست وار' مستقیم یه کلن رو دعوت کن!")

    # ── کلن وار — انتخاب هدف (نمایش نیروها) ─────────
    elif cb.startswith("cw_target_"):
        target_id = cb[10:]
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        if not clan.get("war_active"):
            await query.answer("جنگ کلنی فعال نیست!", show_alert=True)
            return
        if target_id not in data:
            await query.answer("بازیکن پیدا نشد!", show_alert=True)
            return
        target = data[target_id]
        # نمایش نیروهای هدف
        army_text = "⚔️ نیروهای هدف:\n"
        for unit, count in target.get("army", {}).items():
            if unit in UNITS and count > 0:
                u = UNITS[unit]
                magic_tag = "✨" if u.get("magic") else ""
                army_text += f"  {magic_tag}{u['emoji']} {unit} ×{count} | ⚔️{u['attack']*count} 🛡️{u['defense']*count}\n"
        if not any(c > 0 for c in target.get("army", {}).values()):
            army_text += "  بدون نیرو!\n"
        army_text += f"━━━━━━━━━━━━━━━\nکل ⚔️: {get_attack_power(target)} | کل 🛡️: {get_defense_power(target)}\n\nبا کدوم نیروت حمله میکنی?"
        # کیبورد انتخاب واحد حمله
        kb = build_cw_unit_kb(target_id, p)
        await query.edit_message_text(
            f"🎯 هدف: {target.get('name','?')}\n━━━━━━━━━━━━━━━\n{army_text}",
            reply_markup=kb
        )

    # ── کلن وار — حمله با واحد انتخابی ─────────────
    elif cb.startswith("cw_atk_"):
        parts = cb[7:].split("_", 1)
        if len(parts) != 2:
            return
        target_id, attack_unit = parts
        cname = p.get("clan", "")
        if not cname or cname not in clans:
            await query.answer("عضو کلنی نیستی!", show_alert=True)
            return
        clan = clans[cname]
        if not clan.get("war_active"):
            await query.answer("جنگ کلنی فعال نیست!", show_alert=True)
            return
        if target_id in clan.get("members", []):
            await query.answer("نمیتونی به همکلنیت حمله کنی!", show_alert=True)
            return
        war_data = clan.get("war_data", {})
        enemy_name = war_data.get("clan2") if war_data.get("clan1") == cname else war_data.get("clan1")
        enemy_clan = clans.get(enemy_name, {})
        if target_id not in enemy_clan.get("members", []):
            await query.answer("این بازیکن عضو کلن دشمن نیست!", show_alert=True)
            return
        start_time = war_data.get("start_time", 0)
        if time.time() - start_time > war_data.get("duration", 7200):
            await end_clan_war(clans, data, cname, ctx)
            await query.edit_message_text("⏰ زمان جنگ تموم شد!")
            return
        if target_id not in data:
            await query.answer("بازیکن پیدا نشد!", show_alert=True)
            return
        # بررسی نیرو
        if p["army"].get(attack_unit, 0) <= 0:
            await query.answer("این نیرو رو نداری!", show_alert=True)
            return

        target = data[target_id]
        apply_clan_bonuses(p, clans)
        apply_clan_bonuses(target, clans)

        atk_power = get_attack_power(p) + random.randint(0, 30)
        def_power = get_defense_power(target) + random.randint(0, 20)
        scores = war_data.get("scores", {})

        if atk_power > def_power:
            pts = random.randint(3, 8)
            scores[cname] = scores.get(cname, 0) + pts
            loot = min(random.randint(20, 60), max(0, target["alpha_coin"] - 50))
            target["alpha_coin"] = max(50, target["alpha_coin"] - loot)
            p["alpha_coin"] += loot
            # تلفات برای دشمن بُرده شده
            lost_enemy = calc_casualties(target.get("army", {}), random.uniform(0.10, 0.25))
            target["army"] = apply_casualties(target.get("army", {}), lost_enemy)
            lost_text = ""
            if lost_enemy:
                lost_text = "\n💀 تلفات دشمن: " + " | ".join(f"{UNITS[u]['emoji']}{u}×{c}" for u, c in lost_enemy.items() if u in UNITS)
            result_atk = (
                f"⚔️ حمله کلن وار\n━━━━━━━━━━━━━━━\n"
                f"🎯 هدف: {target.get('name','')}\n"
                f"🗡️ واحد: {UNITS.get(attack_unit,{}).get('emoji','')} {attack_unit}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🎉 حمله موفق! +{pts} امتیاز\n"
                f"💰 غنیمت: +{loot} کوین{lost_text}\n"
                f"📊 امتیاز کلن: {scores.get(cname,0)}"
            )
            result_def = (
                f"🚨 پایگاهت مورد حمله قرار گرفت!\n━━━━━━━━━━━━━━━\n"
                f"⚔️ مهاجم: {p.get('name','')} از کلن {cname}\n"
                f"💰 غنیمت از دست رفته: {loot} کوین{lost_text}\n"
                f"برای دفاع /clanwar بزن!"
            )
        else:
            pts = random.randint(1, 3)
            scores[enemy_name] = scores.get(enemy_name, 0) + pts
            result_atk = (
                f"⚔️ حمله کلن وار\n━━━━━━━━━━━━━━━\n"
                f"🎯 هدف: {target.get('name','')}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💀 حمله ناموفق!\n"
                f"دشمن +{pts} امتیاز دفاعی گرفت\n"
                f"📊 امتیاز ما: {scores.get(cname,0)}"
            )
            result_def = (
                f"🛡️ حمله دشمن دفع شد!\n━━━━━━━━━━━━━━━\n"
                f"⚔️ مهاجم: {p.get('name','')} از کلن {cname}\n"
                f"+{pts} امتیاز دفاعی برای کلنت!"
            )

        war_data["scores"] = scores
        clan["war_data"] = war_data
        clans[enemy_name]["war_data"] = war_data
        save_data(data)
        save_clans(clans)
        try:
            await ctx.bot.send_message(chat_id=int(target_id), text=result_def)
        except:
            pass
        scores_now = war_data.get("scores", {})
        start_time = war_data.get("start_time", 0)
        duration = war_data.get("duration", 7200)
        remaining = max(0, duration - (time.time() - start_time))
        h = int(remaining // 3600)
        m2 = int((remaining % 3600) // 60)
        new_text = (
            f"⚔️ جنگ فعال — {cname} علیه {enemy_name}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 امتیاز: ما {scores_now.get(cname,0)} — حریف {scores_now.get(enemy_name,0)}\n"
            f"⏳ زمان باقی‌مانده: {h}h {m2}m\n\n"
            f"🎯 روی نام دشمن بزن تا نیروهاشو ببینی:"
        )
        try:
            await query.edit_message_text(new_text, reply_markup=build_clanwar_kb(clans, data, cname, enemy_name, uid))
        except:
            pass
        await query.answer(result_atk.split("\n")[4] if len(result_atk.split("\n")) > 4 else "انجام شد", show_alert=True)

    elif cb == "cw_scores":
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        war_data = clan.get("war_data", {})
        scores = war_data.get("scores", {})
        c1 = war_data.get("clan1", "")
        c2 = war_data.get("clan2", "")
        text = (
            f"📊 جدول امتیاز\n━━━━━━━━━━━━━━━\n"
            f"🏰 {c1}: {scores.get(c1,0)} امتیاز\n"
            f"🏰 {c2}: {scores.get(c2,0)} امتیاز\n"
            f"━━━━━━━━━━━━━━━\n"
            f"هر ۱ امتیاز = ۱ کوین خزانه کلن\n"
            f"هر ۱۰ امتیاز = ۱ کوین برای هر عضو"
        )
        await query.answer(text, show_alert=True)

    elif cb == "cw_refresh":
        cname = p.get("clan", "")
        if not cname or cname not in clans: return
        clan = clans[cname]
        if not clan.get("war_active"):
            await query.edit_message_text("❌ جنگ کلنی فعال نیست!")
            return
        war_data = clan.get("war_data", {})
        enemy_name = war_data.get("clan2") if war_data.get("clan1") == cname else war_data.get("clan1")
        scores = war_data.get("scores", {})
        start_time = war_data.get("start_time", 0)
        duration = war_data.get("duration", 7200)
        remaining = max(0, duration - (time.time() - start_time))
        if remaining <= 0:
            await end_clan_war(clans, data, cname, ctx)
            await query.edit_message_text("⏰ زمان جنگ تموم شد!")
            return
        h = int(remaining // 3600)
        m2 = int((remaining % 3600) // 60)
        new_text = (
            f"⚔️ جنگ فعال — {cname} علیه {enemy_name}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 امتیاز: ما {scores.get(cname,0)} — حریف {scores.get(enemy_name,0)}\n"
            f"⏳ زمان باقی‌مانده: {h}h {m2}m\n\n"
            f"🎯 روی نام دشمن بزن تا نیروهاشو ببینی:"
        )
        try:
            await query.edit_message_text(new_text, reply_markup=build_clanwar_kb(clans, data, cname, enemy_name, uid))
        except:
            pass

    # ── فروشگاه کریستال ─────────────────────────────
    elif cb == "cshop_buy_crystal":
        await query.message.reply_text(
            f"💎 خرید کریستال\n━━━━━━━━━━━━━━━\n"
            f"برای خرید کریستال با ادمین در پیوی تماس بگیر:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📩 تماس با ادمین", url="https://ble.ir/alphawaradmin")
            ], [InlineKeyboardButton("❌ بستن", callback_data="close")]])
        )

    elif cb == "cshop_shields":
        p2 = data[uid]
        now3 = time.time()
        shield_info = ""
        if p2.get("shield_until", 0) > now3:
            rem = int((p2["shield_until"] - now3) / 3600)
            shield_info = f"🔩 دیوار آهنین فعال: {rem}h مانده\n"
        kb = []
        for sid, s in CRYSTAL_SHIELDS.items():
            kb.append([InlineKeyboardButton(
                f"{s['emoji']} {s['name']} — {s['cost']}💎",
                callback_data=f"cbuy_shield_{sid}"
            )])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="cshop_back")])
        await query.edit_message_text(
            f"🔩 دیوار آهنین\n━━━━━━━━━━━━━━━\n💎 کریستال شما: {p2.get('crystal',0)}\n{shield_info}\n"
            f"دیوار آهنین از حملات دیگران محافظت می‌کنه:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif cb == "cshop_spells":
        p2 = data[uid]
        kb = []
        for sid, s in CRYSTAL_BATTLE_SPELLS.items():
            label = f"{s['emoji']} {s['name']} — {s['cost']}💎"
            if p2.get("crystal_spell") == s["spell_key"]:
                label = f"✅ {label} (فعال)"
            kb.append([InlineKeyboardButton(label, callback_data=f"cbuy_battlespell_{sid}")])
        for sid, s in CRYSTAL_SPELLS.items():
            kb.append([InlineKeyboardButton(f"{s['emoji']} {s['name']} — {s['cost']}💎", callback_data=f"cbuy_spell_{sid}")])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="cshop_back")])
        await query.edit_message_text(
            f"🔮 جادوها\n━━━━━━━━━━━━━━━\n💎 کریستال شما: {p2.get('crystal',0)}\n\n"
            f"⚔️ جادوهای نبرد (یک‌بار مصرف):\n"
            + "\n".join(f"  {s['emoji']} {s['name']}: {s['desc']}" for s in CRYSTAL_BATTLE_SPELLS.values())
            + f"\n\n📦 آیتم‌های دیگر:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif cb == "cshop_units":
        p2 = data[uid]
        kb = []
        for uname, uinfo in UNITS.items():
            if uinfo.get("crystal_unit"):
                kb.append([InlineKeyboardButton(
                    f"{uinfo['emoji']} {uname} | ⚔️{uinfo['attack']} 🛡️{uinfo['defense']} — {uinfo['crystal_cost']}💎",
                    callback_data=f"cbuy_unit_{uname}"
                )])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="cshop_back")])
        await query.edit_message_text(
            f"🐲 نیروهای ویژه کریستالی\n━━━━━━━━━━━━━━━\n💎 کریستال شما: {p2.get('crystal',0)}\n",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif cb == "cshop_boosts":
        p2 = data[uid]
        kb = []
        for bid, b in CRYSTAL_BOOSTS.items():
            kb.append([InlineKeyboardButton(
                f"{b['emoji']} {b['name']} — {b['cost']}💎",
                callback_data=f"cbuy_boost_{bid}"
            )])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="cshop_back")])
        await query.edit_message_text(
            f"⚡ بوست‌ها\n━━━━━━━━━━━━━━━\n💎 کریستال شما: {p2.get('crystal',0)}\n",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif cb == "cshop_back":
        await query.edit_message_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    elif cb.startswith("cbuy_battlespell_"):
        sid = cb[17:]
        if sid not in CRYSTAL_BATTLE_SPELLS:
            await query.answer("جادو یافت نشد!", show_alert=True); return
        s = CRYSTAL_BATTLE_SPELLS[sid]
        if p.get("crystal", 0) < s["cost"]:
            await query.answer(f"💎 کریستال کافی نداری! نیاز: {s['cost']}", show_alert=True); return
        p["crystal"] -= s["cost"]
        p["crystal_spell"] = s["spell_key"]
        save_data(data)
        await query.answer(f"✅ {s['name']} فعال شد!", show_alert=False)
        data = load_data(); p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    elif cb.startswith("cbuy_shield_"):
        sid = cb[12:]
        if sid not in CRYSTAL_SHIELDS:
            await query.answer("آیتم یافت نشد!", show_alert=True); return
        s = CRYSTAL_SHIELDS[sid]
        if p.get("crystal", 0) < s["cost"]:
            await query.answer(f"💎 کریستال کافی نداری! نیاز: {s['cost']}", show_alert=True); return
        p["crystal"] -= s["cost"]
        now3 = time.time()
        p["shield_until"] = max(p.get("shield_until", 0), now3) + s["duration"]
        save_data(data)
        hours = s["duration"] // 3600
        await query.answer(f"✅ دیوار آهنین {hours}h فعال شد!", show_alert=False)
        data = load_data(); p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    elif cb.startswith("cbuy_spell_"):
        sid = cb[11:]
        if sid not in CRYSTAL_SPELLS:
            await query.answer("آیتم یافت نشد!", show_alert=True); return
        s = CRYSTAL_SPELLS[sid]
        if p.get("crystal", 0) < s["cost"]:
            await query.answer(f"💎 کریستال کافی نداری! نیاز: {s['cost']}", show_alert=True); return
        p["crystal"] -= s["cost"]
        now3 = time.time()
        notif = ""
        if s["type"] == "loot_box":
            loot_coin = random.randint(500, 2000)
            loot_unit = random.choice([u for u in UNITS if not UNITS[u].get("crystal_unit")])
            loot_count = random.randint(3, 10)
            p["alpha_coin"] += loot_coin
            p["army"][loot_unit] = p["army"].get(loot_unit, 0) + loot_count
            notif = f"🗝️ +{loot_coin}🪙 | {loot_count}x {loot_unit}"
        else:
            p.setdefault("active_boosts", {})[s["type"]] = now3 + s["duration"]
            notif = f"✅ {s['name']} فعال شد!"
        save_data(data)
        await query.answer(notif, show_alert=False)
        data = load_data(); p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    elif cb.startswith("cbuy_unit_"):
        uname = cb[10:]
        if uname not in UNITS or not UNITS[uname].get("crystal_unit"):
            await query.answer("نیرو یافت نشد!", show_alert=True); return
        uinfo = UNITS[uname]
        cost = uinfo["crystal_cost"]
        if p.get("crystal", 0) < cost:
            await query.answer(f"💎 کریستال کافی نداری! نیاز: {cost}", show_alert=True); return
        p["crystal"] -= cost
        p["army"][uname] = p["army"].get(uname, 0) + 1
        save_data(data)
        await query.answer(f"✅ {uinfo['emoji']} {uname} به ارتشت پیوست!", show_alert=False)
        data = load_data(); p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    elif cb.startswith("cbuy_boost_"):
        bid = cb[11:]
        if bid not in CRYSTAL_BOOSTS:
            await query.answer("بوست یافت نشد!", show_alert=True); return
        b = CRYSTAL_BOOSTS[bid]
        if p.get("crystal", 0) < b["cost"]:
            await query.answer(f"💎 کریستال کافی نداری! نیاز: {b['cost']}", show_alert=True); return
        p["crystal"] -= b["cost"]
        now3 = time.time()
        p.setdefault("active_boosts", {})[b["type"]] = now3 + b["duration"]
        save_data(data)
        await query.answer(f"✅ {b['name']} فعال شد!", show_alert=False)
        data = load_data(); p = get_player(data, query.from_user.id)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(crystalshop_text(p), reply_markup=crystalshop_kb())

    # ── ادمین ──────────────────────────────────────
    elif cb.startswith("adm_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("دسترسی ندارید!", show_alert=True)
            return

        if cb == "adm_confirm_fullreset":
            save_data({})
            save_clans({})
            await query.edit_message_text("✅ ریست کامل انجام شد! همه داده‌ها پاک شدند.")
            return

        if cb == "adm_fullreset":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تأیید — پاک کن همه چیز رو", callback_data="adm_confirm_fullreset")],
                [InlineKeyboardButton("❌ لغو", callback_data="close")],
            ])
            await query.edit_message_text(
                "⚠️ ریست کامل!\nهمه بازیکنان، کلن‌ها، نیروها و ساختمان‌ها پاک میشن.\nمطمئنی؟",
                reply_markup=kb
            )
            return

        texts = {
            "adm_addcoin":     "🪙 /addcoin [@یوزر یا آیدی] [مقدار]",
            "adm_addcrystal":  "💎 /addcrystal [@یوزر یا آیدی] [مقدار]",
            "adm_subcrystal":  "💎 /subcrystal [@یوزر یا آیدی] [مقدار]",
            "adm_viewcrystal": "🔍 /viewcrystal [@یوزر یا آیدی]\nبدون آرگومان = همه بازیکنان",
            "adm_ban":         "🚫 /ban [@یوزر یا آیدی]",
            "adm_unban":       "✅ /unban [@یوزر یا آیدی]",
            "adm_broadcast":   "📢 /broadcast [پیام]",
            "adm_resethp":     "❤️ /resethp [@یوزر یا آیدی]",
            "adm_resetplayer": "🔄 /resetplayer [@یوزر یا آیدی]\n⚠️ تمام پیشرفت پاک میشه!",
        }
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back")]])
        if cb == "adm_stats":
            stats_text = (
                f"📊 آمار کلی:\n━━━━━━━━━━━━━━━\n"
                f"👥 کل بازیکن: {len(data)}\n"
                f"🚫 بن شده: {sum(1 for x in data.values() if x.get('banned'))}\n"
                f"🪙 کل کوین: {sum(x.get('alpha_coin',0) for x in data.values())}\n"
                f"💎 کل کریستال: {sum(x.get('crystal',0) for x in data.values())}"
            )
            await query.edit_message_text(stats_text, reply_markup=back_kb)
        elif cb == "adm_back":
            admin_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🪙 اضافه کوین",    callback_data="adm_addcoin"),
                 InlineKeyboardButton("💎 اضافه کریستال", callback_data="adm_addcrystal")],
                [InlineKeyboardButton("💎 کم کریستال",    callback_data="adm_subcrystal"),
                 InlineKeyboardButton("🔍 موجودی کریستال",callback_data="adm_viewcrystal")],
                [InlineKeyboardButton("📊 آمار",          callback_data="adm_stats"),
                 InlineKeyboardButton("📢 پیام همگانی",   callback_data="adm_broadcast")],
                [InlineKeyboardButton("🚫 بن",            callback_data="adm_ban"),
                 InlineKeyboardButton("✅ رفع بن",         callback_data="adm_unban")],
                [InlineKeyboardButton("❤️ ریست HP",       callback_data="adm_resethp"),
                 InlineKeyboardButton("🔄 ریست بازیکن",   callback_data="adm_resetplayer")],
                [InlineKeyboardButton("💣 ریست کامل بازی",callback_data="adm_fullreset")],
                [InlineKeyboardButton("❌ بستن",           callback_data="close")],
            ])
            await query.edit_message_text("👑 پنل مدیریت Alpha War\n━━━━━━━━━━━━━━━", reply_markup=admin_kb)
        elif cb in texts:
            await query.edit_message_text(f"👑 پنل ادمین\n━━━━━━━━━━━━━━━\n{texts[cb]}", reply_markup=back_kb)

# ═══════════════════════════════════════════════════
#  Text Handler
# ═══════════════════════════════════════════════════
async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = ctx.user_data.get("action")

    if action == "create_clan":
        cname = update.message.text.strip()
        if len(cname) < 3 or len(cname) > 20:
            await update.message.reply_text("❌ اسم کلن باید بین 3 تا 20 حرف باشه!")
            return
        data = load_data()
        clans = load_clans()
        p = get_player(data, update.effective_user.id)
        uid = str(update.effective_user.id)
        if p.get("clan"):
            await update.message.reply_text("❌ قبلاً عضو کلن هستی! اول خارج شو.")
            ctx.user_data.pop("action", None)
            return
        if cname in clans:
            await update.message.reply_text("❌ این اسم قبلاً استفاده شده!")
            return
        if p["alpha_coin"] < 5000:
            await update.message.reply_text("❌ برای ساخت کلن به 5000 آلفاکوین نیاز داری!")
            ctx.user_data.pop("action", None)
            return
        p["alpha_coin"] -= 5000
        clans[cname] = {
            "leader": uid, "members": [uid], "score": 0, "wars_won": 0,
            "last_war": 0, "region_level": 1, "war_active": False,
            "war_data": {}, "in_queue": False, "treasury": 0,
            "pending_requests": [], "war_requests": [],
        }
        p["clan"] = cname
        save_data(data)
        save_clans(clans)
        ctx.user_data.pop("action", None)
        r = CLAN_REGIONS[1]
        await update.message.reply_text(
            f"✅ کلن {cname} ساخته شد!\n"
            f"👑 تو رهبر هستی.\n"
            f"🗺️ منطقه اول: {r['emoji']} {r['name']}\n"
            f"بوف: ⚔️+{r['atk_bonus']}% | 🛡️+{r['def_bonus']}% | 💰+{r['income_bonus']}%\n\n"
            f"با /clan کلنت رو مدیریت کن!\n"
            f"بازیکن‌ها باید درخواست عضویت بدن و تو قبولشون کنی."
        )

    elif action == "search_clan":
        query_text = update.message.text.strip().lower()
        data = load_data()
        clans = load_clans()
        p = get_player(data, update.effective_user.id)
        ctx.user_data.pop("action", None)

        results = [(cname, clan) for cname, clan in clans.items() if query_text in cname.lower()]
        if not results:
            await update.message.reply_text(f"❌ کلنی با نام '{query_text}' پیدا نشد!")
            return
        keyboard = []
        for cname, clan in results[:5]:
            members = len(clan["members"])
            r = CLAN_REGIONS.get(clan.get("region_level", 1), CLAN_REGIONS[1])
            score = clan.get("score", 0)
            is_full = members >= MAX_CLAN_MEMBERS
            label = f"🔒 {cname} (پر)" if is_full else f"🏰 {cname} | {members}/{MAX_CLAN_MEMBERS} | 🏆{score}"
            keyboard.append([InlineKeyboardButton(
                label,
                callback_data="locked" if is_full else f"crequest_{cname}"
            )])
        keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="close")])
        await update.message.reply_text(
            f"🔍 نتایج جستجو برای '{query_text}':\n(برای درخواست عضویت بزن)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ═══════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).base_url("https://tapi.bale.ai/").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite_cmd))
    app.add_handler(CommandHandler("shop", shop_cmd))
    app.add_handler(CommandHandler("build", build_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CommandHandler("spell", spell_cmd))
    app.add_handler(CommandHandler("collect", collect_cmd))
    app.add_handler(CommandHandler("spin", spin_cmd))
    app.add_handler(CommandHandler("mission", mission_cmd))
    app.add_handler(CommandHandler("clan", clan_cmd))
    app.add_handler(CommandHandler("clanwar", clanwar_cmd))
    app.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
    app.add_handler(CommandHandler("crystalshop", crystalshop_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("addcoin", addcoin_cmd))
    app.add_handler(CommandHandler("addcrystal", addcrystal_cmd))
    app.add_handler(CommandHandler("subcrystal", subcrystal_cmd))
    app.add_handler(CommandHandler("viewcrystal", viewcrystal_cmd))
    app.add_handler(CommandHandler("fullreset", fullreset_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("resethp", resethp_cmd))
    app.add_handler(CommandHandler("resetplayer", resetplayer_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Alpha War - Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
