import streamlit as st
import mysql.connector
import bcrypt

# -------------------------
# Database Connection
# -------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",   # change this
    database="login_system"
)

cursor = conn.cursor()

# -------------------------
# Password Functions
# -------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# -------------------------
# User Functions
# -------------------------
def create_user(username, password):
    try:
        hashed = hash_password(password).decode('utf-8')

        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False

def login_user(username, password):
    query = "SELECT password FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result:
        stored_hash = result[0]
        if verify_password(password, stored_hash):
            return True

    return False

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(
    page_title="Secure Login System",
    page_icon="🔐",
    layout="centered"
)

# -------------------------
# Session State
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------
# Sidebar Menu
# -------------------------
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# -------------------------
# Register Page
# -------------------------
if menu == "Register":
    st.title("📝 Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not new_user or not new_pass:
            st.warning("Please fill all fields")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match")
        elif len(new_pass) < 6:
            st.warning("Password must be at least 6 characters")
        else:
            if create_user(new_user, new_pass):
                st.success("Account created successfully ✅")
            else:
                st.error("Username already exists ❌")

# -------------------------
# Login Page
# -------------------------
elif menu == "Login":

    if not st.session_state.logged_in:
        st.title("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

    else:
        st.title("Dashboard")
        st.success(f"Welcome, {st.session_state.username} 🎉")

        st.write("You are securely logged in.")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

# -------------------------
# Close DB Connection
# -------------------------
# conn.close()