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

# ══════════════ سيرفر Render ══════════════
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
        server.serve_forever()
    except:
        pass

Thread(target=run_server, daemon=True).start()

# ══════════════ إعدادات البوت ══════════════
# ضع التوكن هنا
TOKEN = os.environ.get("BOT_TOKEN", "8300157614:AAEk9nvLXncrRtiQfZpCepl5J6T4TzD-siY")
OWNER_USERNAME = "O_SOHAIB_O"
OWNER_CHAT_ID = None
PUBLIC_GROUP_ID = -1002493822482

bot = telebot.TeleBot(TOKEN)
try:
    BOT_INFO = bot.get_me()
    BOT_ID = BOT_INFO.id
    BOT_USERNAME = BOT_INFO.username
except:
    pass

# ══════════════ الذاكرة ══════════════
games = {}
user_to_game = {}
bot_lock = threading.Lock()
wallets_db = {}
profiles_db = {}
# تم حذف whisper_db
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
LAST_GASP_TIME = 15
DISCUSS_TIME = 60
VOTE_TIME = 30
CONFIRM_TIME = 15
DEFENSE_TIME = 20
WILL_TIME = 30
BOMB_TIME = 20
ROOM_CHOOSE_TIME = 20

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
}

# ══════════════ الأصول ══════════════
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
}

ROLE_DESC = {
    "Surgeon": (
        "🔪 <b>الجرّاح</b>\n\n"
        "مشرطك هو الكلمة الأخيرة.\n"
        "كل ليلة تختار غرفة وتشطب اسماً فيها.\n\n"
        "⚡ إعدام لاعب كل ليلة\n"
        "🎯 لا تُبقِ شاهداً"
    ),
    "Anesthetist": (
        "💉 <b>المخدّر</b>\n\n"
        "إبرتك تُطفئ الوعي.\n"
        "إذا سقط الجرّاح… أنت التالي.\n\n"
        "⚡ شلّ قدرات لاعب (مرتان)\n"
        "🎯 احمِ الجرّاح أو خلّفه"
    ),
    "Instigator": (
        "🧠 <b>المحرّض</b>\n\n"
        "تسرق الأصوات وتزرع الفتنة.\n"
        "لا فريق لك… فقط الفوضى.\n\n"
        "⚡ سرقة صوت لاعب + صوتك مزدوج\n"
        "🎯 اقلب الطاولة واخرج حياً"
    ),
    "Psychopath": (
        "🤡 <b>المجنون</b>\n\n"
        "لا فريق لك. فقط الفوضى.\n"
        "جهّز اللغز… وإذا طردوك ينفجر الكل.\n\n"
        "⚡ قنبلة عند الطرد\n"
        "🎯 مُت مع الجميع أو عِش وحيداً"
    ),
    "Doctor": (
        "🩺 <b>الطبيب</b>\n\n"
        "يدك تُنقذ أو تقتل بالخطأ.\n"
        "كل ليلة تحمي واحداً في غرفتك.\n\n"
        "⚡ حماية لاعب كل ليلة (10% خطأ)\n"
        "🎯 أوقف النزيف"
    ),
    "Observer": (
        "👁 <b>المراقب</b>\n\n"
        "عيناك لا تغمض.\n"
        "كل ليلة تقرأ ملف شخص في غرفتك.\n\n"
        "⚡ كشف هوية لاعب\n"
        "🎯 افضح القتلة"
    ),
    "Swapper": (
        "🛏 <b>عابث الأسرّة</b>\n\n"
        "تُبدّل الأماكن في العتمة.\n"
        "الضربة تصيب غير المقصود.\n\n"
        "⚡ تبديل موقع لاعبين\n"
        "🎯 شتّت القتلة"
    ),
    "Patient": (
        "🤕 <b>المريض</b>\n\n"
        "لا شيء بيدك… إلا فرصة.\n"
        "اختر جثة وارتدِ وجهها.\n\n"
        "⚡ وراثة دور ميت (مرة واحدة)\n"
        "🎯 ابقَ حياً"
    ),
    "Screamer": (
        "😱 <b>المرعوب</b>\n\n"
        "رعبك رادارك.\n"
        "كل من يقترب ليلاً… تحسّ به.\n\n"
        "⚡ كشف الزوار تلقائياً\n"
        "🎯 افضح المتسللين"
    ),
    "Nurse": (
        "💊 <b>الممرّض</b>\n\n"
        "حقنة واحدة. إن أصبت شريراً يموت.\n"
        "إن أصبت بريئاً… تموت معه.\n\n"
        "⚡ تسميم لاعب في غرفتك\n"
        "🎯 طهّر المكان"
    ),
}

ROLE_TEAM = {
    "Surgeon": "evil", "Anesthetist": "evil",
    "Instigator": "neutral",
    "Doctor": "good", "Observer": "good", "Swapper": "good",
    "Patient": "good", "Psychopath": "psycho",
    "Screamer": "good", "Nurse": "good",
}

INSTANT_ROLES = {"Surgeon", "Doctor"}

ROLE_ACTION_MAP = {
    "Surgeon": "surgeon", "Doctor": "doctor", "Anesthetist": "anesthetist",
    "Observer": "observer", "Instigator": "instigator", "Swapper": "swapper",
    "Nurse": "nurse", "Patient": "patient",
}

SILENT_PHASES = {
    "night", "morning", "roles_reveal", "resolving",
    "waiting_q", "answering", "will_wait", "last_gasp_wait",
    "confirming", "defense", "qa_results", "ended",
    "room_choosing",
}

# ══════════════ رسائل سينمائية ══════════════
KILL_SCENES = [
    [
        "🌑 الساعة 3:00 صباحاً…",
        "🚶 خطوات خافتة في الممر…",
        "🚪 باب ينفتح ببطء…",
        "🔪 …",
        "💀 <b>{name}</b>… لن يستيقظ بعد الآن",
    ],
    [
        "🌑 صمت ثقيل يلفّ المستشفى…",
        "💨 نفَس دافئ خلف الرقبة…",
        "🔪 ومضة فضية في الظلام…",
        "💀 <b>{name}</b>… آخر ما رآه كان السقف",
    ],
    [
        "🌑 الممر الطويل… فارغ…",
        "👣 أو هكذا بدا…",
        "🔪 …",
        "💀 <b>{name}</b>… وُجد باردًا عند الفجر",
    ],
]

SAVE_SCENES = [
    [
        "🌑 الساعة 3:00 صباحاً…",
        "🚶 خطوات خافتة…",
        "🚪 الباب ينفتح…",
        "🔪 …",
        "🩺 لكن يداً أمسكت المشرط في آخر لحظة!",
        "✨ أحدهم… نجا بأعجوبة",
    ],
]

SURGEON_EXCUSES = [
    "🔪 <i>سقط المشرط من يده… ليلة فاشلة</i>",
    "🔪 <i>وجد نفسه يحدّق بالسقف… بلا حراك</i>",
    "🔪 <i>تاه في الممرات… ربما بقايا ضمير قديم</i>",
]

DOCTOR_SEDATED_MSG = "💉 <i>الطبيب غرق في سبات عميق… لا حماية الليلة</i>"

DOCTOR_FAIL_SCENES = [
    "💉💀 <i>ارتجفت يده… والحقنة أخطأت الوريد</i>",
    "🧪💀 <i>الدواء الخطأ… والصمت جاء سريعاً</i>",
    "😵💀 <i>لحظة سهو واحدة… وتوقف كل شيء</i>",
]

AFK_KILL_MESSAGES = [
    "💔 <b>{name}</b> لم يتحرك منذ زمن… وجدوه بلا نبض",
    "💔 <b>{name}</b> اختفى في صمت… كأنه لم يكن هنا",
]

TITLE_DEFS = {
    "chatterbox": {"icon": "🗣️", "name": "الثرثار", "desc": "أكثر واحد حكى"},
    "sherlock": {"icon": "🕵️", "name": "شارلوك", "desc": "صوّت على القاتل صح"},
    "silent": {"icon": "🤐", "name": "الصامت", "desc": "أقل واحد حكى"},
    "angel": {"icon": "😇", "name": "ملاك الرحمة", "desc": "الطبيب أنقذ"},
    "reaper": {"icon": "💀", "name": "حاصد الأرواح", "desc": "الجرّاح نجا للنهاية"},
    "first_blood": {"icon": "🩸", "name": "أول دم", "desc": "أول ضحية"},
    "survivor": {"icon": "🏆", "name": "الناجي", "desc": "بقي حياً"},
    "bomber": {"icon": "💣", "name": "المُفخّخ", "desc": "فجّر القنبلة"},
    "defuser": {"icon": "🔧", "name": "نازع الفتيل", "desc": "أبطل القنبلة"},
    "phantom": {"icon": "👻", "name": "الشبح", "desc": "ما أحد صوّت عليه"},
    "betrayed": {"icon": "🗡️", "name": "المطعون", "desc": "مات بالمشرط نهاراً"},
}

SHOP_ITEMS = {
    "shield": {"name": "🛡 درع الروح", "price": 120, "desc": "يحميك من الموت مرة واحدة ليلاً"},
    "spy_glass": {"name": "🔭 منظار", "price": 90, "desc": "يكشف فريق لاعب واحد نهاراً"},
    "file_gold": {"name": "📂 ملف ذهبي", "price": 180, "desc": "يكشف دور لاعب عشوائي"},
    "title_vip": {"name": "👑 لقب VIP", "price": 600, "desc": "تاج بجانب اسمك"},
}

MEDICAL_ITEMS = {
    "adrenaline": {"name": "💉 أدرينالين", "desc": "ينقذك من الموت تلقائياً مرة"},
    "scalpel": {"name": "🗡️ مشرط صدئ", "desc": "اطعن أحدهم نهاراً"},
    "detector": {"name": "🔍 كاشف كذب", "desc": "اكشف هوية شخص فوراً"},
}

JOKER_OPTIONS = {
    "cancel_vote": {"name": "🔄 إلغاء التصويت", "desc": "يُبطل نتيجة التصويت"},
    "shield_now": {"name": "🛡 حماية طارئة", "desc": "يحمي أي شخص فوراً لليلة"},
    "reveal_one": {"name": "👁 كشف فوري", "desc": "يكشف دور أي شخص"},
    "double_vote": {"name": "🗳 صوت مزدوج", "desc": "صوتك يُحسب مرتين"},
    "skip_night": {"name": "⏭ تخطّي ليلة", "desc": "الليلة تمر بلا أفعال"},
}

# ══════════════ أدوات مساعدة أساسية ══════════════
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
    if not t:
        return ""
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = re.sub(r'[^\w\s]', '', t.strip().lower())
    for a, b in [("[إأآاٱ]", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")]:
        t = re.sub(a, b, t)
    t = re.sub(r'[٠-٩]', lambda m: str("٠١٢٣٤٥٦٧٨٩".index(m.group())), t)
    return re.sub(r'\s+', ' ', t).strip()


# ══════════════ المحفظة والمتجر ══════════════
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


# ══════════════ البروفايل ══════════════
def get_profile(uid):
    if uid not in profiles_db:
        profiles_db[uid] = {
            "games": 0, "wins": 0, "losses": 0,
            "kills_as_surgeon": 0, "saves_as_doc": 0,
            "reveals_as_obs": 0, "bombs_triggered": 0,
            "deaths": 0, "messages_sent": 0,
            "best_streak": 0, "current_streak": 0,
            "vote_accuracy": [0, 0],
            "roles_played": {},
            "enemies": {},
            "titles_earned": [],
            "xp": 0,
        }
    return profiles_db[uid]

def add_xp(uid, amount):
    p = get_profile(uid)
    p["xp"] += amount

def get_rank(uid):
    xp = get_profile(uid)["xp"]
    if xp >= 10000:
        return "👑 ملك المستشفى"
    elif xp >= 5000:
        return "💎 أسطوري"
    elif xp >= 2000:
        return "🥇 خبير"
    elif xp >= 500:
        return "🥈 متمرّس"
    else:
        return "🥉 مبتدئ"

def update_hall(category, uid, value=1):
    if uid not in hall_of_fame[category]:
        hall_of_fame[category][uid] = 0
    hall_of_fame[category][uid] += value


# ══════════════ الإرسال الآمن ══════════════
def safe_send(cid, text, **kw):
    try:
        return bot.send_message(cid, text, parse_mode="HTML", **kw)
    except Exception as e:
        err = str(e).lower()
        if any(x in err for x in ["kicked", "not found", "deactivated"]):
            threading.Thread(target=force_cleanup, args=(cid,), daemon=True).start()
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

def safe_edit_markup(cid, mid, mk):
    try:
        return bot.edit_message_reply_markup(cid, mid, reply_markup=mk)
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


# ══════════════ الكتم ══════════════
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
        bot.restrict_chat_member(cid, uid,
            permissions=types.ChatPermissions(can_send_messages=False))
    except:
        pass

def unmute_player(cid, uid):
    try:
        bot.restrict_chat_member(cid, uid,
            permissions=types.ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True))
    except:
        pass

def silence_all(cid):
    mute_all(cid)
    with bot_lock:
        if cid not in games:
            return
        uids = list(games[cid]["players"].keys())
    for uid in uids:
        mute_player(cid, uid)

def open_discussion(cid):
    with bot_lock:
        if cid not in games:
            return
        dead_u = [u for u, p in games[cid]["players"].items() if not p["alive"]]
        alive_u = [u for u, p in games[cid]["players"].items() if p["alive"]]
    unmute_all(cid)
    time.sleep(0.3)
    for uid in alive_u:
        unmute_player(cid, uid)
    time.sleep(0.2)
    for uid in dead_u:
        mute_player(cid, uid)


# ══════════════ التنظيف الآمن ══════════════
_cleanup_lock = threading.Lock()

def force_cleanup(cid):
    with _cleanup_lock:
        with bot_lock:
            if cid not in games:
                return
            uids = list(games[cid]["players"].keys())
            for uid in uids:
                user_to_game.pop(uid, None)
            del games[cid]
        safe_unpin_all(cid)
        unmute_all(cid)
        for uid in uids:
            unmute_player(cid, uid)


# ══════════════ أدوات اللعبة ══════════════
def get_alive(cid):
    if cid not in games:
        return {}
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
    if not g["players"][uid]["alive"]:
        return False
    g["players"][uid]["alive"] = False
    if uid not in g["dead_list"]:
        g["dead_list"].append(uid)
    if not g["stats"]["first_death"]:
        g["stats"]["first_death"] = uid
    return True

def get_original_team(g, uid):
    ot = g.get("original_team", {})
    if uid in ot:
        return ot[uid]
    return ROLE_TEAM.get(g["players"][uid]["role"], "good")

def safe_sleep(cid, gid, seconds):
    end = time.time() + seconds
    while time.time() < end:
        time.sleep(min(1.0, end - time.time()))
        with bot_lock:
            if not valid_game(cid, gid):
                return False
    return True

def get_room_players(g, room_id, alive_only=True):
    result = {}
    for uid, p in g["players"].items():
        if alive_only and not p["alive"]:
            continue
        if g["room_choices"].get(uid) == room_id:
            result[uid] = p
    return result

def get_player_room(g, uid):
    return g["room_choices"].get(uid)

def get_room_targets(g, uid, exclude_self=True):
    room = get_player_room(g, uid)
    if not room:
        return {}
    players = get_room_players(g, room)
    if exclude_self:
        return {u: p for u, p in players.items() if u != uid}
    return players

def get_roles_for_count(n):
    n = max(n, 4)
    if n == 4:
        base = ["Surgeon", "Doctor", "Observer", "Patient"]
    elif n == 5:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist", "Patient"]
    elif n == 6:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist",
                random.choice(["Nurse", "Screamer"]), "Patient"]
    elif n == 7:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist",
                "Nurse", random.choice(["Psychopath", "Screamer"]), "Patient"]
    elif n == 8:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist",
                "Nurse", "Psychopath", "Screamer", "Patient"]
    elif n == 9:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist",
                "Nurse", "Psychopath", "Screamer", "Instigator", "Patient"]
    else:
        base = ["Surgeon", "Doctor", "Observer", "Anesthetist",
                "Nurse", "Psychopath", "Screamer", "Instigator", "Swapper"]
        while len(base) < n:
            base.append("Patient")
    random.shuffle(base)
    return base[:n]


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
        "bomb": {"is_set": False, "q": "", "a": "", "raw": "",
                 "defuser": None, "owner": None},
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
        "ask_prompt_sent": False, "ask_type": None,
        "ask_type_chosen": False,
        "qa_answers": {}, "qa_answer_pending": set(),
        "qa_answer_done": set(), "qa_current_round": 0,
        "afk_count": {}, "afk_warned": set(),
        "round_voted": set(), "round_night_acted": set(),
        "round_msg_count": {}, "round_complete_actions": set(),
        "med_items": {},
        "blackout_used": False, "blackout_active": False,
        "last_gasp_pending": {}, "last_gasp_text": {},
        "original_team": {},
        "evil_chat_ids": set(),
        "suspect_votes": {},
        "joker_holder": None, "joker_used": False,
        "joker_effect": None,
        "dramatic_vote_data": None,
        "stats": {
            "msg_count": {}, "first_death": None,
            "surgeon_uid": None,
            "voted_surgeon": set(), "doc_saves": 0,
            "doc_fails": 0,
            "bomb_exploded": False, "bomb_defuser": None,
            "scalpel_kills": set(), "voted_against": {},
            "rooms_history": [],
        },
        "pinned_mids": [],
        "winners_team": None,
    }


# ══════════════ نظام الفوز الذكي ══════════════
def _check_win_inner(cid):
    if cid not in games:
        return None
    g = games[cid]
    pp = g["players"]
    alive = {u: p for u, p in pp.items() if p["alive"]}

    if not alive:
        g["winners_team"] = None
        return "⚰️ <b>لا ناجين… المستشفى ابتلع الجميع</b>"

    evil_alive = [u for u in alive if get_original_team(g, u) == "evil"]
    good_alive = [u for u in alive if get_original_team(g, u) == "good"]
    psycho_alive = [u for u in alive if get_original_team(g, u) == "psycho"]
    neutral_alive = [u for u in alive if get_original_team(g, u) == "neutral"]

    total_alive = len(alive)

    if psycho_alive and not evil_alive and len(alive) <= 2:
        g["winners_team"] = "psycho"
        return "🤡 <b>المجنون يرقص فوق الجثث… وحيداً</b>"

    if not good_alive and not psycho_alive and not neutral_alive:
        g["winners_team"] = "evil"
        return "🔪 <b>الظلام ابتلع كل شيء… انتصر الأشرار</b>"

    if not evil_alive and not psycho_alive:
        g["winners_team"] = "good"
        return "🩺 <b>النور طهّر المستشفى… انتصر الأبرياء</b>"

    has_surgeon = any(pp[u]["role"] == "Surgeon" for u in evil_alive)
    has_anest = any(pp[u]["role"] == "Anesthetist" for u in evil_alive)
    has_active_killer = has_surgeon or has_anest
    has_doctor = any(pp[u]["role"] == "Doctor" for u in good_alive)

    if total_alive == 2 and has_surgeon and has_doctor:
        g["winners_team"] = "evil"
        return "🔪 <b>الجرّاح والطبيب وحدهما… المشرط أسرع من الشفاء</b>"

    if evil_alive and not has_active_killer:
        patient_can_inherit = any(
            pp[u]["role"] == "Patient" and u not in g.get("patient_used", set())
            for u in alive
        )
        dead_surgeon = any(
            pp[u]["role"] == "Surgeon" and not pp[u]["alive"]
            for u in pp
        )
        if not (patient_can_inherit and dead_surgeon):
            g["winners_team"] = "good"
            return "🩺 <b>سقط آخر قاتل… النور يسود</b>"

    non_evil = len(good_alive) + len(psycho_alive) + len(neutral_alive)
    if evil_alive and len(evil_alive) >= non_evil:
        g["winners_team"] = "evil"
        return "🔪 <b>الظلام يسيطر… الأشرار انتصروا</b>"

    if total_alive == 3 and len(evil_alive) == 1 and has_surgeon:
        if not has_doctor:
            g["winners_team"] = "evil"
            return "🔪 <b>لا طبيب… المشرط سيحسم كل شيء</b>"

    if total_alive == 2 and len(evil_alive) == 1:
        other = [u for u in alive if u not in evil_alive][0]
        other_role = pp[other]["role"]
        if other_role == "Nurse" and g.get("nurse_has_poison", {}).get(other, False):
            pass
        elif other_role == "Doctor" and has_surgeon:
            g["winners_team"] = "evil"
            return "🔪 <b>المشرط أسرع… الجرّاح ينتصر</b>"
        elif not has_surgeon and not has_anest:
            g["winners_team"] = "good"
            return "🩺 <b>الشرير بلا أنياب… النور ينتصر</b>"

    return None


def check_win_safe(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return True
        result = _check_win_inner(cid)
    if result:
        show_results(cid, result)
        return True
    return False


# ══════════════ حلقة اللعبة الرئيسية ══════════════
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
            safe_send(c, "🕯 <i>الصمت طال… تبخّر الجميع في الظلام</i>")
            force_cleanup(c)
        for c, t, gid in to_start:
            target = start_hospital if t == "hospital" else start_vote_game
            threading.Thread(target=target, args=(c, gid), daemon=True).start()

threading.Thread(target=game_loop, daemon=True).start()

# ══════════════ اللوبي ══════════════
MIN_HOSPITAL = 4
MIN_VOTE = 3

def build_lobby(cid):
    g = games[cid]
    rem = max(0, int(g["start_at"] - time.time()))
    total = max(g.get("total_wait", DEFAULT_WAIT_TIME), 1)
    gt = g["type"]
    pp = g["players"]
    n = len(pp)

    if gt == "hospital":
        mn = MIN_HOSPITAL
        title = "🏥 **المستشفى الملعون**"
        flavor_text = "الأبواب تصرّ... ورائحة المعقمات تختلط برائحة الدم القديم.\nالأسرّة باردة تنتظر أجساداً دافئة...\n\nهل تجرؤ على حجز مكانك؟"
    else:
        mn = MIN_VOTE
        title = "⚖️ **حلبة التصويت**"
        flavor_text = "المحكمة انعقدت... القاضي مجهول والجلاد بينكم.\nجهّز لسانك، فالحجة الضعيفة تعني الموت.\n\nمن سيخرج بريئاً؟"

    if n == 0:
        pt = "   👻 <i>المكان موحش وفارغ...</i>"
    else:
        lines = []
        for u, p in pp.items():
            rank = get_rank(u)
            lines.append(f"   🔹 {pname_vip(u, p['name'])}  {rank}")
        pt = "\n\n".join(lines)

    bar_f = int(min(max(rem / total, 0), 1.0) * 10)
    bar = "▓" * bar_f + "░" * (10 - bar_f)
    m, sc = divmod(max(0, rem), 60)
    ts = f"{m}:{sc:02d}" if m else f"{sc}s"

    return (
        f"{title}\n\n"
        f"⏳ {bar}  <b>{ts}</b>\n\n"
        f"<i>{flavor_text}</i>\n\n"
        f"👥 <b>الحاضرون ({n}):</b>\n\n{pt}\n\n"
        f"📌 الحد الأدنى: <b>{mn}</b> لاعبين\n\n"
        f"🚀 <code>/force_start</code>  ·  ⏱ <code>/time 30</code>"
    )

def join_markup(gid, gtype="hospital"):
    m = types.InlineKeyboardMarkup()
    if gtype == "hospital":
        btn_text = "🚪 احجز سريراً"
    else:
        btn_text = "🩸 ادخل الحلبة"
        
    m.add(types.InlineKeyboardButton(btn_text, callback_data=f"join_{gid}"))
    return m

def lobby_tick(cid, gid):
    resent = False
    while True:
        time.sleep(8)
        with bot_lock:
            if not valid_game(cid, gid) or games[cid]["phase"] != "joining":
                return
            rem = max(0, int(games[cid]["start_at"] - time.time()))
            gt = games[cid]["type"]

        if rem <= 25 and not resent:
            resent = True
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                txt = build_lobby(cid)
                mk = join_markup(gid, gt)
            asset = ASSETS["LOBBY"] if gt == "hospital" else ASSETS["VOTE"]
            try:
                if gt == "hospital":
                    nm = bot.send_animation(cid, asset, caption=txt,
                                            parse_mode="HTML", reply_markup=mk)
                else:
                    nm = bot.send_photo(cid, asset, caption=txt,
                                       parse_mode="HTML", reply_markup=mk)
            except:
                nm = safe_send(cid, txt, reply_markup=mk)
            if nm:
                with bot_lock:
                    if valid_game(cid, gid):
                        games[cid]["lobby_mid"] = nm.message_id
                        games[cid]["lobby_mt"] = "media"
            continue

        with bot_lock:
            if not valid_game(cid, gid) or games[cid]["phase"] != "joining":
                return
            txt = build_lobby(cid)
            gt = games[cid]["type"]
            mk = join_markup(games[cid]["game_id"], gt)
            mid = games[cid].get("lobby_mid")
            mt = games[cid].get("lobby_mt", "text")
        if mid:
            if mt == "media":
                safe_edit_caption(cid, mid, txt, reply_markup=mk)
            else:
                safe_edit_text(cid, mid, txt, reply_markup=mk)
        if rem <= 0:
            return


# ══════════════ الانضمام ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("join_"))
def cb_join(call):
    cid, uid = call.message.chat.id, call.from_user.id
    try:
        gid = int(call.data.split("_")[1])
    except:
        return
    with bot_lock:
        if not valid_game(cid, gid):
            return bot.answer_callback_query(call.id, "⛔ انتهت", show_alert=True)
        if games[cid]["phase"] != "joining":
            return bot.answer_callback_query(call.id, "⛔ بدأت بالفعل", show_alert=True)
        if uid in games[cid]["players"]:
            return bot.answer_callback_query(call.id, "✅ أنت مسجّل", show_alert=True)
        if len(games[cid]["players"]) >= MAX_PLAYERS:
            return bot.answer_callback_query(call.id, "⛔ الأسرّة ممتلئة", show_alert=True)
        ex = find_game_for_user(uid)
        if ex and ex != cid:
            return bot.answer_callback_query(call.id, "⛔ أنت في مستشفى آخر", show_alert=True)
            
        games[cid]["players"][uid] = {
            "name": clean_name(call.from_user.first_name),
            "role": "Patient", "alive": True
        }
        user_to_game[uid] = cid
        games[cid]["last_activity"] = time.time()
        cnt = len(games[cid]["players"])
        gt = games[cid]["type"]
        
    bot.answer_callback_query(call.id, f"✅ دخلت ({cnt})")
    with bot_lock:
        if not valid_game(cid, gid):
            return
        txt = build_lobby(cid)
        mk = join_markup(games[cid]["game_id"], gt)
        mid = games[cid].get("lobby_mid")
        mt = games[cid].get("lobby_mt", "text")
    if mid:
        if mt == "media":
            safe_edit_caption(cid, mid, txt, reply_markup=mk)
        else:
            safe_edit_text(cid, mid, txt, reply_markup=mk)


# ══════════════ فلترة رسائل المجموعة ══════════════
ALL_CONTENT = [
    'text', 'photo', 'sticker', 'video', 'voice', 'document',
    'animation', 'video_note', 'audio', 'poll', 'location',
    'contact', 'dice', 'venue', 'game',
]

@bot.message_handler(
    content_types=ALL_CONTENT,
    func=lambda m: m.chat.type in ("group", "supergroup") and m.chat.id in games and not (m.text or "").startswith("/")
)
def group_msg_filter(m):
    cid, uid = m.chat.id, m.from_user.id
    text = m.text or ""

    do_delete = False
    do_blackout = False
    blackout_text = ""

    with bot_lock:
        if cid not in games:
            return
        g = games[cid]
        phase = g["phase"]

        if phase == "bomb":
            if not is_participant(cid, uid) or not g["players"].get(uid, {}).get("alive", False):
                do_delete = True
            elif text:
                if normalize_arabic(text) == g["bomb"]["a"]:
                    g["phase"] = "defused"
                    g["bomb"]["defuser"] = uid
                else:
                    do_delete = True
            else:
                do_delete = True
            if do_delete:
                delete_msg(cid, m.message_id)
            return

        if phase == "defense":
            dt = g.get("defense_target")
            if uid == dt and g["players"].get(uid, {}).get("alive", False):
                g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                return
            else:
                do_delete = True

        if not do_delete and is_participant(cid, uid):
            p = g["players"].get(uid)
            if p and not p["alive"]:
                do_delete = True

        if not do_delete and phase in SILENT_PHASES:
            if is_participant(cid, uid):
                do_delete = True

        if not do_delete and phase == "discussion":
            if is_participant(cid, uid) and g["players"][uid]["alive"]:
                if text:
                    g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                    g["round_msg_count"][uid] = g["round_msg_count"].get(uid, 0) + 1
                if g.get("blackout_active", False):
                    do_blackout = True
                    blackout_text = text or "…"

        if not do_delete and not do_blackout and not m.text:
            if phase in SILENT_PHASES and is_participant(cid, uid):
                do_delete = True

    if do_delete:
        delete_msg(cid, m.message_id)
        return
    if do_blackout:
        delete_msg(cid, m.message_id)
        safe_send(cid, f"🔇 <i>همسة من الظلام:</i> {clean(blackout_text, 100)}")
        return


# ══════════════ مغادرة لاعب ══════════════
@bot.message_handler(content_types=['left_chat_member'],
                     func=lambda m: m.chat.type in ("group", "supergroup"))
def on_member_leave(m):
    if not m.left_chat_member:
        return
    uid = m.left_chat_member.id
    cid = m.chat.id
    with bot_lock:
        if cid not in games or uid not in games[cid]["players"]:
            return
        g = games[cid]
        if not g["players"][uid]["alive"]:
            return
        kill_player(g, uid)
        pn = pname(uid, g["players"][uid]["name"])
        rd = ROLE_DISPLAY.get(g["players"][uid]["role"], "?")
        user_to_game.pop(uid, None)
        gid = g["game_id"]
    safe_send(cid, f"🚪 {pn} غادر المستشفى…\n🎭 {rd}")
    check_win_safe(cid, gid)


# ══════════════ أوامر المجموعة (معالج واحد فقط) ══════════════
@bot.message_handler(
    func=lambda m: m.chat.type in ("group", "supergroup") and m.text and m.text.startswith("/")
)
def group_cmd(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split()[0].split("@")[0].lower()

    deletable = {"/hospital", "/vote", "/force_start", "/cancel",
                 "/done", "/time", "/suspect",
                 "/commands", "/hall", "/rooms_cancel"}
    if raw in deletable:
        delete_msg(cid, m.message_id)

    if raw == "/hospital":
        init_game(m, "hospital")
    elif raw == "/vote":
        init_game(m, "vote")
    elif raw == "/time":
        do_time(m)
    elif raw == "/force_start":
        do_force(m)
    elif raw in ("/cancel", "/done"):
        do_cancel(m)
    elif raw == "/suspect":
        do_suspect(m)
    elif raw == "/commands":
        do_commands(m)
    elif raw == "/hall":
        do_hall(m)
    elif raw == "/rooms_cancel":
        do_rooms_cancel(m)


# ══════════════ تنفيذ أوامر المجموعة ══════════════
def init_game(msg, gtype):
    cid = msg.chat.id
    uid = msg.from_user.id
    if msg.chat.type not in ("group", "supergroup"):
        return
    with bot_lock:
        if cid in games:
            return safe_send(cid, "⚠️ <i>المستشفى مشغول… اللعبة قائمة</i>")
        if len(games) >= MAX_GAMES:
            return safe_send(cid, "⚠️ <i>السيرفر ممتلئ… جرّب لاحقاً</i>")
    try:
        me = bot.get_chat_member(cid, BOT_ID)
        if me.status not in ['administrator', 'creator']:
            return safe_send(cid, "⚠️ <i>المستشفى يحتاج صلاحيات المشرف…</i>")
    except:
        return
    with bot_lock:
        if cid in games:
            return
        if find_game_for_user(uid):
            return safe_send(cid, "⚠️ <i>أنت محتجز في مستشفى آخر…</i>")
        gid = int(time.time() * 1000) % 2147483647
        games[cid] = new_game_data(gtype, uid, gid)
    txt = build_lobby(cid)
    mk = join_markup(gid, gtype)
    asset = ASSETS["LOBBY"] if gtype == "hospital" else ASSETS["VOTE"]
    try:
        if gtype == "hospital":
            m2 = bot.send_animation(cid, asset, caption=txt,
                                    parse_mode="HTML", reply_markup=mk)
        else:
            m2 = bot.send_photo(cid, asset, caption=txt,
                                parse_mode="HTML", reply_markup=mk)
    except:
        m2 = safe_send(cid, txt, reply_markup=mk)
    if m2:
        with bot_lock:
            if cid in games:
                games[cid]["lobby_mid"] = m2.message_id
                games[cid]["lobby_mt"] = "media"
    threading.Thread(target=lobby_tick, args=(cid, gid), daemon=True).start()


def do_time(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'):
                    return
            except:
                return
        try:
            s = int(m.text.split()[1]) if len(m.text.split()) > 1 else 30
            s = min(max(s, 10), 120)
            games[cid]["start_at"] += s
            r = int(games[cid]["start_at"] - time.time())
            games[cid]["total_wait"] = max(r, 1)
            games[cid]["last_activity"] = time.time()
        except:
            return


def do_force(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'):
                    return
            except:
                return
        games[cid]["start_at"] = time.time()


def do_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games:
            return
        is_auth = (games[cid]["host"] == uid)
    if not is_auth:
        try:
            is_auth = bot.get_chat_member(cid, uid).status in ['administrator', 'creator']
        except:
            pass
    if not is_auth:
        return
    safe_send(cid, "🛑 <b>أُغلق المستشفى… انتهى كل شيء</b>")
    force_cleanup(cid)


def do_rooms_cancel(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if games[cid]["host"] != uid:
            try:
                st = bot.get_chat_member(cid, uid).status
                if st not in ('administrator', 'creator'):
                    return
            except:
                return
        current = games[cid].get("rooms_enabled", True)
        games[cid]["rooms_enabled"] = not current
        new_state = games[cid]["rooms_enabled"]
    if new_state:
        safe_send(cid, "🏠 <i>نظام الغرف: مفعّل</i>")
    else:
        safe_send(cid, "🏠 <i>نظام الغرف: معطّل (الكل في غرفة واحدة)</i>")


# ══════════════ نظام الشك ══════════════
def do_suspect(m):
    cid, uid = m.chat.id, m.from_user.id
    
    # حذف الرسالة فوراً لزيادة التوتر
    delete_msg(cid, m.message_id)

    with bot_lock:
        if cid not in games or games[cid]["phase"] != "discussion":
            return
        if uid not in games[cid]["players"] or not games[cid]["players"][uid]["alive"]:
            return

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
                        except:
                            continue
            elif ent.type == "text_mention":
                target_uid = ent.user.id

    if not target_uid:
        return

    with bot_lock:
        if cid not in games or games[cid]["phase"] != "discussion":
            return
        if target_uid not in games[cid]["players"] or not games[cid]["players"][target_uid]["alive"]:
            return
        if target_uid == uid:
            return
        sv = games[cid].setdefault("suspect_votes", {})
        sv.setdefault(target_uid, set()).add(uid)


def show_suspect_bar(cid):
    with bot_lock:
        if cid not in games:
            return
        sv = games[cid].get("suspect_votes", {})
        if not sv:
            return
        pp = games[cid]["players"]
        lines = []
        sorted_sus = sorted(sv.items(), key=lambda x: len(x[1]), reverse=True)
        for t_uid, voters in sorted_sus[:5]:
            if t_uid not in pp:
                continue
            count = len(voters)
            bar = "🟥" * min(count, 5) + "⬜" * max(0, 5 - count)
            lines.append(f"  {pp[t_uid]['name']}: {bar} ({count})")
    if lines:
        safe_send(cid,
            "📊 <b>مقياس الشك:</b>\n\n" + "\n".join(lines))


# ══════════════ /commands ══════════════
def do_commands(m):
    cid = m.chat.id
    cmd_text = (
        "📖 <b>أوامر المستشفى الملعون</b>\n\n"
        "<code>/hospital</code> - المستشفى\n"
        "<code>/vote</code> - الحلبة\n"
        "<code>/force_start</code> - بدء\n"
        "<code>/time</code> - وقت\n"
        "<code>/cancel</code> - إلغاء\n"
        "<code>/rooms_cancel</code> - الغرف\n"
        "<code>/suspect</code> - شك\n"
        "<code>/kill</code> - قتل\n"
        "<code>/myrole</code> - دورك\n"
        "<code>/alive</code> - الأحياء\n"
        "<code>/roles</code> - الأدوار\n"
        "<code>/rules</code> - القواعد\n"
        "<code>/profile</code> - ملفك\n"
        "<code>/wallet</code> - محفظتك\n"
        "<code>/shop</code> - المتجر\n"
        "<code>/hall</code> - الشهرة\n"
    )
    safe_send(cid, cmd_text)


def do_hall(m):
    cid = m.chat.id
    lines = []

    def top_entry(cat, emoji, label):
        data = hall_of_fame.get(cat, {})
        if not data:
            return f"{emoji} {label}: <i>لا أحد بعد</i>"
        top_uid = max(data, key=data.get)
        try:
            user = bot.get_chat_member(cid, top_uid).user
            name = clean_name(user.first_name)
        except:
            name = str(top_uid)
        return f"{emoji} {label}: <b>{name}</b> ({data[top_uid]})"

    lines.append(top_entry("wins", "👑", "أكثر انتصارات"))
    lines.append(top_entry("surgeon_kills", "🔪", "أخطر جرّاح"))
    lines.append(top_entry("doc_saves", "🩺", "أفضل طبيب"))
    lines.append(top_entry("observer_reveals", "🕵️", "أذكى مراقب"))
    lines.append(top_entry("bombs", "🤡", "أكثر تفجير"))
    lines.append(top_entry("deaths", "💀", "أكثر موت"))
    lines.append(top_entry("messages", "🗣️", "أكثر ثرثرة"))

    safe_send(cid, "🏆 <b>جدار الشهرة</b>\n\n" + "\n\n".join(lines))

# ══════════════ اختيار الغرف ══════════════
def start_room_choosing(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        rooms_on = g.get("rooms_enabled", True)

    if not rooms_on:
        with bot_lock:
            if not valid_game(cid, gid):
                return
            g = games[cid]
            g["room_choices"] = {}
            for uid, p in g["players"].items():
                if p["alive"]:
                    g["room_choices"][uid] = 1
        start_night(cid, gid)
        return

    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        g["phase"] = "room_choosing"
        g["room_choices"] = {}
        g["room_chat_notified"] = set()
        g["last_activity"] = time.time()

    silence_all(cid)

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        "🏠 اختر غرفتك",
        url=f"https://t.me/{BOT_USERNAME}?start=room_{cid}"))

    safe_send(cid,
        f"🏠 <b>اختاروا غرفكم قبل حلول الظلام…</b>\n\n"
        f"  {ROOM_NAMES[1]}  ·  {ROOM_NAMES[2]}\n"
        f"  {ROOM_NAMES[3]}  ·  {ROOM_NAMES[4]}\n\n"
        f"<i>قدراتكم تعمل فقط على رفاق الغرفة\n"
        f"معكم {ROOM_CHOOSE_TIME} ثانية</i>",
        reply_markup=mk)

    if not safe_sleep(cid, gid, ROOM_CHOOSE_TIME):
        return

    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        for uid, p in g["players"].items():
            if p["alive"] and uid not in g["room_choices"]:
                g["room_choices"][uid] = random.randint(1, 4)

    show_room_map(cid, gid)
    notify_room_mates(cid, gid)

    if not safe_sleep(cid, gid, 2):
        return

    start_night(cid, gid)


def dispatch_room(uid, param):
    try:
        cid = int(param.replace("room_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫 المستشفى أُغلق…")
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return safe_pm(uid, "🚫 لست من نزلاء هذا المكان…")
        if g["phase"] != "room_choosing":
            return safe_pm(uid, "⏰ <i>فات وقت الاختيار…</i>")
        if uid in g["room_choices"]:
            chosen = g["room_choices"][uid]
            return safe_pm(uid, f"✅ اخترت <b>{ROOM_NAMES[chosen]}</b> بالفعل")

    mk = types.InlineKeyboardMarkup(row_width=2)
    for rid, rname in ROOM_NAMES.items():
        mk.add(types.InlineKeyboardButton(
            rname, callback_data=f"pickroom_{cid}_{rid}"))
    safe_pm(uid,
        "🏠 <b>اختر غرفتك لهذه الليلة…</b>\n\n"
        "<i>ستنام فيها وتستخدم قدرتك على رفاقها فقط</i>",
        reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("pickroom_"))
def cb_pickroom(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, rid = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g["phase"] != "room_choosing":
            return bot.answer_callback_query(call.id, "⏰ فات الوقت", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g["room_choices"]:
            return bot.answer_callback_query(call.id, "✅ اخترت بالفعل", show_alert=True)
        if rid not in ROOM_NAMES:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g["room_choices"][uid] = rid
        rname = ROOM_NAMES[rid]

    bot.answer_callback_query(call.id, f"✅ {rname}")
    try:
        bot.edit_message_text(
            f"✅ اخترت <b>{rname}</b>\n\n"
            f"<i>عندما يحلّ الظلام… ستعرف من معك</i>",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass


def show_room_map(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        lines = []
        for rid, rname in ROOM_NAMES.items():
            players_in = get_room_players(g, rid)
            if players_in:
                names = ", ".join([p["name"] for p in players_in.values()])
                lines.append(f"{rname}: {names}")
            else:
                lines.append(f"{rname}: <i>فارغة</i>")
        g["stats"]["rooms_history"].append(dict(g["room_choices"]))

    safe_send(cid,
        f"🗺 <b>خريطة الغرف</b>\n\n" +
        "\n".join(lines) +
        "\n\n<i>الظلام يحلّ… كلٌ في غرفته</i>")


def notify_room_mates(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        for rid in ROOM_NAMES:
            players_in = get_room_players(g, rid)
            if len(players_in) <= 1:
                for uid in players_in:
                    safe_pm(uid,
                        f"🏠 <b>{ROOM_NAMES[rid]}</b>\n\n"
                        f"<i>لا أحد معك في الغرفة… ليلة وحيدة</i>")
            else:
                for uid in players_in:
                    others = [pname(u, p["name"])
                             for u, p in players_in.items() if u != uid]
                    if others:
                        safe_pm(uid,
                            f"🏠 <b>{ROOM_NAMES[rid]}</b>\n\n"
                            f"معك في الغرفة:\n" +
                            "\n".join([f"  🔹 {o}" for o in others]) +
                            f"\n\n<i>يمكنكم التحدث هنا بالخاص أثناء الليل…</i>")


# ══════════════ الليل ══════════════
def start_night(cid, expected_gid):
    auto_send = []
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
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
        g["whisper_used"] = set()
        g["last_activity"] = time.time()
        rnd = g["round"]
        gid = g["game_id"]

        for uid, p in g["players"].items():
            if not p["alive"]:
                continue
            if p["role"] in INSTANT_ROLES:
                auto_send.append((uid, p["role"]))

    silence_all(cid)

    with bot_lock:
        if valid_game(cid, gid):
            for mid in list(games[cid].get("pinned_mids", [])):
                safe_unpin(cid, mid)
            games[cid]["pinned_mids"] = []

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        "🌑 تسلّل لمهمتك",
        url=f"https://t.me/{BOT_USERNAME}?start=night_{cid}"))

    try:
        bot.send_photo(cid, ASSETS["NIGHT"],
            caption=(
                f"🌑 <b>الليلة {rnd}</b>\n\n"
                f"<i>الظلام يغطّي الممرات… كلٌ في غرفته\n"
                f"معكم {NIGHT_TIME} ثانية</i>"),
            parse_mode="HTML", reply_markup=mk)
    except:
        safe_send(cid,
            f"🌑 <b>الليلة {rnd}</b>\n\n"
            f"<i>معكم {NIGHT_TIME} ثانية</i>",
            reply_markup=mk)

    for uid, role in auto_send:
        send_night_action(cid, uid, role)

    if not safe_sleep(cid, gid, NIGHT_TIME):
        return

    with bot_lock:
        if valid_game(cid, gid):
            for rid in ROOM_NAMES:
                players_in = get_room_players(games[cid], rid)
                if len(players_in) > 1:
                    for uid in players_in:
                        safe_pm(uid,
                            "🌅 <i>طلع الفجر… خرج الجميع من الغرفة</i>")

    with bot_lock:
        if not valid_game(cid, gid):
            return
        if games[cid]["round"] != rnd or games[cid]["phase"] != "night":
            return
    resolve_night(cid, rnd, gid)


# ══════════════ إرسال أفعال الليل ══════════════
def dispatch_night(uid, param):
    try:
        cid = int(param.replace("night_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫 المستشفى أُغلق…")
        g = games[cid]
        if uid not in g["players"]:
            return safe_pm(uid, "🚫 لست من نزلاء هذا المكان…")
        if not g["players"][uid]["alive"]:
            return safe_pm(uid, "💀 <i>الأموات لا يتسللون…</i>")
        if g["phase"] != "night":
            return safe_pm(uid, "☀️ <i>الشمس طالعة… انتظر الظلام</i>")
        if uid in g.get("night_acted", set()):
            return safe_pm(uid, "✅ <i>نفّذت مهمتك بالفعل</i>")
        if uid in g["sedated_current"]:
            return safe_pm(uid, "💉 <i>جسدك ثقيل… المخدّر أطفأ وعيك</i>")

        role = g["players"][uid]["role"]
        if role == "Psychopath":
            return safe_pm(uid, "🤡 <i>ليلتك هادئة… لحظتك عند المحرقة</i>")
        if role == "Screamer":
            return safe_pm(uid, "😱 <i>عيناك مفتوحتان تلقائياً… فقط راقب</i>")

        if role not in INSTANT_ROLES:
            an = g["ability_night"].get(uid, 999)
            if g["round"] < an:
                return safe_pm(uid, f"🔒 <i>قدرتك تستيقظ الليلة {an}… اصبر</i>")
            if role == "Anesthetist":
                if g["anesthetist_uses"].get(uid, 0) <= 0:
                    return safe_pm(uid, "💉 <i>نفدت إبرك…</i>")
            if role == "Nurse":
                if not g["nurse_has_poison"].get(uid, True):
                    return safe_pm(uid, "💊 <i>الحقنة فارغة…</i>")
            if role == "Patient":
                if uid in g.get("patient_used", set()):
                    return safe_pm(uid, "🚫 <i>استخدمت فرصتك الوحيدة</i>")
                dead = [(u, p) for u, p in g["players"].items()
                        if not p["alive"] and u != uid]
                if not dead:
                    return safe_pm(uid, "🚫 <i>لا جثث بعد… انتظر</i>")

    send_night_action(cid, uid, role)


def send_night_action(cid, uid, role):
    def room_btns(prefix, exclude_teams=None):
        with bot_lock:
            if cid not in games:
                return None
            g = games[cid]
            tgts = get_room_targets(g, uid)
            if exclude_teams:
                tgts = {u: p for u, p in tgts.items()
                       if get_original_team(g, u) not in exclude_teams}
        if not tgts:
            return None
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(*[types.InlineKeyboardButton(
            p["name"], callback_data=f"act_{cid}_{t}_{prefix}")
            for t, p in tgts.items()])
        return m

    prompts = {
        "Surgeon": "🔪 <b>من ينام للأبد في غرفتك الليلة؟</b>",
        "Doctor": "🩺 <b>من تحرسه من الظلام في غرفتك؟</b>",
        "Anesthetist": "💉 <b>من تُطفئ وعيه في غرفتك؟</b>",
        "Observer": "👁 <b>من تفتح ملفه في غرفتك؟</b>",
        "Instigator": "🧠 <b>من تسرق لسانه في غرفتك؟</b>",
        "Swapper": "🛏 <b>الطرف الأول… من تنقله؟</b>",
        "Nurse": "💊 <b>من تحقنه بالسم في غرفتك؟</b>",
    }

    if role == "Patient":
        with bot_lock:
            if cid not in games:
                return
            dead = [(u, p) for u, p in games[cid]["players"].items()
                    if not p["alive"] and u != uid and p["role"] != "Patient"]
        if not dead:
            return safe_pm(uid, "🚫 <i>لا جثث مناسبة…</i>")
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(
            f"💀 {p['name']} ({ROLE_DISPLAY.get(p['role'], '?')})",
            callback_data=f"act_{cid}_{u}_patient") for u, p in dead])
        safe_pm(uid, "🤕 <b>اختر جثة… وارتدِ وجهها</b>", reply_markup=mk)
        return

    if role == "Anesthetist":
        mk = room_btns("anesthetist", exclude_teams={"evil"})
        if not mk:
            return safe_pm(uid, "🚫 <i>لا أهداف في غرفتك… أو كلهم حلفاء</i>")
        with bot_lock:
            uses = games[cid]["anesthetist_uses"].get(uid, 0) if cid in games else 0
        safe_pm(uid, f"💉 <b>من تُطفئ وعيه؟</b> (بقي: {uses})", reply_markup=mk)
        return

    if role == "Swapper":
        with bot_lock:
            if cid not in games:
                return
            tgts = get_alive_except(cid, uid)
        if not tgts:
            return safe_pm(uid, "🚫 <i>لا أهداف…</i>")
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(
            p["name"], callback_data=f"act_{cid}_{t}_swapper")
            for t, p in tgts.items()])
        safe_pm(uid, prompts["Swapper"], reply_markup=mk)
        return

    if role == "Surgeon":
        mk = room_btns("surgeon", exclude_teams={"evil"})
        if not mk:
            return safe_pm(uid, "🚫 <i>لا ضحايا في غرفتك… أو كلهم حلفاء</i>")
        safe_pm(uid, prompts["Surgeon"], reply_markup=mk)
        return

    if role in prompts:
        action_key = ROLE_ACTION_MAP.get(role, role.lower())
        mk = room_btns(action_key)
        if not mk:
            return safe_pm(uid, "🚫 <i>لا أحد في غرفتك لتستهدفه…</i>")
        safe_pm(uid, prompts[role], reply_markup=mk)


# ══════════════ معالج أفعال الليل ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("act_"))
def cb_act(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, tid, act = int(parts[1]), int(parts[2]), parts[3]
    except:
        return

    edit_text = None
    send_swapper2 = False
    swapper2_others = {}

    with bot_lock:
        if cid not in games or games[cid]["phase"] != "night":
            return bot.answer_callback_query(call.id, "⏰ فات الوقت", show_alert=True)
        g = games[cid]
        pp = g["players"]
        if uid not in pp or not pp[uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)

        if act != "patient":
            if tid not in pp or not pp[tid]["alive"] or tid == uid:
                return bot.answer_callback_query(call.id, "❌ هدف غير صالح", show_alert=True)
        else:
            if tid not in pp or pp[tid]["alive"]:
                return bot.answer_callback_query(call.id, "❌ لازم يكون ميتاً", show_alert=True)

        role = pp[uid]["role"]
        tn = pp.get(tid, {}).get("name", "?")

        expected = "swapper" if act == "swapper2" else act
        allowed = ROLE_ACTION_MAP.get(role)
        if allowed != expected:
            return bot.answer_callback_query(call.id, "❌ ليس دورك", show_alert=True)
        if act != "swapper2" and uid in g.get("night_acted", set()):
            return bot.answer_callback_query(call.id, "✅ سبق ونفّذت", show_alert=True)

        if act not in ("swapper", "swapper2", "patient"):
            my_room = get_player_room(g, uid)
            target_room = get_player_room(g, tid)
            if my_room != target_room:
                return bot.answer_callback_query(call.id, "❌ ليس في غرفتك", show_alert=True)

        if act == "surgeon":
            if get_original_team(g, tid) == "evil":
                return bot.answer_callback_query(call.id, "❌ هذا حليفك… لا تقتله", show_alert=True)
            g["actions"]["surgeon"] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "doctor":
            g["actions"]["doctor"] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "anesthetist":
            uses = g["anesthetist_uses"].get(uid, 0)
            if uses <= 0:
                return bot.answer_callback_query(call.id, "❌ نفدت الإبر", show_alert=True)
            if get_original_team(g, tid) == "evil":
                return bot.answer_callback_query(call.id, "❌ هذا حليفك!", show_alert=True)
            g["sedated_current"].add(tid)
            g["anesthetist_uses"][uid] = uses - 1
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "instigator":
            g["instigator_steal"][uid] = tid
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "observer":
            g["observer_targets"][uid] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "swapper":
            g["swap_data"][uid] = {"first": tid}
            swapper2_others = {u: p for u, p in get_alive_except(cid, uid).items()
                              if u != tid}
            if swapper2_others:
                send_swapper2 = True
            else:
                return bot.answer_callback_query(call.id, "❌ ما في أحد ثاني", show_alert=True)

        elif act == "swapper2":
            if uid not in g["swap_data"] or "first" not in g["swap_data"][uid]:
                return bot.answer_callback_query(call.id, "❌", show_alert=True)
            if uid in g.get("night_acted", set()):
                return bot.answer_callback_query(call.id, "✅ سبق", show_alert=True)
            f1 = g["swap_data"][uid]["first"]
            g["swap_data"][uid]["second"] = tid
            g["screamer_visitors"].setdefault(f1, []).append(uid)
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)
            f1n = pp.get(f1, {}).get("name", "?")
            edit_text = f"🛏 تم التبديل: <b>{f1n}</b> ↔ <b>{tn}</b>"

        elif act == "nurse":
            if not g["nurse_has_poison"].get(uid, True):
                return bot.answer_callback_query(call.id, "❌ الحقنة فارغة", show_alert=True)
            g["nurse_poison"][uid] = tid
            g["screamer_visitors"].setdefault(tid, []).append(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)

        elif act == "patient":
            if uid in g.get("patient_used", set()):
                return bot.answer_callback_query(call.id, "❌ استخدمت فرصتك", show_alert=True)
            dr = pp[tid]["role"]
            if dr == "Patient":
                return bot.answer_callback_query(call.id, "❌ لا فائدة من وراثة مريض", show_alert=True)
            old_team = get_original_team(g, uid)
            g["original_team"][uid] = old_team
            pp[uid]["role"] = dr
            g["patient_used"].add(uid)
            g["night_acted"].add(uid)
            g["round_night_acted"].add(uid)
            g["ability_night"][uid] = g["round"] + 1
            if dr == "Nurse":
                g["nurse_has_poison"][uid] = True
            if dr == "Anesthetist":
                g["anesthetist_uses"][uid] = 2
                g["original_team"][uid] = "evil"
                g["evil_chat_ids"].add(uid)
            if dr == "Instigator":
                g["original_team"][uid] = "neutral"
            if dr == "Surgeon":
                g["stats"]["surgeon_uid"] = uid
                g["evil_chat_ids"].add(uid)
                g["original_team"][uid] = "evil"
            nd = ROLE_DISPLAY.get(dr, dr)
            edit_text = f"🤕 تحوّلت إلى <b>{nd}</b>… ابدأ من الليلة القادمة"

        else:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)

    if send_swapper2:
        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.add(*[types.InlineKeyboardButton(
            p["name"], callback_data=f"act_{cid}_{u}_swapper2")
            for u, p in swapper2_others.items()])
        bot.answer_callback_query(call.id, f"✅ {tn}")
        try:
            bot.edit_message_text(
                f"✅ الطرف الأول: <b>{tn}</b>\n\n🛏 <b>الطرف الثاني:</b>",
                uid, call.message.message_id, parse_mode="HTML",
                reply_markup=mk)
        except:
            pass
        return

    bot.answer_callback_query(call.id, "✅")
    final = edit_text or f"✅ <b>{tn}</b>… تم"
    try:
        bot.edit_message_text(final, uid, call.message.message_id,
                             parse_mode="HTML")
    except:
        pass


# ══════════════ الجوكر ══════════════
def assign_joker(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        alive = [u for u, p in g["players"].items() if p["alive"]]
        if not alive:
            return
        holder = random.choice(alive)
        g["joker_holder"] = holder
        g["joker_used"] = False

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        "🃏 افتح بطاقة الجوكر",
        url=f"https://t.me/{BOT_USERNAME}?start=joker_{cid}"))
    safe_pm(holder,
        "🃏 <b>بطاقة الجوكر وصلت!</b>\n\n"
        "<i>سلاح قوي… لكنه يكشف هويتك عند الاستخدام\n"
        "استخدمه بحكمة… مرة واحدة فقط</i>",
        reply_markup=mk)


def dispatch_joker(uid, param):
    try:
        cid = int(param.replace("joker_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫 المستشفى أُغلق…")
        g = games[cid]
        if g.get("joker_holder") != uid:
            return safe_pm(uid, "🚫 <i>ليست لك هذه البطاقة…</i>")
        if g.get("joker_used"):
            return safe_pm(uid, "🃏 <i>استخدمت بطاقتك بالفعل</i>")
        if g["phase"] not in ("discussion", "voting", "night"):
            return safe_pm(uid, "⏰ <i>ليس الوقت المناسب…</i>")

    mk = types.InlineKeyboardMarkup(row_width=1)
    for jk_id, jk in JOKER_OPTIONS.items():
        mk.add(types.InlineKeyboardButton(
            f"{jk['name']} — {jk['desc']}",
            callback_data=f"jkuse_{cid}_{jk_id}"))
    safe_pm(uid,
        "🃏 <b>اختر قوة الجوكر…</b>\n\n"
        "⚠️ <i>هويتك ستُكشف للجميع!</i>",
        reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("jkuse_"))
def cb_joker_use(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, jk_id = int(parts[1]), parts[2]
    except:
        return

    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g.get("joker_holder") != uid or g.get("joker_used"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if jk_id not in JOKER_OPTIONS:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)

        g["joker_used"] = True
        g["joker_effect"] = jk_id
        jk_name = JOKER_OPTIONS[jk_id]["name"]
        player_name = pname(uid, g["players"][uid]["name"])
        player_role = ROLE_DISPLAY.get(g["players"][uid]["role"], "?")
        gid = g["game_id"]

    bot.answer_callback_query(call.id, f"🃏 {jk_name}")
    try:
        bot.edit_message_text(
            f"🃏 <b>استخدمت: {jk_name}</b>",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass

    safe_send(cid,
        f"🃏 <b>بطاقة الجوكر!</b>\n\n"
        f"{player_name} استخدم <b>{jk_name}</b>\n"
        f"🎭 هويته: {player_role}")

    if jk_id == "cancel_vote":
        with bot_lock:
            if valid_game(cid, gid):
                if g["phase"] == "voting":
                    g["votes"] = {}
                    safe_send(cid, "🔄 <i>أُبطلت كل الأصوات!</i>")

    elif jk_id == "shield_now":
        with bot_lock:
            if not valid_game(cid, gid):
                return
            targets = get_alive_except(cid, uid)
        if targets:
            mk2 = types.InlineKeyboardMarkup(row_width=2)
            mk2.add(*[types.InlineKeyboardButton(
                p["name"], callback_data=f"jkshield_{cid}_{t}")
                for t, p in targets.items()])
            safe_pm(uid, "🛡 <b>من تحمي الليلة؟</b>", reply_markup=mk2)

    elif jk_id == "reveal_one":
        with bot_lock:
            if not valid_game(cid, gid):
                return
            targets = get_alive_except(cid, uid)
        if targets:
            mk2 = types.InlineKeyboardMarkup(row_width=2)
            mk2.add(*[types.InlineKeyboardButton(
                p["name"], callback_data=f"jkreveal_{cid}_{t}")
                for t, p in targets.items()])
            safe_pm(uid, "👁 <b>من تكشف دوره؟</b>", reply_markup=mk2)

    elif jk_id == "skip_night":
        with bot_lock:
            if valid_game(cid, gid) and g["phase"] == "night":
                g["actions"] = {}
                g["night_acted"] = set(pp for pp in g["players"])
                safe_send(cid, "⏭ <i>الليلة مرّت بسلام… لا أفعال</i>")


@bot.callback_query_handler(func=lambda c: c.data.startswith("jkshield_"))
def cb_joker_shield(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, tid = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if tid in g["players"] and g["players"][tid]["alive"]:
            g["actions"]["joker_shield"] = tid
            tn = g["players"][tid]["name"]
    bot.answer_callback_query(call.id, "✅")
    try:
        bot.edit_message_text(f"🛡 <b>{tn}</b> محمي الليلة",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("jkreveal_"))
def cb_joker_reveal(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, tid = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if tid in g["players"]:
            tr = ROLE_DISPLAY.get(g["players"][tid]["role"], "?")
            tn = g["players"][tid]["name"]
    bot.answer_callback_query(call.id, "👁")
    try:
        bot.edit_message_text(f"👁 <b>{tn}</b> → {tr}",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass
    safe_send(cid, f"👁 <b>الجوكر يكشف:</b> {pname(tid, tn)} → {tr}")

# ══════════════ نتائج الليل ══════════════
def resolve_night(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if g["round"] != expected_rnd or g["phase"] != "night":
            return
        g["phase"] = "morning"
        pp = g["players"]
        actions = g["actions"]
        sedated = g["sedated_current"]
        gid = g["game_id"]

        swaps = {}
        for uid, data in g["swap_data"].items():
            if uid in sedated:
                continue
            if "first" in data and "second" in data:
                a, b = data["first"], data["second"]
                if a in swaps or b in swaps:
                    continue
                if pp.get(a, {}).get("alive") and pp.get(b, {}).get("alive"):
                    swaps[a] = b
                    swaps[b] = a

        def sw(t):
            return swaps.get(t, t) if t else t

        g["silenced"] = set()
        for inst_uid, target in g["instigator_steal"].items():
            if inst_uid not in sedated and pp.get(target, {}).get("alive", False):
                g["silenced"].add(target)

        surgeon_uid = g["stats"].get("surgeon_uid")
        so = actions.get("surgeon")
        surgeon_missing = False
        surgeon_sedated = False
        if surgeon_uid and pp.get(surgeon_uid, {}).get("alive"):
            if surgeon_uid in sedated:
                so = None
                surgeon_sedated = True
            elif not so:
                surgeon_missing = True
        else:
            so = None
        surg_target = sw(so) if so else None
        if surg_target and surg_target == surgeon_uid:
            surg_target = None

        doctor_uid = next((u for u, p in pp.items()
                          if p["role"] == "Doctor" and p["alive"]), None)
        do_ = actions.get("doctor")
        doctor_missing = False
        doctor_sedated = False
        if doctor_uid:
            if doctor_uid in sedated:
                do_ = None
                doctor_sedated = True
            elif not do_:
                doctor_missing = True
        doc_target = sw(do_) if do_ else None

        joker_shield = actions.get("joker_shield")

        doctor_failed = False
        doc_fail_victim = None
        if doc_target and doc_target in pp and pp[doc_target]["alive"]:
            if random.random() < DOCTOR_FAIL_CHANCE:
                doctor_failed = True
                doc_fail_victim = doc_target

        surgeon_kill = None
        was_saved = False
        save_method = None

        if surg_target and surg_target in pp and pp[surg_target]["alive"]:
            if doctor_failed and doc_target == surg_target:
                doc_fail_victim = surg_target
                surgeon_kill = None
            elif doc_target == surg_target and not doctor_failed:
                was_saved = True
                save_method = "doctor"
                g["stats"]["doc_saves"] += 1
            elif joker_shield == surg_target:
                was_saved = True
                save_method = "joker"
            else:
                surgeon_kill = surg_target

        if surgeon_kill:
            if has_item(surgeon_kill, "shield"):
                use_item(surgeon_kill, "shield")
                surgeon_kill = None
                was_saved = True
                save_method = "shield"

        if doctor_failed and doc_fail_victim:
            med = g["med_items"].get(doc_fail_victim)
            if med and med["item"] == "adrenaline" and not med.get("used"):
                med["used"] = True
                doctor_failed = False
                doc_fail_victim = None

        if surgeon_kill:
            med = g["med_items"].get(surgeon_kill)
            if med and med["item"] == "adrenaline" and not med.get("used"):
                med["used"] = True
                surgeon_kill = None
                was_saved = True
                save_method = "adrenaline"

        nurse_results = []
        for nu, pt in g["nurse_poison"].items():
            if nu in sedated:
                continue
            if not pp.get(nu, {}).get("alive", False):
                continue
            actual = sw(pt)
            if actual == nu:
                continue
            if actual in pp and pp[actual]["alive"]:
                med_a = g["med_items"].get(actual)
                if med_a and med_a["item"] == "adrenaline" and not med_a.get("used"):
                    med_a["used"] = True
                    nurse_results.append({"nu": nu, "t": actual, "saved": True})
                elif has_item(actual, "shield"):
                    use_item(actual, "shield")
                    nurse_results.append({"nu": nu, "t": actual, "saved": True})
                else:
                    team = get_original_team(g, actual)
                    is_evil = team in ("evil", "psycho")
                    nurse_results.append({
                        "nu": nu, "t": actual,
                        "evil": is_evil, "saved": False
                    })

        observer_results = []
        for obs_uid, obs_target in g["observer_targets"].items():
            if obs_uid in sedated:
                observer_results.append({"uid": obs_uid, "sedated": True})
            else:
                actual_obs = sw(obs_target)
                if actual_obs in pp:
                    tr = pp[actual_obs]["role"]
                    td = ROLE_DISPLAY.get(tr, tr)
                    obs_tn = pp[actual_obs]["name"]
                    observer_results.append({
                        "uid": obs_uid, "sedated": False,
                        "name": obs_tn, "role": td,
                        "target": actual_obs
                    })

        real_visitors = {}
        for orig_target, visitor_list in g["screamer_visitors"].items():
            actual_target = sw(orig_target)
            real_visitors.setdefault(actual_target, []).extend(visitor_list)

        screams = []
        for uid_s, p_s in pp.items():
            if p_s["alive"] and p_s["role"] == "Screamer" and uid_s not in sedated:
                for v in real_visitors.get(uid_s, []):
                    if v in pp and v != uid_s:
                        screams.append({
                            "screamer": uid_s,
                            "visitor_name": pname(v, pp[v]["name"])
                        })

        doc_fail_name = pname(doc_fail_victim, pp[doc_fail_victim]["name"]) if doc_fail_victim else None
        doc_fail_role = ROLE_DISPLAY.get(pp[doc_fail_victim]["role"], "?") if doc_fail_victim else None
        surg_kill_name = pname(surgeon_kill, pp[surgeon_kill]["name"]) if surgeon_kill else None
        surg_kill_role = ROLE_DISPLAY.get(pp[surgeon_kill]["role"], "?") if surgeon_kill else None

    if not is_game_active(cid, gid):
        return

    try:
        morning_msg = bot.send_photo(cid, ASSETS["DAY"],
            caption="🌅 <b>الفجر يكشف ما خلّفه الظلام…</b>",
            parse_mode="HTML")
    except:
        morning_msg = safe_send(cid, "🌅 <b>طلع الفجر…</b>")

    if morning_msg:
        safe_pin(cid, morning_msg.message_id)
        with bot_lock:
            if valid_game(cid, gid):
                games[cid]["pinned_mids"].append(morning_msg.message_id)

    if not safe_sleep(cid, gid, 2):
        return

    if surgeon_sedated:
        safe_send(cid, "💉 <i>الجرّاح غرق في سبات… يده لم تتحرك الليلة</i>")
        if not safe_sleep(cid, gid, 1):
            return

    if doctor_sedated:
        safe_send(cid, DOCTOR_SEDATED_MSG)
        if not safe_sleep(cid, gid, 1):
            return

    if surgeon_missing and not surgeon_sedated:
        safe_send(cid, random.choice(SURGEON_EXCUSES))
        if not safe_sleep(cid, gid, 1):
            return

    if doctor_failed and doc_fail_victim:
        with bot_lock:
            if not valid_game(cid, gid):
                return
            kill_player(games[cid], doc_fail_victim)
            games[cid]["stats"]["doc_fails"] += 1
        mute_player(cid, doc_fail_victim)
        safe_send(cid,
            f"💉💀 <b>{doc_fail_name}</b>\n\n"
            f"<i>{random.choice(DOCTOR_FAIL_SCENES)}</i>\n\n"
            f"🎭 {doc_fail_role}")
        if not safe_sleep(cid, gid, 2):
            return

    if was_saved:
        scene = random.choice(SAVE_SCENES)
        for line in scene:
            if not is_game_active(cid, gid):
                return
            safe_send(cid, line)
            time.sleep(2)
        if not safe_sleep(cid, gid, 1):
            return

    if surgeon_kill:
        scene = random.choice(KILL_SCENES)
        for line in scene:
            if not is_game_active(cid, gid):
                return
            formatted = line.format(name=surg_kill_name) if "{name}" in line else line
            safe_send(cid, formatted)
            time.sleep(2)

        safe_send(cid, f"🎭 {surg_kill_role}")

        with bot_lock:
            if not valid_game(cid, gid):
                return
            kill_player(games[cid], surgeon_kill)
            games[cid]["last_gasp_pending"][surgeon_kill] = True
            games[cid]["phase"] = "last_gasp_wait"

        mute_player(cid, surgeon_kill)
        safe_pm(surgeon_kill,
            "🩸 <i>أنفاسك الأخيرة… اكتب حتى 5 كلمات الآن</i>")

        if not safe_sleep(cid, gid, LAST_GASP_TIME):
            return

        with bot_lock:
            if not valid_game(cid, gid):
                return
            gasp = games[cid]["last_gasp_text"].get(surgeon_kill)
            games[cid]["last_gasp_pending"][surgeon_kill] = False
            games[cid]["phase"] = "morning"

        if gasp:
            safe_send(cid, f"🩸 <i>همس قبل الرحيل:</i> «<b>{gasp}</b>»")
        else:
            safe_send(cid, "🩸 <i>…فتح فمه لكن لم يخرج صوت</i>")
        if not safe_sleep(cid, gid, 1):
            return

    elif not surgeon_missing and not surgeon_sedated and not doctor_failed and not was_saved:
        safe_send(cid, "✨ <i>ليلة هادئة… بلا دماء. لكن إلى متى؟</i>")
        if not safe_sleep(cid, gid, 1):
            return

    for res in nurse_results:
        if not is_game_active(cid, gid):
            return
        if res.get("saved"):
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                tn_ = pname(res["t"], games[cid]["players"][res["t"]]["name"])
            safe_send(cid, f"💊⚡ <i>وصل السم لـ {tn_}… لكن شيئاً أنقذه</i>")
            if not safe_sleep(cid, gid, 1):
                return
            continue

        nu, tgt, is_evil = res["nu"], res["t"], res["evil"]
        with bot_lock:
            if not valid_game(cid, gid):
                return
            pp2 = games[cid]["players"]
            if not pp2[tgt]["alive"]:
                continue
            tn_ = pname(tgt, pp2[tgt]["name"])
            nn_ = pname(nu, pp2[nu]["name"])
            tgt_role = ROLE_DISPLAY.get(pp2[tgt]["role"], "?")
            nu_role = ROLE_DISPLAY.get(pp2[nu]["role"], "?")
            kill_player(games[cid], tgt)
            if not is_evil:
                if pp2[nu]["alive"]:
                    kill_player(games[cid], nu)
                games[cid]["nurse_has_poison"][nu] = False
            else:
                games[cid]["nurse_has_poison"][nu] = True

        mute_player(cid, tgt)
        if not is_evil:
            mute_player(cid, nu)
            safe_send(cid,
                f"💊 <b>{tn_}</b> <i>سقط مسموماً</i>  ·  {tgt_role}\n\n"
                f"😢 <b>{nn_}</b> <i>لحق به ندماً…</i>  ·  {nu_role}")
        else:
            safe_send(cid, f"💊 <b>{tn_}</b> <i>سقط مسموماً</i>  ·  {tgt_role}")
            safe_pm(nu, "💊 <i>أصبت هدفاً شريراً… حقنتك عادت ممتلئة</i>")

        if not safe_sleep(cid, gid, 1):
            return

    if check_win_safe(cid, gid):
        return

    for s in screams:
        safe_pm(s["screamer"], f"😱 <i>أحسست بظل يقترب…</i> {s['visitor_name']}")

    for obs in observer_results:
        if obs["sedated"]:
            safe_pm(obs["uid"], "💉 <i>كل شيء ضبابي… المخدّر أعماك</i>")
        else:
            safe_pm(obs["uid"], f"👁 كشفت ملف <b>{obs['name']}</b> → {obs['role']}")
            prof = get_profile(obs["uid"])
            prof["reveals_as_obs"] = prof.get("reveals_as_obs", 0) + 1
            update_hall("observer_reveals", obs["uid"])

    with bot_lock:
        if valid_game(cid, gid):
            for uid_g, p_g in games[cid]["players"].items():
                if p_g["alive"] and has_item(uid_g, "file_gold"):
                    others = [u for u, p in games[cid]["players"].items()
                             if u != uid_g and p["alive"]]
                    if others:
                        ro = random.choice(others)
                        hr = ROLE_DISPLAY.get(games[cid]["players"][ro]["role"], "?")
                        hn = games[cid]["players"][ro]["name"]
                        use_item(uid_g, "file_gold")
                        safe_pm(uid_g,
                            f"📂✨ <i>الملف الذهبي يهمس:</i>\n"
                            f"<b>{hn}</b> هو {hr}")

    _try_promote_anesthetist(cid, gid)

    if expected_rnd > 1:
        afk_kills, afk_warnings = check_afk(cid)
        for uid_w in afk_warnings:
            safe_pm(uid_w,
                "⚠️ <b>تحذير!</b>\n\n"
                "<i>أنت على وشك الموت بسبب الخمول!\n"
                "تحدّث أو صوّت أو نفّذ مهمتك… وإلا ستسقط</i>")
        for uid_afk in afk_kills:
            if not is_game_active(cid, gid):
                return
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                name_afk = pname(uid_afk, games[cid]["players"][uid_afk]["name"])
                role_afk = ROLE_DISPLAY.get(games[cid]["players"][uid_afk]["role"], "?")
            mute_player(cid, uid_afk)
            safe_send(cid,
                random.choice(AFK_KILL_MESSAGES).format(name=name_afk) +
                f"\n🎭 {role_afk}")
            if not safe_sleep(cid, gid, 1):
                return

    if check_win_safe(cid, gid):
        return

    do_medical_drop(cid, gid)

    if not safe_sleep(cid, gid, 1):
        return

    start_discussion(cid, gid)


def _try_promote_anesthetist(cid, gid):
    promote_uid = None
    with bot_lock:
        if not valid_game(cid, gid):
            return
        gg = games[cid]
        surg_alive = any(p["alive"] and p["role"] == "Surgeon"
                        for p in gg["players"].values())
        if not surg_alive:
            for u, p in gg["players"].items():
                if p["alive"] and p["role"] == "Anesthetist":
                    p["role"] = "Surgeon"
                    gg["stats"]["surgeon_uid"] = u
                    promote_uid = u
                    break
    if promote_uid:
        safe_pm(promote_uid,
            "🔪 <i>سقط المعلّم… ورثت المشرط. أنت الجرّاح الآن</i>")


# ══════════════ AFK ══════════════
def check_afk(cid):
    afk_kills = []
    afk_warnings = []
    with bot_lock:
        if cid not in games:
            return [], []
        g = games[cid]
        pp = g["players"]

        for uid, p in pp.items():
            if not p["alive"]:
                continue
            night_acted = uid in g.get("round_complete_actions", set())
            voted = uid in g.get("round_voted", set())
            talked = g.get("round_msg_count", {}).get(uid, 0) > 0
            role = p["role"]
            has_night_role = role not in ("Psychopath", "Screamer", "Patient")
            if role == "Patient" and uid in g.get("patient_used", set()):
                has_night_role = False
            was_sedated = uid in g.get("sedated_current", set())
            was_silenced = uid in g.get("silenced", set())

            was_active = False
            if talked:
                was_active = True
            if voted and not was_silenced:
                was_active = True
            if night_acted and has_night_role:
                was_active = True
            if was_sedated:
                was_active = True
            if was_silenced and not has_night_role and not talked:
                was_active = True

            if was_active:
                g["afk_count"][uid] = 0
            else:
                g["afk_count"][uid] = g["afk_count"].get(uid, 0) + 1

            count = g["afk_count"].get(uid, 0)
            if count >= AFK_KILL_THRESHOLD:
                afk_kills.append(uid)
            elif count >= AFK_WARNING_THRESHOLD and uid not in g.get("afk_warned", set()):
                afk_warnings.append(uid)
                g["afk_warned"].add(uid)

        for uid in afk_kills:
            kill_player(g, uid)

        g["round_complete_actions"] = set(g.get("round_night_acted", set()))
        g["round_voted"] = set()
        g["round_night_acted"] = set()
        g["round_msg_count"] = {}

    return afk_kills, afk_warnings


# ══════════════ صندوق الإمداد ══════════════
def do_medical_drop(cid, gid):
    if random.random() > MEDICAL_DROP_CHANCE:
        return
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        alive = [u for u, p in g["players"].items()
                if p["alive"] and u not in g["med_items"]]
        if not alive:
            return
        lucky = random.choice(alive)
        item = random.choice(["adrenaline", "scalpel", "detector"])
        g["med_items"][lucky] = {"item": item, "used": False}
        ln = pname(lucky, g["players"][lucky]["name"])
        iname = MEDICAL_ITEMS[item]["name"]

    safe_send(cid, f"📦 <i>{ln} تعثّر بشيء غامض بين الركام…</i>")
    idesc = MEDICAL_ITEMS[item]["desc"]
    if item == "adrenaline":
        safe_pm(lucky,
            f"📦 وجدت <b>{iname}</b>\n<i>{idesc}</i>\n\n"
            f"💉 <i>يعمل تلقائياً عند الخطر</i>")
    else:
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            f"🔓 استخدم {iname}",
            callback_data=f"meduse_{cid}_{item}"))
        safe_pm(lucky, f"📦 وجدت <b>{iname}</b>\n<i>{idesc}</i>", reply_markup=mk)


# ══════════════ بدء المستشفى ══════════════
def start_hospital(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        pp = g["players"]
        if len(pp) < MIN_HOSPITAL:
            safe_send(cid, f"⚠️ <i>نحتاج {MIN_HOSPITAL} نزلاء على الأقل…</i>")
            force_cleanup(cid)
            return
        uids = list(pp.keys())
        random.shuffle(uids)
        roles = get_roles_for_count(len(uids))
        for i, uid in enumerate(uids):
            pp[uid]["role"] = roles[i]
            g["original_team"][uid] = ROLE_TEAM.get(roles[i], "good")
        for uid, p in pp.items():
            if p["role"] == "Anesthetist":
                g["anesthetist_uses"][uid] = 2
            if p["role"] == "Nurse":
                g["nurse_has_poison"][uid] = True
            if p["role"] == "Surgeon":
                g["stats"]["surgeon_uid"] = uid
            g["afk_count"][uid] = 0
            if p["role"] not in INSTANT_ROLES and p["role"] not in ("Psychopath", "Screamer"):
                g["ability_night"][uid] = 2
            prof = get_profile(uid)
            prof["roles_played"][p["role"]] = prof["roles_played"].get(p["role"], 0) + 1
        for uid, p in pp.items():
            if g["original_team"].get(uid) == "evil":
                g["evil_chat_ids"].add(uid)
        g["phase"] = "roles_reveal"
        g["game_started_at"] = time.time()
        gid = g["game_id"]

    # --- شرح سينمائي ---
    safe_send(cid,
        "📜 <b>بروتوكول النجاة</b>\n\n"
        "1️⃣ <b>الليل:</b> يذهب كلٌ إلى غرفته. القتلة يتسللون، والأطباء يحركون، والمراقبون يراقبون.\n"
        "2️⃣ <b>النهار:</b> تشرق الشمس لتكشف الضحايا. ناقشوا، ابحثوا عن الجرّاح، واستخدموا /suspect للشك.\n"
        "3️⃣ <b>التصويت:</b> ضعوا المتهم في القفص. إما أن يحترق أو يُعفى عنه.\n\n"
        "<i>البقاء للأذكى...</i>")
    time.sleep(3)

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📂 افتح ملفك السري",
        url=f"https://t.me/{BOT_USERNAME}?start=role_{cid}"))
    safe_send(cid, "📋 <b>وُزّعت الملفات السرية…</b>\n\n<i>كل واحد يكتشف مصيره من الزر… 👇</i>", reply_markup=mk)

    if not safe_sleep(cid, gid, 12):
        return

    with bot_lock:
        if not valid_game(cid, gid):
            return
        player_lines = [f"  🔹 {pname_vip(u, p['name'])}" for u, p in games[cid]["players"].items()]
        roles_in = [p["role"] for p in games[cid]["players"].values()]
        random.shuffle(roles_in)
        archive = [f"  ▫️ {ROLE_DISPLAY.get(r, r)}" for r in roles_in]

    safe_send(cid,
        f"🏥 <b>أُغلقت أبواب المستشفى</b>\n\n👥 النزلاء:\n\n" +
        "\n\n".join(player_lines) +
        f"\n\n🗂 <i>الأدوار المتاحة (مخلوطة):</i>\n\n" + "\n".join(archive))

    assign_joker(cid, gid)

    if not safe_sleep(cid, gid, 4):
        return

    start_room_choosing(cid, gid)


# ══════════════ dispatch_role ══════════════
def dispatch_role(uid, param):
    try:
        cid = int(param.replace("role_", ""))
    except:
        return
    with bot_lock:
        if cid not in games or uid not in games[cid]["players"]:
            return safe_pm(uid, "🚫 الباب مغلق… لست هنا")
        if uid in games[cid].get("role_revealed", set()):
            return safe_pm(uid, "📂 فتحت ملفك سابقاً")
        games[cid]["role_revealed"].add(uid)
        role = games[cid]["players"][uid]["role"]
        g = games[cid]
        team = get_original_team(g, uid)
        evil_teammates = []
        if team == "evil":
            for u2, p2 in g["players"].items():
                if u2 != uid and get_original_team(g, u2) == "evil" and p2["alive"]:
                    evil_teammates.append(pname(u2, p2["name"]))
            g["evil_chat_ids"].add(uid)

    desc = ROLE_DESC.get(role, "")
    team_label = {"evil": "🔴 فريق الظلام", "psycho": "🟡 مستقل",
                  "good": "🟢 فريق النور", "neutral": "⚪ محايد"}.get(team, "")
    safe_pm(uid, f"📂 <b>ملفك السري</b>\n\n{desc}\n\n🏷 {team_label}")

    if evil_teammates:
        time.sleep(1)
        teammates_txt = "\n".join([f"  🔴 {et}" for et in evil_teammates])
        safe_pm(uid, f"🌑 <b>رفاقك في الظلام:</b>\n\n{teammates_txt}\n\n<i>تتواصلون بالخاص أثناء الليل…</i>")

    if role == "Psychopath":
        with bot_lock:
            if cid in games:
                games[cid]["psycho_phase"][uid] = "q"
        time.sleep(1)
        safe_pm(uid, "🤡 <b>حان وقت التلغيم</b>\n\n✏️ أرسل <b>سؤال اللغز</b>… إذا أحرقوك سيحتاجون الجواب:")
        return

    if role not in INSTANT_ROLES and role not in ("Psychopath", "Screamer"):
        time.sleep(1)
        safe_pm(uid, "🎴 <i>قدرتك تستيقظ من الليلة الثانية… اصبر</i>")


# ══════════════ حلبة التصويت ══════════════
def start_vote_game(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if len(g["players"]) < MIN_VOTE:
            safe_send(cid, f"⚠️ <i>نحتاج {MIN_VOTE} لاعبين على الأقل…</i>")
            force_cleanup(cid)
            return
        g["asked_uids"] = set()
        g["vote_round"] = 0
        g["game_started_at"] = time.time()
        g["asked_uids_done"] = set()
        gid = g["game_id"]

    # --- شرح سينمائي ---
    safe_send(cid,
        "📜 <b>دستور الحلبة</b>\n\n"
        "1️⃣ <b>الميكروفون:</b> كل جولة يختار لاعب سؤالاً (تصويت أو سؤال وجواب).\n"
        "2️⃣ <b>التصويت:</b> اختاروا الشخص المناسب للسؤال.\n"
        "3️⃣ <b>الجواب:</b> اكتبوا أجوبتكم بالسر في الخاص.\n"
        "4️⃣ <b>النتائج:</b> نكشف الأوراق ونرى من يوافق من.\n\n"
        "<i>الجمهور لا يرحم...</i>")
    time.sleep(3)

    safe_send(cid, "🗳 <b>بدأت حلبة التصويت!</b>\n\n<i>كل لاعب يطرح سؤالاً بدوره…</i>")
    if not safe_sleep(cid, gid, 2):
        return
    run_vote_round(cid, gid)


def run_vote_round(cid, expected_gid):
    while True:
        with bot_lock:
            if not valid_game(cid, expected_gid):
                return
            g = games[cid]
            pp = g["players"]
            available = [u for u in pp if u not in g["asked_uids"]]
            if not available:
                break
            asker = random.choice(available)
            g["asker"] = asker
            g["asked_uids"].add(asker)
            g["phase"] = "waiting_q"
            g["vote_question"] = None
            g["votes"] = {}
            g["vote_round"] += 1
            g["last_activity"] = time.time()
            g["ask_prompt_sent"] = False
            g["ask_type"] = None
            g["ask_type_chosen"] = False
            g["qa_answers"] = {}
            g["qa_answer_pending"] = set()
            g["qa_answer_done"] = set()
            an = pname(asker, pp[asker]["name"])
            rnd = g["vote_round"]
            total = len(pp)
            g["qa_current_round"] = rnd
            gid = g["game_id"]

        silence_all(cid)

        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎤 استلم الميكروفون",
            url=f"https://t.me/{BOT_USERNAME}?start=ask_{cid}"))

        ask_msg = safe_send(cid,
            f"🎤 <b>الجولة {rnd}/{total}</b>  ·  {an}\n\n"
            f"<i>يختار سلاحه… معه {VOTE_GAME_ASK_TIME} ثانية</i>",
            reply_markup=mk)

        if ask_msg:
            with bot_lock:
                if valid_game(cid, gid):
                    games[cid]["ask_msg_id"] = ask_msg.message_id

        end_ask = time.time() + VOTE_GAME_ASK_TIME
        timed_out = False
        while time.time() < end_ask:
            time.sleep(1)
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                if games[cid]["phase"] != "waiting_q" or games[cid]["vote_round"] != rnd:
                    break
        else:
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                if games[cid]["phase"] == "waiting_q" and games[cid]["vote_round"] == rnd:
                    timed_out = True

        if timed_out:
            with bot_lock:
                if not valid_game(cid, gid):
                    return
                an2 = pname(asker, games[cid]["players"][asker]["name"])
            open_discussion(cid)
            safe_send(cid, f"⏰ <i>{an2} تجمّد أمام الميكروفون… مرّ دوره</i>")
            if not safe_sleep(cid, gid, 1):
                return
            continue

        with bot_lock:
            if not valid_game(cid, gid):
                return
            current_phase = games[cid]["phase"]
            current_rnd = games[cid]["vote_round"]

        if current_phase == "voting_active" and current_rnd == rnd:
            if not safe_sleep(cid, gid, VOTE_GAME_VOTE_TIME):
                return
            _tally_vote_round(cid, rnd, gid)
        elif current_phase == "answering" and current_rnd == rnd:
            if not safe_sleep(cid, gid, VOTE_GAME_ANSWER_TIME):
                return
            _show_qa_round(cid, rnd, gid)
        else:
            continue

        with bot_lock:
            if not valid_game(cid, gid):
                return
            is_last = len(games[cid]["asked_uids"]) >= len(games[cid]["players"])

        if is_last:
            break

        with bot_lock:
            if valid_game(cid, gid):
                games[cid]["phase"] = "vote_discuss"
        open_discussion(cid)
        safe_send(cid, f"💬 <i>استراحة نقاش… معكم {VOTE_GAME_DISCUSS_TIME} ثانية</i>")
        if not safe_sleep(cid, gid, VOTE_GAME_DISCUSS_TIME):
            return

    show_vote_game_end(cid, expected_gid)


def _tally_vote_round(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if g["phase"] != "voting_active" or g["vote_round"] != expected_rnd:
            return
        votes = g["votes"]
        pp = g["players"]
        voted_uids = {k for k in votes if isinstance(k, int)}
        no_vote = [pname(u, pp[u]["name"]) for u in pp if u not in voted_uids]
        if not votes:
            has_votes = False
            result_lines = []
        else:
            has_votes = True
            counts = {}
            for v in votes.values():
                counts[v] = counts.get(v, 0) + 1
            sr = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            medals = ["🥇", "🥈", "🥉"]
            result_lines = []
            for i, (uid_r, cnt) in enumerate(sr):
                n = pname(uid_r, pp[uid_r]["name"]) if uid_r in pp else "?"
                m = medals[i] if i < 3 else f"  {i+1}."
                result_lines.append(f"  {m}  {n}  ·  <b>{cnt}</b> صوت")
        g["phase"] = "vote_results"

    if not has_votes:
        msg = "🤷 <i>لم يصوّت أحد…</i>"
    else:
        msg = "🗳 <b>النتائج:</b>\n\n" + "\n\n".join(result_lines)
    if no_vote:
        msg += "\n\n❌ لم يصوّتوا: " + " · ".join(no_vote)
    safe_send(cid, msg)


def _show_qa_round(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if g["phase"] != "answering" or g["vote_round"] != expected_rnd:
            return
        pp = g["players"]
        answers = g.get("qa_answers", {})
        question = g.get("vote_question", "")
        asker_uid = g.get("asker")
        an = pname(asker_uid, pp[asker_uid]["name"]) if asker_uid and asker_uid in pp else "?"
        rnd = g["vote_round"]
        total = len(pp)
        revealed = []
        anon = []
        no_answer = []
        for uid_a, p in pp.items():
            if uid_a == asker_uid:
                continue
            if uid_a in answers:
                a = answers[uid_a]
                if a.get("reveal"):
                    revealed.append(f"🔹 {pname(uid_a, p['name'])}: \"{a['text']}\"")
                else:
                    anon.append(f"🎭: \"{a['text']}\"")
            else:
                no_answer.append(pname(uid_a, p["name"]))
        all_lines = revealed + anon
        random.shuffle(all_lines)
        g["phase"] = "qa_results"

    header = f"📝 <b>الجولة {rnd}/{total}</b>\n❓ «{question}»\n\n"
    if all_lines:
        header += "\n\n".join(all_lines)
    else:
        header += "<i>لا أحد أجاب…</i>"
    if no_answer:
        header += "\n\n❌ لم يجيبوا: " + " · ".join(no_answer)
    safe_send(cid, header)


def show_vote_game_end(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            safe_send(cid, "🏁 <b>انتهت الحلبة</b>")
            return
        g = games[cid]
        elapsed = int(time.time() - g.get("game_started_at", time.time()))
        em, es = divmod(elapsed, 60)
        n = len(g["players"])
        player_lines = [f"  🔹 {pname_vip(u, p['name'])}" for u, p in g["players"].items()]
        for uid in g["players"]:
            add_coins(uid, LOSE_REWARD)
            add_xp(uid, 5)

    safe_send(cid,
        f"🏁 <b>انتهت حلبة التصويت</b>\n\n👥 المشاركون ({n}):\n\n" +
        "\n\n".join(player_lines) +
        f"\n\n⏱ {em}:{es:02d}\n💰 كل مشارك حصل على +{LOSE_REWARD} 🪙\n\n🔄 /vote  ·  /hospital")
    force_cleanup(cid)


def send_vote_q(cid, asker_uid, question):
    with bot_lock:
        if cid not in games:
            return
        g = games[cid]
        an = pname(asker_uid, g["players"][asker_uid]["name"])
        rnd = g["vote_round"]
        total = len(g["players"])
        old_mid = g.get("ask_msg_id")
        g.setdefault("asked_uids_done", set()).add(asker_uid)
    if old_mid:
        safe_edit_text(cid, old_mid, f"🎤 {rnd}/{total} · {an} ✅")
    open_discussion(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🗳 صوّت الآن", url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))
    safe_send(cid,
        f"🗳 <b>الجولة {rnd}/{total}</b>\n\n🎤 {an} يسأل:\n❓ «<b>{question}</b>»\n\n"
        f"<i>صوّتوا على شخص! معكم {VOTE_GAME_VOTE_TIME} ثانية</i>", reply_markup=mk)


def send_qa_q(cid, asker_uid, question):
    with bot_lock:
        if cid not in games:
            return
        g = games[cid]
        an = pname(asker_uid, g["players"][asker_uid]["name"])
        rnd = g["vote_round"]
        total = len(g["players"])
        old_mid = g.get("ask_msg_id")
        g.setdefault("asked_uids_done", set()).add(asker_uid)
    if old_mid:
        safe_edit_text(cid, old_mid, f"🎤 {rnd}/{total} · {an} ✅")
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✏️ أجب في الخاص", url=f"https://t.me/{BOT_USERNAME}?start=answer_{cid}"))
    safe_send(cid,
        f"❓ <b>الجولة {rnd}/{total}</b>\n\n🎤 {an} يسأل:\n❓ «<b>{question}</b>»\n\n"
        f"<i>أجيبوا في الخاص! معكم {VOTE_GAME_ANSWER_TIME} ثانية</i>", reply_markup=mk)


# ══════════════ الألقاب والنتائج ══════════════
def calc_titles(cid):
    titles = {}
    with bot_lock:
        if cid not in games:
            return {}
        g = games[cid]
        pp = g["players"]
        stats = g["stats"]
        alive = {u: p for u, p in pp.items() if p["alive"]}
        mc = stats.get("msg_count", {})
        if mc:
            top_talker = max(mc, key=mc.get)
            if mc[top_talker] > 0:
                titles.setdefault(top_talker, []).append("chatterbox")
        all_players = list(pp.keys())
        if all_players:
            min_talk = min(all_players, key=lambda u: mc.get(u, 0))
            if mc.get(min_talk, 0) <= 2:
                titles.setdefault(min_talk, []).append("silent")
        vs = stats.get("voted_surgeon", set())
        surg_uid = stats.get("surgeon_uid")
        if vs and surg_uid and not pp.get(surg_uid, {}).get("alive", True):
            for det in vs:
                titles.setdefault(det, []).append("sherlock")
        if stats.get("doc_saves", 0) > 0:
            doc_uid = next((u for u, p in pp.items() if p["role"] == "Doctor"), None)
            if doc_uid:
                titles.setdefault(doc_uid, []).append("angel")
        if surg_uid and surg_uid in alive:
            titles.setdefault(surg_uid, []).append("reaper")
        fd = stats.get("first_death")
        if fd and fd in pp:
            titles.setdefault(fd, []).append("first_blood")
        for u in alive:
            titles.setdefault(u, []).append("survivor")
        if stats.get("bomb_exploded"):
            psycho_uid = next((u for u, p in pp.items() if p["role"] == "Psychopath"), None)
            if psycho_uid:
                titles.setdefault(psycho_uid, []).append("bomber")
        bd = stats.get("bomb_defuser")
        if bd and bd in pp:
            titles.setdefault(bd, []).append("defuser")
        voted_target_uids = set(stats.get("voted_against", {}).keys())
        for u in pp:
            if u not in voted_target_uids:
                titles.setdefault(u, []).append("phantom")
        for u in stats.get("scalpel_kills", set()):
            if u in pp:
                titles.setdefault(u, []).append("betrayed")
    return titles


def show_results(cid, winner_msg):
    titles_map = calc_titles(cid)
    lines = []
    title_lines = []
    reward_lines = []

    with bot_lock:
        if cid not in games:
            safe_send(cid, winner_msg)
            return
        g = games[cid]
        pp = g["players"]
        elapsed = int(time.time() - g.get("game_started_at", time.time()))
        em, es = divmod(elapsed, 60)
        ac = len([p for p in pp.values() if p["alive"]])
        dc = len([p for p in pp.values() if not p["alive"]])
        winners_team = g.get("winners_team")
        order = {"evil": 1, "psycho": 2, "neutral": 3, "good": 4}
        sp = sorted(pp.items(), key=lambda x: order.get(get_original_team(g, x[0]), 4))

        for uid, p in sp:
            rd = ROLE_DISPLAY.get(p["role"], p["role"])
            team = get_original_team(g, uid)
            ti = {"evil": "🔴", "psycho": "🟡", "good": "🟢", "neutral": "⚪"}.get(team, "⚪")
            st = "💀" if not p["alive"] else "✅"
            player_titles = titles_map.get(uid, [])
            title_icons = ""
            if player_titles:
                title_icons = " " + " ".join([TITLE_DEFS[t]["icon"] for t in player_titles if t in TITLE_DEFS])
            lines.append(f"  {ti}  {st}  {pname(uid, p['name'])}  ·  {rd}{title_icons}")

        for uid, p in pp.items():
            team = get_original_team(g, uid)
            is_winner = False
            if winners_team == "psycho" and p["role"] == "Psychopath":
                is_winner = True
            elif winners_team == "neutral" and team == "neutral":
                is_winner = True
            elif winners_team and team == winners_team:
                is_winner = True
            if team == "neutral" and p["alive"]:
                is_winner = True

            reward = WIN_REWARD if is_winner else LOSE_REWARD
            xp_gain = 20 if is_winner else 5
            player_titles = titles_map.get(uid, [])
            if "sherlock" in player_titles or "reaper" in player_titles:
                reward += MVP_BONUS
                xp_gain += 10
            
            add_coins(uid, reward)
            add_xp(uid, xp_gain)
            prof = get_profile(uid)
            prof["games"] += 1
            if is_winner:
                prof["wins"] += 1
                prof["current_streak"] += 1
                prof["best_streak"] = max(prof["best_streak"], prof["current_streak"])
                update_hall("wins", uid)
            else:
                prof["losses"] += 1
                prof["current_streak"] = 0
            if not p["alive"]:
                prof["deaths"] += 1
                update_hall("deaths", uid)
            prof["messages_sent"] += g["stats"]["msg_count"].get(uid, 0)
            update_hall("messages", uid, g["stats"]["msg_count"].get(uid, 0))
            for t_id in titles_map.get(uid, []):
                if t_id not in prof["titles_earned"]:
                    prof["titles_earned"].append(t_id)
            if p["role"] == "Surgeon":
                kills = len([d for d in g["dead_list"] if d != uid and g["stats"].get("surgeon_uid") == uid])
                prof["kills_as_surgeon"] += kills
                update_hall("surgeon_kills", uid, kills)
            if p["role"] == "Doctor":
                prof["saves_as_doc"] += g["stats"].get("doc_saves", 0)
                update_hall("doc_saves", uid, g["stats"].get("doc_saves", 0))
            if p["role"] == "Psychopath" and g["stats"].get("bomb_exploded"):
                prof["bombs_triggered"] += 1
                update_hall("bombs", uid)
            emoji = "🏆" if is_winner else "💫"
            reward_lines.append(f"  {emoji} {p['name']}: +{reward} 🪙")

        for uid, t_list in titles_map.items():
            if uid in pp:
                pn = pp[uid]["name"]
                for t_id in t_list:
                    td = TITLE_DEFS.get(t_id)
                    if td:
                        title_lines.append(f"  {td['icon']}  <b>{td['name']}</b>  ←  {pname(uid, pn)}")

    safe_send(cid,
        f"{winner_msg}\n\n{'━' * 20}\n\n" + "\n\n".join(lines) +
        f"\n\n{'━' * 20}\n\n✅ أحياء: {ac}  ·  💀 ضحايا: {dc}  ·  ⏱ {em}:{es:02d}\n\n"
        f"🔄 /hospital  ·  /vote")

    if title_lines:
        time.sleep(1)
        safe_send(cid, "🏅 <b>ألقاب هذه الجولة</b>\n\n" + "\n\n".join(title_lines))

    if reward_lines:
        time.sleep(1)
        safe_send(cid, "💰 <b>المكافآت</b>\n\n" + "\n\n".join(reward_lines))

    force_cleanup(cid)


# ══════════════ أوامر الخاص ══════════════
@bot.message_handler(commands=['start'], chat_types=['private'])
def cmd_start(m):
    global OWNER_CHAT_ID
    uid = m.from_user.id
    uname = m.from_user.username or ""
    if uname.lower() == OWNER_USERNAME.lower():
        OWNER_CHAT_ID = uid

    param = m.text.split()[1] if len(m.text.split()) > 1 else ""

    if not param:
        wallet = get_wallet(uid)
        rank = get_rank(uid)
        safe_pm(uid,
            f"🏥 <b>المستشفى الملعون</b>\n\n<i>بين الجدران البيضاء… القتلة يرتدون الأبيض</i>\n\n"
            f"🏥 /hospital — افتح أبواب المستشفى\n🗳 /vote — حلبة التصويت\n"
            f"📜 /roles — ملفات الأدوار\n📖 /rules — كيف تنجو\n"
            f"🎭 /myrole — دورك\n🟢 /alive — الأحياء\n📊 /profile — ملفك\n"
            f"💰 /wallet — محفظتك\n🛒 /shop — المتجر\n\n"
            f"🪙 <b>{wallet.get('coins', 0)}</b> · 💎 <b>{wallet.get('gems', 0)}</b>\n🎖 {rank}")
        return

    if param.startswith("role_"):
        dispatch_role(uid, param)
    elif param.startswith("v_"):
        dispatch_vote(uid, param)
    elif param.startswith("night_"):
        dispatch_night(uid, param)
    elif param.startswith("ask_"):
        dispatch_ask(uid, param)
    elif param.startswith("answer_"):
        dispatch_answer(uid, param)
    elif param.startswith("evilchat_"):
        dispatch_evil_chat(uid, param)
    elif param.startswith("room_"):
        dispatch_room(uid, param)
    elif param.startswith("joker_"):
        dispatch_joker(uid, param)


@bot.message_handler(commands=['rules'], chat_types=['private'])
def cmd_rules(m):
    safe_pm(m.from_user.id,
        "📖 <b>كيف تنجو من المستشفى</b>\n\n"
        "🏠 <b>الغرف</b> — اختر غرفة قبل كل ليلة\n"
        "🌑 <b>الليل</b> — كل دور ينفّذ مهمته بالسر\n"
        "🌅 <b>الفجر</b> — الجثث تتكلم\n"
        "💬 <b>النقاش</b> — اتّهم، دافع\n"
        "⚖️ <b>التصويت</b> — أصابع الاتهام\n"
        "🎤 <b>الدفاع</b> — المتهم يدافع\n"
        "👍👎 <b>الحكم</b> — محرقة أم عفو")

@bot.message_handler(commands=['roles'], chat_types=['private'])
def cmd_roles(m):
    t = "📜 <b>ملفات المستشفى السرية</b>\n\n"
    for d in ROLE_DESC.values():
        t += f"{d}\n{'━' * 20}\n\n"
    safe_pm(m.from_user.id, t)

@bot.message_handler(commands=['myrole'], chat_types=['private'])
def cmd_myrole(m):
    uid = m.from_user.id
    with bot_lock:
        fc = find_game_for_user(uid)
        if not fc or fc not in games:
            return safe_pm(uid, "🚫 لست محتجزاً في أي مستشفى…")
        g = games[fc]
        r = ROLE_DISPLAY.get(g["players"][uid]["role"], "?")
        team = get_original_team(g, uid)
        ti = {"evil": "🔴 ظلام", "psycho": "🟡 مستقل", "good": "🟢 نور", "neutral": "⚪ محايد"}.get(team, "")
    safe_pm(uid, f"🎭 دورك: <b>{r}</b> · {ti}")

@bot.message_handler(commands=['alive'], chat_types=['private'])
def cmd_alive(m):
    uid = m.from_user.id
    with bot_lock:
        fc = find_game_for_user(uid)
        if not fc or fc not in games:
            return safe_pm(uid, "🚫 لست في أي مستشفى…")
        a = get_alive(fc)
        names = "\n\n".join([f"  🟢 {pname(u, p['name'])}" for u, p in a.items()])
    safe_pm(uid, f"<b>الأحياء ({len(a)})</b>\n\n{names}")

@bot.message_handler(commands=['wallet'], chat_types=['private'])
def cmd_wallet(m):
    uid = m.from_user.id
    w = get_wallet(uid)
    safe_pm(uid, f"💰 <b>محفظتك</b>\n\n  🪙 عملات: <b>{w.get('coins', 0)}</b>\n  💎 جواهر: <b>{w.get('gems', 0)}</b>")

@bot.message_handler(commands=['shop'], chat_types=['private'])
def cmd_shop(m):
    uid = m.from_user.id
    mk = types.InlineKeyboardMarkup(row_width=1)
    for item_id, item in SHOP_ITEMS.items():
        mk.add(types.InlineKeyboardButton(f"{item['name']} — {item['price']} 🪙", callback_data=f"buy_{item_id}"))
    safe_pm(uid, "🛒 <b>متجر المستشفى</b>", reply_markup=mk)

@bot.message_handler(commands=['profile'], chat_types=['private'])
def cmd_profile(m):
    uid = m.from_user.id
    p = get_profile(uid)
    w = get_wallet(uid)
    rank = get_rank(uid)
    name = clean_name(m.from_user.first_name)
    total = p["games"]
    wr = f"{(p['wins']/total*100):.0f}%" if total > 0 else "0%"
    safe_pm(uid,
        f"📊 <b>ملف {name}</b>\n🎖 {rank} · XP: {p['xp']}\n\n"
        f"🎮 مباريات: {total} (🏆 {p['wins']} - 💔 {p['losses']})\n📈 نسبة الفوز: {wr}\n\n"
        f"🔪 قتلت كجرّاح: {p['kills_as_surgeon']}\n🩺 أنقذت كطبيب: {p['saves_as_doc']}\n"
        f"💀 مرات الموت: {p['deaths']}\n\n💰 {w.get('coins', 0)} 🪙")

@bot.message_handler(commands=['kill'], chat_types=['private'])
def cmd_kill_private(m):
    uid = m.from_user.id
    with bot_lock:
        cid = user_to_game.get(uid)
        if not cid or cid not in games:
            return safe_pm(uid, "🚫 <b>لست محتجزاً في أي مستشفى</b>")
        g = games[cid]
        if not g["players"][uid]["alive"]:
            return safe_pm(uid, "💀 <b>الأموات لا يحملون المشارط…</b>")
        if g["phase"] != "discussion":
            return safe_pm(uid, "⏳ <b>المشرط لا يعمل إلا في وضح النهار…</b>")
        med = g["med_items"].get(uid)
        if not med or med["item"] != "scalpel" or med.get("used"):
            return safe_pm(uid, "❌ <b>لا مشرط بيدك…</b>")
        targets = get_alive_except(cid, uid)
    if not targets:
        return safe_pm(uid, "🚫 <b>لا أهداف…</b>")
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(*[types.InlineKeyboardButton(p["name"], callback_data=f"scalpel_{cid}_{t}") for t, p in targets.items()])
    safe_pm(uid, "🗡️ <b>اختر ضحيتك…</b>\n\n⚠️ <i>هويتك ستُكشف</i>", reply_markup=mk)


# ══════════════ معالج رسائل الخاص ══════════════
@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def pm_handler(msg):
    uid = msg.from_user.id
    text = msg.text.strip()

    # همسة /x المعلقة
    x_key = None
    # لا توجد whisper_db هنا للهمسات العادية أو x_whisper

    with bot_lock:
        fc = find_game_for_user(uid)
    if not fc:
        return

    with bot_lock:
        if fc not in games:
            return
        g = games[fc]
        gid = g["game_id"]
        is_room_chat = (g["phase"] == "night" and g["players"].get(uid, {}).get("alive", False) and get_player_room(g, uid) is not None)
        is_evil_chat = (uid in g.get("evil_chat_ids", set()) and g["phase"] == "night")
        pp_phase = g.get("psycho_phase", {}).get(uid)
        is_last_gasp = (g.get("last_gasp_pending", {}).get(uid, False) and g["phase"] == "last_gasp_wait")
        is_will = (g.get("will_pending", {}).get(uid, False) and g["phase"] in ("will_wait", "confirming"))
        is_qa = (g["type"] == "vote" and g["phase"] == "answering" and uid in g.get("qa_answer_pending", set()))
        is_asker = (g["type"] == "vote" and g.get("asker") == uid and g["phase"] == "waiting_q" and g.get("ask_type_chosen", False))

    if is_room_chat and not is_evil_chat:
        with bot_lock:
            if fc not in games:
                return
            room = get_player_room(games[fc], uid)
            room_mates = get_room_players(games[fc], room)
            sender_name = games[fc]["players"][uid]["name"]
        for mate_uid in room_mates:
            if mate_uid != uid:
                safe_pm(mate_uid, f"🏠 <b>{clean_name(sender_name)}:</b> {clean(text, 200)}")
        return

    if is_evil_chat:
        with bot_lock:
            if fc not in games:
                return
            evil_ids = list(games[fc].get("evil_chat_ids", set()))
            sender_name = games[fc]["players"][uid]["name"]
        for eid in evil_ids:
            if eid != uid:
                safe_pm(eid, f"🔴 <b>{clean_name(sender_name)}:</b> {clean(text, 200)}")
        return

    if pp_phase == "q":
        q_text = clean(text, 100).strip()
        if not q_text:
            return safe_pm(uid, "❌ <i>اكتب شيئاً حقيقياً…</i>")
        with bot_lock:
            if fc not in games:
                return
            games[fc]["bomb"]["q"] = q_text
            games[fc]["psycho_phase"][uid] = "a"
        safe_pm(uid, f"✅ اللغز: «{q_text}»\n\n💡 <i>والآن… أرسل <b>الجواب</b>:</i>")
        return

    if pp_phase == "a":
        a_text = clean(text, 50).strip()
        if not a_text:
            return safe_pm(uid, "❌ <i>اكتب جواباً…</i>")
        with bot_lock:
            if fc not in games:
                return
            games[fc]["bomb"]["a"] = normalize_arabic(text)
            games[fc]["bomb"]["raw"] = a_text
            games[fc]["bomb"]["is_set"] = True
            games[fc]["bomb"]["owner"] = uid
            games[fc]["psycho_phase"][uid] = "done"
            q = games[fc]["bomb"]["q"]
        safe_pm(uid, f"💣 <b>القنبلة جاهزة</b>\n\n❓ «{q}»\n💡 «{a_text}»\n\n<i>إذا أحرقوك… ينفجر كل شيء 🤡</i>")
        return

    if is_last_gasp:
        words = text.split()[:5]
        gasp = " ".join(words)
        with bot_lock:
            if fc not in games:
                return
            games[fc]["last_gasp_pending"][uid] = False
            games[fc]["last_gasp_text"][uid] = clean(gasp, 80)
        safe_pm(uid, "🩸 <i>…سُجّلت كلماتك الأخيرة</i>")
        return

    if is_will:
        with bot_lock:
            if fc not in games:
                return
            games[fc]["will_pending"][uid] = False
            pn_ = pname(uid, games[fc]["players"][uid]["name"])
            role_d = ROLE_DISPLAY.get(games[fc]["players"][uid]["role"], "?")
        safe_pm(uid, "📜 <i>حُفظت وصيتك…</i>")
        safe_send(fc, f"📜 <b>وصية {pn_}</b>\n\n«{clean(text, 500)}»\n\n<i>{role_d}</i>")
        return

    if is_qa:
        answer_text = clean(text, 200)
        with bot_lock:
            if fc not in games:
                return
            g2 = games[fc]
            if g2["phase"] != "answering" or uid not in g2["qa_answer_pending"]:
                return
            g2["qa_answer_pending"].discard(uid)
            g2["qa_answer_done"].add(uid)
            g2["qa_answers"][uid] = {"text": answer_text, "reveal": None}
        mk = types.InlineKeyboardMarkup()
        mk.add(
            types.InlineKeyboardButton("✅ بتوقيعي", callback_data=f"reveal_{fc}_y"),
            types.InlineKeyboardButton("🎭 مجهول", callback_data=f"reveal_{fc}_n"))
        safe_pm(uid, "✅ <b>وصل جوابك!</b> توقّعه؟", reply_markup=mk)
        return

    if is_asker:
        q_text = clean(text, 200).strip()
        if not q_text:
            return safe_pm(uid, "❌ <i>اكتب سؤالاً…</i>")
        with bot_lock:
            if fc not in games or games[fc]["phase"] != "waiting_q":
                return
            g3 = games[fc]
            ask_type = g3["ask_type"]
            g3["vote_question"] = q_text
            if ask_type == "vote":
                g3["phase"] = "voting_active"
                g3["votes"] = {}
            else:
                g3["phase"] = "answering"
                g3["qa_answers"] = {}
                g3["qa_answer_pending"] = set()
                g3["qa_answer_done"] = set()
        safe_pm(uid, "✅ <i>سؤالك في الهواء…</i>")
        if ask_type == "vote":
            send_vote_q(fc, uid, q_text)
        else:
            send_qa_q(fc, uid, q_text)
        return


# ══════════════ dispatch helpers ══════════════
def dispatch_ask(uid, param):
    try:
        cid = int(param.replace("ask_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫")
        g = games[cid]
        if uid not in g["players"] or g.get("asker") != uid or g["phase"] != "waiting_q":
            return safe_pm(uid, "❌ ليس دورك…")
        if g.get("ask_prompt_sent"):
            if g.get("ask_type_chosen"):
                return safe_pm(uid, "✏️ <i>اكتب سؤالك هنا…</i>")
            else:
                return safe_pm(uid, "👆 <i>اختر نوع السؤال أولاً</i>")
        g["ask_prompt_sent"] = True
    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("❓ سؤال وجواب", callback_data=f"asktype_{cid}_qa"),
        types.InlineKeyboardButton("🗳 سؤال وتصويت", callback_data=f"asktype_{cid}_vote"))
    safe_pm(uid, "🎤 <b>اختر سلاحك:</b>", reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("asktype_"))
def cb_asktype(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, qtype = int(parts[1]), parts[2]
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g.get("asker") != uid or g["phase"] != "waiting_q" or g.get("ask_type_chosen"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g["ask_type"] = qtype
        g["ask_type_chosen"] = True
    label = "❓ سؤال وجواب" if qtype == "qa" else "🗳 سؤال وتصويت"
    bot.answer_callback_query(call.id, f"✅ {label}")
    try:
        bot.edit_message_text(f"✅ <b>{label}</b>\n\n✏️ <i>اكتب سؤالك الآن:</i>",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass


def dispatch_answer(uid, param):
    try:
        cid = int(param.replace("answer_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫")
        g = games[cid]
        if uid not in g["players"] or g["phase"] != "answering":
            return safe_pm(uid, "⏰ فات الأوان…")
        if uid in g.get("qa_answer_done", set()):
            return safe_pm(uid, "✅ أجبت بالفعل")
        if uid in g.get("qa_answer_pending", set()):
            return safe_pm(uid, "✏️ <i>اكتب جوابك…</i>")
        g["qa_answer_pending"].add(uid)
        question = g.get("vote_question", "")
    safe_pm(uid, f"❓ «<b>{question}</b>»\n\n✏️ <i>اكتب جوابك:</i>")


def dispatch_evil_chat(uid, param):
    try:
        cid = int(param.replace("evilchat_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫")
        g = games[cid]
        if uid not in g["players"] or get_original_team(g, uid) != "evil":
            return safe_pm(uid, "🚫 لست من الظلام…")
        g["evil_chat_ids"].add(uid)
    safe_pm(uid, "🌑 <i>قناة الظلام مفتوحة…</i>")


# ══════════════ التشغيل ══════════════
print("🏥 المستشفى الملعون يعمل…")
try:
    print(f"🤖 @{BOT_USERNAME}")
except:
    pass
print(f"🔑 المالك: @{OWNER_USERNAME}")
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
```
