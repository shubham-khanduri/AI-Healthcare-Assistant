"""
pages/login.py — AI Healthcare Assistant
Login page: collect email & password and store them in session state.
"""
import streamlit as st
import time
import database as db

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Login — AI Healthcare Assistant",
    page_icon="🏥",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .login-box {
            max-width: 420px;
            margin: 2rem auto;
            padding: 2rem 2.5rem;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,.07);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 7])

with left:
    if st.button("Home", type="primary", use_container_width=True):
        st.switch_page("app.py")


# ── Session state defaults ─────────────────────────────────────────────────────
if "login_email" not in st.session_state:
    st.session_state.login_email = ""
if "login_password" not in st.session_state:
    st.session_state.login_password = ""
if "login_submitted" not in st.session_state:
    st.session_state.login_submitted = False

# ── Login form ─────────────────────────────────────────────────────────────────
st.markdown("## 🏥 AI Healthcare Assistant")
st.markdown("### Login")
st.divider()

with st.form("login_form"):
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Login", use_container_width=True)
    register = st.form_submit_button("Register", use_container_width=True, type="primary")

if submitted:
    if not email or not password:
        st.error("Please enter both email and password.")
    else:
        cur = db.patient_login(email)

        if not cur:
            st.error("User not found")
        else:
            # Store credentials in session state
            st.session_state.login_email = email
            st.session_state.login_password = password
            st.session_state.login_submitted = True
            st.success(f"Logged in as **{email}**")

            time.sleep(1)

            st.switch_page(
                "pages/patient.py",
                query_params = {
                    "id": cur["id"],
                    "logged_in": True
                }
            )
            
if register:
    st.switch_page("pages/register.py")
