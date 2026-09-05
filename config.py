import streamlit as st

STORE_NAME = "Ebuka Store"
ADMIN_PASSWORD = "admin123"

# Read from Streamlit Secrets instead of hardcoded
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]