import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from database import (
    buy_shop_item,
    complete_mission,
    get_completed_missions,
    get_habits_for_date,
    get_or_create_player,
    get_player,
    get_purchases,
    get_shop_purchases,
    save_habit,
)
from game_logic import MISSION, calculate_level, get_mission_reward

# =====================================================
# تابع برای بارگذاری آیتم‌ها
# =====================================================

# مسیر اصلی پروژه
BASE_DIR = Path(__file__).resolve().parent

# مسیر فایل آیتم‌های فروشگاه
ITEMS_FILE = BASE_DIR / "data" / "items.json"

def load_shop_items():
    """خواندن و اعتبارسنجی آیتم‌های بازارچه."""
    with ITEMS_FILE.open("r", encoding="utf-8") as file:
        items = json.load(file)

    if not isinstance(items, list):
        raise ValueError("ساختار فایل آیتم‌ها معتبر نیست.")

    seen_ids = set()

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("اطلاعات یک آیتم معتبر نیست.")

        for field in ("id", "name", "description", "price"):
            if field not in item:
                raise ValueError(f"فیلد {field} در یک آیتم وجود ندارد.")

        if not isinstance(item["id"], str) or not item["id"].strip():
            raise ValueError("شناسه آیتم باید رشته‌ای غیرخالی باشد.")

        if item["id"] in seen_ids:
            raise ValueError(f"شناسه تکراری: {item['id']}")

        seen_ids.add(item["id"])

        price = item["price"]
        if isinstance(price, bool) or not isinstance(price, int) or price < 0:
            raise ValueError(f"قیمت آیتم {item['id']} معتبر نیست.")

    return items
# =====================================================
# تنظیمات صفحه
# =====================================================


st.set_page_config(
    page_title="قهرمانان تندرستی",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# طراحی و ظاهر برنامه
# =====================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [data-testid="stApp"] {
        font-family: 'Vazirmatn', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f4fbf7 0%, #edf7f2 100%);
        direction: rtl;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e1f3e9 0%, #f5fbf7 100%);
        border-left: 1px solid #d4eade;
    }

    h1, h2, h3, p, label {
        text-align: right;
    }

    .hero {
        background: linear-gradient(120deg, #087f5b, #21a179);
        color: white;
        padding: 30px;
        border-radius: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(20, 110, 75, 0.13);
    }

    .hero h1, .hero p {
        color: white;
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        opacity: 0.95;
    }

    .stat-card {
        background: white;
        border: 1px solid #d9eee2;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(20, 90, 60, 0.05);
        min-height: 100px;
    }

    .stat-title {
        color: #54816c;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .stat-value {
        color: #087f5b;
        font-size: 28px;
        font-weight: 800;
    }

    .panel {
        background: white;
        border: 1px solid #dcefe4;
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(20, 90, 60, 0.04);
    }

    .mission-box {
        background: #f0faf4;
        border: 1px solid #d6eddf;
        border-radius: 18px;
        padding: 20px;
        margin: 14px 0;
    }

    .small-muted {
        color: #648575;
        font-size: 14px;
    }

    .success-note {
        background: #e7f8ed;
        border-right: 5px solid #199765;
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
    }

    .tip-box {
        background: #edf8f2;
        border-radius: 16px;
        padding: 18px;
        color: #245d48;
        line-height: 2;
    }

    div.stButton > button {
        border-radius: 12px;
        min-height: 44px;
        font-family: 'Vazirmatn', sans-serif;
        font-weight: 600;
        border: 1px solid #cfe8d9;
        transition: 0.2s;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #087f5b, #21a179);
        color: white;
        border: none;
    }

    div.stButton > button:hover {
        border-color: #087f5b;
        transform: translateY(-1px);
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dcefe4;
        padding: 15px;
        border-radius: 16px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# اطلاعات اولیه بازیکن
# =====================================================

# -----------------------------
# بارگذاری بازیکن از پایگاه داده
# -----------------------------
if "player_id" not in st.session_state:
    player = get_or_create_player("player_1")
    st.session_state.player_id = player["id"]
    st.session_state.xp = player["xp"]
    st.session_state.coins = player["coins"]
    st.session_state.completed_missions = list(
        get_completed_missions(player["id"])
    )
else:
    player = get_player(st.session_state.player_id)
    if player is not None:
        st.session_state.xp = player["xp"]
        st.session_state.coins = player["coins"]
        st.session_state.completed_missions = list(
            get_completed_missions(player["id"])
        )

defaults = {
    "xp": 0,
    "coins": 0,
    "completed_missions": [],
    "mission_started": False,
    "mission_step": 0,
    "mission_answers": {},
    "mission_finished": False,
    "reward_claimed": False,
    "mission_run_id": 0,
    "page": "خانه",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# توابع کمکی
# =====================================================

def reset_mission():
    """آماده‌سازی مأموریت برای شروع دوباره."""

    st.session_state.mission_started = False
    st.session_state.mission_step = 0
    st.session_state.mission_answers = {}
    st.session_state.mission_finished = False
    st.session_state.reward_claimed = False

    # با تغییر شناسه، کلیدهای رادیویی اجرای قبلی هم عوض می‌شوند.
    st.session_state.mission_run_id += 1


def start_mission():
    """شروع یک اجرای تازه از مأموریت."""

    reset_mission()
    st.session_state.mission_started = True


def go_home():
    reset_mission()
    st.session_state.page = "خانه"


def get_level_progress(xp):
    level = calculate_level(xp)
    progress = (xp % 100) / 100
    return level, progress


def get_mission_steps():
    return MISSION.get("steps", [])


def get_correct_count():
    steps = get_mission_steps()
    answers = st.session_state.mission_answers

    count = 0
    for i, step in enumerate(steps):
        if i in answers and answers[i] == step.get("correct"):
            count += 1

    return count



def claim_reward_once():
    """ثبت پاداش مأموریت در پایگاه داده، فقط یک بار."""

    if st.session_state.reward_claimed:
        return None

    correct_count = get_correct_count()
    total_questions = len(get_mission_steps())
    reward = get_mission_reward(correct_count)

    xp_reward = int(reward.get("xp", 0))
    coin_reward = int(reward.get("coins", 0))

    mission_id = str(
        MISSION.get("id", MISSION.get("title", "main_mission"))
    )

    saved = complete_mission(
        player_id=st.session_state.player_id,
        mission_id=mission_id,
        correct_count=correct_count,
        total_questions=total_questions,
        xp_awarded=xp_reward,
        coins_awarded=coin_reward,
    )

    # اگر این مأموریت قبلاً ثبت شده باشد، پاداش مجدد نده.
    if not saved:
        player = get_player(st.session_state.player_id)

        if player is not None:
            st.session_state.xp = player["xp"]
            st.session_state.coins = player["coins"]

        st.session_state.reward_claimed = True
        st.session_state.completed_missions = list(
            get_completed_missions(st.session_state.player_id)
        )
        return None

    # فقط پس از ذخیره موفق، امتیازهای نشست را به‌روزرسانی کن.
    st.session_state.xp += xp_reward
    st.session_state.coins += coin_reward
    st.session_state.reward_claimed = True

    st.session_state.completed_missions = list(
        get_completed_missions(st.session_state.player_id)
    )

    return reward


# =====================================================
# نوار کناری
# =====================================================

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:20px 5px;">
            <div style="font-size:48px;">🌱</div>
            <h2 style="text-align:center;color:#087f5b;">
                قهرمانان تندرستی
            </h2>
            <p style="text-align:center;color:#54816c;">
                هر روز یک قدم قوی‌تر
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    pages = [
        "خانه",
        "مأموریت‌ها",
        "عادت‌های من",
        "فروشگاه",
        "افتخارات",
    ]

    for page_name in pages:
        if st.button(
            f"{'🏠' if page_name == 'خانه' else '🗺️' if page_name == 'مأموریت‌ها' else '⭐' if page_name == 'عادت‌های من' else '🛍️' if page_name == 'فروشگاه' else '🏆'}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if st.session_state.page == page_name else "secondary",
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    st.caption("نسخه آزمایشی بازی")
    st.caption("سلامتی، شادی و یادگیری 🌿")


# =====================================================
# اطلاعات بالای صفحات
# =====================================================
current_player = get_player(st.session_state.player_id)

if current_player is not None:
    st.session_state.xp = current_player["xp"]
    st.session_state.coins = current_player["coins"]
    st.session_state.completed_missions = list(
        get_completed_missions(current_player["id"])
    ) 
    
level, level_progress = get_level_progress(st.session_state.xp)

st.markdown(
    """
    <div class="hero">
        <p>دنیای ماجراجویی تو</p>
        <h1>سلام، قهرمان! 🌟</h1>
        <p>تصمیم‌های خوب بگیر، مهارت یاد بگیر و پیشرفت کن.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">⭐ سطح فعلی</div>
            <div class="stat-value">{level}</div>
            <div class="small-muted">در مسیر قهرمانی</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">🪙 سکه‌ها</div>
            <div class="stat-value">{st.session_state.coins}</div>
            <div class="small-muted">برای خرید وسایل بازی</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">⚡ تجربه (XP)</div>
            <div class="stat-value">{st.session_state.xp}</div>
            <div class="small-muted">تا سطح بعدی</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.progress(level_progress, text=f"پیشرفت سطح {level}")


# =====================================================
# صفحه خانه
# =====================================================

if st.session_state.page == "خانه":

    st.markdown("## 🗺️ ماجراجویی‌های تو")

    left, right = st.columns([2, 1])

    with left:
        st.markdown(
            """
            <div class="panel">
                <h3>☀️ راز روز داغ مدرسه</h3>
                <p>
                    امروز هوا گرم است و تو مسئول کمک به گروهت هستی.
                    برای انتخاب رفتارهای سالم، سه مرحله را پشت سر بگذار!
                </p>
                <p class="small-muted">
                    🎯 مأموریت آموزشی | 🧩 ۳ مرحله | 🌟 دریافت تجربه و سکه
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "▶️ شروع مأموریت",
            type="primary",
            use_container_width=True,
            key="home_start_mission",
        ):
            st.session_state.page = "مأموریت‌ها"
            start_mission()
            st.rerun()

        st.markdown(
            """
            <div class="panel">
                <h3>🥗 انتخاب‌های سالم</h3>
                <p>با یادگیری عادت‌های مفید، مهارت‌های زندگی خودت را تقویت کن.</p>
                <p class="small-muted">به‌زودی در دسترس</p>
            </div>
            <div class="panel">
                <h3>🏃 ورزش و تحرک</h3>
                <p>برای حرکت بیشتر و استراحت مناسب، ایده‌های تازه کشف کن.</p>
                <p class="small-muted">به‌زودی در دسترس</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel">
                <h3>💚 پیام قهرمان</h3>
                <p>
                    هر تصمیم خوب، حتی کوچک، یک قدم به سوی زندگی سالم‌تر است.
                </p>
                <hr>
                <h3>💡 نکته امروز</h3>
                <p>در روزهای گرم، آب کافی بنوش و هنگام فعالیت به بدنت استراحت بده.</p>
                <hr>
                <p class="small-muted">
                    پیشرفت خودت را با گذشته خودت مقایسه کن؛
                    هرکس مسیر مخصوص خودش را دارد.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =====================================================
# صفحه مأموریت‌ها
# =====================================================

elif st.session_state.page == "مأموریت‌ها":

    steps = get_mission_steps()
    mission_title = MISSION.get("title", "راز روز داغ مدرسه")

    st.markdown(f"## 🧭 {mission_title}")

    if not steps:
        st.error(
            "در فایل game_logic.py فهرست مراحل مأموریت پیدا نشد. "
            "لطفاً ساختار متغیر MISSION را بررسی کن."
        )

    elif not st.session_state.mission_started and not st.session_state.mission_finished:
        st.markdown(
            """
            <div class="panel">
                <h3>آماده‌ای قهرمان؟ 🌟</h3>
                <p>
                    این مأموریت چند مرحله دارد. در هر مرحله یک گزینه انتخاب کن،
                    بازخورد آموزشی را بخوان و سپس به مرحله بعد برو.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚀 شروع مأموریت",
            type="primary",
            use_container_width=True,
            key="mission_start_button",
        ):
            start_mission()
            st.rerun()

    elif st.session_state.mission_started and not st.session_state.mission_finished:

        index = st.session_state.mission_step

        if index >= len(steps):
            st.session_state.mission_finished = True
            st.rerun()

        else:
            step = steps[index]
            run_id = st.session_state.mission_run_id

            st.progress(
                (index + 1) / len(steps),
                text=f"مرحله {index + 1} از {len(steps)}",
            )

            st.markdown(
                f"""
                <div class="mission-box">
                    <h3>🧩 {step.get("title", f"مرحله {index + 1}")}</h3>
                    <p>{step.get("story", "بهترین انتخاب را انجام بده.")}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # کلید هر اجرا متفاوت است؛ پاسخ قبلی تداخل ایجاد نمی‌کند.
            radio_key = f"answer_{run_id}_{index}"
            submit_key = f"submit_{run_id}_{index}"
            continue_key = f"continue_{run_id}_{index}"

            already_answered = index in st.session_state.mission_answers

            if not already_answered:
                options = step.get("options", [])

                if not options:
                    st.error("برای این مرحله گزینه‌ای تعریف نشده است.")
                else:
                    selected_option = st.radio(
                        "کدام گزینه را انتخاب می‌کنی؟",
                        options,
                        index=None,
                        key=radio_key,
                    )

                    if st.button(
                        "ثبت انتخاب",
                        type="primary",
                        key=submit_key,
                        use_container_width=True,
                    ):
                        if selected_option is None:
                            st.warning("لطفاً اول یک گزینه انتخاب کن.")
                        else:
                            chosen_index = options.index(selected_option)
                            st.session_state.mission_answers[index] = chosen_index
                            st.rerun()

            # فقط وقتی پاسخ ذخیره شده باشد، بازخورد نمایش داده می‌شود.
            if index in st.session_state.mission_answers:
                chosen = st.session_state.mission_answers[index]
                correct = step.get("correct")
                is_correct = chosen == correct

                if is_correct:
                    st.success("آفرین! پاسخ درست است. 🌟")
                else:
                    st.info("تلاش خوبی بود! از بازخورد این مرحله یاد بگیر. 💚")
# بازخورد متناسب با گزینه‌ای که بازیکن انتخاب کرده است
                feedback_data = step.get("feedback", "")

                if isinstance(feedback_data, list):
    # اگر برای هر گزینه بازخورد جداگانه تعریف شده باشد
                    if 0 <= chosen < len(feedback_data):
                        feedback = feedback_data[chosen]
                    else:
                        feedback = "برای این انتخاب بازخوردی تعریف نشده است."
                else:
    # اگر یک بازخورد عمومی برای کل مرحله تعریف شده باشد
                    feedback = feedback_data

                if isinstance(feedback, str) and feedback.strip():
                    feedback = feedback.replace(r"\u200c", "\u200c")

                st.markdown(
         f"""
             <div class="success-note">
               <strong>📘 نکته آموزشی:</strong>
                <p>{feedback}</p>
             </div>
                 """,
                unsafe_allow_html=True,
                )


                skill = step.get("skill")
                if skill:
                    st.caption(f"مهارت این مرحله: {skill}")

                if st.button(
                    "مرحله بعدی ➜" if index < len(steps) - 1 else "پایان مأموریت 🏆",
                    type="primary",
                    use_container_width=True,
                    key=continue_key,
                ):
                    if index < len(steps) - 1:
                        st.session_state.mission_step += 1
                    else:
                        st.session_state.mission_finished = True

                    st.rerun()

    # -------------------------------------------------
    # پایان مأموریت و جایزه
    # -------------------------------------------------

    if st.session_state.mission_finished:
        correct_count = get_correct_count()
        total_steps = len(steps)

        st.markdown(
            """
            <div class="panel">
                <h2>🏆 مأموریت تمام شد، قهرمان!</h2>
                <p>ممنون که در این ماجراجویی شرکت کردی.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(f"پاسخ‌های درست: **{correct_count} از {total_steps}**")

        if not st.session_state.reward_claimed:
            reward = claim_reward_once()
        else:
            reward = None

        if reward is not None:
            st.success(
                f"جایزه مأموریت: {reward.get('xp', 0)} تجربه "
                f"و {reward.get('coins', 0)} سکه! 🎁"
            )
        else:
            st.info("جایزه این اجرای مأموریت قبلاً ثبت شده است.")

        st.markdown(
            """
            <div class="tip-box">
                🌱 <strong>یادت باشد:</strong>
                مهم‌تر از گرفتن امتیاز، یادگرفتن نکته‌های مفید و
                استفاده از آن‌ها در زندگی روزمره است.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🏠 بازگشت به خانه",
            type="primary",
            use_container_width=True,
            key="mission_return_home",
        ):
            go_home()
            st.rerun()

        if st.button(
            "🔁 شروع دوباره مأموریت",
            use_container_width=True,
            key="mission_restart_button",
        ):
            start_mission()
            st.rerun()


# =====================================================
# صفحه عادت‌های من
# =====================================================

elif st.session_state.page == "عادت‌های من":
    st.title("🌱 عادت‌های من")
    st.write("عادت‌های امروزت را علامت بزن تا در بازی ثبت شوند.")

    # تاریخ روز بر اساس تقویم میلادی سیستم
    today = datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()

    player_id = st.session_state.player_id

    # دریافت عادت‌هایی که برای امروز ذخیره شده‌اند
    saved_habits = get_habits_for_date(player_id, today)

    habits = [
        ("reading", "📚 امروز کمی مطالعه کردم"),
        ("movement", "🏃 امروز تحرک داشتم"),
        ("water", "💧 امروز به نوشیدن آب توجه کردم"),
        ("rest", "🌙 امروز به استراحت کافی توجه کردم"),
    ]

    st.caption(f"تاریخ ثبت: {today}")

    # هر روز کلیدهای جداگانه دارد تا وضعیت روزهای قبل
    # با وضعیت روز جاری اشتباه نشود.
    for habit_id, label in habits:
        widget_key = f"habit_{habit_id}_{today}"

        # مقدار اولیه را فقط یک بار برای هر کلید تعیین کن.
        if widget_key not in st.session_state:
            st.session_state[widget_key] = saved_habits.get(
                habit_id, False
            )

        st.checkbox(label, key=widget_key)

        # ذخیره وضعیت فعلی در پایگاه داده
        save_habit(
            player_id=player_id,
            habit_id=habit_id,
            completed=st.session_state[widget_key],
            log_date=today,
        )

    completed_count = sum(
        bool(st.session_state[f"habit_{habit_id}_{today}"])
        for habit_id, _ in habits
    )

    st.progress(completed_count / len(habits))

    st.write(
        f"امروز {completed_count} مورد از "
        f"{len(habits)} عادت را انجام داده‌ای."
    )

    if completed_count == len(habits):
        st.success("آفرین! هر چهار عادت امروزت ثبت شده‌اند.")
    elif completed_count > 0:
        st.info("عالیه؛ با ادامه دادن می‌توانی عادت‌های بیشتری ثبت کنی.")
    else:
        st.info("برای شروع، هر عادتی را که امروز انجام داده‌ای علامت بزن.")


# =====================================================
# صفحه فروشگاه
# =====================================================

elif st.session_state.page == "فروشگاه":   
    st.markdown("## 🐚 بازارچه گنجینه‌های خلیج فارس")
    st.write(
        "نشان‌های دریایی و یادگاری‌های هرمزگان را "
        "با سکه‌های مأموریت‌ها جمع‌آوری کن."
    )

    player = get_player(st.session_state.player_id)

    if player is None:
        st.error("اطلاعات بازیکن پیدا نشد.")
        st.stop()

    # منبع موجودی، پایگاه داده است.
    st.session_state.coins = player["coins"]
    st.metric("🪙 موجودی سکه", player["coins"])

    try:
        items = load_shop_items()
        owned_items = get_shop_purchases(player["id"])
    except (OSError, ValueError, json.JSONDecodeError) as error:
        st.error(f"بارگذاری فروشگاه ناموفق بود: {error}")
        st.stop()

    rarities = ["همه"] + list(dict.fromkeys(
        item.get("rarity", "معمولی") for item in items
    ))

    selected_rarity = st.selectbox(
        "فیلتر بر اساس کمیابی",
        rarities,
        key="shop_rarity_filter",
    )

    if selected_rarity != "همه":
        items = [
            item for item in items
            if item.get("rarity", "معمولی") == selected_rarity
        ]

    if not items:
        st.info("در این دسته هنوز آیتمی وجود ندارد.")

    columns = st.columns(2)

    for index, item in enumerate(items):
        with columns[index % 2]:
            with st.container(border=True):

                image_value = item.get("image", "")
                image_path = BASE_DIR / image_value

                if (
                    image_value
                    and image_path.is_file()
                    and image_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
                ):
                    st.image(str(image_path), use_container_width=True)
                elif (
                    image_value
                    and image_path.is_file()
                    and image_path.suffix.lower() == ".svg"
                ):
                    st.image(str(image_path), width=160)
                else:
                    st.markdown(
                        f"<div style='font-size:64px;text-align:center'>"
                        f"{item.get('emoji', '🐚')}</div>",
                        unsafe_allow_html=True,
                    )

                st.subheader(item["name"])
                st.caption(
                    f"{item.get('category', 'گنجینه‌ها')} | "
                    f"کمیابی: {item.get('rarity', 'معمولی')}"
                )
                st.write(item["description"])
                st.write(f"**قیمت: 🪙 {item['price']} سکه**")

                item_id = item["id"]

                if item_id in owned_items:
                    st.success("✅ در مجموعه شما")
                elif st.session_state.coins < item["price"]:
                    st.button(
                        "سکه کافی نیست",
                        key=f"shop_unavailable_{item_id}",
                        disabled=True,
                        use_container_width=True,
                    )
                else:
                    if st.button(
                        "🛒 خرید نشان",
                        key=f"shop_buy_{item_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        success, message = buy_shop_item(
                            player_id=player["id"],
                            item_id=item_id,
                            price=item["price"],
                        )

                        if success:
                            st.success(message)
                        else:
                            st.warning(message)

                        # موجودی و مالکیت را از پایگاه داده تازه‌سازی کن.
                        refreshed_player = get_player(player["id"])
                        if refreshed_player is not None:
                            st.session_state.coins = refreshed_player["coins"]

                        st.rerun()

    st.divider()
    st.subheader("🎒 گنجینه‌های جمع‌آوری‌شده")
    st.write(f"تعداد نشان‌های این مجموعه: {len(owned_items)} از ۵")

    owned_catalog = [
        item for item in load_shop_items()
        if item["id"] in owned_items
    ]

    if owned_catalog:
        inventory_columns = st.columns(3)

        for index, item in enumerate(owned_catalog):
            with inventory_columns[index % 3]:
                st.markdown(
                    f"### {item.get('emoji', '🐚')} {item['name']}"
                )
                st.caption(item.get("rarity", "معمولی"))
    else:
        st.info(
            "هنوز نشانی جمع‌آوری نکرده‌ای. "
            "اولین گنجینه‌ات را از بازارچه بخر!"
        )

# =====================================================
# صفحه افتخارات
# =====================================================

elif st.session_state.page == "افتخارات":

    st.markdown("## 🏆 افتخارات من")

    st.markdown(
        f"""
        <div class="panel">
            <h3>🌟 قهرمان سطح {level}</h3>
            <p>تجربه به‌دست‌آمده: {st.session_state.xp}</p>
            <p>سکه‌های جمع‌شده: {st.session_state.coins}</p>
            <p>مأموریت‌های تکمیل‌شده: {len(st.session_state.completed_missions)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.completed_missions:
        st.success("آفرین! دست‌کم یک مأموریت را به پایان رسانده‌ای.")
    else:
        st.info("اولین مأموریتت را کامل کن تا مسیر افتخاراتت شروع شود.")


# =====================================================
# پاورقی
# =====================================================

st.markdown("---")
st.caption("قهرمانان تندرستی | یادگیری، بازی و انتخاب‌های سالم 🌱")

