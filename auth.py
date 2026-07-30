import streamlit as st
import hashlib
from database import get_connection


# ======================================
# HASH PASSWORD
# ======================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ======================================
# REGISTER USER
# ======================================
def register_user(nama, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    # cek email sudah ada atau belum
    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    if cursor.fetchone():
        conn.close()
        return False, "Email sudah terdaftar."

    password_hash = hash_password(password)

    cursor.execute("""
        INSERT INTO users
        (nama,email,password,role)
        VALUES
        (?,?,?,?)
    """, (
        nama,
        email,
        password_hash,
        "user"
    ))

    conn.commit()
    conn.close()

    return True, "Registrasi berhasil."


# ======================================
# LOGIN
# ======================================
def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=?
        AND password=?
    """, (
        email,
        password_hash
    ))

    user = cursor.fetchone()

    conn.close()

    if user:

        st.session_state["login"] = True
        st.session_state["user_id"] = user["id"]
        st.session_state["nama"] = user["nama"]
        st.session_state["email"] = user["email"]
        st.session_state["role"] = user["role"]

        return True

    return False


# ======================================
# LOGOUT
# ======================================
def logout():

    st.session_state["login"] = False
    st.session_state["user_id"] = None
    st.session_state["nama"] = ""
    st.session_state["email"] = ""
    st.session_state["role"] = ""

    st.rerun()


# ======================================
# SUDAH LOGIN?
# ======================================
def is_login():

    return st.session_state.get("login", False)


# ======================================
# APAKAH ADMIN?
# ======================================
def is_admin():

    return st.session_state.get("role") == "admin"


# ======================================
# APAKAH USER?
# ======================================
def is_user():

    return st.session_state.get("role") == "user"


# ======================================
# INISIALISASI SESSION
# ======================================
def init_session():

    if "login" not in st.session_state:
        st.session_state["login"] = False

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    if "nama" not in st.session_state:
        st.session_state["nama"] = ""

    if "email" not in st.session_state:
        st.session_state["email"] = ""

    if "role" not in st.session_state:
        st.session_state["role"] = ""