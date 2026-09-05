import streamlit as st
import pandas as pd
from supabase import create_client
from config import *

st.set_page_config(page_title=STORE_NAME, layout="wide")

# CONNECT SUPABASE
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SESSION STATE
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

mode = st.sidebar.selectbox("Mode", ["Customer Store", "Admin"])

# ========== ADMIN PAGE ==========
if mode == "Admin":
    st.title("🔒 Admin Panel")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Welcome Owner!")
        
        with st.form("add_product"):
            name = st.text_input("Product Name")
            price = st.number_input("Price ₦", 0)
            img = st.text_input("Image URL")
            description = st.text_area("Description")
            if st.form_submit_button("Add Product"):
                supabase.table("products").insert({
                    "name": name, 
                    "price": price, 
                    "img": img, 
                    "description": description
                }).execute()
                st.success("Product Added!")
                st.rerun()
        
        st.subheader("All Products")
        data = supabase.table("products").select("*").execute()
        if data.data:
            st.dataframe(pd.DataFrame(data.data))
        else:
            st.info("No products yet. Add one above.")
    else:
        st.warning("Enter password")

# ========== CUSTOMER STORE ==========
else:
    st.title(f"🏪 {STORE_NAME}")
    
    # LOGIN
    if not st.session_state.logged_in:
        email = st.text_input("Enter Email to Continue")
        if st.button("Login"):
            if email:
                st.session_state.user_email = email
                st.session_state.logged_in = True
                st.rerun()
    
    # SHOW PRODUCTS
    else:
        st.write(f"Hi {st.session_state.user_email} 👋")
        if st.button("Logout"): 
            st.session_state.clear()
            st.rerun()

        st.header("Our Products")
        data = supabase.table("products").select("*").execute()
        
        if data.data:
            cols = st.columns(3)
            for i, p in enumerate(data.data):
                with cols[i % 3]:
                    if p["img"]: 
                        st.image(p["img"])
                    st.subheader(p["name"])
                    st.write(f"₦{int(p['price']):,}")
                    st.write(p["description"]) # CHANGED HERE
                    st.button("Buy Now", key=p["id"])
        else:
            st.info("No products yet. Check back soon!")