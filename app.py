
import streamlit as st

st.set_page_config(
    page_title="قهرمانان تندرستی",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- طراحی و فونت ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Vazirmatn', sans-serif;
}

.stApp {
    background: #F5F8F5;
    color: #19352C;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p, label, span, div {
    font-family: 'Vazirmatn', sans-serif;
}

h1 {
    color: #155B43;
    font-weight: 800;
}

h2, h3 {
    color: #234C3D;
    font-weight: 700;
}

[data-testid="stSidebar"] {
    background: #E9F3EC;
    border-left: 1px solid #D8E7DC;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2ECE4;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(31, 74, 53, 0.04);
}

[data-testid="stMetricLabel"] {
    color: #60776B;
}

[data-testid="stMetricValue"] {
    color: #176B4D;
    font-weight: 800;
}

.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-family: 'Vazirmatn', sans-serif;
    font-weight: 600;
    border: 1px solid #CFE2D5;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: #167653;
    color: white;
    border: none;
}

.stButton > button:hover {
    border-color: #167653;
    transform: translateY(-1px);
}

.game-card {
    background: white;
    padding: 23px;
    border: 1px solid #E0EBE2;
    border-radius: 20px;
    box-shadow: 0 5px 20px rgba(27, 69, 48, 0.045);
    margin-bottom: 14px;
}

.hero {
    background: linear-gradient(120deg, #155B43, #25845D);
    color: white;
    padding: 30px;
    border-radius: 24px;
    margin-bottom: 24px;
}

.hero h2, .hero p {
    color: white;
}

.eyebrow {
    color: #C8F0D8;
    font-size: 0.9rem;
    font-weight: 600;
}

.muted {
    color: #718479;
    font-size: 0.9rem;
}

div[role="radiogroup"] {
    gap: 12px;
}

hr {
    border-color: #E0EBE2;
}
</style>
""", unsafe_allow_html=True)

# ---------- منوی کناری ----------
with st.sidebar:
    st.markdown("## 🌱 قهرمانان")
    st.caption("هر روز، یک قدم قوی‌تر")
    st.divider()

    page = st.radio(
        "منوی بازی",
        [
            "🏡 خانه",
            "🗺️ مأموریت‌ها",
            "🌟 عادت‌های من",
            "🎒 فروشگاه",
            "🏆 افتخارها",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("نسخه آزمایشی بازی · ۰٫۱")

# ---------- سربرگ ----------
st.markdown("""
<div class="hero">
    <div class="eyebrow">ماجراجویی امروزت از اینجا شروع می‌شود</div>
    <h2>سلام، قهرمان! 🌿</h2>
    <p>یک مأموریت انتخاب کن، چیز تازه‌ای یاد بگیر و شخصیتت را رشد بده.</p>
</div>
""", unsafe_allow_html=True)

# ---------- اطلاعات بازیکن ----------
c1, c2, c3, c4 = st.columns(4)

c1.metric("⭐ سطح شخصیت", "۱")
c2.metric("🪙 سکه‌ها", "۱۲۰")
c3.metric("⚡ تجربه", "۶۰ / ۱۰۰")
c4.metric("🏅 نشان‌ها", "۲")

st.progress(0.60, text="۶۰٪ تا رسیدن به سطح بعد")

st.markdown("## 🗺️ مأموریت پیشنهادی امروز")

left, right = st.columns([1.6, 1], gap="large")

with left:
    st.markdown("""
    <div class="game-card">
        <div style="font-size: 42px;">☀️ 💧</div>
        <h3>راز روز داغ مدرسه</h3>
        <p>هوا گرم است و تیم مدرسه می‌خواهد فعالیت کند.
        آیا می‌توانی بهترین تصمیم‌ها را بگیری؟</p>
        <p class="muted">۳ مرحله · حدود ۳ دقیقه · پاداش: ۵۰ تجربه</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 شروع مأموریت", type="primary",
                 use_container_width=True):
        st.session_state["mission_started"] = True

    if st.session_state.get("mission_started", False):
        st.success("آماده‌ای؟ در نسخه بعد، داستان تعاملی مأموریت اینجا اجرا می‌شود.")

with right:
    st.markdown("""
    <div class="game-card">
        <h3>🎯 هدف امروز</h3>
        <p>یک فعالیت مفید انتخاب کن و اولین قدم را بردار.</p>
        <hr>
        <p>📚 مطالعه</p>
        <p>🏃 تحرک</p>
        <p>📵 مدیریت زمان صفحه‌نمایش</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## 🎒 مسیر پیشرفت")

a, b, c = st.columns(3)

with a:
    st.markdown("""
    <div class="game-card">
        <div style="font-size:32px;">🏃</div>
        <h3>قهرمان تحرک</h3>
        <p class="muted">با مأموریت‌های فعال آشنا شو.</p>
    </div>
    """, unsafe_allow_html=True)

with b:
    st.markdown("""
    <div class="game-card">
        <div style="font-size:32px;">📚</div>
        <h3>ذهن کنجکاو</h3>
        <p class="muted">با یادگیری و مطالعه پیشرفت کن.</p>
    </div>
    """, unsafe_allow_html=True)

with c:
    st.markdown("""
    <div class="game-card">
        <div style="font-size:32px;">🎨</div>
        <h3>شخصیت من</h3>
        <p class="muted">ظاهر دلخواهت را بساز.</p>
    </div>
    """, unsafe_allow_html=True)
