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
TOKEN = "8300157614:AAEob3NY0woxB4zhChSy1GCUj1eDZUNyYTQ"

OWNER_USERNAME = "O_SOHAIB_O"
OWNER_CHAT_ID = None
PUBLIC_GROUP_ID = -1002493822482

bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True, num_threads=3)

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

NIGHT_TIME = 40
LAST_GASP_TIME = 45 
DISCUSS_TIME = 40
VOTE_TIME = 25
CONFIRM_TIME = 20
DEFENSE_TIME = 40
WILL_TIME = 30
BOMB_TIME = 25
ROOM_CHOOSE_TIME = 30

VOTE_GAME_ASK_TIME = 45
VOTE_GAME_VOTE_TIME = 25
VOTE_GAME_ANSWER_TIME = 30
VOTE_GAME_DISCUSS_TIME = 20

AFK_KILL_THRESHOLD = 2
AFK_WARNING_THRESHOLD = 1
MEDICAL_DROP_CHANCE = 0.3
DOCTOR_FAIL_CHANCE = 0.1

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

# ══════════════ الأدوار والشروحات المصغرة ══════════════
ROLE_DISPLAY = {
    "Surgeon": "🔪 الجرّاح", "Anesthetist": "💉 المخدّر",
    "Instigator": "🧠 المحرّض", "Psychopath": "🤡 المجنون",
    "Doctor": "🩺 الطبيب", "Observer": "👁 المراقب",
    "Swapper": "🛏 عابث الأسرّة", "Patient": "🤕 المريض",
    "Screamer": "😱 المرعوب", "Nurse": "💊 الممرّض",
    "Security": "👮 حارس الأمن",
}

# شرح مصغر يظهر عند استلام الدور فقط
ROLE_GUIDE_SHORT = {
    "Surgeon": "🔪 <b>أنت الجرّاح (الأشرار).</b>\nهدفك تصفية الأبرياء. ستتحرك كل ليلة لاختيار ضحيتك.",
    "Anesthetist": "💉 <b>أنت المخدّر (الأشرار).</b>\nمهمتك شل قدرات الأطباء ليلاً. ستتفعل قدرتك في الليلة الثانية.",
    "Instigator": "🧠 <b>أنت المحرّض (محايد).</b>\nتستطيع سرقة صوت أحدهم في التصويت. ستتفعل قدرتك في الليلة الثانية.",
    "Psychopath": "🤡 <b>أنت المجنون (فريق مستقل).</b>\nهدفك إقناعهم بإعدامك. قم بتجهيز قنبلتك الليلة!",
    "Doctor": "🩺 <b>أنت الطبيب (الأخيار).</b>\nمهمتك حماية الأرواح. اختر شخصاً لإنقاذه كل ليلة.",
    "Observer": "👁 <b>أنت المراقب (الأخيار).</b>\nتستطيع كشف هويات الآخرين. ستتفعل قدرتك في الليلة الثانية.",
    "Swapper": "🛏 <b>أنت عابث الأسرّة (الأخيار).</b>\nقم بتبديل مواقع اللاعبين لإرباك القتلة. ستتفعل قدرتك في الليلة الثانية.",
    "Patient": "🤕 <b>أنت المريض (الأخيار).</b>\nترقب جثث الموتى لتسرق هوياتهم وتكمل مسيرتهم.",
    "Screamer": "😱 <b>أنت المرعوب (الأخيار).</b>\nلا تحتاج لفعل شيء. إذا زارك أحد ليلاً (غير الجراح) ستصرخ باسمه تلقائياً ليسمعه الجميع!",
    "Nurse": "💊 <b>أنت الممرّض (الأخيار).</b>\nتملك حقنة سم واحدة لقتل الشرير. ستتفعل قدرتك في الليلة الثانية.",
    "Security": "👮 <b>أنت حارس الأمن (الأخيار).</b>\nلديك رصاصة واحدة لتحقيق العدالة. ستتفعل قدرتك في الليلة الثانية."
}

ROLE_TEAM = {
    "Surgeon": "evil", "Anesthetist": "evil",
    "Instigator": "neutral",
    "Doctor": "good", "Observer": "good", "Swapper": "good",
    "Patient": "good", "Psychopath": "psycho",
    "Screamer": "good", "Nurse": "good",
    "Security": "good",
}

# فقط الجراح والطبيب والمجنون يتم تفعيل إشعارهم الليلة الأولى فوراً
INSTANT_ROLES = {"Surgeon", "Doctor", "Psychopath"}

ROLE_ACTION_MAP = {
    "Surgeon": "surgeon", "Doctor": "doctor", "Anesthetist": "anesthetist",
    "Observer": "observer", "Instigator": "instigator", "Swapper": "swapper",
    "Nurse": "nurse", "Patient": "patient", "Security": "security"
}

SILENT_PHASES = {
    "night", "morning", "roles_reveal", "resolving",
    "waiting_q", "answering", "will_wait", "last_gasp_wait",
    "confirming", "qa_results", "ended",
    "room_choosing",
}

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
    return html.escape(s)

def clean_name(t):
    s = str(t or "مجهول")
    s = s.replace('\n', '').replace('\r', '')
    return html.escape(s)

def pname(uid, name):
    return f"<a href='tg://user?id={uid}'><b>{name}</b></a>"

def pname_vip(uid, name):
    crown = "👑 " if has_title(uid, "title_vip") else ""
    return f"{crown}<a href='tg://user?id={uid}'><b>{name}</b></a>"

import unicodedata
import re

def normalize_arabic(t):
    if not t:
        return ""

    # إزالة التشكيل (الحركات)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')

    # إزالة المسافات الزائدة وتحويل لحروف صغيرة + إزالة التشكيل المتبقي
    t = t.strip().lower()

    # توحيد الحروف المتشابهة
    replacements = [
        ("أ|إ|آ", "ا"),
        ("ة", "ه"),
        ("ى", "ي"),
        ("ؤ", "و"),
        ("ئ", "ي")
    ]
    for a, b in replacements:
        t = re.sub(a, b, t)

    # تحويل الأرقام العربية إلى إنجليزية
    t = re.sub(r'[٠-٩]', lambda m: str("٠١٢٣٤٥٦٧٨٩".index(m.group())), t)

    return re.sub(r'\s+', ' ', t).strip()

def corrupt_text(text):
    words = text.split()
    new_words =[]
    for w in words:
        if random.random() < 0.6: 
            new_words.append("." * random.randint(2, 5))
        else:
            new_words.append(w)
    return " ".join(new_words)

# ══════════════ المحفظة والبروفايل ══════════════
def get_wallet(uid):
    if uid not in wallets_db:
        wallets_db = {"coins": 0, "gems": 0, "inventory":[], "titles": []}
    return wallets_db

def add_coins(uid, amount):
    w = get_wallet(uid)
    w += amount

def has_item(uid, item_id):
    return item_id in get_wallet(uid)

def use_item(uid, item_id):
    w = get_wallet(uid)
    if item_id in w:
        w.remove(item_id)
        return True
    return False

def has_title(uid, title_id):
    return title_id in get_wallet(uid)

def buy_item(uid, item_id):
    if item_id not in SHOP_ITEMS:
        return False, "❌ غير موجود"
    w = get_wallet(uid)
    item = SHOP_ITEMS
    if w < item:
        return False, "❌ رصيدك لا يكفي"
    if item_id.startswith("title_"):
        if item_id in w:
            return False, "❌ تملكه بالفعل"
        w -= item
        w.append(item_id)
    else:
        w -= item
        w.append(item_id)
    return True, f"✅ حصلت على <b>{item}</b>"

def get_profile(uid):
    if uid not in profiles_db:
        profiles_db = {
            "games": 0, "wins": 0, "losses": 0,
            "kills_as_surgeon": 0, "saves_as_doc": 0,
            "reveals_as_obs": 0, "bombs_triggered": 0,
            "deaths": 0, "messages_sent": 0,
            "best_streak": 0, "current_streak": 0,
            "xp": 0,
        }
    return profiles_db

def add_xp(uid, amount):
    p = get_profile(uid)
    p += amount

def update_hall(category, uid, value=1):
    if uid not in hall_of_fame:
        hall_of_fame = 0
    hall_of_fame += value

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
        uids = list(games.keys())
    for uid in uids:
        mute_player(cid, uid)

def open_discussion(cid):
    with bot_lock:
        if cid not in games: return
        dead_u = [u for u, p in games.items() if not p]
        alive_u =.items() if p]
    unmute_all(cid)
    time.sleep(0.3)
    for uid in alive_u: unmute_player(cid, uid)
    time.sleep(0.2)
    for uid in dead_u: mute_player(cid, uid)

# ══════════════ التنظيف الشامل ══════════════
_cleanup_lock = threading.Lock()

def force_cleanup(cid):
    with _cleanup_lock:
        with bot_lock:
            if cid in games:
                uids = list(games.get("players", {}).keys())
                for uid in uids:
                    user_to_game.pop(uid, None)
                del games
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
    return {u: p for u, p in games.items() if p}

def get_alive_except(cid, exc):
    return {u: p for u, p in get_alive(cid).items() if u != exc}

def is_participant(cid, uid):
    return cid in games and uid in games

def find_game_for_user(uid):
    return user_to_game.get(uid)

def valid_game(cid, gid):
    return cid in games and games == gid

def is_game_active(cid, gid):
    with bot_lock:
        return valid_game(cid, gid)

def kill_player(g, uid):
    if not g: return False
    g = False
    if uid not in g:
        g.append(uid)
    if not g:
        g = uid
    return True

def get_original_team(g, uid):
    ot = g.get("original_team", {})
    if uid in ot: return ot
    return ROLE_TEAM.get(g, "good")

def safe_sleep(cid, gid, seconds):
    end = time.time() + seconds
    while time.time() < end:
        time.sleep(min(1.0, end - time.time()))
        with bot_lock:
            if not valid_game(cid, gid): return False
    return True

def get_room_players(g, room_id, alive_only=True):
    result = {}
    for uid, p in g.items():
        if alive_only and not p: continue
        if g.get(uid) == room_id:
            result = p
    return result

def get_player_room(g, uid):
    return g.get(uid)

def get_room_targets(g, uid, exclude_self=True):
    my_room = get_player_room(g, uid)
    if not my_room: return {}
    
    if my_room == 5: 
        players = {u: p for u, p in g.items() if p}
    else: 
        players = get_room_players(g, my_room)
    
    if exclude_self:
        return {u: p for u, p in players.items() if u != uid}
    return players

def get_roles_for_count(n):
    n = max(n, 4)
    base =
    if n >= 5: base.append("Anesthetist")
    if n >= 6: base.append("Nurse") 
    if n >= 7: base.append("Security") 
    
    pool =
    while len(base) < n:
        r = random.choice(pool)
        base.append(r)
        
    random.shuffle(base)
    return base

def transfer_radio(g, dead_uid, killer_uid=None):
    if dead_uid in g:
        g.remove(dead_uid)
        new_holder = None
        if killer_uid and killer_uid in g and g:
            new_holder = killer_uid
        else:
            alive = if g and u != dead_uid]
            if alive:
                new_holder = random.choice(alive)
        if new_holder:
            g.add(new_holder)
            safe_pm(new_holder, "📻 <b>لقد عثرت على لاسلكي!</b>\n\nتحدث عبره باستخدام:\n<code>/لاسلكي الرسالة</code>")

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
        "round": 0, "dead_list":[], "silenced": set(),
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
            "rooms_history":[],
        },
        "pinned_mids":[], "winners_team": None,
    }

# ══════════════ نظام الفوز ══════════════
def _check_win_inner(cid):
    if cid not in games: return None
    g = games
    pp = g
    alive = {u: p for u, p in pp.items() if p}

    if not alive:
        g = None
        return "⚰️ <b>لا ناجين... المستشفى ابتلع الجميع.</b>"

    evil_alive =
    good_alive =
    psycho_alive =
    neutral_alive =

    total_alive = len(alive)

    if psycho_alive and not evil_alive and len(alive) <= 2:
        g = "psycho"
        return "🤡 <b>المجنون يرقص وحيداً فوق الجثث.</b>"

    if not good_alive and not psycho_alive and not neutral_alive:
        g = "evil"
        return "🔪 <b>الظلام انتصر... الأطباء ماتوا.</b>"

    if not evil_alive and not psycho_alive:
        g = "good"
        return "🩺 <b>تم تطهير المستشفى... النور ينتصر.</b>"

    # حالات خاصة
    has_surgeon = any(pp == "Surgeon" for u in evil_alive)
    has_active_killer = has_surgeon or any(pp == "Anesthetist" for u in evil_alive)
    
    if total_alive == 2 and has_surgeon and good_alive:
        g = "evil"
        return "🔪 <b>المشرط أسرع... الجرّاح فاز.</b>"

    if evil_alive and not has_active_killer:
        patient_can = any(pp == "Patient" and u not in g.get("patient_used", set()) for u in alive)
        dead_surg = any(pp == "Surgeon" and not pp for u in pp)
        if not (patient_can and dead_surg):
            g = "good"
            return "🩺 <b>سقط آخر قاتل...</b>"

    non_evil = len(good_alive) + len(psycho_alive) + len(neutral_alive)
    if evil_alive and len(evil_alive) >= non_evil:
        g = "evil"
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
        g = games
        g = "ended"
        
        lines = []
        for u, p in g.items():
            status = "حي" if p else "ميت"
            lines.append(f"▫️ {p}: {ROLE_DISPLAY.get(p, '?')} ({status})")
    
    full = f"{msg}\n\n<b>الأدوار:</b>\n\n" + "\n\n".join(lines)
    safe_send(cid, full)
    force_cleanup(cid)

def check_afk(cid):
    return [],[]

def do_medical_drop(cid, gid):
    pass

# ══════════════ حلقة اللعبة ══════════════
def game_loop():
    while True:
        time.sleep(3)
        now = time.time()
        to_del = []
        to_start =[]
        with bot_lock:
            for cid in list(games.keys()):
                g = games
                if now - g > INACTIVITY_TIMEOUT:
                    to_del.append(cid)
                    continue
                if g == "joining" and g <= now:
                    g = "starting"
                    to_start.append((cid, g, g))
        
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
    g = games
    rem = max(0, int(g - time.time()))
    total = max(g.get("total_wait", DEFAULT_WAIT_TIME), 1)
    gt = g
    pp = g
    n = len(pp)

    if gt == "hospital":
        mn = MIN_HOSPITAL
        title = "🏥 المستشفى"
        flavor = "الممرات مظلمة... ثق بحدسك فقط."
    else:
        mn = MIN_VOTE
        title = "⚖️ مجلس التصويت"
        flavor = "من صاحب الحجة الأقوى؟"

    if n == 0:
        pt = "   <i>(لا أحد بعد)</i>"
    else:
        lines =[]
        for u, p in pp.items():
            lines.append(f"   🔹 {pname_vip(u, p)}")
        pt = "\n".join(lines)

    bar_f = int(min(max(rem / total, 0), 1.0) * 10)
    bar = "▓" * bar_f + "░" * (10 - bar_f)
    m, sc = divmod(max(0, rem), 60)
    ts = f"{m}:{sc:02d}" if m else f"{sc}s"

    return (
        f"<b>{title}</b>\n\n"
        f"⏳ {bar}  <b>{ts}</b>\n\n"
        f"<i>{flavor}</i>\n\n"
        f"👥 <b>المسجلون ({n}):</b>\n\n{pt}\n\n"
        f"📌 مطلوب: <b>{mn}</b>\n\n"
        f"🚀 <code>/force_start</code>  ·  ⏱ <code>/time 30</code>"
    )

def join_markup(gid, gtype="hospital"):
    m = types.InlineKeyboardMarkup()
    btn_text = "💀 توقيع الدخول" if gtype == "hospital" else "🗳️ تسجيل الحضور"
    m.add(types.InlineKeyboardButton(btn_text, callback_data=f"join_{gid}"))
    return m

def lobby_tick(cid, gid):
    resent = False
    while True:
        time.sleep(8)
        with bot_lock:
            if not valid_game(cid, gid) or games != "joining": return
            rem = max(0, int(games - time.time()))
            gt = games

        if rem <= 25 and not resent:
            resent = True
            with bot_lock:
                if not valid_game(cid, gid): return
                txt = build_lobby(cid)
                mk = join_markup(gid, gt)
            asset = ASSETS if gt == "hospital" else ASSETS
            
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
                        games = nm.message_id
                        games = "media" if nm.content_type in else "text"
            continue

        with bot_lock:
            if not valid_game(cid, gid) or games != "joining": return
            txt = build_lobby(cid)
            gt = games
            mk = join_markup(games, gt)
            mid = games.get("lobby_mid")
            mt = games.get("lobby_mt", "text")
        if mid:
            if mt == "media": safe_edit_caption(cid, mid, txt, reply_markup=mk)
            else: safe_edit_text(cid, mid, txt, reply_markup=mk)
        if rem <= 0: return

# ══════════════ الانضمام ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("join_"))
def cb_join(call):
    cid, uid = call.message.chat.id, call.from_user.id
    try: gid = int(call.data.split("_"))
    except: return
    
    with bot_lock:
        if not valid_game(cid, gid):
            return bot.answer_callback_query(call.id, "⛔ انتهت", show_alert=True)
        if games != "joining":
            return bot.answer_callback_query(call.id, "⛔ بدأت", show_alert=True)
        if uid in games:
            return bot.answer_callback_query(call.id, "✅ مسجل", show_alert=True)
        if len(games) >= MAX_PLAYERS:
            return bot.answer_callback_query(call.id, "⛔ ممتلئ", show_alert=True)
        ex = find_game_for_user(uid)
        if ex and ex != cid:
            return bot.answer_callback_query(call.id, "⛔ أنت في لعبة أخرى", show_alert=True)
            
        games = {
            "name": clean_name(call.from_user.first_name),
            "role": "Patient", "alive": True
        }
        user_to_game = cid
        games = time.time()
        cnt = len(games)
        gt = games
        
    bot.answer_callback_query(call.id, f"✅ تم ({cnt})")
    
    with bot_lock:
        if not valid_game(cid, gid): return
        txt = build_lobby(cid)
        mk = join_markup(games, gt)
        mid = games.get("lobby_mid")
        mt = games.get("lobby_mt", "text")
    if mid:
        if mt == "media": safe_edit_caption(cid, mid, txt, reply_markup=mk)
        else: safe_edit_text(cid, mid, txt, reply_markup=mk)

# ══════════════ فلتر الرسائل ══════════════
@bot.message_handler(content_types=,
                     func=lambda m: m.chat.type in ("group", "supergroup") and m.chat.id in games and not (m.text or "").startswith("/"))
def group_msg_filter(m):
    cid, uid = m.chat.id, m.from_user.id
    text = m.text or ""
    do_delete = False
    do_blackout = False
    blackout_text = ""

    with bot_lock:
        if cid not in games: return
        g = games
        phase = g

        if phase == "bomb":
            if not is_participant(cid, uid) or not g.get(uid, {}).get("alive", False):
                do_delete = True
            elif text:
                if normalize_arabic(text) == g:
                    g = "defused"
                    g = uid
                else: do_delete = True
            else: do_delete = True
            if do_delete: delete_msg(cid, m.message_id)
            return

        if phase == "defense":
            # السماح للجميع بالكلام في مرحلة الدفاع
            if is_participant(cid, uid) and g:
                g = g.get(uid, 0) + 1
                return
            else: do_delete = True

        if not do_delete and is_participant(cid, uid):
            p = g.get(uid)
            if p and not p: do_delete = True

        if not do_delete and phase in SILENT_PHASES:
            if is_participant(cid, uid): do_delete = True

        if not do_delete and phase == "discussion":
            if is_participant(cid, uid) and g:
                if text:
                    g = g.get(uid, 0) + 1
                    g = g.get(uid, 0) + 1
                if g.get("blackout_active", False):
                    do_blackout = True
                    blackout_text = text or "..."

    if do_delete: delete_msg(cid, m.message_id)
    elif do_blackout:
        delete_msg(cid, m.message_id)
        safe_send(cid, f"🔇 <i>همس:</i> {clean(blackout_text, 50)}")

@bot.message_handler(content_types=, func=lambda m: m.chat.type in ("group", "supergroup"))
def on_member_leave(m):
    if not m.left_chat_member: return
    uid = m.left_chat_member.id
    cid = m.chat.id
    with bot_lock:
        if cid not in games or uid not in games: return
        g = games
        if not g: return
        kill_player(g, uid)
        pn = pname(uid, g)
        rd = ROLE_DISPLAY.get(g, "?")
        user_to_game.pop(uid, None)
        gid = g
    safe_send(cid, f"🚪 {pn} غادر... وكان: {rd}")
    check_win_safe(cid, gid)

# ══════════════ أوامر المجموعة والتعليمات ══════════════
@bot.message_handler(func=lambda m: m.chat.type in ("group", "supergroup") and m.text and m.text.startswith("/"))
def group_cmd(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split().split("@").lower()

    deletable = {"/hospital", "/vote", "/force_start", "/cancel", "/done", "/time", "/commands", "/hall", "/rooms_cancel", "/لاسلكي", "/كشف_الكاميرات", "/shop", "/buy", "/profile", "/roles", "/tutorial"}
    if raw in deletable: delete_msg(cid, m.message_id)

    if raw == "/hospital": init_game(m, "hospital")
    elif raw == "/vote": init_game(m, "vote")
    elif raw == "/time": do_time(m)
    elif raw == "/force_start": do_force(m)
    elif raw in ("/cancel", "/done"): do_cancel(m)
    elif raw == "/commands": do_commands(m)
    elif raw == "/hall": do_hall(m)
    elif raw == "/rooms_cancel": do_rooms_cancel(m)
    elif raw == "/shop": do_shop(m)
    elif raw == "/profile": do_profile(m)
    elif raw == "/buy": do_buy(m)
    elif raw == "/roles": do_roles(m)
    elif raw == "/tutorial": do_tutorial(m)

def init_game(msg, gtype):
    cid = msg.chat.id
    uid = msg.from_user.id
    if msg.chat.type not in ("group", "supergroup"): return

    with bot_lock:
        if cid in games:
            g = games
            is_stuck = False
            if g == "joining" and (time.time() - g > 300):
                is_stuck = True
            
            if is_stuck:
                uids = list(g.keys())
                for u in uids: user_to_game.pop(u, None)
                del games
            else:
                return safe_send(cid, "⚠️ <i>اللعبة جارية!</i>")

        if find_game_for_user(uid):
            return safe_send(cid, "⚠️ <i>أنت في لعبة أخرى.</i>")

        gid = int(time.time() * 1000) % 2147483647
        games = new_game_data(gtype, uid, gid)

    txt = build_lobby(cid)
    mk = join_markup(gid, gtype)
    
    m2 = None
    try:
        if gtype == "hospital":
            m2 = bot.send_animation(cid, ASSETS, caption=txt, parse_mode="HTML", reply_markup=mk)
        else:
            m2 = bot.send_photo(cid, ASSETS, caption=txt, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"Lobby Media Failed: {e}")
        m2 = safe_send(cid, txt, reply_markup=mk)
    
    if m2:
        with bot_lock:
            if cid in games:
                games = m2.message_id
                games = "media" if m2.content_type in else "text"
    
    threading.Thread(target=lobby_tick, args=(cid, gid), daemon=True).start()

def do_time(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games != "joining": return
        if games != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        try:
            s = int(m.text.split()) if len(m.text.split()) > 1 else 30
            s = min(max(s, 10), 120)
            games += s
            r = int(games - time.time())
            games = max(r, 1)
            games = time.time()
        except: return

def do_force(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games != "joining": return
        if games != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        games = time.time()

def do_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games: return
        is_auth = (games == uid)
    if not is_auth:
        try: is_auth = bot.get_chat_member(cid, uid).status in
        except: pass
    if not is_auth: return
    safe_send(cid, "🛑 <b>تم إلغاء اللعبة.</b>")
    force_cleanup(cid)

def do_rooms_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games != "joining": return
        if games != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'): return
            except: return
        current = games.get("rooms_enabled", True)
        games = not current
        new_state = games
    if new_state: safe_send(cid, "🏠 <i>الغرف: مفعّلة</i>")
    else: safe_send(cid, "🏠 <i>الغرف: معطّلة</i>")

def do_roles(m):
    safe_pm(m.from_user.id, "🎭 <b>دليل المستشفى السري:</b>\n\n" + "\n\n".join())

def do_tutorial(m):
    txt = (
        "📚 <b>كيف تنجو من المستشفى؟ (دليل سريع)</b>\n\n"
        "1️⃣ <b>توقيع الدخول:</b> انضم للعبة من خلال الزر الموجود في مجموعة الدردشة.\n\n"
        "2️⃣ <b>اختيار المخبأ:</b> ستصلك رسالة لاختيار الغرفة. (إذا اخترت غرفة، لن يتمكن من استهدافك سوى من معك في نفس الغرفة. إذا اخترت الممر، يمكنك استهداف الجميع، لكن الجميع سيراك!).\n\n"
        "3️⃣ <b>الليل يحل:</b>\n"
        "   - الأشرار (الجراح والمخدر) يختارون ضحاياهم من قائمتهم.\n"
        "   - الأخيار (الطبيب، المراقب، الحارس) يستخدمون قدراتهم لحماية الفريق أو كشف الأشرار.\n\n"
        "4️⃣ <b>طلوع الفجر:</b> يتم إعلان من مات الليلة الماضية، ويُفتح باب النقاش.\n\n"
        "5️⃣ <b>المحاكمة:</b> يصوت الجميع ضد اللاعب المشتبه به. إذا تمت إدانته، يُحرق فوراً.\n\n"
        "🏆 <b>كيف تفوز؟</b>\n"
        "   - الأخيار: إعدام جميع الأشرار والمجانين.\n"
        "   - الأشرار: قتل الأخيار حتى يتساوى العدد.\n"
        "   - المجنون: خداع الجميع ليصوتوا ضده فيُعدم ويفجر المستشفى بأكمله!"
    )
    safe_pm(m.from_user.id, txt)

def do_commands(m):
    cid = m.chat.id
    cmd_text = (
        "📖 <b>سجل الأوامر</b>\n\n"
        "<code>/hospital</code> - فتح أبواب المستشفى (بدء اللعبة)\n\n"
        "<code>/vote</code> - بدء مجلس التصويت\n\n"
        "<code>/force_start</code> - إجبار اللعبة على البدء فوراً\n\n"
        "<code>/time</code> - تمديد وقت التسجيل\n\n"
        "<code>/cancel</code> - إلغاء الجلسة الحالية\n\n"
        "<code>/myrole</code> - للتحقق من بطاقة هويتك مجدداً\n\n"
        "<code>/roles</code> - عرض تفاصيل جميع الأدوار\n\n"
        "<code>/tutorial</code> - إرسال دليل اللعب الشامل\n\n"
        "<code>/alive</code> - كشف عن الأحياء المتبقين\n\n"
        "<code>/profile</code> - إظهار ملفك الشخصي وإنجازاتك\n\n"
        "<code>/shop</code> - فتح نافذة المتجر الأسود"
    )
    safe_send(cid, cmd_text)

def do_hall(m):
    cid = m.chat.id
    lines =[]
    def top_entry(cat, emoji, label):
        data = hall_of_fame.get(cat, {})
        if not data: return f"{emoji} {label}: <i>-</i>"
        top_uid = max(data, key=data.get)
        try:
            user = bot.get_chat_member(cid, top_uid).user
            name = clean_name(user.first_name)
        except: name = str(top_uid)
        return f"{emoji} {label}: <b>{name}</b> ({data})"

    lines.append(top_entry("wins", "👑", "أكثر الانتصارات"))
    lines.append(top_entry("surgeon_kills", "🔪", "أمهر جرّاح"))
    lines.append(top_entry("doc_saves", "🩺", "أفضل طبيب"))
    lines.append(top_entry("bombs", "🤡", "أخطر مجنون (مفجر)"))
    lines.append(top_entry("deaths", "💀", "أكثر الضحايا"))
    safe_send(cid, "🏆 <b>لوحة الشرف (أساطير المستشفى)</b>\n\n" + "\n\n".join(lines))

def do_shop(m):
    cid = m.chat.id
    text = "🛒 <b>السوق المظلم</b>\nاستخدم <code>/buy كود</code> لاقتناء الأدوات.\n\n"
    for k, v in SHOP_ITEMS.items():
        text += f"🔹 <b>{v}</b> ({v} 💰)\n   {v}\n   كود: <code>{k}</code>\n\n"
    safe_send(cid, text)

def do_buy(m):
    cid, uid = m.chat.id, m.from_user.id
    try: item_id = m.text.split()
    except: return safe_send(cid, "⚠️ صيغة الشراء: <code>/buy كود_الغرض</code>")
    success, msg = buy_item(uid, item_id)
    safe_send(cid, msg)

def do_profile(m):
    cid, uid = m.chat.id, m.from_user.id
    p = get_profile(uid)
    w = get_wallet(uid)
    
    txt = (
        f"👤 <b>الهوية:</b> {clean_name(m.from_user.first_name)}\n\n"
        f"💰 <b>الرصيد:</b> {w} عملة\n"
        f"🎮 <b>المواجهات:</b> {p}\n"
        f"🏆 <b>النجاة:</b> {p}\n"
        f"💀 <b>السقوط:</b> {p}\n"
        f"🔪 <b>الضحايا (كجراح):</b> {p}\n"
        f"🩺 <b>الإنقاذ (كطبيب):</b> {p}\n\n"
        f"🎒 <b>المخزون:</b> {', '.join(w) if w else 'فارغ تماماً'}"
    )
    safe_send(cid, txt)

# ══════════════ الغرف ══════════════
def start_room_choosing(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        rooms_on = g.get("rooms_enabled", True)

    if not rooms_on:
        with bot_lock:
            if not valid_game(cid, gid): return
            g = games
            g = {}
            for uid, p in g.items():
                if p: g = 1
        start_night(cid, gid)
        return

    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        g = "room_choosing"
        g = {}
        g = set()
        g = time.time()

    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🏠 حدد مخبأك", url=f"https://t.me/{BOT_USERNAME}?start=room_{cid}"))
    safe_send(cid, f"🏠 <b>حان وقت المبيت...</b>\n\nحدد مكان اختبائك الليلة عبر اللوحة أدناه.\n\n<i>معكم {ROOM_CHOOSE_TIME} ثانية لاتخاذ القرار</i>", reply_markup=mk)

    if not safe_sleep(cid, gid, ROOM_CHOOSE_TIME): return

    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        for uid, p in g.items():
            if p and uid not in g:
                g = random.randint(1, 5)

    notify_room_mates(cid, gid)
    if not safe_sleep(cid, gid, 2): return
    start_night(cid, gid)

def dispatch_room(uid, param):
    try: cid = int(param.replace("room_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 اللعبة لم تعد متاحة.")
        g = games
        if uid not in g or not g: return safe_pm(uid, "🚫 أنت لست جزءاً من هذه الجولة.")
        if g != "room_choosing": return safe_pm(uid, "⏰ لقد نفد وقت الاختيار.")
        if uid in g: return safe_pm(uid, f"✅ لقد حجزت مكانك بالفعل.")

    mk = types.InlineKeyboardMarkup(row_width=2)
    for rid, rname in ROOM_NAMES.items():
        mk.add(types.InlineKeyboardButton(rname, callback_data=f"pickroom_{cid}_{rid}"))
    safe_pm(uid, "🏠 <b>أين ستختبئ الليلة؟</b>\n\n📌 <b>الغرف العادية:</b> مكان آمن نسبياً، يمكنك التحدث واستخدام قدرتك فقط مع من يشاركك نفس الغرفة.\n\n📌 <b>الممر المظلم:</b> مكان مكشوف وخطير. يمكنك استهداف أي شخص في المستشفى، لكن الجميع يمكنهم استهدافك أيضاً!", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pickroom_"))
def cb_pickroom(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, rid = int(parts), int(parts)
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games
        if g != "room_choosing": return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        if uid not in g or not g: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g: return bot.answer_callback_query(call.id, "✅", show_alert=True)
        g = rid
    bot.answer_callback_query(call.id, f"✅ توجهت إلى {ROOM_NAMES}")
    try: bot.edit_message_text(f"✅ تم تأمين موقعك في: <b>{ROOM_NAMES}</b>\nانتظر حلول الظلام...", uid, call.message.message_id, parse_mode="HTML")
    except: pass

def notify_room_mates(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        for rid in ROOM_NAMES:
            players_in = get_room_players(g, rid)
            for uid in players_in:
                others = [pname(u, p) for u, p in players_in.items() if u != uid]
                txt = f"🚪 <b>أنت الآن في {ROOM_NAMES}</b>\n\nيشاركك المكان:\n" + "\n".join(others) if others else f"🚪 <b>أنت الآن في {ROOM_NAMES}</b>\n\nيبدو أنك وحدك هنا..."
                safe_pm(uid, txt)

# ══════════════ الليل ══════════════
def start_night(cid, expected_gid):
    auto_send =[]
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games
        g = "night"
        g = {}
        g += 1
        g = {}
        g = {}
        g = {}
        g = {}
        g = {}
        g = set()
        g = set()
        g = {}
        g = {}
        g = {}
        g = {}
        g = set()
        g = time.time()
        rnd = g
        gid = g
        for uid, p in g.items():
            if not p: continue
            if p in INSTANT_ROLES: auto_send.append((uid, p))

    silence_all(cid)
    with bot_lock:
        if valid_game(cid, gid):
            for mid in list(games.get("pinned_mids",[])): safe_unpin(cid, mid)
            games =[]

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🌑 التحرك في الظلام", url=f"https://t.me/{BOT_USERNAME}?start=night_{cid}"))
    try:
        try:
            bot.send_photo(cid, ASSETS, caption=f"🌑 <b>الليلة {rnd}</b>\n\nاستخدم اللوحة أدناه لاتخاذ قراراتك.\n<i>معكم {NIGHT_TIME} ثانية</i>", parse_mode="HTML", reply_markup=mk)
        except:
            safe_send(cid, f"🌑 <b>الليلة {rnd}</b>\n\nاستخدم اللوحة أدناه لاتخاذ قراراتك.\n<i>معكم {NIGHT_TIME} ثانية</i>", reply_markup=mk)
    except: pass

    for uid, role in auto_send: send_night_action(cid, uid, role)
    if not safe_sleep(cid, gid, NIGHT_TIME): return
    with bot_lock:
        if not valid_game(cid, gid): return
        if games != rnd or games != "night": return
    resolve_night(cid, rnd, gid)

def dispatch_night(uid, param):
    try: cid = int(param.replace("night_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 انتهت اللعبة.")
        g = games
        if uid not in g: return safe_pm(uid, "🚫 لست مشاركاً.")
        if not g: return safe_pm(uid, "💀 كيف لروح أن تتحرك؟ أنت ميت.")
        if g != "night": return safe_pm(uid, "☀️ انتظر حتى يحل الظلام.")
        if uid in g.get("night_acted", set()): return safe_pm(uid, "✅ لقد أنهيت تحركاتك لهذه الليلة.")
        if uid in g: return safe_pm(uid, "💉 جسدك مخدر بالكامل... لا تستطيع التحرك.")
        
        role = g
        
        # ⚠️ حظر الليلة الأولى لأي دور عدا الجراح، الطبيب، والمجنون
        if g == 1 and role not in:
            return safe_pm(uid, "⏳ <b>قدرتك قيد التجهيز...</b>\nستتمكن من استخدامها ابتداءً من الليلة الثانية. راقب بصمت.")

        if role == "Screamer": return safe_pm(uid, "😱 <b>أنت المرعوب!</b>\nليس لديك تدخل يدوي. إذا اقترب منك أي شخص الليلة (غير الجراح)، ستصرخ باسمه تلقائياً ليسمعه الجميع!")
        
        # ⚠️ قفل تعافي المريض
        if uid in g.get("ability_night", {}):
            an = g
            if g < an:
                return safe_pm(uid, f"🔒 جسدك لا يزال يتعافى بعد أخذ الهوية الجديدة... قدرتك ستتفعل في الليلة {an}.")

        if role == "Anesthetist" and g.get(uid, 0) <= 0: return safe_pm(uid, "💉 لقد نفدت كل حقن التخدير لديك.")
        if role == "Nurse" and not g.get(uid, True): return safe_pm(uid, "💊 لقد استخدمت حقنة السم مسبقاً.")
        if role == "Patient":
            if uid in g.get("patient_used", set()): return safe_pm(uid, "🚫 لقد تقمصت دوراً بالفعل.")
            dead =.items() if not p and u != uid]
            if not dead: return safe_pm(uid, "🚫 لا توجد جثث لتقمص هويتها بعد.")

    send_night_action(cid, uid, role)

def send_night_action(cid, uid, role):
    with bot_lock:
        if cid not in games: return
        g = games
        
    # ⚠️ تخصيص المجنون لتجهيز القنبلة
    if role == "Psychopath":
        with bot_lock:
            bomb_set = g
        if not bomb_set:
            with bot_lock:
                g = "q"
            safe_pm(uid, "🤡 <b>حان وقت الجنون!</b>\n\nأرسل لي الآن 'اللغز' أو 'السؤال' الذي سيكون شفرة قنبلتك (اكتبه في رسالة عادية هنا):")
        else:
            safe_pm(uid, "💣 قنبلتك مزروعة وجاهزة. استرح الآن وانتظر الصباح.")
        return

    def room_btns(prefix, exclude_teams=None):
        with bot_lock:
            if cid not in games: return None
            g = games
            tgts = get_room_targets(g, uid)
            if exclude_teams:
                tgts = {u: p for u, p in tgts.items() if get_original_team(g, u) not in exclude_teams}
        if not tgts: return None
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(*, callback_data=f"act_{cid}_{t}_{prefix}") for t, p in tgts.items()])
        return m

    prompts = {
        "Surgeon": "🔪 <b>حدد الضحية التي سينهيها مشرطك:</b>",
        "Doctor": "🩺 <b>اختر المريض الذي تريد حمايته الليلة:</b>",
        "Anesthetist": "💉 <b>اختر من تريد تخديره وشل حركته:</b>",
        "Observer": "👁 <b>من تريد أن تكشف هويته الحقيقية؟</b>",
        "Instigator": "🧠 <b>حدد من ستسرق صوته للتصويت غداً:</b>",
        "Swapper": "🛏 <b>اختر الطرف الأول لتبديل مكانه:</b>",
        "Nurse": "💊 <b>لمن ستعطي حقنة السم القاتلة؟ (انتبه للون فريقك)</b>",
        "Security": "👮 <b>حدد المشتبه به لتصفيته (رصاصة واحدة):</b>",
    }

    if role == "Security":
        with bot_lock:
            if cid not in games: return
            ammo = games.get(uid, 0)
        if ammo <= 0: return safe_pm(uid, "🚫 مسدسك فارغ.")
        
        mk = room_btns("security")
        if not mk: return safe_pm(uid, "🚫 لا يوجد أهداف قريبة منك.")
        safe_pm(uid, f"👮 <b>بندقيتك مجهزة برصاصة واحدة. لا تتردد.</b>\n\n<i>تلميح: يمكنك إرسال الأمر /كشف_الكاميرات لترى آخر من تم الكشف عنه.</i>", reply_markup=mk)
        return

    if role == "Patient":
        with bot_lock:
            if cid not in games: return
            dead =.items() if not p and u != uid and p != "Patient"]
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*} ({ROLE_DISPLAY.get(p, '?')})", callback_data=f"act_{cid}_{u}_patient") for u, p in dead])
        safe_pm(uid, "🤕 <b>أمامك الجثث... اختر واحدة لتتقمص دورها:</b>", reply_markup=mk)
        return

    if role == "Swapper":
        with bot_lock:
            if cid not in games: return
            tgts = get_alive_except(cid, uid)
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*, callback_data=f"act_{cid}_{t}_swapper") for t, p in tgts.items()])
        safe_pm(uid, prompts, reply_markup=mk)
        return

    mk = None
    if role in prompts:
        key = ROLE_ACTION_MAP.get(role, role.lower())
        ex = {"evil"} if role in ("Surgeon", "Anesthetist") else None
        mk = room_btns(key, exclude_teams=ex)
        
    if not mk: safe_pm(uid, "🚫 السكون يعم المكان... لا أهداف في نطاقك الليلة.")
    else: safe_pm(uid, prompts, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_"))
def cb_act(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, tid, act = int(parts), int(parts), parts
    except: return

    send_swapper2 = False
    with bot_lock:
        if cid not in games or games != "night": return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        g = games
        pp = g
        if uid not in pp or not pp: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g.get("night_acted", set()) and act != "swapper2": return bot.answer_callback_query(call.id, "✅", show_alert=True)

        role_emoji_map = {
            "surgeon": "🔪 حركة سريعة ومميتة في الظلام...",
            "doctor": "🩺 خطوات حذرة في أروقة المستشفى...",
            "anesthetist": "💉 يتم تحضير إبرة التخدير بهدوء...",
            "nurse": "💊 رائحة الدواء تفوح في الأرجاء...",
        }
        if act in role_emoji_map:
            safe_send(cid, f"<i>{role_emoji_map}</i>")

        if act == "surgeon":
            g = tid
            g.setdefault(tid, []).append(uid)
        elif act == "doctor":
            g = tid
            g.setdefault(tid,[]).append(uid)
        elif act == "anesthetist":
            g.add(tid)
            g = g.get(uid, 0) - 1
            g.setdefault(tid,[]).append(uid)
        elif act == "instigator": g = tid
        elif act == "observer":
            g = tid
            g.setdefault(tid,[]).append(uid)
        elif act == "swapper":
            g = {"first": tid}
            send_swapper2 = True
        elif act == "swapper2":
            g = tid
            g.setdefault(tid, []).append(uid)
            g.setdefault(g,[]).append(uid)
        elif act == "nurse":
            g = tid
            g.setdefault(tid, []).append(uid)
        elif act == "security":
            g = tid
            g = 0
            g.setdefault(tid,[]).append(uid)
        elif act == "patient":
            dr = pp
            g = get_original_team(g, uid)
            pp = dr
            g.add(uid)
            # إعطاء تعافي لليلة واحدة
            g = g + 1
            if dr == "Nurse": g = True
            if dr == "Anesthetist": g = 2; g = "evil"; g.add(uid); g.add(uid)
            if dr == "Surgeon": g = uid; g.add(uid); g = "evil"; g.add(uid)
            if dr == "Security": g = 1

        if act != "swapper":
            g.add(uid)
            g.add(uid)

    if send_swapper2:
        with bot_lock: tgts = get_alive_except(cid, uid)
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*, callback_data=f"act_{cid}_{u}_swapper2") for u, p in tgts.items() if u != tid])
        try: bot.edit_message_text("🛏 <b>اختر الطرف الثاني لإتمام التبديل:</b>", uid, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except: pass
        return

    bot.answer_callback_query(call.id, "✅")
    
    # رسالة خاصة للمريض
    if act == "patient":
        try: bot.edit_message_text(f"💉 <b>تمت العملية بنجاح!</b>\n\nلقد استوليت على هوية ({ROLE_DISPLAY}).\n⏳ ستتفعل قدراتك الجديدة ابتداءً من الليلة القادمة.", uid, call.message.message_id, parse_mode="HTML")
        except: pass
    else:
        try: bot.edit_message_text("✅ <b>تم اتخاذ القرار. تراجع في الظلام وانتظر الصباح.</b>", uid, call.message.message_id, parse_mode="HTML")
        except: pass

# ══════════════ الجوكر ══════════════
def assign_joker(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        alive =.items() if p]
        if not alive: return
        holder = random.choice(alive)
        g = holder
        g = False
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🃏 استخدام البطاقة", url=f"https://t.me/{BOT_USERNAME}?start=joker_{cid}"))
    safe_pm(holder, "🃏 <b>لقد وقعت بطاقة الجوكر في يدك!</b>\n\nتمنحك قدرة استثنائية لمرة واحدة فقط. استخدمها بحذر.", reply_markup=mk)

def dispatch_joker(uid, param):
    try: cid = int(param.replace("joker_", ""))
    except: return
    with bot_lock:
        if cid not in games: return
        g = games
        if g.get("joker_holder") != uid or g.get("joker_used"): return safe_pm(uid, "🚫 البطاقة مستخدمة أو أنها لم تعد بحوزتك.")
    
    mk = types.InlineKeyboardMarkup(row_width=1)
    for k, v in JOKER_OPTIONS.items():
        mk.add(types.InlineKeyboardButton(v, callback_data=f"jkuse_{cid}_{k}"))
    safe_pm(uid, "🃏 <b>ما هي الورقة التي ستلعبها؟</b>\n\n⚠️ <i>ملاحظة: استخدام الجوكر سيكشف هويتك الحقيقية أمام الجميع!</i>", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("jkuse_"))
def cb_joker_use(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, jk = int(parts), parts
    except: return
    with bot_lock:
        if cid not in games: return
        g = games
        if g.get("joker_holder") != uid or g.get("joker_used"): return
        g = True
        g = jk
        pn = g
        pr = ROLE_DISPLAY.get(g, "?")
    
    bot.answer_callback_query(call.id, "🃏")
    safe_send(cid, f"🃏 <b>مفاجأة الجوكر!</b>\n\nاللاعب {pname(uid, pn)} ألقى ببطاقته واستخدم مهارة <b>{JOKER_OPTIONS}</b>\n\nهويته الحقيقية هي: {pr}")

    if jk == "cancel_vote" and g == "voting":
        g = {}
        safe_send(cid, "🔄 تم إبطال جميع الأصوات الحالية!")
    elif jk == "skip_night" and g == "night":
        g = {}
        g = set(g.keys())
        safe_send(cid, "⏭ الظلام ينقشع مبكراً... تم تخطي الليلة دون أي أحداث!")

# ══════════════ معالجة الليل ══════════════
def resolve_night(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games
        if g != expected_rnd or g != "night": return
        g = "morning"
        pp = g
        actions = g
        sedated = g
        
        swaps = {}
        for uid, d in g.items():
            if uid not in sedated and "second" in d:
                a, b = d, d
                if pp.get(a, {}).get("alive") and pp.get(b, {}).get("alive"):
                    swaps = b; swaps = a
        def sw(t): return swaps.get(t, t) if t else t

        s_uid = g.get("surgeon_uid")
        s_tgt = None
        if s_uid and pp and s_uid not in sedated:
            raw_tgt = actions.get("surgeon")
            if raw_tgt: s_tgt = sw(raw_tgt)

        sec_tgt = None
        sec_uid = next((u for u, p in pp.items() if p=="Security" and p), None)
        if sec_uid and sec_uid not in sedated:
            raw_sec = actions.get("security")
            if raw_sec: sec_tgt = sw(raw_sec)

        d_uid = next((u for u, p in pp.items() if p=="Doctor" and p), None)
        d_tgt = None
        d_failed = False
        if d_uid and d_uid not in sedated:
            raw_d = actions.get("doctor")
            if raw_d:
                d_tgt = sw(raw_d)
                if random.random() < DOCTOR_FAIL_CHANCE: d_failed = True

        victim = None
        saved = False
        
        if s_tgt and s_tgt in pp and pp:
            if d_tgt == s_tgt and not d_failed: saved = True
            elif has_item(s_tgt, "shield"):
                use_item(s_tgt, "shield")
                saved = True
            else: victim = s_tgt

        sec_victim = None
        sec_died_guilt = False
        if sec_tgt and sec_tgt in pp and pp:
            if sec_tgt != victim:
                if d_tgt == sec_tgt and not d_failed: saved = True
                else:
                    sec_victim = sec_tgt
                    if get_original_team(g, sec_victim) == "good":
                        sec_died_guilt = True

        nurse_kills = []
        for n, t in g.items():
            if n not in sedated and pp:
                t_real = sw(t)
                if t_real in pp and pp:
                    nk_innocent = False
                    if get_original_team(g, t_real) not in ("evil", "psycho"):
                        nk_innocent = True
                    nurse_kills.append({"victim": t_real, "killer": n, "suicide": nk_innocent})

    try: bot.send_photo(cid, ASSETS, caption="🌅 <b>تشرق الشمس على المستشفى...</b>", parse_mode="HTML")
    except: safe_send(cid, "🌅 <b>تشرق الشمس على المستشفى...</b>")
    
    if not safe_sleep(cid, expected_gid, 2): return

    if d_failed and d_tgt:
        with bot_lock: kill_player(g, d_tgt)
        safe_send(cid, f"💉💀 <b>{pname(d_tgt, pp)}</b> فارق الحياة إثر خطأ طبي في الجرعة!")
        with bot_lock: transfer_radio(g, d_tgt)
    
    if saved:
        safe_send(cid, "✨ <b>المعجزة تحققت... أحدهم نجا من الموت المحتم الليلة الماضية.</b>")
    
    if victim:
        with bot_lock: kill_player(g, victim)
        safe_send(cid, f"🔪💀 <b>{pname(victim, pp)}</b> وُجد ممزقاً بمشرط الجراح.\n\n🎭 بطاقته الملطخة بالدماء تشير إلى: {ROLE_DISPLAY.get(pp, '?')}")
        with bot_lock: transfer_radio(g, victim, s_uid)
        with bot_lock: g = True
        safe_pm(victim, f"🩸 <b>لديك {LAST_GASP_TIME} ثانية لكتابة كلماتك الأخيرة التي ستُقرأ على الجميع.</b>\n\n(اكتب ما شئت)")
        safe_sleep(cid, expected_gid, LAST_GASP_TIME)
        with bot_lock: txt = g.get(victim)
        if txt: safe_send(cid, f"🩸 <i>كلمات {pp} الأخيرة:</i>\n\n{txt}")

    if sec_victim:
        with bot_lock: kill_player(g, sec_victim)
        safe_send(cid, f"🔫💀 <b>{pname(sec_victim, pp)}</b> سقط برصاص حارس الأمن.\n\n🎭 هويته الحقيقية: ||{ROLE_DISPLAY.get(pp, '?')}||")
        with bot_lock: transfer_radio(g, sec_victim, sec_uid)
        
        if sec_died_guilt:
            safe_sleep(cid, expected_gid, 2)
            with bot_lock: kill_player(g, sec_uid)
            safe_send(cid, f"🔥💀 <b>{pname(sec_uid, pp)}</b> (حارس الأمن) أدرك أنه قتل بريئاً... وألقى بنفسه في المحرقة ندماً.\n\n🎭 كان: ||{ROLE_DISPLAY.get(pp, '?')}||")
            with bot_lock: transfer_radio(g, sec_uid)

    for nk in nurse_kills:
        vic = nk
        nur = nk
        if pp:
            with bot_lock: kill_player(g, vic)
            safe_send(cid, f"💊💀 <b>{pname(vic, pp)}</b> لفظ أنفاسه الأخيرة إثر حقنة مسمومة.\n\n🎭 هويته: ||{ROLE_DISPLAY.get(pp, '?')}||")
            with bot_lock: transfer_radio(g, vic, nur)
            
            if nk and pp:
                safe_sleep(cid, expected_gid, 2)
                with bot_lock: kill_player(g, nur)
                safe_send(cid, f"🧪💀 <b>{pname(nur, pp)}</b> (الممرض) اكتشف خطأه القاتل وشرب السم ليلحق بضحيته.\n\n🎭 كان: ||{ROLE_DISPLAY.get(pp, '?')}||")
                with bot_lock: transfer_radio(g, nur)

    if check_win_safe(cid, expected_gid): return
    
    # ⚠️ صراخ المرعوب العلني
    for u, vs in g.items():
        u_real = sw(u)
        if u_real in pp and pp == "Screamer" and pp and u_real not in sedated:
            # إذا الجراح قتله هذا الدور، لا يصرخ (الجراح يكتمه)
            if victim == u_real:
                continue
            
            for v in vs:
                # الجراح دائماً صامت ولا يسبب صراخ حتى لو لم يمت المرعوب (مثلا طبيب أنقذه)
                if pp == "Surgeon": continue
                
                visitor_name = pp
                screamer_name = pp
                safe_send(cid, f"😱 <b>صراخ يمزق السكون!</b>\nاللاعب {pname(u_real, screamer_name)} يصرخ بهستيريا: <i>\"النجدة! {visitor_name} كان يتجول حول سريري!!\"</i>")

    # رسائل الكشف (المراقب)
    for u, t in g.items():
        if u not in sedated and pp.get(u, {}).get("alive"):
            t_real = sw(t)
            if t_real in pp:
                role_name = ROLE_DISPLAY.get(pp, '?')
                safe_pm(u, f"👁 <b>الرؤية تتضح:</b> اللاعب {pp} يخفي خلفه دور: {role_name}")
                with bot_lock: g = role_name 

    # AFK
    afk_kills, _ = check_afk(cid)
    for ak in afk_kills:
        safe_send(cid, f"💔 <b>{pp}</b> لم يتحمل الضغط ومات بسكتة قلبية من الرعب (عدم التفاعل).")
        with bot_lock: transfer_radio(g, ak)

    if check_win_safe(cid, expected_gid): return
    
    _try_promote_anesthetist(cid, expected_gid)
    do_medical_drop(cid, expected_gid)
    
    start_discussion(cid, expected_gid)

def _try_promote_anesthetist(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        surg_alive = any(p == "Surgeon" and p for p in g.values())
        if not surg_alive:
            for u, p in g.items():
                if p == "Anesthetist" and p:
                    p = "Surgeon"
                    g = u
                    safe_pm(u, "🔪 <b>لقد سقط الجراح السابق... المشرط الآن في يدك. أنت الجراح الجديد!</b>")
                    break

# ══════════════ النقاش والتصويت ══════════════
def start_discussion(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games = "discussion"
        alive = len(get_alive(cid))
    
    open_discussion(cid)
    safe_send(cid, f"💬 <b>وقت تبادل الاتهامات ({DISCUSS_TIME}ث)</b>\n\n👥 الأحياء المتبقون: {alive}\n\nتبادلوا الشكوك بحرية. من لديه شيء ليخفيه؟")
    
    if not safe_sleep(cid, gid, DISCUSS_TIME): return
    show_suspect_bar(cid)
    if not safe_sleep(cid, gid, 2): return
    start_voting(cid, gid)

def start_voting(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games = "voting"
        games = {}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚖️ التصويت للإعدام", url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))
    msg = safe_send(cid, f"⚖️ <b>المحاكمة تبدأ ({VOTE_TIME}ث)</b>\n\nمن سيلقى حتفه اليوم؟", reply_markup=mk)
    if msg:
        safe_pin(cid, msg.message_id)
        with bot_lock: games.append(msg.message_id)
    
    if not safe_sleep(cid, gid, VOTE_TIME): return
    tally_trial(cid, gid)

def tally_trial(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        votes = g
        valid_votes = {k: v for k, v in votes.items() if isinstance(k, int) and k in g and g}
        
    safe_unpin_all(cid)
    if not valid_votes:
        safe_send(cid, "🤷 <b>الصمت يعم... لم يتم توجيه تهمة لأي شخص.</b>")
        return start_room_choosing(cid, gid)

    counts = {}
    for t in valid_votes.values(): counts = counts.get(t, 0) + 1
    top_v = max(counts.values())
    candidates =

    txt = "📩 <b>صناديق الاقتراع أفرزت التالي:</b>\n\n"
    for v, t in valid_votes.items():
        vn = g
        tn = g
        txt += f"🔸 {vn} صوّت ضد {tn}\n"
    safe_send(cid, txt)
    
    if len(candidates) == 1:
        start_defense(cid, gid, candidates)
    else:
        safe_send(cid, "🤝 <b>انقسام في الآراء... لا توجد أغلبية، لذا لن يُعدم أحد اليوم.</b>")
        start_room_choosing(cid, gid)

def start_defense(cid, gid, sus):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        g = "defense"
        g = sus
    
    open_discussion(cid)
    safe_send(cid, f"🎤 <b>اللاعب {g} في قفص الاتهام!</b>\n\nدافع عن نفسك، وللآخرين حق الرد! ({DEFENSE_TIME}ث).")
    
    if not safe_sleep(cid, gid, DEFENSE_TIME): return
    
    with bot_lock:
        g = games
        g = "confirming"
        g = {"yes": set(), "no": set()}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔥 إدانة", callback_data=f"cf_{cid}_y"),
           types.InlineKeyboardButton("🕊 براءة", callback_data=f"cf_{cid}_n"))
    safe_send(cid, "⚖️ <b>القرار النهائي للجمهور:</b>", reply_markup=mk)
    
    if not safe_sleep(cid, gid, CONFIRM_TIME): return
    resolve_confirm(cid, gid)

def resolve_confirm(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games
        sus = g if g.get("confirm_target") else g.get("defense_target")
        if not sus: return 
        yes = len(g)
        no = len(g)
        
    if yes > no:
        with bot_lock: kill_player(g, sus)
        pn = g
        pr = ROLE_DISPLAY.get(g, "?")
        safe_send(cid, f"🔥 <b>تم تنفيذ حكم الإعدام بحق {pn}.</b>\n\n🎭 اتضح أنه كان: {pr}")
        with bot_lock: transfer_radio(g, sus)
        
        # المجنون
        if g == "Psychopath":
            with bot_lock: bomb = g
            if bomb:
                safe_send(cid, f"🤡 <b>ضحكة هيستيرية تملأ المكان... المجنون ترك قنبلة قبل موته!</b>\n\n❓ {bomb}\n\nلديك {BOMB_TIME} ثانية لفك الشفرة والنجاة!")
                open_discussion(cid)
                with bot_lock: g = "bomb"
                
                t_end = time.time() + BOMB_TIME
                while time.time() < t_end:
                    time.sleep(1)
                    with bot_lock:
                        if g == "defused": break
                
                with bot_lock: phase = g
                if phase == "defused":
                    d_name = g]
                    safe_send(cid, f"✅ <b>توقف المؤقت! {d_name} تمكن من إبطال القنبلة بذكاء.</b>")
                else:
                    safe_send(cid, f"💥 <b>BOOM! المستشفى انهار فوق رؤوس الجميع.</b>\n\nالجواب الصحيح كان: {bomb}")
                    with bot_lock: g = "psycho"
                    show_results(cid, "🤡 جنون تام! المجنون فاز وحده من بين الركام.")
                    return

        if check_win_safe(cid, gid): return
    else:
        safe_send(cid, "🕊 <b>عفو عام... لقد تمت تبرئته بقرار الأغلبية.</b>")
    
    start_room_choosing(cid, gid)

@bot.callback_query_handler(func=lambda c: c.data.startswith("vote_"))
def cb_vote(call):
    uid = call.from_user.id
    try: cid, tid = int(call.data.split("_")), int(call.data.split("_"))
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "⛔", show_alert=True)
        g = games
        if g not in ("voting", "voting_active"): return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        if uid not in g or not g: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g: return bot.answer_callback_query(call.id, "✅", show_alert=True)
        g = tid
        if g == "Instigator": g = tid
        if g.get("joker_holder") == uid and g.get("joker_effect") == "double_vote": g = tid
    bot.answer_callback_query(call.id, "✅ سُجل صوتك")

@bot.callback_query_handler(func=lambda c: c.data.startswith("cf_"))
def cb_confirm(call):
    uid = call.from_user.id
    try: cid, ch = int(call.data.split("_")), call.data.split("_")
    except: return
    with bot_lock:
        if cid not in games or games != "confirming": return
        if uid not in games or not games: return
        if uid == games.get("defense_target"): return bot.answer_callback_query(call.id, "أنت المتهم! لا يحق لك التصويت هنا.", show_alert=True)
        
        cv = games
        cv.discard(uid); cv.discard(uid)
        if ch == "y": cv.add(uid)
        else: cv.add(uid)
        
        y, n = len(cv), len(cv)
        
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
        g = games
        
        if g == "night" and g.get(uid, {}).get("alive"):
            my_room = get_player_room(g, uid)
            if my_room:
                my_name = g
                if my_room == 5:
                    hall_players = get_room_players(g, 5)
                    for u in hall_players:
                        if u != uid: safe_pm(u, f"🌑 <b>{my_name} (من الممر المظلم):</b> {clean(text, 200)}")
                    corrupted = corrupt_text(text)
                    all_in_rooms =.items() if p and g.get(u) != 5]
                    for u in all_in_rooms:
                        safe_pm(u, f"👻 <b>(صوت خافت قادم من الممر):</b> {clean(corrupted, 200)}")
                else:
                    room_mates = get_room_players(g, my_room)
                    for u in room_mates:
                        if u != uid: safe_pm(u, f"🏠 <b>{my_name}:</b> {clean(text, 200)}")
                return

        if g == "Psychopath" and g.get("psycho_phase", {}).get(uid) == "q":
            g = clean(text, 100); g = "a"
            safe_pm(uid, "✅ <b>ممتاز!</b>\nالآن أرسل لي 'الجواب الصحيح' بكلمة أو جملة قصيرة لتكتمل الشفرة:"); return
        if g == "Psychopath" and g.get("psycho_phase", {}).get(uid) == "a":
            g = normalize_arabic(text); g = clean(text, 50); g = True; g = uid; g = "done"
            safe_pm(uid, "💣 <b>اكتمل الفخ!</b>\nقنبلتك جاهزة الآن. إذا أقنعتهم بإعدامك نهاراً، ستنفجر في وجوههم."); return
        if g.get("last_gasp_pending", {}).get(uid):
            g = clean(text, 3000); g = False
            safe_pm(uid, "🩸 تم تسطير كلماتك بدمائك."); return
        if g == "vote" and g == "waiting_q" and g.get("asker") == uid and g.get("ask_type_chosen"):
            g = clean(text, 200)
            if g == "vote": g = "voting_active"; send_vote_q(fc, uid, text)
            else: g = "answering"; send_qa_q(fc, uid, text)
            safe_pm(uid, "✅ تم عرض سؤالك أمام المجلس."); return
        if g == "vote" and g == "answering" and uid in g.get("qa_answer_pending", set()):
            g.remove(uid); g.add(uid)
            g = {"text": clean(text, 200), "reveal": None}
            mk = types.InlineKeyboardMarkup(); mk.add(types.InlineKeyboardButton("✅ بإسمي", callback_data=f"reveal_{fc}_y"), types.InlineKeyboardButton("🎭 مجهول", callback_data=f"reveal_{fc}_n"))
            safe_pm(uid, "✅ تم استلام حجتك. هل تريد عرضها بإسمك أم بشكل مجهول؟", reply_markup=mk); return

@bot.message_handler(commands=, chat_types=)
def cmd_radio(m):
    uid = m.from_user.id
    text = m.text.split(maxsplit=1)
    if len(text) < 2: return safe_pm(uid, "⚠️ أرسل رسالتك هكذا: /لاسلكي ثم النص")
    msg_content = text
    
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid: return
        g = games
        if uid not in g: return safe_pm(uid, "🚫 أنت لا تملك جهاز لاسلكي للاتصال به.")
        
        my_role = g
        my_name = g
        
        for holder in g:
            safe_pm(holder, f"📻 <b>لاسلكي ({my_name}):</b>\n\n{clean(msg_content, 200)}")

@bot.message_handler(commands=, chat_types=)
def cmd_check_cam(m):
    uid = m.from_user.id
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid: return
        g = games
        if g != "Security": return safe_pm(uid, "🚫 هذه الميزة متاحة لحارس الأمن فقط.")
        if uid in g: return safe_pm(uid, "🚫 لقد قمت بالتحقق من التسجيلات لهذه الليلة بالفعل.")
        
        last = g.get("observer_last_reveal")
        g.add(uid)
        
        if last: safe_pm(uid, f"📹 <b>تفقد كاميرات المراقبة:</b>\n\nآخر شخص راقبه المراقب (ربما يكون الجراح) يحمل دور: <b>{last}</b>")
        else: safe_pm(uid, "📹 <b>شاشة الكاميرا سوداء:</b>\n\nيبدو أن المراقب لم يقم بأي نشاط مؤخراً أو أنه ميت.")

def start_hospital(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games
        pp = g
        if len(pp) < MIN_HOSPITAL:
            safe_send(cid, f"⚠️ عدد المتواجدين غير كافٍ للبدء ({len(pp)}/{MIN_HOSPITAL}). تم إلغاء الجلسة.")
            force_cleanup(cid)
            return
        
        uids = list(pp.keys())
        random.shuffle(uids)
        roles = get_roles_for_count(len(uids))
        for i, uid in enumerate(uids):
            pp = roles
            g = ROLE_TEAM.get(roles, "good")
            if roles == "Anesthetist": g = 2; g.add(uid); g.add(uid)
            if roles == "Nurse": g = True
            if roles == "Surgeon": g = uid; g.add(uid); g.add(uid)
            if roles == "Security": g = 1
            
        g = "roles_reveal"
        g = time.time()
        gid = g

    safe_send(cid, "🏥 <b>تم إغلاق أبواب المستشفى وتوزيع المهام...</b>\n\nالظلام يخيّم والقتلة يتجولون الآن.")
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📂 استلام بطاقة الهوية", url=f"https://t.me/{BOT_USERNAME}?start=role_{cid}"))
    safe_send(cid, "اسحب بطاقتك وتعرف على دورك أدناه 👇", reply_markup=mk)
    
    if not safe_sleep(cid, gid, 10): return
    
    assign_joker(cid, gid)
    start_room_choosing(cid, gid)

def start_vote_game(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games
        if len(g) < MIN_VOTE:
            safe_send(cid, f"⚠️ العدد غير كافٍ ({len(g)}/{MIN_VOTE}).")
            force_cleanup(cid)
            return
        g = set()
        g = 0
        g = time.time()
        g = set()
        gid = g

    safe_send(cid, "🗳 <b>بدأت جلسة المجلس! جهزوا حججكم.</b>")
    if not safe_sleep(cid, gid, 2): return
    run_vote_round(cid, gid)

def run_vote_round(cid, gid):
    while True:
        with bot_lock:
            if not valid_game(cid, gid): return
            g = games
            avail = if u not in g]
            if not avail: break
            asker = random.choice(avail)
            g = asker
            g.add(asker)
            g = "waiting_q"
            g += 1
            rnd = g
        
        silence_all(cid)
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎤 استلام المنصة", url=f"https://t.me/{BOT_USERNAME}?start=ask_{cid}"))
        safe_send(cid, f"🎤 <b>الجولة {rnd}</b>: الكلمة الآن للمتحدث {g}", reply_markup=mk)
        
        t_end = time.time() + VOTE_GAME_ASK_TIME
        got_q = False
        while time.time() < t_end:
            time.sleep(1)
            with bot_lock:
                if not valid_game(cid, gid): return
                if g != "waiting_q":
                    got_q = True
                    break
        
        if not got_q:
            safe_send(cid, "⏰ انتهى وقت المتحدث ولم يطرح سؤالاً.")
            continue
            
        with bot_lock: p = g
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
        votes = games
    
    if not votes: safe_send(cid, "🤷 لا توجد أصوات.")
    else:
        counts = {}
        for v in votes.values(): counts = counts.get(v, 0) + 1
        res =[]
        for k, v in counts.items():
            name = games
            res.append(f"▫️ {name}: {v}")
        safe_send(cid, "🗳 <b>النتائج النهائية للتصويت:</b>\n\n" + "\n".join(res))

def _show_qa_round(cid, rnd, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        ans = games
        q = games
    
    txt = f"❓ <b>{q}</b>\n\n"
    for uid, data in ans.items():
        name = games if data else "🎭 مجهول"
        txt += f"🔹 {name}: {data}\n"
    safe_send(cid, txt)

def show_vote_game_end(cid, gid):
    safe_send(cid, "🏁 <b>تم رفع الجلسة وانتهاء اللعبة!</b>")
    force_cleanup(cid)

@bot.message_handler(commands=, chat_types=)
def start_pm(m):
    try:
        args = m.text.split()
        if len(args) > 1:
            param = args
            if param.startswith("room_"): dispatch_room(m.from_user.id, param)
            elif param.startswith("night_"): dispatch_night(m.from_user.id, param)
            elif param.startswith("joker_"): dispatch_joker(m.from_user.id, param)
            elif param.startswith("role_"): 
                cid = int(param.replace("role_", ""))
                if cid in games and m.from_user.id in games:
                    role = games
                    # ⚠️ التعديل الجذري: إرسال دليل مفصل عند أول استلام للدور
                    guide = ROLE_GUIDE.get(role, f"🎭 دورك: <b>{ROLE_DISPLAY.get(role, role)}</b>")
                    # رسالة توضيحية قصيرة 
                    short_guide = ROLE_GUIDE_SHORT.get(role, f"🎭 دورك: <b>{ROLE_DISPLAY.get(role, role)}</b>")
                    safe_pm(m.from_user.id, short_guide)
            elif param.startswith("ask_"):
                cid = int(param.replace("ask_", ""))
                with bot_lock:
                    if cid in games and games == m.from_user.id:
                        mk = types.InlineKeyboardMarkup()
                        mk.add(types.InlineKeyboardButton("تصويت مباشر", callback_data=f"asktype_{cid}_vote"),
                               types.InlineKeyboardButton("جلسة نقاش (سؤال وجواب)", callback_data=f"asktype_{cid}_qa"))
                        safe_pm(m.from_user.id, "كيف ترغب في إدارة جلستك؟", reply_markup=mk)
            return
    except: pass
    safe_pm(m.from_user.id, "🤖 أهلاً بك في عالم الغموض.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("asktype_"))
def cb_asktype(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, typ = int(parts), parts
    except: return
    with bot_lock:
        if cid not in games: return
        g = games
        if g.get("asker") != uid: return
        g = "vote" if typ == "vote" else "qa"
        g = True
    bot.answer_callback_query(call.id, "المنصة لك")
    try: bot.edit_message_text("✍️ <b>اكتب سؤالك أو موضوع النقاش الآن وإرسله:</b>", uid, call.message.message_id, parse_mode="HTML")
    except: pass

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def pm_handler_voting_q(m):
    uid = m.from_user.id
    text = m.text
    with bot_lock:
        cid = find_game_for_user(uid)
        if not cid or cid not in games: return
        g = games
        if g != "vote": return 
        
        if g == "waiting_q" and g.get("asker") == uid and g.get("ask_type_chosen"):
            g = clean(text, 200)
            if g == "vote": 
                g = "voting_active"
                send_vote_q(cid, uid, text)
            else: 
                g = "answering"
                send_qa_q(cid, uid, text)
            safe_pm(uid, "✅ تم إيصال رسالتك للمجلس.")
            return

        if g == "answering" and uid in g.get("players") and g:
            if uid not in g:
                g = {"text": clean(text, 200), "reveal": True} 
                safe_pm(uid, "✅ تم تدوين إجابتك.")
            return

def send_vote_q(cid, asker_id, text):
    with bot_lock:
        g = games
        alive =.items() if p]
    
    mk = types.InlineKeyboardMarkup()
    for u in alive:
        mk.add(types.InlineKeyboardButton(g, callback_data=f"vote_{cid}_{u}"))
    
    safe_send(cid, f"❓ <b>موضوع التصويت المطروح:</b>\n\n{text}\n\nأدلوا بأصواتكم الآن!", reply_markup=mk)

def send_qa_q(cid, asker_id, text):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✍️ تقديم حجة", url=f"https://t.me/{BOT_USERNAME}?start=v"))
    safe_send(cid, f"❓ <b>موضوع النقاش:</b>\n\n{text}\n\nاكتبوا ردودكم وأرسلوها عبر اللوحة أدناه.", reply_markup=mk)

# ══════════════ التشغيل ══════════════
print("Bot Started...")
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60, allowed_updates=)
    except Exception as e:
        print(f"Polling Crash: {e}")
        time.sleep(5)
