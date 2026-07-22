import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- تنظیمات اولیه صفحه ---
st.set_page_config(
    page_title="مدیریت هوشمند گله بز",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- تزریق استایل ۳ بعدی، رنگ کرمی-قهوه‌ای و آیکون‌های مدرن ---
st.markdown("""
    <!-- افزودن آیکون‌های مدرن FontAwesome و فونت وزیرمتن -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    * { font-family: 'Vazirmatn', sans-serif !important; }
    
    /* پس‌زمینه اصلی کرمی و گرم */
    .stApp {
        background-color: #FDFBF7 !important;
        direction: rtl;
        text-align: right;
    }
    
    /* مخفی کردن منوی مزاحم کشویی */
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="baseButton-header"] { display: none !important; }
    
    /* هدر سه بعدی لوکس با عکس بزغاله */
    .hero-3d-card {
        background: linear-gradient(135deg, #7A4B2E 0%, #9E6B48 100%);
        border-radius: 28px;
        padding: 24px;
        color: white;
        box-shadow: 0 15px 35px rgba(122, 75, 46, 0.25), inset 0 2px 3px rgba(255,255,255,0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        border: 1px solid #B88560;
    }
    .hero-title { font-size: 1.6rem; font-weight: 900; margin: 0; color: #FFF8F0; }
    .hero-subtitle { font-size: 0.85rem; color: #EADFCF; margin-top: 6px; margin-bottom: 0; }
    .goat-avatar {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        border: 3px solid #FFF8F0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        object-fit: cover;
    }
    
    /* تب‌های ۳ بعدی جدید */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F3ECE1;
        padding: 8px;
        border-radius: 20px;
        box-shadow: inset 2px 2px 6px rgba(0,0,0,0.06);
        direction: rtl;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 14px;
        font-size: 0.9rem;
        font-weight: 700;
        color: #6E5341 !important;
        border: none !important;
        transition: all 0.25s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #ffffff, #F8F3EA) !important;
        color: #7A4B2E !important;
        box-shadow: 0 6px 15px rgba(122, 75, 46, 0.12) !important;
    }

    /* کارت‌های آمار سه بعدی (Metrics) */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #F6F0E6);
        border-radius: 22px;
        padding: 20px;
        box-shadow: 8px 8px 20px #E6DDCF, -6px -6px 20px #FFFFFF;
        border: 1px solid #EFE8DC;
        text-align: center;
        transition: transform 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
    }
    div[data-testid="stMetric"] label { font-weight: bold; color: #7A6354; font-size: 0.95rem; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #7A4B2E; font-size: 1.8rem; font-weight: 900; }
    
    /* دکمه‌های ۳ بعدی شیک با افکت فشردن */
    .stButton > button {
        background: linear-gradient(135deg, #8C5A3C 0%, #6E442B 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 14px 24px !important;
        border-radius: 16px !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
        box-shadow: 0 8px 18px rgba(140, 90, 60, 0.25), inset 0 1px 0 rgba(255,255,255,0.3) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 22px rgba(140, 90, 60, 0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 4px 10px rgba(140, 90, 60, 0.2) !important;
    }

    /* فرم‌ها و ورودی‌ها */
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2D7C7 !important;
        padding: 10px 14px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    /* جداول شیک */
    div[data-testid="stDataFrame"] {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03);
        border: 1px solid #EFE8DC;
    }
    </style>
""", unsafe_allow_html=True)

# --- پایگاه داده (SQLite) ---
def get_db_connection():
    conn = sqlite3.connect('goat_farm.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS goats (
                    tag_id TEXT PRIMARY KEY, rfid_code TEXT, breed TEXT, birth_date TEXT, parity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reproduction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, tag_id TEXT, insemination_date TEXT, expected_kidding_date TEXT, dry_off_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS milk_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, tag_id TEXT, record_date TEXT, morning_kg REAL, evening_kg REAL, fat_pct REAL, protein_pct REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS treatments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, tag_id TEXT, disease TEXT, drug TEXT, treatment_date TEXT, withdrawal_days INTEGER, safe_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- هدر ۳ بعدی با عکس بزغاله بامزه ---
st.markdown("""
    <div class="hero-3d-card">
        <div>
            <h1 class="hero-title">سیستم هوشمند مدیریت گله بز</h1>
            <p class="hero-subtitle">پلتفرم مدیریت صنعتی دامداری | شناسنامه، شیردهی و سلامت</p>
        </div>
        <img src="https://images.unsplash.com/photo-1524024973431-2ad916746881?auto=format&fit=crop&w=250&q=80" class="goat-avatar" alt="بزغاله بامزه">
    </div>
""", unsafe_allow_html=True)

# --- تب‌های ناوبری ۳ بعدی با آیکون‌های مدرن ---
tab_dash, tab_goat, tab_milk, tab_repro, tab_health = st.tabs([
    "📊 داشبورد کل", 
    "🏷️ شناسنامه دام", 
    "🥛 رکورد شیر", 
    "🧬 تقویم زایش", 
    "🏥 قرنطینه و سلامت"
])

# ---------------------------------------------------------
# ۱. داشبورد کل گله
# ---------------------------------------------------------
with tab_dash:
    conn = get_db_connection()
    total_goats = conn.execute("SELECT COUNT(*) FROM goats").fetchone()[0]
    total_milk_today = conn.execute(
        "SELECT SUM(morning_kg + evening_kg) FROM milk_records WHERE record_date = ?", 
        (datetime.today().strftime('%Y-%m-%d'),)
    ).fetchone()[0] or 0.0
    active_pregnant = conn.execute("SELECT COUNT(*) FROM reproduction").fetchone()[0]
    
    today_str = datetime.today().strftime('%Y-%m-%d')
    quarantine_count = conn.execute(
        "SELECT COUNT(DISTINCT tag_id) FROM treatments WHERE safe_date > ?", (today_str,)
    ).fetchone()[0]
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("کل دام‌های ثبت‌شده", f"{total_goats} رأس")
        st.metric("دام‌های باردار فعال", f"{active_pregnant} رأس")
    with col2:
        st.metric("تولید شیر امروز", f"{round(total_milk_today, 1)} kg")
        st.metric("دام تحت قرنطینه", f"{quarantine_count} رأس")

    st.markdown("<br>", unsafe_allow_html=True)
    if quarantine_count > 0:
        st.error(f"⚠️ **هشدار قرنطینه:** شیر {quarantine_count} رأس بز به دلیل دوره پرهیز دارویی نباید وارد تانک اصلی شود!")
    else:
        st.success("✨ **وضعیت بهداشتی گله عالی است:** تمام شیرهای تولیدی امروز قابل تحویل می‌باشند.")

# ---------------------------------------------------------
# ۲. ثبت و مدیریت دام
# ---------------------------------------------------------
with tab_goat:
    st.markdown("### 🏷️ ثبت شناسنامه دیجیتال (RFID)")
    
    with st.form("add_goat_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tag_id = st.text_input("شماره پلاک گوش (Tag ID):")
            rfid_code = st.text_input("کد RFID / میکروچیپ:")
            breed = st.selectbox("نژاد بز:", ["سانن (Saanen)", "آلپاین (Alpine)", "مورسیا (Murcia)", "بومی / ترکیبی"])
        with col2:
            birth_date = st.date_input("تاریخ تولد:")
            parity = st.number_input("شکم زایش (Parity):", min_value=1, max_value=10, value=1)
        
        submit = st.form_submit_button("💾 ثبت دام در سیستم")
        if submit and tag_id:
            try:
                conn = get_db_connection()
                conn.execute("INSERT INTO goats VALUES (?, ?, ?, ?, ?)", (tag_id, rfid_code, breed, str(birth_date), parity))
                conn.commit()
                conn.close()
                st.success(f"بز با پلاک {tag_id} با موفقیت در سیستم ثبت شد.")
            except Exception as e:
                st.error("خطا: این شماره پلاک قبلاً ثبت شده است.")

    st.markdown("---")
    st.markdown("### 📋 فهرست کامل دام‌های گله")
    conn = get_db_connection()
    df_goats = pd.read_sql_query("SELECT tag_id AS 'شماره پلاک', rfid_code AS 'کد RFID', breed AS 'نژاد', birth_date AS 'تاریخ تولد', parity AS 'شکم زایش' FROM goats", conn)
    conn.close()
    st.dataframe(df_goats, use_container_width=True)

# ---------------------------------------------------------
# ۳. ثبت رکورد شیر
# ---------------------------------------------------------
with tab_milk:
    st.markdown("### 🥛 ثبت و تحلیل دوشش روزانه")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if not goat_list:
        st.info("💡 ابتدا از بخش 'شناسنامه دام'، حداقل یک بز ثبت کنید.")
    else:
        with st.form("milk_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز:", goat_list)
            record_date = st.date_input("تاریخ دوشش:", datetime.today())
            col1, col2 = st.columns(2)
            with col1:
                morning = st.number_input("شیر دوشش صبح (kg):", min_value=0.0, step=0.1)
                fat = st.number_input("درصد چربی (%):", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
            with col2:
                evening = st.number_input("شیر دوشش عصر (kg):", min_value=0.0, step=0.1)
                protein = st.number_input("درصد پروتئین (%):", min_value=0.0, max_value=10.0, value=3.2, step=0.1)
            
            submit_milk = st.form_submit_button("💾 ثبت رکورد دوشش")
            if submit_milk:
                conn = get_db_connection()
                conn.execute("INSERT INTO milk_records (tag_id, record_date, morning_kg, evening_kg, fat_pct, protein_pct) VALUES (?, ?, ?, ?, ?, ?)",
                             (selected_goat, str(record_date), morning, evening, fat, protein))
                conn.commit()
                conn.close()
                st.success("رکورد شیردهی ذخیره شد.")

# ---------------------------------------------------------
# ۴. تقویم تولیدمثل
# ---------------------------------------------------------
with tab_repro:
    st.markdown("### 🧬 مدیریت تقویم زایش (دوره ۱۵۰ روزه)")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if goat_list:
        with st.form("insemination_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز:", goat_list)
            insemination_date = st.date_input("تاریخ تلقیح / جفت‌گیری:")
            
            submit_insem = st.form_submit_button("📅 محاسبه و ثبت زمان زایش")
            if submit_insem:
                expected_kidding = insemination_date + timedelta(days=150)
                dry_off = expected_kidding - timedelta(days=60)
                
                conn = get_db_connection()
                conn.execute("INSERT INTO reproduction (tag_id, insemination_date, expected_kidding_date, dry_off_date) VALUES (?, ?, ?, ?)",
                             (selected_goat, str(insemination_date), str(expected_kidding), str(dry_off)))
                conn.commit()
                conn.close()
                st.success(f"تاریخ زایش تخمینی: {expected_kidding} | تاریخ خشک کردن: {dry_off}")

# ---------------------------------------------------------
# ۵. سلامت و قرنطینه شیر
# ---------------------------------------------------------
with tab_health:
    st.markdown("### 🏥 مدیریت سلامت و هشدار پرهیز دارویی")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if goat_list:
        with st.form("treatment_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز بیمار:", goat_list)
            disease = st.text_input("نام بیماری:")
            drug = st.text_input("نام داروی تجویزی:")
            col1, col2 = st.columns(2)
            with col1:
                treatment_date = st.date_input("تاریخ شروع درمان:")
            with col2:
                withdrawal_days = st.number_input("روزهای پرهیز شیر:", min_value=1, max_value=30, value=5)
            
            submit_treatment = st.form_submit_button("🚨 ثبت و اعمال قرنطینه شیر")
            if submit_treatment:
                safe_date = datetime.today().date() + timedelta(days=withdrawal_days)
                conn = get_db_connection()
                conn.execute("INSERT INTO treatments (tag_id, disease, drug, treatment_date, withdrawal_days, safe_date) VALUES (?, ?, ?, ?, ?, ?)",
                             (selected_goat, disease, drug, str(datetime.today().date()), withdrawal_days, str(safe_date)))
                conn.commit()
                conn.close()
                st.warning(f"شیر بز {selected_goat} تا تاریخ {safe_date} در حالت قرنطینه قرار گرفت.")
