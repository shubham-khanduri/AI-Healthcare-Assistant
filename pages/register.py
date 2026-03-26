import streamlit as st

import database as db

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

left, right = st.columns([1, 7])

with left:
    if st.button("Home", type="primary", use_container_width=True):
        st.switch_page("app.py")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD PATIENT
# ══════════════════════════════════════════════════════════════════════════════
st.title("➕ Register New Patient")
st.markdown("Add a new patient to the healthcare system.")
st.divider()

with st.form("add_patient_form", clear_on_submit=True):
    fc1, fc2 = st.columns(2)
    name       = fc1.text_input("Full Name *",  placeholder="Jane Doe")
    age        = fc2.number_input("Age *", min_value=0, max_value=130, value=30, step=1)
    gender     = fc1.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"])
    blood_type = fc2.selectbox(
        "Blood Type",
        ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    )
    allergies = st.text_input(
        "Known Allergies",
        placeholder="e.g., Penicillin, Pollen — enter 'None' if no known allergies",
    )
    contact = st.text_input("Email / Contact", placeholder="patient@example.com")

    if st.form_submit_button("➕ Register Patient", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Patient name is required.")
        else:
            db.add_patient(
                name.strip(),
                int(age),
                gender,
                blood_type,
                allergies or "None",
                contact,
            )
            st.success(f"✅ **{name.strip()}** has been registered successfully!")
            st.balloons()
            st.rerun()
