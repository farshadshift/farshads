import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- تنظیمات صفحه وب ---
st.set_page_config(
    page_title="سیستم هوشمند مدیریت گله بز",
    page_icon="🐐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- استایل سفارشی راست‌چین (RTL) ---
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 8px; }
    div[data-testid="stSidebar"] { text-align: right; direction: rtl; }
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
    # جدول شناسنامه بزها
    c.execute('''CREATE TABLE IF NOT EXISTS goats (
                    tag_id TEXT PRIMARY KEY,
                    rfid_code TEXT,
                    breed TEXT,
                    birth_date TEXT,
                    parity INTEGER
                )''')
    # جدول تولیدمثل
    c.execute('''CREATE TABLE IF NOT EXISTS reproduction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT,
                    insemination_date TEXT,
                    expected_kidding_date TEXT,
                    dry_off_date TEXT
                )''')
    # جدول شیردهی
    c.execute('''CREATE TABLE IF NOT EXISTS milk_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT,
                    record_date TEXT,
                    morning_kg REAL,
                    evening_kg REAL,
                    fat_pct REAL,
                    protein_pct REAL
                )''')
    # جدول درمان و قرنطینه
    c.execute('''CREATE TABLE IF NOT EXISTS treatments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT,
                    disease TEXT,
                    drug TEXT,
                    treatment_date TEXT,
                    withdrawal_days INTEGER,
                    safe_date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- منوی اصلی وب‌اپلیکیشن ---
st.sidebar.title("🐐 سیستم مدیریت گله بز")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "منوی دسترسی:",
    ["📊 داشبورد کل گله", "🏷️ ثبت و مدیریت دام", "🥛 ثبت رکورد شیر", "🧬 تقویم تولیدمثل", "🏥 مدیریت سلامت و قرنطینه شیر"]
)

# ---------------------------------------------------------
# ۱. داشبورد کل گله
# ---------------------------------------------------------
if menu == "📊 داشبورد کل گله":
    st.title("📊 داشبورد مدیریتی گله")
    st.write("خلاصه وضعیت عملکردی دامداری منطبق بر استانداردهای اروپایی")
    
    conn = get_db_connection()
    total_goats = conn.execute("SELECT COUNT(*) FROM goats").fetchone()[0]
    total_milk_today = conn.execute(
        "SELECT SUM(morning_kg + evening_kg) FROM milk_records WHERE record_date = ?", 
        (datetime.today().strftime('%Y-%m-%d'),)
    ).fetchone()[0] or 0.0
    active_pregnant = conn.execute("SELECT COUNT(*) FROM reproduction").fetchone()[0]
    
    # هشدار پرهیز دارویی
    today_str = datetime.today().strftime('%Y-%m-%d')
    quarantine_count = conn.execute(
        "SELECT COUNT(DISTINCT tag_id) FROM treatments WHERE safe_date > ?", (today_str,)
    ).fetchone()[0]
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("کل راس دام ثبت شده", f"{total_goats} رأس")
    col2.metric("تولید شیر امروز", f"{round(total_milk_today, 1)} کیلوگرم")
    col3.metric("دام‌های باردار", f"{active_pregnant} رأس")
    col4.metric("دام‌های تحت دوره پرهیز دارویی", f"{quarantine_count} رأس", delta_color="inverse")

    st.markdown("---")
    st.subheader("⚠️ هشدارها و هشدارهای بهداشتی امروز")
    if quarantine_count > 0:
        st.error(f"توجه: شیر {quarantine_count} رأس بز به دلیل مصرف دارو نباید وارد تانک اصلی شیر شود!")
    else:
        st.success("تمامی شیرهای دوشیده شده قابل تحویل به کارخانه / تانک جمع‌آوری می‌باشند.")

# ---------------------------------------------------------
# ۲. ثبت و مدیریت دام (شناسنامه)
# ---------------------------------------------------------
elif menu == "🏷️ ثبت و مدیریت دام":
    st.title("🏷️ ثبت و مدیریت شناسنامه دیجیتال (RFID)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("ثبت بز جدید")
        with st.form("add_goat_form"):
            tag_id = st.text_input("شماره پلاک گوش (Tag ID):")
            rfid_code = st.text_input("کد میکروچیپ / RFID:")
            breed = st.selectbox("نژاد:", ["سانن (Saanen)", "آلپاین (Alpine)", "مورسیا (Murcia)", "بومی / ترکیبی"])
            birth_date = st.date_input("تاریخ تولد:")
            parity = st.number_input("شکم زایش (Parity):", min_value=1, max_value=10, value=1)
            
            submit = st.form_submit_button("ثبت در سیستم")
            if submit and tag_id:
                try:
                    conn = get_db_connection()
                    conn.execute(
                        "INSERT INTO goats VALUES (?, ?, ?, ?, ?)",
                        (tag_id, rfid_code, breed, str(birth_date), parity)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"بز با پلاک {tag_id} با موفقیت ثبت شد.")
                except Exception as e:
                    st.error(f"خطا در ثبت (احتمال تکراری بودن پلاک): {e}")

    with col2:
        st.subheader("فهرست کامل دام‌های ثبت شده")
        conn = get_db_connection()
        df_goats = pd.read_sql_query("SELECT tag_id AS 'پلاک', rfid_code AS 'کد RFID', breed AS 'نژاد', birth_date AS 'تاریخ تولد', parity AS 'شکم زایش' FROM goats", conn)
        conn.close()
        st.dataframe(df_goats, use_container_width=True)

# ---------------------------------------------------------
# ۳. ثبت رکورد شیر
# ---------------------------------------------------------
elif menu == "🥛 ثبت رکورد شیر":
    st.title("🥛 ثبت و تحلیل رکورد شیردهی")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    if not goat_list:
        st.warning("ابتدا باید حداقل یک بز در بخش شناسنامه ثبت کنید.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("ورود داده دوشش")
            with st.form("milk_form"):
                selected_goat = st.selectbox("انتخاب بز:", goat_list)
                record_date = st.date_input("تاریخ دوشش:", datetime.today())
                morning = st.number_input("شیر دوشش صبح (kg):", min_value=0.0, step=0.1)
                evening = st.number_input("شیر دوشش عصر (kg):", min_value=0.0, step=0.1)
                fat = st.number_input("درصد چربی (%):", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
                protein = st.number_input("درصد پروتئین (%):", min_value=0.0, max_value=10.0, value=3.2, step=0.1)
                
                submit_milk = st.form_submit_button("ثبت رکورد شیر")
                if submit_milk:
                    conn = get_db_connection()
                    conn.execute(
                        "INSERT INTO milk_records (tag_id, record_date, morning_kg, evening_kg, fat_pct, protein_pct) VALUES (?, ?, ?, ?, ?, ?)",
                        (selected_goat, str(record_date), morning, evening, fat, protein)
                    )
                    conn.commit()
                    conn.close()
                    st.success("رکورد شیر با موفقیت ذخیره شد.")

        with col2:
            st.subheader("جدول رکوردهای اخیر")
            conn = get_db_connection()
            df_milk = pd.read_sql_query(
                "SELECT tag_id AS 'پلاک', record_date AS 'تاریخ', morning_kg AS 'صبح', evening_kg AS 'عصر', (morning_kg + evening_kg) AS 'مجموع روزانه (kg)', fat_pct AS 'چربی %', protein_pct AS 'پروتئین %' FROM milk_records ORDER BY id DESC LIMIT 15", conn
            )
            conn.close()
            st.dataframe(df_milk, use_container_width=True)

# ---------------------------------------------------------
# ۴. تقویم تولیدمثل
# ---------------------------------------------------------
elif menu == "🧬 تقویم تولیدمثل":
    st.title("🧬 مدیریت تولیدمثل و محاسبه زمان زایش (دوره ۱۵۰ روزه)")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("ثبت تلقیح / جفت‌گیری")
        with st.form("insemination_form"):
            selected_goat = st.selectbox("انتخاب بز:", goat_list)
            insemination_date = st.date_input("تاریخ تلقیح:")
            
            submit_insem = st.form_submit_button("محاسبه و ثبت تقویم")
            if submit_insem:
                # الگوریتم ۱۵۰ روز بارداری و ۶۰ روز خشک کردن (استاندارد فرانسه/هلند)
                expected_kidding = insemination_date + timedelta(days=150)
                dry_off = expected_kidding - timedelta(days=60)
                
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO reproduction (tag_id, insemination_date, expected_kidding_date, dry_off_date) VALUES (?, ?, ?, ?)",
                    (selected_goat, str(insemination_date), str(expected_kidding), str(dry_off))
                )
                conn.commit()
                conn.close()
                st.success("تاریخ زایش و خشک کردن با موفقیت محاسبه و ثبت شد.")

    with col2:
        st.subheader("تقویم زایش گله")
        conn = get_db_connection()
        df_repro = pd.read_sql_query(
            "SELECT tag_id AS 'پلاک بز', insemination_date AS 'تاریخ تلقیح', dry_off_date AS 'زمان خشک کردن', expected_kidding_date AS 'تاریخ تخمینی زایش' FROM reproduction ORDER BY expected_kidding_date ASC", conn
        )
        conn.close()
        st.dataframe(df_repro, use_container_width=True)

# ---------------------------------------------------------
# ۵. مدیریت سلامت و پرهیز دارویی
# ---------------------------------------------------------
elif menu == "🏥 مدیریت سلامت و قرنطینه شیر":
    st.title("🏥 مدیریت سلامت و هشدار عدم ورود شیر به تانک (Withdrawal Alert)")
    st.info("بر اساس قوانین اتحادیه اروپا، شیر بزهایی که آنتی‌بیوتیک یا داروی خاص مصرف می‌کنند تا پایان دوره پرهیز نباید وارد مخزن شیر شود.")
    
    conn = get_db_connection()
    goat_list = [row['tag_id'] for row in conn.execute("SELECT tag_id FROM goats").fetchall()]
    conn.close()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("ثبت درمان دارویی")
        with st.form("treatment_form"):
            selected_goat = st.selectbox("انتخاب بز بیمار:", goat_list)
            disease = st.text_input("نام بیماری (مثال: ورم پستان):")
            drug = st.text_input("نام داروی تزریقی / تجویزی:")
            treatment_date = st.date_input("تاریخ شروع درمان:")
            withdrawal_days = st.number_input("دوره پرهیز مصرف شیر (روز):", min_value=1, max_value=30, value=5)
            
            submit_treatment = st.form_submit_button("ثبت و اعمال قرنطینه شیر")
            if submit_treatment:
                safe_date = treatment_date + timedelta(days=withdrawal_days)
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO treatments (tag_id, disease, drug, treatment_date, withdrawal_days, safe_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (selected_goat, disease, drug, str(treatment_date), withdrawal_days, str(safe_date))
                )
                conn.commit()
                conn.close()
                st.warning(f"شیر بز {selected_goat} تا تاریخ {safe_date} در حالت قرنطینه قرار گرفت!")

    with col2:
        st.subheader("سابقه درمان‌ها و وضعیت فعلی سلامت")
        conn = get_db_connection()
        df_treatments = pd.read_sql_query(
            "SELECT tag_id AS 'پلاک بز', disease AS 'بیماری', drug AS 'دارو', treatment_date AS 'تاریخ درمان', safe_date AS 'تاریخ پایان قرنطینه شیر' FROM treatments ORDER BY id DESC", conn
        )
        conn.close()
        st.dataframe(df_treatments, use_container_width=True)
