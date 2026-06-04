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
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- የመግቢያ ማረጋገጫ (Login) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 ቢላል ዳቦ ቤት - መግቢያ ማረጋገጫ")
    username = st.text_input("የተጠቃሚ ስም (Username)", key="username_login")
    password = st.text_input("የሚስጥር ቃል (Password)", type="password", key="password_login")
    
    if st.button("🚪 ግባ (Login)"):
        # እዚህ ጋር ያንተን አዲስ ፓስዋርድ መተካት ትችላለህ
        if username == "bilal" and password == "dabo123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ የተሳሳተ የተጠቃሚ ስም ወይም የሚስጥር ቃል!")
    return False

if check_password():
    st.set_page_config(page_title="ቢላል ዳቦ ቤት", layout="wide")
    st.title("🍞 ቢላል ዳቦ ቤት - የሂሳብ መቆጣጠሪያ")
    
    # የጎን ማውጫ (Sidebar Menu)
    menu = ["📝 መረጃ መመዝገቢያ", "📊 የሪፖርት ማሳያ እና ማጥፊያ"]
    choice = st.sidebar.selectbox("📋 ማውጫ", menu)
    
    df = load_data()
    
    if choice == "📝 መረጃ መመዝገቢያ":
        st.header("🛒 የዕለት ሽያጭ እና ወጪ መመዝገቢያ")
        
        with st.form("input_form", clear_on_submit=True):
            date_input = st.date_input("ቀን", datetime.now())
            record_type = st.selectbox("የመዝገብ ዓይነት", ["የዳቦ ሽያጭ", "ዱቤ", "የዱቤ አሰባሰብ", "ወጪ"])
            amount = st.number_input("መጠኑ (በቁጥር/በኪሎ)", min_value=0, step=1)
            price = st.number_input("የአንዱ ዋጋ (ብሩ)", min_value=0.0, step=0.5)
            
            submitted = st.form_submit_with_button("💾 መዝግብ")
            if submitted:
                # ወጪ ከሆነ መጠኑ 1 ተደርጎ አጠቃላይ ዋጋው ራሱ የዋጋው መጠን ይሆናል
                if record_type == "ወጪ":
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
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=False)
                save_data(df)
                st.success("✅ መረጃው በተሳካ ሁኔታ ተመዝግቧል!")
                st.rerun()

    elif choice == "📊 የሪፖርት ማሳያ እና ማጥፊያ":
        st.header("📋 የሪፖርቶች ማሳያ እና ማጥፊያ ገጽ")
        
        if df.empty:
            st.info("📭 እስካሁን ምንም የተመዘገበ ሪፖርት የለም።")
        else:
            # ሪፖርቱን ለመለየት ማጣሪያ (Filter) ማድረጊያ
            filter_type = st.radio("የሪፖርት ዓይነት ምረጥ፦", ["ሁሉንም አሳይ", "የዳቦ ሽያጭ ብቻ", "ወጪዎች ብቻ", "ዱቤዎች ብቻ"], horizontal=True)
            
            # በተመረጠው መሰረት ዳታውን ለይቶ ማሳየት
            if filter_type == "የዳቦ ሽያጭ ብቻ":
                display_df = df[df["ዓይነት"] == "የዳቦ ሽያጭ"]
            elif filter_type == "ወጪዎች ብቻ":
                display_df = df[df["ዓይነት"] == "ወጪ"]
            elif filter_type == "ዱቤዎች ብቻ":
                display_df = df[df["ዓይነት"] == "ዱቤ"]
            else:
                display_df = df

            if display_df.empty:
                st.info("ℹ️ በዚህ ክፍል ውስጥ ምንም የተመዘገበ መረጃ የለም።")
            else:
                st.write("---")
                # ማጥፊያ በተን ለእያንዳንዱ መስመር መፍጠር
                for index, row in display_df.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            # ወጪ ከሆነ አጻጻፉን ለየት ማድረግ
                            if row['ዓይነት'] == "ወጪ":
                                st.markdown(f"🔴 **የወጪ ሪፖርት** | 📅 **ቀን:** {row['ቀን']}")
                            else:
                                st.markdown(f"🟢 **{row['ዓይነት']}** | 📅 **ቀን:** {row['ቀን']}")
                                
                        with col2:
                            if row['ዓይነት'] == "ወጪ":
                                st.write(f"💰 **የወጣው ገንዘብ:** {row['አጠቃላይ']} ብር")
                            else:
                                st.write(f"🔢 **መጠን:** {row['መጠኑ']} | 💰 **አጠቃላይ:** {row['አጠቃላይ']} ብር")
                                
                        with col3:
                            # የእያንዳንዱ መስመር ማጥፊያ በተን
                            if st.button("🗑️ አጥፋ", key=f"del_{index}"):
                                df = df.drop(index)
                                save_data(df)
                                st.warning("⚠️ ሪፖርቱ በተሳካ ሁኔታ ተሰርዟል!")
                                st.rerun()
                        st.write("---")
