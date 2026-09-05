import streamlit as st
import pandas as pd, gspread, urllib.parse
from oauth2client.service_account import ServiceAccountCredentials
from config import *

st.set_page_config(page_title=STORE_NAME, layout="wide")

# CONNECT TO GOOGLE SHEET
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp"], scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
except:
    st.error("Google Sheet not connected. Check st.secrets")
    st.stop()

# SESSION STATE
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""

# SIDEBAR
mode = st.sidebar.selectbox("Mode", ["Customer Store", "Admin - Add Products"])

# ========== ADMIN PAGE ==========
if mode == "Admin - Add Products":
    st.title("🔒 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Welcome Owner!")
        
        with st.form("add_product"):
            name = st.text_input("Product Name")
            price = st.number_input("Price ₦", min_value=0)
            img = st.text_input("Image URL")
            desc = st.text_area("Description")
            
            if st.form_submit_button("Add Product"):
                sheet.append_row([name, price, img, desc])
                st.success(f"{name} added!")
                st.rerun()
        
        df = pd.DataFrame(sheet.get_all_records())
        st.dataframe(df)
    else:
        st.warning("Enter password")

# ========== CUSTOMER STORE ==========
else:
    # CHECK IF COMING BACK FROM LOGIN WITH URL ?email=xxx
    params = st.query_params
    if "email" in params and not st.session_state.logged_in:
        st.session_state.user_email = params["email"]
        st.session_state.logged_in = True

    df = pd.DataFrame(sheet.get_all_records())
    st.title(f"🏪 {STORE_NAME}")
    
    # LOGIN
    if not st.session_state.logged_in:
        email = st.text_input("Email to Login")
        if st.button("Login"):
            st.session_state.user_email = email
            st.session_state.logged_in = True
            st.query_params["email"] = email # Remember in URL
            st.rerun()
    
    # SHOW PRODUCTS
    else:
        st.write(f"Hi {st.session_state.user_email} 👋 | ")
        if st.button("Logout"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.image(row["img"], width=200)
                st.subheader(row["name"])
                st.write(f"₦{int(row['price']):,}")
                st.write(row["desc"])
                buy_link = f"https://your-streamlit-url.streamlit.app/?email={st.session_state.user_email}&product={row['name']}&price={row['price']}"
                st.link_button("Buy Now", buy_link)