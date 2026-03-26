"""
app.py — AI Healthcare Assistant
Home / landing page.

Run with:  streamlit run app.py
"""

import streamlit as st

import database as db

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Hide default Streamlit header/menu */
        #MainMenu, footer, header { visibility: hidden; }

        /* Top bar */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1.5rem 0;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 2.5rem;
        }
        .topbar-brand {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f766e;
            letter-spacing: -0.3px;
        }

        /* Hero */
        .hero {
            text-align: center;
            padding: 2rem 1rem 3rem 1rem;
        }
        .hero h1 {
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f766e;
            margin-bottom: 0.75rem;
            line-height: 1.2;
        }
        .hero p {
            font-size: 1.15rem;
            color: #475569;
            max-width: 640px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.7;
        }

        /* Feature cards */
        .feature-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 2rem 1.5rem;
            text-align: center;
            height: 100%;
        }
        .feature-card .icon {
            font-size: 2.8rem;
            margin-bottom: 0.8rem;
        }
        .feature-card h3 {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }
        .feature-card p {
            font-size: 0.92rem;
            color: #64748b;
            line-height: 1.6;
        }

        /* Divider label */
        .section-label {
            text-align: center;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #94a3b8;
            margin-bottom: 1.2rem;
        }

        /* How it works steps */
        .step {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1.2rem;
        }
        .step-num {
            min-width: 2rem;
            height: 2rem;
            border-radius: 50%;
            background: #0f766e;
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .step-text h4 {
            margin: 0 0 0.2rem 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: #0f172a;
        }
        .step-text p {
            margin: 0;
            font-size: 0.88rem;
            color: #64748b;
        }

        /* Footer */
        .home-footer {
            text-align: center;
            font-size: 0.8rem;
            color: #94a3b8;
            padding: 2rem 0 1rem 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Initialise database ────────────────────────────────────────────────────────
db.init_db()

# ── Top bar ────────────────────────────────────────────────────────────────────
left, right = st.columns([6, 1])
with left:
    st.markdown('<div class="topbar-brand">🏥 AI Healthcare Assistant</div>', unsafe_allow_html=True)
with right:
    if st.button("Login →", type="primary", use_container_width=True):
        st.switch_page("pages/login.py")

st.divider()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>Your Personal<br>AI Health Companion</h1>
        <p>
            Keep track of your diagnoses and get instant, intelligent answers
            about your health — powered by AI, built around you.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero visual — three inline SVG-based banner icons
col_l, col_c, col_r = st.columns([1, 4, 1])
with col_c:
    st.markdown(
        """
        <div style="display:flex;justify-content:center;gap:3rem;font-size:4rem;padding:1rem 0 2.5rem 0;">
            🩺🧬💊
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Feature cards ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">What we offer</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="icon">📋</div>
            <h3>Diagnosis History</h3>
            <p>All your past diagnoses stored securely in one place — review them anytime, anywhere.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="icon">🤖</div>
            <h3>AI Health Assistant</h3>
            <p>Ask questions about your diagnoses, medications, or general health topics and receive clear, reliable answers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="icon">🔒</div>
            <h3>Private & Secure</h3>
            <p>Your medical data is protected. Only you have access to your personal health records.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)

_, mid, _ = st.columns([1, 3, 1])
with mid:
    st.markdown(
        """
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-text">
                <h4>Create your account</h4>
                <p>Sign up with your email to get started. No complicated forms.</p>
            </div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-text">
                <h4>Log your diagnoses</h4>
                <p>Add diagnoses provided by your doctor and track your health journey over time.</p>
            </div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-text">
                <h4>Ask the AI assistant</h4>
                <p>Chat with an AI that knows your history and answers your healthcare questions instantly.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── CTA ────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    if st.button("Get Started — Login", type="primary", use_container_width=True):
        st.switch_page("pages/login.py")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="home-footer">AI Healthcare Assistant &nbsp;·&nbsp; For informational purposes only. Always consult a qualified healthcare professional.</div>',
    unsafe_allow_html=True,
)
