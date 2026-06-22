import streamlit as st
import pandas as pd
import json
from datetime import datetime
import requests

DABO_WAGA = 9

# --- 🌐 SUPABASE CLOUD DATABASE CONFIG ---
SUPABASE_URL = "https://fcerzqxtdrlfrtqjubvz.supabase.co"
SUPABASE_KEY = "sb_publishable_J3ZTXdoo6e3y7RYd44p6SA_PZmtVYdg"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- 🗄 የሪሳይክል ቢን ሲስተም መጀመሪያ መነሳት ---
if "recycle_bin" not in st.session_state:
    st.session_state.recycle_bin = {"staff": {}, "expenses": {}, "flour": {}}

# --- 🗄 የዳታቤዝ ረዳት ተግባራት ---
def init_db():
    pass

def load_dube_record():
    url = f"{SUPABASE_URL}/rest/v1/dube_record?select=*"
    res = requests.get(url, headers=HEADERS)
    dube_data = {}
    if res.status_code == 200:
        for row in res.json():
            dube_data[row['customer_name']] = {
                'original': int(row['original']),
                'paid': int(row['paid']),
                'yedere_dube': int(row['yedere_dube'])
            }
    return dube_data

def save_dube_record(dube_data):
    for name, v in dube_data.items():
        payload = {
            "customer_name": name,
            "original": int(v['original']),
            "paid": int(v['paid']),
            "yedere_dube": int(v['yedere_dube'])
        }
        url = f"{SUPABASE_URL}/rest/v1/dube_record"
        headers_upsert = HEADERS.copy()
        headers_upsert["Prefer"] = "resolution=merge-duplicates"
        requests.post(url, headers=headers_upsert, json=payload)

def load_staff_history():
    url = f"{SUPABASE_URL}/rest/v1/staff_history?select=*"
    res = requests.get(url, headers=HEADERS)
    history = {}
    if res.status_code == 200:
        for row in res.json():
            try: coll_names = json.loads(row['collected_names'])
            except: coll_names = {}
            try: today_details = json.loads(row['today_dube_details'])
            except: today_details = {}
            
            history[row['record_id']] = {
                'staff_name': row['staff_name'], 'date': row['date'],
                'morning_load': row['morning_load'], 'returned': row['returned'],
                'cash_sold_dabo': row['cash_sold_dabo'], 'cash_sold_birr': row['cash_sold_birr'],
                'new_dube_dabo': row['new_dube_dabo'], 'today_dube_details': today_details,
                'coll_dabo': row['coll_dabo'], 'coll_birr': row['coll_birr'],
                'collected_names': coll_names, 'expected_birr': row['expected_birr'],
                'actual_birr': row['actual_birr'], 'diff': row['diff']
            }
    return history

def save_staff_record_single(r_id, r):
    payload = {
        "record_id": r_id, "staff_name": r['staff_name'], "date": r['date'],
        "morning_load": int(r.get('morning_load', 0)), "returned": int(r.get('returned', 0)),
        "cash_sold_dabo": int(r.get('cash_sold_dabo', 0)), "cash_sold_birr": float(r.get('cash_sold_birr', 0)),
        "new_dube_dabo": int(r.get('new_dube_dabo', 0)), "today_dube_details": json.dumps(r.get('today_dube_details', {})),
        "coll_dabo": int(r.get('coll_dabo', 0)), "coll_birr": float(r.get('coll_birr', 0)),
        "collected_names": json.dumps(r.get('collected_names', {})), "expected_birr": float(r.get('expected_birr', 0)),
        "actual_birr": float(r.get('actual_birr', 0)), "diff": float(r.get('diff', 0))
    }
    url = f"{SUPABASE_URL}/rest/v1/staff_history"
    headers_upsert = HEADERS.copy()
    headers_upsert["Prefer"] = "resolution=merge-duplicates"
    requests.post(url, headers=headers_upsert, json=payload)

# 🗑 የሰራተኛ ሪፖርት ሪሳይክል ቢን ፈንክሽኖች
def delete_staff_record(r_id):
    global staff_history
    if r_id in staff_history:
        st.session_state.recycle_bin["staff"][r_id] = staff_history[r_id]
        url = f"{SUPABASE_URL}/rest/v1/staff_history?record_id=eq.{r_id}"
        requests.delete(url, headers=HEADERS)
        del staff_history[r_id]

def load_expenses():
    url = f"{SUPABASE_URL}/rest/v1/expenses?select=*"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return {"list": res.json()}
    return {"list": []}

def add_expense(item, amount):
    payload = {
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "item": item,
        "amount": float(amount)
    }
    headers_expense = HEADERS.copy()
    headers_expense["Prefer"] = "return=representation"
    url = f"{SUPABASE_URL}/rest/v1/expenses"
    requests.post(url, headers=headers_expense, json=payload)

# 🗑 የወጪ እና የዱቄት መሰረዣ (ወደ ሪሳይክል ቢን ማዛወሪያ)
def delete_expense_to_bin(exp_obj, is_flour=False):
    exp_id = exp_obj.get('id')
    if is_flour:
        st.session_state.recycle_bin["flour"][exp_id] = exp_obj
    else:
        st.session_state.recycle_bin["expenses"][exp_id] = exp_obj
    
    url = f"{SUPABASE_URL}/rest/v1/expenses?id=eq.{exp_id}"
    requests.delete(url, headers=HEADERS)

# ዳታዎችን ከCloud መጫን
dube_mezgebiya = load_dube_record()
staff_history = load_staff_history()
expenses_data = load_expenses()

def get_daily_id(s_name):
    return f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{s_name}"

# --- 🔒 የመግቢያ ሲስተም ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center;'>🔐 ቢላል ዳቦ ቤት - መግቢያ ማረጋገጫ</h2>", unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("የተጠቃሚ ስም (Username)", key="username_login")
        password = st.text_input("የይለፍ ቃል (Password)", type="password", key="password_login")
        
        if st.button("🚪 ግባ (Login)"):
            if username == "bilal" and password == "dabo1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ የተሳሳተ የተጠቃሚ ስም ወይም የይለፍ ቃል!")
    return False

if check_password():
    st.set_page_config(page_title="ቢላል ዳቦ ቤት", layout="wide")
    st.title("🥖 ቢላል ዳቦ ቤት - የላቀ የሂሳብ መቆጣጠሪያ ")

    menu = [
        "🏠 ዋና ገጽ (Dashboard)", 
        "📝 [1] አዲስ ዱቤ", 
        "💰 [2] ዱቤ መቀበያ", 
        "📊 [3] ስራ መዝጊያ", 
        "📜 [4] ሪፖርት",
        "🛠 [5] ማስተካከያ (EDIT)", 
        "💸 [6] ወጪ መመዝገቢያ",
        "🗑 [7] ሪሳይክል ቢን",
        "🚪 ውጣ (Logout)"
    ]
    choice = st.sidebar.selectbox("የአሰሳ ማውጫ", menu)

    if choice == "🚪 ውጣ (Logout)":
        st.session_state.authenticated = False
        st.rerun()

    # --- 🏠 ዋና ገጽ (Dashboard) ---
    if choice == "🏠 ዋና ገጽ (Dashboard)":
        try:
            url_exp = f"{SUPABASE_URL}/rest/v1/expenses"
            res_exp = requests.get(url_exp, headers=HEADERS)
            live_expenses = res_exp.json() if res_exp.status_code == 200 else []
        except:
            live_expenses = []
            
        total_uncollected_dabo = sum(max(0, v.get('original', 0) + v.get('yedere_dube', 0) - v.get('paid', 0)) for v in dube_mezgebiya.values())
        total_uncollected_birr = total_uncollected_dabo * DABO_WAGA
        
        total_expenses = 0
        if isinstance(live_expenses, list):
            total_expenses = sum(float(e.get('amount', 0)) for e in live_expenses if "🌾 ዱቄት" not in str(e.get('item','')))
        
        st.subheader("📈 የዛሬው አጠቃላይ የሂሳብ ሁኔታ")
        col1, col2, col3 = st.columns(3)
        col1.metric("ያልተሰበሰበ ጠቅላላ ዳቦ", f"{total_uncollected_dabo} ዳቦ")
        col2.metric("የዳቦ ነጠላ ዋጋ", f"{DABO_WAGA} ብር")
        col3.metric("የወጣ ጠቅላላ ወጪ", f"{total_expenses} ብር")
        
        st.write("---")
        st.subheader("🔴 ዱቤ ያልከፈሉ ደንበኞች ስም ዝርዝር")
        
        dashboard_data = []
        for name, data in dube_mezgebiya.items():
            unpaid_dabo = (data.get('original', 0) + data.get('yedere_dube', 0)) - data.get('paid', 0)
            if unpaid_dabo > 0:
                dashboard_data.append({
                    "የደንበኛ ስም": name,
                    "ያልተከፈለ ዕዳ (ዳቦ)": unpaid_dabo,
                    "ዕዳ በብር": unpaid_dabo * DABO_WAGA
                })
        
        if dashboard_data:
            df = pd.DataFrame(dashboard_data)
            df.index = df.index + 1
            st.table(df)
        else:
            st.success("🎉 በአሁኑ ሰዓት ምንም ያልተሰበሰበ የዳቦ ዕዳ የለም!")

    # --- 📝 [1] አዲስ ዱቤ ---
    elif choice == "📝 [1] አዲስ ዱቤ":
        st.header("📝 አዲስ ዱቤ መመዝገቢያ")
        with st.form("new_dube_form", clear_on_submit=True):
            name = st.text_input("የደንበኛ ስም").strip()
            count = st.number_input("ለደንበኛው የተሰጠ የዳቦ ብዛት", min_value=1, step=1)
            submit = st.form_submit_button("✅ መዝግብ")
            
            if submit and name:
                if name in dube_mezgebiya: 
                    dube_mezgebiya[name]['original'] += count
                else: 
                    dube_mezgebiya[name] = {'original': count, 'paid': 0, 'yedere_dube': 0}
                save_dube_record(dube_mezgebiya)
                st.success(f"✅ ለ {name} {count} ዳቦ ተመዝግቧል!")
                st.rerun()

        st.write("---")
        st.subheader("🔄 የደንበኞች ጠቅላላ ዕዳ ማስተካከያ")
        active_debtors = {}
        for k, v in dube_mezgebiya.items():
            total_debt = (v.get('original', 0) + v.get('yedere_dube', 0)) - v.get('paid', 0)
            if total_debt > 0: active_debtors[k] = total_debt
        
        if active_debtors:
            edit_name = st.selectbox("ማስተካከል የሚፈልጉትን ደንበኛ ስም ይምረጡ፦", list(active_debtors.keys()))
            current_total = active_debtors[edit_name]
            st.warning(f"👉 {edit_name} ዕዳ፦ {current_total} ዳቦ")
            new_total_val = st.number_input("ትክክለኛውን ጠቅላላ የዳቦ ብዛት ያስገቡ፦", min_value=0, step=1, value=int(current_total))
            
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 የዳቦ መጠን አስተካክል"):
                    if new_total_val == 0:
                        dube_mezgebiya[edit_name].update({'original': 0, 'yedere_dube': 0, 'paid': 0})
                    else:
                        dube_mezgebiya[edit_name].update({'yedere_dube': new_total_val, 'original': 0, 'paid': 0})
                    save_dube_record(dube_mezgebiya)
                    st.success("🔄 ተስተካክሏል!")
                    st.rerun()
            with col_del:
                if st.button("🗑 ዕዳ ሙሉ በሙሉ ሰርዝ"):
                    dube_mezgebiya[edit_name].update({'original': 0, 'yedere_dube': 0, 'paid': 0})
                    save_dube_record(dube_mezgebiya)
                    st.success("🗑 ተሰርዟል!")
                    st.rerun()

    # --- 💰 [2] ዱቤ መቀበያ ---
    elif choice == "💰 [2] ዱቤ መቀበያ":
        st.header("💰 ዱቤ መቀበያ")
        s_name = st.text_input("ተቀባይ ሰራተኛ ስም").strip().capitalize()
        custs = [n for n, d in dube_mezgebiya.items() if (d.get('yedere_dube', 0) + d['original'] - d['paid']) > 0]
        
        if not custs: st.info("ምንም ዕዳ ያለበት ደንበኛ የለም።")
        elif s_name:
            sel_name = st.selectbox("የደንበኛ ስም ይምረጡ", custs)
            d = dube_mezgebiya[sel_name]
            qeri = d.get('yedere_dube', 0) + d['original'] - d['paid']
            st.warning(f"👉 {sel_name} ቀሪ ዕዳ: {qeri} ዳቦ")
            amt = st.number_input("የተቀበሉት የዳቦ መጠን", min_value=1, max_value=int(qeri), step=1)
            
            if st.button("✅ ክፍያ መዝግብ"):
                dube_mezgebiya[sel_name]['paid'] += amt
                rec_id = get_daily_id(s_name)
                if rec_id not in staff_history:
                    staff_history[rec_id] = {"staff_name": s_name, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "coll_dabo": 0, "coll_birr": 0, "collected_names": {}, "today_dube_details": {}}
                
                staff_history[rec_id]["collected_names"][sel_name] = staff_history[rec_id]["collected_names"].get(sel_name, 0) + amt
                staff_history[rec_id]["coll_dabo"] = sum(staff_history[rec_id]["collected_names"].values())
                staff_history[rec_id]["coll_birr"] = staff_history[rec_id]["coll_dabo"] * DABO_WAGA
                save_dube_record(dube_mezgebiya)
                save_staff_record_single(rec_id, staff_history[rec_id])
                st.success(f"✅ ከ {sel_name} ተቀብሏል!")
                st.rerun()

    # --- 📊 [3] ስራ መዝጊያ ---
    elif choice == "📊 [3] ስራ መዝጊያ":
        st.header("📊 የዕለት ስራ መዝጊያ")
        s_name = st.text_input("የሰራተኛው ስም").strip().capitalize()
        
        if s_name:
            col1, col2 = st.columns(2)
            wosede = col1.number_input("📦 ጠዋት የወሰደው ዳቦ", min_value=0, step=1)
            melesse = col2.number_input("📦 ማታ የመለሰው ዳቦ", min_value=0, step=1)
            
            st.write("---")
            st.subheader("➕ አዲስ ዱቤ የወሰዱ")
            if "closing_new_dube" not in st.session_state: st.session_state.closing_new_dube = [{"name": "", "amt": 0}]
            
            recorded_today_dube = {}
            new_dube_total = 0
            for idx, item in enumerate(st.session_state.closing_new_dube):
                c1, c2 = st.columns(2)
                d_n = c1.text_input(f"የደንበኛ ስም {idx+1}", value=item["name"], key=f"cls_new_name_{idx}").strip()
                d_a = c2.number_input(f"ዳቦ ብዛት {idx+1}", value=item["amt"], min_value=0, step=1, key=f"cls_new_amt_{idx}")
                if d_n and d_a > 0:
                    recorded_today_dube[d_n] = d_a
                    new_dube_total += d_a
                    
            if st.button("➕ ሌላ አዲስ ዱቤ ጨምር"):
                st.session_state.closing_new_dube.append({"name": "", "amt": 0})
                st.rerun()
                
            st.write("---")
            st.subheader("💰 የድሮ ዱቤ መቀበያ (የተሰበሰበ)")
            custs = [n for n, d in dube_mezgebiya.items() if (d.get('yedere_dube',0) + d['original'] - d['paid']) > 0]
            
            collected_names = {}
            for name in custs:
                d = dube_mezgebiya[name]
                qeri_h = d.get('yedere_dube', 0) + d['original'] - d['paid']
                ans = st.number_input(f"👉 {name} ({qeri_h} አለበት)፦", min_value=0, max_value=int(qeri_h), step=1, key=f"cls_coll_{name}")
                if ans > 0: collected_names[name] = ans

            st.write("---")
            st.subheader("💸 የዕለት ወጪ መመዝገቢያ (ካለ)")
            exp_item = st.text_input("የወጪ ምክንያት (ምሳሌ፡ የላስቲክ...)").strip()
            exp_amount = st.number_input("የወጪ ብር መጠን", min_value=0.0, step=1.0)

            st.write("---")
            st.subheader("💰 ሰራተኛው ያስረከበው ብር (Actual Birr)")
            actual_birr = st.number_input("💰 ሰራተኛው ያስረከበው ብር", min_value=0.
