"""
app.py — AI Healthcare Assistant
Main Streamlit application.

Run with:  streamlit run app.py
"""
from datetime import date
import time

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

patient_id = None
logged_in = False

query_params = st.query_params

if "id" in query_params:
    patient_id = query_params["id"]

if "logged_in" in query_params:
    logged_in = query_params["logged_in"]

# ── Session state defaults ────────────────────────────────────────────────────
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = []
if "model" not in st.session_state:
    st.session_state.model  = None
    st.session_state.ai_ok  = False
    st.session_state.ai_err = ""

if not logged_in:
    st.markdown("### Please login first. Redirecting to login page in 5 seconds...")

    time.sleep(5)

    st.switch_page("pages/login.py")

else:
    left, right = st.columns([7, 1])

    with right:
        if st.button("Log Out", type="primary", use_container_width=True):
            st.switch_page("app.py")

    # Load Gemini model once per session
    if not st.session_state.model:
        try:
            st.session_state.model = ai.configure_gemini()
            st.session_state.ai_ok = True
        except Exception as exc:
            st.session_state.ai_err = str(exc)

    # ── Sidebar ───────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🏥 AI Healthcare")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "👤 Patient Profile",
                "🤖 AI Assistant",
                "🔍 Symptom Checker"
            ],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**Active Patient**")

        st.session_state.patient_id = patient_id
        
        pat = db.get_patient(st.session_state.patient_id)
        st.success(f"👤 {pat['name']}")
        st.caption(f"Age {pat['age']} · {pat['gender']} · {pat['blood_type']}")
        
        st.divider()
        if st.session_state.ai_ok:
            st.markdown("**AI Status:** ✅ Ready")
        else:
            st.markdown("**AI Status:** ❌ Not configured")
            with st.expander("Setup help"):
                st.caption("Create a `.env` file in this folder with:")
                st.code("GEMINI_API_KEY=your_key_here", language="bash")
                st.caption("Free key → https://aistudio.google.com/app/apikey")
                if st.session_state.ai_err:
                    st.caption(f"Error: {st.session_state.ai_err}")


    # ── Guard helpers ──────────────────────────────────────────────────────────────
    def need_patient() -> bool:
        if not st.session_state.patient_id:
            st.warning("👈  Please select a patient from the sidebar to continue.")
            return False
        return True


    def need_ai() -> bool:
        if not st.session_state.ai_ok:
            st.error("AI is not configured. Add your Gemini API key to the `.env` file.")
            st.code("GEMINI_API_KEY=your_key_here", language="bash")
            st.markdown("Get a free key → https://aistudio.google.com/app/apikey")
            return False
        return True


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE: PATIENT PROFILE
    # ══════════════════════════════════════════════════════════════════════════════
    if page == "👤 Patient Profile":
        if need_patient():
            patient = db.get_patient(st.session_state.patient_id)

            # Header
            st.title(f"👤 {patient['name']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Age",        patient["age"])
            c2.metric("Gender",     patient["gender"])
            c3.metric("Blood Type", patient["blood_type"])
            allergy_display = patient["allergies"]
            c4.metric("Allergies",  allergy_display[:22] + ("…" if len(allergy_display) > 22 else ""))

            with st.container(border=True):
                st.caption(
                    f"📧 {patient['contact'] or 'No contact saved'}"
                    f"   •   📅 Patient since {patient['created_at'][:10]}"
                )

            st.divider()

            tab_hist, tab_add, tab_consult = st.tabs(
                ["📋 Medical History", "➕ Add Diagnosis", "💬 Assistant History"]
            )

            # ── Tab 1: Medical history ─────────────────────────────────────────────
            with tab_hist:
                diagnoses = db.get_patient_diagnoses(st.session_state.patient_id)
                if not diagnoses:
                    st.info("No diagnoses recorded yet. Use the **Add Diagnosis** tab to add one.")
                else:
                    for d in diagnoses:
                        with st.expander(
                            f"🗓️ {d['date']}  —  **{d['diagnosis']}**  ·  {d['doctor_name']}",
                            expanded=True,
                        ):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown(f"**Condition:** {d['diagnosis']}")
                                st.markdown(f"**Date:** {d['date']}")
                                st.markdown(f"**Doctor:** {d['doctor_name']}")
                            with col_b:
                                st.markdown("**Medications:**")
                                if d["medications"]:
                                    for med in d["medications"].split(","):
                                        st.markdown(f"• {med.strip()}")
                                else:
                                    st.caption("None prescribed")
                            if d["notes"]:
                                st.info(f"📝 **Notes:** {d['notes']}")

            # ── Tab 2: Add diagnosis ───────────────────────────────────────────────
            with tab_add:
                st.subheader("Record a New Diagnosis")
                with st.form("add_diagnosis_form", clear_on_submit=True):
                    fc1, fc2 = st.columns(2)
                    diag_date   = fc1.date_input("Date of Diagnosis",  value=date.today())
                    doctor_name = fc2.text_input("Doctor's Name *",     placeholder="Dr. Jane Smith")
                    diagnosis   = st.text_input(
                        "Diagnosis / Condition *",
                        placeholder="e.g., Type 2 Diabetes Mellitus",
                    )
                    medications = st.text_area(
                        "Medications",
                        placeholder="e.g., Metformin 500mg twice daily, Lisinopril 10mg once daily",
                        height=80,
                    )
                    notes = st.text_area(
                        "Clinical Notes",
                        placeholder="e.g., Follow-up in 3 months, monitor HbA1c",
                        height=80,
                    )
                    if st.form_submit_button("💾 Save Diagnosis", type="primary", use_container_width=True):
                        if not doctor_name.strip() or not diagnosis.strip():
                            st.error("Doctor's name and diagnosis are required.")
                        else:
                            db.add_diagnosis(
                                st.session_state.patient_id,
                                str(diag_date),
                                doctor_name.strip(),
                                diagnosis.strip(),
                                medications,
                                notes,
                            )
                            st.success("✅ Diagnosis recorded successfully!")
                            st.rerun()

            # ── Tab 3: Consultation history ────────────────────────────────────────
            with tab_consult:
                consultations = db.get_patient_consultations(st.session_state.patient_id)
                if not consultations:
                    st.info("No AI consultations yet. Try the **AI Assistant** or **Symptom Checker**!")
                else:
                    for c in consultations:
                        icon    = "🔍" if c["type"] == "symptom_check" else "🤖"
                        label   = "Symptom Check" if c["type"] == "symptom_check" else "AI Chat"
                        preview = c["query"][:65] + ("…" if len(c["query"]) > 65 else "")
                        with st.expander(f"{icon} {label}  ·  {c['timestamp'][:16]}  —  {preview}"):
                            st.markdown(f"**Query:**\n\n{c['query']}")
                            st.divider()
                            st.markdown(c["response"])


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE: AI ASSISTANT
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "🤖 AI Assistant":
        if need_patient() and need_ai():
            patient   = db.get_patient(st.session_state.patient_id)
            diagnoses = db.get_patient_diagnoses(st.session_state.patient_id)

            st.title("🤖 AI Health Assistant")
            st.markdown(
                f"Chatting in context of **{patient['name']}** "
                f"({patient['age']} y/o {patient['gender']})"
            )

            i1, i2, i3 = st.columns(3)
            i1.info(f"📋 {len(diagnoses)} diagnosis record{'s' if len(diagnoses) != 1 else ''}")
            i2.info(f"⚠️ Allergies: {patient['allergies']}")
            i3.info(f"🩸 Blood type: {patient['blood_type']}")

            st.divider()

            # Suggested questions based on existing diagnoses
            if diagnoses and not st.session_state.chat_msgs:
                conditions = [d["diagnosis"] for d in diagnoses[:3]]
                st.markdown("**💡 Suggested questions:**")
                sq_cols = st.columns(len(conditions))
                for idx, cond in enumerate(conditions):
                    suggestion = f"What should I know about managing {cond}?"
                    if sq_cols[idx].button(suggestion, key=f"sq_{idx}"):
                        st.session_state.chat_msgs.append(
                            {"role": "user", "content": suggestion}
                        )
                        with st.spinner("Thinking…"):
                            try:
                                resp = ai.chat_with_patient_context(
                                    st.session_state.patient_id,
                                    suggestion,
                                    st.session_state.model,
                                    [],
                                )
                                st.session_state.chat_msgs.append(
                                    {"role": "assistant", "content": resp}
                                )
                                db.save_consultation(
                                    st.session_state.patient_id, suggestion, resp, "chat"
                                )
                            except Exception as exc:
                                st.session_state.chat_msgs.append(
                                    {"role": "assistant", "content": f"⚠️ AI error: {exc}"}
                                )
                        st.rerun()
                st.divider()

            # Display chat history
            if not st.session_state.chat_msgs:
                with st.chat_message("assistant"):
                    st.markdown(
                        f"Hello! I'm your AI health assistant. I have access to "
                        f"**{patient['name']}'s** medical history, including their diagnoses "
                        f"and current medications. How can I help you today?"
                    )

            for msg in st.session_state.chat_msgs:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Chat input
            if user_input := st.chat_input("Ask about your health, medications, diagnoses…"):
                st.session_state.chat_msgs.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking…"):
                        try:
                            prev_msgs = st.session_state.chat_msgs[:-1]   # exclude current
                            resp = ai.chat_with_patient_context(
                                st.session_state.patient_id,
                                user_input,
                                st.session_state.model,
                                prev_msgs,
                            )
                            st.markdown(resp)
                            st.session_state.chat_msgs.append(
                                {"role": "assistant", "content": resp}
                            )
                            db.save_consultation(
                                st.session_state.patient_id, user_input, resp, "chat"
                            )
                        except Exception as exc:
                            err_msg = f"⚠️ AI error: {exc}"
                            st.error(err_msg)
                            st.session_state.chat_msgs.append(
                                {"role": "assistant", "content": err_msg}
                            )

            # Clear chat button
            if st.session_state.chat_msgs:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_msgs = []
                    st.rerun()


    # ══════════════════════════════════════════════════════════════════════════════
    # PAGE: SYMPTOM CHECKER
    # ══════════════════════════════════════════════════════════════════════════════
    elif page == "🔍 Symptom Checker":
        if need_ai():
            st.title("🔍 Symptom Checker")
            st.markdown(
                "Describe your symptoms and receive an AI-powered health assessment. "
                "Select a patient for a personalised analysis."
            )

            if st.session_state.patient_id:
                p = db.get_patient(st.session_state.patient_id)
                st.success(
                    f"Personalised for **{p['name']}** "
                    f"(Age {p['age']}, {p['gender']}) — medical history included."
                )
            else:
                st.info(
                    "No patient selected — analysis will be general. "
                    "Select a patient for personalised results."
                )

            st.divider()

            with st.form("symptom_form"):
                symptoms = st.text_area(
                    "Describe your symptoms *",
                    placeholder=(
                        "e.g., I have been experiencing a persistent headache for two days, "
                        "along with a mild fever (38 °C), fatigue, and stiff neck…"
                    ),
                    height=130,
                )
                sc1, sc2 = st.columns(2)
                duration = sc1.text_input("How long have you had these symptoms?",
                                        placeholder="e.g., 2 days, 1 week")
                severity = sc2.select_slider(
                    "Overall severity",
                    options=["Mild", "Moderate", "Severe"],
                    value="Moderate",
                )
                submitted = st.form_submit_button(
                    "🔍 Analyse Symptoms", type="primary", use_container_width=True
                )

            if submitted:
                if not symptoms.strip():
                    st.error("Please describe your symptoms before analysing.")
                else:
                    full_input = (
                        f"{symptoms}\n"
                        f"Duration: {duration or 'not specified'}\n"
                        f"Severity: {severity}"
                    )
                    with st.spinner("Analysing your symptoms…"):
                        try:
                            result = ai.analyze_symptoms(
                                full_input,
                                st.session_state.model,
                                st.session_state.patient_id,
                            )

                            st.subheader("📊 AI Analysis Results")
                            st.markdown(result)
                            st.warning(
                                "⚠️ **Disclaimer:** This is AI-generated health information, "
                                "not a medical diagnosis. Always consult a qualified healthcare "
                                "professional for proper evaluation and treatment."
                            )

                            if st.session_state.patient_id:
                                db.save_consultation(
                                    st.session_state.patient_id,
                                    full_input,
                                    result,
                                    "symptom_check",
                                )
                                st.caption("✅ Analysis saved to consultation history.")
                        except Exception as exc:
                            st.error(f"AI error: {exc}")

