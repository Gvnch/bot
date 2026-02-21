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

# ══════════════ سيرفر Render (لإبقاء البوت نشطاً) ══════════════
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running - The Hospital & Council are Open")
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
# ⚠️ توكن البوت الخاص بك
TOKEN = "8300157614:AAEob3NY0woxB4zhChSy1GCUj1eDZUNyYTQ"

OWNER_USERNAME = "O_SOHAIB_O"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True, num_threads=3)

try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass

try:
    BOT_INFO = bot.get_me()
    BOT_USERNAME = BOT_INFO.username
    print(f"--- Logged in as: {BOT_USERNAME} ---")
except Exception as e:
    print(f"Login Failed: {e}")

# ══════════════ الذاكرة المركزية ══════════════
games = {}
user_to_game = {}
bot_lock = threading.RLock()
wallets_db = {}
profiles_db = {}

# ══════════════ ثوابت التوقيت واللعب ══════════════
MAX_PLAYERS = 15
DEFAULT_WAIT_TIME = 60
INACTIVITY_TIMEOUT = 300

NIGHT_TIME = 45
LAST_GASP_TIME = 30 
DISCUSS_TIME = 45
VOTE_TIME = 30
CONFIRM_TIME = 25
DEFENSE_TIME = 35
BOMB_TIME = 25
ROOM_CHOOSE_TIME = 30

# ثوابت لعبة التصويت /vote
VOTE_GAME_ASK_TIME = 45
VOTE_GAME_VOTE_TIME = 30
VOTE_GAME_ANSWER_TIME = 40

DOCTOR_FAIL_CHANCE = 0.1

ROOM_NAMES = {
    1: "🛏 الجناح A (عنبر هادئ)",
    2: "🛏 الجناح B (عنبر مزدحم)",
    3: "🔬 المختبر (رائحة كيميائية)",
    4: "🏚 القبو (مظلم وبارد)",
    5: "🌑 الممر الرئيسي (مكشوف للجميع)",
}

ASSETS = {
    "NIGHT": "AgACAgQAAxkBAAOAaYVV970SelJjAdfgC2lejaG2UXIAAjcMaxtYrDFQipw_Ve7HzpEBAAMCAAN4AAM4BA",
    "DAY": "AgACAgQAAxkBAAOVaYW5klHrisedX42r1ZlR5rHoBawAAp4Maxt3RDBQDWc7kkg-my0BAAMCAAN5AAM4BA",
    "LOBBY": "CgACAgQAAxkBAAOQaYVbS9aSPzDTHS3eGmnRwL3a0aUAAmAfAAJ3RChQ180c8TNqhjc4BA",
    "VOTE": "AgACAgQAAxkBAANYaYUTJSrHhkDUESz7dLuUONpJWUsAAqoNaxuKXihQitHU1Aa5h9gBAAMCAAN5AAM4BA",
}

# ══════════════ الأدوار والتوجيهات الاحترافية ══════════════
ROLE_DISPLAY = {
    "Surgeon": "🔪 الجرّاح", "Anesthetist": "💉 المخدّر",
    "Instigator": "🧠 المحرّض", "Psychopath": "🤡 المجنون",
    "Doctor": "🩺 الطبيب", "Observer": "👁 المراقب",
    "Swapper": "🛏 عابث الأسرّة", "Patient": "🤕 المريض",
    "Screamer": "😱 المرعوب", "Nurse": "💊 الممرّض",
    "Security": "👮 حارس الأمن",
}

ROLE_GUIDE_SHORT = {
    "Surgeon": "🔪 <b>هويتك: الجرّاح (قائد الأشرار)</b>\n\nأنت سبب هذا الكابوس. هدفك هو تصفية كل من يقف في طريقك حتى تسيطر على المستشفى.\n\n▪️ <b>مهمتك:</b> كل ليلة، ستخرج في الظلام لاختيار ضحية جديدة لتمزيقها بمشرطك.",
    "Anesthetist": "💉 <b>هويتك: المخدّر (فريق الأشرار)</b>\n\nأنت الذراع اليمنى للجراح. حقنك تشل الحركة وتمنع الأخيار من استخدام قدراتهم.\n\n▪️ <b>مهمتك:</b> ابتداءً من الليلة الثانية، يمكنك تخدير شخص ما ليلاً لمنعه من التحرك تماماً.",
    "Instigator": "🧠 <b>هويتك: المحرّض (مستقل/خبيث)</b>\n\nأنت تتلاعب بعقول الجميع لتغيير مسار العدالة.\n\n▪️ <b>مهمتك:</b> يمكنك سلب صوت أحدهم ليلاً ليصبح التصويت لصالحك في الصباح.",
    "Psychopath": "🤡 <b>هويتك: المجنون (منفرد)</b>\n\nأنت لا تكترث لمن يعيش ومن يموت، أنت فقط تريد رؤية العالم يحترق!\n\n▪️ <b>مهمتك:</b> ازرع قنبلتك الليلة. غداً، يجب أن تتلاعب بالجميع ليقوموا بالتصويت على إعدامك. إذا أعدموك... ستنفجر القنبلة وتفوز أنت وحدك!",
    "Doctor": "🩺 <b>هويتك: الطبيب (الأخيار)</b>\n\nأنت بصيص الأمل الأخير في هذا المكان الملعون.\n\n▪️ <b>مهمتك:</b> كل ليلة، اختر مريضاً لإنقاذه. إذا حاول الجراح قتله، ستعترض طريقه وتنقذ حياته.",
    "Observer": "👁 <b>هويتك: المراقب (الأخيار)</b>\n\nعيناك لا تخطئان أبداً. أنت تراقب الجميع من خلف الكاميرات.\n\n▪️ <b>مهمتك:</b> ابتداءً من الليلة الثانية، يمكنك كشف الهوية الحقيقية لأحد اللاعبين السريين.",
    "Swapper": "🛏 <b>هويتك: عابث الأسرّة (الأخيار)</b>\n\nأنت تتسلل ليلاً لتبديل أسرّة المرضى لإرباك القتلة.\n\n▪️ <b>مهمتك:</b> ابتداءً من الليلة الثانية، اختر شخصين وبدّل مكانيهما لحماية الأبرياء من الموت.",
    "Patient": "🤕 <b>هويتك: المريض (الأخيار)</b>\n\nأنت ضعيف الآن، لكن الموت يمنحك الفرصة.\n\n▪️ <b>مهمتك:</b> راقب الجثث. عندما يموت أحدهم، يمكنك التسلل لسرقة هويته وإكمال مسيرته وقدراته.",
    "Screamer": "😱 <b>هويتك: المرعوب (الأخيار)</b>\n\nأعصابك منهارة تماماً. تملك سكيناً حاداً لحماية نفسك لمرة واحدة فقط.\n\n▪️ <b>مهمتك:</b> يمكنك الاختباء والارتجاف (وإذا زارك أحد ستصرخ باسمه). أو يمكنك استخدام سكينك لقتل أي شخص يزورك الليلة بدافع الخوف الأعمى!",
    "Nurse": "💊 <b>هويتك: الممرّض (الأخيار)</b>\n\nتحمل في جيبك حقنة سم قاتلة... لمرة واحدة فقط.\n\n▪️ <b>مهمتك:</b> ابتداءً من الليلة الثانية، يمكنك إنهاء حياة شخص تشك بأنه الجراح. لكن احذر! إذا قتلت بريئاً، ستشرب السم وتنتحر ندماً.",
    "Security": "👮 <b>هويتك: حارس الأمن (الأخيار)</b>\n\nمسدسك محشو برصاصتين لتحقيق العدالة.\n\n▪️ <b>مهمتك:</b> يمكنك إطلاق النار ليلاً. لكن احذر! إذا قتلت أبرياء للمرة الثانية، سيغضب باقي المرضى ويرمونك حياً في المحرقة في الصباح!"
}

ROLE_TEAM = {
    "Surgeon": "evil", "Anesthetist": "evil", "Instigator": "neutral",
    "Doctor": "good", "Observer": "good", "Swapper": "good",
    "Patient": "good", "Psychopath": "psycho", "Screamer": "good", 
    "Nurse": "good", "Security": "good",
}

INSTANT_ROLES = {"Surgeon", "Doctor", "Psychopath", "Patient", "Screamer"}

SHOP_ITEMS = {
    "shield": {"name": "🛡 درع الروح", "price": 120, "desc": "حماية لمرة واحدة ليلاً"},
    "spy_glass": {"name": "🔭 منظار", "price": 90, "desc": "كشف فريق لاعب"},
    "title_vip": {"name": "👑 لقب VIP", "price": 600, "desc": "تاج بجانب الاسم"},
}

# ══════════════ أدوات مساعدة وتنسيق ══════════════
def clean(t, mx=200):
    return html.escape(str(t or "")[:mx].replace('\n', ' ').replace('\r', ''))

def clean_name(t):
    return html.escape(str(t or "مجهول")[:30].replace('\n', '').replace('\r', ''))

def pname(uid, name):
    crown = "👑 " if has_title(uid, "title_vip") else ""
    return f"{crown}<a href='tg://user?id={uid}'><b>{clean_name(name)}</b></a>"

def normalize_arabic(t):
    if not t: return ""
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = t.strip().lower()
    for a, b in [("أ|إ|آ", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")]:
        t = re.sub(a, b, t)
    return re.sub(r'\s+', ' ', t).strip()

def corrupt_text(text):
    words = text.split()
    return " ".join(["..." + w[-1:] if len(w)>1 and random.random()<0.5 else w for w in words])

# ══════════════ الاقتصاد وقواعد البيانات ══════════════
def get_wallet(uid):
    if uid not in wallets_db:
        wallets_db[uid] = {"coins": 0, "inventory": [], "titles": []}
    return wallets_db[uid]

def has_item(uid, item_id):
    w = get_wallet(uid)
    return item_id in w["inventory"] or item_id in w["titles"]

def use_item(uid, item_id):
    w = get_wallet(uid)
    if item_id in w["inventory"]:
        w["inventory"].remove(item_id)
        return True
    return False

def has_title(uid, title_id):
    return title_id in get_wallet(uid)["titles"]

def buy_item(uid, item_id):
    if item_id not in SHOP_ITEMS: return False, "❌ الغرض غير موجود في السوق السوداء."
    w = get_wallet(uid)
    item = SHOP_ITEMS[item_id]
    if w["coins"] < item["price"]: return False, "❌ عذراً، لا تملك رصيداً كافياً."
    
    w["coins"] -= item["price"]
    if item_id.startswith("title_"):
        if item_id in w["titles"]: return False, "❌ أنت تملك هذا اللقب مسبقاً."
        w["titles"].append(item_id)
    else:
        w["inventory"].append(item_id)
    return True, f"✅ تمت الصفقة بنجاح. حصلت على <b>{item['name']}</b>."

def get_profile(uid):
    if uid not in profiles_db:
        profiles_db[uid] = {"games": 0, "wins": 0, "deaths": 0}
    return profiles_db[uid]

# ══════════════ الإرسال والإدارة ══════════════
def safe_send(cid, text, **kw):
    try: return bot.send_message(cid, text, parse_mode="HTML", **kw)
    except: return None

def safe_pm(uid, text, **kw):
    try: return bot.send_message(uid, text, parse_mode="HTML", **kw)
    except: return None

def delete_msg(cid, mid):
    try: bot.delete_message(cid, mid)
    except: pass

def safe_pin(cid, mid):
    try: bot.pin_chat_message(cid, mid, disable_notification=True)
    except: pass

def safe_unpin_all(cid):
    try: bot.unpin_all_chat_messages(cid)
    except: pass

def mute_all(cid):
    try: bot.set_chat_permissions(cid, types.ChatPermissions(can_send_messages=False))
    except: pass

def unmute_all(cid):
    try: bot.set_chat_permissions(cid, types.ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True))
    except: pass

def mute_player(cid, uid):
    try: bot.restrict_chat_member(cid, uid, permissions=types.ChatPermissions(can_send_messages=False))
    except: pass

def unmute_player(cid, uid):
    try: bot.restrict_chat_member(cid, uid, permissions=types.ChatPermissions(
                can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
    except: pass

def silence_all(cid):
    mute_all(cid)
    with bot_lock:
        if cid not in games: return
        uids = list(games[cid]["players"].keys())
    for uid in uids: mute_player(cid, uid)

def open_discussion(cid):
    with bot_lock:
        if cid not in games: return
        dead_u = [u for u, p in games[cid]["players"].items() if not p["alive"]]
        alive_u = [u for u, p in games[cid]["players"].items() if p["alive"]]
    unmute_all(cid)
    time.sleep(0.3)
    for uid in alive_u: unmute_player(cid, uid)
    for uid in dead_u: mute_player(cid, uid)

def force_cleanup(cid):
    with bot_lock:
        if cid in games:
            mid = games[cid].get("lobby_mid")
            if mid: delete_msg(cid, mid)
            for uid in list(games[cid]["players"].keys()):
                user_to_game.pop(uid, None)
            del games[cid]
    safe_unpin_all(cid)
    unmute_all(cid)

# ══════════════ أدوات اللعبة ══════════════
def get_alive(cid):
    if cid not in games: return {}
    return {u: p for u, p in games[cid]["players"].items() if p["alive"]}

def get_alive_except(cid, exc):
    return {u: p for u, p in get_alive(cid).items() if u != exc}

def valid_game(cid, gid):
    return cid in games and games[cid]["game_id"] == gid

def kill_player(g, uid):
    if uid not in g["players"]: return False
    g["players"][uid]["alive"] = False
    return True

def get_original_team(g, uid):
    return g["original_team"].get(uid, ROLE_TEAM.get(g["players"].get(uid, {}).get("role"), "good"))

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
    
    if exclude_self: return {u: p for u, p in players.items() if u != uid}
    return players

def get_roles_for_count(n):
    n = max(n, 4)
    base = ["Surgeon", "Doctor", "Observer", "Screamer"]
    
    if n >= 5: base.append("Anesthetist")
    if n >= 6: base.append("Nurse") 
    if n >= 7: base.append("Psychopath")
    if n >= 8: base.append("Swapper")
    if n >= 9: base.append("Instigator")
    if n >= 10: base.append("Security")
    
    pool = ["Patient", "Doctor", "Observer", "Screamer", "Swapper"]
    while len(base) < n:
        base.append(random.choice(pool))
        
    random.shuffle(base)
    return base

# ══════════════ بيانات وهيكلة اللعبة ══════════════
def new_game_data(gtype, host_id, gid):
    return {
        "type": gtype, "host": host_id, "players": {}, "phase": "joining",
        "start_at": time.time() + DEFAULT_WAIT_TIME,
        "total_wait": DEFAULT_WAIT_TIME, "game_id": gid,
        "lobby_mid": None, "lobby_mt": "text",
        
        # --- Hospital Specific ---
        "rooms_enabled": (gtype == "hospital"), "room_choices": {},
        "actions": {}, "votes": {}, "confirm_votes": {},
        "bomb": {"is_set": False, "q": "", "a": "", "defuser": None},
        "round": 0, "sedated_current": set(), "swap_data": {},
        "screamer_knife_used": set(), "security_ammo": {}, "security_mistakes": {},
        "patient_used": set(), "psycho_phase": {},
        "confirm_target": None, "defense_target": None,
        "last_gasp_pending": {}, "last_gasp_text": {},
        "original_team": {}, "pinned_mids": [],
        
        # --- Vote Game Specific ---
        "asker": None, "ask_type": None, "ask_type_chosen": False, 
        "vote_question": None, "asked_uids": set(), 
        "qa_answers": {}, "qa_answer_pending": set(), "vote_game_votes": {}
    }

# ══════════════ نظام الفوز وتوزيع المكافآت (المستشفى) ══════════════
def _check_win_inner(cid):
    if cid not in games: return None
    g = games[cid]
    pp = g["players"]
    alive = {u: p for u, p in pp.items() if p["alive"]}

    if not alive: return "⚰️ <b>لا ناجين... المستشفى ابتلع الجميع في ظلامه الحالك.</b>"

    evil_alive = [u for u in alive if ROLE_TEAM.get(pp[u]["role"]) == "evil"]
    good_alive = [u for u in alive if ROLE_TEAM.get(pp[u]["role"]) == "good"]
    psycho_alive = [u for u in alive if ROLE_TEAM.get(pp[u]["role"]) == "psycho"]

    total_alive = len(alive)

    if psycho_alive and not evil_alive and total_alive <= 2:
        return "🤡 <b>المجنون يرقص وحيداً فوق الجثث المتفحمة!</b>"

    if not good_alive and not psycho_alive:
        return "🔪 <b>الظلام انتصر... الجراح أتم عمليته الجراحية بنجاح.</b>"

    if not evil_alive and not psycho_alive:
        return "🩺 <b>أشرقت الشمس... تم تطهير المستشفى ونجا الأبرياء!</b>"

    has_surgeon = any(pp[u]["role"] == "Surgeon" for u in evil_alive)
    if total_alive == 2 and has_surgeon and good_alive:
        return "🔪 <b>المشرط أسرع من العلاج... الجرّاح فاز باللحظة الأخيرة.</b>"

    if evil_alive and len(evil_alive) >= len(good_alive) + len(psycho_alive):
        return "🔪 <b>الكثرة تغلب... الأشرار سيطروا على الأروقة.</b>"

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
            status = "❤️ حي" if p["alive"] else "💀 ميت"
            lines.append(f"▫️ {pname(u, p['name'])} <b>({ROLE_DISPLAY.get(p['role'], '?')})</b> - {status}")
            
            # 💰 توزيع الغنائم للإحصائيات
            prof = get_profile(u)
            wall = get_wallet(u)
            prof["games"] += 1
            wall["coins"] += 50 
            if not p["alive"]:
                prof["deaths"] += 1
            else:
                prof["wins"] += 1
                wall["coins"] += 50 
    
    full = f"{msg}\n\n📋 <b>سجلات المستشفى (الهويات الحقيقية):</b>\n\n" + "\n\n".join(lines) + "\n\n💰 <i>تم توزيع العملات على جميع المشاركين والناجين! تفقد /profile</i>"
    safe_send(cid, full)
    force_cleanup(cid)

# ══════════════ حلقة اللعبة المستمرة ══════════════
def game_loop():
    while True:
        time.sleep(3)
        now = time.time()
        to_del = []
        to_start = []
        with bot_lock:
            for cid, g in list(games.items()):
                if now - g.get("start_at", now) > INACTIVITY_TIMEOUT and g["phase"] != "joining":
                    to_del.append(cid)
                    continue
                if g["phase"] == "joining" and g["start_at"] <= now:
                    g["phase"] = "starting"
                    to_start.append((cid, g["type"], g["game_id"]))
        
        for c in to_del:
            safe_send(c, "🕯 <i>انطفأت الأنوار... (تم إنهاء الجلسة بسبب الخمول أو عدم الاكتمال)</i>")
            force_cleanup(c)
        
        for c, t, gid in to_start:
            target = start_hospital if t == "hospital" else start_vote_game
            threading.Thread(target=target, args=(c, gid), daemon=True).start()

threading.Thread(target=game_loop, daemon=True).start()

# ══════════════ نظام اللوبي (الانتظار) ══════════════
MIN_HOSPITAL = 4
MIN_VOTE = 3

def build_lobby(cid):
    if cid not in games: return "Error"
    g = games[cid]
    rem = max(0, int(g["start_at"] - time.time()))
    total = max(g["total_wait"], 1)
    gt = g["type"]
    pp = g["players"]
    n = len(pp)

    if gt == "hospital":
        mn = MIN_HOSPITAL
        title = "🏥 <b>أبواب المستشفى مفتوحة...</b>"
        flavor = "الممرات مظلمة... ثق بحدسك فقط ولا تدير ظهرك لأحد."
    else:
        mn = MIN_VOTE
        title = "⚖️ <b>مجلس التصويت والمحاكمة</b>"
        flavor = "استعدوا للمواجهات الفكرية وكشف الأسرار."

    if n == 0:
        pt = "   <i>(صمت... لا يوجد أحد بعد)</i>"
    else:
        lines = [f"   👤 {pname(u, p['name'])}" for u, p in pp.items()]
        pt = "\n\n".join(lines)

    bar_f = int(min(max(rem / total, 0), 1.0) * 10)
    bar = "🟩" * bar_f + "⬜" * (10 - bar_f)
    m, sc = divmod(rem, 60)
    ts = f"{m}:{sc:02d}" if m else f"{sc} ثانية"

    return (
        f"{title}\n\n"
        f"⏳ {bar} \n⏱ <b>الوقت المتبقي:</b> {ts}\n\n"
        f"<i>{flavor}</i>\n\n"
        f"👥 <b>اللاعبون المسجلون ({n}):</b>\n\n{pt}\n\n"
        f"📌 مطلوب كحد أدنى: <b>{mn}</b>\n\n"
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
            
            nm = safe_send(cid, txt, reply_markup=mk)
            if nm:
                with bot_lock:
                    if valid_game(cid, gid):
                        games[cid]["lobby_mid"] = nm.message_id
                        games[cid]["lobby_mt"] = "text"
            continue

        with bot_lock:
            if not valid_game(cid, gid) or games[cid]["phase"] != "joining": return
            txt = build_lobby(cid)
            mk = join_markup(gid, games[cid]["type"])
            mid = games[cid]["lobby_mid"]
        
        if mid:
            try: bot.edit_message_text(text=txt, chat_id=cid, message_id=mid, parse_mode="HTML", reply_markup=mk)
            except: pass
            
        if rem <= 0: return

# ══════════════ الانضمام والتفاعل ══════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("join_"))
def cb_join(call):
    cid, uid = call.message.chat.id, call.from_user.id
    try: gid = int(call.data.split("_")[1])
    except: return
    
    with bot_lock:
        if not valid_game(cid, gid):
            return bot.answer_callback_query(call.id, "⛔ انتهى وقت التسجيل أو اللعبة ألغيت.", show_alert=True)
        if games[cid]["phase"] != "joining":
            return bot.answer_callback_query(call.id, "⛔ اللعبة بدأت بالفعل.", show_alert=True)
        if uid in games[cid]["players"]:
            return bot.answer_callback_query(call.id, "✅ أنت مسجل مسبقاً في السجلات.", show_alert=False)
        if len(games[cid]["players"]) >= MAX_PLAYERS:
            return bot.answer_callback_query(call.id, "⛔ الغرفة ممتلئة.", show_alert=True)
        if uid in user_to_game and user_to_game[uid] != cid:
            return bot.answer_callback_query(call.id, "⛔ أنت مسجل في جلسة أخرى.", show_alert=True)
            
        games[cid]["players"][uid] = {
            "name": clean_name(call.from_user.first_name),
            "role": "Patient", "alive": True
        }
        user_to_game[uid] = cid
        games[cid]["start_at"] = time.time() + max(15, games[cid]["start_at"] - time.time())
        cnt = len(games[cid]["players"])
        
    bot.answer_callback_query(call.id, f"✅ تم تسجيلك بنجاح ({cnt})", show_alert=False)
    
    with bot_lock:
        if not valid_game(cid, gid): return
        txt = build_lobby(cid)
        mk = join_markup(gid, games[cid]["type"])
        mid = games[cid].get("lobby_mid")
    if mid:
        try: bot.edit_message_text(text=txt, chat_id=cid, message_id=mid, parse_mode="HTML", reply_markup=mk)
        except: pass

# ══════════════ أوامر المجموعة ══════════════
@bot.message_handler(commands=['hospital', 'vote', 'force_start', 'cancel', 'time', 'commands', 'rooms_cancel', 'shop', 'buy', 'profile', 'tutorial'], chat_types=['group', 'supergroup'])
def group_cmd(m):
    cid = m.chat.id
    uid = m.from_user.id
    raw = m.text.split()[0].split("@")[0].lower()

    delete_msg(cid, m.message_id)

    if raw == "/hospital": init_game(m, "hospital")
    elif raw == "/vote": init_game(m, "vote")
    elif raw == "/time": do_time(m)
    elif raw == "/force_start": do_force(m)
    elif raw == "/cancel": do_cancel(m)
    elif raw == "/commands": do_commands(m)
    elif raw == "/rooms_cancel": do_rooms_cancel(m)
    elif raw == "/shop": do_shop(m)
    elif raw == "/profile": do_profile(m)
    elif raw == "/tutorial": do_tutorial(m)
    elif raw == "/buy": 
        args = m.text.split()
        if len(args) > 1: buy_item(uid, args[1])

def init_game(msg, gtype):
    cid = msg.chat.id
    uid = msg.from_user.id

    with bot_lock:
        if cid in games:
            if games[cid]["phase"] == "joining" and (time.time() - games[cid]["start_at"] > 120):
                force_cleanup(cid) 
            else:
                return safe_send(cid, "⚠️ <i>هناك جلسة قيد التحضير أو جارية بالفعل هنا!</i>")

        if uid in user_to_game:
            return safe_send(cid, "⚠️ <i>عذراً، أنت متورط في جلسة أخرى حالياً.</i>")

        gid = int(time.time() * 1000) % 2147483647
        games[cid] = new_game_data(gtype, uid, gid)

    txt = build_lobby(cid)
    mk = join_markup(gid, gtype)
    
    m2 = safe_send(cid, txt, reply_markup=mk)
    if m2:
        with bot_lock:
            if cid in games:
                games[cid]["lobby_mid"] = m2.message_id
                games[cid]["lobby_mt"] = "text"
    
    threading.Thread(target=lobby_tick, args=(cid, gid), daemon=True).start()

def do_time(m):
    cid = m.chat.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining": return
        try:
            s = int(m.text.split()[1]) if len(m.text.split()) > 1 else 30
            games[cid]["start_at"] += min(s, 120)
        except: pass

def do_force(m):
    cid = m.chat.id
    with bot_lock:
        if cid in games and games[cid]["phase"] == "joining":
            games[cid]["start_at"] = time.time()

def do_cancel(m):
    cid = m.chat.id
    with bot_lock:
        if cid not in games: return
    safe_send(cid, "🛑 <b>تم إلغاء الجلسة بالكامل.</b>")
    force_cleanup(cid)

def do_rooms_cancel(m):
    cid = m.chat.id
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "joining": return
        games[cid]["rooms_enabled"] = not games[cid]["rooms_enabled"]
        state = "مفعّلة ✅" if games[cid]["rooms_enabled"] else "معطّلة ❌"
    safe_send(cid, f"🏠 <i>نظام الغرف والأجنحة الآن: {state}</i>")

def do_tutorial(m):
    txt = (
        "📚 <b>دليل لعبة المستشفى والمجلس</b>\n\n"
        "🏥 <b>المستشفى (/hospital):</b>\n"
        "1️⃣ <b>التسجيل:</b> انقر للتوقيع.\n"
        "2️⃣ <b>الهوية:</b> سيصلك دورك في الخاص.\n"
        "3️⃣ <b>المخبأ:</b> اختر غرفة للاختباء فيها ليلاً.\n"
        "4️⃣ <b>الليل:</b> يختار الأشرار ضحاياهم، ويحاول الأخيار الحماية أو الكشف.\n"
        "5️⃣ <b>الصباح:</b> نكتشف الجثث ونصوّت لإعدام المشتبه به.\n\n"
        "⚖️ <b>مجلس التصويت (/vote):</b>\n"
        "كل لاعب سيعتلي المنصة بدوره ليطرح سؤالاً أو موضوعاً للنقاش. يمكنه اختيار (تصويت مباشر) أو (جمع الحجج)."
    )
    safe_pm(m.from_user.id, txt)

def do_commands(m):
    cmd_text = (
        "📖 <b>سجل أوامر الإدارة</b>\n\n"
        "<code>/hospital</code> - فتح أبواب المستشفى\n"
        "<code>/vote</code> - بدء مجلس التصويت\n"
        "<code>/force_start</code> - إجبار اللعبة على البدء\n"
        "<code>/time 30</code> - تمديد وقت التسجيل\n"
        "<code>/cancel</code> - إلغاء الجلسة الحالية\n\n"
        "<code>/shop</code> - فتح نافذة السوق السوداء\n"
        "<code>/profile</code> - إظهار ملفك الشخصي"
    )
    safe_send(m.chat.id, cmd_text)

def do_shop(m):
    cid = m.chat.id
    text = "🛒 <b>السوق المظلم (الأسود)</b>\nاستخدم <code>/buy كود</code> لاقتناء الأدوات.\n\n"
    for k, v in SHOP_ITEMS.items():
        text += f"🔹 <b>{v['name']}</b> ({v['price']} 💰)\n   <i>{v['desc']}</i>\n   كود الشراء: <code>{k}</code>\n\n"
    safe_send(cid, text)

def do_profile(m):
    cid, uid = m.chat.id, m.from_user.id
    p = get_profile(uid)
    w = get_wallet(uid)
    
    txt = (
        f"👤 <b>الهوية:</b> {clean_name(m.from_user.first_name)}\n\n"
        f"💰 <b>الرصيد:</b> {w['coins']} عملة\n"
        f"🎮 <b>المواجهات:</b> {p['games']}\n"
        f"🏆 <b>النجاة:</b> {p['wins']}\n"
        f"💀 <b>السقوط:</b> {p['deaths']}\n\n"
        f"🎒 <b>المخزون:</b> {', '.join(w['inventory']) if w['inventory'] else 'فارغ'}"
    )
    safe_send(cid, txt)

# ══════════════ 🏛 مجلس التصويت (VOTE GAME) ══════════════
def start_vote_game(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        mid = g.get("lobby_mid")
        if mid: delete_msg(cid, mid)

        pp = g["players"]
        if len(pp) < MIN_VOTE:
            safe_send(cid, f"⚠️ <b>المجلس فارغ!</b>\nالعدد غير كافٍ للبدء ({len(pp)}/{MIN_VOTE}). تم رفع الجلسة.")
            force_cleanup(cid)
            return
            
        g["phase"] = "vote_round"
        g["round"] = 0
        gid = g["game_id"]
    
    safe_send(cid, "🏛 <b>أبواب مجلس التصويت تُغلق...</b>\n\nالجميع يجلس على طاولته. استعدوا للمواجهة الفكرية وكشف الحقائق.")
    if not safe_sleep(cid, gid, 3): return
    
    threading.Thread(target=run_vote_round, args=(cid, gid), daemon=True).start()

def run_vote_round(cid, gid):
    while True:
        with bot_lock:
            if not valid_game(cid, gid): return
            g = games[cid]
            avail = [u for u, p in g["players"].items() if p["alive"] and u not in g["asked_uids"]]
            
            if not avail: 
                show_vote_game_end(cid, gid)
                return
            
            asker = random.choice(avail)
            g["asker"] = asker
            g["asked_uids"].add(asker)
            g["phase"] = "waiting_q"
            g["ask_type_chosen"] = False
            g["vote_question"] = None
            g["qa_answers"] = {}
            g["vote_game_votes"] = {}
            g["qa_answer_pending"] = set([u for u, p in g["players"].items() if p["alive"] and u != asker])
            
            g["round"] += 1
            rnd = g["round"]
            asker_name = g["players"][asker]["name"]

        silence_all(cid)
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🎤 اعتلاء المنصة", url=f"https://t.me/{BOT_USERNAME}?start=ask_{cid}"))
        safe_send(cid, f"⚖️ <b>الجولة {rnd}</b>\n\nالكلمة الآن للمتحدث: <b>{asker_name}</b>\nولديه {VOTE_GAME_ASK_TIME} ثانية لطرح قضيته.", reply_markup=mk)
        
        # انتظار سؤال المتحدث
        t_end = time.time() + VOTE_GAME_ASK_TIME
        got_q = False
        while time.time() < t_end:
            time.sleep(1)
            with bot_lock:
                if not valid_game(cid, gid): return
                if games[cid]["phase"] not in ("waiting_q",): 
                    got_q = True
                    break
        
        if not got_q:
            safe_send(cid, "⏰ <b>انتهى الوقت!</b>\nالمتحدث ارتبك ولم ينطق بكلمة. ننتقل للمتحدث التالي.")
            continue
            
        with bot_lock:
            phase = games[cid]["phase"]
            
        if phase == "voting_active":
            if not safe_sleep(cid, gid, VOTE_GAME_VOTE_TIME): return
            _tally_vote_round(cid, rnd, gid)
        elif phase == "answering":
            if not safe_sleep(cid, gid, VOTE_GAME_ANSWER_TIME): return
            _show_qa_round(cid, rnd, gid)
        
        if not safe_sleep(cid, gid, 5): return

def send_vote_q(cid, asker_id, text):
    with bot_lock:
        g = games[cid]
        alive = get_alive(cid)
        asker_name = g["players"][asker_id]["name"]
    
    mk = types.InlineKeyboardMarkup(row_width=2)
    for u, p in alive.items():
        mk.add(types.InlineKeyboardButton(p["name"], callback_data=f"vgvote_{cid}_{u}"))
    
    safe_send(cid, f"⚖️ <b>تصويت مباشر من {asker_name}!</b>\n\n❓ <b>القضية المطروحة:</b>\n« {text} »\n\n<i>⏳ أمامكم {VOTE_GAME_VOTE_TIME} ثانية للإدلاء بأصواتكم في الأسفل.</i>", reply_markup=mk)

def send_qa_q(cid, asker_id, text):
    with bot_lock:
        asker_name = games[cid]["players"][asker_id]["name"]
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✍️ تقديم حجة (في الخاص)", url=f"https://t.me/{BOT_USERNAME}?start=qa_{cid}"))
    safe_send(cid, f"💬 <b>جلسة نقاش يطرحها {asker_name}!</b>\n\n❓ <b>الموضوع:</b>\n« {text} »\n\n<i>⏳ أمامكم {VOTE_GAME_ANSWER_TIME} ثانية. انتقلوا للخاص لتقديم حججكم (بأسمائكم أو كمجهولين).</i>", reply_markup=mk)

def _tally_vote_round(cid, rnd, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        votes = g.get("vote_game_votes", {})
        question = g.get("vote_question", "بدون سؤال")
    
    if not votes: 
        safe_send(cid, "🤷 <b>لم يشارك أحد في التصويت!</b>\nمرت الجولة بصمت.")
    else:
        counts = {}
        for v_uid, t_uid in votes.items(): 
            counts[t_uid] = counts.get(t_uid, 0) + 1
        
        res = []
        for t_uid, c in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            t_name = g["players"][t_uid]["name"]
            res.append(f"▫️ <b>{t_name}</b> حصل على {c} أصوات")
        
        txt = f"📊 <b>نتائج التصويت (الجولة {rnd})</b>\n\n❓ <b>السؤال كان:</b> {question}\n\n" + "\n".join(res)
        safe_send(cid, txt)
        
def _show_qa_round(cid, rnd, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        ans = g.get("qa_answers", {})
        q = g.get("vote_question", "")
    
    txt = f"💬 <b>استعراض الحجج (الجولة {rnd})</b>\n\n❓ <b>الموضوع:</b> {q}\n\n"
    if not ans:
        txt += "<i>صمت مطبق... لم يجرؤ أحد على تقديم حجة.</i>"
    else:
        for uid, data in ans.items():
            name = g["players"][uid]["name"] if data.get("reveal") else "🎭 مجهول"
            txt += f"🔹 <b>{name} يقول:</b>\n« {data['text']} »\n\n"
    
    safe_send(cid, txt)

def show_vote_game_end(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        for u, p in g["players"].items():
            prof = get_profile(u)
            wall = get_wallet(u)
            prof["games"] += 1
            wall["coins"] += 70 # مكافأة مجلس التصويت
    
    safe_send(cid, "🏛 <b>تم رفع الجلسة!</b>\n\nانتهت جميع الجولات وقال الجميع كلمتهم بجرأة.\n\n💰 <i>تم توزيع 70 عملة لجميع المشاركين كجائزة لحضور المجلس.</i>")
    force_cleanup(cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith("asktype_"))
def cb_asktype(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, typ = int(parts[1]), parts[2]
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g.get("asker") != uid or g["phase"] != "waiting_q": return bot.answer_callback_query(call.id, "⏰ انتهى وقتك للمنصة", show_alert=True)
        g["ask_type"] = typ
        g["ask_type_chosen"] = True
    
    bot.answer_callback_query(call.id, "✅ تم اختيار النمط")
    try: bot.edit_message_text("✍️ <b>الآن... اكتب سؤالك أو موضوع النقاش في رسالة واحدة وأرسله هنا:</b>", uid, call.message.message_id, parse_mode="HTML")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith("vgvote_"))
def cb_vgvote(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, tid = int(parts[1]), int(parts[2])
    except: return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "voting_active": return bot.answer_callback_query(call.id, "⏰ التصويت مغلق.", show_alert=True)
        g = games[cid]
        if uid not in g["players"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g["vote_game_votes"][uid] = tid
    bot.answer_callback_query(call.id, "✅ تم تسجيل صوتك للمجلس", show_alert=False)

@bot.callback_query_handler(func=lambda c: c.data.startswith("reveal_"))
def cb_reveal(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, ch = int(parts[1]), parts[3]
    except: return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "answering": return
        g = games[cid]
        if uid not in g.get("qa_answers", {}): return
        g["qa_answers"][uid]["reveal"] = (ch == "y")
    bot.answer_callback_query(call.id, "✅ تم حفظ التفضيل")
    try: bot.edit_message_text(f"✅ تم تأكيد النشر كـ: <b>{'باسمك الحقيقي' if ch == 'y' else 'شخص مجهول'}</b>", uid, call.message.message_id, parse_mode="HTML")
    except: pass

# ══════════════ بدء اللعبة والغرف (HOSPITAL) ══════════════
def start_hospital(cid, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        
        mid = g.get("lobby_mid")
        if mid: delete_msg(cid, mid)

        pp = g["players"]
        if len(pp) < MIN_HOSPITAL:
            safe_send(cid, f"⚠️ <b>المستشفى فارغ!</b>\nعدد المتواجدين غير كافٍ للبدء ({len(pp)}/{MIN_HOSPITAL}). تم إغلاق الأبواب وإلغاء الجلسة.")
            force_cleanup(cid)
            return
        
        uids = list(pp.keys())
        random.shuffle(uids)
        roles = get_roles_for_count(len(uids))
        for i, uid in enumerate(uids):
            pp[uid]["role"] = roles[i]
            if roles[i] == "Security":
                g["security_ammo"][uid] = 2
                g["security_mistakes"][uid] = 0
            
        g["phase"] = "roles_reveal"
        gid = g["game_id"]

    safe_send(cid, "🏥 <b>تم إغلاق أبواب المستشفى بإحكام...</b>\n\nالظلام يخيّم والقتلة يتجولون الآن بينكم. لا تثق بأحد.")
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📂 استلام بطاقة الهوية السرية", url=f"https://t.me/{BOT_USERNAME}?start=role_{cid}"))
    safe_send(cid, "اسحب بطاقتك وتعرف على دورك ومهمتك أدناه 👇", reply_markup=mk)
    
    if not safe_sleep(cid, gid, 15): return
    start_room_choosing(cid, gid)

def start_room_choosing(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        rooms_on = g["rooms_enabled"]

    if not rooms_on:
        start_night(cid, gid)
        return

    with bot_lock:
        games[cid]["phase"] = "room_choosing"
        games[cid]["room_choices"] = {}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🏠 التوجه إلى المخبأ", url=f"https://t.me/{BOT_USERNAME}?start=room_{cid}"))
    safe_send(cid, f"🔔 <b>حان وقت الإغلاق...</b>\n\nكل مريض عليه اختيار مكان اختبائه لهذه الليلة.\n\n<i>⏳ أمامكم {ROOM_CHOOSE_TIME} ثانية</i>", reply_markup=mk)

    if not safe_sleep(cid, gid, ROOM_CHOOSE_TIME): return

    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        for uid, p in g["players"].items():
            if p["alive"] and uid not in g["room_choices"]:
                g["room_choices"][uid] = 5

    notify_room_mates(cid, gid)
    if not safe_sleep(cid, gid, 3): return
    start_night(cid, gid)

def dispatch_room(uid, param):
    try: cid = int(param.replace("room_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 المستشفى تم تدميره.")
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]: return safe_pm(uid, "🚫 أنت ميت.")
        if g["phase"] != "room_choosing": return safe_pm(uid, "⏰ نفد الوقت.")
        if uid in g["room_choices"]: return safe_pm(uid, "✅ أقفلت الباب بالفعل.")

    mk = types.InlineKeyboardMarkup(row_width=1)
    for rid, rname in ROOM_NAMES.items():
        mk.add(types.InlineKeyboardButton(rname, callback_data=f"pickroom_{cid}_{rid}"))
    safe_pm(uid, "🏠 <b>أين ستختبئ الليلة؟</b>\n\nاختر غرفتك بحذر:", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pickroom_"))
def cb_pickroom(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, rid = int(parts[1]), int(parts[2])
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g = games[cid]
        if g["phase"] != "room_choosing": return bot.answer_callback_query(call.id, "⏰ الوقت انتهى", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g["room_choices"][uid] = rid
    bot.answer_callback_query(call.id, "✅")
    try: bot.edit_message_text(f"✅ تمركزت في: <b>{ROOM_NAMES[rid]}</b>\n\nانتظر بصمت حتى يحل الظلام...", uid, call.message.message_id, parse_mode="HTML")
    except: pass

def notify_room_mates(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        for rid in ROOM_NAMES:
            players_in = get_room_players(g, rid)
            for uid in players_in:
                others = [pname(u, p["name"]) for u, p in players_in.items() if u != uid]
                txt = f"🚪 <b>أنت تختبئ في {ROOM_NAMES[rid]}</b>\n\n"
                if others: txt += "يشاركك المكان:\n" + "\n".join(others)
                else: txt += "أنت وحدك هنا... الصمت مخيف."
                safe_pm(uid, txt)

# ══════════════ الليل والأفعال (HOSPITAL) ══════════════
def start_night(cid, expected_gid):
    auto_send = []
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        g["phase"] = "night"
        g["round"] += 1
        g["actions"] = {}
        g["sedated_current"] = set()
        g["night_acted"] = set()
        rnd = g["round"]
        gid = g["game_id"]
        
        for uid, p in g["players"].items():
            if p["alive"] and p["role"] in INSTANT_ROLES:
                auto_send.append((uid, p["role"]))

    silence_all(cid)

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🌑 التحرك في الظلام", url=f"https://t.me/{BOT_USERNAME}?start=night_{cid}"))
    safe_send(cid, f"🌑 <b>حلّ الظلام - الليلة {rnd}</b>\n\nالكاميرات تعطلت والعيون أُغمضت... استخدموا قدراتكم بحذر.\n\n<i>⏳ أمامكم {NIGHT_TIME} ثانية</i>", reply_markup=mk)

    for uid, role in auto_send: send_night_action(cid, uid, role)
    if not safe_sleep(cid, gid, NIGHT_TIME): return
    resolve_night(cid, rnd, gid)

def dispatch_night(uid, param):
    try: cid = int(param.replace("night_", ""))
    except: return
    with bot_lock:
        if cid not in games: return safe_pm(uid, "🚫 اللعبة لم تعد متاحة.")
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]: return safe_pm(uid, "💀 كيف لروح أن تتحرك؟ أنت ميت.")
        if g["phase"] != "night": return safe_pm(uid, "☀️ انتظر حتى يحل الظلام.")
        if uid in g["night_acted"]: return safe_pm(uid, "✅ لقد أنهيت تحركاتك لهذه الليلة، عُد إلى سريرك.")
        if uid in g["sedated_current"]: return safe_pm(uid, "💉 جسدك مخدر بالكامل... لا تستطيع تحريك إصبعك.")
        
        role = g["players"][uid]["role"]
        if g["round"] == 1 and role not in INSTANT_ROLES:
            return safe_pm(uid, "⏳ <b>قدرتك قيد التجهيز...</b>\nستتمكن من استخدامها ابتداءً من الليلة الثانية.")
        
    send_night_action(cid, uid, role)

def send_night_action(cid, uid, role):
    with bot_lock:
        if cid not in games: return
        g = games[cid]
        
    if role == "Psychopath":
        with bot_lock: bomb_set = g["bomb"]["is_set"]
        if not bomb_set:
            with bot_lock: g["psycho_phase"][uid] = "q"
            safe_pm(uid, "🤡 <b>حان وقت الجنون والمرح!</b>\n\nازرع قنبلتك الآن. أرسل لي 'اللغز' أو 'الكلمة الشفرة' (في رسالة عادية هنا):")
        else:
            safe_pm(uid, "💣 قنبلتك مزروعة وتكتك بهدوء. انتظر الصباح لتبدأ خطتك.")
        return

    if role == "Screamer":
        with bot_lock: used = uid in g["screamer_knife_used"]
        if used:
            return safe_pm(uid, "😱 سكينك مكسور ويديك ترتجفان... ليس لديك سوى البقاء في سريرك والارتعاش الليلة.")
        mk = types.InlineKeyboardMarkup(row_width=1)
        mk.add(types.InlineKeyboardButton("🔪 استخدام السكين (حماية عمياء)", callback_data=f"act_{cid}_{uid}_screamer_knife"))
        mk.add(types.InlineKeyboardButton("🛏 الاختباء والارتجاف بصمت", callback_data=f"act_{cid}_{uid}_screamer_hide"))
        safe_pm(uid, "😱 الخوف ينهش عقلك... لديك سكين حاد. هل ستطعن أي شخص يقترب منك الليلة بدافع الخوف؟ (مرة واحدة فقط للنجاة من أي شخص!)", reply_markup=mk)
        return

    if role == "Security":
        with bot_lock: ammo = g["security_ammo"].get(uid, 0)
        if ammo <= 0: return safe_pm(uid, "🚫 مسدسك فارغ تماماً.")

    if role == "Patient":
        with bot_lock: dead = [(u, p) for u, p in g["players"].items() if not p["alive"] and p["role"] != "Patient"]
        if not dead: return safe_pm(uid, "🤕 <b>لا توجد جثث بعد...</b>\nعليك الانتظار حتى تسيل الدماء لكي تسرق هوية أحدهم.")
        mk = types.InlineKeyboardMarkup(row_width=1)
        for u, p in dead: mk.add(types.InlineKeyboardButton(f"💀 {p['name']} ({ROLE_DISPLAY.get(p['role'], '?')})", callback_data=f"act_{cid}_{u}_patient"))
        safe_pm(uid, "🤕 <b>الجثث مكدسة أمامك...</b>\nاختر الجثة التي ستتقمص دورها وتأخذ قدراتها:", reply_markup=mk)
        return

    def room_btns(prefix, exclude_teams=None):
        with bot_lock:
            tgts = get_room_targets(g, uid)
            if exclude_teams:
                tgts = {u: p for u, p in tgts.items() if get_original_team(g, u) not in exclude_teams}
        if not tgts: return None
        m = types.InlineKeyboardMarkup(row_width=1)
        for t, p in tgts.items(): m.add(types.InlineKeyboardButton(f"🎯 {p['name']}", callback_data=f"act_{cid}_{t}_{prefix}"))
        return m

    prompts = {
        "Surgeon": "🔪 <b>مشرطك متعطش للدماء...</b>\nاختر من ستنهي حياته الليلة:",
        "Doctor": "🩺 <b>قسم أبقراط يطالبك بالتحرك...</b>\nاختر من ستراقبه وتحميه الليلة:",
        "Anesthetist": "💉 <b>إبرة التخدير جاهزة...</b>\nاختر من ستشل حركته وتمنعه من استخدام قدرته:",
        "Observer": "👁 <b>الكاميرات تعمل...</b>\nمن تريد فحص ملفه الطبي السري لتعرف هويته؟",
        "Instigator": "🧠 <b>التلاعب بالعقول...</b>\nحدد من ستسرق صوته للتصويت في محكمة الغد:",
        "Swapper": "🛏 <b>ارتباك وخداع...</b>\nاختر الطرف الأول الذي ستنقله من سريره:",
        "Nurse": "💊 <b>حقنة السم (لمرة واحدة)...</b>\nلمن ستعطيها؟ (احذر قتل الأبرياء):",
        "Security": "👮 <b>مسدسك المحشو...</b>\nحدد المشتبه به لتصفيته الآن:",
    }

    key_map = {"Surgeon": "surgeon", "Doctor": "doctor", "Anesthetist": "anesthetist", "Observer": "observer", "Instigator": "instigator", "Swapper": "swapper", "Nurse": "nurse", "Security": "security"}
    key = key_map.get(role, role.lower())
    ex = ["evil"] if role in ("Surgeon", "Anesthetist") else None
    mk = room_btns(key, exclude_teams=ex)
        
    if not mk: safe_pm(uid, "🚫 <b>لا يوجد أحد في نطاقك...</b>\nغرفتك معزولة الليلة ولا تستطيع استهداف أحد.")
    else: safe_pm(uid, prompts.get(role, "اختر هدفك:"), reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_"))
def cb_act(call):
    uid = call.from_user.id
    try: parts = call.data.split("_"); cid, tid, act = int(parts[1]), int(parts[2]), parts[3]
    except: return

    send_swapper2 = False
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "night": return bot.answer_callback_query(call.id, "⏰ الوقت انتهى.", show_alert=True)
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        if uid in g["night_acted"] and act != "swapper2": return bot.answer_callback_query(call.id, "✅ سبق لك التحرك.", show_alert=True)

        if act == "surgeon": g["actions"]["surgeon"] = tid
        elif act == "doctor": g["actions"]["doctor"] = tid
        elif act == "anesthetist": g["actions"]["anesthetist"] = tid; g["sedated_current"].add(tid)
        elif act == "observer": g["actions"]["observer"] = tid
        elif act == "nurse": g["actions"]["nurse"] = tid
        elif act == "security": g["actions"]["security"] = tid
        elif act == "screamer_knife": g["actions"]["screamer_knife"] = uid
        elif act == "screamer_hide": pass # Just mark as acted
        elif act == "swapper":
            g["swap_data"] = {"first": tid}
            send_swapper2 = True
        elif act == "swapper2":
            g["swap_data"]["second"] = tid
            g["actions"]["swapper"] = (g["swap_data"]["first"], tid)
        elif act == "patient":
            dr = g["players"][tid]["role"]
            g["players"][uid]["role"] = dr
            g["patient_used"].add(uid)
            if dr == "Security": g["security_ammo"][uid] = 2; g["security_mistakes"][uid] = 0

        if act != "swapper": g["night_acted"].add(uid)

    if send_swapper2:
        with bot_lock: tgts = get_alive_except(cid, uid)
        mk = types.InlineKeyboardMarkup(row_width=1)
        for u, p in tgts.items():
            if u != tid: mk.add(types.InlineKeyboardButton(f"🔀 {p['name']}", callback_data=f"act_{cid}_{u}_swapper2"))
        try: bot.edit_message_text("🛏 <b>اختر الطرف الثاني لإتمام التبديل:</b>", uid, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except: pass
        return

    bot.answer_callback_query(call.id, "✅ تم تسجيل حركتك.", show_alert=False)
    try: bot.edit_message_text("✅ <b>تم اتخاذ القرار سراً.</b>\n\nتراجع في الظلام وانتظر بزوغ الفجر لترى نتائج أفعالك...", uid, call.message.message_id, parse_mode="HTML")
    except: pass

# ══════════════ معالجة نتائج الليل والإعلانات المذهلة ══════════════
def resolve_night(cid, expected_rnd, expected_gid):
    with bot_lock:
        if not valid_game(cid, expected_gid): return
        g = games[cid]
        g["phase"] = "morning"
        pp = g["players"]
        actions = g["actions"]
        sedated = g["sedated_current"]
        
        # Swaps
        swaps = {}
        if "swapper" in actions:
            a, b = actions["swapper"]
            if pp.get(a, {}).get("alive") and pp.get(b, {}).get("alive"): swaps[a] = b; swaps[b] = a
        def sw(t): return swaps.get(t, t) if t else t

        s_uid = next((u for u, p in pp.items() if p["role"] == "Surgeon" and p["alive"]), None)
        d_uid = next((u for u, p in pp.items() if p["role"] == "Doctor" and p["alive"]), None)
        sec_uid = next((u for u, p in pp.items() if p["role"] == "Security" and p["alive"]), None)
        n_uid = next((u for u, p in pp.items() if p["role"] == "Nurse" and p["alive"]), None)
        obs_uid = next((u for u, p in pp.items() if p["role"] == "Observer" and p["alive"]), None)

        s_tgt = sw(actions.get("surgeon"))
        d_tgt = sw(actions.get("doctor"))
        sec_tgt = sw(actions.get("security"))
        n_tgt = sw(actions.get("nurse"))
        obs_tgt = sw(actions.get("observer"))

        # Build Real Visitors Map
        real_visitors = {}
        if s_tgt and s_uid not in sedated: real_visitors.setdefault(s_tgt, []).append(s_uid)
        if d_tgt and d_uid not in sedated: real_visitors.setdefault(d_tgt, []).append(d_uid)
        if sec_tgt and sec_uid not in sedated: real_visitors.setdefault(sec_tgt, []).append(sec_uid)
        if n_tgt and n_uid not in sedated: real_visitors.setdefault(n_tgt, []).append(n_uid)
        if obs_tgt and obs_uid not in sedated: real_visitors.setdefault(obs_tgt, []).append(obs_uid)

        # Screamer Knife Logic
        screamer_kills = []
        knife_user = actions.get("screamer_knife") # Who clicked use knife tonight
        if knife_user and knife_user in pp and pp[knife_user]["alive"]:
            vis = real_visitors.get(knife_user, [])
            if vis:
                g["screamer_knife_used"].add(knife_user) 
                for v_uid in vis:
                    screamer_kills.append({"screamer": knife_user, "victim": v_uid})
                    if v_uid == s_uid and s_tgt == knife_user: s_tgt = None 

        # Surgeon Kill Logic
        victim = None
        saved = False
        d_failed = False
        
        if actions.get("doctor") and random.random() < DOCTOR_FAIL_CHANCE: d_failed = True

        if s_tgt and s_tgt in pp:
            if d_tgt == s_tgt and not d_failed: saved = True
            elif has_item(s_tgt, "shield"): use_item(s_tgt, "shield"); saved = True
            else: victim = s_tgt

        # Security Kill Logic
        sec_victim = None
        sec_suicide = False
        if sec_tgt and sec_uid and sec_uid not in sedated:
            g["security_ammo"][sec_uid] = g["security_ammo"].get(sec_uid, 2) - 1
            if sec_tgt != victim and sec_tgt not in [k["victim"] for k in screamer_kills]:
                if d_tgt == sec_tgt and not d_failed: saved = True
                else:
                    sec_victim = sec_tgt
                    if ROLE_TEAM.get(pp[sec_victim]["role"]) == "good":
                        g["security_mistakes"][sec_uid] = g["security_mistakes"].get(sec_uid, 0) + 1
                        if g["security_mistakes"][sec_uid] >= 2: sec_suicide = True

        # Nurse Kill Logic
        nurse_victim = None
        nurse_suicide = False
        if n_tgt and n_uid and n_uid not in sedated:
            if n_tgt != victim and n_tgt not in [k["victim"] for k in screamer_kills] and n_tgt != sec_victim:
                nurse_victim = n_tgt
                if ROLE_TEAM.get(pp[nurse_victim]["role"]) not in ("evil", "psycho"): nurse_suicide = True

    # ---- الإعلانات الصباحية ----
    try: bot.send_photo(cid, ASSETS["DAY"], caption="🌅 <b>بزغ الفجر على المستشفى...</b>\n\nتُفتح الأبواب الثقيلة، ويبدأ الجميع بتفقد العنابر.", parse_mode="HTML")
    except: safe_send(cid, "🌅 <b>بزغ الفجر على المستشفى...</b>\n\nتُفتح الأبواب الثقيلة، ويبدأ الجميع بتفقد العنابر.")
    
    if not safe_sleep(cid, expected_gid, 3): return

    # Screamer Fear Kills
    for k in screamer_kills:
        scr = k["screamer"]
        vic = k["victim"]
        with bot_lock: kill_player(g, vic)
        safe_send(cid, f"😱🔪 <b>دماء بدافع الهلع الأعمى!</b>\nالمرعوب <b>{pp[scr]['name']}</b> فقد عقله من الخوف، واستل سكيناً ليطعن من اقترب من سريره!\n\nسقط <b>{pp[vic]['name']}</b> صريعاً على الفور.\n\n🎭 بطاقة الضحية: <b>{ROLE_DISPLAY.get(pp[vic]['role'], '?')}</b>")
        safe_sleep(cid, expected_gid, 2)

    # Doctor Fail
    if d_failed and d_tgt and d_tgt not in [k["victim"] for k in screamer_kills]:
        with bot_lock: kill_player(g, d_tgt)
        safe_send(cid, f"💉💀 <b>كارثة طبية!</b>\nاللاعب <b>{pp[d_tgt]['name']}</b> فارق الحياة إثر خطأ كارثي في جرعة الطبيب!\n\n🎭 هويته: <b>{ROLE_DISPLAY.get(pp[d_tgt]['role'], '?')}</b>")
        safe_sleep(cid, expected_gid, 2)
    
    if saved: safe_send(cid, "✨ <b>تدخل ملائكي!</b>\nأحدهم نجا من موت محقق الليلة الماضية بفضل رعاية طبية أو درع خفي.")
    
    # Surgeon Kill / Screamer Scream (if no knife used)
    if victim:
        with bot_lock: kill_player(g, victim)
        
        if pp[victim]["role"] == "Screamer" and victim != knife_user:
            safe_send(cid, f"😱 <b>صراخ يتبعه صمت مميت!</b>\nالمرعوب <b>{pp[victim]['name']}</b> صرخ بأعلى صوته: <i>\"النجدة! {pp[s_uid]['name']} هو الجرّاح الذي يقتلنا!!\"</i>\nلكن المشرط كان أسرع بكثير...\n\n🔪💀 مات المرعوب.\n🎭 هويته: <b>{ROLE_DISPLAY.get(pp[victim]['role'], '?')}</b>")
        else:
            safe_send(cid, f"🔪💀 <b>جريمة بشعة!</b>\nوُجد <b>{pp[victim]['name']}</b> ممزقاً بمشرط الجراح في بركة من الدماء.\n\n🎭 بطاقته الملطخة تشير إلى أنه كان: <b>{ROLE_DISPLAY.get(pp[victim]['role'], '?')}</b>")
        
        with bot_lock: g["last_gasp_pending"][victim] = True
        safe_pm(victim, f"🩸 <b>أنت تحتضر...</b>\nلديك {LAST_GASP_TIME} ثانية لكتابة كلماتك الأخيرة التي ستُقرأ على مسامع الجميع. (اكتبها هنا):")
        safe_sleep(cid, expected_gid, LAST_GASP_TIME)
        with bot_lock: txt = g["last_gasp_text"].get(victim)
        if txt: safe_send(cid, f"🩸 <i>الكلمات الأخيرة لـ {pp[victim]['name']}:</i>\n\n«{txt}»")

    # Security Kill
    if sec_victim:
        with bot_lock: kill_player(g, sec_victim)
        safe_send(cid, f"🔫💀 <b>طلقة نارية كسرت السكون!</b>\nسقط <b>{pp[sec_victim]['name']}</b> برصاص حارس الأمن.\n\n🎭 هويته: <b>{ROLE_DISPLAY.get(pp[sec_victim]['role'], '?')}</b>")
        safe_sleep(cid, expected_gid, 2)
        if sec_suicide:
            with bot_lock: kill_player(g, sec_uid)
            safe_send(cid, f"🔥💀 <b>غضب الأبرياء!</b>\nحارس الأمن <b>{pp[sec_uid]['name']}</b> أخطأ للمرة الثانية وقتل بريئاً آخر! لم يتحمل بقية المرضى رعونته، فقاموا برميه حياً في المحرقة في الصباح.\n\n🎭 كان يحمل شارة: <b>{ROLE_DISPLAY.get(pp[sec_uid]['role'], '?')}</b>")

    # Nurse Kill
    if nurse_victim:
        with bot_lock: kill_player(g, nurse_victim)
        safe_send(cid, f"💊💀 <b>تسمم حاد!</b>\nلفظ <b>{pp[nurse_victim]['name']}</b> أنفاسه الأخيرة إثر حقنة مسمومة من الممرض.\n\n🎭 هويته: <b>{ROLE_DISPLAY.get(pp[nurse_victim]['role'], '?')}</b>")
        safe_sleep(cid, expected_gid, 2)
        if nurse_suicide:
            with bot_lock: kill_player(g, n_uid)
            safe_send(cid, f"🧪💀 <b>انتحار!</b>\nالممرض <b>{pp[n_uid]['name']}</b> اكتشف خطأه وشرب السم ليلحق بضحيته البريئة.\n\n🎭 كان: <b>{ROLE_DISPLAY.get(pp[n_uid]['role'], '?')}</b>")

    if check_win_safe(cid, expected_gid): return
    
    # Regular Screamer visits (didn't use knife, and didn't die to surgeon)
    with bot_lock:
        screamers = [u for u, p in pp.items() if p["role"] == "Screamer" and p["alive"]]
    
    for scr_uid in screamers:
        if scr_uid != knife_user:
            vis = real_visitors.get(scr_uid, [])
            for v_uid in vis:
                if v_uid != s_uid: 
                    safe_send(cid, f"😱 <b>صراخ يمزق الأروقة!</b>\nالمرعوب <b>{pp[scr_uid]['name']}</b> يصرخ بهستيريا: <i>\"لقد رأيت {pp[v_uid]['name']} يتجول حول سريري في الظلام!!\"</i>")
                    safe_sleep(cid, expected_gid, 1)

    # Observer Logic
    if obs_uid and obs_tgt and obs_tgt in pp:
        safe_pm(obs_uid, f"👁 <b>الرؤية واضحة عبر الكاميرات:</b>\nاللاعب {pp[obs_tgt]['name']} يخفي خلفه دور: <b>{ROLE_DISPLAY.get(pp[obs_tgt]['role'], '?')}</b>")

    start_discussion(cid, expected_gid)

# ══════════════ النقاش والتصويت (HOSPITAL) ══════════════
def start_discussion(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games[cid]["phase"] = "discussion"
        alive_count = len(get_alive(cid))
    
    open_discussion(cid)
    safe_send(cid, f"💬 <b>فتح باب النقاش ({DISCUSS_TIME} ثانية)</b>\n\n👥 الأحياء المتبقون: <b>{alive_count}</b>\n\nالكلمة لكم الآن! تبادلوا الشكوك، دافعوا عن أنفسكم، وحللوا ما حدث. القاتل يجلس بينكم.")
    
    if not safe_sleep(cid, gid, DISCUSS_TIME): return
    start_voting(cid, gid)

def start_voting(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        games[cid]["phase"] = "voting"
        games[cid]["votes"] = {}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚖️ التصويت للإعدام بالمحرقة", url=f"https://t.me/{BOT_USERNAME}?start=v_{cid}"))
    msg = safe_send(cid, f"⚖️ <b>المحاكمة تبدأ ({VOTE_TIME} ثانية)</b>\n\nاضغطوا على الزر أدناه لاختيار من سيتم رميه في المحرقة اليوم.", reply_markup=mk)
    if msg: safe_pin(cid, msg.message_id)
    
    if not safe_sleep(cid, gid, VOTE_TIME): return
    tally_trial(cid, gid)

def tally_trial(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        valid_votes = {k: v for k, v in g["votes"].items() if k in g["players"] and g["players"][k]["alive"]}
        
    safe_unpin_all(cid)
    if not valid_votes:
        safe_send(cid, "🤷 <b>انتهى الوقت بصمت...</b>\nلم يتجرأ أحد على توجيه تهمة. ستستمر الحياة يوماً آخر.")
        return start_room_choosing(cid, gid)

    counts = {}
    for t in valid_votes.values(): counts[t] = counts.get(t, 0) + 1
    top_v = max(counts.values())
    candidates = [k for k, v in counts.items() if v == top_v]

    txt = "📩 <b>صناديق الاقتراع أفرزت التالي:</b>\n\n"
    for v_uid, t_uid in valid_votes.items():
        txt += f"🔸 {g['players'][v_uid]['name']} صوّت ضد <b>{g['players'][t_uid]['name']}</b>\n"
    safe_send(cid, txt)
    
    if len(candidates) == 1: start_defense(cid, gid, candidates[0])
    else:
        safe_send(cid, "🤝 <b>انقسام في الآراء!</b>\nتساوت الأصوات، ولا توجد أغلبية. لن يُعدم أحد اليوم.")
        start_room_choosing(cid, gid)

def start_defense(cid, gid, sus):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        g["phase"] = "defense"
        g["defense_target"] = sus
        sus_name = g["players"][sus]["name"]
    
    open_discussion(cid)
    safe_send(cid, f"🎤 <b>اللاعب {sus_name} في قفص الاتهام!</b>\n\nلديك <b>{DEFENSE_TIME} ثانية</b> للدفاع عن نفسك وإثبات براءتك، وللآخرين حق الرد.")
    
    if not safe_sleep(cid, gid, DEFENSE_TIME): return
    
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        g["phase"] = "confirming"
        g["confirm_votes"] = {"yes": set(), "no": set()}
    
    silence_all(cid)
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔥 إعدام", callback_data=f"cf_{cid}_y"),
           types.InlineKeyboardButton("🕊 براءة", callback_data=f"cf_{cid}_n"))
    safe_send(cid, "⚖️ <b>القرار النهائي للجمهور:</b>\nهل يُعدم أم يُبرأ؟", reply_markup=mk)
    
    if not safe_sleep(cid, gid, CONFIRM_TIME): return
    resolve_confirm(cid, gid)

def resolve_confirm(cid, gid):
    with bot_lock:
        if not valid_game(cid, gid): return
        g = games[cid]
        sus = g["defense_target"]
        if not sus: return 
        yes = len(g["confirm_votes"]["yes"])
        no = len(g["confirm_votes"]["no"])
        sus_p = g["players"].get(sus, {})
        
    if yes > no:
        with bot_lock: kill_player(g, sus)
        safe_send(cid, f"🔥 <b>تم تنفيذ حكم الإعدام بالمحرقة بحق {sus_p['name']}!</b>\n\n🎭 عند تفتيش أغراضه، اتضح أنه كان: <b>{ROLE_DISPLAY.get(sus_p['role'], '?')}</b>")
        
        if sus_p["role"] == "Psychopath":
            with bot_lock: bomb_q = g["bomb"]["q"]
            if bomb_q:
                safe_send(cid, f"🤡 <b>ضحكات هيستيرية تملأ المكان!</b>\nالمجنون خدعكم وتُركت قنبلة موقوتة قبل موته!\n\n❓ <b>اللغز/الشفرة:</b> {bomb_q}\n\n<i>⏳ أمامكم {BOMB_TIME} ثانية لفك الشفرة والنجاة! أرسلوا الإجابة هنا في المجمموعة.</i>")
                open_discussion(cid)
                with bot_lock: g["phase"] = "bomb"
                
                t_end = time.time() + BOMB_TIME
                while time.time() < t_end:
                    time.sleep(1)
                    with bot_lock:
                        if not valid_game(cid, gid): return
                        if g["phase"] == "defused": break
                
                with bot_lock: phase = g["phase"]
                if phase == "defused":
                    d_name = g["players"][g["bomb"]["defuser"]]["name"]
                    safe_send(cid, f"✅ <b>تم إبطال الكارثة!</b>\nاللاعب <b>{d_name}</b> تمكن من فك الشفرة وإيقاف المؤقت في اللحظة الأخيرة.")
                else:
                    safe_send(cid, f"💥 <b>BOOOOOM!</b>\n\nالقنبلة انفجرت ودمرت المستشفى بأكمله فوق رؤوسكم.\nالجواب الصحيح كان: {g['bomb']['a']}")
                    show_results(cid, "🤡 <b>المجنون العبقري!</b>\nلقد خدع الجميع، مات ولكنه أخذ المستشفى معه إلى الجحيم منتصراً.")
                    return

        if check_win_safe(cid, gid): return
    else:
        safe_send(cid, "🕊 <b>عفو عام...</b>\nلقد تمت تبرئته بقرار الأغلبية وسيعود لسريره.")
    
    start_room_choosing(cid, gid)

@bot.callback_query_handler(func=lambda c: c.data.startswith("vote_"))
def cb_vote(call):
    uid = call.from_user.id
    try: cid, tid = int(call.data.split("_")[1]), int(call.data.split("_")[2])
    except: return
    with bot_lock:
        if cid not in games: return bot.answer_callback_query(call.id, "⛔", show_alert=True)
        g = games[cid]
        if g["phase"] != "voting": return bot.answer_callback_query(call.id, "⏰ التصويت مغلق.", show_alert=True)
        if uid not in g["players"] or not g["players"][uid]["alive"]: return bot.answer_callback_query(call.id, "❌", show_alert=True)
        g["votes"][uid] = tid
    bot.answer_callback_query(call.id, "✅ تم إيداع صوتك السري في الصندوق.", show_alert=False)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cf_"))
def cb_confirm(call):
    uid = call.from_user.id
    try: cid, ch = int(call.data.split("_")[1]), call.data.split("_")[2]
    except: return
    with bot_lock:
        if cid not in games or games[cid]["phase"] != "confirming": return
        g = games[cid]
        if uid not in g["players"] or not g["players"][uid]["alive"]: return
        if uid == g["defense_target"]: return bot.answer_callback_query(call.id, "❌ أنت المتهم! لا يحق لك التصويت هنا.", show_alert=True)
        
        cv = g["confirm_votes"]
        cv["yes"].discard(uid); cv["no"].discard(uid)
        if ch == "y": cv["yes"].add(uid)
        else: cv["no"].add(uid)
        
        y, n = len(cv["yes"]), len(cv["no"])
        
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(f"🔥 إعدام ({y})", callback_data=f"cf_{cid}_y"),
           types.InlineKeyboardButton(f"🕊 براءة ({n})", callback_data=f"cf_{cid}_n"))
    try: bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=mk)
    except: pass
    bot.answer_callback_query(call.id, "✅ سُجل قرارك.", show_alert=False)

# ══════════════ الرسائل الخاصة والرسائل المباشرة ══════════════
@bot.message_handler(commands=['start'], chat_types=['private'])
def start_pm(m):
    args = m.text.split()
    if len(args) > 1:
        param = args[1]
        uid = m.from_user.id
        
        if param.startswith("room_"): dispatch_room(uid, param)
        elif param.startswith("night_"): dispatch_night(uid, param)
        elif param.startswith("v_"):
            try: cid = int(param.replace("v_", ""))
            except: return
            with bot_lock:
                if cid in games and games[cid]["phase"] == "voting":
                    alive = get_alive(cid)
                    mk = types.InlineKeyboardMarkup(row_width=1)
                    for u, p in alive.items():
                        if u != uid: mk.add(types.InlineKeyboardButton(p["name"], callback_data=f"vote_{cid}_{u}"))
                    safe_pm(uid, "⚖️ <b>صندوق الاقتراع:</b>\nاختر من ترغب في إرساله للمحرقة:", reply_markup=mk)
                    
        elif param.startswith("ask_"):
            try: cid = int(param.replace("ask_", ""))
            except: return
            with bot_lock:
                if cid in games and games[cid].get("asker") == uid and games[cid]["phase"] == "waiting_q":
                    mk = types.InlineKeyboardMarkup(row_width=1)
                    mk.add(types.InlineKeyboardButton("🗳 تصويت مباشر (للجميع)", callback_data=f"asktype_{cid}_vote"),
                           types.InlineKeyboardButton("💬 جلسة نقاش وجمع حجج", callback_data=f"asktype_{cid}_qa"))
                    safe_pm(uid, "🎤 <b>المنصة لك!</b>\nكيف ترغب في إدارة جلستك في المجلس؟", reply_markup=mk)
                    
        elif param.startswith("qa_"):
            try: cid = int(param.replace("qa_", ""))
            except: return
            with bot_lock:
                if cid in games and games[cid]["phase"] == "answering":
                    safe_pm(uid, "✍️ <b>المنصة مفتوحة:</b>\nاكتب حجتك أو رأيك في رسالة واحدة وأرسلها هنا:")
                    
        elif param.startswith("role_"): 
            try: cid = int(param.replace("role_", ""))
            except: return
            with bot_lock:
                if cid in games and uid in games[cid]["players"]:
                    role = games[cid]["players"][uid]["role"]
                    guide = ROLE_GUIDE_SHORT.get(role, f"🎭 دورك: <b>{ROLE_DISPLAY.get(role, role)}</b>")
                    safe_pm(uid, f"📇 <b>ملفك السري:</b>\n\n{guide}")
        return
    safe_pm(m.from_user.id, "أهلاً بك. هذا البوت مخصص لإدارة لعبة المستشفى المرعب والمحاكمة.")

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and not m.text.startswith("/"))
def pm_handler_special(msg):
    uid = msg.from_user.id
    text = msg.text.strip()

    with bot_lock:
        cid = user_to_game.get(uid)
        if not cid or cid not in games: return
        g = games[cid]
        
        # Room logic
        if g["type"] == "hospital" and g["phase"] == "night" and g["players"].get(uid, {}).get("alive"):
            my_room = get_player_room(g, uid)
            if my_room:
                my_name = g["players"][uid]["name"]
                if my_room == 5:
                    for u in get_room_players(g, 5):
                        if u != uid: safe_pm(u, f"🌑 <b>{my_name} (من الممر المظلم):</b> {clean(text)}")
                    corrupted = corrupt_text(text)
                    for u in [u for u, p in g["players"].items() if p["alive"] and g["room_choices"].get(u) != 5]:
                        safe_pm(u, f"👻 <b>(صوت خافت قادم من الممر):</b> {clean(corrupted)}")
                else:
                    for u in get_room_players(g, my_room):
                        if u != uid: safe_pm(u, f"🏠 <b>{my_name}:</b> {clean(text)}")
                return

        # Psychopath logic
        if g["players"].get(uid, {}).get("role") == "Psychopath":
            step = g["psycho_phase"].get(uid)
            if step == "q":
                g["bomb"]["q"] = clean(text, 100); g["psycho_phase"][uid] = "a"
                safe_pm(uid, "✅ <b>ممتاز!</b>\nالآن أرسل لي 'الجواب الصحيح' بكلمة واحدة لتكتمل الشفرة:")
                return
            if step == "a":
                g["bomb"]["a"] = normalize_arabic(text); g["bomb"]["is_set"] = True; g["psycho_phase"][uid] = "done"
                safe_pm(uid, "💣 <b>اكتمل الفخ!</b>\nقنبلتك جاهزة. نم الآن بسلام.")
                return
                
        # Last gasp logic
        if g["last_gasp_pending"].get(uid):
            g["last_gasp_text"][uid] = clean(text, 300); g["last_gasp_pending"][uid] = False
            safe_pm(uid, "🩸 تم تسطير كلماتك بدمائك. ارقد بسلام.")
            return

        # Vote game logic
        if g["type"] == "vote":
            if g["phase"] == "waiting_q" and g.get("asker") == uid and g.get("ask_type_chosen"):
                g["vote_question"] = clean(text, 200)
                if g["ask_type"] == "vote": 
                    g["phase"] = "voting_active"
                    send_vote_q(cid, uid, g["vote_question"])
                else: 
                    g["phase"] = "answering"
                    send_qa_q(cid, uid, g["vote_question"])
                safe_pm(uid, "✅ <b>تم طرح قضيتك على المجلس!</b>")
                return

            if g["phase"] == "answering" and uid in g["qa_answer_pending"]:
                g["qa_answer_pending"].remove(uid)
                g["qa_answers"][uid] = {"text": clean(text, 200), "reveal": True}
                
                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton("✅ باسمي الحقيقي", callback_data=f"reveal_{cid}_{uid}_y"),
                       types.InlineKeyboardButton("🎭 كشف مجهول", callback_data=f"reveal_{cid}_{uid}_n"))
                safe_pm(uid, "✅ <b>تم تدوين حجتك.</b>\nهل تريد عرضها باسمك أم بشكل مجهول؟", reply_markup=mk)
                return

@bot.message_handler(content_types=['text'], func=lambda m: m.chat.type in ("group", "supergroup") and not (m.text or "").startswith("/"))
def group_msg_filter(m):
    cid, uid = m.chat.id, m.from_user.id
    text = m.text or ""
    do_delete = False

    with bot_lock:
        if cid not in games: return
        g = games[cid]
        phase = g["phase"]

        if phase == "bomb":
            if uid not in g["players"] or not g["players"][uid]["alive"]: do_delete = True
            elif text:
                if normalize_arabic(text) == g["bomb"]["a"]:
                    g["phase"] = "defused"; g["bomb"]["defuser"] = uid
                else: do_delete = True
            else: do_delete = True
            if do_delete: delete_msg(cid, m.message_id)
            return

        if uid in g["players"] and not g["players"][uid]["alive"]: do_delete = True

    if do_delete: delete_msg(cid, m.message_id)

# ══════════════ تشغيل البوت النهائي ══════════════
print(">>> Bot is Fully Operational and Ready! <<<")
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Polling Error: {e}")
        time.sleep(5)
