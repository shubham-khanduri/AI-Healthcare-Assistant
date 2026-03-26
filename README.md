# 🏥 AI Healthcare Assistant

A Python AI healthcare web application that lets patients manage their medical profiles, 
review diagnoses, and get personalised health guidance from an AI assistant powered by 
Google Gemini.

Built as a second-year engineering student project using **Streamlit**, **SQLite**, and 
the **Google Gemini API**.

---

## Features

| Feature | Description |
|---|---|
| **Login & Registration** | Patients log in with their email address; new patients can self-register |
| **Patient Management** | Register patients with age, gender, blood type, and allergy info |
| **Diagnosis Records** | Each diagnosis stores date, doctor's name, medications, and notes |
| **Medical History** | View all past diagnoses in an expandable card layout |
| **AI Assistant** | Multi-turn chat that reads the patient's full medical history for context-aware answers |
| **Symptom Checker** | Input symptoms + duration + severity → AI returns ranked conditions, self-care tips, and when to seek care |
| **Consultation History** | All AI interactions are saved and viewable per patient |
| **Admin Dashboard** | Overview of all registered patients, system stats, and quick navigation |
| **Mock Data** | 4 demo patients with 8 realistic diagnoses pre-loaded on first run |

---

## Project Structure

```
AIHC/
├── app.py              ← Landing / home page
├── database.py         ← SQLite CRUD operations + data seeding
├── ai_assistant.py     ← Google Gemini AI integration
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
├── README.md
└── pages/
    ├── login.py        ← Login page (email-based authentication)
    ├── register.py     ← New patient registration form
    ├── patient.py      ← Patient portal (Profile, AI Assistant, Symptom Checker)
    └── admin.py        ← Admin dashboard (all patients + stats)
```

---

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a free Gemini API key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key

### 3. Create your `.env` file

Create a `.env` file and add the line below. Replace the placeholder with your real key:

```
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

### 4. Run the application

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## How to Use

1. **Landing page** — click **Login →** in the top-right corner
2. **Login** — enter the email address associated with your patient record  
   - No account? Click **Register** to create one
3. Once logged in, navigate using the left sidebar:
   - **Patient Profile** — view medical history, add diagnoses, see past AI consultations
   - **AI Assistant** — chat with the AI about your health (context-aware, with suggested questions)
   - **Symptom Checker** — describe symptoms for AI-powered triage

> **Demo accounts** — use any of the pre-loaded patient emails (e.g. `alice.j@example.com`) to log in without registering.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit (multi-page app) |
| AI Model | Google Gemini 2.5 Flash (free tier) |
| Database | SQLite 3 (local file: `healthcare.db`) |
| Language | Python 3.10+ |

---

## Notes

- The database file `healthcare.db` is created automatically on first run — no setup needed
- To reset mock data, simply delete `healthcare.db` and restart the app
- To use a different Gemini model, change `GEMINI_MODEL` in `ai_assistant.py`
- Login uses the patient's `contact` (email) field — no password is stored
- The AI always includes the patient's medical record in every prompt to provide personalised answers
- All AI responses are automatically saved to the consultation history table

---

## Disclaimer

This application is for **educational purposes only**. The AI assistant provides general health information and is not a substitute for professional medical advice, diagnosis, or treatment.
