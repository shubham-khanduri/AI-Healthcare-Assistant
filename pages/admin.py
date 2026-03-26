"""
app.py — AI Healthcare Assistant
Main Streamlit application.

Run with:  streamlit run app.py
"""
from datetime import date

import streamlit as st
from dotenv import load_dotenv

import database as db
import ai_assistant as ai

load_dotenv()

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Diagnosis card */
        .diag-card {
            background: #fffbf0;
            border-left: 5px solid #f59e0b;
            border-radius: 8px;
            padding: 1.1rem 1.3rem;
            margin: .5rem 0;
        }
        /* Consultation card */
        .consult-card {
            background: #f0fdf4;
            border-left: 5px solid #22c55e;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: .4rem 0;
        }
        /* Soften metric numbers */
        [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## 🏥 AI Healthcare")
    st.divider()


all_patients = db.get_all_patients()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
st.title("🏥 AI Healthcare Assistant")
st.markdown("*AI-powered health management — empowering patients with knowledge*")
st.divider()

# Summary metrics
n_p, n_d, n_c = db.get_stats()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Registered Patients", n_p)
m2.metric("Diagnoses Recorded",  n_d)
m3.metric("AI Consultations",    n_c)
m4.metric("AI Status", "Ready ✅" if st.session_state.ai_ok else "Setup Needed ⚠️")

st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("👥 Patient Overview")
    for p in all_patients:
        diag_count = len(db.get_patient_diagnoses(p["id"]))
        with st.container(border=True):
            ca, cb, cc = st.columns([3, 1, 1])
            with ca:
                st.markdown(f"**{p['name']}** &nbsp; `{p['gender']}` &nbsp; Age {p['age']}")
                st.caption(f"🩸 {p['blood_type']}  &nbsp;  ⚠️ Allergies: {p['allergies']}")
            cb.metric("Diagnoses", diag_count)
            if cc.button("View →", key=f"view_{p['id']}"):
                st.session_state.patient_id = p["id"]
                st.session_state.chat_msgs  = []

