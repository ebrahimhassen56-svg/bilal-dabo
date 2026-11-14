import streamlit as st
import pandas as pd
import json
import datetime
import requests

def get_ethiopian_datetime():
    import datetime
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    
    g_year = now.year
    g_month = now.month
    g_day = now.day
    
    is_leap = 1 if (g_year % 4 == 3) else 0
    
    if g_month > 9 or (g_month == 9 and g_day >= (11 + is_leap)):
        eth_year = g_year - 7
    else:
        eth_year = g_year - 8
        
    if g_month == 1:    
        start_matrix = [4, 8, 5] if (g_year % 4 == 1) else [4, 8, 5]
    elif g_month == 2:  
        start_matrix = [5, 7, 6]
    elif g_month == 3:  
        start_matrix = [6, 9, 7] if ((g_year - 1) % 4 == 3) else [6, 9, 7]
    elif g_month == 4:  
        start_matrix = [7, 8, 8]
    elif g_month == 5:  
        start_matrix = [8, 8, 9]
    elif g_month == 6:  
        start_matrix = [9, 7, 10]
    elif g_month == 7:  
        start_matrix = [10, 7, 11]
    elif g_month == 8:  
        start_matrix = [11, 6, 12]
    elif g_month == 9:  
        start_matrix = [12, 5, 13]
    elif g_month == 10: 
        start_matrix = [1, 11, 2] if (g_year % 4 == 3) else [1, 10, 2]
    elif g_month == 11: 
        start_matrix = [2, 10, 3] if (g_year % 4 == 3) else [2, 9, 3]
    elif g_month == 12: 
        start_matrix = [3, 10, 4] if (g_year % 4 == 3) else [3, 9, 4]

    offset_day = start_matrix[1]
    if g_month == 3 and (g_year % 4 == 0):
        offset_day = 8
        
    if g_day <= offset_day:
        eth_month = start_matrix[0]
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

    if g_month == 9:
        new_year_day = 12 if (g_year % 4 == 3) else 11
        if g_day >= new_year_day:
            eth_month = 1
            eth_day = g_day - new_year_day + 1
        else:
            eth_month = 13
            eth_day = g_day - 5

    time_str = now.strftime("%H:%M")
    return f"{eth_year}-{eth_month:02d}-{eth_day:02d} {time_str}"

DABO_WAGA = 13.50

# --- 🌐 SUPABASE CLOUD DATABASE CONFIG ---
SUPABASE_URL = "https://fcerzqxtdrlfrtqjubvz.supabase.co"
SUPABASE_KEY = "sb_publishable_J3ZTXdoo6e3y7RYd44p6SA_PZmtVYdg"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def load_dube_record():
    url = f"{SUPABASE_URL}/rest/v1/dube_record?select=*"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        dube_data = {}
        if res.status_code == 200:
            for row in res.json():
                dube_data[str(row['customer_name'])] = {
                    'original': int(row.get('original', 0)),
                    'paid': int(row.get('paid', 0)),
                    'yedere_dube': int(row.get('yedere_dube', 0))
                }
        return dube_data
    except:
        return {}

def save_dube_record(dube_data):
    for name, v in dube_data.items():
        try:
            payload = {
                "customer_name": str(name),
                "original": int(v.get('original', 0)),
                "paid": int(v.get('paid', 0)),
                "yedere_dube": int(v.get('yedere_dube', 0))
            }
            url = f"{SUPABASE_URL}/rest/v1/dube_record"
            headers_upsert = HEADERS.copy()
            headers_upsert["Prefer"] = "resolution=merge-duplicates"
            requests.post(url, headers=headers_upsert, json=payload, timeout=8)
        except:
            pass

def load_staff_history():
    url = f"{SUPABASE_URL}/rest/v1/staff_history?select=*"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        history = {}
        if res.status_code == 200:
            for row in res.json():
                c_names = row.get('collected_names')
                if isinstance(c_names, str):
                    try: coll_names = json.loads(c_names)
                    except: coll_names = {}
                elif isinstance(c_names, dict):
                    coll_names = c_names
                else:
                    coll_names = {}

                t_details = row.get('today_dube_details')
                if isinstance(t_details, str):
                    try: today_details = json.loads(t_details)
                    except: today_details = {}
                elif isinstance(t_details, dict):
                    today_details = t_details
                else:
                    today_details = {}
                
                rec_id = str(row.get('record_id'))
                history[rec_id] = {
                    'staff_name': str(row.get('staff_name', '')),
                    'date': str(row.get('date', '')),
                    'morning_load': int(row.get('morning_load') or 0),
                    'returned': int(row.get('returned') or 0),
                    'cash_sold_dabo': int(row.get('cash_sold_dabo') or 0),
                    'cash_sold_birr': float(row.get('cash_sold_birr') or 0.0),
                    'new_dube_dabo': int(row.get('new_dube_dabo') or 0),
                    'today_dube_details': today_details,
                    'coll_dabo': int(row.get('coll_dabo') or 0),
                    'coll_birr': float(row.get('coll_birr') or 0.0),
                    'collected_names': coll_names,
                    'expected_birr': float(row.get('expected_birr') or 0.0),
                    'actual_birr': float(row.get('actual_birr') or 0.0),
                    'diff': float(row.get('diff') or 0.0)
                }
        return history
    except:
        return {}

def save_staff_record_single(r_id, r):
    t_det = r.get('today_dube_details', {})
    c_nam = r.get('collected_names', {})
    
    clean_t_det = {str(k): int(v) for k, v in t_det.items()} if isinstance(t_det, dict) else {}
    clean_c_nam = {str(k): int(v) for k, v in c_nam.items()} if isinstance(c_nam, dict) else {}

    payload = {
        "record_id": str(r_id),
        "staff_name": str(r.get('staff_name', '')),
        "date": str(r.get('date', '')),
        "morning_load": int(r.get('morning_load', 0)),
        "returned": int(r.get('returned', 0)),
        "cash_sold_dabo": int(r.get('cash_sold_dabo', 0)),
        "cash_sold_birr": float(r.get('cash_sold_birr', 0)),
        "new_dube_dabo": int(r.get('new_dube_dabo', 0)),
        "today_dube_details": json.dumps(clean_t_det),
        "coll_dabo": int(r.get('coll_dabo', 0)),
        "coll_birr": float(r.get('coll_birr', 0)),
        "collected_names": json.dumps(clean_c_nam),
        "expected_birr": float(r.get('expected_birr', 0)),
        "actual_birr": float(r.get('actual_birr', 0)),
        "diff": float(r.get('diff', 0))
    }
    url = f"{SUPABASE_URL}/rest/v1/staff_history"
    headers_upsert = HEADERS.copy()
    headers_upsert["Prefer"] = "resolution=merge-duplicates"
    res = requests.post(url, headers=headers_upsert, json=payload, timeout=10)
    return res.status_code in [200, 201]

def delete_staff_record(r_id):
    url = f"{SUPABASE_URL}/rest/v1/staff_history?record_id=eq.{r_id}"
    requests.delete(url, headers=HEADERS, timeout=10)

def load_expenses():
    url = f"{SUPABASE_URL}/rest/v1/expenses?select=*"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return {"list": res.json()}
        return {"list": []}
    except:
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
    requests.post(url, headers=headers_expense, json=payload, timeout=10)

def delete_expense(expense_id):
    url = f"{SUPABASE_URL}/rest/v1/expenses?id=eq.{expense_id}"
    requests.delete(url, headers=HEADERS, timeout=10)

dube_mezgebiya = load_dube_record()
staff_history = load_staff_history()
expenses_data = load_expenses()

def get_daily_id(s_name):
    eth_now = get_ethiopian_datetime().replace(" ", "_").replace(":", "-")
    return f"{eth_now}_{s_name}"

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
        "🚪 ውጣ (Logout)"
    ]
    choice = st.sidebar.selectbox("የአሰሳ ማውጫ", menu)

    if choice == "🚪 ውጣ (Logout)":
        st.session_state.authenticated = False
        st.rerun()

    if choice == "🏠 ዋና ገጽ (Dashboard)":
        try:
            url_exp = f"{SUPABASE_URL}/rest/v1/expenses"
            res_exp = requests.get(url_exp, headers=HEADERS, timeout=10)
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
                    staff_history[rec_id] = {
                        "staff_name": s_name, "date": get_ethiopian_datetime(),
                        "morning_load": 0, "returned": 0, "cash_sold_dabo": 0, "cash_sold_birr": 0,
                        "new_dube_dabo": 0, "today_dube_details": {},
                        "coll_dabo": 0, "coll_birr": 0, "collected_names": {},
                        "expected_birr": 0, "actual_birr": 0, "diff": 0
                    }
                
                staff_history[rec_id]["collected_names"][sel_name] = staff_history[rec_id]["collected_names"].get(sel_name, 0) + amt
                staff_history[rec_id]["coll_dabo"] = sum(staff_history[rec_id]["collected_names"].values())
                staff_history[rec_id]["coll_birr"] = staff_history[rec_id]["coll_dabo"] * DABO_WAGA
                save_dube_record(dube_mezgebiya)
                save_staff_record_single(rec_id, staff_history[rec_id])
                st.success(f"✅ ከ {sel_name} ተቀብሏል!")
                st.rerun()

    elif choice == "📊 [3] ስራ መዝጊያ":
        st.header("📊 የዕለት ስራ መዝጊያ")
        s_name = st.text_input("የሰራተኛው ስም").strip().capitalize()
        
        if s_name:
            col1, col2 = st.columns(2)
            wosede = col1.number_input("📦 ጠዋት የወሰደው ዳቦ", min_value=0, step=1)
            melesse = col2.number_input("📦 ማታ የመለሰው ዳቦ", min_value=0, step=1)
            
            st.write("---")
            st.subheader("➕ አዲስ ዱቤ የወሰዱ")
            if "closing_new_dube" not in st.session_state: 
                st.session_state.closing_new_dube = [{"name": "", "amt": 0}]
            
            recorded_today_dube = {}
            new_dube_total = 0
            for idx, item in enumerate(st.session_state.closing_new_dube):
                c1, c2 = st.columns(2)
                d_n = c1.text_input(f"የደንበኛ ስም {idx+1}", value=item["name"], key=f"cls_new_name_{idx}").strip()
                d_a = c2.number_input(f"ዳቦ ብዛት {idx+1}", value=item["amt"], min_value=0, step=1, key=f"cls_new_amt_{idx}")
                if d_n and d_a > 0:
                    recorded_today_dube[d_n] = int(d_a)
                    new_dube_total += int(d_a)
                    
            if st.button("➕ ሌላ አዲስ ዱቤ ጨምር"):
                st.session_state.closing_new_dube.append({"name": "", "amt": 0})
                st.rerun()
                
            st.write("---")
            st.subheader("💰 የድሮ ዱቤ መቀበያ (የተሰበሰበ)")
            custs = [n for n, d in dube_mezgebiya.items() if (d.get('yedere_dube',0) + d.get('original',0) - d.get('paid',0)) > 0]
            
            collected_names = {}
            for name in custs:
                d = dube_mezgebiya[name]
                qeri_h = max(0, d.get('yedere_dube', 0) + d.get('original', 0) - d.get('paid', 0))
                if qeri_h > 0:
                    ans = st.number_input(f"👉 {name} ({qeri_h} አለበት)፦", min_value=0, max_value=int(qeri_h), step=1, key=f"cls_coll_{name}")
                    if ans > 0: 
                        collected_names[name] = int(ans)

            st.write("---")
            st.subheader("💸 የዕለት ወጪ መመዝገቢያ (ካለ)")
            exp_item = st.text_input("የወጪ ምክንያት (ምሳሌ፡ የላስቲክ...)").strip()
            exp_amount = st.number_input("የወጪ ብር መጠን", min_value=0.0, step=1.0)

            st.write("---")
            actual_birr = st.number_input("💰 ሰራተኛው ያስረከበው ብር (Actual Birr)", min_value=0.0)
            
            if st.button("💾 የዕለት ሒሳብ ዝጋ"):
                rec_id = get_daily_id(s_name)
                
                # 1. አዲስ ዱቤዎችን በ dube_mezgebiya ላይ መመዝገብ
                for d_n, d_a in recorded_today_dube.items():
                    if d_n in dube_mezgebiya: 
                        dube_mezgebiya[d_n]['original'] += d_a
                    else: 
                        dube_mezgebiya[d_n] = {'original': d_a, 'paid': 0, 'yedere_dube': 0}
                    
                # 2. የተሰበሰቡ ዱቤዎችን በ dube_mezgebiya ላይ መመዝገብ
                for name, v in collected_names.items():
                    if name in dube_mezgebiya:
                        dube_mezgebiya[name]['paid'] += v
                    
                coll_dabo_sum = sum(collected_names.values())
                coll_birr_sum = coll_dabo_sum * DABO_WAGA
                
                total_out = wosede - melesse
                cash_sold_dabo = max(0, total_out - new_dube_total)
                cash_sold_birr = cash_sold_dabo * DABO_WAGA
                
                if exp_item and exp_amount > 0:
                    add_expense(f"{s_name}: {exp_item}", exp_amount)
                    expected = cash_sold_birr + coll_birr_sum - exp_amount
                else:
                    expected = cash_sold_birr + coll_birr_sum
                
                # 3. የሰራተኛውን ሪፖርት ማዘጋጀት
                new_record = {
                    "staff_name": s_name, 
                    "date": get_ethiopian_datetime(),
                    "morning_load": int(wosede), 
                    "returned": int(melesse), 
                    "cash_sold_dabo": int(cash_sold_dabo), 
                    "cash_sold_birr": float(cash_sold_birr), 
                    "new_dube_dabo": int(new_dube_total), 
                    "today_dube_details": recorded_today_dube, 
                    "coll_dabo": int(coll_dabo_sum), 
                    "coll_birr": float(coll_birr_sum),
                    "collected_names": collected_names,
                    "expected_birr": float(expected), 
                    "actual_birr": float(actual_birr), 
                    "diff": float(actual_birr - expected)
                }
                
                # መጀመሪያ ሪፖርቱን ማስቀመጥ (ቅድሚያ ለሪፖርት ምዝገባ)
                staff_history[rec_id] = new_record
                saved_successfully = save_staff_record_single(rec_id, staff_history[rec_id])
                
                # 4. የደንበኞችን የዕለት ዱቤ ወደ ያደረ ዱቤ ማዞር እና ዳታቤዝ ላይ መመዝገብ
                for name, data in dube_mezgebiya.items():
                    data['yedere_dube'] = max(0, data.get('yedere_dube', 0) + data.get('original', 0) - data.get('paid', 0))
                    data['original'] = 0
                    data['paid'] = 0
                
                save_dube_record(dube_mezgebiya)
                
                st.session_state.closing_new_dube = [{"name": "", "amt": 0}]
                if saved_successfully:
                    st.success(f"✅ {s_name} የዛሬ ሂሳብ (የተሰበሰበውን ዱቤ ጨምሮ) በተሳካ ሁኔታ ተመዝግቧል!")
                else:
                    st.warning("⚠️ ሪፖርቱ በከፊል ተመዝግቧል፣ እባክዎ በሪፖርት ገጽ ያረጋግጡ!")
                st.rerun()

    elif choice == "📜 [4] ሪፖርት":
        st.header("📊 የክትትልና የሪፖርት ማዕከል")
        st.write("---")
        
        show_summary = st.checkbox("📊 የአጠቃላይ ቢዝነስ ማጠቃለያ ለማየት እዚህ ጋ ያብሩ", value=False)
        
        if show_summary:
            st.subheader("📅 የአጠቃላይ የቢዝነሱ የዘመን ክልል ማጠቃለያ (በኢትዮጵያ አቆጣጠር)")
            
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

            s_str = f"{s_year:04d}-{s_month:02d}-{s_day:02d}"
            e_str = f"{e_year:04d}-{e_month:02d}-{e_day:02d}"

            if s_str <= e_str:
                st.success(f"📅 የተመረጠው ክልል፦ ከ **{s_str}** እስከ **{e_str}**")
                daily_summary = {}

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
                        d
