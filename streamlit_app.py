import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- تنظیمات صفحه (مخصوص موبایل و دسکتاپ) ---
st.set_page_config(
    page_title="مدیریت هوشمند گله بز",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="collapsed" # منو در موبایل بسته می‌ماند تا صفحه شلوغ نشود
)

# --- استایل حرفه‌ای و مدرن (Custom CSS) ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    * { font-family: 'Vazirmatn', sans-serif !important; }
    .main { text-align: right; direction: rtl; background-color: #f8f9fa; }
    
    /* کارت‌های آمار شیک */
    div[data-testid="stMetric"] {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        text-align: right;
    }
    div[data-testid="stMetric"] label { font-weight: bold; color: #4a5568; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #2e7d32; font-size: 1.8rem; }
    
    /* دکمه‌های مدرن */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(46, 125, 50, 0.3); }
    
    /* منوی سمت راست */
    div[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-left: 1px solid #e2e8f0;
        text-align: right;
        direction: rtl;
    }
    
    /* فرم‌ها و ورودی‌ها */
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 8px 12px !important;
    }
    
    /* هدر اصلی */
    .header-box {
        background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%);
        color: white;
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(27, 94, 32, 0.15);
        text-align: right;
    }
    .header-box h1 { color: white; margin: 0; font-size: 1.8rem; }
    .header-box p { color: #c8e6c9; margin-top: 5px; margin-bottom: 0; }
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

# --- هدر وب‌اپلیکیشن ---
st.markdown("""
    <div class="header-box">
        <h1>🐐 سامانه هوشمند مدیریت گله بز صنعتی</h1>
        <p>پلتفرم جامع ثبت اطلاعات شناسنامه، تولیدمثل، رکورد شیر و قرنطینه بهداشتی</p>
    </div>
""", unsafe_allow_html=True)

# --- منوی دسترسی ---
st.sidebar.image("https://img.icons8.com/illustrations/100/goat.png", width=80)
st.sidebar.title("منوی کنترل")
menu = st.sidebar.radio(
    "بخش مورد نظر را انتخاب کنید:",
    ["📊 داشبورد کل گله", "🏷️ ثبت و مدیریت دام", "🥛 ثبت رکورد شیر", "🧬 تقویم تولیدمثل", "🏥 سلامت و قرنطینه شیر"]
)

# ---------------------------------------------------------
# ۱. داشبورد کل گله
# ---------------------------------------------------------
if menu == "📊 داشبورد کل گله":
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
        st.metric("کل رأس دام ثبت شده", f"{total_goats} رأس")
        st.metric("دام‌های باردار", f"{active_pregnant} رأس")
    with col2:
        st.metric("تولید شیر امروز", f"{round(total_milk_today, 1)} kg")
        st.metric("دام تحت قرنطینه دارویی", f"{quarantine_count} رأس")

    st.markdown("<br>", unsafe_allow_html=True)
    if quarantine_count > 0:
        st.error(f"⚠️ **هشدار بهداشتی فوری:** شیر {quarantine_count} رأس بز به دلیل مصرف دارو تا پایان دوره پرهیز نباید وارد مخزن اصلی شود!")
    else:
        st.success("✅ **وضعیت بهداشتی سفید:** تمامی شیرهای دوشیده شده قابل تحویل به کارخانه می‌باشند.")

# ---------------------------------------------------------
# ۲. ثبت و مدیریت دام (شناسنامه)
# ---------------------------------------------------------
elif menu == "🏷️ ثبت و مدیریت دام":
    st.subheader("🏷️ مدیریت شناسنامه دیجیتال (RFID)")
    
    tab1, tab2 = st.tabs(["➕ ثبت بز جدید", "📋 فهرست کامل دام‌ها"])
    
    with tab1:
        with st.form("add_goat_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tag_id = st.text_input("شماره پلاک گوش (Tag ID):")
                rfid_code = st.text_input("کد RFID / میکروچیپ:")
                breed = st.selectbox("نژاد:", ["سانن (Saanen)", "آلپاین (Alpine)", "مورسیا (Murcia)", "بومی / ترکیبی"])
            with col2:
                birth_date = st.date_input("تاریخ تولد:")
                parity = st.number_input(" شکم زایش (Parity):", min_value=1, max_value=10, value=1)
            
            submit = st.form_submit_button("💾 ثبت در سیستم")
            if submit and tag_id:
                try:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO goats VALUES (?, ?, ?, ?, ?)", (tag_id, rfid_code, breed, str(birth_date), parity))
                    conn.commit()
                    conn.close()
                    st.success(f"بز با پلاک {tag_id} با موفقیت ثبت شد.")
                except Exception as e:
                    st.error(f"خطا در ثبت (پلاک تکراری است): {e}")

    with tab2:
        conn = get_db_connection()
        df_goats = pd.read_sql_query("SELECT tag_id AS 'پلاک', rfid_code AS 'RFID', breed AS 'نژاد', birth_date AS 'تولد', parity AS 'شکم' FROM goats", conn)
        conn.close()
        st.dataframe(df_goats, use_container_width=True)

# ---------------------------------------------------------
# ۳. ثبت رکورد شیر
# ---------------------------------------------------------
elif menu == "🥛 ثبت رکورد شیر":
    st.subheader("🥛 ثبت و تحلیل رکورد شیردهی")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if not goat_list:
        st.info("💡 هنوز هیچ بزی ثبت نشده است. ابتدا از منوی 'ثبت و مدیریت دام' بز جدید تعریف کنید.")
    else:
        tab1, tab2 = st.tabs(["📥 ثبت دوشش جدید", "📊 رکوردهای اخیر"])
        
        with tab1:
            with st.form("milk_form", clear_on_submit=True):
                selected_goat = st.selectbox("انتخاب بز:", goat_list)
                record_date = st.date_input("تاریخ دوشش:", datetime.today())
                col1, col2 = st.columns(2)
                with col1:
                    morning = st.number_input("شیر صبح (kg):", min_value=0.0, step=0.1)
                    fat = st.number_input("چربی (%):", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
                with col2:
                    evening = st.number_input("شیر عصر (kg):", min_value=0.0, step=0.1)
                    protein = st.number_input("پروتئین (%):", min_value=0.0, max_value=10.0, value=3.2, step=0.1)
                
                submit_milk = st.form_submit_button("💾 ثبت رکورد شیر")
                if submit_milk:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO milk_records (tag_id, record_date, morning_kg, evening_kg, fat_pct, protein_pct) VALUES (?, ?, ?, ?, ?, ?)",
                                 (selected_goat, str(record_date), morning, evening, fat, protein))
                    conn.commit()
                    conn.close()
                    st.success("رکورد شیر با موفقیت ثبت شد.")

        with tab2:
            conn = get_db_connection()
            df_milk = pd.read_sql_query("SELECT tag_id AS 'پلاک', record_date AS 'تاریخ', (morning_kg + evening_kg) AS 'مجموع شیر (kg)', fat_pct AS 'چربی %', protein_pct AS 'پروتئین %' FROM milk_records ORDER BY id DESC LIMIT 15", conn)
            conn.close()
            st.dataframe(df_milk, use_container_width=True)

# ---------------------------------------------------------
# ۴. تقویم تولیدمثل
# ---------------------------------------------------------
elif menu == "🧬 تقویم تولیدمثل":
    st.subheader("🧬 تقویم زایش و خشک‌کردن (دوره ۱۵۰ روزه)")
    
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
                st.success(f"تاریخ تخمینی زایش: {expected_kidding} | زمان خشک کردن: {dry_off}")

        st.markdown("---")
        conn = get_db_connection()
        df_repro = pd.read_sql_query("SELECT tag_id AS 'پلاک', insemination_date AS 'تاریخ تلقیح', dry_off_date AS 'زمان خشک‌کردن', expected_kidding_date AS 'تاریخ زایش' FROM reproduction ORDER BY expected_kidding_date ASC", conn)
        conn.close()
        st.dataframe(df_repro, use_container_width=True)

# ---------------------------------------------------------
# ۵. سلامت و پرهیز دارویی
# ---------------------------------------------------------
elif menu == "🏥 سلامت و قرنطینه شیر":
    st.subheader("🏥 مدیریت درمان و قرنطینه شیر (Withdrawal Alert)")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if goat_list:
        with st.form("treatment_form", clear_on_submit=True):
            selected_goat = st.selectbox("انتخاب بز بیمار:", goat_list)
            disease = st.text_input("نام بیماری (مثال: ورم پستان):")
            drug = st.text_input("نام دارو:")
            col1, col2 = st.columns(2)
            with col1:
                treatment_date = st.date_input("تاریخ شروع درمان:")
            with col2:
                withdrawal_days = st.number_input("روزهای پرهیز شیر:", min_value=1, max_value=30, value=5)
            
            submit_treatment = st.form_submit_button("🚨 ثبت و اعمال قرنطینه")
            if submit_treatment:
                safe_date = treatment_date + timedelta(days=withdrawal_days)
                conn = get_db_connection()
                conn.execute("INSERT INTO treatments (tag_id, disease, drug, treatment_date, withdrawal_days, safe_date) VALUES (?, ?, ?, ?, ?, ?)",
                             (selected_goat, disease, drug, str(treatment_date), withdrawal_days, str(safe_date)))
                conn.commit()
                conn.close()
                st.warning(f"شیر بز {selected_goat} تا تاریخ {safe_date} قرنطینه شد.")

        st.markdown("---")
        conn = get_db_connection()
        df_treatments = pd.read_sql_query("SELECT tag_id AS 'پلاک', disease AS 'بیماری', drug AS 'دارو', treatment_date AS 'تاریخ درمان', safe_date AS 'پایان قرنطینه' FROM treatments ORDER BY id DESC", conn)
        conn.close()
        st.dataframe(df_treatments, use_container_width=True)
