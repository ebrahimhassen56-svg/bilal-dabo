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
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
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
                    staff_history[rec_id] = {"staff_name": s_name, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "coll_dabo": 0, "coll_birr": 0, "collected_names": {}, "today_dube_details": {}}
                    
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
    # --- 📜 [4] ሪፖርት ---
    elif choice == "📜 [4] ሪፖርት":
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
        st.header("📜 የሰራተኞች የዕለት ሪፖርት ዝርዝር")
        all_s = sorted(list(set([r['staff_name'] for r in staff_history.values() if 'staff_name' in r])))
        
        if all_s:
            sel_staff = st.selectbox("ሰራተኛ ይምረጡ", all_s)
            staff_recs = sorted([(r_id, r) for r_id, r in staff_history.items() if r.get('staff_name') == sel_staff], key=lambda x: x[1].get('date', ''), reverse=True)
            
            rep_rows = []
            for r_id, r in staff_recs:
                cash_birr = r.get('cash_sold_birr', 0)
                coll_dabo = r.get('coll_dabo', 0)  # 👈 የተሰበሰበው ዳቦ መጠን
                coll_birr = r.get('coll_birr', 0)  # 👈 የተሰበሰበው ብር መጠን
                
                expected_birr = r.get('expected_birr', 0)
                calculated_expense = (cash_birr + coll_birr) - expected_birr
                if calculated_expense < 0: calculated_expense = 0
                
                rep_rows.append({
                    "ቀንና ሰዓት": r.get('date',''), 
                    "ወጣ": r.get('morning_load',0), 
                    "ገባ": r.get('returned',0),
                    "ካሽ(ዳ)": r.get('cash_sold_dabo',0), 
                    "ካሽ(ብር)": cash_birr,
                    "ዱቤ(ዳ)": coll_dabo,  # 👈 አዲስ የተጨመረ አምድ (የተሰበሰበ ዳቦ)
                    "ዱቤ(ብር)": coll_birr, 
                    "አዲስ ዱ": r.get('new_dube_dabo',0),
                    "የዕለት ወጪ": calculated_expense,
                    "የተጠበቀ": expected_birr, 
                    "የመጣ": r.get('actual_birr',0), 
                    "+/-": r.get('diff',0)
                })
            
            df_rep = pd.DataFrame(rep_rows)
            st.dataframe(df_rep, use_container_width=True)
            
            st.subheader("📅 የዕለት ዝርዝር መረጃ")
            for r_id, rec in staff_recs:
                expander_title = f"📅 ሪፖርት ቀን፦ {rec.get('date','')}"
                with st.expander(expander_title):
                    col_info, col_del = st.columns([4, 1.5])
                    with col_info:
                        if rec.get("collected_names"):
                            st.write("💵 የድሮ ዱቤ የተቀበለው፦")
                            for c_n, c_a in rec["collected_names"].items():
                                st.write(f"👉 {c_n}: {c_a} ዳቦ")
                        if rec.get("today_dube_details"):
                            st.write("📦 አዲስ ዱቤ የወሰዱ፦")
                            for n_n, n_a in rec["today_dube_details"].items():
                                st.write(f"🔸 {n_n}: {n_a} ዳቦ")
                    with col_del:
                        if st.button("🗑 ይህንን ሪፖርት አጥፋ", key=f"del_staff_{r_id}"):
                            delete_staff_record(r_id)
                            st.warning("⚠️ ሪፖርቱ ተሰርዟል!")
                            st.rerun()
        else: st.info("ምንም የሪፖርት ታሪክ የለም።")

    # --- 🛠 [5] ማስተካከያ (EDIT) ---
    elif choice == "🛠 [5] ማስተካከያ (EDIT)":
        st.header("🛠 ማስተካከያ (EDIT) ማዕከል")
        opt_main = st.radio("ማስተካከል የፈለጉትን ምርጫ ይምረጡ፦", [
            "[1] የደንበኛ የዱቤ ሂሳብ ለመቀየር",
            "[2] የሰራተኛ ያስረከበው ብር (Actual Birr) ለመቀየር",
            "[3] የሰራተኛ የወሰደው ወይም የመለሰው ዳቦ ለመቀየር"
        ])
        
        if opt_main.startswith("[3]"):
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
    elif choice == "💸 [6] ወጪ መመዝገቢያ":
        st.header("💸 የወጪ እና የዱቄት ፍጆታ መቆጣጠሪያ")
        st.write("---")
        
        # ሰራተኛው መጀመሪያ የሚመርጥባቸው ሁለት ቼክ ቦክሶች
        st.subheader("🛠 ምን መመዝገብ ይፈልጋሉ? (ከታች ይምረጡ)")
        col_chk1, col_chk2 = st.columns(2)
        with col_chk1:
            show_normal = st.checkbox("🔹 የመደበኛ ዕቃዎች ወጪ መመዝገቢያ", value=False)
        with col_chk2:
            show_duket = st.checkbox("🌾 የዕለት የዱቄት ፍጆታ መመዝገቢያ", value=False)
            
        st.write("---")
        
        # ገጹን ለሁለት ከፍለን ጎን ለጎን እናሳየዋለን
        col_left, col_right = st.columns(2)
        
        # --- 🔹 [1] የመደበኛ ወጪዎች ክፍል (ብር ያለበት) ---
        with col_left:
            if show_normal:
                st.subheader("📝 መደበኛ ወጪ መመዝገብ")
                with st.form("normal_expense_form", clear_on_submit=True):
                    item = st.text_input("የየዕቃው ስም / የወጣበት ምክንያት (ምሳሌ፡ የላስቲክ፣ መብራት...)").strip()
                    amount = st.number_input("የወጣው ብር መጠን", min_value=0.0, step=10.0)
                    submit_normal = st.form_submit_button("📥 መደበኛ ወጪ መዝግብ")
                    
                    if submit_normal and item and amount > 0:
                        add_expense(item, amount)
                        st.success("✅ መደበኛ ወጪ ተመዝግቧል!")
                        st.rerun()
                
                st.write("---")
                st.subheader("📜 የመደበኛ ወጪዎች ዝርዝር")
                if expenses_data.get("list"):
                    normal_exps = [e for e in expenses_data["list"] if "🌾 ዱቄት" not in str(e.get('item',''))]
                    if normal_exps:
                        for exp in normal_exps:
                            c_text, c_btn = st.columns([3, 1])
                            with c_text: 
                                st.write(f"🏷 {exp.get('item','')} | 💰 **{exp.get('amount',0)} ብር**")
                                st.caption(f"📅 {exp.get('date','')}")
                            with c_btn:
                                if st.button("🗑 አጥፋ", key=f"del_exp_{exp.get('id')}"):
                                    delete_expense(exp.get('id'))
                                    st.warning("⚠️ መዝገቡ ተሰርዟል!")
                                    st.rerun()
                            st.write("---")
                    else:
                        st.info("ምንም መደበኛ የወጪ መዝገብ የለም።")
                else: 
                    st.info("ምንም የወጪ መዝገብ የለም።")

        # --- 🌾 [2] የዱቄት ፍጆታ ክፍል (የጆንያ ብዛት ብቻ) ---
        with col_right:
            if show_duket:
                st.subheader("🌾 የዛሬ የዱቄት ፍጆታ መመዝገብ")
                with st.form("duket_consumption_form", clear_on_submit=True):
                    # የብር ዋጋው ሙሉ በሙሉ ጠፍቶ የጆንያ ብዛት ብቻ ነው የሚጠይቀው
                    duket_count = st.number_input("የወጣው የዱቄት ብዛት (በጆንያ)", min_value=1, step=1)
                    submit_duket = st.form_submit_button("🌾 የዱቄት ብዛት መዝግብ")
                    
                    if submit_duket and duket_count > 0:
                        duket_label = f"🌾 ዱቄት ({duket_count} ጆንያ) ወጥቷል"
                        # በብር ቦታ ላይ 0.0 ቁጭ ይላል (ከገንዘብ ሂሳብ ጋር እንዳይደባለቅ)
                        add_expense(duket_label, 0.0)
                        st.success(f"✅ የ {duket_count} ጆንያ ዱቄት ፍጆታ በተሳካ ሁኔታ ተመዝግቧል!")
                        st.rerun()
                
                st.write("---")
                st.subheader("📜 የወጡ የዱቄት ጆንያዎች ታሪክ")
                if expenses_data.get("list"):
                    duket_exps = [e for e in expenses_data["list"] if "🌾 ዱቄት" in str(e.get('item',''))]
                    if duket_exps:
                        for exp in duket_exps:
                            c_text, c_btn = st.columns([3, 1])
                            with c_text: 
                                # እዚህ ጋር የጆንያውን ብዛት እና ቀኑን ብቻ ያሳያል
                                st.write(f"📦 **{exp.get('item','')}**")
                                st.caption(f"📅 {exp.get('date','')}")
                            with c_btn:
                                if st.button("🗑 አጥፋ", key=f"del_duket_{exp.get('id')}"):
                                    delete_expense(exp.get('id'))
                                    st.warning("⚠️ የዱቄት መዝገብ ተሰርዟል!")
                                    st.rerun()
                            st.write("---")
                    else:
                        st.info("ምንም የተመዘገበ የዱቄት ፍጆታ የለም።")
                else:
                    st.info("ምንም የመዝገብ ታሪክ የለም።")
