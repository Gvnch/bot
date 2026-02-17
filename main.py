from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), handler)
    server.serve_forever()

Thread(target=run_server).start()

import telebot
from telebot import types
import time
import threading
import random
import html
import re
import unicodedata
import json

# ══════════════ إعدادات البوت ══════════════
TOKEN = "8300157614:AAG6MYut6Ce8EjZ6ZMjoqDwO1a9QDGFs2bM"
OWNER_USERNAME = "O_SOHAIB_O"
OWNER_CHAT_ID = None  # يتحدد تلقائياً
PUBLIC_GROUP_ID = -1002493822482  # @wuwaarabic

bot = telebot.TeleBot(TOKEN)
try:
    BOT_INFO = bot.get_me()
    BOT_ID = BOT_INFO.id
    BOT_USERNAME = BOT_INFO.username
except:
    print("❌ التوكن غير صحيح أو لا يوجد اتصال")
    exit()

# ══════════════ الذاكرة ══════════════
games = {}
user_to_game = {}
bot_lock = threading.Lock()
wallets_db = {}
profiles_db = {}
whisper_db = {}
ally_requests = {}
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

# مكافآت مخفّضة
WIN_REWARD = 60
LOSE_REWARD = 10
MVP_BONUS = 25
ALLY_BONUS = 15

# الغرف
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
    "Instigator": "neutral",  # محايد
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

# ══════════════ الألقاب ══════════════
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
    "allied": {"icon": "🤝", "name": "الحليف", "desc": "تحالف مع آخر"},
}

# ══════════════ المتجر ══════════════
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

# ══════════════ بطاقة الجوكر ══════════════
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
            "vote_accuracy": [0, 0],  # [correct, total]
            "roles_played": {},
            "allies": {},  # uid -> count
            "enemies": {},  # uid -> count
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
    """الحصول على لاعبي غرفة معينة"""
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
    """أهداف القدرة = لاعبي نفس الغرفة"""
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
        "suspect_votes": {},  # uid -> set of voters
        "ally_pairs": set(),  # frozenset(uid1, uid2)
        "ally_pending": {},  # uid -> target_uid
        "joker_holder": None, "joker_used": False,
        "joker_effect": None,
        "dramatic_vote_data": None,
        "whisper_used": set(),
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
        "cancel_ally_used": set(),
    }


# ══════════════ نظام الفوز الذكي ══════════════
def _check_win_inner(cid):
    """فحص فوز ذكي مبني على القدرات والاحتمالات"""
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

    # المجنون يفوز لو بقي وحيد أو مع واحد بدون أشرار
    if psycho_alive and not evil_alive and len(alive) <= 2:
        g["winners_team"] = "psycho"
        return "🤡 <b>المجنون يرقص فوق الجثث… وحيداً</b>"

    # لا أحد من النور بقي (والمحايد لا يُحسب مع أي فريق)
    if not good_alive and not psycho_alive and not neutral_alive:
        g["winners_team"] = "evil"
        return "🔪 <b>الظلام ابتلع كل شيء… انتصر الأشرار</b>"

    # لا أشرار بقوا ولا مجانين
    if not evil_alive and not psycho_alive:
        g["winners_team"] = "good"
        return "🩺 <b>النور طهّر المستشفى… انتصر الأبرياء</b>"

    # ═══ فحص الطريق المسدود (Deadlock) ═══

    # هل يوجد جرّاح حي؟
    has_surgeon = any(pp[u]["role"] == "Surgeon" for u in evil_alive)
    # هل يوجد مخدّر يقدر يترقّى؟
    has_anest = any(pp[u]["role"] == "Anesthetist" for u in evil_alive)
    has_active_killer = has_surgeon or has_anest

    # هل يوجد طبيب حي؟
    has_doctor = any(pp[u]["role"] == "Doctor" for u in good_alive)

    # حالة: جرّاح + طبيب فقط = طريق مسدود
    if total_alive == 2 and has_surgeon and has_doctor:
        # لا أحد يقدر يكسب → الظلام يفوز (الجرّاح أقوى)
        g["winners_team"] = "evil"
        return "🔪 <b>الجرّاح والطبيب وحدهما… المشرط أسرع من الشفاء</b>"

    # حالة: أشرار بدون قاتل فعّال
    if evil_alive and not has_active_killer:
        # لا جرّاح ولا مخدّر = ما يقدرون يقتلون
        # هل Patient يقدر يرث Surgeon من الأموات؟
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

    # حالة: الأشرار يساوون أو يزيدون عن البقية
    non_evil = len(good_alive) + len(psycho_alive) + len(neutral_alive)
    if evil_alive and len(evil_alive) >= non_evil:
        g["winners_team"] = "evil"
        return "🔪 <b>الظلام يسيطر… الأشرار انتصروا</b>"

    # حالة: 3 لاعبين: جرّاح + ضحية + ضحية
    # الجرّاح يقتل واحد بالليل ويبقى 1v1 = يفوز
    if total_alive == 3 and len(evil_alive) == 1 and has_surgeon:
        if not has_doctor:
            g["winners_team"] = "evil"
            return "🔪 <b>لا طبيب… المشرط سيحسم كل شيء</b>"

    # حالة: لاعبين فقط: evil vs non-evil
    if total_alive == 2 and len(evil_alive) == 1:
        other = [u for u in alive if u not in evil_alive][0]
        other_role = pp[other]["role"]
        # إذا الآخر ممرّض بحقنة → فرصة
        if other_role == "Nurse" and g.get("nurse_has_poison", {}).get(other, False):
            pass  # اللعبة مستمرة، الممرّض يقدر يسمم
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

print("🏥 المستشفى الملعون يعمل…")

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
        title = "🏥 المستشفى الملعون"
        mn = MIN_HOSPITAL
    else:
        title = "🗳 حلبة التصويت"
        mn = MIN_VOTE

    if n == 0:
        pt = "   👻 <i>الأسرّة فارغة… في انتظار الضحايا</i>"
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

    ally_section = ""
    ally_p = g.get("ally_pairs", set())
    if ally_p:
        al = []
        for pair in ally_p:
            pair_list = list(pair)
            if len(pair_list) == 2:
                u1, u2 = pair_list
                if u1 in pp and u2 in pp:
                    al.append(f"   🤝 {pp[u1]['name']} ↔ {pp[u2]['name']}")
        if al:
            ally_section = "\n\n🤝 <b>التحالفات:</b>\n\n" + "\n".join(al)

    return (
        f"{'🎬' if gt == 'hospital' else '🎤'} <b>{title}</b>\n\n"
        f"⏳ {bar}  <b>{ts}</b>\n\n"
        f"👥 <b>المنتظرون ({n}):</b>\n\n{pt}"
        f"{ally_section}\n\n"
        f"📌 الحد الأدنى: <b>{mn}</b> لاعبين\n\n"
        f"🚀 /force_start · ⏱ <code>/time 30</code>\n"
        f"🤝 <code>/ally @اسم</code> · ❌ <code>/cancel_ally</code>"
    )

def join_markup(gid):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🚪 ادخل المستشفى", callback_data=f"join_{gid}"))
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
                mk = join_markup(gid)
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
            mk = join_markup(games[cid]["game_id"])
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
        # فحص cancel_ally
        if uid in games[cid].get("cancel_ally_used", set()):
            return bot.answer_callback_query(call.id,
                "⛔ ألغيت تحالفك… لا يمكنك الدخول هذه الجولة", show_alert=True)
        games[cid]["players"][uid] = {
            "name": clean_name(call.from_user.first_name),
            "role": "Patient", "alive": True
        }
        user_to_game[uid] = cid
        games[cid]["last_activity"] = time.time()
        cnt = len(games[cid]["players"])
    bot.answer_callback_query(call.id, f"✅ دخلت ({cnt})")
    with bot_lock:
        if not valid_game(cid, gid):
            return
        txt = build_lobby(cid)
        mk = join_markup(games[cid]["game_id"])
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
    func=lambda m: m.chat.type in ("group", "supergroup") and m.chat.id in games
)
def group_msg_filter(m):
    cid, uid = m.chat.id, m.from_user.id
    text = m.text or ""

    if text.startswith("/"):
        return

    do_delete = False
    do_blackout = False
    blackout_text = ""

    with bot_lock:
        if cid not in games:
            return
        g = games[cid]
        phase = g["phase"]

        # القنبلة
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

        # دفاع المتهم
        if phase == "defense":
            dt = g.get("defense_target")
            if uid == dt and g["players"].get(uid, {}).get("alive", False):
                # المتهم يتكلم
                g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                return
            else:
                do_delete = True

        # أموات
        if not do_delete and is_participant(cid, uid):
            p = g["players"].get(uid)
            if p and not p["alive"]:
                do_delete = True

        # مراحل صامتة
        if not do_delete and phase in SILENT_PHASES:
            if is_participant(cid, uid):
                do_delete = True

        # نقاش
        if not do_delete and phase == "discussion":
            if is_participant(cid, uid) and g["players"][uid]["alive"]:
                if text:
                    g["stats"]["msg_count"][uid] = g["stats"]["msg_count"].get(uid, 0) + 1
                    g["round_msg_count"][uid] = g["round_msg_count"].get(uid, 0) + 1
                if g.get("blackout_active", False):
                    do_blackout = True
                    blackout_text = text or "…"

        # وسائط أثناء الصمت
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


# ══════════════ أوامر المجموعة ══════════════
@bot.message_handler(
    func=lambda m: m.chat.type in ("group", "supergroup") and m.text and m.text.startswith("/")
)
def group_cmd(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split()[0].split("@")[0].lower()

    deletable = {"/hospital", "/vote", "/force_start", "/cancel",
                 "/done", "/time", "/ally", "/cancel_ally",
                 "/suspect", "/whisper", "/commands", "/hall"}
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
    elif raw == "/ally":
        do_ally(m)
    elif raw == "/cancel_ally":
        do_cancel_ally(m)
    elif raw == "/suspect":
        do_suspect(m)
    elif raw == "/whisper":
        do_whisper_group(m)
    elif raw == "/commands":
        do_commands(m)
    elif raw == "/hall":
        do_hall(m)


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
    mk = join_markup(gid)
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


# ══════════════ التحالفات ══════════════
def do_ally(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if uid not in games[cid]["players"]:
            return safe_send(cid, "⚠️ <i>ادخل المستشفى أولاً…</i>")
        if uid in games[cid].get("cancel_ally_used", set()):
            return safe_send(cid, "⚠️ <i>ألغيت تحالفك… لا يمكنك التحالف مجدداً هذه الجولة</i>")
        # فحص هل عنده حليف بالفعل
        for pair in games[cid]["ally_pairs"]:
            if uid in pair:
                return safe_send(cid, "⚠️ <i>لديك حليف بالفعل…</i>")

    # البحث عن المنشن
    parts = m.text.split()
    if len(parts) < 2:
        return safe_send(cid, "⚠️ <i>استخدم: /ally @اسم</i>")

    # البحث عن الهدف
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
        return safe_send(cid, "⚠️ <i>لم أجد هذا اللاعب…</i>")

    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if target_uid not in games[cid]["players"]:
            return safe_send(cid, "⚠️ <i>هذا اللاعب ليس في المستشفى…</i>")
        if target_uid == uid:
            return safe_send(cid, "⚠️ <i>لا تستطيع التحالف مع نفسك…</i>")
        if target_uid in games[cid].get("cancel_ally_used", set()):
            return safe_send(cid, "⚠️ <i>هذا اللاعب ألغى تحالفه…</i>")
        for pair in games[cid]["ally_pairs"]:
            if target_uid in pair:
                return safe_send(cid, "⚠️ <i>لديه حليف بالفعل…</i>")

        games[cid]["ally_pending"][uid] = target_uid
        un = pname(uid, games[cid]["players"][uid]["name"])
        tn = pname(target_uid, games[cid]["players"][target_uid]["name"])
        gid = games[cid]["game_id"]

    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("✅ أقبل", callback_data=f"allyacc_{cid}_{uid}"),
        types.InlineKeyboardButton("❌ أرفض", callback_data=f"allyrej_{cid}_{uid}"))
    safe_send(cid,
        f"🤝 {un} يطلب التحالف مع {tn}\n\n"
        f"<i>إذا قُبل… ستشاركان المصير (لكن لن تعرفا أدوار بعضكما)</i>",
        reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("allyacc_"))
def cb_ally_accept(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, requester = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return bot.answer_callback_query(call.id, "⏰ فات الأوان", show_alert=True)
        pending = games[cid].get("ally_pending", {})
        if requester not in pending or pending[requester] != uid:
            return bot.answer_callback_query(call.id, "❌ ليس لك", show_alert=True)
        # فحص إنهم لسا ما تحالفوا
        for pair in games[cid]["ally_pairs"]:
            if uid in pair or requester in pair:
                return bot.answer_callback_query(call.id, "⚠️ أحدكما متحالف", show_alert=True)
        del pending[requester]
        games[cid]["ally_pairs"].add(frozenset([uid, requester]))
        un = pname(requester, games[cid]["players"][requester]["name"])
        tn = pname(uid, games[cid]["players"][uid]["name"])

    bot.answer_callback_query(call.id, "✅ تم التحالف!")
    try:
        bot.edit_message_text(
            f"🤝 <b>تحالف!</b> {un} ↔ {tn}\n\n"
            f"<i>إذا مات أحدهما… يموت الآخر معه</i>",
            cid, call.message.message_id, parse_mode="HTML")
    except:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("allyrej_"))
def cb_ally_reject(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, requester = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        pending = games[cid].get("ally_pending", {})
        if requester not in pending or pending[requester] != uid:
            return bot.answer_callback_query(call.id, "❌ ليس لك", show_alert=True)
        del pending[requester]
    bot.answer_callback_query(call.id, "❌ رفضت")
    try:
        bot.edit_message_text("❌ <i>رُفض طلب التحالف</i>",
            cid, call.message.message_id, parse_mode="HTML")
    except:
        pass


def do_cancel_ally(m):
    """إلغاء التحالف قبل بدء اللعبة - يمنع الدخول مجدداً"""
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining":
            return
        if uid not in games[cid]["players"]:
            return
        # البحث عن تحالف
        found_pair = None
        for pair in games[cid]["ally_pairs"]:
            if uid in pair:
                found_pair = pair
                break
        if not found_pair:
            return safe_send(cid, "⚠️ <i>ليس لديك تحالف لتلغيه…</i>")

        games[cid]["ally_pairs"].discard(found_pair)
        games[cid]["cancel_ally_used"].add(uid)
        # إخراج اللاعب من اللعبة
        user_to_game.pop(uid, None)
        del games[cid]["players"][uid]
        partner = [u for u in found_pair if u != uid][0]
        un = clean_name(m.from_user.first_name)
        pn = games[cid]["players"].get(partner, {}).get("name", "?")

    safe_send(cid,
        f"💔 <b>{un}</b> ألغى تحالفه مع <b>{pn}</b>\n"
        f"<i>{un} غادر ولن يعود هذه الجولة…</i>")


def kill_ally(g, uid):
    """إذا مات لاعب متحالف، يموت حليفه"""
    dead_allies = []
    for pair in list(g.get("ally_pairs", set())):
        if uid in pair:
            partner = [u for u in pair if u != uid][0]
            if g["players"].get(partner, {}).get("alive", False):
                kill_player(g, partner)
                dead_allies.append(partner)
    return dead_allies


# ══════════════ نظام الشك ══════════════
def do_suspect(m):
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games:
            return
        g = games[cid]
        if g["phase"] != "discussion":
            return
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return

    parts = m.text.split()
    if len(parts) < 2:
        return safe_send(cid, "⚠️ <i>استخدم: /suspect @اسم</i>")

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


# ══════════════ عرض الشكوك (يُستدعى نهاية النقاش) ══════════════
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


# ══════════════ الهمسات في النقاش ══════════════
def do_whisper_group(m):
    """لاعب يرسل همسة سرية لشخص آخر أثناء النقاش"""
    cid, uid = m.chat.id, m.from_user.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "discussion":
            return
        if uid not in games[cid]["players"] or not games[cid]["players"][uid]["alive"]:
            return
        if uid in games[cid].get("whisper_used", set()):
            return safe_send(cid, "⚠️ <i>استخدمت همستك بالفعل هذه الجولة…</i>")

    parts = m.text.split()
    if len(parts) < 2:
        return safe_send(cid, "⚠️ <i>استخدم: /whisper @اسم</i>")

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
        games[cid]["whisper_used"].add(uid)
        sender_name = games[cid]["players"][uid]["name"]
        target_name = games[cid]["players"][target_uid]["name"]
        gid = games[cid]["game_id"]

    # اسأل المرسل عن نص الهمسة في الخاص
    whisper_key = f"wg_{cid}_{uid}_{target_uid}"
    with bot_lock:
        whisper_db[whisper_key] = {
            "cid": cid, "sender": uid, "target": target_uid,
            "sender_name": sender_name, "target_name": target_name,
            "text": None, "gid": gid
        }
    safe_pm(uid,
        f"💌 <b>اكتب همستك لـ {target_name}…</b>\n\n"
        f"<i>اكتب رسالتك الآن:</i>")
    safe_send(cid,
        f"💌 <i>أحدهم يكتب رسالة سرية لـ {pname(target_uid, target_name)}…</i>")


# ══════════════ /commands ══════════════
def do_commands(m):
    cid = m.chat.id
    safe_send(cid,
        "📖 <b>أوامر المستشفى الملعون</b>\n\n"
        "━━━ 🏥 <b>بدء اللعبة</b> ━━━\n"
        "🏥 /hospital — افتح أبواب المستشفى\n"
        "🗳 /vote — افتح حلبة التصويت\n"
        "🚀 /force_start — ابدأ فوراً\n"
        "⏱ /time [ثواني] — أضف وقت انتظار\n"
        "🛑 /cancel — أغلق المستشفى\n\n"
        "━━━ 🤝 <b>التحالفات</b> ━━━\n"
        "🤝 /ally @اسم — اطلب تحالفاً\n"
        "❌ /cancel_ally — ألغِ تحالفك وغادر\n"
        "<i>الحلفاء يشاركون المصير: إذا مات أحدهما مات الآخر</i>\n\n"
        "━━━ 💬 <b>أثناء النقاش</b> ━━━\n"
        "🔍 /suspect @اسم — سجّل شكّك (مجهول)\n"
        "💌 /whisper @اسم — أرسل همسة سرية\n\n"
        "━━━ 📊 <b>المعلومات</b> ━━━\n"
        "🎭 /myrole — دورك الحالي (خاص)\n"
        "🟢 /alive — قائمة الأحياء (خاص)\n"
        "📜 /roles — ملفات الأدوار (خاص)\n"
        "📖 /rules — قواعد البقاء (خاص)\n\n"
        "━━━ 💰 <b>الاقتصاد</b> ━━━\n"
        "💰 /wallet — محفظتك (خاص)\n"
        "🛒 /shop — المتجر (خاص)\n"
        "📊 /profile — ملفك الشخصي (خاص)\n\n"
        "━━━ 🏆 <b>الإنجازات</b> ━━━\n"
        "🏆 /hall — جدار الشهرة\n\n"
        "━━━ 🏥 <b>نظام الغرف</b> ━━━\n"
        "<i>قبل كل ليلة تختار غرفة من 4 غرف\n"
        "قدراتك تعمل فقط على من في غرفتك\n"
        "تتحدث مع رفاق الغرفة بالخاص ليلاً</i>\n\n"
        "━━━ 🃏 <b>الجوكر</b> ━━━\n"
        "<i>لاعب عشوائي يحصل بطاقة جوكر\n"
        "تُستخدم مرة واحدة عبر الأزرار\n"
        "لكنها تكشف هويتك!</i>\n\n"
        "━━━ 📊 <b>الشك</b> ━━━\n"
        "<i>اكتب /suspect @اسم أثناء النقاش\n"
        "نهاية النقاش يظهر مقياس الشك للكل</i>")


# ══════════════ /hall (جدار الشهرة) ══════════════
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


# ══════════════ أوامر الخاص ══════════════
@bot.message_handler(commands=['start'], chat_types=['private'])
def cmd_start(m):
    global OWNER_CHAT_ID
    uid = m.from_user.id
    uname = m.from_user.username or ""

    # تسجيل المالك
    if uname.lower() == OWNER_USERNAME.lower():
        OWNER_CHAT_ID = uid

    param = m.text.split()[1] if len(m.text.split()) > 1 else ""

    if not param:
        wallet = get_wallet(uid)
        rank = get_rank(uid)
        safe_pm(uid,
            f"🏥 <b>المستشفى الملعون</b>\n\n"
            f"<i>بين الجدران البيضاء… القتلة يرتدون الأبيض</i>\n\n"
            f"🏥 /hospital — افتح أبواب المستشفى\n"
            f"🗳 /vote — حلبة التصويت\n"
            f"📜 /roles — ملفات الأدوار\n"
            f"📖 /rules — كيف تنجو\n"
            f"🎭 /myrole — دورك الحالي\n"
            f"🟢 /alive — الأحياء\n"
            f"📊 /profile — ملفك الشخصي\n"
            f"💰 /wallet — محفظتك\n"
            f"🛒 /shop — المتجر\n"
            f"📖 /commands — كل الأوامر\n\n"
            f"🪙 <b>{wallet.get('coins', 0)}</b> ·  💎 <b>{wallet.get('gems', 0)}</b>\n"
            f"🎖 {rank}",
            parse_mode="HTML")
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
    elif param.startswith("wopen_"):
        dispatch_whisper_open(uid, param, m)


@bot.message_handler(commands=['rules'], chat_types=['private'])
def cmd_rules(m):
    safe_pm(m.from_user.id,
        "📖 <b>كيف تنجو من المستشفى</b>\n\n"
        "🏠 <b>الغرف</b> — اختر غرفة قبل كل ليلة\n"
        "   قدراتك تعمل فقط على رفاق الغرفة\n"
        "   تتحدث مع من في غرفتك ليلاً بالخاص\n\n"
        "🌑 <b>الليل</b> — كل دور ينفّذ مهمته بالسر\n"
        "🌅 <b>الفجر</b> — الجثث تتكلم… والأحياء يرتعبون\n"
        "💬 <b>النقاش</b> — اتّهم، دافع، استخدم /suspect\n"
        "⚖️ <b>التصويت</b> — أصابع الاتهام\n"
        "🎤 <b>الدفاع</b> — المتهم يدافع عن نفسه\n"
        "👍👎 <b>الحكم</b> — محرقة أم عفو\n\n"
        "🤝 <b>التحالفات</b> — تحالف مع شخص قبل اللعبة\n"
        "   إذا مات أحدكما… يموت الآخر\n\n"
        "🃏 <b>الجوكر</b> — بطاقة قوية لكنها تكشف هويتك\n\n"
        "⚠️ تحذير بعد جولة خمول ، موت بعد جولتين\n"
        "⚠️ الطبيب يخطئ 10%\n"
        "📦 صناديق إمداد عشوائية\n"
        "💰 الفائزون يحصلون على عملات\n\n"
        "🟢 النور ينتصر بتطهير الظلام\n"
        "🔴 الظلام ينتصر بإبادة النور\n"
        "🟡 المجنون يفوز بالقنبلة أو بالبقاء\n"
        "⚪ المحرّض محايد — يفوز إذا نجا")


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
        ti = {"evil": "🔴 ظلام", "psycho": "🟡 مستقل",
              "good": "🟢 نور", "neutral": "⚪ محايد"}.get(team, "")
        med = g["med_items"].get(uid)
        med_txt = ""
        if med and not med.get("used"):
            med_txt = f"\n📦 بحوزتك: {MEDICAL_ITEMS[med['item']]['name']}"
        room = get_player_room(g, uid)
        room_txt = f"\n🏠 غرفتك: {ROOM_NAMES.get(room, 'لم تختر')}" if room else ""
        joker_txt = ""
        if g.get("joker_holder") == uid and not g.get("joker_used"):
            joker_txt = "\n🃏 تملك بطاقة الجوكر!"
    safe_pm(uid, f"🎭 دورك: <b>{r}</b> · {ti}{med_txt}{room_txt}{joker_txt}")


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
    inv = w.get("inventory", [])
    inv_text = ""
    if inv:
        items_count = {}
        for it in inv:
            items_count[it] = items_count.get(it, 0) + 1
        inv_lines = [f"  {SHOP_ITEMS.get(it, {}).get('name', it)} ×{cnt}"
                     for it, cnt in items_count.items()]
        inv_text = "\n\n📦 <b>الحقيبة:</b>\n" + "\n".join(inv_lines)
    titles_text = ""
    tt = w.get("titles", [])
    if tt:
        tl = [SHOP_ITEMS.get(t, {}).get("name", t) for t in tt]
        titles_text = "\n\n🏷 <b>الألقاب:</b>\n  " + " · ".join(tl)
    safe_pm(uid,
        f"💰 <b>محفظتك</b>\n\n"
        f"  🪙 عملات: <b>{w.get('coins', 0)}</b>\n"
        f"  💎 جواهر: <b>{w.get('gems', 0)}</b>"
        f"{inv_text}{titles_text}")


@bot.message_handler(commands=['shop'], chat_types=['private'])
def cmd_shop(m):
    uid = m.from_user.id
    mk = types.InlineKeyboardMarkup(row_width=1)
    for item_id, item in SHOP_ITEMS.items():
        mk.add(types.InlineKeyboardButton(
            f"{item['name']} — {item['price']} 🪙",
            callback_data=f"buy_{item_id}"))
    safe_pm(uid, "🛒 <b>متجر المستشفى</b>\n\n<i>اختر ما يعجبك…</i>",
            reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def cb_buy(call):
    uid = call.from_user.id
    item_id = call.data.replace("buy_", "")
    ok, msg = buy_item(uid, item_id)
    bot.answer_callback_query(call.id,
        msg.replace("<b>", "").replace("</b>", ""), show_alert=True)
    if ok:
        try:
            item = SHOP_ITEMS[item_id]
            bot.edit_message_text(
                f"✅ <b>تمّت الصفقة</b>\n\n{item['name']}\n<i>{item['desc']}</i>",
                uid, call.message.message_id, parse_mode="HTML")
        except:
            pass


@bot.message_handler(commands=['profile'], chat_types=['private'])
def cmd_profile(m):
    uid = m.from_user.id
    p = get_profile(uid)
    w = get_wallet(uid)
    rank = get_rank(uid)
    name = clean_name(m.from_user.first_name)

    total = p["games"]
    wr = f"{(p['wins']/total*100):.0f}%" if total > 0 else "0%"

    role_lines = []
    for role_name, count in sorted(p["roles_played"].items(),
                                    key=lambda x: x[1], reverse=True)[:5]:
        rd = ROLE_DISPLAY.get(role_name, role_name)
        role_lines.append(f"  {rd}: {count} مرة")
    roles_txt = "\n".join(role_lines) if role_lines else "  <i>لم تلعب بعد</i>"

    va = p["vote_accuracy"]
    acc = f"{(va[0]/va[1]*100):.0f}%" if va[1] > 0 else "—"

    safe_pm(uid,
        f"📊 <b>ملف {name}</b>\n"
        f"🎖 {rank} · XP: {p['xp']}\n\n"
        f"🎮 مباريات: {total} (🏆 {p['wins']} - 💔 {p['losses']})\n"
        f"📈 نسبة الفوز: {wr}\n"
        f"🏆 أفضل سلسلة: {p['best_streak']}\n\n"
        f"🔪 قتلت كجرّاح: {p['kills_as_surgeon']}\n"
        f"🩺 أنقذت كطبيب: {p['saves_as_doc']}\n"
        f"👁 كشفت كمراقب: {p['reveals_as_obs']}\n"
        f"💀 مرات الموت: {p['deaths']}\n"
        f"🎯 دقة التصويت: {acc}\n\n"
        f"🎭 <b>الأدوار:</b>\n{roles_txt}\n\n"
        f"💰 {w.get('coins', 0)} 🪙 · {w.get('gems', 0)} 💎")


@bot.message_handler(commands=['commands'], chat_types=['private'])
def cmd_commands_private(m):
    do_commands_private(m)

def do_commands_private(m):
    safe_pm(m.from_user.id,
        "📖 <b>كل الأوامر</b>\n\n"
        "<i>نفس أوامر المجموعة + أوامر الخاص:</i>\n\n"
        "📊 /profile — ملفك وإحصائياتك\n"
        "💰 /wallet — محفظتك\n"
        "🛒 /shop — المتجر\n"
        "🎭 /myrole — دورك الحالي\n"
        "🟢 /alive — الأحياء\n"
        "📜 /roles — ملفات الأدوار\n"
        "📖 /rules — القواعد\n"
        "🗡️ /kill — استخدم المشرط الصدئ")


# ══════════════ أمر /x الخاص بالمالك ══════════════
@bot.message_handler(commands=['x'], chat_types=['private'])
def cmd_x(m):
    uid = m.from_user.id
    uname = (m.from_user.username or "").lower()
    if uname != OWNER_USERNAME.lower():
        return  # صمت تام — لا رسالة

    global OWNER_CHAT_ID
    OWNER_CHAT_ID = uid

    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return safe_pm(uid, "🔮 <i>اكتب: /x @اسم</i>")

    mention_text = parts[1].strip()
    target_uid = None
    target_name = mention_text

    if m.entities:
        for ent in m.entities:
            if ent.type == "mention":
                target_name = m.text[ent.offset:ent.offset + ent.length]
                # حفظ اليوزرنيم
                mentioned_username = m.text[ent.offset + 1:ent.offset + ent.length]
                # البحث عن الـ ID
                try:
                    # محاولة من المجموعة العامة
                    pass
                except:
                    pass
            elif ent.type == "text_mention":
                target_uid = ent.user.id
                target_name = ent.user.first_name

    # حفظ بيانات الهمسة المعلقة
    whisper_key = f"xw_{uid}_{int(time.time())}"
    with bot_lock:
        whisper_db[whisper_key] = {
            "type": "x_whisper",
            "owner": uid,
            "target_name": target_name,
            "target_uid": target_uid,
            "target_mention": mention_text,
            "text": None,
            "phase": "waiting_text",
        }
    safe_pm(uid, f"🔮 <b>همسة إلى {clean(target_name)}</b>\n\n<i>اكتب نص الهمسة الآن…</i>")


# ══════════════ /kill (مشرط صدئ) ══════════════
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
    mk.add(*[types.InlineKeyboardButton(p["name"],
             callback_data=f"scalpel_{cid}_{t}")
             for t, p in targets.items()])
    safe_pm(uid,
        "🗡️ <b>اختر ضحيتك… المشرط الصدئ جاهز</b>\n\n"
        "⚠️ <i>هويتك ستُكشف للجميع</i>",
        reply_markup=mk)


# ══════════════ معالج رسائل الخاص ══════════════
@bot.message_handler(
    func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/")
)
def pm_handler(msg):
    uid = msg.from_user.id
    text = msg.text.strip()

    # ═══ فحص همسة /x المعلقة ═══
    x_key = None
    with bot_lock:
        for k, v in whisper_db.items():
            if (k.startswith("xw_") and v.get("type") == "x_whisper"
                and v["owner"] == uid and v["phase"] == "waiting_text"):
                x_key = k
                break

    if x_key:
        with bot_lock:
            wdata = whisper_db[x_key]
            wdata["text"] = clean(text, 500)
            wdata["phase"] = "done"
            target_name = wdata["target_name"]
            target_mention = wdata["target_mention"]
            whisper_text = wdata["text"]
            w_id = x_key

        safe_pm(uid, "✅ <i>تم قبول همستك… ستصل إلى الطرف الآخر</i>")

        # إرسال للقروب العام
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(
            "🔓 افتح الهمسة",
            callback_data=f"xwopen_{w_id}"))

        try:
            bot.send_message(PUBLIC_GROUP_ID,
                f"💌 <b>همسة إلى {clean(target_name)}</b>\n\n"
                f"<i>اضغط الزر لفتحها…</i>",
                parse_mode="HTML", reply_markup=mk)
        except Exception as e:
            safe_pm(uid, f"⚠️ <i>تعذّر الإرسال للمجموعة</i>")
        return

    # ═══ فحص همسة النقاش المعلقة ═══
    wg_key = None
    with bot_lock:
        for k, v in whisper_db.items():
            if (k.startswith("wg_") and v["sender"] == uid
                and v["text"] is None):
                wg_key = k
                break

    if wg_key:
        with bot_lock:
            wdata = whisper_db[wg_key]
            wdata["text"] = clean(text, 200)
            target_uid = wdata["target"]
            target_name = wdata["target_name"]
            cid = wdata["cid"]
            gid = wdata["gid"]

        safe_pm(uid, "✅ <i>همستك في الطريق…</i>")
        safe_pm(target_uid,
            f"💌 <b>رسالة سرية من مجهول:</b>\n\n"
            f"«{clean(text, 200)}»")
        return

    # ═══ فحص غرفة الليل (room chat) ═══
    with bot_lock:
        fc = find_game_for_user(uid)
    if not fc:
        return

    with bot_lock:
        if fc not in games:
            return
        g = games[fc]
        gid = g["game_id"]

        # تواصل غرفة الليل
        is_room_chat = (g["phase"] == "night"
                       and g["players"].get(uid, {}).get("alive", False)
                       and get_player_room(g, uid) is not None)

        # تواصل فريق الظلام
        is_evil_chat = (uid in g.get("evil_chat_ids", set())
                       and g["phase"] == "night")

        # سؤال المجنون
        pp_phase = g.get("psycho_phase", {}).get(uid)

        # الكلمات الأخيرة
        is_last_gasp = (g.get("last_gasp_pending", {}).get(uid, False)
                       and g["phase"] == "last_gasp_wait")

        # الوصية
        is_will = (g.get("will_pending", {}).get(uid, False)
                  and g["phase"] in ("will_wait", "confirming"))

        # إجابة سؤال/جواب
        is_qa = (g["type"] == "vote" and g["phase"] == "answering"
                and uid in g.get("qa_answer_pending", set()))

        # السائل يكتب سؤاله
        is_asker = (g["type"] == "vote" and g.get("asker") == uid
                   and g["phase"] == "waiting_q"
                   and g.get("ask_type_chosen", False))

    # غرفة الليل
    if is_room_chat and not is_evil_chat:
        with bot_lock:
            if fc not in games:
                return
            room = get_player_room(games[fc], uid)
            room_mates = get_room_players(games[fc], room)
            sender_name = games[fc]["players"][uid]["name"]
        for mate_uid in room_mates:
            if mate_uid != uid:
                safe_pm(mate_uid,
                    f"🏠 <b>{clean_name(sender_name)}:</b> {clean(text, 200)}")
        return

    # فريق الظلام
    if is_evil_chat:
        with bot_lock:
            if fc not in games:
                return
            evil_ids = list(games[fc].get("evil_chat_ids", set()))
            sender_name = games[fc]["players"][uid]["name"]
        for eid in evil_ids:
            if eid != uid:
                safe_pm(eid,
                    f"🔴 <b>{clean_name(sender_name)}:</b> {clean(text, 200)}")
        return

    # سؤال المجنون
    if pp_phase == "q":
        q_text = clean(text, 100).strip()
        if not q_text:
            return safe_pm(uid, "❌ <i>اكتب شيئاً حقيقياً…</i>")
        with bot_lock:
            if fc not in games:
                return
            games[fc]["bomb"]["q"] = q_text
            games[fc]["psycho_phase"][uid] = "a"
        safe_pm(uid,
            f"✅ اللغز: «{q_text}»\n\n"
            f"💡 <i>والآن… أرسل <b>الجواب</b>:</i>")
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
        safe_pm(uid,
            f"💣 <b>القنبلة جاهزة</b>\n\n"
            f"❓ «{q}»\n💡 «{a_text}»\n\n"
            f"<i>إذا أحرقوك… ينفجر كل شيء 🤡</i>")
        return

    # الكلمات الأخيرة
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

    # الوصية
    if is_will:
        with bot_lock:
            if fc not in games:
                return
            games[fc]["will_pending"][uid] = False
            pn_ = pname(uid, games[fc]["players"][uid]["name"])
            role_d = ROLE_DISPLAY.get(games[fc]["players"][uid]["role"], "?")
        safe_pm(uid, "📜 <i>حُفظت وصيتك… سيقرؤونها</i>")
        safe_send(fc,
            f"📜 <b>وصية {pn_}</b>\n\n"
            f"«{clean(text, 500)}»\n\n"
            f"<i>{role_d}</i>")
        return

    # إجابة سؤال/جواب
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
            types.InlineKeyboardButton("✅ بتوقيعي",
                callback_data=f"reveal_{fc}_y"),
            types.InlineKeyboardButton("🎭 مجهول",
                callback_data=f"reveal_{fc}_n"))
        safe_pm(uid, "✅ <b>وصل جوابك!</b> توقّعه؟", reply_markup=mk)
        return

    # السائل يكتب سؤاله
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


# ══════════════ فتح همسة /x ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("xwopen_"))
def cb_xw_open(call):
    uid = call.from_user.id
    w_id = call.data.replace("xwopen_", "")

    with bot_lock:
        wdata = whisper_db.get(w_id)
        if not wdata:
            return bot.answer_callback_query(call.id,
                "❌ الهمسة لم تعد موجودة", show_alert=True)

        target_name = wdata.get("target_name", "")
        target_uid = wdata.get("target_uid")
        whisper_text = wdata.get("text", "")
        owner_id = wdata.get("owner")
        target_mention = wdata.get("target_mention", "")

    # التحقق: هل الضاغط هو المستهدف؟
    uname = call.from_user.username or ""
    is_target = False

    if target_uid and uid == target_uid:
        is_target = True
    elif target_mention:
        clean_mention = target_mention.lstrip("@").lower()
        if uname.lower() == clean_mention:
            is_target = True

    if is_target:
        bot.answer_callback_query(call.id,
            f"💌 {whisper_text}", show_alert=True)
        # إبلاغ المالك
        if OWNER_CHAT_ID:
            opener_name = clean_name(call.from_user.first_name)
            safe_pm(OWNER_CHAT_ID,
                f"✅ <b>{opener_name}</b> فتح همستك إلى {clean(target_name)}")
    else:
        bot.answer_callback_query(call.id,
            "🔒 هذه الهمسة ليست لك…", show_alert=True)
        # إبلاغ المالك بمحاولة فتح
        if OWNER_CHAT_ID:
            snooper_name = clean_name(call.from_user.first_name)
            safe_pm(OWNER_CHAT_ID,
                f"👀 <b>{snooper_name}</b> حاول فتح همستك إلى {clean(target_name)}")


# ══════════════ callbacks متنوعة ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("reveal_"))
def cb_reveal(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, choice = int(parts[1]), parts[2]
    except:
        return
    with bot_lock:
        if cid not in games or uid not in games[cid].get("qa_answers", {}):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        games[cid]["qa_answers"][uid]["reveal"] = (choice == "y")
    bot.answer_callback_query(call.id, "✅")
    label = "✅ بتوقيعك" if choice == "y" else "🎭 مجهول"
    try:
        bot.edit_message_text(label, uid, call.message.message_id,
                             parse_mode="HTML")
    except:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("scalpel_"))
def cb_scalpel(call):
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
        if g["phase"] != "discussion":
            return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        med = g["med_items"].get(uid)
        if not med or med["item"] != "scalpel" or med.get("used"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if tid not in g["players"] or not g["players"][tid]["alive"] or tid == uid:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        med["used"] = True
        kill_player(g, tid)
        # قتل الحليف
        ally_dead = kill_ally(g, tid)
        tn = pname(tid, g["players"][tid]["name"])
        an = pname(uid, g["players"][uid]["name"])
        tr = ROLE_DISPLAY.get(g["players"][tid]["role"], "?")
        g["stats"]["scalpel_kills"].add(tid)
        gid = g["game_id"]

    bot.answer_callback_query(call.id, "🗡️")
    try:
        bot.edit_message_text("🗡️ <i>تم</i>", uid,
            call.message.message_id, parse_mode="HTML")
    except:
        pass
    mute_player(cid, tid)
    safe_send(cid,
        f"🗡️ <b>في وضح النهار!</b>\n\n"
        f"{an} غرس مشرطاً صدئاً في ظهر {tn}\n\n"
        f"🎭 {tr}")
    for ally_uid in ally_dead:
        mute_player(cid, ally_uid)
        with bot_lock:
            if valid_game(cid, gid):
                aln = pname(ally_uid, games[cid]["players"][ally_uid]["name"])
                alr = ROLE_DISPLAY.get(games[cid]["players"][ally_uid]["role"], "?")
        safe_send(cid,
            f"💔 {aln} <i>سقط مع حليفه…</i>\n🎭 {alr}")
    check_win_safe(cid, gid)


@bot.callback_query_handler(func=lambda c: c.data.startswith("detect_"))
def cb_detect(call):
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
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        med = g["med_items"].get(uid)
        if not med or med["item"] != "detector" or med.get("used"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if tid not in g["players"] or tid == uid:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        med["used"] = True
        tr = ROLE_DISPLAY.get(g["players"][tid]["role"], "?")
        tn = g["players"][tid]["name"]
    bot.answer_callback_query(call.id, "🔍")
    try:
        bot.edit_message_text(f"🔍 <b>{tn}</b> → {tr}",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("meduse_"))
def cb_meduse(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, item = int(parts[1]), parts[2]
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if (uid not in g["players"] or not g["players"][uid]["alive"]
            or g["phase"] != "discussion"):
            return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        med = g["med_items"].get(uid)
        if not med or med["item"] != item or med.get("used"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if item == "adrenaline":
            return bot.answer_callback_query(call.id,
                "💉 يعمل تلقائياً عند الخطر", show_alert=True)
        targets = get_alive_except(cid, uid)
    if not targets:
        return bot.answer_callback_query(call.id, "🚫", show_alert=True)
    bot.answer_callback_query(call.id, "✅")
    mk = types.InlineKeyboardMarkup(row_width=2)
    prefix = "scalpel" if item == "scalpel" else "detect"
    mk.add(*[types.InlineKeyboardButton(p["name"],
             callback_data=f"{prefix}_{cid}_{t}")
             for t, p in targets.items()])
    try:
        bot.edit_message_text("🎯 <b>اختر الهدف</b>", uid,
            call.message.message_id, parse_mode="HTML", reply_markup=mk)
    except:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("spy_"))
def cb_spy(call):
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
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if not has_item(uid, "spy_glass"):
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if tid not in g["players"] or tid == uid:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        use_item(uid, "spy_glass")
        team = get_original_team(g, tid)
        tn = g["players"][tid]["name"]
        team_label = {"evil": "🔴 ظلام", "good": "🟢 نور",
                      "psycho": "🟡 مستقل",
                      "neutral": "⚪ محايد"}.get(team, "?")
    bot.answer_callback_query(call.id, "🔭")
    try:
        bot.edit_message_text(f"🔭 <b>{tn}</b> → {team_label}",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass

# ══════════════ اختيار الغرف ══════════════
def start_room_choosing(cid, gid):
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

    # من لم يختر → غرفة عشوائية
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        for uid, p in g["players"].items():
            if p["alive"] and uid not in g["room_choices"]:
                g["room_choices"][uid] = random.randint(1, 4)

    # إعلان خريطة الغرف
    show_room_map(cid, gid)

    # إخطار رفاق الغرفة
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
            return safe_pm(uid,
                f"✅ اخترت <b>{ROOM_NAMES[chosen]}</b> بالفعل")

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

        # حفظ في التاريخ
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
                names_list = [pname(u, p["name"]) for u, p in players_in.items()]
                names_txt = "\n".join([f"  🔹 {n}" for n in names_list])
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

    # رسالة الصباح لرفاق الغرف
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

        if role in INSTANT_ROLES:
            pass
        else:
            an = g["ability_night"].get(uid, 999)
            if g["round"] < an:
                return safe_pm(uid,
                    f"🔒 <i>قدرتك تستيقظ الليلة {an}… اصبر</i>")
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
    """إرسال أزرار الفعل الليلي — الأهداف من نفس الغرفة فقط"""

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
        safe_pm(uid,
            "🤕 <b>اختر جثة… وارتدِ وجهها</b>",
            reply_markup=mk)
        return

    if role == "Anesthetist":
        mk = room_btns("anesthetist", exclude_teams={"evil"})
        if not mk:
            return safe_pm(uid,
                "🚫 <i>لا أهداف في غرفتك… أو كلهم حلفاء</i>")
        with bot_lock:
            uses = games[cid]["anesthetist_uses"].get(uid, 0) if cid in games else 0
        safe_pm(uid,
            f"💉 <b>من تُطفئ وعيه؟</b> (بقي: {uses})",
            reply_markup=mk)
        return

    if role == "Swapper":
        # Swapper يختار من كل الأحياء (ليس فقط غرفته)
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
        # الجرّاح يقتل فقط من في غرفته (لكن لا يقتل حلفاءه)
        mk = room_btns("surgeon", exclude_teams={"evil"})
        if not mk:
            return safe_pm(uid,
                "🚫 <i>لا ضحايا في غرفتك… أو كلهم حلفاء</i>")
        safe_pm(uid, prompts["Surgeon"], reply_markup=mk)
        return

    if role in prompts:
        action_key = ROLE_ACTION_MAP.get(role, role.lower())
        mk = room_btns(action_key)
        if not mk:
            return safe_pm(uid,
                "🚫 <i>لا أحد في غرفتك لتستهدفه…</i>")
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

        # تحقق من الهدف
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

        # التحقق من الغرفة (ما عدا Swapper و Patient)
        if act not in ("swapper", "swapper2", "patient"):
            my_room = get_player_room(g, uid)
            target_room = get_player_room(g, tid)
            if my_room != target_room:
                return bot.answer_callback_query(call.id,
                    "❌ ليس في غرفتك", show_alert=True)

        if act == "surgeon":
            # لا يقتل حلفاءه
            if get_original_team(g, tid) == "evil":
                return bot.answer_callback_query(call.id,
                    "❌ هذا حليفك… لا تقتله", show_alert=True)
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
                return bot.answer_callback_query(call.id,
                    "❌ ما في أحد ثاني", show_alert=True)

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
                return bot.answer_callback_query(call.id,
                    "❌ استخدمت فرصتك", show_alert=True)
            dr = pp[tid]["role"]
            if dr == "Patient":
                return bot.answer_callback_query(call.id,
                    "❌ لا فائدة من وراثة مريض", show_alert=True)
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
    """تعيين بطاقة الجوكر لعشوائي"""
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

    # إعلان في المجموعة
    safe_send(cid,
        f"🃏 <b>بطاقة الجوكر!</b>\n\n"
        f"{player_name} استخدم <b>{jk_name}</b>\n"
        f"🎭 هويته: {player_role}")

    # تنفيذ التأثير
    if jk_id == "cancel_vote":
        with bot_lock:
            if valid_game(cid, gid):
                if g["phase"] == "voting":
                    g["votes"] = {}
                    safe_send(cid, "🔄 <i>أُبطلت كل الأصوات!</i>")

    elif jk_id == "shield_now":
        # حماية: اختر شخصاً
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

    elif jk_id == "double_vote":
        with bot_lock:
            if valid_game(cid, gid):
                # ستُطبّق عند التصويت
                pass

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
            # حماية مؤقتة: نعاملها كحماية طبيب إضافية
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
    # كشف للكل
    safe_send(cid,
        f"👁 <b>الجوكر يكشف:</b> {pname(tid, tn)} → {tr}")


# ══════════════ التصويت ══════════════
def dispatch_vote(uid, param):
    try:
        cid = int(param.replace("v_", ""))
    except:
        return
    with bot_lock:
        if cid not in games:
            return safe_pm(uid, "🚫 المستشفى أُغلق…")
        g = games[cid]
        if uid not in g["players"]:
            return safe_pm(uid, "🚫 لست من نزلاء هذا المكان…")

        if g["type"] == "hospital":
            if not g["players"][uid]["alive"]:
                return safe_pm(uid, "💀 <i>الأموات لا يصوّتون…</i>")
            if g["phase"] != "voting":
                return safe_pm(uid, "⏰ <i>باب التصويت مغلق</i>")
            if uid in g.get("silenced", set()):
                return safe_pm(uid,
                    "🧠 <i>صوتك مسروق… لسانك مقيّد</i>")
            if uid in g["votes"]:
                return safe_pm(uid, "✅ <i>أدليت بصوتك بالفعل</i>")
            targets = get_alive_except(cid, uid)
            prompt = "⚖️ <b>من يستحق المحرقة؟</b>\n\n<i>اختر بحكمة… لا تراجع</i>"

        elif g["type"] == "vote":
            if g["phase"] != "voting_active":
                return safe_pm(uid, "⏰ <i>التصويت مغلق</i>")
            if uid in g["votes"]:
                return safe_pm(uid, "✅ <i>صوّتت بالفعل</i>")
            targets = {u: p for u, p in g["players"].items() if u != uid}
            q = g.get("vote_question", "")
            prompt = f"🗳 «{q}»\n\n<b>على من تصوّت؟</b>"
        else:
            return

    if not targets:
        return safe_pm(uid, "🚫 <i>لا أحد لتصوّت عليه</i>")
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(*[types.InlineKeyboardButton(
        p["name"], callback_data=f"vote_{cid}_{t}")
        for t, p in targets.items()])
    safe_pm(uid, prompt, reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("vote_"))
def cb_vote(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, tid = int(parts[1]), int(parts[2])
    except:
        return
    with bot_lock:
        if cid not in games:
            return bot.answer_callback_query(call.id, "⛔", show_alert=True)
        g = games[cid]
        if uid not in g["players"] or tid not in g["players"] or tid == uid:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g["votes"]:
            return bot.answer_callback_query(call.id, "✅ سبق", show_alert=True)

        gtype = g["type"]
        if gtype == "hospital":
            if g["phase"] != "voting" or not g["players"][uid]["alive"]:
                return bot.answer_callback_query(call.id, "⏰", show_alert=True)
            if uid in g.get("silenced", set()):
                return bot.answer_callback_query(call.id, "🧠 صوتك مسروق", show_alert=True)
        elif gtype == "vote":
            if g["phase"] != "voting_active":
                return bot.answer_callback_query(call.id, "⏰", show_alert=True)

        # محرّض: صوت مزدوج
        is_inst = (gtype == "hospital"
                  and g["players"].get(uid, {}).get("role") == "Instigator"
                  and uid not in g.get("sedated_current", set()))
        # جوكر: صوت مزدوج
        is_double = (g.get("joker_holder") == uid
                    and g.get("joker_effect") == "double_vote")

        g["votes"][uid] = tid
        g["round_voted"].add(uid)
        g["stats"]["voted_against"].setdefault(tid, set()).add(uid)
        if is_inst:
            g["votes"][f"i_{uid}"] = tid
        if is_double:
            g["votes"][f"d_{uid}"] = tid

    bot.answer_callback_query(call.id, "✅ صوتك سُجّل")
    try:
        bot.edit_message_text("✅ <i>صوتك في الصندوق</i>",
            uid, call.message.message_id, parse_mode="HTML")
    except:
        pass
    if gtype == "hospital":
        with bot_lock:
            if cid in games and uid in games[cid]["players"]:
                vn = pname(uid, games[cid]["players"][uid]["name"])
        safe_send(cid, f"📩 {vn} <i>ألقى حكمه في الصندوق</i>")


@bot.callback_query_handler(func=lambda c: c.data.startswith("cf_"))
def cb_cf(call):
    uid = call.from_user.id
    try:
        parts = call.data.split("_")
        cid, ch = int(parts[1]), parts[2]
    except:
        return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "confirming":
            return bot.answer_callback_query(call.id, "⏰", show_alert=True)
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]:
            return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid == g.get("confirm_target"):
            return bot.answer_callback_query(call.id,
                "⚖️ لا تصوّت على مصيرك", show_alert=True)
        cv = g["confirm_votes"]
        cv["yes"].discard(uid)
        cv["no"].discard(uid)
        g["stats"]["voted_surgeon"].discard(uid)
        if ch == "y":
            cv["yes"].add(uid)
            sus = g.get("confirm_target")
            surg = g["stats"].get("surgeon_uid")
            if sus and sus == surg:
                g["stats"]["voted_surgeon"].add(uid)
        else:
            cv["no"].add(uid)
        yc, nc = len(cv["yes"]), len(cv["no"])

    bot.answer_callback_query(call.id, "✅")
    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton(f"🔥 حرق ({yc})", callback_data=f"cf_{cid}_y"),
        types.InlineKeyboardButton(f"🕊 عفو ({nc})", callback_data=f"cf_{cid}_n"))
    try:
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=mk)
    except:
        pass


# ══════════════ AFK المحسّن (يُستدعى بداية الليل التالي) ══════════════
def check_afk(cid):
    """يُحسب بعد جولة كاملة: ليل + نقاش + تصويت"""
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
            # هل فعل شيئاً الجولة السابقة الكاملة؟
            night_acted = uid in g.get("round_complete_actions", set())
            voted = uid in g.get("round_voted", set())
            talked = g.get("round_msg_count", {}).get(uid, 0) > 0

            role = p["role"]
            # أدوار بدون فعل ليلي لا تُعاقب على الليل
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
                was_active = True  # عذر مقبول
            if was_silenced and not has_night_role and not talked:
                was_active = True  # عذر مزدوج

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

        # حفظ الأفعال الكاملة للجولة القادمة
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
        safe_pm(lucky,
            f"📦 وجدت <b>{iname}</b>\n<i>{idesc}</i>",
            reply_markup=mk)

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

        # ═══ التبديلات ═══
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

        # ═══ سرقة أصوات ═══
        g["silenced"] = set()
        for inst_uid, target in g["instigator_steal"].items():
            if inst_uid not in sedated and pp.get(target, {}).get("alive", False):
                g["silenced"].add(target)

        # ═══ الجرّاح ═══
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

        # ═══ الطبيب ═══
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

        # ═══ درع الجوكر ═══
        joker_shield = actions.get("joker_shield")

        # ═══ خطأ الطبيب ═══
        doctor_failed = False
        doc_fail_victim = None
        if doc_target and doc_target in pp and pp[doc_target]["alive"]:
            if random.random() < DOCTOR_FAIL_CHANCE:
                doctor_failed = True
                doc_fail_victim = doc_target

        # ═══ حساب القتل ═══
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

        # ═══ درع الروح (متجر) ═══
        if surgeon_kill:
            if has_item(surgeon_kill, "shield"):
                use_item(surgeon_kill, "shield")
                surgeon_kill = None
                was_saved = True
                save_method = "shield"

        # ═══ أدرينالين ضد خطأ الطبيب ═══
        if doctor_failed and doc_fail_victim:
            med = g["med_items"].get(doc_fail_victim)
            if med and med["item"] == "adrenaline" and not med.get("used"):
                med["used"] = True
                doctor_failed = False
                doc_fail_victim = None

        # ═══ أدرينالين ضد الجرّاح ═══
        if surgeon_kill:
            med = g["med_items"].get(surgeon_kill)
            if med and med["item"] == "adrenaline" and not med.get("used"):
                med["used"] = True
                surgeon_kill = None
                was_saved = True
                save_method = "adrenaline"

        # ═══ الممرّض ═══
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

        # ═══ المراقب ═══
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

        # ═══ المرعوب (بعد التبديل) ═══
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

        # ═══ أسماء للعرض ═══
        doc_fail_name = pname(doc_fail_victim, pp[doc_fail_victim]["name"]) if doc_fail_victim else None
        doc_fail_role = ROLE_DISPLAY.get(pp[doc_fail_victim]["role"], "?") if doc_fail_victim else None
        surg_kill_name = pname(surgeon_kill, pp[surgeon_kill]["name"]) if surgeon_kill else None
        surg_kill_role = ROLE_DISPLAY.get(pp[surgeon_kill]["role"], "?") if surgeon_kill else None

    # ═══════════ الصباح (خارج القفل) ═══════════
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

    # ═══ رسائل الحالات ═══
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

    # ═══ خطأ الطبيب ═══
    if doctor_failed and doc_fail_victim:
        with bot_lock:
            if not valid_game(cid, gid):
                return
            kill_player(games[cid], doc_fail_victim)
            ally_dead = kill_ally(games[cid], doc_fail_victim)
            games[cid]["stats"]["doc_fails"] += 1
        mute_player(cid, doc_fail_victim)
        safe_send(cid,
            f"💉💀 <b>{doc_fail_name}</b>\n\n"
            f"<i>{random.choice(DOCTOR_FAIL_SCENES)}</i>\n\n"
            f"🎭 {doc_fail_role}")
        for ally_uid in ally_dead:
            _announce_ally_death(cid, gid, ally_uid)
        if not safe_sleep(cid, gid, 2):
            return

    # ═══ الإنقاذ (سينمائي) ═══
    if was_saved:
        scene = random.choice(SAVE_SCENES)
        for line in scene:
            if not is_game_active(cid, gid):
                return
            safe_send(cid, line)
            time.sleep(2)
        if not safe_sleep(cid, gid, 1):
            return

    # ═══ قتل الجرّاح (سينمائي) ═══
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
            ally_dead = kill_ally(games[cid], surgeon_kill)
            games[cid]["last_gasp_pending"][surgeon_kill] = True
            games[cid]["phase"] = "last_gasp_wait"

        mute_player(cid, surgeon_kill)
        safe_pm(surgeon_kill,
            "🩸 <i>أنفاسك الأخيرة… اكتب حتى 5 كلمات الآن</i>")

        for ally_uid in ally_dead:
            _announce_ally_death(cid, gid, ally_uid)

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

    # ═══ السم ═══
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
            ally_dead_t = kill_ally(games[cid], tgt)
            ally_dead_n = []
            if not is_evil:
                if pp2[nu]["alive"]:
                    kill_player(games[cid], nu)
                    ally_dead_n = kill_ally(games[cid], nu)
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
            safe_send(cid,
                f"💊 <b>{tn_}</b> <i>سقط مسموماً</i>  ·  {tgt_role}")
            safe_pm(nu, "💊 <i>أصبت هدفاً شريراً… حقنتك عادت ممتلئة</i>")

        for a_uid in ally_dead_t + ally_dead_n:
            _announce_ally_death(cid, gid, a_uid)
        if not safe_sleep(cid, gid, 1):
            return

    # ═══ فحص فوز ═══
    if check_win_safe(cid, gid):
        return

    # ═══ المرعوب (خاص) ═══
    for s in screams:
        safe_pm(s["screamer"],
            f"😱 <i>أحسست بظل يقترب…</i> {s['visitor_name']}")

    # ═══ المراقب (خاص) ═══
    for obs in observer_results:
        if obs["sedated"]:
            safe_pm(obs["uid"],
                "💉 <i>كل شيء ضبابي… المخدّر أعماك</i>")
        else:
            safe_pm(obs["uid"],
                f"👁 كشفت ملف <b>{obs['name']}</b> → {obs['role']}")
            # تحديث بروفايل
            prof = get_profile(obs["uid"])
            prof["reveals_as_obs"] = prof.get("reveals_as_obs", 0) + 1
            update_hall("observer_reveals", obs["uid"])

    # ═══ ملف ذهبي (متجر) ═══
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

    # ═══ ترقية المخدّر ═══
    _try_promote_anesthetist(cid, gid)

    # ═══ AFK (بعد جولة كاملة) ═══
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

    # ═══ صندوق إمداد ═══
    do_medical_drop(cid, gid)

    if not safe_sleep(cid, gid, 1):
        return

    start_discussion(cid, gid)


def _announce_ally_death(cid, gid, ally_uid):
    """إعلان موت الحليف"""
    mute_player(cid, ally_uid)
    with bot_lock:
        if not valid_game(cid, gid):
            return
        aln = pname(ally_uid, games[cid]["players"][ally_uid]["name"])
        alr = ROLE_DISPLAY.get(games[cid]["players"][ally_uid]["role"], "?")
    safe_send(cid, f"💔 {aln} <i>سقط مع حليفه…</i>\n🎭 {alr}")


def _try_promote_anesthetist(cid, gid):
    """ترقية المخدّر إذا مات الجرّاح"""
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


# ══════════════ النقاش ══════════════
def start_discussion(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        g["phase"] = "discussion"
        g["last_activity"] = time.time()
        g["suspect_votes"] = {}
        g["whisper_used"] = set()
        alive_count = len(get_alive(cid))
        gid = g["game_id"]

    open_discussion(cid)

    safe_send(cid,
        f"💬 <b>النقاش مفتوح</b>  ·  👥 {alive_count} أحياء\n\n"
        f"<i>اتّهموا… دافعوا… استخدموا /suspect و /whisper\n"
        f"معكم {DISCUSS_TIME} ثانية</i>")

    # منظار (spy_glass)
    with bot_lock:
        if valid_game(cid, gid):
            for uid_spy, p_spy in games[cid]["players"].items():
                if p_spy["alive"] and has_item(uid_spy, "spy_glass"):
                    targets_spy = get_alive_except(cid, uid_spy)
                    if targets_spy:
                        mk_spy = types.InlineKeyboardMarkup(row_width=2)
                        mk_spy.add(*[types.InlineKeyboardButton(
                            p["name"], callback_data=f"spy_{cid}_{t}")
                            for t, p in targets_spy.items()])
                        safe_pm(uid_spy,
                            "🔭 <b>المنظار جاهز… اختر من تتجسس عليه</b>",
                            reply_markup=mk_spy)

    if not safe_sleep(cid, gid, DISCUSS_TIME):
        return

    # عرض مقياس الشك
    show_suspect_bar(cid)

    if not safe_sleep(cid, gid, 2):
        return

    start_voting(cid, gid)


# ══════════════ التصويت ══════════════
def start_voting(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        games[cid]["phase"] = "voting"
        games[cid]["votes"] = {}
        games[cid]["last_activity"] = time.time()
        gid = games[cid]["game_id"]

    silence_all(cid)

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        "⚖️ أدلِ بحكمك",
        url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))

    vote_msg = safe_send(cid,
        f"⚖️ <b>وقت الحساب</b>\n\n"
        f"<i>من يستحق المحرقة؟ معكم {VOTE_TIME} ثانية</i>",
        reply_markup=mk)

    if vote_msg:
        safe_pin(cid, vote_msg.message_id)
        with bot_lock:
            if valid_game(cid, gid):
                games[cid]["pinned_mids"].append(vote_msg.message_id)

    if not safe_sleep(cid, gid, VOTE_TIME):
        return

    tally_trial(cid, gid)


# ══════════════ التصويت الدرامي ══════════════
def tally_trial(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if g["phase"] != "voting":
            return
        votes = dict(g["votes"])
        g["silenced"] = set()
        gid = g["game_id"]

        # إزالة أصوات المخدّرين
        to_remove = []
        for k in votes:
            if isinstance(k, str) and k.startswith("i_"):
                try:
                    iuid = int(k.replace("i_", ""))
                    if iuid in g["sedated_current"]:
                        to_remove.append(k)
                except:
                    pass
        for k in to_remove:
            del votes[k]

        if not votes:
            no_votes = True
            vote_list = []
            top = []
        else:
            no_votes = False
            counts = {}
            for v in votes.values():
                counts[v] = counts.get(v, 0) + 1
            mx = max(counts.values())
            top = [t for t, v in counts.items() if v == mx]
            # تجهيز قائمة درامية
            vote_list = []
            for voter_uid, target_uid in votes.items():
                if isinstance(voter_uid, int) and voter_uid in g["players"]:
                    vote_list.append({
                        "voter": pname(voter_uid, g["players"][voter_uid]["name"]),
                        "target": pname(target_uid, g["players"][target_uid]["name"]),
                        "target_name": g["players"][target_uid]["name"],
                    })
            random.shuffle(vote_list)

    with bot_lock:
        if valid_game(cid, gid):
            for mid in games[cid]["pinned_mids"]:
                safe_unpin(cid, mid)
            games[cid]["pinned_mids"] = []

    if no_votes:
        safe_send(cid,
            "🤷 <i>صمت مطبق… لا أحد أشار بإصبعه\n"
            "الظلام قادم مجدداً</i>")
        if not safe_sleep(cid, gid, 2):
            return
        start_room_choosing(cid, gid)
        return

    # ═══ كشف الأصوات واحداً واحداً ═══
    safe_send(cid, "📨 <b>تُفتح الأصوات…</b>")
    if not safe_sleep(cid, gid, 2):
        return

    for i, v in enumerate(vote_list):
        if not is_game_active(cid, gid):
            return
        safe_send(cid,
            f"📩 الصوت {i+1}:\n"
            f"  {v['voter']} ← صوّت على → {v['target']}")
        time.sleep(2)

    if not safe_sleep(cid, gid, 1):
        return

    if len(top) == 1:
        sus = top[0]
        with bot_lock:
            if not valid_game(cid, gid):
                return
            sn = pname(sus, games[cid]["players"][sus]["name"])
            games[cid]["defense_target"] = sus

        # ═══ مرحلة الدفاع ═══
        start_defense(cid, gid, sus)
    else:
        names = []
        with bot_lock:
            if not valid_game(cid, gid):
                return
            for t in top:
                names.append(pname(t, games[cid]["players"][t]["name"]))
        safe_send(cid,
            f"🤝 <i>تعادل بين {' و '.join(names)}… لا إعدام</i>")
        if not safe_sleep(cid, gid, 2):
            return
        start_room_choosing(cid, gid)


# ══════════════ دفاع المتهم ══════════════
def start_defense(cid, gid, sus_uid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        g = games[cid]
        g["phase"] = "defense"
        g["defense_target"] = sus_uid
        sn = pname(sus_uid, g["players"][sus_uid]["name"])

    # فتح الكلام للمتهم فقط
    silence_all(cid)
    unmute_player(cid, sus_uid)

    safe_send(cid,
        f"⚖️ <b>{sn} في قفص الاتهام</b>\n\n"
        f"🎤 <i>لديه {DEFENSE_TIME} ثانية للدفاع عن نفسه…\n"
        f"الباقي يستمعون بصمت</i>")

    if not safe_sleep(cid, gid, DEFENSE_TIME):
        return

    # مرحلة التأكيد
    with bot_lock:
        if not valid_game(cid, gid):
            return
        games[cid]["phase"] = "confirming"
        games[cid]["confirm_votes"] = {"yes": set(), "no": set()}
        games[cid]["confirm_target"] = sus_uid
        sn2 = pname(sus_uid, games[cid]["players"][sus_uid]["name"])

    silence_all(cid)

    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("🔥 حرق (0)", callback_data=f"cf_{cid}_y"),
        types.InlineKeyboardButton("🕊 عفو (0)", callback_data=f"cf_{cid}_n"))

    safe_send(cid,
        f"⚖️ <b>الحكم على {sn2}</b>\n\n"
        f"<i>حرق أم عفو؟ المتهم لا يصوّت\n"
        f"معكم {CONFIRM_TIME} ثانية</i>",
        reply_markup=mk)

    if not safe_sleep(cid, gid, CONFIRM_TIME):
        return

    resolve_confirm(cid, gid)


# ══════════════ نتيجة الحكم ══════════════
def resolve_confirm(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        if g["phase"] != "confirming":
            return
        cv = g["confirm_votes"]
        yc, nc = len(cv["yes"]), len(cv["no"])
        sus = g.get("confirm_target")
        pp = g["players"]
        gid = g["game_id"]
        if not sus or sus not in pp:
            g["phase"] = "morning"
            return
        sn = pname(sus, pp[sus]["name"])
        sr = pp[sus]["role"]
        sd = ROLE_DISPLAY.get(sr, sr)
        sus_team = get_original_team(g, sus)

    if yc > nc:
        # ═══ حرق ═══
        with bot_lock:
            if not valid_game(cid, gid):
                return
            kill_player(games[cid], sus)
            ally_dead = kill_ally(games[cid], sus)
            games[cid]["will_pending"][sus] = True
            games[cid]["phase"] = "will_wait"

        mute_player(cid, sus)

        if sus_team == "evil":
            flavor = "احترق الشر معه… أخيراً"
        elif sus_team == "psycho":
            flavor = "ابتسامته لم تختفِ حتى وهو يحترق…"
        elif sus_team == "neutral":
            flavor = "المحرّض سقط… لكن هل كان يستحق؟"
        else:
            flavor = "هل أحرقتم بريئاً؟ الندم قادم…"

        safe_send(cid,
            f"🔥 <b>{sn} في المحرقة</b>\n\n"
            f"🎭 {sd}\n\n"
            f"<i>{flavor}</i>")

        safe_pm(sus,
            "🔥 <i>النيران تلتهمك… اكتب وصيتك الأخيرة</i>\n\n"
            "<i>(حتى 500 حرف)</i>")

        for a_uid in ally_dead:
            _announce_ally_death(cid, gid, a_uid)

        # تحديث دقة التصويت
        with bot_lock:
            if valid_game(cid, gid):
                surg_uid = games[cid]["stats"].get("surgeon_uid")
                for voter_uid in cv["yes"]:
                    prof = get_profile(voter_uid)
                    prof["vote_accuracy"][1] += 1
                    if sus == surg_uid or sus_team in ("evil",):
                        prof["vote_accuracy"][0] += 1

        # ═══ قنبلة المجنون ═══
        if sr == "Psychopath":
            trigger_bomb = False
            with bot_lock:
                if valid_game(cid, gid):
                    bomb = games[cid]["bomb"]
                    if bomb["is_set"] and bomb.get("owner") == sus:
                        trigger_bomb = True
                        games[cid]["stats"]["bomb_exploded"] = True
            if trigger_bomb:
                if not safe_sleep(cid, gid, 2):
                    return
                trigger_bomb_phase(cid, gid)
                return
            else:
                safe_send(cid,
                    "🤡 <i>المجنون نسي الفتيل… محظوظون</i>")

        # ═══ ترقية المخدّر ═══
        _try_promote_anesthetist(cid, gid)

        if check_win_safe(cid, gid):
            return

        if not safe_sleep(cid, gid, WILL_TIME):
            return

        with bot_lock:
            if valid_game(cid, gid):
                games[cid]["will_pending"][sus] = False

        start_room_choosing(cid, gid)
    else:
        # ═══ عفو ═══
        safe_send(cid, f"🕊 <b>{sn} نجا من المحرقة… هذه المرة</b>")
        if not safe_sleep(cid, gid, 2):
            return
        start_room_choosing(cid, gid)


# ══════════════ القنبلة ══════════════
def trigger_bomb_phase(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        g["phase"] = "bomb"
        g["bomb"]["defuser"] = None
        bomb_q = g["bomb"]["q"]
        gid = g["game_id"]

    open_discussion(cid)

    safe_send(cid,
        f"💣💣💣 <b>قنبلة!</b>\n\n"
        f"❓ <b>{bomb_q}</b>\n\n"
        f"<i>اكتبوا الجواب هنا بسرعة!\n"
        f"معكم {BOMB_TIME} ثانية قبل الانفجار!</i>")

    end_t = time.time() + BOMB_TIME
    while time.time() < end_t:
        time.sleep(1)
        with bot_lock:
            if not valid_game(cid, gid):
                return
            if games[cid]["phase"] == "defused":
                break

    with bot_lock:
        if not valid_game(cid, gid):
            return
        phase = games[cid]["phase"]
        defuser_uid = games[cid]["bomb"].get("defuser")
        if defuser_uid and defuser_uid in games[cid]["players"]:
            defuser_name = pname(defuser_uid,
                games[cid]["players"][defuser_uid]["name"])
            games[cid]["stats"]["bomb_defuser"] = defuser_uid
        else:
            defuser_name = None

    if phase == "defused":
        dn = defuser_name or "أحدهم"
        safe_send(cid,
            f"✅ <b>{dn} أبطل القنبلة في آخر لحظة!</b>\n\n"
            f"<i>نفس واحد…</i>")
        if not check_win_safe(cid, gid):
            if not safe_sleep(cid, gid, 2):
                return
            start_room_choosing(cid, gid)
    else:
        with bot_lock:
            if not valid_game(cid, gid):
                return
            raw = games[cid]["bomb"]["raw"]
        safe_send(cid,
            f"💥💥💥 <b>BOOM!</b>\n\n"
            f"💡 الجواب كان: <b>{raw}</b>\n\n"
            f"🤡 <i>المجنون يضحك من الجحيم…</i>")
        with bot_lock:
            if valid_game(cid, gid):
                games[cid]["winners_team"] = "psycho"
        show_results(cid,
            "🤡 <b>المجنون فجّر المستشفى… لا ناجين</b>")


# ══════════════ بدء المستشفى ══════════════
def start_hospital(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            return
        g = games[cid]
        pp = g["players"]
        if len(pp) < MIN_HOSPITAL:
            safe_send(cid,
                f"⚠️ <i>نحتاج {MIN_HOSPITAL} نزلاء على الأقل…</i>")
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
            # ═══ إصلاح: تعيين ability_night لكل الأدوار ═══
            if p["role"] not in INSTANT_ROLES and p["role"] not in ("Psychopath", "Screamer"):
                g["ability_night"][uid] = 2
            # تحديث بروفايل
            prof = get_profile(uid)
            prof["roles_played"][p["role"]] = prof["roles_played"].get(p["role"], 0) + 1
        # evil_chat_ids
        for uid, p in pp.items():
            if g["original_team"].get(uid) == "evil":
                g["evil_chat_ids"].add(uid)
        g["phase"] = "roles_reveal"
        g["game_started_at"] = time.time()
        gid = g["game_id"]

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(
        "📂 افتح ملفك السري",
        url=f"https://t.me/{BOT_USERNAME}?start=role_{cid}"))
    safe_send(cid,
        "📋 <b>وُزّعت الملفات السرية…</b>\n\n"
        "<i>كل واحد يكتشف مصيره من الزر… لا تتأخر 👇</i>",
        reply_markup=mk)

    if not safe_sleep(cid, gid, 12):
        return

    with bot_lock:
        if not valid_game(cid, gid):
            return
        player_lines = []
        for u, p in games[cid]["players"].items():
            player_lines.append(f"  🔹 {pname_vip(u, p['name'])}")
        roles_in = [p["role"] for p in games[cid]["players"].values()]
        random.shuffle(roles_in)
        archive = [f"  ▫️ {ROLE_DISPLAY.get(r, r)}" for r in roles_in]

    safe_send(cid,
        f"🏥 <b>أُغلقت أبواب المستشفى</b>\n\n"
        f"👥 النزلاء:\n\n" + "\n\n".join(player_lines) +
        f"\n\n🗂 <i>الأدوار المتاحة (مخلوطة):</i>\n\n" +
        "\n".join(archive))

    # تعيين الجوكر
    assign_joker(cid, gid)

    if not safe_sleep(cid, gid, 4):
        return

    # بدء اختيار الغرف ثم الليل
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
    team_label = {
        "evil": "🔴 فريق الظلام",
        "psycho": "🟡 مستقل",
        "good": "🟢 فريق النور",
        "neutral": "⚪ محايد",
    }.get(team, "")
    safe_pm(uid, f"📂 <b>ملفك السري</b>\n\n{desc}\n\n🏷 {team_label}")

    if evil_teammates:
        time.sleep(1)
        teammates_txt = "\n".join([f"  🔴 {et}" for et in evil_teammates])
        safe_pm(uid,
            f"🌑 <b>رفاقك في الظلام:</b>\n\n{teammates_txt}\n\n"
            f"<i>تتواصلون بالخاص أثناء الليل…</i>")

    if role == "Psychopath":
        with bot_lock:
            if cid in games:
                games[cid]["psycho_phase"][uid] = "q"
        time.sleep(1)
        safe_pm(uid,
            "🤡 <b>حان وقت التلغيم</b>\n\n"
            "✏️ أرسل <b>سؤال اللغز</b>… إذا أحرقوك سيحتاجون الجواب:")
        return

    # الأدوار غير الفورية — الإعلام بتوقيت القدرة
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

    safe_send(cid,
        "🗳 <b>بدأت حلبة التصويت!</b>\n\n"
        "<i>كل لاعب يطرح سؤالاً بدوره…</i>")
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
        mk.add(types.InlineKeyboardButton(
            "🎤 استلم الميكروفون",
            url=f"https://t.me/{BOT_USERNAME}?start=ask_{cid}"))

        ask_msg = safe_send(cid,
            f"🎤 <b>الجولة {rnd}/{total}</b>  ·  {an}\n\n"
            f"<i>يختار سلاحه… معه {VOTE_GAME_ASK_TIME} ثانية</i>",
            reply_markup=mk)

        if ask_msg:
            with bot_lock:
                if valid_game(cid, gid):
                    games[cid]["ask_msg_id"] = ask_msg.message_id

        # انتظار السؤال
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
        safe_send(cid,
            f"💬 <i>استراحة نقاش… معكم {VOTE_GAME_DISCUSS_TIME} ثانية</i>")
        if not safe_sleep(cid, gid, VOTE_GAME_DISCUSS_TIME):
            return

    show_vote_game_end(cid, expected_gid)


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
        types.InlineKeyboardButton("❓ سؤال وجواب",
            callback_data=f"asktype_{cid}_qa"),
        types.InlineKeyboardButton("🗳 سؤال وتصويت",
            callback_data=f"asktype_{cid}_vote"))
    safe_pm(uid,
        "🎤 <b>اختر سلاحك:</b>\n\n"
        "<i>سؤال يُجاب عليه… أم سؤال يُصوَّت عليه؟</i>",
        reply_markup=mk)


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
        bot.edit_message_text(
            f"✅ <b>{label}</b>\n\n✏️ <i>اكتب سؤالك الآن:</i>",
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
    safe_pm(uid,
        "🌑 <i>قناة الظلام مفتوحة… اكتب هنا للتواصل مع رفاقك أثناء الليل</i>")


# ══════════════ نتائج جولة التصويت ══════════════
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
        msg = "🤷 <i>لم يصوّت أحد… صمت مريب</i>"
    else:
        msg = "🗳 <b>النتائج:</b>\n\n" + "\n\n".join(result_lines)
    if no_vote:
        msg += "\n\n❌ لم يصوّتوا: " + " · ".join(no_vote)
    safe_send(cid, msg)


# ══════════════ نتائج جولة سؤال/جواب ══════════════
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
            # ═══ إصلاح: استثناء السائل ═══
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
        header += "<i>لا أحد أجاب… صمت مطلق</i>"
    if no_answer:
        header += "\n\n❌ لم يجيبوا: " + " · ".join(no_answer)
    safe_send(cid, header)


# ══════════════ إعلان أسئلة حلبة التصويت ══════════════
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
    mk.add(types.InlineKeyboardButton(
        "🗳 صوّت الآن",
        url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))

    safe_send(cid,
        f"🗳 <b>الجولة {rnd}/{total}</b>\n\n"
        f"🎤 {an} يسأل:\n"
        f"❓ «<b>{question}</b>»\n\n"
        f"<i>صوّتوا على شخص! معكم {VOTE_GAME_VOTE_TIME} ثانية</i>",
        reply_markup=mk)


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
    mk.add(types.InlineKeyboardButton(
        "✏️ أجب في الخاص",
        url=f"https://t.me/{BOT_USERNAME}?start=answer_{cid}"))

    safe_send(cid,
        f"❓ <b>الجولة {rnd}/{total}</b>\n\n"
        f"🎤 {an} يسأل:\n"
        f"❓ «<b>{question}</b>»\n\n"
        f"<i>أجيبوا في الخاص! معكم {VOTE_GAME_ANSWER_TIME} ثانية</i>",
        reply_markup=mk)


# ══════════════ نهاية حلبة التصويت ══════════════
def show_vote_game_end(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid):
            safe_send(cid, "🏁 <b>انتهت الحلبة</b>")
            return
        g = games[cid]
        elapsed = int(time.time() - g.get("game_started_at", time.time()))
        em, es = divmod(elapsed, 60)
        n = len(g["players"])
        player_lines = []
        for u, p in g["players"].items():
            player_lines.append(f"  🔹 {pname_vip(u, p['name'])}")
        for uid in g["players"]:
            add_coins(uid, LOSE_REWARD)
            add_xp(uid, 5)

    safe_send(cid,
        f"🏁 <b>انتهت حلبة التصويت</b>\n\n"
        f"👥 المشاركون ({n}):\n\n" + "\n\n".join(player_lines) +
        f"\n\n⏱ {em}:{es:02d}\n"
        f"💰 كل مشارك حصل على +{LOSE_REWARD} 🪙\n\n"
        f"🔄 /vote  ·  /hospital")
    force_cleanup(cid)


# ══════════════ حساب الألقاب ══════════════
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

        # الثرثار
        if mc:
            top_talker = max(mc, key=mc.get)
            if mc[top_talker] > 0:
                titles.setdefault(top_talker, []).append("chatterbox")

        # الصامت
        all_players = list(pp.keys())
        if all_players:
            min_talk = min(all_players, key=lambda u: mc.get(u, 0))
            if mc.get(min_talk, 0) <= 2:
                titles.setdefault(min_talk, []).append("silent")

        # شارلوك
        vs = stats.get("voted_surgeon", set())
        surg_uid = stats.get("surgeon_uid")
        if vs and surg_uid and not pp.get(surg_uid, {}).get("alive", True):
            for det in vs:
                titles.setdefault(det, []).append("sherlock")

        # ملاك الرحمة
        if stats.get("doc_saves", 0) > 0:
            doc_uid = next((u for u, p in pp.items()
                           if p["role"] == "Doctor"), None)
            if doc_uid:
                titles.setdefault(doc_uid, []).append("angel")

        # حاصد الأرواح
        if surg_uid and surg_uid in alive:
            titles.setdefault(surg_uid, []).append("reaper")

        # أول دم
        fd = stats.get("first_death")
        if fd and fd in pp:
            titles.setdefault(fd, []).append("first_blood")

        # الناجي
        for u in alive:
            titles.setdefault(u, []).append("survivor")

        # المُفخّخ
        if stats.get("bomb_exploded"):
            psycho_uid = next((u for u, p in pp.items()
                              if p["role"] == "Psychopath"), None)
            if psycho_uid:
                titles.setdefault(psycho_uid, []).append("bomber")

        # نازع الفتيل
        bd = stats.get("bomb_defuser")
        if bd and bd in pp:
            titles.setdefault(bd, []).append("defuser")

        # الشبح
        voted_target_uids = set(stats.get("voted_against", {}).keys())
        for u in pp:
            if u not in voted_target_uids:
                titles.setdefault(u, []).append("phantom")

        # المطعون
        for u in stats.get("scalpel_kills", set()):
            if u in pp:
                titles.setdefault(u, []).append("betrayed")

        # الحليف
        for pair in g.get("ally_pairs", set()):
            for u in pair:
                if u in pp:
                    titles.setdefault(u, []).append("allied")

    return titles


# ══════════════ عرض النتائج ══════════════
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
        sp = sorted(pp.items(),
                    key=lambda x: order.get(get_original_team(g, x[0]), 4))

        for uid, p in sp:
            rd = ROLE_DISPLAY.get(p["role"], p["role"])
            team = get_original_team(g, uid)
            ti = {"evil": "🔴", "psycho": "🟡",
                  "good": "🟢", "neutral": "⚪"}.get(team, "⚪")
            st = "💀" if not p["alive"] else "✅"
            player_titles = titles_map.get(uid, [])
            title_icons = ""
            if player_titles:
                title_icons = " " + " ".join(
                    [TITLE_DEFS[t]["icon"] for t in player_titles if t in TITLE_DEFS])
            lines.append(f"  {ti}  {st}  {pname(uid, p['name'])}  ·  {rd}{title_icons}")

        # مكافآت
        for uid, p in pp.items():
            team = get_original_team(g, uid)
            is_winner = False
            if winners_team == "psycho" and p["role"] == "Psychopath":
                is_winner = True
            elif winners_team == "neutral" and team == "neutral":
                is_winner = True
            elif winners_team and team == winners_team:
                is_winner = True

            # المحرّض يفوز لو نجا
            if team == "neutral" and p["alive"]:
                is_winner = True

            reward = WIN_REWARD if is_winner else LOSE_REWARD
            xp_gain = 20 if is_winner else 5

            player_titles = titles_map.get(uid, [])
            if "sherlock" in player_titles or "reaper" in player_titles:
                reward += MVP_BONUS
                xp_gain += 10

            # مكافأة التحالف
            for pair in g.get("ally_pairs", set()):
                if uid in pair:
                    partner = [u for u in pair if u != uid]
                    if partner:
                        partner_alive = pp.get(partner[0], {}).get("alive", False)
                        if p["alive"] and partner_alive:
                            reward += ALLY_BONUS
                            xp_gain += 5

            add_coins(uid, reward)
            add_xp(uid, xp_gain)

            # تحديث البروفايل
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

            # ألقاب البروفايل
            for t_id in titles_map.get(uid, []):
                if t_id not in prof["titles_earned"]:
                    prof["titles_earned"].append(t_id)

            # إحصائيات خاصة
            if p["role"] == "Surgeon":
                kills = len([d for d in g["dead_list"]
                           if d != uid and g["stats"].get("surgeon_uid") == uid])
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

        # ألقاب للعرض
        for uid, t_list in titles_map.items():
            if uid in pp:
                pn = pp[uid]["name"]
                for t_id in t_list:
                    td = TITLE_DEFS.get(t_id)
                    if td:
                        title_lines.append(
                            f"  {td['icon']}  <b>{td['name']}</b>  ←  {pname(uid, pn)}")

    # ═══ رسالة النتائج ═══
    result_text = (
        f"{winner_msg}\n\n"
        f"{'━' * 20}\n\n"
        + "\n\n".join(lines) +
        f"\n\n{'━' * 20}\n\n"
        f"✅ أحياء: {ac}  ·  💀 ضحايا: {dc}  ·  ⏱ {em}:{es:02d}\n\n"
        f"🔴 = ظلام  🟢 = نور  🟡 = مستقل  ⚪ = محايد\n\n"
        f"🔄 /hospital  ·  /vote"
    )
    safe_send(cid, result_text)

    # ═══ رسالة الألقاب (منفصلة) ═══
    if title_lines:
        time.sleep(1)
        titles_text = (
            "🏅 <b>ألقاب هذه الجولة</b>\n\n"
            + "\n\n".join(title_lines)
        )
        safe_send(cid, titles_text)

    # ═══ رسالة المكافآت (منفصلة) ═══
    if reward_lines:
        time.sleep(1)
        rewards_text = (
            "💰 <b>المكافآت</b>\n\n"
            + "\n\n".join(reward_lines)
        )
        safe_send(cid, rewards_text)

    force_cleanup(cid)

# ══════════════ إصلاحات وإضافات نهائية ══════════════

# ═══ دالة فتح الهمسة من dispatch (كانت مفقودة) ═══
def dispatch_whisper_open(uid, param, m):
    """عندما يضغط أحد على زر فتح الهمسة من start"""
    # يتم التعامل معها عبر callback xwopen_ بالفعل
    pass


# ═══ إضافة أمر /rooms_cancel قبل اللعبة ═══
@bot.message_handler(
    func=lambda m: (m.chat.type in ("group", "supergroup")
                    and m.text and m.text.split()[0].split("@")[0].lower() == "/rooms_cancel")
)
def cmd_rooms_cancel(m):
    """تعطيل نظام الغرف قبل بدء اللعبة"""
    cid, uid = m.chat.id, m.from_user.id
    delete_msg(cid, m.message_id)
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


# ═══ تعديل start_room_choosing ليتحقق من rooms_enabled ═══
_original_start_room_choosing = start_room_choosing

def start_room_choosing_wrapper(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid):
            return
        rooms_on = games[cid].get("rooms_enabled", True)
    if rooms_on:
        _original_start_room_choosing(cid, gid)
    else:
        # كل اللاعبين في غرفة 1
        with bot_lock:
            if not valid_game(cid, gid):
                return
            g = games[cid]
            g["room_choices"] = {}
            for uid, p in g["players"].items():
                if p["alive"]:
                    g["room_choices"][uid] = 1
        start_night(cid, gid)

start_room_choosing = start_room_choosing_wrapper


# ═══ تعديل /commands لتشمل rooms_cancel ═══
_original_do_commands = do_commands

def do_commands_wrapper(m):
    cid = m.chat.id
    safe_send(cid,
        "📖 <b>أوامر المستشفى الملعون</b>\n\n"

        "━━━ 🏥 <b>بدء اللعبة</b> ━━━\n"
        "🏥 /hospital — افتح أبواب المستشفى\n"
        "🗳 /vote — افتح حلبة التصويت\n"
        "🚀 /force_start — ابدأ فوراً\n"
        "⏱ /time [ثواني] — أضف وقت انتظار\n"
        "🛑 /cancel — أغلق المستشفى\n"
        "🏠 /rooms_cancel — تبديل نظام الغرف\n\n"

        "━━━ 🤝 <b>التحالفات (قبل اللعبة)</b> ━━━\n"
        "🤝 /ally @اسم — اطلب تحالفاً\n"
        "❌ /cancel_ally — ألغِ تحالفك وغادر\n"
        "<i>الحلفاء يشاركون المصير\n"
        "إذا مات أحدهما مات الآخر\n"
        "لكنهما لا يعرفان دور بعضهما</i>\n\n"

        "━━━ 💬 <b>أثناء النقاش</b> ━━━\n"
        "🔍 /suspect @اسم — سجّل شكّك (مجهول)\n"
        "💌 /whisper @اسم — همسة سرية لشخص\n"
        "🗡️ /kill — مشرط صدئ (إن وجد)\n\n"

        "━━━ 🏠 <b>نظام الغرف</b> ━━━\n"
        "<i>قبل كل ليلة تختار غرفة من 4\n"
        "قدراتك تعمل فقط على رفاق الغرفة\n"
        "تتحدث مع رفاق غرفتك بالخاص ليلاً\n"
        "الجرّاح لا يقتل حلفاءه\n"
        "الصباح: الكل يخرج للنقاش العام</i>\n\n"

        "━━━ 🃏 <b>الجوكر</b> ━━━\n"
        "<i>لاعب عشوائي يحصل بطاقة جوكر\n"
        "تُستخدم مرة واحدة عبر الأزرار\n"
        "خيارات: إلغاء تصويت · حماية · كشف · صوت مزدوج · تخطّي ليلة\n"
        "تحذير: تكشف هويتك ودورك!</i>\n\n"

        "━━━ 📊 <b>الشك والتصويت</b> ━━━\n"
        "<i>/suspect @اسم أثناء النقاش\n"
        "نهاية النقاش يظهر مقياس الشك\n"
        "التصويت يُكشف درامياً صوتاً بصوت\n"
        "المتهم يحصل وقت للدفاع قبل الحكم</i>\n\n"

        "━━━ 📊 <b>المعلومات (خاص)</b> ━━━\n"
        "🎭 /myrole — دورك الحالي\n"
        "🟢 /alive — قائمة الأحياء\n"
        "📜 /roles — ملفات الأدوار\n"
        "📖 /rules — قواعد البقاء\n"
        "📊 /profile — ملفك وإحصائياتك\n"
        "💰 /wallet — محفظتك\n"
        "🛒 /shop — المتجر\n\n"

        "━━━ 🏆 <b>الإنجازات</b> ━━━\n"
        "🏆 /hall — جدار الشهرة\n\n"

        "━━━ ⚖️ <b>نظام الفوز</b> ━━━\n"
        "🟢 النور: تطهير كل الأشرار\n"
        "🔴 الظلام: إبادة النور\n"
        "🟡 المجنون: القنبلة أو البقاء الأخير\n"
        "⚪ المحرّض: النجاة حتى النهاية\n"
        "<i>طريق مسدود؟ البوت يحسم بذكاء\n"
        "جرّاح+طبيب فقط = الجرّاح يفوز\n"
        "شرير بلا أنياب = النور ينتصر</i>")

do_commands = do_commands_wrapper


# ═══ إعادة ربط أمر المجموعة ═══
_original_group_cmd = group_cmd

@bot.message_handler(
    func=lambda m: m.chat.type in ("group", "supergroup") and m.text and m.text.startswith("/")
)
def group_cmd_final(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split()[0].split("@")[0].lower()

    deletable = {"/hospital", "/vote", "/force_start", "/cancel",
                 "/done", "/time", "/ally", "/cancel_ally",
                 "/suspect", "/whisper", "/commands", "/hall",
                 "/rooms_cancel"}
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
    elif raw == "/ally":
        do_ally(m)
    elif raw == "/cancel_ally":
        do_cancel_ally(m)
    elif raw == "/suspect":
        do_suspect(m)
    elif raw == "/whisper":
        do_whisper_group(m)
    elif raw == "/commands":
        do_commands(m)
    elif raw == "/hall":
        do_hall(m)
    elif raw == "/rooms_cancel":
        cmd_rooms_cancel(m)


# ══════════════ التشغيل ══════════════
print("🏥 المستشفى الملعون يعمل…")
print(f"🤖 @{BOT_USERNAME}")
print(f"🔑 المالك: @{OWNER_USERNAME}")
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
