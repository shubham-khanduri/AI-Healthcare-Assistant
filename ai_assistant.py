"""
ai_assistant.py — Google Gemini AI integration for the healthcare application.

Provides:
  - configure_gemini()              : initialise and return the Gemini model
  - chat_with_patient_context()     : multi-turn chat with patient history injected
  - analyze_symptoms()              : structured symptom analysis
"""
import os
import google.generativeai as genai
import database as db

# Change to "gemini-2.0-flash" if you want the newer model (also free-tier)
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a compassionate and knowledgeable AI medical assistant \
integrated into a patient healthcare portal.

Your responsibilities:
- Help patients understand their diagnoses, medications, and health conditions.
- Answer health and wellness questions clearly and empathetically.
- Provide general medical information and education.
- Guide patients on when to seek professional care.

Important rules:
- You provide GENERAL HEALTH INFORMATION only — NOT medical advice or diagnoses.
- Always recommend consulting a licensed healthcare provider for treatment decisions.
- When referencing the patient's records, be accurate and specific.
- Be concise, warm, and avoid unnecessary jargon.
- If symptoms sound severe or life-threatening, strongly advise emergency care.
"""


# ── Setup ──────────────────────────────────────────────────────────────────────

def configure_gemini():
    """Read API key from environment, configure Gemini, and return the model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found.\n"
            "1. Create a free key at https://aistudio.google.com/app/apikey\n"
            "2. Add it to a .env file:  GEMINI_API_KEY=your_key_here"
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_patient_context(patient_id: int) -> str:
    """Build a compact plain-text summary of the patient's medical record."""
    patient   = db.get_patient(patient_id)
    diagnoses = db.get_patient_diagnoses(patient_id)

    if not patient:
        return "No patient record found."

    n = len(diagnoses)
    lines = [
        "=== PATIENT MEDICAL RECORD ===",
        f"Name       : {patient['name']}",
        f"Age/Gender : {patient['age']} years old, {patient['gender']}",
        f"Blood Type : {patient['blood_type']}",
        f"Allergies  : {patient['allergies']}",
        "",
        f"=== DIAGNOSIS HISTORY ({n} record{'s' if n != 1 else ''}) ===",
    ]

    if diagnoses:
        for d in diagnoses:
            lines += [
                f"  Date     : {d['date']}",
                f"  Condition: {d['diagnosis']}",
                f"  Doctor   : {d['doctor_name']}",
                f"  Meds     : {d['medications'] or 'None prescribed'}",
                f"  Notes    : {d['notes'] or 'None'}",
                "  " + "-" * 40,
            ]
    else:
        lines.append("  No diagnoses on record.")

    return "\n".join(lines)


# ── AI Functions ───────────────────────────────────────────────────────────────

def chat_with_patient_context(patient_id: int, question: str,
                               model, prev_messages: list) -> str:
    """
    Send a question to Gemini with the patient's full medical context.

    prev_messages  – list of {"role": "user"|"assistant", "content": "..."} 
                     representing turns BEFORE the current question.
    """
    ctx = _build_patient_context(patient_id)

    # Convert previous turns into Gemini's history format
    gemini_history = [
        {
            "role": "user" if m["role"] == "user" else "model",
            "parts": [m["content"]],
        }
        for m in prev_messages
    ]

    chat = model.start_chat(history=gemini_history)

    # Inject patient context with every new message so it's always fresh
    prompt = (
        f"[Patient Medical Context — use this to personalise your answer]\n"
        f"{ctx}\n\n"
        f"[Patient's Question]\n{question}"
    )
    return chat.send_message(prompt).text


def analyze_symptoms(symptoms: str, model, patient_id: int = None) -> str:
    """
    Analyse reported symptoms and return a structured, readable assessment.
    If a patient is selected their profile is included for personalised results.
    """
    patient_context = ""
    if patient_id:
        patient   = db.get_patient(patient_id)
        diagnoses = db.get_patient_diagnoses(patient_id)
        if patient:
            existing = (
                ", ".join(d["diagnosis"] for d in diagnoses)
                if diagnoses else "none recorded"
            )
            patient_context = (
                f"\nPatient Profile: {patient['age']}-year-old {patient['gender']}, "
                f"Blood type: {patient['blood_type']}, Allergies: {patient['allergies']}\n"
                f"Existing conditions: {existing}\n"
            )

    prompt = f"""A patient has reported the following symptoms:

Symptoms: {symptoms}
{patient_context}
Please provide a structured response with these sections:

## 🔎 Possible Conditions
List 3–5 possible conditions ranked from most to least likely.
For each, give a one-sentence explanation of why it fits these symptoms.

## 🚨 Warning Signs — Seek Emergency Care If…
List specific red-flag symptoms requiring immediate emergency attention.

## 💊 General Self-Care Tips
Safe, practical home-care suggestions for symptom relief.

## 📋 Recommended Next Steps
Clear guidance on the appropriate level of care (self-care / GP / urgent care / ER).

---
End with a brief disclaimer reminding the patient this is not a diagnosis \
and they should consult a qualified healthcare professional.
"""
    return model.generate_content(prompt).text
