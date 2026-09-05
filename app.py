import streamlit as st
import pandas as pd, gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_cookies_manager import EncryptedCookieManager
from config import *

st.set_page_config(page_title=STORE_NAME, layout="wide")

# CONNECT TO GOOGLE SHEET
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp"], scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

cookies = EncryptedCookieManager(prefix="sell_site_", password="secret123")
if not cookies.ready(): st.stop()

# SIDEBAR: CHOOSE MODE
mode = st.sidebar.selectbox("Mode", ["Customer Store", "Admin - Add Products"])

# ========== ADMIN PAGE ==========
if mode == "Admin - Add Products":
    st.title("🔒 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Welcome Owner!")
        
        with st.form("add_product"):
            st.subheader("Add New Product")
            name = st.text_input("Product Name")
            price = st.number_input("Price ₦", min_value=0)
            img = st.text_input("Image URL - Upload to GitHub first")
            desc = st.text_area("Description")
            
            if st.form_submit_button("Add Product"):
                sheet.append_row([name, price, img, desc])
                st.success(f"{name} added! Refresh store to see it.")
        
        st.subheader("Current Products")
        df = pd.DataFrame(sheet.get_all_records())
        st.dataframe(df)
        
        if st.button("Logout Admin"):
            st.session_state.clear()
    else:
        st.warning("Wrong password")

# ========== CUSTOMER STORE ==========
else:
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        if cookies.get("user_email"):
            st.session_state.user_email = cookies.get("user_email")
            st.session_state.logged_in = True

    # LOAD PRODUCTS FROM GOOGLE SHEET
    df = pd.DataFrame(sheet.get_all_records())
    
    st.title(f"🏪 {STORE_NAME}")
    
    # LOGIN
    if not st.session_state.logged_in:
        email = st.text_input("Email to Login")
        if st.button("Login"):
            st.session_state.user_email = email
            st.session_state.logged_in = True
            cookies["user_email"] = email
            cookies.save()
            st.rerun()
    
    # SHOW PRODUCTS
    else:
        st.write(f"Hi {st.session_state.user_email}")
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.image(row["img"], width=200)
                st.subheader(row["name"])
                st.write(f"₦{int(row['price']):,}")
                st.write(row["desc"])
                link = f"https://your-streamlit-url.streamlit.app/?product={row['name']}&price={row['price']}"
                st.link_button("Buy Now", link)