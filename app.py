import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Ebuka Store", layout="wide")

# ========= SETTINGS =========
ADMIN_EMAIL = "yourmail@gmail.com" # where you receive orders
SENDER_EMAIL = "yourmail@gmail.com" # gmail to send from
SENDER_PASSWORD = "your-app-password" # use Gmail App Password

# ========= SESSION STATE =========
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp" not in st.session_state: st.session_state.otp = None
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "cart" not in st.session_state: st.session_state.cart = []

# ========= PRODUCTS =========
products = [
    {"id": 1, "name": "ON MY LIGHT - Digital Album", "price": 5000, "img": "/mnt/data/wa_image_2507823551423557689", "desc": "KELLY B vs SRET WISE"},
    {"id": 2, "name": "Wireless Earphone", "price": 25000, "img": "https://placehold.co/400x400/1a1d23/ffffff?text=Earphone", "desc": "Noise Cancelling"},
    {"id": 3, "name": "Company T-Shirt", "price": 12000, "img": "https://placehold.co/400x400/1a1d23/ffffff?text=T-Shirt", "desc": "Black Premium Cotton"}
]

# ========= FUNCTIONS =========
def send_otp(email):
    code = str(random.randint(100000, 999999))
    st.session_state.otp = code
    st.session_state.user_email = email
    st.info(f"Demo Code: {code}") # Remove this when using real email
    # In production, send real email here

def send_confirmation_email(to_email, cart_items, total):
    subject = "Order Confirmation - Ebuka Store"
    body = f"Thank you for your order!\n\nItems:\n"
    for item in cart_items:
        body += f"- {item['name']} x{item['qty']} = ₦{item['price']*item['qty']:,}\n"
    body += f"\nTotal: ₦{total:,}\n\nWe will contact you on WhatsApp for delivery in Onitsha."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [to_email, ADMIN_EMAIL], msg.as_string())
        server.quit()
        return True
    except:
        return False

# ========= CSS DESIGN =========
st.markdown("""
<style>
   .stApp { background-color: #0e1117; color: white; }
   .product-card { background: #1a1d23; padding: 15px; border-radius: 15px; margin-bottom: 15px; }
   .price { color: #00ff88; font-size: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ========= LOGIN PAGE =========
if not st.session_state.logged_in:
    st.title("🏪 Ebuka Store - Login")
    st.write("Tinye email gị to get code and shop")

    email = st.text_input("Email Address")
    if st.button("Send Login Code"):
        if "@" in email:
            send_otp(email)
        else:
            st.error("Enter valid email")

    otp_input = st.text_input("Enter Code")
    if st.button("Login"):
        if otp_input == st.session_state.otp:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong code")

# ========= SHOP PAGE =========
else:
    st.sidebar.title(f"Hello {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🏪 Ebuka Store")

    # PRODUCT GRID
    st.subheader("Products")
    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.image(product["img"], use_container_width=True) # picture opens immediately
            st.write(f"**{product['name']}**")
            st.caption(product["desc"])
            st.markdown(f'<p class="price">₦{product["price"]:,}</p>', unsafe_allow_html=True)
            qty = st.number_input("Qty", 1, 10, 1, key=f"qty{i}")
            if st.button("Add to Cart", key=f"btn{i}"):
                st.session_state.cart.append({"name": product["name"], "price": product["price"], "qty": qty})
                st.success("Added to cart")
            st.markdown('</div>', unsafe_allow_html=True)

    # CART + CHECKOUT
    with st.sidebar:
        st.title("🛒 Cart")
        if len(st.session_state.cart) == 0:
            st.write("Empty")
        else:
            total = 0
            for item in st.session_state.cart:
                st.write(f"{item['name']} x{item['qty']}")
                total += item['price'] * item['qty']
            st.markdown(f"### Total: ₦{total:,}")

            address = st.text_area("Delivery Address in Onitsha")
            phone = st.text_input("WhatsApp Number")

            if st.button("Place Order"):
                if address and phone:
                    success = send_confirmation_email(st.session_state.user_email, st.session_state.cart, total)
                    if success:
                        st.success("Order placed! Confirmation email sent.")
                        st.session_state.cart = []
                    else:
                        st.error("Email failed. But we got your order.")
                else:
                    st.warning("Add address and phone")

    st.divider()
    st.write("📍 Onitsha, Anambra | 📞 080xxxx | Delivery 24hrs")