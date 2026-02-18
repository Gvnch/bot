from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types
import time
import threading
import random
import html
import re
import unicodedata
import json
import os
import sys

# ══════════════ سيرفر Render (لإبقاء البوت نشطاً) ══════════════
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        pass

def run_server():
    try:
        server = HTTPServer(("0.0.0.0", 10000), handler)
        print("--- Server Started on Port 10000 ---")
        server.serve_forever()
    except Exception as e:
        print(f"Server Error: {e}")

Thread(target=run_server, daemon=True).start()

# ══════════════ إعدادات البوت ══════════════
# ⚠️ ضع التوكن الخاص بك هنا
TOKEN = "8300157614:AAFE7hhuCZ9qdn1FSPe-xOOhWilfgXJd3NE"

OWNER_USERNAME = "O_SOHAIB_O"
OWNER_CHAT_ID = None
PUBLIC_GROUP_ID = -1002493822482

# إعدادات الاتصال المحسنة لمنع تضارب رندر
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True, num_threads=3)

# ⚠️ حذف الويب هوك لمنع تضارب النسخ (Error 409)
try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass

try:
    BOT_INFO = bot.get_me()
    BOT_ID = BOT_INFO.id
    BOT_USERNAME = BOT_INFO.username
    print(f"--- Logged in as: {BOT_USERNAME} ---")
except Exception as e:
    print(f"Login Failed: {e}")

# ══════════════ الذاكرة ══════════════
games = {}
user_to_game = {}

# ⚠️ التعديل الجذري: استخدام RLock بدلاً من Lock لمنع التجميد (Deadlock)
bot_lock = threading.RLock()

wallets_db = {}
profiles_db = {}
hall_of_fame = {
    "wins": {}, "surgeon_kills": {}, "doc_saves": {},
    "observer_reveals": {}, "bombs": {}, "deaths": {},
    "messages": {},
}

# ══════════════ ثوابت ══════════════
MAX_GAMES = 100
MAX_PLAYERS = 15
DEFAULT_WAIT_TIME = 60
INACTIVITY_TIMEOUT = 300

NIGHT_TIME = 50
LAST_GASP_TIME = 15
DISCUSS_TIME = 60
VOTE_TIME = 30
CONFIRM_TIME = 15
DEFENSE_TIME = 20
WILL_TIME = 30
BOMB_TIME = 20
ROOM_CHOOSE_TIME = 25

VOTE_GAME_ASK_TIME = 45
VOTE_GAME_VOTE_TIME = 20
VOTE_GAME_ANSWER_TIME = 30
VOTE_GAME_DISCUSS_TIME = 15

AFK_KILL_THRESHOLD = 2
AFK_WARNING_THRESHOLD = 1
MEDICAL_DROP_CHANCE = 0.3
DOCTOR_FAIL_CHANCE = 0.1

WIN_REWARD = 60
LOSE_REWARD = 10
MVP_BONUS = 25

ROOM_NAMES = {
    1: "🛏 الجناح A",
    2: "🛏 الجناح B",
    3: "🔬 المختبر",
    4: "🏚 القبو",
    5: "🌑 الممر المظلم",
}

# ══════════════ الأصول (Assets) ══════════════
ASSETS = {
    "NIGHT": "AgACAgQAAxkBAAOAaYVV970SelJjAdfgC2lejaG2UXIAAjcMaxtYrDFQipw_Ve7HzpEBAAMCAAN4AAM4BA",
    "DAY": "AgACAgQAAxkBAAOVaYW5klHrisedX42r1ZlR5rHoBawAAp4Maxt3RDBQDWc7kkg-my0BAAMCAAN5AAM4BA",
    "LOBBY": "CgACAgQAAxkBAAOQaYVbS9aSPzDTHS3eGmnRwL3a0aUAAmAfAAJ3RChQ180c8TNqhjc4BA",
    "VOTE": "AgACAgQAAxkBAANYaYUTJSrHhkDUESz7dLuUONpJWUsAAqoNaxuKXihQitHU1Aa5h9gBAAMCAAN5AAM4BA",
}

# ══════════════ الأدوار ══════════════
ROLE_DISPLAY = {
    "Surgeon": "🔪 الجرّاح", "Anesthetist": "💉 المخدّر",
    "Instigator": "🧠 المحرّض", "Psychopath": "🤡 المجنون",
    "Doctor": "🩺 الطبيب", "Observer": "👁 المراقب",
    "Swapper": "🛏 عابث الأسرّة", "Patient": "🤕 المريض",
    "Screamer": "😱 المرعوب", "Nurse": "💊 الممرّض",
    "Security": "👮 حارس الأمن",
}

ROLE_TEAM = {
    "Surgeon": "evil", "Anesthetist": "evil",
    "Instigator": "neutral",
    "Doctor": "good", "Observer": "good", "Swapper": "good",
    "Patient": "good", "Psychopath": "psycho",
    "Screamer": "good", "Nurse": "good",
    "Security": "good",
}

INSTANT_ROLES = {"Surgeon", "Doctor", "Security", "Nurse", "Anesthetist"}

ROLE_ACTION_MAP = {
    "Surgeon": "surgeon", "Doctor": "doctor", "Anesthetist": "anesthetist",
    "Observer": "observer", "Instigator": "instigator", "Swapper": "swapper",
    "Nurse": "nurse", "Patient": "patient", "Security": "security"
}

SILENT_PHASES = {
    "night", "morning", "roles_reveal", "resolving",
    "waiting_q", "answering", "will_wait", "last_gasp_wait",
    "confirming", "defense", "qa_results", "ended",
    "room_choosing",
}

# ══════════════ المتجر والألقاب ══════════════
TITLE_DEFS = {
    "chatterbox": {"icon": "🗣️", "name": "الثرثار", "desc": "أكثر واحد حكى"},
    "sherlock": {"icon": "🕵️", "name": "شارلوك", "desc": "صوّت على القاتل صح"},
    "silent": {"icon": "🤐", "name": "الصامت", "desc": "أقل واحد حكى"},
    "angel": {"icon": "😇", "name": "ملاك الرحمة", "desc": "الطبيب أنقذ"},
    "reaper": {"icon": "💀", "name": "حاصد الأرواح", "desc": "الجرّاح نجا للنهاية"},
    "first_blood": {"icon": "🩸", "name": "أول دم", "desc": "أول ضحية"},
    "survivor": {"icon": "🏆", "name": "الناجي", "desc": "بقي حياً"},
}

SHOP_ITEMS = {
    "shield": {"name": "🛡 درع الروح", "price": 120, "desc": "حماية لمرة واحدة ليلاً"},
    "spy_glass": {"name": "🔭 منظار", "price": 90, "desc": "كشف فريق لاعب"},
    "file_gold": {"name": "📂 ملف ذهبي", "price": 180, "desc": "كشف دور لاعب عشوائي"},
    "title_vip": {"name": "👑 لقب VIP", "price": 600, "desc": "تاج بجانب الاسم"},
}

JOKER_OPTIONS = {
    "cancel_vote": {"name": "🔄 إلغاء التصويت", "desc": "إبطال الأصوات"},
    "shield_now": {"name": "🛡 حماية طارئة", "desc": "حماية فورية"},
    "reveal_one": {"name": "👁 كشف فوري", "desc": "كشف دور"},
    "double_vote": {"name": "🗳 صوت مزدوج", "desc": "صوتك بـ 2"},
    "skip_night": {"name": "⏭ تخطّي ليلة", "desc": "إلغاء أفعال الليل"},
}

# ══════════════ أدوات مساعدة ══════════════
def clean(t, mx=200):
    s = str(t or "")
    s = s.replace('\n', ' ').replace('\r', '')
    return html.escape(s[:mx])

def clean_name(t):
    s = str(t or "مجهول")
    s = s.replace('\n', '').replace('\r', '')
    return html.escape(s[:25])

def pname(uid, name):
    return f"<a href='tg://user?id={uid}'><b>{name}</b></a>"

def pname_vip(uid, name):
    crown = "👑 " if has_title(uid, "title_vip") else ""
    return f"{crown}<a href='tg://user?id={uid}'><b>{name}</b></a>"

def normalize_arabic(t):
    if not t: return ""
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = re.sub(r'[^\w\s]', '', t.strip().lower())
    for a, b in [("[إأآاٱ]", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")]:
        t = re.sub(a, b, t)
    t = re.sub(r'[٠-٩]', lambda m: str("٠١٢٣٤٥٦٧٨٩".index(m.group())), t)
    return re.sub(r'\s+', ' ', t).strip()

def corrupt_text(text):
    words = text.split()
    new_words = []
    for w in words:
        if random.random() < 0.6: 
            new_words.append("." * random.randint(2, 5))
        else:
            new_words.append(w)
    return " ".join(new_words)

# ══════════════ المحفظة والبروفايل ══════════════
def get_wallet(uid):
    if uid not in wallets_db:
        wallets_db[uid] = {"coins": 0, "gems": 0, "inventory": [], "titles": []}
    return wallets_db[uid]

def add_coins(uid, amount):
    w = get_wallet(uid)
    w["coins"] += amount

def has_item(uid, item_id):
    return item_id in get_wallet(uid)["inventory"]

def use_item(uid, item_id):
    w = get_wallet(uid)
    if item_id in w["inventory"]:
        w["inventory"].remove(item_id)
        return True
    return False

def has_title(uid, title_id):
    return title_id in get_wallet(uid)["titles"]

def buy_item(uid, item_id):
    if item_id not in SHOP_ITEMS:
        return False, "❌ غير موجود"
    w = get_wallet(uid)
    item = SHOP_ITEMS[item_id]
    if w["coins"] < item["price"]:
        return False, "❌ رصيدك لا يكفي"
    if item_id.startswith("title_"):
        if item_id in w["titles"]:
            return False, "❌ تملكه بالفعل"
        w["coins"] -= item["price"]
        w["titles"].append(item_id)
    else:
        w["coins"] -= item["price"]
        w["inventory"].append(item_id)
    return True, f"✅ حصلت على <b>{item['name']}</b>"

def get_profile(uid):
    if uid not in profiles_db:
        profiles_db[uid] = {
            "games": 0, "wins": 0, "losses": 0,
            "kills_as_surgeon": 0, "saves_as_doc": 0,
            "reveals_as_obs": 0, "bombs_triggered": 0,
            "deaths": 0, "messages_sent": 0,
            "best_streak": 0, "current_streak": 0,
            "xp": 0,
        }
    return profiles_db[uid]

def add_xp(uid, amount):
    p = get_profile(uid)
    p["xp"] += amount

def update_hall(category, uid, value=1):
    if uid not in hall_of_fame[category]:
        hall_of_fame[category][uid] = 0
    hall_of_fame[category][uid] += value

# ══════════════ الإرسال والإدارة (الآمنة) ══════════════
def safe_send(cid, text, **kw):
    try:
        return bot.send_message(cid, text, parse_mode="HTML", **kw)
    except Exception as e:
        print(f"Error sending to {cid}: {e}")
        return None

def safe_pm(uid, text, **kw):
    try:
        return bot.send_message(uid, text, parse_mode="HTML", **kw)
    except:
        return None

def safe_edit_caption(cid, mid, text, **kw):
    try:
        return bot.edit_message_caption(caption=text, chat_id=cid, message_id=mid, parse_mode="HTML", **kw)
    except:
        return None

def safe_edit_text(cid, mid, text, **kw):
    try:
        return bot.edit_message_text(text, chat_id=cid, message_id=mid, parse_mode="HTML", **kw)
    except:
        return None

def delete_msg(cid, mid):
    try:
        bot.delete_message(cid, mid)
    except:
        pass

def safe_pin(cid, mid):
    try:
        bot.pin_chat_message(cid, mid, disable_notification=True)
    except:
        pass

def safe_unpin(cid, mid):
    try:
        bot.unpin_chat_message(cid, mid)
    except:
        pass

def safe_unpin_all(cid):
    try:
        bot.unpin_all_chat_messages(cid)
    except:
        pass

def mute_all(cid):
    try:
        bot.set_chat_permissions(cid, types.ChatPermissions(can_send_messages=False))
    except:
        pass

def unmute_all(cid):
    try:
        bot.set_chat_permissions(cid, types.ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True))
    except:
        pass

def mute_player(cid, uid):
    try:
        bot.restrict_chat_member(cid, uid, permissions=types.ChatPermissions(can_send_messages=False))
    except:
        pass

def unmute_player(cid, uid):
    try:
        bot.restrict_chat_member(cid, uid, permissions=types.ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True))
    except:
        pass

def silence_all(cid):
    mute_all(cid)
    with bot_lock:
        if cid not in games: return
        uids = list(games[cid]["players"].keys())
    for uid in uids:
        mute_player(cid, uid)

def open_discussion(cid):
    with bot_lock:
        if cid not in games: return
        dead_u = [u for u, p in games[cid]["players"].items() if not p["alive"]]
        alive_u = [u for u, p in games[cid]["players"].items() if p["alive"]]
    unmute_all(cid)
    time.sleep(0.3)
    for uid in alive_u: unmute_player(cid, uid)
    time.sleep(0.2)
    for uid in dead_u: mute_player(cid, uid)

# ══════════════ التنظيف الشامل ══════════════
_cleanup_lock = threading.Lock()

def force_cleanup(cid):
    # مع RLock، يمكننا الدخول هنا حتى لو كنا نمسك القفل في دالة أخرى
    with _cleanup_lock:
        with bot_lock:
            if cid in games:
                uids = list(games[cid].get("players", {}).keys())
                for uid in uids:
                    user_to_game.pop(uid, None)
                del games[cid]
        safe_unpin_all(cid)
        unmute_all(cid)
        try:
            bot.set_chat_permissions(cid, types.ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True, can_add_web_page_previews=True))
        except:
            pass

# ══════════════ أدوات اللعبة ══════════════
def get_alive(cid):
    if cid not in games: return {}
    return {u: p for u, p in games[cid]["players"].items() if p["alive"]}

def get_alive_except(cid, exc):
    return {u: p for u, p in get_alive(cid).items() if u != exc}

def is_participant(cid, uid):
    return cid in games and uid in games[cid]["players"]

def find_game_for_user(uid):
    return user_to_game.get(uid)

def valid_game(cid, gid):
    return cid in games and games[cid]["game_id"] == gid

def is_game_active(cid, gid):
    with bot_lock:
        return valid_game(cid, gid)

def kill_player(g, uid):
    if not g["players"][uid]["alive"]: return False
    g["players"][uid]["alive"] = False
    if uid not in g["dead_list"]:
        g["dead_list"].append(uid)
    if not g["stats"]["first_death"]:
        g["stats"]["first_death"] = uid
    return True

def get_original_team(g, uid):
    ot = g.get("original_team", {})
    if uid in ot: return ot[uid]
    return ROLE_TEAM.get(g["players"][uid]["role"], "good")

def safe_sleep(cid, gid, seconds):
    end = time.time() + seconds
    while time.time() < end:
        time.sleep(min(1.0, end - time.time()))
        with bot_lock:
            if not valid_game(cid, gid): return False
    return True

def get_room_players(g, room_id, alive_only=True):
    result = {}
    for uid, p in g["players"].items():
        if alive_only and not p["alive"]: continue
        if g["room_choices"].get(uid) == room_id:
            result[uid] = p
    return result

def get_player_room(g, uid):
    return g["room_choices"].get(uid)

def get_room_targets(g, uid, exclude_self=True):
    my_room = get_player_room(g, uid)
    if not my_room: return {}
    
    if my_room == 5: 
        players = {u: p for u, p in g["players"].items() if p["alive"]}
    else: 
        players = get_room_players(g, my_room)
    
    if exclude_self:
        return {u: p for u, p in players.items() if u != uid}
    return players

def get_roles_for_count(n):
    n = max(n, 4)
    base = ["Surgeon", "Doctor", "Observer", "Patient"]
    if n >= 5: base.append("Anesthetist")
    if n >= 6: base.append("Nurse") 
    if n >= 7: base.append("Security") 
    
    pool = ["Psychopath", "Screamer", "Instigator", "Swapper", "Patient"]
    while len(base) < n:
        r = random.choice(pool)
        base.append(r)
        
    random.shuffle(base)
    return base[:n]

def transfer_radio(g, dead_uid, killer_uid=None):
    if dead_uid in g["radio_holders"]:
        g["radio_holders"].remove(dead_uid)
        new_holder = None
        if killer_uid and killer_uid in g["players"] and g["players"][killer_uid]["alive"]:
            new_holder = killer_uid
        else:
            alive = [u for u in g["players"] if g["players"][u]["alive"] and u != dead_uid]
            if alive:
                new_holder = random.choice(alive)
        if new_holder:
            g["radio_holders"].add(new_holder)
            safe_pm(new_holder, "📻 <b>لقد عثرت على لاسلكي!</b>\n\nتحدث عبره للشرير باستخدام:\n<code>/لاسلكي الرسالة</code>")

# ══════════════ بيانات اللعبة ══════════════
def new_game_data(gtype, host_id, gid):
    return {
        "type": gtype, "host": host_id, "players": {}, "phase": "joining",
        "start_at": time.time() + DEFAULT_WAIT_TIME,
        "total_wait": DEFAULT_WAIT_TIME,
        "last_activity": time.time(), "game_id": gid,
        "lobby_mid": None, "lobby_mt": "text",
        "rooms_enabled": (gtype == "hospital"),
        "room_choices": {},
        "room_chat_notified": set(),
        "actions": {}, "votes": {}, "confirm_votes": {},
        "bomb": {"is_set": False, "q": "", "a": "", "raw": "", "defuser": None, "owner": None},
        "round": 0, "dead_list": [], "silenced": set(),
        "sedated_current": set(),
        "screamer_visitors": {}, "swap_data": {}, "nurse_poison": {},
        "will_pending": {}, "anesthetist_uses": {},
        "nurse_has_poison": {},
        "patient_used": set(), "psycho_phase": {},
        "confirm_target": None, "defense_target": None,
        "asker": None, "vote_question": None,
        "asked_uids": set(), "asked_uids_done": set(),
        "vote_round": 0, "game_started_at": 0,
        "ask_msg_id": None,
        "role_revealed": set(), "ability_night": {},
        "ability_drawn": set(),
        "night_acted": set(), "instigator_steal": {},
        "observer_targets": {},
        "ask_prompt_sent": False, "ask_type": None, "ask_type_chosen": False,
        "qa_answers": {}, "qa_answer_pending": set(), "qa_answer_done": set(), "qa_current_round": 0,
        "afk_count": {}, "afk_warned": set(),
        "round_voted": set(), "round_night_acted": set(),
        "round_msg_count": {}, "round_complete_actions": set(),
        "med_items": {},
        "blackout_used": False, "blackout_active": False,
        "last_gasp_pending": {}, "last_gasp_text": {},
        "original_team": {}, "evil_chat_ids": set(),
        "suspect_votes": {},
        "joker_holder": None, "joker_used": False, "joker_effect": None,
        "radio_holders": set(),
        "security_ammo": {}, 
        "observer_last_reveal": None,
        "security_checked_cam": set(), 
        "stats": {
            "msg_count": {}, "first_death": None,
            "surgeon_uid": None, "voted_surgeon": set(),
            "doc_saves": 0, "doc_fails": 0,
            "bomb_exploded": False, "bomb_defuser": None,
            "scalpel_kills": set(), "voted_against": {},
            "rooms_history": [],
        },
        "pinned_mids": [], "winners_team": None,
    }

# ══════════════ نظام الفوز ══════════════
def _check_win_inner(cid):
    if cid not in games: return None
    g = games[cid]
    pp = g["players"]
    alive = {u: p for u, p in pp.items() if p["alive"]}

    if not alive:
        g["winners_team"] = None
        return "⚰️ <b>لا ناجين... المستشفى ابتلع الجميع.</b>"

    evil_alive = [u for u in alive if get_original_team(g, u) == "evil"]
    good_alive = [u for u in alive if get_original_team(g, u) == "good"]
    psycho_alive = [u for u in alive if get_original_team(g, u) == "psycho"]
    neutral_alive = [u for u in alive if get_original_team(g, u) == "neutral"]

    total_alive = len(alive)

    if psycho_alive and not evil_alive and len(alive) <= 2:
        g["winners_team"] = "psycho"
        return "🤡 <b>المجنون يرقص وحيداً فوق الجثث.</b>"

    if not good_alive and not psycho_alive and not neutral_alive:
        g["winners_team"] = "evil"
        return "🔪 <b>الظلام انتصر... الأطباء ماتوا.</b>"

    if not evil_alive and not psycho_alive:
        g["winners_team"] = "good"
        return "🩺 <b>تم تطهير المستشفى... النور ينتصر.</b>"

    # حالات خاصة
    has_surgeon = any(pp[u]["role"] == "Surgeon" for u in evil_alive)
    has_active_killer = has_surgeon or any(pp[u]["role"] == "Anesthetist" for u in evil_alive)
    
    if total_alive == 2 and has_surgeon and good_alive:
        g["winners_team"] = "evil"
        return "🔪 <b>المشرط أسرع... الجرّاح فاز.</b>"

    if evil_alive and not has_active_killer:
        patient_can = any(pp[u]["role"] == "Patient" and u not in g.get("patient_used", set()) for u in alive)
        dead_surg = any(pp[u]["role"] == "Surgeon" and not pp[u]["alive"] for u in pp)
        if not (patient_can and dead_surg):
            g["winners_team"] = "good"
            return "🩺 <b>سقط آخر قاتل...</b>"

    non_evil = len(good_alive) + len(psycho_alive) + len(neutral_alive)
    if evil_alive and len(evil_alive) >= non_evil:
        g["winners_team"] = "evil"
        return "🔪 <b>الكثرة تغلب... الأشرار سيطروا.</b>"

    return None

def check_win_safe(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return True
        result = _check_win_inner(cid)
    if result:
        show_results(cid, result)
        return True
    return False

def show_results(cid, msg):
    with bot_lock:
        if cid not in games: return
        g = games[cid]
        g["phase"] = "ended"
        
        lines = []
        for u, p in g["players"].items():
            status = "حي" if p["alive"] else "ميت"
            lines.append(f"▫️ {p['name']}: {ROLE_DISPLAY.get(p['role'], '?')} ({status})")
    
    full = f"{msg}\n\n<b>الأدوار:</b>\n" + "\n".join(lines)
    safe_send(cid, full)
    force_cleanup(cid)

def check_afk(cid):
    return [], []

def do_medical_drop(cid, gid):
    pass

# ══════════════ حلقة اللعبة ══════════════
def game_loop():
    while True:
        time.sleep(3)
        now = time.time()
        to_del = []
        to_start = []
        with bot_lock:
            for cid in list(games.keys()):
                g = games[cid]
                if now - g["last_activity"] > INACTIVITY_TIMEOUT:
                    to_del.append(cid)
                    continue
                if g["phase"] == "joining" and g["start_at"] <= now:
                    g["phase"] = "starting"
                    to_start.append((cid, g["type"], g["game_id"]))
        
        for c in to_del:
            safe_send(c, "🕯 <i>انطفأت الأنوار... (انتهت المهلة)</i>")
            force_cleanup(c)
        
        for c, t, gid in to_start:
            target = start_hospital if t == "hospital" else start_vote_game
            threading.Thread(target=target, args=(c, gid), daemon=True).start()

threading.Thread(target=game_loop, daemon=True).start()

# ══════════════ اللوبي ══════════════
MIN_HOSPITAL = 4
MIN_VOTE = 3

def build_lobby(cid):
    if cid not in games: return "Error"
    g = games[cid]
    rem = max(0, int(g["start_at"] - time.time()))
    total = max(g.get("total_wait", DEFAULT_WAIT_TIME), 1)
    gt = g["type"]
    pp = g["players"]
    n = len(pp)

    if gt == "hospital":
        mn = MIN_HOSPITAL
        title = "🏥 المستشفى المهجور"
        flavor = "الممرات مظلمة... ثق بحدسك فقط."
    else:
        mn = MIN_VOTE
        title = "⚖️ مجلس التصويت"
        flavor = "ايش دخلك؟ انقلع"

    if n == 0:
        pt = "   <i>(لا أحد بعد)</i>"
    else:
        lines = []
        for u, p in pp.items():
            lines.append(f"   🔹 {pname_vip(u, p['name'])}")
        pt = "\n".join(lines)

    bar_f = int(min(max(rem / total, 0), 1.0) * 10)
    bar = "▓" * bar_f + "░" * (10 - bar_f)
    m, sc = divmod(max(0, rem), 60)
    ts = f"{m}:{sc:02d}" if m else f"{sc}s"

    return (
        f"{title}\n\n"
        f"⏳ {bar}  <b>{ts}</b>\n\n"
        f"<i>{flavor}</i>\n\n"
        f"👥 <b>المسجلون ({n}):</b>\n{pt}\n\n"
        f"📌 مطلوب: <b>{mn}</b>\n\n"
        f"🚀 <code>/force_start</code>  ·  ⏱ <code>/time 30</code>"
    )

def join_markup(gid, gtype="hospital"):
    m = types.InlineKeyboardMarkup()
    btn_text = "🩸 توقيع الدخول" if gtype == "hospital" else "🗳️ تسجيل الحضور"
    m.add(types.InlineKeyboardButton(btn_text, callback_data=f"join_{gid}"))
    return m

def lobby_tick(cid, gid):
    resent = False
    while True:
        time.sleep(8)
        with bot_lock:
            if not valid_game(cid, gid) or games[cid]["phase"] != "joining": return
            rem = max(0, int(games[cid]["start_at"] - time.time()))
            gt = games[cid]["type"]

        if rem <= 25 and not resent:
            resent = True
            with bot_lock:
                if not valid_game(cid, gid): return
                txt = build_lobby(cid)
                mk = join_markup(gid, gt)
            asset = ASSETS["LOBBY"] if gt == "hospital" else ASSETS["VOTE"]
            
            # محاولة إرسال ميديا أو نص
            nm = None
            try:
                if gt == "hospital":
                    nm = bot.send_animation(cid, asset, caption=txt, parse_mode="HTML", reply_markup=mk)
                else:
                    nm = bot.send_photo(cid, asset, caption=txt, parse_mode="HTML", reply_markup=mk)
            except Exception as e:
                print(f"Media Failed: {e}")
                nm = safe_send(cid, txt, reply_markup=mk)

            if nm:
                with bot_lock:
                    if valid_game(cid, gid):
                        games[cid]["lobby_mid"] = nm.message_id
                        games[cid]["lobby_mt"] = "media" if nm.content_type in ['photo', 'animation'] else "text"
            continue

        with bot_lock:
            if not valid_game(cid, gid) or games[cid]["phase"] != "joining": return
            txt = build_lobby(cid)
            gt = games[cid]["type"]
            mk = join_markup(games[cid]["game_id"], gt)
            mid = games[cid].get("lobby_mid")
            mt = games[cid].get("lobby_mt", "text")
        if mid:
            if mt == "media": safe_edit_caption(cid, mid, txt, reply_markup=mk)
            else: safe_edit_text(cid, mid, txt, reply_markup=mk)
        if rem <= 0: return

# ══════════════ الانضمام ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("join_"))
def cb_join(call):
    cid, uid = call.message.chat.id, call.from_user.id
    try: gid = int(call.data.split("_")[1])
    except: return
    
    with bot_lock:
        if not valid_game(cid, gid):
            return bot.answer_callback_query(call.id, "⛔ انتهت", show_alert=True)
        if games[cid]["phase"] != "joining":
            return bot.answer_callback_query(call.id, "⛔ بدأت", show_alert=True)
        if uid in games[cid]["players"]:
            return bot.answer_callback_query(call.id, "✅ مسجل", show_alert=True)
        if len(games[cid]["players"]) >= MAX_PLAYERS:
            return bot.answer_callback_query(call.id, "⛔ ممتلئ", show_alert=True)
        ex = find_game_for_user(uid)
        if ex and ex != cid:
            return bot.answer_callback_query(call.id, "⛔ أنت في لعبة أخرى", show_alert=True)
            
        games[cid]["players"][uid] = {
            "name": clean_name(call.from_user.first_name),
            "role": "Patient", "alive": True
        }
        user_to_game[uid] = cid
        games[cid]["last_activity"] = time.time()
        cnt = len(games[cid]["players"])
        gt = games[cid]["type"]
        
    bot.answer_callback_query(call.id, f"✅ تم ({cnt})")
    
    with bot_lock:
        if not valid_game(cid, gid): return
        txt = build_lobby(cid)
        mk = join_markup(games[cid]["game_id"], gt)
        mid = games[cid].get("lobby_mid")
        mt = games[cid].get("lobby_mt", "text")
    if mid:
        if mt == "media": safe_edit_caption(cid, mid, txt, reply_markup=mk)
        else: safe_edit_text(cid, mid, txt, reply_markup=mk)

# ══════════════ فلتر الرسائل ══════════════
@bot.message_handler(content_types=['text', 'photo', 'sticker', 'video', 'voice', 'document', 'animation'],
                     func=lambda m: m.chat.type in ("group", "supergroup") and m.chat.id in games and not (m.text or "").startswith("/"))
def group_msg_filter(m):
    cid, uid = m.chat.id, m.from_user.id
    text = m.text or ""
    do_delete = False
    do_blackout = False
    blackout_text = ""

    with bot_lock:
        if cid not in games: return
        g = games[cid]
        phase = g["phase"]

        if phase == "bomb":
            if not is_participant(cid, uid) or not g["players"].get(uid, {}).get("alive", False):
                do_delete = True
            elif text:
                if normalize_arabic(text) == g["bomb"]["a"]:
                    g["phase"] = "defused"
                    g["bomb"]["defuser"] = uid
                else: do_delete = True
            else: do_delete = True
            if do_delete: delete_msg(cid, m.message_id)
            return

        if phase == "defense":
            dt = g.get("defense_target")
            if uid == dt and g["players"].get(uid, {}).get("alive", False):
                g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                return
            else: do_delete = True

        if not do_delete and is_participant(cid, uid):
            p = g["players"].get(uid)
            if p and not p["alive"]: do_delete = True

        if not do_delete and phase in SILENT_PHASES:
            if is_participant(cid, uid): do_delete = True

        if not do_delete and phase == "discussion":
            if is_participant(cid, uid) and g["players"][uid]["alive"]:
                if text:
                    g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                    g["round_msg_count"][uid] = g["round_msg_count"].get(uid, 0) + 1
                if g.get("blackout_active", False):
                    do_blackout = True
                    blackout_text = text or "..."

    if do_delete: delete_msg(cid, m.message_id)
    elif do_blackout:
        delete_msg(cid, m.message_id)
        safe_send(cid, f"🔇 <i>همس:</i> {clean(blackout_text, 50)}")

@bot.message_handler(content_types=['left_chat_member'], func=lambda m: m.chat.type in ("group", "supergroup"))
def on_member_leave(m):
    if not m.left_chat_member: return
    uid = m.left_chat_member.id
    cid = m.chat.id
    with bot_lock:
        if cid not in games or uid not in games[cid]["players"]: return
        g = games[cid]
        if not g["players"][uid]["alive"]: return
        kill_player(g, uid)
        pn = pname(uid, g["players"][uid]["name"])
        rd = ROLE_DISPLAY.get(g["players"][uid]["role"], "?")
        user_to_game.pop(uid, None)
        gid = g["game_id"]
    safe_send(cid, f"🚪 {pn} غادر... وكان: {rd}")
    check_win_safe(cid, gid)

# ══════════════ أوامر المجموعة ══════════════
@bot.message_handler(func=lambda m: m.chat.type in ("group", "supergroup") and m.text and m.text.startswith("/"))
def group_cmd(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split()[0].split("@")[0].lower()

    deletable = {"/hospital", "/vote", "/force_start", "/cancel", "/done", "/time", "/suspect", "/commands", "/hall", "/rooms_cancel", "/لاسلكي", "/كشف_الكاميرات", "/shop", "/buy", "/profile"}
    if raw in deletable: delete_msg(cid, m.message_id)

    if raw == "/hospital": init_game(m, "hospital")
    elif raw == "/vote": init_game(m, "vote")
    elif raw == "/time": do_time(m)
    elif raw == "/force_start": do_force(m)
    elif raw in ("/cancel", "/done"): do_cancel(m)
    elif raw == "/suspect": do_suspect(m)
    elif raw == "/commands": do_commands(m)
    elif raw == "/hall": do_hall(m)
    elif raw == "/rooms_cancel": do_rooms_cancel(m)
    elif raw == "/shop": do_shop(m)
    elif raw == "/profile": do_profile(m)
    elif raw == "/buy": do_buy(m)

# ══════════════ دالة بدء اللعبة ══════════════
def init_game(msg, gtype):
    cid = msg.chat.id
    uid = msg.from_user.id
    if msg.chat.type not in ("group", "supergroup"): return

    with bot_lock:
        if cid in games:
            g = games[cid]
            is_stuck = False
            if g["phase"] == "joining" and (time.time() - g["last_activity"] > 300):
                is_stuck = True
            
            if is_stuck:
                uids = list(g["players"].keys())
                for u in uids: user_to_game.pop(u, None)
                del games[cid]
            else:
                return safe_send(cid, "⚠️ <i>اللعبة جارية!</i>")

        if find_game_for_user(uid):
            return safe_send(cid, "⚠️ <i>أنت في لعبة أخرى.</i>")

        gid = int(time.time() * 1000) % 2147483647
        games[cid] = new_game_data(gtype, uid, gid)

    txt = build_lobby(cid)
    mk = join_markup(gid, gtype)
    
    m2 = None
    try:
        if gtype == "hospital":
            m2 = bot.send_animation(cid, ASSETS["LOBBY"], caption=txt, parse_mode="HTML", reply_markup=mk)
        else:
            m2 = bot.send_photo(cid, ASSETS["VOTE"], caption=txt, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"Lobby Media Failed: {e}")
        m2 = safe_send(cid, txt, reply_markup=mk)
    
    if m2:
        with bot_lock:
            if cid in games:
                games[cid]["lobby_mid"] = m2.message_id
                games[cid]["lobby_mt"] = "media" if m2.content_type in ['photo', 'animation'] else "text"
    
    threading.Thread(target=lobby_tick, args=(cid, gid), daemon=True).start()

def do_time(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining": return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        try:
            s = int(m.text.split()[1]) if len(m.text.split()) > 1 else 30
            s = min(max(s, 10), 120)
            games[cid]["start_at"] += s
            r = int(games[cid]["start_at"] - time.time())
            games[cid]["total_wait"] = max(r, 1)
            games[cid]["last_activity"] = time.time()
        except: return

def do_force(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining": return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        games[cid]["start_at"] = time.time()

def do_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games: return
        is_auth = (games[cid]["host"] == uid)
    if not is_auth:
        try: is_auth = bot.get_chat_member(cid, uid).status in ['administrator', 'creator']
        except: pass
    if not is_auth: return
    safe_send(cid, "🛑 <b>تم إلغاء اللعبة.</b>")
    force_cleanup(cid)

def do_rooms_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining": return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        current = games[cid].get("rooms_enabled", True)
        games[cid]["rooms_enabled"] = not current
        new_state = games[cid]["rooms_enabled"]
    if new_state: safe_send(cid, "🏠 <i>الغرف: مفعّلة</i>")
    else: safe_send(cid, "🏠 <i>الغرف: معطّلة</i>")

# ══════════════ الشك ══════════════
def do_suspect(m):
    cid, uid = m.chat.id, m.from_user.id
    delete_msg(cid, m.message_id)
    
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "discussion": return
        if uid not in games[cid]["players"] or not games[cid]["players"][uid]["alive"]: return

    target_uid = None
    if m.entities:
        for ent in m.entities:
            if ent.type == "mention":
                mentioned = m.text[ent.offset + 1:ent.offset + ent.length]
                with bot_lock:
                    for u, p in games[cid]["players"].items():
                        try:
                            member = bot.get_chat_member(cid, u)
                            if member.user.username and member.user.username.lower() == mentioned.lower():
                                target_uid = u
                                break
                        except: continue
            elif ent.type == "text_mention": target_uid = ent.user.id

    if not target_uid: return

    with bot_lock:
        if cid not in games or games[cid]["phase"] != "discussion": return
        if target_uid not in games[cid]["players"] or not games[cid]["players"][target_uid]["alive"]: return
        if target_uid == uid: return
        sv = games[cid].setdefault("suspect_votes", {})
        sv.setdefault(target_uid, set()).add(uid)

def show_suspect_bar(cid):
    with bot_lock:
        if cid not in games: return
        sv = games[cid].get("suspect_votes", {})
        if not sv: return
        pp = games[cid]["players"]
        lines = []
        sorted_sus = sorted(sv.items(), key=lambda x: len(x[1]), reverse=True)
        for t_uid, voters in sorted_sus[:5]:
            if t_uid not in pp: continue
            count = len(voters)
            bar = "🟥" * min(count, 5) + "⬜" * max(0, 5 - count)
            lines.append(f"  {pp[t_uid]['name']}: {bar} ({count})")
    if lines: safe_send(cid, "📊 <b>مقياس الشك:</b>\n" + "\n".join(lines))

def do_commands(m):
    cid = m.chat.id
    cmd_text = (
        "📖 <b>أوامر المستشفى</b>\n\n"
        "<code>/hospital</code> - بدء المستشفى\n"
        "<code>/vote</code> - بدء مجلس التصويت\n"
        "<code>/force_start</code> - بدء فوري\n"
        "<code>/time</code> - تمديد الوقت\n"
        "<code>/cancel</code> - إلغاء اللعبة\n"
        "<code>/suspect</code> - توجيه اتهام\n"
        "<code>/myrole</code> - معرفة هويتك\n"
        "<code>/alive</code> - قائمة الأحياء\n"
        "<code>/shop</code> - المتجر\n"
    )
    safe_send(cid, cmd_text)

def do_hall(m):
    cid = m.chat.id
    lines = []
    def top_entry(cat, emoji, label):
        data = hall_of_fame.get(cat, {})
        if not data: return f"{emoji} {label}: <i>-</i>"
        top_uid = max(data, key=data.get)
        try:
            user = bot.get_chat_member(cid, top_uid).user
            name = clean_name(user.first_name)
        except: name = str(top_uid)
        return f"{emoji} {label}: <b>{name}</b> ({data[top_uid]})"

    lines.append(top_entry("wins", "👑", "انتصارات"))
    lines.append(top_entry("surgeon_kills", "🔪", "جرّاح"))
    lines.append(top_entry("doc_saves", "🩺", "طبيب"))
    lines.append(top_entry("bombs", "🤡", "مفجر"))
    lines.append(top_entry("deaths", "💀", "ضحايا"))
    safe_send(cid, "🏆 <b>لوحة الشرف</b>\n\n" + "\n".join(lines))

def do_shop(m):
    cid = m.chat.id
    text = "🛒 <b>المتجر</b>\nاستخدم <code>/buy كود</code> للشراء.\n\n"
    for k, v in SHOP_ITEMS.items():
        text += f"🔹 <b>{v['name']}</b> ({v['price']} 💰)\n   {v['desc']}\n   كود: <code>{k}</code>\n\n"
    safe_send(cid, text)

def do_buy(m):
    cid, uid = m.chat.id, m.from_user.id
    try: item_id = m.text.split()[1]
    except: return safe_send(cid, "⚠️ الاستخدام: <code>/buy كود_الغرض</code>")
    success, msg = buy_item(uid, item_id)
    safe_send(cid, msg)

def do_profile(m):
    cid, uid = m.chat.id, m.from_user.id
    p = get_profile(uid)
    w = get_wallet(uid)
    
    txt = (
        f"👤 <b>ملف اللاعب:</b> {clean_name(m.from_user.first_name)}\n\n"
        f"💰 <b>العملات:</b> {w['coins']}\n"
        f"🎮 <b>الألعاب:</b> {p['games']}\n"
        f"🏆 <b>الفوز:</b> {p['wins']}\n"
        f"💀 <b>الخسارة:</b> {p['losses']}\n"
        f"🔪 <b>القتلى (جرّاح):</b> {p['kills_as_surgeon']}\n"
        f"🩺 <b>الإنقاذ (طبيب):</b> {p['saves_as_doc']}\n\n"
        f"🎒 <b>المخزون:</b> {', '.join(w['inventory']) if w['inventory'] else 'فارغ'}"
    )
    safe_send(cid, txt)

# ══════════════ الغرف ══════════════
def start_room_choosing(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        rooms_on = g.get("rooms_enabled", True)

    if not rooms_on:
        with bot_lock:
            if not valid_game(cid, gid): return
            g = games[cid]
            g["room_choices"] = {}
            for uid, p in g["players"].items():
                if p["alive"]: g["room_choices"][uid] = 1
        start_night(cid, gid)
        return

    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        g["phase"] = "room_choosing"
        g["room_choices"] = {}
        g["room_chat_notified"] = set()
        g["last_activity"] = time.time()

    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🏠 اختر موقعك", url=f"https://t.me/{BOT_USERNAME}?start=room_{cid}"))
    safe_send(cid, f"🏠 <b>حان وقت المبيت...</b>\nاختر الغرفة أو ابق في الممر.\n<i>معكم {ROOM_CHOOSE_TIME} ثانية</i>", reply_markup=mk)

    if not safe_sleep(cid, gid, ROOM_CHOOSE_TIME): return

    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        for uid, p in g["players"].items():
            if p["alive"] and uid not in g["room_choices"]:
                g["room_choices"][uid] = random.randint(1, 5)

    show_room_map(cid, gid)
    notify_room_mates(cid, gid)
    if not safe_sleep(cid, gid, 2): return
    start_night(cid, gid)

def dispatch_room(uid, param):
    try: cid = int(param.replace("room_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 اللعبة انتهت.")
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]: return safe_pm(uid, "🚫 لست مشاركاً.")
        if g["phase"] != "room_choosing": return safe_pm(uid, "⏰ انتهى الوقت.")
        if uid in g["room_choices"]: return safe_pm(uid, f"✅ اخترت موقعك.")

    mk = types.InlineKeyboardMarkup(row_width=2)
    for rid, rname in ROOM_NAMES.items():
        mk.add(types.InlineKeyboardButton(rname, callback_data=f"pickroom_{cid}_{rid}"))
    safe_pm(uid, "🏠 <b>أين ستختبئ الليلة؟</b>\n\n📌 <i>الغرف:</i> آمنة، تتحدث فقط مع من معك.\n📌 <i>الممر:</i> خطر، تستهدف الجميع ويراك الجميع.", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pickroom_"))
def cb_pickroom(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, rid = int(parts[1]), int(parts[2])
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g["phase"] != "room_choosing": return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g["room_choices"]: return bot.answer_callback_query(call.id, "✅", show_alert=True)
        g["room_choices"][uid] = rid
    bot.answer_callback_query(call.id, f"✅ {ROOM_NAMES[rid]}")
    try: bot.edit_message_text(f"✅ تم اختيار: <b>{ROOM_NAMES[rid]}</b>", uid, call.message.message_id, parse_mode="HTML")
    except: pass

def show_room_map(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        lines = []
        for rid, rname in ROOM_NAMES.items():
            players_in = get_room_players(g, rid)
            if players_in:
                names = ", ".join([p["name"] for p in players_in.values()])
                lines.append(f"{rname}: {names}")
            else: lines.append(f"{rname}: <i>-</i>")
        g["stats"]["rooms_history"].append(dict(g["room_choices"]))
    safe_send(cid, f"🗺 <b>توزيع الأماكن</b>\n" + "\n".join(lines))

def notify_room_mates(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        for rid in ROOM_NAMES:
            players_in = get_room_players(g, rid)
            for uid in players_in:
                others = [pname(u, p["name"]) for u, p in players_in.items() if u != uid]
                txt = f"🏠 <b>{ROOM_NAMES[rid]}</b>\nمعك:\n" + "\n".join(others) if others else f"🏠 <b>{ROOM_NAMES[rid]}</b>\nأنت وحيد..."
                safe_pm(uid, txt)

# ══════════════ الليل ══════════════
def start_night(cid, expected_gid):
    auto_send = []
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        g["phase"] = "night"
        g["actions"] = {}
        g["round"] += 1
        g["screamer_visitors"] = {}
        g["swap_data"] = {}
        g["nurse_poison"] = {}
        g["instigator_steal"] = {}
        g["observer_targets"] = {}
        g["sedated_current"] = set()
        g["night_acted"] = set()
        g["will_pending"] = {}
        g["last_gasp_pending"] = {}
        g["last_gasp_text"] = {}
        g["round_msg_count"] = {}
        g["suspect_votes"] = {}
        g["security_checked_cam"] = set()
        g["last_activity"] = time.time()
        rnd = g["round"]
        gid = g["game_id"]
        for uid, p in g["players"].items():
            if not p["alive"]: continue
            if p["role"] in INSTANT_ROLES: auto_send.append((uid, p["role"]))

    silence_all(cid)
    with bot_lock:
        if valid_game(cid, gid):
            for mid in list(games[cid].get("pinned_mids", [])): safe_unpin(cid, mid)
            games[cid]["pinned_mids"] = []

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🌑 ابدأ المهمة", url=f"https://t.me/{BOT_USERNAME}?start=night_{cid}"))
    try:
        try:
            bot.send_photo(cid, ASSETS["NIGHT"], caption=f"🌑 <b>الليلة {rnd}</b>\n<i>معكم {NIGHT_TIME} ثانية</i>", parse_mode="HTML", reply_markup=mk)
        except:
            safe_send(cid, f"🌑 <b>الليلة {rnd}</b>\n<i>معكم {NIGHT_TIME} ثانية</i>", reply_markup=mk)
    except: pass

    for uid, role in auto_send: send_night_action(cid, uid, role)
    if not safe_sleep(cid, gid, NIGHT_TIME): return
    with bot_lock:
        if not valid_game(cid, gid): return
        if games[cid]["round"] != rnd or games[cid]["phase"] != "night": return
    resolve_night(cid, rnd, gid)

def dispatch_night(uid, param):
    try: cid = int(param.replace("night_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 انتهت اللعبة.")
        g = games[cid]
        if uid not in g["players"]: return safe_pm(uid, "🚫 لست مشاركاً.")
        if not g["players"][uid]["alive"]: return safe_pm(uid, "💀 أنت ميت.")
        if g["phase"] != "night": return safe_pm(uid, "☀️ انتظر الليل.")
        if uid in g.get("night_acted", set()): return safe_pm(uid, "✅ قمت بمهمتك.")
        if uid in g["sedated_current"]: return safe_pm(uid, "💉 أنت مخدّر.")
        role = g["players"][uid]["role"]
        
        if role == "Psychopath": return safe_pm(uid, "🤡 انتظر دورك عند الحرق.")
        if role == "Screamer": return safe_pm(uid, "😱 راقب بصمت.")
        
        if role not in INSTANT_ROLES:
            an = g["ability_night"].get(uid, 999)
            if g["round"] < an: return safe_pm(uid, f"🔒 قدرتك مقفلة حتى الليلة {an}")
            if role == "Anesthetist" and g["anesthetist_uses"].get(uid, 0) <= 0: return safe_pm(uid, "💉 نفدت الإبر.")
            if role == "Nurse" and not g["nurse_has_poison"].get(uid, True): return safe_pm(uid, "💊 الحقنة فارغة.")
            if role == "Patient":
                if uid in g.get("patient_used", set()): return safe_pm(uid, "🚫 استخدمتها سابقاً.")
                dead = [u for u, p in g["players"].items() if not p["alive"] and u != uid]
                if not dead: return safe_pm(uid, "🚫 لا توجد جثث.")

    send_night_action(cid, uid, role)

def send_night_action(cid, uid, role):
    def room_btns(prefix, exclude_teams=None):
        with bot_lock:
            if cid not in games: return None
            g = games[cid]
            tgts = get_room_targets(g, uid)
            if exclude_teams:
                tgts = {u: p for u, p in tgts.items() if get_original_team(g, u) not in exclude_teams}
        if not tgts: return None
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(*[types.InlineKeyboardButton(p["name"], callback_data=f"act_{cid}_{t}_{prefix}") for t, p in tgts.items()])
        return m

    prompts = {
        "Surgeon": "🔪 <b>اختر الهدف...</b>",
        "Doctor": "🩺 <b>من يستحق النجاة؟</b>",
        "Anesthetist": "💉 <b>إيقاف الهدف...</b>",
        "Observer": "👁 <b>كشف الحقيقة...</b>",
        "Instigator": "🧠 <b>سرقة الصوت...</b>",
        "Swapper": "🛏 <b>تبديل المواقع (1)...</b>",
        "Nurse": "💊 <b>الحقنة القاتلة...</b>",
        "Security": "👮 <b>تحييد الخطر (رصاصة واحدة)...</b>",
    }

    if role == "Security":
        with bot_lock:
            if cid not in games: return
            ammo = games[cid]["security_ammo"].get(uid, 0)
        if ammo <= 0: return safe_pm(uid, "🚫 نفدت ذخيرتك.")
        
        mk = room_btns("security")
        if not mk: return safe_pm(uid, "🚫 لا أهداف.")
        safe_pm(uid, f"👮 <b>لديك رصاصة واحدة. لا تتردد.</b>\n<i>يمكنك أيضاً استخدام /كشف_الكاميرات</i>", reply_markup=mk)
        return

    if role == "Patient":
        with bot_lock:
            if cid not in games: return
            dead = [(u, p) for u, p in games[cid]["players"].items() if not p["alive"] and u != uid and p["role"] != "Patient"]
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(f"💀 {p['name']} ({ROLE_DISPLAY.get(p['role'], '?')})", callback_data=f"act_{cid}_{u}_patient") for u, p in dead])
        safe_pm(uid, "🤕 <b>تقمص دوراً جديداً:</b>", reply_markup=mk)
        return

    if role == "Swapper":
        with bot_lock:
            if cid not in games: return
            tgts = get_alive_except(cid, uid)
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(p["name"], callback_data=f"act_{cid}_{t}_swapper") for t, p in tgts.items()])
        safe_pm(uid, prompts["Swapper"], reply_markup=mk)
        return

    mk = None
    if role in prompts:
        key = ROLE_ACTION_MAP.get(role, role.lower())
        ex = {"evil"} if role in ("Surgeon", "Anesthetist") else None
        mk = room_btns(key, exclude_teams=ex)
        
    if not mk: safe_pm(uid, "🚫 لا يوجد أهداف في نطاقك.")
    else: safe_pm(uid, prompts[role], reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_"))
def cb_act(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, tid, act = int(parts[1]), int(parts[2]), parts[3]
    except: return

    send_swapper2 = False
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "night": return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        g = games[cid]
        pp = g["players"]
        if uid not in pp or not pp[uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g.get("night_acted", set()) and act != "swapper2": return bot.answer_callback_query(call.id, "✅", show_alert=True)

        role_emoji_map = {
            "surgeon": "🔪 حركة سريعة في الظلام...",
            "doctor": "🩺 خطوات هادئة...",
            "anesthetist": "💉 يتم تحضير الإبرة...",
            "nurse": "💊 رائحة الدواء تفوح...",
        }
        if act in role_emoji_map:
            safe_send(cid, f"<i>{role_emoji_map[act]}</i>")

        if act == "surgeon":
            g["actions"]["surgeon"] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "doctor":
            g["actions"]["doctor"] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "anesthetist":
            g["sedated_current"].add(tid)
            g["anesthetist_uses"][uid] = g["anesthetist_uses"].get(uid, 0) - 1
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "instigator": g["instigator_steal"][uid] = tid
        elif act == "observer":
            g["observer_targets"][uid] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "swapper":
            g["swap_data"][uid] = {"first": tid}
            send_swapper2 = True
        elif act == "swapper2":
            g["swap_data"][uid]["second"] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["screamer_visitors"].setdefault(g["swap_data"][uid]["first"], []).append(uid)
        elif act == "nurse":
            g["nurse_poison"][uid] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "security":
            g["actions"]["security"] = tid
            g["security_ammo"][uid] = 0
            g["screamer_visitors"].setdefault(tid, []).append(uid)
        elif act == "patient":
            dr = pp[tid]["role"]
            g["original_team"][uid] = get_original_team(g, uid)
            pp[uid]["role"] = dr
            g["patient_used"].add(uid)
            g["ability_night"][uid] = g["round"] + 1
            if dr == "Nurse": g["nurse_has_poison"][uid] = True
            if dr == "Anesthetist": g["anesthetist_uses"][uid] = 2; g["original_team"][uid] = "evil"; g["evil_chat_ids"].add(uid); g["radio_holders"].add(uid)
            if dr == "Surgeon": g["stats"]["surgeon_uid"] = uid; g["evil_chat_ids"].add(uid); g["original_team"][uid] = "evil"; g["radio_holders"].add(uid)
            if dr == "Security": g["security_ammo"][uid] = 1

        if act != "swapper":
            g["night_acted"].add(uid)

    if send_swapper2:
        with bot_lock: tgts = get_alive_except(cid, uid)
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(p["name"], callback_data=f"act_{cid}_{u}_swapper2") for u, p in tgts.items() if u != tid])
        try: bot.edit_message_text("🛏 <b>تبديل المواقع (2)...</b>", uid, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except: pass
        return

    bot.answer_callback_query(call.id, "✅")
    try: bot.edit_message_text("✅ <b>تم استلام الأمر.</b>", uid, call.message.message_id, parse_mode="HTML")
    except: pass

# ══════════════ الجوكر ══════════════
def assign_joker(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        alive = [u for u, p in g["players"].items() if p["alive"]]
        if not alive: return
        holder = random.choice(alive)
        g["joker_holder"] = holder
        g["joker_used"] = False
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🃏 بطاقة الجوكر", url=f"https://t.me/{BOT_USERNAME}?start=joker_{cid}"))
    safe_pm(holder, "🃏 <b>عثرت على بطاقة الجوكر!</b>\nاستخدمها بحكمة لمرة واحدة.", reply_markup=mk)

def dispatch_joker(uid, param):
    try: cid = int(param.replace("joker_", ""))
    except: return
    with bot_lock:
        if cid not in games: return
        g = games[cid]
        if g.get("joker_holder") != uid or g.get("joker_used"): return safe_pm(uid, "🚫 البطاقة مستخدمة أو ليست لك.")
    
    mk = types.InlineKeyboardMarkup(row_width=1)
    for k, v in JOKER_OPTIONS.items():
        mk.add(types.InlineKeyboardButton(v["name"], callback_data=f"jkuse_{cid}_{k}"))
    safe_pm(uid, "🃏 <b>قدرة الجوكر:</b>\n⚠️ الاستخدام سيكشف هويتك.", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("jkuse_"))
def cb_joker_use(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, jk = int(parts[1]), parts[2]
    except: return
    with bot_lock:
        if cid not in games: return
        g = games[cid]
        if g.get("joker_holder") != uid or g.get("joker_used"): return
        g["joker_used"] = True
        g["joker_effect"] = jk
        pn = g["players"][uid]["name"]
        pr = ROLE_DISPLAY.get(g["players"][uid]["role"], "?")
    
    bot.answer_callback_query(call.id, "🃏")
    safe_send(cid, f"🃏 <b>الجوكر!</b>\n{pname(uid, pn)} استخدم <b>{JOKER_OPTIONS[jk]['name']}</b>\nهويته: {pr}")

    if jk == "cancel_vote" and g["phase"] == "voting":
        g["votes"] = {}
        safe_send(cid, "🔄 تم تصفير الأصوات!")
    elif jk == "skip_night" and g["phase"] == "night":
        g["actions"] = {}
        g["night_acted"] = set(g["players"].keys())
        safe_send(cid, "⏭ تم تخطي الليلة!")

# ══════════════ معالجة الليل ══════════════
def resolve_night(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        if g["round"] != expected_rnd or g["phase"] != "night": return
        g["phase"] = "morning"
        pp = g["players"]
        actions = g["actions"]
        sedated = g["sedated_current"]
        
        swaps = {}
        for uid, d in g["swap_data"].items():
            if uid not in sedated and "second" in d:
                a, b = d["first"], d["second"]
                if pp.get(a, {}).get("alive") and pp.get(b, {}).get("alive"):
                    swaps[a] = b; swaps[b] = a
        def sw(t): return swaps.get(t, t) if t else t

        s_uid = g["stats"].get("surgeon_uid")
        s_tgt = None
        if s_uid and pp[s_uid]["alive"] and s_uid not in sedated:
            raw_tgt = actions.get("surgeon")
            if raw_tgt: s_tgt = sw(raw_tgt)

        sec_tgt = None
        sec_uid = next((u for u, p in pp.items() if p["role"]=="Security" and p["alive"]), None)
        if sec_uid and sec_uid not in sedated:
            raw_sec = actions.get("security")
            if raw_sec: sec_tgt = sw(raw_sec)

        d_uid = next((u for u, p in pp.items() if p["role"]=="Doctor" and p["alive"]), None)
        d_tgt = None
        d_failed = False
        if d_uid and d_uid not in sedated:
            raw_d = actions.get("doctor")
            if raw_d:
                d_tgt = sw(raw_d)
                if random.random() < DOCTOR_FAIL_CHANCE: d_failed = True

        victim = None
        saved = False
        
        if s_tgt and s_tgt in pp and pp[s_tgt]["alive"]:
            if d_tgt == s_tgt and not d_failed: saved = True
            else: victim = s_tgt

        sec_victim = None
        sec_died_guilt = False
        if sec_tgt and sec_tgt in pp and pp[sec_tgt]["alive"]:
            if sec_tgt != victim:
                if d_tgt == sec_tgt and not d_failed: saved = True
                else:
                    sec_victim = sec_tgt
                    if get_original_team(g, sec_victim) == "good":
                        sec_died_guilt = True

        nurse_kills = []
        for n, t in g["nurse_poison"].items():
            if n not in sedated and pp[n]["alive"]:
                t_real = sw(t)
                if t_real in pp and pp[t_real]["alive"]:
                    nk_innocent = False
                    if get_original_team(g, t_real) not in ("evil", "psycho"):
                        nk_innocent = True
                    nurse_kills.append({"victim": t_real, "killer": n, "suicide": nk_innocent})

    try: bot.send_photo(cid, ASSETS["DAY"], caption="🌅 <b>الفجر...</b>", parse_mode="HTML")
    except: safe_send(cid, "🌅 <b>طلع الفجر...</b>")
    
    if not safe_sleep(cid, expected_gid, 2): return

    if d_failed and d_tgt:
        with bot_lock: kill_player(g, d_tgt)
        safe_send(cid, f"💉💀 <b>{pname(d_tgt, pp[d_tgt]['name'])}</b> مات بخطأ طبي!")
        with bot_lock: transfer_radio(g, d_tgt)
    
    if saved:
        safe_send(cid, "✨ <b>أحدهم نجا من الموت بأعجوبة.</b>")
    
    if victim:
        with bot_lock: kill_player(g, victim)
        safe_send(cid, f"🔪💀 <b>{pname(victim, pp[victim]['name'])}</b> وُجد مقتولاً.\n🎭 {ROLE_DISPLAY.get(pp[victim]['role'], '?')}")
        with bot_lock: transfer_radio(g, victim, s_uid)
        with bot_lock: g["last_gasp_pending"][victim] = True
        safe_pm(victim, "🩸 لديك 15 ثانية لكتابة كلمات أخيرة.")
        safe_sleep(cid, expected_gid, LAST_GASP_TIME)
        with bot_lock: txt = g["last_gasp_text"].get(victim)
        if txt: safe_send(cid, f"🩸 <i>كلمات أخيرة:</i> {txt}")

    if sec_victim:
        with bot_lock: kill_player(g, sec_victim)
        safe_send(cid, f"🔫💀 <b>{pname(sec_victim, pp[sec_victim]['name'])}</b> قُتل برصاص حارس الأمن.\n🎭 ||{ROLE_DISPLAY.get(pp[sec_victim]['role'], '?')}||")
        with bot_lock: transfer_radio(g, sec_victim, sec_uid)
        
        if sec_died_guilt:
            safe_sleep(cid, expected_gid, 2)
            with bot_lock: kill_player(g, sec_uid)
            safe_send(cid, f"🔥💀 <b>{pname(sec_uid, pp[sec_uid]['name'])}</b> (الحارس) ألقى نفسه في المحرقة ندماً.\n🎭 ||{ROLE_DISPLAY.get(pp[sec_uid]['role'], '?')}||")
            with bot_lock: transfer_radio(g, sec_uid)

    for nk in nurse_kills:
        vic = nk["victim"]
        nur = nk["killer"]
        if pp[vic]["alive"]:
            with bot_lock: kill_player(g, vic)
            safe_send(cid, f"💊💀 <b>{pname(vic, pp[vic]['name'])}</b> مات مسموماً.\n🎭 ||{ROLE_DISPLAY.get(pp[vic]['role'], '?')}||")
            with bot_lock: transfer_radio(g, vic, nur)
            
            if nk["suicide"] and pp[nur]["alive"]:
                safe_sleep(cid, expected_gid, 2)
                with bot_lock: kill_player(g, nur)
                safe_send(cid, f"🧪💀 <b>{pname(nur, pp[nur]['name'])}</b> (الممرض) شرب السم ندماً.\n🎭 ||{ROLE_DISPLAY.get(pp[nur]['role'], '?')}||")
                with bot_lock: transfer_radio(g, nur)

    if check_win_safe(cid, expected_gid): return
    
    for u, t in g["observer_targets"].items():
        if u not in sedated and pp.get(u, {}).get("alive"):
            t_real = sw(t)
            if t_real in pp:
                role_name = ROLE_DISPLAY.get(pp[t_real]['role'], '?')
                safe_pm(u, f"👁 {pp[t_real]['name']} هو {role_name}")
                with bot_lock: g["observer_last_reveal"] = role_name
            
    for u, vs in g["screamer_visitors"].items():
        u_real = sw(u)
        if u_real in pp and pp[u_real]["role"] == "Screamer" and pp[u_real]["alive"] and u_real not in sedated:
            for v in vs: safe_pm(u_real, f"😱 شعرت بوجود {pp[v]['name']}")

    if check_win_safe(cid, expected_gid): return
    
    _try_promote_anesthetist(cid, expected_gid)
    start_discussion(cid, expected_gid)

def _try_promote_anesthetist(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        surg_alive = any(p["role"] == "Surgeon" and p["alive"] for p in g["players"].values())
        if not surg_alive:
            for u, p in g["players"].items():
                if p["role"] == "Anesthetist" and p["alive"]:
                    p["role"] = "Surgeon"
                    g["stats"]["surgeon_uid"] = u
                    safe_pm(u, "🔪 <b>لقد أصبحت الجرّاح الجديد!</b>")
                    break

# ══════════════ النقاش والتصويت ══════════════
def start_discussion(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games[cid]["phase"] = "discussion"
        alive = len(get_alive(cid))
    
    open_discussion(cid)
    safe_send(cid, f"💬 <b>النقاش ({DISCUSS_TIME}ث)</b>\n👥 {alive} أحياء\nاستخدم /suspect للشك.")
    
    if not safe_sleep(cid, gid, DISCUSS_TIME): return
    show_suspect_bar(cid)
    if not safe_sleep(cid, gid, 2): return
    start_voting(cid, gid)

def start_voting(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games[cid]["phase"] = "voting"
        games[cid]["votes"] = {}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    # تم تعديل نص الزر
    mk.add(types.InlineKeyboardButton("⚖️ الحكم", url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))
    msg = safe_send(cid, f"⚖️ <b>وقت إصدار الحكم ({VOTE_TIME}ث)</b>", reply_markup=mk)
    if msg:
        safe_pin(cid, msg.message_id)
        with bot_lock: games[cid]["pinned_mids"].append(msg.message_id)
    
    if not safe_sleep(cid, gid, VOTE_TIME): return
    tally_trial(cid, gid)

def tally_trial(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        votes = g["votes"]
        valid_votes = {k: v for k, v in votes.items() if isinstance(k, int) and k in g["players"] and g["players"][k]["alive"]}
        
    safe_unpin_all(cid)
    if not valid_votes:
        safe_send(cid, "🤷 <b>تعادل سلبي (لا أصوات).</b>")
        return start_room_choosing(cid, gid)

    counts = {}
    for t in valid_votes.values(): counts[t] = counts.get(t, 0) + 1
    top_v = max(counts.values())
    candidates = [k for k, v in counts.items() if v == top_v]

    txt = "📩 <b>النتائج:</b>\n"
    for v, t in valid_votes.items():
        vn = g["players"][v]["name"]
        tn = g["players"][t]["name"]
        txt += f"🔸 {vn} ➔ {tn}\n"
    safe_send(cid, txt)
    
    if len(candidates) == 1:
        start_defense(cid, gid, candidates[0])
    else:
        safe_send(cid, "🤝 <b>تعادل في الأصوات! لا أحد يموت.</b>")
        start_room_choosing(cid, gid)

def start_defense(cid, gid, sus):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        g["phase"] = "defense"
        g["defense_target"] = sus
    
    unmute_player(cid, sus)
    safe_send(cid, f"🎤 <b>{g['players'][sus]['name']}</b>، دافع عن نفسك ({DEFENSE_TIME}ث).")
    if not safe_sleep(cid, gid, DEFENSE_TIME): return
    
    with bot_lock:
        g = games[cid]
        g["phase"] = "confirming"
        g["confirm_votes"] = {"yes": set(), "no": set()}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔥 إدانة", callback_data=f"cf_{cid}_y"),
           types.InlineKeyboardButton("🕊 براءة", callback_data=f"cf_{cid}_n"))
    safe_send(cid, "⚖️ <b>حكم الجمهور:</b>", reply_markup=mk)
    
    if not safe_sleep(cid, gid, CONFIRM_TIME): return
    resolve_confirm(cid, gid)

def resolve_confirm(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        sus = g["confirm_target"] if g.get("confirm_target") else g.get("defense_target")
        if not sus: return 
        yes = len(g["confirm_votes"]["yes"])
        no = len(g["confirm_votes"]["no"])
        
    if yes > no:
        with bot_lock: kill_player(g, sus)
        pn = g["players"][sus]["name"]
        pr = ROLE_DISPLAY.get(g["players"][sus]["role"], "?")
        safe_send(cid, f"🔥 <b>{pn} تمت إدانته.</b>\n🎭 كان: {pr}")
        with bot_lock: transfer_radio(g, sus)
        
        if g["players"][sus]["role"] == "Psychopath":
            with bot_lock: bomb = g["bomb"]
            if bomb["is_set"]:
                safe_send(cid, f"🤡 <b>انفجرت قنبلة المجنون!</b>\n❓ {bomb['q']}\nلديك {BOMB_TIME} ثانية للإجابة!")
                open_discussion(cid)
                with bot_lock: g["phase"] = "bomb"
                
                t_end = time.time() + BOMB_TIME
                while time.time() < t_end:
                    time.sleep(1)
                    with bot_lock:
                        if g["phase"] == "defused": break
                
                with bot_lock: phase = g["phase"]
                if phase == "defused":
                    d_name = g["players"][g["bomb"]["defuser"]]["name"]
                    safe_send(cid, f"✅ <b>{d_name} أبطل القنبلة!</b>")
                else:
                    safe_send(cid, f"💥 <b>BOOM! الجميع مات.</b>\nالجواب: {bomb['raw']}")
                    with bot_lock: g["winners_team"] = "psycho"
                    show_results(cid, "🤡 المجنون فاز.")
                    return

        if check_win_safe(cid, gid): return
    else:
        safe_send(cid, "🕊 <b>حكم بالبراءة.</b>")
    
    start_room_choosing(cid, gid)

@bot.callback_query_handler(func=lambda c: c.data.startswith("vote_"))
def cb_vote(call):
    uid = call.from_user.id
    try: cid, tid = int(call.data.split("_")[1]), int(call.data.split("_")[2])
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "⛔", show_alert=True)
        g = games[cid]
        if g["phase"] not in ("voting", "voting_active"): return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g["votes"]: return bot.answer_callback_query(call.id, "✅", show_alert=True)
        g["votes"][uid] = tid
        if g["players"][uid]["role"] == "Instigator": g["votes"][f"i_{uid}"] = tid
        if g.get("joker_holder") == uid and g.get("joker_effect") == "double_vote": g["votes"][f"d_{uid}"] = tid
    bot.answer_callback_query(call.id, "✅ تم")

@bot.callback_query_handler(func=lambda c: c.data.startswith("cf_"))
def cb_confirm(call):
    uid = call.from_user.id
    try: cid, ch = int(call.data.split("_")[1]), call.data.split("_")[2]
    except: return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "confirming": return
        if uid not in games[cid]["players"] or not games[cid]["players"][uid]["alive"]: return
        if uid == games[cid].get("defense_target"): return bot.answer_callback_query(call.id, "لا يمكنك التصويت", show_alert=True)
        
        cv = games[cid]["confirm_votes"]
        cv["yes"].discard(uid); cv["no"].discard(uid)
        if ch == "y": cv["yes"].add(uid)
        else: cv["no"].add(uid)
        
        y, n = len(cv["yes"]), len(cv["no"])
        
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(f"🔥 إدانة ({y})", callback_data=f"cf_{cid}_y"),
           types.InlineKeyboardButton(f"🕊 براءة ({n})", callback_data=f"cf_{cid}_n"))
    try: bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=mk)
    except: pass
    bot.answer_callback_query(call.id, "✅")

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def pm_handler_special(msg):
    uid = msg.from_user.id
    text = msg.text.strip()

    with bot_lock:
        fc = find_game_for_user(uid)
        if not fc or fc not in games: return
        g = games[fc]
        
        if g["phase"] == "night" and g["players"].get(uid, {}).get("alive"):
            my_room = get_player_room(g, uid)
            if my_room:
                my_name = g["players"][uid]["name"]
                if my_room == 5:
                    hall_players = get_room_players(g, 5)
                    for u in hall_players:
                        if u != uid: safe_pm(u, f"🌑 <b>{my_name} (في الممر):</b> {clean(text, 200)}")
                    corrupted = corrupt_text(text)
                    all_in_rooms = [u for u, p in g["players"].items() if p["alive"] and g["room_choices"].get(u) != 5]
                    for u in all_in_rooms:
                        safe_pm(u, f"👻 <b>(صوت خافت في الممر):</b> {clean(corrupted, 200)}")
                else:
                    room_mates = get_room_players(g, my_room)
                    for u in room_mates:
                        if u != uid: safe_pm(u, f"🏠 <b>{my_name}:</b> {clean(text, 200)}")
                return

        if g["players"][uid]["role"] == "Psychopath" and g.get("psycho_phase", {}).get(uid) == "q":
            g["bomb"]["q"] = clean(text, 100); g["psycho_phase"][uid] = "a"
            safe_pm(uid, "✅ تم تسجيل اللغز. الآن الجواب:"); return
        if g["players"][uid]["role"] == "Psychopath" and g.get("psycho_phase", {}).get(uid) == "a":
            g["bomb"]["a"] = normalize_arabic(text); g["bomb"]["raw"] = clean(text, 50); g["bomb"]["is_set"] = True; g["bomb"]["owner"] = uid; g["psycho_phase"][uid] = "done"
            safe_pm(uid, "💣 القنبلة جاهزة."); return
        if g.get("last_gasp_pending", {}).get(uid):
            g["last_gasp_text"][uid] = clean(text, 50); g["last_gasp_pending"][uid] = False
            safe_pm(uid, "🩸 تم."); return
        if g["type"] == "vote" and g["phase"] == "waiting_q" and g.get("asker") == uid and g.get("ask_type_chosen"):
            g["vote_question"] = clean(text, 200)
            if g["ask_type"] == "vote": g["phase"] = "voting_active"; send_vote_q(fc, uid, text)
            else: g["phase"] = "answering"; send_qa_q(fc, uid, text)
            safe_pm(uid, "✅ تم النشر."); return
        if g["type"] == "vote" and g["phase"] == "answering" and uid in g.get("qa_answer_pending", set()):
            g["qa_answer_pending"].remove(uid); g["qa_answer_done"].add(uid)
            g["qa_answers"][uid] = {"text": clean(text, 200), "reveal": None}
            mk = types.InlineKeyboardMarkup(); mk.add(types.InlineKeyboardButton("✅ اسمي", callback_data=f"reveal_{fc}_y"), types.InlineKeyboardButton("🎭 مجهول", callback_data=f"reveal_{fc}_n"))
            safe_pm(uid, "✅ الجواب وصل.", reply_markup=mk); return

@bot.message_handler(commands=['لاسلكي'], chat_types=['private'])
def cmd_radio(m):
    uid = m.from_user.id
    text = m.text.split(maxsplit=1)
    if len(text) < 2: return safe_pm(uid, "⚠️ اكتب الرسالة: /لاسلكي (نص)")
    msg_content = text[1]
    
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid: return
        g = games[cid]
        if uid not in g["radio_holders"]: return safe_pm(uid, "🚫 لا تملك جهاز لاسلكي.")
        
        my_role = g["players"][uid]["role"]
        my_name = g["players"][uid]["name"]
        
        for holder in g["radio_holders"]:
            safe_pm(holder, f"📻 <b>لاسلكي ({my_name}):</b>\n{clean(msg_content, 200)}")

@bot.message_handler(commands=['كشف_الكاميرات'], chat_types=['private'])
def cmd_check_cam(m):
    uid = m.from_user.id
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid: return
        g = games[cid]
        if g["players"][uid]["role"] != "Security": return safe_pm(uid, "🚫 لست حارس أمن.")
        if uid in g["security_checked_cam"]: return safe_pm(uid, "🚫 لقد فحصت الكاميرات هذه الليلة.")
        
        last = g.get("observer_last_reveal")
        g["security_checked_cam"].add(uid)
        
        if last: safe_pm(uid, f"📹 <b>تسجيلات الكاميرا:</b>\nآخر شخص راقبه المراقب كان دوره: <b>{last}</b>")
        else: safe_pm(uid, "📹 <b>شاشة سوداء:</b>\nالمراقب لم يقم بأي نشاط مؤخراً.")

def start_hospital(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        pp = g["players"]
        if len(pp) < MIN_HOSPITAL:
            safe_send(cid, f"⚠️ العدد غير كافٍ ({len(pp)}/{MIN_HOSPITAL}).")
            # ⚠️ استخدام RLock يسمح بالاستدعاء المتداخل بأمان
            force_cleanup(cid)
            return
        
        uids = list(pp.keys())
        random.shuffle(uids)
        roles = get_roles_for_count(len(uids))
        for i, uid in enumerate(uids):
            pp[uid]["role"] = roles[i]
            g["original_team"][uid] = ROLE_TEAM.get(roles[i], "good")
            if roles[i] == "Anesthetist": g["anesthetist_uses"][uid] = 2; g["radio_holders"].add(uid); g["evil_chat_ids"].add(uid)
            if roles[i] == "Nurse": g["nurse_has_poison"][uid] = True
            if roles[i] == "Surgeon": g["stats"]["surgeon_uid"] = uid; g["radio_holders"].add(uid); g["evil_chat_ids"].add(uid)
            if roles[i] == "Security": g["security_ammo"][uid] = 1
            
        g["phase"] = "roles_reveal"
        g["game_started_at"] = time.time()
        gid = g["game_id"]

    safe_send(cid, "🏥 <b>بدأ الكابوس!</b>\nافحص ملفك السري في الخاص.")
    mk = types.InlineKeyboardMarkup()
    # تم تغيير نص الزر
    mk.add(types.InlineKeyboardButton("📂 ملفك", url=f"https://t.me/{BOT_USERNAME}?start=role_{cid}"))
    safe_send(cid, "اضغط هنا لمعرفة دورك 👇", reply_markup=mk)
    
    if not safe_sleep(cid, gid, 10): return
    
    assign_joker(cid, gid)
    start_room_choosing(cid, gid)

def start_vote_game(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        if len(g["players"]) < MIN_VOTE:
            safe_send(cid, f"⚠️ العدد غير كافٍ ({len(g['players'])}/{MIN_VOTE}).")
            force_cleanup(cid)
            return
        g["asked_uids"] = set()
        g["vote_round"] = 0
        g["game_started_at"] = time.time()
        g["asked_uids_done"] = set()
        gid = g["game_id"]

    safe_send(cid, "🗳 <b>بدأت الحلبة!</b>")
    if not safe_sleep(cid, gid, 2): return
    run_vote_round(cid, gid)

def run_vote_round(cid, gid):
    while True:
        with bot_lock:
            if not valid_game(cid, gid): return
            g = games[cid]
            avail = [u for u in g["players"] if u not in g["asked_uids"]]
            if not avail: break
            asker = random.choice(avail)
            g["asker"] = asker
            g["asked_uids"].add(asker)
            g["phase"] = "waiting_q"
            g["vote_round"] += 1
            rnd = g["vote_round"]
        
        silence_all(cid)
        mk = types.InlineKeyboardMarkup()
        # تم تعديل نص الزر
        mk.add(types.InlineKeyboardButton("🎤 المنصة", url=f"https://t.me/{BOT_USERNAME}?start=ask_{cid}"))
        safe_send(cid, f"🎤 <b>الجولة {rnd}</b>: {g['players'][asker]['name']}", reply_markup=mk)
        
        t_end = time.time() + VOTE_GAME_ASK_TIME
        got_q = False
        while time.time() < t_end:
            time.sleep(1)
            with bot_lock:
                if not valid_game(cid, gid): return
                if g["phase"] != "waiting_q":
                    got_q = True
                    break
        
        if not got_q:
            safe_send(cid, "⏰ انتهى الوقت.")
            continue
            
        with bot_lock: p = g["phase"]
        if p == "voting_active":
            if not safe_sleep(cid, gid, VOTE_GAME_VOTE_TIME): return
            _tally_vote_round(cid, rnd, gid)
        elif p == "answering":
            if not safe_sleep(cid, gid, VOTE_GAME_ANSWER_TIME): return
            _show_qa_round(cid, rnd, gid)
            
    show_vote_game_end(cid, gid)

def _tally_vote_round(cid, rnd, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        votes = games[cid]["votes"]
    
    if not votes: safe_send(cid, "🤷 لا أصوات.")
    else:
        counts = {}
        for v in votes.values(): counts[v] = counts.get(v, 0) + 1
        res = []
        for k, v in counts.items():
            name = games[cid]["players"][k]["name"]
            res.append(f"▫️ {name}: {v}")
        safe_send(cid, "🗳 <b>النتائج:</b>\n" + "\n".join(res))

def _show_qa_round(cid, rnd, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        ans = games[cid]["qa_answers"]
        q = games[cid]["vote_question"]
    
    txt = f"❓ <b>{q}</b>\n\n"
    for uid, data in ans.items():
        name = games[cid]["players"][uid]["name"] if data["reveal"] else "🎭 مجهول"
        txt += f"🔹 {name}: {data['text']}\n"
    safe_send(cid, txt)

def show_vote_game_end(cid, gid):
    safe_send(cid, "🏁 <b>انتهت اللعبة!</b>")
    force_cleanup(cid)

@bot.message_handler(commands=['start'], chat_types=['private'])
def start_pm(m):
    try:
        args = m.text.split()
        if len(args) > 1:
            param = args[1]
            if param.startswith("room_"): dispatch_room(m.from_user.id, param)
            elif param.startswith("night_"): dispatch_night(m.from_user.id, param)
            elif param.startswith("joker_"): dispatch_joker(m.from_user.id, param)
            elif param.startswith("role_"): 
                cid = int(param.replace("role_", ""))
                if cid in games and m.from_user.id in games[cid]["players"]:
                    role = games[cid]["players"][m.from_user.id]["role"]
                    safe_pm(m.from_user.id, f"🎭 دورك: <b>{ROLE_DISPLAY.get(role, role)}</b>")
            elif param.startswith("ask_"):
                # منطق لعبة التصويت (المنصة)
                cid = int(param.replace("ask_", ""))
                with bot_lock:
                    if cid in games and games[cid]["asker"] == m.from_user.id:
                        mk = types.InlineKeyboardMarkup()
                        mk.add(types.InlineKeyboardButton("تصويت", callback_data=f"asktype_{cid}_vote"),
                               types.InlineKeyboardButton("سؤال وجواب", callback_data=f"asktype_{cid}_qa"))
                        safe_pm(m.from_user.id, "ما هو نوع الجولة؟", reply_markup=mk)
            return
    except: pass
    safe_pm(m.from_user.id, "🤖 أهلاً بك.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("asktype_"))
def cb_asktype(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, typ = int(parts[1]), parts[2]
    except: return
    with bot_lock:
        if cid not in games: return
        g = games[cid]
        if g.get("asker") != uid: return
        g["ask_type"] = "vote" if typ == "vote" else "qa"
        g["ask_type_chosen"] = True
    bot.answer_callback_query(call.id, "اكتب سؤالك الآن")
    try: bot.edit_message_text("✍️ اكتب سؤالك الآن:", uid, call.message.message_id)
    except: pass

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def pm_handler_voting_q(m):
    uid = m.from_user.id
    text = m.text
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid or cid not in games: return
        g = games[cid]
        if g["type"] != "vote": return # فقط للعبة التصويت
        
        # استلام السؤال من السائل
        if g["phase"] == "waiting_q" and g.get("asker") == uid and g.get("ask_type_chosen"):
            g["vote_question"] = clean(text, 200)
            if g["ask_type"] == "vote": 
                g["phase"] = "voting_active"
                send_vote_q(cid, uid, text)
            else: 
                g["phase"] = "answering"
                send_qa_q(cid, uid, text)
            safe_pm(uid, "✅ تم النشر.")
            return

        # استلام الإجابة من اللاعبين (في وضع سؤال وجواب)
        if g["phase"] == "answering" and uid in g.get("players") and g["players"][uid]["alive"]:
            # منطق تجميع الإجابات (مبسط)
            if uid not in g["qa_answers"]:
                g["qa_answers"][uid] = {"text": clean(text, 200), "reveal": True} # افتراضياً الاسم ظاهر
                safe_pm(uid, "✅ تم استلام إجابتك.")
            return

def send_vote_q(cid, asker_id, text):
    with bot_lock:
        g = games[cid]
        alive = [u for u, p in g["players"].items() if p["alive"]]
    
    mk = types.InlineKeyboardMarkup()
    for u in alive:
        mk.add(types.InlineKeyboardButton(g["players"][u]["name"], callback_data=f"vote_{cid}_{u}"))
    
    safe_send(cid, f"❓ <b>سؤال التصويت:</b>\n{text}\n\nصوّت الآن!", reply_markup=mk)

def send_qa_q(cid, asker_id, text):
    safe_send(cid, f"❓ <b>سؤال للنقاش:</b>\n{text}\n\nأرسل إجابتك للبوت في الخاص.")

# ══════════════ التشغيل ══════════════
print("Bot Started...")
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60, allowed_updates=["message", "callback_query", "chat_member"])
    except Exception as e:
        print(f"Polling Crash: {e}")
        time.sleep(5)
