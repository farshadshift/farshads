import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- تنظیمات صفحه موبایل ---
st.set_page_config(
    page_title="مدیریت گله بز",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- استایل اختصاصی RTL و مدرن ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    * { font-family: 'Vazirmatn', sans-serif !important; }
    .main { text-align: right; direction: rtl; background-color: #f4f6f9; padding: 10px; }
    
    /* مخفی کردن کامل منوی کشویی مزاحم */
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="baseButton-header"] { display: none !important; }
    
    /* کارت‌های آمار شیک و برجسته */
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 10px;
    }
    div[data-testid="stMetric"] label { font-weight: bold; color: #4a5568; font-size: 0.9rem; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #2e7d32; font-size: 1.6rem; font-weight: 800; }
    
    /* دکمه‌ها */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 12px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(46, 125, 50, 0.2);
    }
    
    /* هدر بالای صفحه */
    .header-card {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 18px;
        border-radius: 18px;
        margin-bottom: 15px;
        box-shadow: 0 8px 20px rgba(27, 94, 32, 0.2);
        text-align: center;
    }
    .header-card h2 { color: white; margin: 0; font-size: 1.3rem; font-weight: 800; }
    .header-card p { color: #e8f5e9; margin-top: 4px; margin-bottom: 0; font-size: 0.8rem; }
    
    /* تب‌های بالای صفحه */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        direction: rtl;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
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

# --- هدر اصلی برنامه ---
st.markdown("""
    <div class="header-card">
        <h2>🐐 مدیریت هوشمند گله بز</h2>
        <p>سامانه ثبت شناسنامه، شیردهی، زایش و قرنطینه</p>
    </div>
""", unsafe_allow_html=True)

# --- منوی تب‌های بالای صفحه (مخصوص موبایل) ---
tab_dash, tab_goat, tab_milk, tab_repro, tab_health = st.tabs([
    "📊 داشبورد", 
    "🏷️ ثبت دام", 
    "🥛 شیردهی", 
    "🧬 زایش", 
    "🏥 سلامت"
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
        st.metric("کل دام‌ها", f"{total_goats} رأس")
        st.metric("دام‌های باردار", f"{active_pregnant} رأس")
    with col2:
        st.metric("تولید شیر امروز", f"{round(total_milk_today, 1)} kg")
        st.metric("تحت قرنطینه", f"{quarantine_count} رأس")

    st.markdown("<br>", unsafe_allow_html=True)
    if quarantine_count > 0:
        st.error(f"🚨 **هشدار:** شیر {quarantine_count} رأس بز به دلیل مصرف دارو نباید وارد تانک اصلی شود!")
    else:
        st.success("✅ **وضعیت بهداشتی:** تمام شیرهای امروز قابل تحویل می‌باشند.")

# ---------------------------------------------------------
# ۲. ثبت و مدیریت دام
# ---------------------------------------------------------
with tab_goat:
    st.subheader("🏷️ شناسنامه دام (RFID)")
    
    with st.form("add_goat_form", clear_on_submit=True):
        tag_id = st.text_input("شماره پلاک گوش (Tag ID):")
        rfid_code = st.text_input("کد RFID / میکروچیپ:")
        breed = st.selectbox("نژاد:", ["سانن (Saanen)", "آلپاین (Alpine)", "مورسیا (Murcia)", "بومی / ترکیبی"])
        birth_date = st.date_input("تاریخ تولد:")
        parity = st.number_input("شکم زایش:", min_value=1, max_value=10, value=1)
        
        submit = st.form_submit_button("💾 ثبت دام جدید")
        if submit and tag_id:
            try:
                conn = get_db_connection()
                conn.execute("INSERT INTO goats VALUES (?, ?, ?, ?, ?)", (tag_id, rfid_code, breed, str(birth_date), parity))
                conn.commit()
                conn.close()
                st.success(f"بز {tag_id} ثبت شد.")
            except Exception as e:
                st.error("خطا: این شماره پلاک قبلاً ثبت شده است.")

    st.markdown("---")
    st.subheader("📋 لیست بزهای ثبت شده")
    conn = get_db_connection()
    df_goats = pd.read_sql_query("SELECT tag_id AS 'پلاک', breed AS 'نژاد', parity AS 'شکم' FROM goats", conn)
    conn.close()
    st.dataframe(df_goats, use_container_width=True)

# ---------------------------------------------------------
# ۳. ثبت رکورد شیر
# ---------------------------------------------------------
with tab_milk:
    st.subheader("🥛 رکورد شیردهی")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if not goat_list:
        st.info("💡 ابتدا از بخش 'ثبت دام'، حداقل یک بز ثبت کنید.")
    else:
        with st.form("milk_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز:", goat_list)
            record_date = st.date_input("تاریخ دوشش:", datetime.today())
            morning = st.number_input("شیر صبح (kg):", min_value=0.0, step=0.1)
            evening = st.number_input("شیر عصر (kg):", min_value=0.0, step=0.1)
            fat = st.number_input("درصد چربی (%):", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
            
            submit_milk = st.form_submit_button("💾 ثبت دوشش")
            if submit_milk:
                conn = get_db_connection()
                conn.execute("INSERT INTO milk_records (tag_id, record_date, morning_kg, evening_kg, fat_pct, protein_pct) VALUES (?, ?, ?, ?, ?, 3.2)",
                             (selected_goat, str(record_date), morning, evening, fat))
                conn.commit()
                conn.close()
                st.success("رکورد ذخیره شد.")

# ---------------------------------------------------------
# ۴. تقویم تولیدمثل
# ---------------------------------------------------------
with tab_repro:
    st.subheader("🧬 تقویم زایش (۱۵۰ روزه)")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if goat_list:
        with st.form("insemination_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز:", goat_list)
            insemination_date = st.date_input("تاریخ جفت‌گیری / تلقیح:")
            
            submit_insem = st.form_submit_button("📅 محاسبه زمان زایش")
            if submit_insem:
                expected_kidding = insemination_date + timedelta(days=150)
                dry_off = expected_kidding - timedelta(days=60)
                
                conn = get_db_connection()
                conn.execute("INSERT INTO reproduction (tag_id, insemination_date, expected_kidding_date, dry_off_date) VALUES (?, ?, ?, ?)",
                             (selected_goat, str(insemination_date), str(expected_kidding), str(dry_off)))
                conn.commit()
                conn.close()
                st.success(f"تاریخ زایش: {expected_kidding}")

# ---------------------------------------------------------
# ۵. سلامت و قرنطینه شیر
# ---------------------------------------------------------
with tab_health:
    st.subheader("🏥 پرهیز دارویی و قرنطینه")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if goat_list:
        with st.form("treatment_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز بیمار:", goat_list)
            disease = st.text_input("نام بیماری:")
            drug = st.text_input("دارو:")
            withdrawal_days = st.number_input("روزهای پرهیز شیر:", min_value=1, max_value=30, value=5)
            
            submit_treatment = st.form_submit_button("🚨 اعمال قرنطینه")
            if submit_treatment:
                safe_date = datetime.today().date() + timedelta(days=withdrawal_days)
                conn = get_db_connection()
                conn.execute("INSERT INTO treatments (tag_id, disease, drug, treatment_date, withdrawal_days, safe_date) VALUES (?, ?, ?, ?, ?, ?)",
                             (selected_goat, disease, drug, str(datetime.today().date()), withdrawal_days, str(safe_date)))
                conn.commit()
                conn.close()
                st.warning(f"شیر تا {safe_date} قرنطینه شد.")
