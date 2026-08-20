import streamlit as st
import pandas as pd
import json
import datetime
import requests

def get_ethiopian_datetime():
    import datetime
    
    # 1. የሰርቨሩን ሰዓት ወደ ኢትዮጵያ ሰዓት ማስተካከል (+3 ሰዓት)
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    
    g_year = now.year
    g_month = now.month
    g_day = now.day
    
    # 2. የጃንዋሪ 1 ቀን የኢትዮጵያ ካላንደር መነሻ ማስተካከያ ማስላት
    # የፈረንጆቹ ዓመት በ4 ሲካፈል ቀሪው 3 ከሆነ (ምሳሌ፡ 2023, 2027) ጳጉሜ 6 ትሆናለች
    is_leap = 1 if (g_year % 4 == 3) else 0
    
    # የዓመተ ምህረት ልዩነት ማግኘት
    if g_month > 9 or (g_month == 9 and g_day >= (11 + is_leap)):
        eth_year = g_year - 7
    else:
        eth_year = g_year - 8
        
    # በፈረንጆቹ ወራት መሰረት የኢትዮጵያ ወር እና ቀን መነሻ ማውጫ ማትሪክስ
    # [የኢትዮጵያ_ወር, የፈረንጆች_ቀን_ሲቀነስ_የሚጨመር_ቁጥር, የሁለተኛው_ክፍል_የኢትዮጵያ_ወር]
    if g_month == 1:    # ጃንዋሪ
        start_matrix = [4, 8, 5] if (g_year % 4 == 1) else [4, 8, 5]
    elif g_month == 2:  # ፌብሩዋሪ
        start_matrix = [5, 7, 6]
    elif g_month == 3:  # ማርች
        start_matrix = [6, 9, 7] if ((g_year - 1) % 4 == 3) else [6, 9, 7]
    elif g_month == 4:  # ኤፕሪል
        start_matrix = [7, 8, 8]
    elif g_month == 5:  # ሜይ
        start_matrix = [8, 8, 9]
    elif g_month == 6:  # ጁን
        start_matrix = [9, 7, 10]
    elif g_month == 7:  # ጁላይ (አሁን ያለንበት ወር)
        start_matrix = [10, 7, 11]
    elif g_month == 8:  # ኦገስት
        start_matrix = [11, 6, 12]
    elif g_month == 9:  # ሴፕቴምበር
        start_matrix = [12, 5, 13]
    elif g_month == 10: # ኦክቶበር
        start_matrix = [1, 11, 2] if (g_year % 4 == 3) else [1, 10, 2]
    elif g_month == 11: # ኖቬምበር
        start_matrix = [2, 10, 3] if (g_year % 4 == 3) else [2, 9, 3]
    elif g_month == 12: # ዲሴምበር
        start_matrix = [3, 10, 4] if (g_year % 4 == 3) else [3, 9, 4]

    # የትክክለኛውን ቀን እና ወር ስሌት ማውጣት
    # ማርች ላይ የካቲት 29 ካለ ማስተካከያ ይደረጋል
    offset_day = start_matrix[1]
    if g_month == 3 and (g_year % 4 == 0):
        offset_day = 8
        
    if g_day <= offset_day:
        eth_month = start_matrix[0]
        # ወሩ ከመግባቱ በፊት የባለፈው ወር ቀሪ ቀናትን መቁጠር
        if g_month == 3 and (g_year % 4 == 0):
            eth_day = g_day + 22
        elif g_month == 1:
            eth_day = g_day + 23 if ((g_year-1) % 4 == 3) else g_day + 22
        elif g_month in [2, 4, 5, 7, 8]:
            eth_day = g_day + 23
        elif g_month in [6, 9, 10, 11, 12]:
            eth_day = g_day + 22
    else:
        eth_month = start_matrix[2]
        eth_day = g_day - offset_day

    # የሴፕቴምበር (አዲስ ዓመት) ልዩ ማስተካከያ
    if g_month == 9:
        new_year_day = 12 if (g_year % 4 == 3) else 11
        if g_day >= new_year_day:
            eth_month = 1
            eth_day = g_day - new_year_day + 1
        else:
            eth_month = 13
            eth_day = g_day - 5

    # 3. ሰዓቱን በ24 ሰዓት ፎርማት መውሰድ
    time_str = now.strftime("%H:%M")
    
    # ውጤት፡ ዓመት-ወር-ቀን ሰዓት (ምሳሌ፡ 2018-10-30 11:15)
    return f"{eth_year}-{eth_month:02d}-{eth_day:02d} {time_str}"
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

def delete_staff_record(r_id):
    url = f"{SUPABASE_URL}/rest/v1/staff_history?record_id=eq.{r_id}"
    requests.delete(url, headers=HEADERS)

def load_expenses():
    url = f"{SUPABASE_URL}/rest/v1/expenses?select=*"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return {"list": res.json()}
    return {"list": []}

def add_expense(item, amount):
    payload = {
        "date": get_ethiopian_datetime(),
        "item": item,
        "amount": float(amount)
    }
    headers_expense = HEADERS.copy()
    headers_expense["Prefer"] = "return=representation"
    
    url = f"{SUPABASE_URL}/rest/v1/expenses"
    requests.post(url, headers=headers_expense, json=payload)

def delete_expense(expense_id):
    url = f"{SUPABASE_URL}/rest/v1/expenses?id=eq.{expense_id}"
    requests.delete(url, headers=HEADERS)

# ዳታዎችን ከCloud መጫን
dube_mezgebiya = load_dube_record()
staff_history = load_staff_history()
expenses_data = load_expenses()

def get_daily_id(s_name):
    # የአሁኑን የኢትዮጵያ ቀን በ ID ውስጥ መጠቀም
    eth_now = get_ethiopian_datetime().replace(" ", "_").replace(":", "-")
    return f"{eth_now}_{s_name}"

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

    # ማውጫዎች
    menu = [
        "🏠 ዋና ገጽ (Dashboard)", 
        "📝 [1] አዲስ ዱቤ", 
        "💰 [2] ዱቤ መቀበያ", 
        "📊 [3] ስራ መዝጊያ", 
        "📜 [4] ሪፖርት",
        "🛠 [5] ማስተካከያ (EDIT)", 
        "💸 [6] ወጪ መመዝገቢያ",
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
            total_expenses = sum(float(e.get('amount', 0)) for e in live_expenses)
        
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
                confirm_del_debt = st.checkbox("🗑 በእርግጠኝነት ይጥፋ?", key=f"conf_del_debt_{edit_name}")
                if st.button("🗑 ዕዳ ሙሉ በሙሉ ሰርዝ", disabled=not confirm_del_debt):
                    dube_mezgebiya[edit_name].update({'original': 0, 'yedere_dube': 0, 'paid': 0})
                    save_dube_record(dube_mezgebiya)
                    st.success("🗑 ተሰርዟል!")
                    st.rerun()

    # --- 💰 [2] ዱቤ መቀበያ ---
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
                    staff_history[rec_id] = {"staff_name": s_name, "date": get_ethiopian_datetime(), "coll_dabo": 0, "coll_birr": 0, "collected_names": {}, "today_dube_details": {}}
                
                staff_history[rec_id]["collected_names"][sel_name] = staff_history[rec_id]["collected_names"].get(sel_name, 0) + amt
                staff_history[rec_id]["coll_dabo"] = sum(staff_history[rec_id]["collected_names"].values())
                staff_history[rec_id]["coll_birr"] = staff_history[rec_id]["coll_dabo"] * DABO_WAGA
                save_dube_record(dube_mezgebiya)
                save_staff_record_single(rec_id, staff_history[rec_id])
                st.success(f"✅ ከ {sel_name} ተቀብሏል!")
                st.rerun()


    # --- 📊 [3] ስራ መዝጊያ ---
    # --- 📊 [3] ስራ መዝጊያ ---
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
            actual_birr = st.number_input("💰 ሰራተኛው ያስረከበው ብር (Actual Birr)", min_value=0.0)
            
            if st.button("💾 የዕለት ሒሳብ ዝጋ"):
                rec_id = get_daily_id(s_name)
                if rec_id not in staff_history:
                    staff_history[rec_id] = {"staff_name": s_name, "date": get_ethiopian_datetime(), "coll_dabo": 0, "coll_birr": 0, "collected_names": {}, "today_dube_details": {}}
                    
                for d_n, d_a in recorded_today_dube.items():
                    if d_n in dube_mezgebiya: dube_mezgebiya[d_n]['original'] += d_a
                    else: dube_mezgebiya[d_n] = {'original': d_a, 'paid': 0, 'yedere_dube': 0}
                    
                for name, v in collected_names.items():
                    dube_mezgebiya[name]['paid'] += v
                    staff_history[rec_id]["collected_names"][name] = staff_history[rec_id]["collected_names"].get(name, 0) + v
                    
                coll_dabo_sum = sum(staff_history[rec_id]["collected_names"].values())
                coll_birr_sum = coll_dabo_sum * DABO_WAGA
                
                total_out = wosede - melesse
                cash_sold_dabo = total_out - new_dube_total
                cash_sold_birr = cash_sold_dabo * DABO_WAGA
                
                # 🛠 እዚህ ጋር ነው ወጪው ተቀንሶ ትክክለኛው 'Expected' የሚሰላው!
                if exp_item and exp_amount > 0:
                    add_expense(f"{s_name}: {exp_item}", exp_amount)
                    expected = cash_sold_birr + coll_birr_sum - exp_amount
                else:
                    expected = cash_sold_birr + coll_birr_sum
                
                staff_history[rec_id].update({
                    "morning_load": wosede, "returned": melesse, "cash_sold_dabo": cash_sold_dabo, 
                    "cash_sold_birr": cash_sold_birr, "new_dube_dabo": new_dube_total, 
                    "today_dube_details": recorded_today_dube, "coll_dabo": coll_dabo_sum, "coll_birr": coll_birr_sum,
                    "expected_birr": expected, "actual_birr": actual_birr, "diff": actual_birr - expected
                })
                
                for name, data in dube_mezgebiya.items():
                    data['yedere_dube'] = data.get('yedere_dube', 0) + data['original'] - data['paid']
                    data['original'] = 0; data['paid'] = 0
                    
                save_dube_record(dube_mezgebiya)
                save_staff_record_single(rec_id, staff_history[rec_id])
                st.session_state.closing_new_dube = [{"name": "", "amt": 0}]
                st.success(f"✅ {s_name} የዛሬ ሂሳብ እና ወጪ በተሳካ ሁኔታ ተመዝግቧል!")
                st.rerun()
    # --- 📜 [4] ሪፖርት ---
# --- 📜 [4] ሪፖርት ---
    elif choice == "📜 [4] ሪፖርት":
        st.header("📊 የክትትልና የሪፖርት ማዕከል")
        st.write("---")
        
        # 🛠 ቼክቦክስ - ማጠቃለያውን ለማሳየት/ለመደበቅ
        show_summary = st.checkbox("📊 የአጠቃላይ ቢዝነስ ማጠቃለያ ለማየት እዚህ ጋ ያብሩ", value=False)
        
        # --- 📅 [ክፍል 1]፡ የሙሉ ዳቦ ቤቱ የቀን/የሳምንት/የወር ጠቅላላ ማጠቃለያ ሂሳብ ---
        if show_summary:
            st.subheader("📅 የአጠቃላይ የቢዝነሱ የዘመን ክልል ማጠቃለያ (በኢትዮጵያ አቆጣጠር)")
            
            # በኢትዮጵያ አቆጣጠር የቀን መምረጫዎች
            col_eth1, col_eth2 = st.columns(2)
            with col_eth1:
                st.caption("📌 **ከቀን (የመጀመሪያ ቀን)፦**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    s_day = st.number_input("ቀን", min_value=1, max_value=30, value=1, key="s_d")
                with c2:
                    s_month = st.number_input("ወር", min_value=1, max_value=13, value=1, key="s_m")
                with c3:
                    s_year = st.number_input("ዓ.ም", min_value=2015, max_value=2030, value=2018, key="s_y")

            with col_eth2:
                st.caption("📌 **እስከ ቀን (የመጨረሻ ቀን)፦**")
                c4, c5, c6 = st.columns(3)
                with c4:
                    e_day = st.number_input("ቀን", min_value=1, max_value=30, value=30, key="e_d")
                with c5:
                    e_month = st.number_input("ወር", min_value=1, max_value=13, value=12, key="e_m")
                with c6:
                    e_year = st.number_input("ዓ.ም", min_value=2015, max_value=2030, value=2018, key="e_y")

            # ቀኖቹን ወደ YYYY-MM-DD ፎርማት ማዘጋጀት
            s_str = f"{s_year:04d}-{s_month:02d}-{s_day:02d}"
            e_str = f"{e_year:04d}-{e_month:02d}-{e_day:02d}"

            if s_str <= e_str:
                st.success(f"📅 የተመረጠው ክልል፦ ከ **{s_str}** እስከ **{e_str}**")
                
                # ቀናትን መሰረት ያደረገ የመረጃ ማደራጃ ዲክሽነሪ
                daily_summary = {}

                # 1. የሰራተኞችን መረጃ በቀን መደመር
                for r in staff_history.values():
                    r_date_str = str(r.get('date', ''))[:10]
                    if s_str <= r_date_str <= e_str:
                        if r_date_str not in daily_summary:
                            daily_summary[r_date_str] = {
                                "morning_load": 0, "returned": 0, "cash_sold_dabo": 0,
                                "cash_sold_birr": 0, "coll_dabo": 0, "coll_birr": 0,
                                "new_dube_dabo": 0, "expected_birr": 0, "actual_birr": 0,
                                "diff": 0, "expense": 0, "duket_bags": 0
                            }
                        
                        d_item = daily_summary[r_date_str]
                        d_item["morning_load"] += r.get('morning_load', 0)
                        d_item["returned"] += r.get('returned', 0)
                        d_item["cash_sold_dabo"] += r.get('cash_sold_dabo', 0)
                        d_item["cash_sold_birr"] += r.get('cash_sold_birr', 0)
                        d_item["coll_dabo"] += r.get('coll_dabo', 0)
                        d_item["coll_birr"] += r.get('coll_birr', 0)
                        d_item["new_dube_dabo"] += r.get('new_dube_dabo', 0)
                        d_item["expected_birr"] += r.get('expected_birr', 0)
                        d_item["actual_birr"] += r.get('actual_birr', 0)
                        d_item["diff"] += r.get('diff', 0)

                # 2. የወጪ እና የዱቄት መረጃዎችን በቀን መደመር
                if expenses_data.get("list"):
                    for exp in expenses_data["list"]:
                        exp_date_str = str(exp.get('date', ''))[:10]
                        if s_str <= exp_date_str <= e_str:
                            if exp_date_str not in daily_summary:
                                daily_summary[exp_date_str] = {
                                    "morning_load": 0, "returned": 0, "cash_sold_dabo": 0,
                                    "cash_sold_birr": 0, "coll_dabo": 0, "coll_birr": 0,
                                    "new_dube_dabo": 0, "expected_birr": 0, "actual_birr": 0,
                                    "diff": 0, "expense": 0, "duket_bags": 0
                                }
                            
                            item_name = str(exp.get('item', ''))
                            if "🌾 ዱቄት" in item_name:
                                try:
                                    parts = item_name.split('(')
                                    if len(parts) > 1:
                                        num_bags = int(parts[1].split(' ')[0])
                                        daily_summary[exp_date_str]["duket_bags"] += num_bags
                                except:
                                    pass
                            else:
                                daily_summary[exp_date_str]["expense"] += float(exp.get('amount', 0))

                # ሰንጠረዡን ማዘጋጀት (ቀኑ ከቅርብ ወደ ቆየ እንዲደራደር)
                sorted_dates = sorted(daily_summary.keys(), reverse=True)
                
                if sorted_dates:
                    summary_rows = []
                    
                    # ለአጠቃላይ ድምር የሚሆኑ ተለዋዋጮች
                    tot_m_load = tot_ret = tot_cash_d = tot_cash_b = 0
                    tot_coll_d = tot_new_dube = tot_exp_b = tot_act_b = 0
                    tot_diff = tot_exp = tot_duket = 0

                    for d in sorted_dates:
                        val = daily_summary[d]
                        summary_rows.append({
                            "ቀን": d,
                            "የወጣ ዳቦ": val["morning_load"],
                            "የተመለሰ": val["returned"],
                            "ካሽ (ዳቦ)": val["cash_sold_dabo"],
                            "ካሽ (ብር)": val["cash_sold_birr"],
                            "የተሰበሰበ ዱቤ(ዳ)": val["coll_dabo"],
                            "አዲስ ዱቤ(ዳ)": val["new_dube_dabo"],
                            "የተጠበቀ ብር": val["expected_birr"],
                            "የመጣ ብር": val["actual_birr"],
                            "ልዩነት (+/-)": val["diff"],
                            "የቀኑ ወጪ": val["expense"],
                            "ወጪ ዱቄት (ጆንያ)": val["duket_bags"]
                        })
                        
                        # ሁሉንም ቀናት መደመር
                        tot_m_load += val["morning_load"]
                        tot_ret += val["returned"]
                        tot_cash_d += val["cash_sold_dabo"]
                        tot_cash_b += val["cash_sold_birr"]
                        tot_coll_d += val["coll_dabo"]
                        tot_new_dube += val["new_dube_dabo"]
                        tot_exp_b += val["expected_birr"]
                        tot_act_b += val["actual_birr"]
                        tot_diff += val["diff"]
                        tot_exp += val["expense"]
                        tot_duket += val["duket_bags"]

                    # ከስር የአጠቃላይ ቀናቶች ድምር መስመር መጨመር (Total Row)
                    summary_rows.append({
                        "ቀን": "∑ ጠቅላላ ድምር",
                        "የወጣ ዳቦ": tot_m_load,
                        "የተመለሰ": tot_ret,
                        "ካሽ (ዳቦ)": tot_cash_d,
                        "ካሽ (ብር)": tot_cash_b,
                        "የተሰበሰበ ዱቤ(ዳ)": tot_coll_d,
                        "አዲስ ዱቤ(ዳ)": tot_new_dube,
                        "የተጠበቀ ብር": tot_exp_b,
                        "የመጣ ብር": tot_act_b,
                        "ልዩነት (+/-)": tot_diff,
                        "የቀኑ ወጪ": tot_exp,
                        "ወጪ ዱቄት (ጆንያ)": tot_duket
                    })
                    
                    df_summary = pd.DataFrame(summary_rows)
                    st.write("---")
                    st.markdown(f"##### 🏢 ከ **{s_str}** እስከ **{e_str}** ያለው የቀን በቀን አጠቃላይ የቢዝነስ ሰንጠረዥ፦")
                    st.dataframe(df_summary, use_container_width=True, hide_index=True)
                else:
                    st.info("በተመረጠው የጊዜ ክልል ውስጥ ምንም የተመዘገበ መረጃ የለም።")
            else:
                st.error("❌ ስህተት፡ የ 'ከቀን' መጀመሪያ ከ 'እስከ ቀን' ማነስ አለበት!")
        
        st.write("---")
        
        # --- 🔴 [ክፍል 2]፡ ዱቤ ያልከፈሉ ደንበኞች ስም ዝርዝር ---
        st.header("🔴 ዱቤ ያልከፈሉ ደንበኞች ስም ዝርዝር")
        rows = []
        for k, v in dube_mezgebiya.items():
            qeri_total = v.get('yedere_dube', 0) + v.get('original', 0) - v.get('paid', 0)
            if qeri_total > 0:
                rows.append({"የደንበኛ ስም": k, "ያልተከፈለ ዕዳ (ዳቦ)": qeri_total, "ዕዳ በብር": qeri_total * DABO_WAGA})
        
        if rows:
            df_dube = pd.DataFrame(rows)
            st.dataframe(df_dube, use_container_width=True)
        else:
            st.success("ምንም የዱቤ ዕዳ የለም። 🎉")
        
        st.write("---")
        
        # --- 📜 [ክፍል 3]፡ የሰራተኞች የዕለት ሪፖርት ዝርዝር (ከነ Edit ማድረጊያው) ---
        st.header("📜 የሰራተኞች የዕለት ሪፖርት ዝርዝር")
        all_s = sorted(list(set([r['staff_name'] for r in staff_history.values() if 'staff_name' in r])))
        
        if all_s:
            sel_staff = st.selectbox("ሰራተኛ ይምረጡ", all_s)
            staff_recs = sorted([(r_id, r) for r_id, r in staff_history.items() if r.get('staff_name') == sel_staff], key=lambda x: x[1].get('date', ''), reverse=True)
            
            rep_rows = []
            for r_id, r in staff_recs:
                cash_birr = r.get('cash_sold_birr', 0)
                coll_dabo = r.get('coll_dabo', 0)
                coll_birr = r.get('coll_birr', 0)
                
                expected_birr = r.get('expected_birr', 0)
                calculated_expense = (cash_birr + coll_birr) - expected_birr
                if calculated_expense < 0: calculated_expense = 0
                
                rep_rows.append({
                    "ቀንና ሰዓት": r.get('date',''), 
                    "ወጣ": r.get('morning_load',0), 
                    "ገባ": r.get('returned',0),
                    "ካሽ(ዳ)": r.get('cash_sold_dabo',0), 
                    "ካሽ(ብር)": cash_birr,
                    "ዱቤ(ዳ)": coll_dabo,
                    "ዱቤ(ብር)": coll_birr, 
                    "አዲስ ዱ": r.get('new_dube_dabo',0),
                    "የዕለት ወጪ": calculated_expense,
                    "የተጠበቀ": expected_birr, 
                    "የመጣ": r.get('actual_birr',0), 
                    "+/-": r.get('diff',0)
                })
            
            df_rep = pd.DataFrame(rep_rows)
            st.dataframe(df_rep, use_container_width=True)
            
            st.subheader("📅 የዕለት ዝርዝር መረጃ እና ማስተካከያ (Edit/Delete)")
            for r_id, rec in staff_recs:
                expander_title = f"📅 ሪፖርት ቀን፦ {rec.get('date','')} ({rec.get('staff_name','')})"
                with st.expander(expander_title):
                    tab_info, tab_edit, tab_del = st.tabs(["👁 ዝርዝር መረጃ", "✏️ ማስተካከያ (Edit)", "🗑 ሰርዝ"])
                    
                    # 1. የዝርዝር መረጃ ታብ
                    with tab_info:
                        if rec.get("collected_names"):
                            st.write("💵 የድሮ ዱቤ የተቀበለው፦")
                            for c_n, c_a in rec["collected_names"].items():
                                st.write(f"👉 {c_n}: {c_a} ዳቦ")
                        if rec.get("today_dube_details"):
                            st.write("📦 አዲስ ዱቤ የወሰዱ፦")
                            for n_n, n_a in rec["today_dube_details"].items():
                                st.write(f"🔸 {n_n}: {n_a} ዳቦ")
                        if not rec.get("collected_names") and not rec.get("today_dube_details"):
                            st.info("ምንም ተጨማሪ የዱቤ ዝርዝር የለውም።")

                    # 2. የ Edit (ማስተካከያ) ታብ
                    with tab_edit:
                        st.subheader("✏️ የሪፖርት መረጃ ማስተካከያ")
                        with st.form(f"edit_form_{r_id}"):
                            c_e1, c_e2, c_e3 = st.columns(3)
                            with c_e1:
                                new_morning = st.number_input("የወጣ ዳቦ", min_value=0, value=int(rec.get('morning_load', 0)))
                                new_returned = st.number_input("የተመለሰ ዳቦ", min_value=0, value=int(rec.get('returned', 0)))
                            with c_e2:
                                new_actual_birr = st.number_input("የመጣ ብር (Actual)", min_value=0.0, value=float(rec.get('actual_birr', 0.0)))
                                new_cash_dabo = st.number_input("በካሽ የተሸጠ ዳቦ", min_value=0, value=int(rec.get('cash_sold_dabo', 0)))
                            with c_e3:
                                new_new_dube = st.number_input("አዲስ ዱቤ (ዳቦ)", min_value=0, value=int(rec.get('new_dube_dabo', 0)))
                                new_coll_dabo = st.number_input("ከድሮ ዱቤ የተሰበሰበ (ዳቦ)", min_value=0, value=int(rec.get('coll_dabo', 0)))
                            
                            save_edit = st.form_submit_button("💾 ለውጦቹን አስቀምጥ")
                            
                            if save_edit:
                                # በድጋሚ ሂሳቡን ማስላት
                                new_cash_birr = new_cash_dabo * DABO_WAGA
                                new_coll_birr = new_coll_dabo * DABO_WAGA
                                new_expected_birr = new_cash_birr + new_coll_birr
                                new_diff = new_actual_birr - new_expected_birr
                                
                                # በስታፍ ሂሳብ መዝገብ ላይ ማስተካከል
                                staff_history[r_id]['morning_load'] = new_morning
                                staff_history[r_id]['returned'] = new_returned
                                staff_history[r_id]['cash_sold_dabo'] = new_cash_dabo
                                staff_history[r_id]['cash_sold_birr'] = new_cash_birr
                                staff_history[r_id]['coll_dabo'] = new_coll_dabo
                                staff_history[r_id]['coll_birr'] = new_coll_birr
                                staff_history[r_id]['new_dube_dabo'] = new_new_dube
                                staff_history[r_id]['expected_birr'] = new_expected_birr
                                staff_history[r_id]['actual_birr'] = new_actual_birr
                                staff_history[r_id]['diff'] = new_diff
                                
                                # Supabase/Database የምትጠቀም ከሆነ እዚህ ጋር save_data() ጥራ
                                if 'save_data' in globals():
                                    save_data()
                                    
                                st.success("✅ ሪፖርቱ በትክክል ተስተካክሏል!")
                                st.rerun()

                    # 3. የመሰረዣ ታብ
                    with tab_del:
                        confirm_delete = st.checkbox("🗑 በእርግጠኝነት ይጥፋ?", key=f"conf_del_{r_id}")
                        if st.button("❌ ሪፖርት አጥፋ", key=f"del_staff_{r_id}", disabled=not confirm_delete):
                            delete_staff_record(r_id)
                            st.warning("⚠️ ሪፖርቱ ተሰርዟል!")
                            st.rerun()
        else: 
            st.info("ምንም የሪፖርት ታሪክ የለም።")
   # --- 🛠 [5] ማስተካከያ (EDIT) ---
    elif choice == "🛠 [5] ማስተካከያ (EDIT)":
        st.header("🛠 ማስተካከያ (EDIT) ማዕከል")
        opt_main = st.radio("ማስተካከል የፈለጉትን ምርጫ ይምረጡ፦", [
            "[1] የደንበኛ የዱቤ ሂሳብ ለመቀየር",
            "[2] የሰራተኛ ያስረከበው ብር (Actual Birr) ለመቀየር",
            "[3] የሰራተኛ የወሰደው ወይም የመለሰው ዳቦ ለመቀየር",
            "[4] የደንበኛ ስም ስህተት ለማስተካከል (Rename Customer)",
            "[5] የሰራተኛ ስም ስህተት ለማስተካከል (Rename Staff)"
        ])
        
        # --- [5] የሰራተኛ ስም ማስተካከያ ---
        if opt_main.startswith("[5]"):
            st.subheader("✏️ የሰራተኛ ስም ማሻሻያ ማዕከል")
            st.caption("⚠️ የሰራተኛ ስም ሲቀይሩ የድሮ የዕለት ሪፖርቶች ታሪክ በሙሉ ወደ አዲሱ ስም ይዛወራል! ስሙ አስቀድሞ ካለ ከነበረው ጋር ይዋሃዳል።")
            
            all_staffs = sorted(list(set([r['staff_name'] for r in staff_history.values() if 'staff_name' in r])))
            
            if not all_staffs:
                st.info("ምንም የተመዘገበ ሰራተኛ የለም።")
            else:
                old_staff_name = st.selectbox("የሚቀየረውን የተሳሳተ ሰራተኛ ስም ይምረጡ፦", [""] + all_staffs, key="rename_old_staff")
                if old_staff_name:
                    new_staff_name = st.text_input("ትክክለኛውን አዲስ የሰራተኛ ስም ያስገቡ፦", value=old_staff_name).strip().capitalize()
                    
                    if st.button("💾 የሰራተኛ ስም አሻሽል", key="execute_staff_rename_btn"):
                        if new_staff_name and new_staff_name != old_staff_name:
                            
                            # በሜሞሪ ውስጥ ያሉትን የድሮ ቁልፎች (IDs) ለይቶ መያዝ
                            old_ids = [r_id for r_id, r in staff_history.items() if r.get('staff_name') == old_staff_name]
                            
                            for old_id in old_ids:
                                r = staff_history.pop(old_id) # ከሜሞሪ ሙሉ በሙሉ መንቀል
                                r['staff_name'] = new_staff_name
                                
                                # አዲስ መለያ ID መፍጠር
                                time_part = old_id.split('_')[0] + "_" + old_id.split('_')[1] if len(old_id.split('_')) >= 2 else datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                                new_id = f"{time_part}_{new_staff_name}"
                                
                                # 1. አዲሱን በፋይል ላይ መጻፍ
                                save_staff_record_single(new_id, r)
                                # 2. የድሮውን ከፋይል ላይ ማጥፋት
                                delete_staff_record(old_id)
                                
                                # 3. አዲሱን በሜሞሪ ውስጥ መመዝገብ
                                staff_history[new_id] = r
                                    
                            st.success(f"✅ የሰራተኛ ስም ከ '{old_staff_name}' ወደ '{new_staff_name}' ተቀይሮ የድሮው ታሪክ ጠፍቷል!")
                            st.rerun()
                        else:
                            st.info("ምንም የተቀየረ ስም የለም ወይም ስሙ ባዶ ነው።")

        # --- [4] የደንበኛ ስም ማስተካከያ ---
        elif opt_main.startswith("[4]"):
            st.subheader("✏️ የደንበኛ ስም ማሻሻያ ማዕከል")
            st.caption("⚠️ ስሙን ሲቀይሩ የድሮው የዱቤ ታሪክ በሙሉ ወደ አዲሱ ስም ይዞራል! የድሮው ስም ሙሉ በሙሉ ከሲስተሙ ይጠፋል።")
            
            all_customers = list(dube_mezgebiya.keys())
            if not all_customers:
                st.info("ምንም የተመዘገበ ደንበኛ የለም።")
            else:
                old_name = st.selectbox("የሚቀየረውን የተሳሳተ ስም ይምረጡ፦", [""] + all_customers, key="rename_old_user_opt4")
                if old_name:
                    new_name = st.text_input("ትክክለኛውን አዲስ ስም ያስገቡ፦", value=old_name).strip()
                    
                    if st.button("💾 የስም ማሻሻያ አውርድ", key="execute_rename_btn_opt4"):
                        if new_name and new_name != old_name:
                            
                            # 1. በዋናው የዱቤ መዝገብ ላይ ስሙን መቀየር/መቀላቀል
                            old_data = dube_mezgebiya.pop(old_name, None) 
                            
                            if old_data:
                                if new_name in dube_mezgebiya:
                                    dube_mezgebiya[new_name]['original'] = dube_mezgebiya[new_name].get('original', 0) + old_data.get('original', 0)
                                    dube_mezgebiya[new_name]['paid'] = dube_mezgebiya[new_name].get('paid', 0) + old_data.get('paid', 0)
                                    dube_mezgebiya[new_name]['yedere_dube'] = dube_mezgebiya[new_name].get('yedere_dube', 0) + old_data.get('yedere_dube', 0)
                                else:
                                    dube_mezgebiya[new_name] = old_data
                                    
                                save_dube_record(dube_mezgebiya) 
                            
                            # 2. በየቀኑ የሰራተኞች ታሪክ (በፋይልም በሜሞሪም) ውስጥ የድሮውን ስም ፈንቅሎ ማጥፋት
                            for r_id, r in staff_history.items():
                                record_changed = False
                                
                                # የከፈለው የድሮ ዱቤ ታሪክ ውስጥ ካለ
                                if "collected_names" in r and old_name in r["collected_names"]:
                                    old_coll = r["collected_names"].pop(old_name, 0) 
                                    r["collected_names"][new_name] = r["collected_names"].get(new_name, 0) + old_coll
                                    record_changed = True
                                    
                                # የዛሬ አዲስ ዱቤ ታሪክ ውስጥ ካለ
                                if "today_dube_details" in r and old_name in r["today_dube_details"]:
                                    old_today = r["today_dube_details"].pop(old_name, 0) 
                                    r["today_dube_details"][new_name] = r["today_dube_details"].get(new_name, 0) + old_today
                                    record_changed = True
                                
                                # ለውጡን በፋይል ላይ መልሶ መጻፍ
                                if record_changed:
                                    save_staff_record_single(r_id, r)
                                
                            st.success(f"✅ የደንበኛ ስም ከ '{old_name}' ወደ '{new_name}' ተቀይሯል! የድሮው ስም ሙሉ በሙሉ ጠፍቷል።")
                            st.rerun()
                        else:
                            st.info("ምንም የተቀየረ ስም የለም ወይም ስሙ ባዶ ነው።")

        # --- [3] የሰራተኛ የወሰደው ወይም የመለሰው ዳቦ ለመቀየር ---
        elif opt_main.startswith("[3]"):
            s_name = st.text_input("የሰራተኛውን ስም ያስገቡ:").strip().capitalize()
            matches = [(r_id, r) for r_id, r in staff_history.items() if r.get('staff_name') == s_name]
            
            if s_name and not matches: st.error("❌ ሰራተኛው አልተገኘም!")
            elif matches:
                sel_day = st.selectbox("ቀን መምረጫ", range(len(matches)), format_func=lambda x: f"ቀን: {matches[x][1]['date']}")
                sel_id, sel_rec = matches[sel_day]
                sub_opt = st.selectbox("ምን መቀየር ይፈልጋሉ?", ["[1] የወሰደው (Morning Load)", "[2] የመለሰው (Returned)"])
                val = st.number_input("አዲሱን ቁጥር ያስገቡ", min_value=0, step=1, value=int(sel_rec["morning_load"] if sub_opt.startswith("[1]") else sel_rec["returned"]))
                
                if st.button("✅ መረጃ አስተካክል"):
                    if sub_opt.startswith("[1]"): sel_rec["morning_load"] = val
                    else: sel_rec["returned"] = val
                    
                    total_out = sel_rec["morning_load"] - sel_rec["returned"]
                    sel_rec["cash_sold_dabo"] = total_out - sel_rec.get("new_dube_dabo", 0)
                    sel_rec["cash_sold_birr"] = sel_rec["cash_sold_dabo"] * DABO_WAGA
                    sel_rec["expected_birr"] = sel_rec["cash_sold_birr"] + sel_rec.get("coll_birr", 0)
                    sel_rec["diff"] = sel_rec["actual_birr"] - sel_rec["expected_birr"]
                    
                    save_staff_record_single(sel_id, sel_rec)
                    st.success("✅ በተሳካ ሁኔታ ተስተካክሏል!")
                    st.rerun()

        # --- [2] የሰራተኛ ያስረከበው ብር (Actual Birr) ለመቀየር ---
        elif opt_main.startswith("[2]"):
            s_name = st.text_input("የሰራተኛውን ስም ያስገቡ:").strip().capitalize()
            matches = [(r_id, r) for r_id, r in staff_history.items() if r.get('staff_name') == s_name]
            
            if s_name and not matches: st.error("❌ ሰራተኛው አልተገኘም!")
            elif matches:
                sel_day = st.selectbox("ቀን መምረጫ", range(len(matches)), format_func=lambda x: f"ቀን: {matches[x][1]['date']}")
                sel_id, sel_rec = matches[sel_day]
                new_actual = st.number_input("ትክክለኛውን ብር ያስገቡ", min_value=0.0, value=float(sel_rec["actual_birr"]))
                
                if st.button("✅ ብር አስተካክል"):
                    sel_rec["actual_birr"] = new_actual
                    sel_rec["diff"] = new_actual - sel_rec.get("expected_birr", 0)
                    save_staff_record_single(sel_id, sel_rec)
                    st.success("✅ ያስረከበው ብር ተስተካክሏል!")
                    st.rerun()

        # --- [1] የደንበኛ የዱቤ ሂሳብ ለመቀየር ---
        elif opt_main.startswith("[1]"):
            name = st.text_input("የደንበኛ ስም ያስገቡ:").strip()
            s_name = st.text_input("የሰራተኛው ስም ያስገቡ:").strip().capitalize()
            matches = [(r_id, r) for r_id, r in staff_history.items() if r.get('staff_name') == s_name]
            
            if s_name and not matches: st.error("❌ ሰራተኛው አልተገኘም!")
            elif matches and name:
                sel_day = st.selectbox("ቀን መምረጫ", range(len(matches)), format_func=lambda x: f"ቀን: {matches[x][1]['date']}")
                sel_id, sel_rec = matches[sel_day]
                
                if "today_dube_details" not in sel_rec: sel_rec["today_dube_details"] = {}
                if "collected_names" not in sel_rec: sel_rec["collected_names"] = {}
                
                opt = st.radio("የሂሳብ አይነት", ["[1] አዲስ የወሰደው ዳቦ", "[2] የከፈለው የድሮ ዱቤ"])
                current_val = sel_rec["today_dube_details"].get(name, 0) if opt.startswith("[1]") else sel_rec["collected_names"].get(name, 0)
                
                st.info(f"አሁን ያለው ዋጋ: {current_val} ዳቦ")
                amt = st.number_input("ትክክለኛውን የዳቦ ብዛት ያስገቡ", min_value=0, step=1, value=int(current_val))
                
                if st.button("⚙️ የደንበኛ ዱቤ አስተካክል"):
                    if opt.startswith("[1]"):
                        old_v = sel_rec["today_dube_details"].get(name, 0)
                        sel_rec["today_dube_details"][name] = amt
                        sel_rec["new_dube_dabo"] = sum(sel_rec["today_dube_details"].values())
                        if name not in dube_mezgebiya: dube_mezgebiya[name] = {'original':0, 'paid':0, 'yedere_dube':0}
                        dube_mezgebiya[name]['yedere_dube'] += (amt - old_v)
                    else:
                        old_v = sel_rec["collected_names"].get(name, 0)
                        sel_rec["collected_names"][name] = amt
                        sel_rec["coll_dabo"] = sum(sel_rec["collected_names"].values())
                        sel_rec["coll_birr"] = sel_rec["coll_dabo"] * DABO_WAGA
                        if name not in dube_mezgebiya: dube_mezgebiya[name] = {'original':0, 'paid':0, 'yedere_dube':0}
                        dube_mezgebiya[name]['yedere_dube'] -= (amt - old_v)
                        
                    total_out = sel_rec["morning_load"] - sel_rec["returned"]
                    sel_rec["cash_sold_dabo"] = total_out - sel_rec.get("new_dube_dabo", 0)
                    sel_rec["cash_sold_birr"] = sel_rec["cash_sold_dabo"] * DABO_WAGA
                    sel_rec["expected_birr"] = sel_rec["cash_sold_birr"] + sel_rec.get("coll_birr", 0)
                    sel_rec["diff"] = sel_rec["actual_birr"] - sel_rec["expected_birr"]
                    
                    save_dube_record(dube_mezgebiya)
                    save_staff_record_single(sel_id, sel_rec)
                    st.success("✅ ሂሳቡ በተሳካ ሁኔታ ተስተካክሏል!")
                    st.rerun()

    # --- 💸 [6] ወጪ መመዝገቢያ ---
    # --- 💸 [6] ወጪ መመዝገቢያ ---
    elif "ወጪ" in choice:
        st.header("💸 የወጪ እና የዱቄት ፍጆታ መቆጣጠሪያ")
        st.write("---")
        
        # ቼክቦክሶቹ ወዲያው እንዲታዩ value=True ተደርገዋል
        col_chk1, col_chk2 = st.columns(2)
        with col_chk1:
            show_normal = st.checkbox("🔹 የመደበኛ ዕቃዎች ወጪ መመዝገቢያ", value=True)
        with col_chk2:
            show_duket = st.checkbox("🌾 የዕለት የዱቄት ፍጆታ መመዝገቢያ", value=True)
            
        st.write("---")
        
        col_left, col_right = st.columns(2)
        
        # --- 🔹 [1] የመደበኛ ወጪዎች ክፍል ---
        with col_left:
            if show_normal:
                st.subheader("📝 መደበኛ ወጪ መመዝገብ")
                with st.form("normal_expense_form", clear_on_submit=True):
                    item = st.text_input("የየዕቃው ስም / የወጣበት ምክንያት").strip()
                    amount = st.number_input("የወጣው ብር መጠን", min_value=0.0, step=10.0)
                    submit_normal = st.form_submit_button("📥 መደበኛ ወጪ መዝግብ")
                    
                    if submit_normal and item and amount > 0:
                        add_expense(item, amount)
                        st.success("✅ መደበኛ ወጪ ተመዝግቧል!")
                        st.rerun()
                
                st.write("---")
                st.subheader("📜 የመደበኛ ወጪዎች ዝርዝር")
                if expenses_data.get("list"):
                    # list(reversed(...)) በማድረግ አዲሱ መዝገብ ከላይ እንዲመጣ ተደርጓል
                    normal_exps = list(reversed([e for e in expenses_data["list"] if "🌾 ዱቄት" not in str(e.get('item',''))]))
                    if normal_exps:
                        df_normal = pd.DataFrame([
                            {
                                "ዕቃ / ምክንያት": e.get('item', ''),
                                "የወጣው ብር": f"{e.get('amount', 0)} ብር",
                                "ቀን": e.get('date', '')
                            } for e in normal_exps
                        ])
                        st.dataframe(df_normal, use_container_width=True, hide_index=True)
                        
                        st.caption("🗑 ወጪ ለመሰረዝ ከታች ይምረጡ፦")
                        exp_to_delete = st.selectbox(
                            "የሚሰረዘውን መዝገብ ይምረጡ",
                            options=normal_exps,
                            format_func=lambda x: f"{x.get('item')} - {x.get('amount')} ብር ({x.get('date')})",
                            key="sb_del_normal"
                        )
                        
                        if st.button("🗑 መዝገቡን አጥፋ", key="btn_del_exp"):
                            delete_expense(exp_to_delete.get('id'))
                            st.warning("⚠️ መዝገቡ ተሰርዟል!")
                            st.rerun()
                    else:
                        st.info("ምንም መደበኛ የወጪ መዝገብ የለም።")
                else: 
                    st.info("ምንም የወጪ መዝገብ የለም።")

        # --- 🌾 [2] የዱቄት ፍጆታ ክፍል ---
        with col_right:
            if show_duket:
                st.subheader("🌾 የዛሬ የዱቄት ፍጆታ መመዝገብ")
                with st.form("duket_consumption_form", clear_on_submit=True):
                    duket_count = st.number_input("የወጣው የዱቄት ብዛት (በጆንያ)", min_value=1, step=1)
                    submit_duket = st.form_submit_button("🌾 የዱቄት ብዛት መዝግብ")
                    
                    if submit_duket and duket_count > 0:
                        duket_label = f"🌾 ዱቄት ({duket_count} ጆንያ) ወጥቷል"
                        add_expense(duket_label, 0.0)
                        st.success(f"✅ የ {duket_count} ጆንያ ዱቄት ፍጆታ ተመዝግቧል!")
                        st.rerun()
                
                st.write("---")
                st.subheader("📜 የወጡ የዱቄት ጆንያዎች ታሪክ")
                if expenses_data.get("list"):
                    # list(reversed(...)) በማድረግ አዲሱ የዱቄት መዝገብ ከላይ እንዲመጣ ተደርጓል
                    duket_exps = list(reversed([e for e in expenses_data["list"] if "🌾 ዱቄት" in str(e.get('item',''))]))
                    if duket_exps:
                        df_duket = pd.DataFrame([
                            {
                                "የዱቄት ፍጆታ ዝርዝር": e.get('item', ''),
                                "ቀን": e.get('date', '')
                            } for e in duket_exps
                        ])
                        st.dataframe(df_duket, use_container_width=True, hide_index=True)
                        
                        st.caption("🗑 የዱቄት መዝገብ ለመሰረዝ ከታች ይምረጡ፦")
                        duket_to_delete = st.selectbox(
                            "የሚሰረዘውን የዱቄት መዝገብ ይምረጡ",
                            options=duket_exps,
                            format_func=lambda x: f"{x.get('item')} ({x.get('date')})",
                            key="sb_del_duket"
                        )
                        
                        if st.button("🗑 የዱቄት መዝገብ አጥፋ", key="btn_del_duket"):
                            delete_expense(duket_to_delete.get('id'))
                            st.warning("⚠️ የዱቄት መዝገብ ተሰርዟል!")
                            st.rerun()
                    else:
                        st.info("ምንም የተመዘገበ የዱቄት ፍጆታ የለም።")
                else:
                    st.info("ምንም የመዝገብ ታሪክ የለም።")
