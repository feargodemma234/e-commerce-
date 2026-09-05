import streamlit as st
from supabase import create_client
from config import STORE_NAME, ADMIN_PASSWORD, SUPABASE_URL, SUPABASE_KEY

st.set_page_config(page_title=STORE_NAME, page_icon="🛍️", layout="wide")

# Connect to Supabase
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# Get products
@st.cache_data
def get_products():
    res = supabase.table("products").select("*").order("id", desc=True).execute()
    return res.data

# Delete cache when product added
def clear_cache():
    st.cache_data.clear()

# Sidebar Navigation
st.sidebar.title(f"🛍️ {STORE_NAME}")
page = st.sidebar.radio("Navigation", ["Shop", "Admin"])

# ========== SHOP PAGE ==========
if page == "Shop":
    st.title(f"Welcome to {STORE_NAME}")
    st.write("Find the best products here")
    
    products = get_products()
    
    if not products:
        st.info("No products available yet. Check back soon!")
    else:
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                with st.container(border=True):
                    if product.get("image_url"):
                        st.image(product["image_url"], use_container_width=True)
                    st.subheader(product["name"])
                    st.write(f"**Price: ₦{product['price']}**")
                    st.write(product["description"])
                    st.button("Add to Cart", key=f"btn_{product['id']}", disabled=True)

# ========== ADMIN PAGE ==========
elif page == "Admin":
    st.title("🔒 Admin Panel")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Logged in successfully!")
        
        tab1, tab2 = st.tabs(["Add Product", "View Products"])
        
        # ADD PRODUCT TAB
        with tab1:
            st.subheader("Add New Product")
            with st.form("add_product_form", clear_on_submit=True):
                name = st.text_input("Product Name")
                price = st.number_input("Price (₦)", min_value=0.0, step=100.0)
                description = st.text_area("Product Description")
                image_url = st.text_input("Image URL")
                
                submitted = st.form_submit_button("Add Product")
                
                if submitted:
                    if name and price:
                        supabase.table("products").insert({
                            "name": name,
                            "price": price,
                            "description": description,
                            "image_url": image_url
                        }).execute()
                        clear_cache()
                        st.success(f"Product '{name}' added successfully!")
                    else:
                        st.error("Please fill Name and Price")
        
        # VIEW PRODUCTS TAB
        with tab2:
            st.subheader("All Products")
            products = get_products()
            if products:
                st.dataframe(products, use_container_width=True)
            else:
                st.info("No products yet")
                
    elif password:
        st.error("Wrong password!")

else:
    st.write("Select a page")