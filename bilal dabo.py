import streamlit as st
import pandas as pd
import os
from datetime import datetime

# የውሂብ ፋይል ስም
DATA_FILE = "bilal_dabo_records.csv"

# ፋይሉ መኖሩን ማረጋገጥ፣ ከሌለ መፍጠር
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ቀን", "ዓይነት", "መጠኑ", "ዋጋ", "አጠቃላይ", "ተመዝጋቢ"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["ቀን", "ዓይነት", "መጠኑ", "ዋጋ", "አጠቃላይ", "ተመዝጋቢ"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- የመግቢያ ማረጋገጫ (Login) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center;'>🔒 ቢላል ዳቦ ቤት - መግቢያ ማረጋገጫ</h2>", unsafe_allow_html=True)
    
    # መግቢያ ሳጥን ማዕከል እንዲሆን
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("የተጠቃሚ ስም (Username)", key="username_login")
        password = st.text_input("የሚስጥር ቃል (Password)", type="password", key="password_login")
        
        if st.button("🚪 ግባ (Login)", use_container_width=True):
            # ⚠️ ማሳሰቢያ፦ እዚህ ጋር "dabo123" የሚለውን ወደ አዲሱ ፓስዋርድህ መቀየር ትችላለህ
            if username == "bilal" and password == "dabo123":
                st.session_state.authenticated = True
                st.success("✅ በትክክል ገብተዋል!")
                st.rerun()
            else:
                st.error("❌ የተሳሳተ የተጠቃሚ ስም ወይም የሚስጥር ቃል!")
    return False

# የይለፍ ቃል ትክክል ከሆነ አፑ ይከፈታል
if check_password():
    st.set_page_config(page_title="ቢላል ዳቦ ቤት", layout="wide")
    
    # የጎን ማውጫ (Sidebar Menu)
    st.sidebar.markdown("### 🏢 ቢላል ዳቦ ቤት")
    menu = ["📝 መረጃ መመዝገቢያ", "📊 የሪፖርት ማሳያ እና ማጥፊያ", "📈 የሂሳብ ማጠቃለያ"]
    choice = st.sidebar.selectbox("📋 ዋና ማውጫ", menu)
    
    df = load_data()
    
    # --- 1. መረጃ መመዝገቢያ ገፅ ---
    if choice == "📝 መረጃ መመዝገቢያ":
        st.header("🛒 የዕለት ሽያጭ፣ ዱቤ እና ወጪ መመዝገቢያ")
        st.write("እባክዎ መረጃዎችን በጥንቃቄ ያስግቡ።")
        
        with st.form("input_form", clear_on_submit=True):
            date_input = st.date_input("ቀን", datetime.now())
            record_type = st.selectbox("የመዝገብ ዓይነት", ["የዳቦ ሽያጭ", "ዱቤ", "የዱቤ አሰባሰብ", "ወጪ"])
            
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("መጠኑ (በቁጥር/በኪሎ)", min_value=0, step=1, value=0)
            with col2:
                price = st.number_input("የአንዱ ዋጋ ወይም አጠቃላይ ዋጋ (በብር)", min_value=0.0, step=0.5, value=0.0)
            
            submitted = st.form_submit_with_button("💾 መረጃውን መዝግብ")
            if submitted:
                if record_type == "ወጪ":
                    total = price
                    amount = 1  # ለወጪ መጠን ስለማያስፈልግ በ1 ይባዛል
                elif record_type == "የዱቤ አሰባሰብ":
                    total = price
                    amount = 1
                else:
                    total = amount * price

                new_row = {
                    "ቀን": str(date_input),
                    "ዓይነት": record_type,
                    "መጠኑ": amount,
                    "ዋጋ": price,
                    "አጠቃላይ": total,
                    "ተመዝጋቢ": "bilal"
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"✅ የ [{record_type}] መረጃ በ {total} ብር በተሳካ ሁኔታ ተመዝግቧል!")
                st.rerun()

    # --- 2. የሪፖርት ማሳያ እና ማጥፊያ ገፅ ---
    elif choice == "📊 የሪፖርት ማሳያ እና ማጥፊያ":
        st.header("📋 የተመዘገቡ ሙሉ ሪፖርቶች ማስተካከያ")
        
        if df.empty:
            st.info("📭 እስካሁን ምንም የተመዘገበ መረጃ የለም።")
        else:
            # የማጣሪያ ራዲዮ በተን
            filter_type = st.radio(
                "የሪፖርት ዓይነት ይምረጡ፦", 
                ["ሁሉንም አሳይ", "የዳቦ ሽያጭ ብቻ", "ወጪዎች ብቻ", "ዱቤዎች ብቻ", "የዱቤ አሰባሰብ ብቻ"], 
                horizontal=True
            )
            
            # ዳታውን ማጣራት
            if filter_type == "የዳቦ ሽያጭ ብቻ":
                display_df = df[df["ዓይነት"] == "የዳቦ ሽያጭ"]
            elif filter_type == "ወጪዎች ብቻ":
                display_df = df[df["ዓይነት"] == "ወጪ"]
            elif filter_type == "ዱቤዎች ብቻ":
                display_df = df[df["ዓይነት"] == "ዱቤ"]
            elif filter_type == "የዱቤ አሰባሰብ ብቻ":
                display_df = df[df["ዓይነት"] == "የዱቤ አሰባሰብ"]
            else:
                display_df = df

            if display_df.empty:
                st.info("ℹ️ በዚህ ክፍል ውስጥ ምንም የተመዘገበ መረጃ የለም።")
            else:
                st.write("---")
                # እያንዳንዱን መዝገብ በመስመር ማሳየትና ማጥፊያ በተን መፍጠር
                for index, row in display_df.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            if row['ዓይነት'] == "ወጪ":
                                st.markdown(f"🔴 **የወጪ ሪፖርት** | 📅 **ቀን:** {row['ቀን']}")
                            elif row['ዓይነት'] == "ዱቤ":
                                st.markdown(f"🔵 **የዱቤ መዝገብ** | 📅 **ቀን:** {row['ቀን']}")
                            elif row['ዓይነት'] == "የዱቤ አሰባሰብ":
                                st.markdown(f"🟡 **የዱቤ አሰባሰብ** | 📅 **ቀን:** {row['ቀን']}")
                            else:
                                st.markdown(f"🟢 **{row['ዓይነት']}** | 📅 **ቀን:** {row['ቀን']}")
                                
                        with col2:
                            if row['ዓይነት'] in ["ወጪ", "የዱቤ አሰባሰብ"]:
                                st.write(f"💰 **ገንዘብ:** {row['አጠቃላይ']} ብር")
                            else:
                                st.write(f"🔢 **መጠን:** {row['መጠኑ']} | 💰 **አጠቃላይ:** {row['አጠቃላይ']} ብር")
                                
                        with col3:
                            # 🗑️ ማጥፊያ በተን ለእያንዳንዱ መስመር
                            if st.button("🗑️ አጥፋ", key=f"del_{index}"):
                                df = df.drop(index)
                                # የጠፋውን ዳታ ማስቀመጥ እና ገጹን ማደስ
                                df = df.reset_index(drop=True)
                                save_data(df)
                                st.warning("⚠️ መረጃው ሙሉ በሙሉ ተሰርዟል!")
                                st.rerun()
                        st.write("---")

    # --- 3. የሂሳብ ማጠቃለያ (Dashboard) ገፅ ---
    elif choice == "📈 የሂሳብ ማጠቃለያ":
        st.header("📊 የቢላል ዳቦ ቤት አጠቃላይ የሂሳብ ሁኔታ")
        
        if df.empty:
            st.info("📭 የሂሳብ ማጠቃለያ ለመስራት መጀመሪያ መረጃ ይመዝግቡ።")
        else:
            # የሂሳብ ስሌቶች
            total_sales = df[df["ዓይነት"] == "የዳቦ ሽያጭ"]["አጠቃላይ"].sum()
            total_expenses = df[df["ዓይነት"] == "ወጪ"]["አጠቃላይ"].sum()
            total_dube = df[df["ዓይነት"] == "ዱቤ"]["አጠቃላይ"].sum()
            total_collected = df[df["ዓይነት"] == "የዱቤ አሰባሰብ"]["አጠቃላይ"].sum()
            
            net_profit = total_sales - total_expenses
            remaining_dube = total_dube - total_collected
            
            # ውጤቱን በሳጥን ማሳያ
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🟢 ጠቅላላ የዳቦ ሽያጭ", value=f"{total_sales:,.2f} ብር")
                st.metric(label="🟡 የተሰበሰበ ዱቤ", value=f"{total_collected:,.2f} ብር")
            with col2:
                st.metric(label="🔴 ጠቅላላ ወጪ", value=f"{total_expenses:,.2f} ብር")
                st.metric(label="🔵 ያልተሰበሰበ ጠቅላላ ዱቤ", value=f"{total_dube:,.2f} ብር")
            with col3:
                st.metric(label="💵 የተጣራ ትርፍ (ሽያጭ - ወጪ)", value=f"{net_profit:,.2f} ብር")
                st.metric(label="⏳ ከደንበኞች የሚጠበቅ ቀሪ ዱቤ", value=f"{remaining_dube:,.2f} ብር", delta=f"-{total_collected:,.2f} የተሰበሰበ")
            
            st.write("---")
            st.subheader("📋 የቅርብ ጊዜ እንቅስቃሴዎች")
            st.dataframe(df.tail(10), use_container_width=True)
