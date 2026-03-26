"""
database.py — SQLite data layer for the AI Healthcare application.
Handles all CRUD operations for patients, diagnoses, and consultations.
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "healthcare.db"


@contextmanager
def _db():
    """Context manager that opens a connection, commits, and closes cleanly."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema & Seed ──────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist and seed mock data on first run."""
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                age         INTEGER NOT NULL,
                gender      TEXT    NOT NULL,
                blood_type  TEXT    DEFAULT 'Unknown',
                allergies   TEXT    DEFAULT 'None',
                contact     TEXT    DEFAULT '',
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS diagnoses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  INTEGER NOT NULL REFERENCES patients(id),
                date        TEXT    NOT NULL,
                doctor_name TEXT    NOT NULL,
                diagnosis   TEXT    NOT NULL,
                medications TEXT    DEFAULT '',
                notes       TEXT    DEFAULT '',
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS consultations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  INTEGER NOT NULL REFERENCES patients(id),
                type        TEXT    NOT NULL DEFAULT 'chat',
                query       TEXT    NOT NULL,
                response    TEXT    NOT NULL,
                timestamp   TEXT    DEFAULT (datetime('now'))
            );
        """)
        if conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
            _seed(conn)


def _seed(conn):
    """Insert mock patients and diagnoses for demonstration purposes."""
    patients = [
        ("Alice Johnson", 34, "Female", "A+",  "Penicillin",      "alice.j@example.com"),
        ("Bob Martinez",  52, "Male",   "O-",  "None",            "bob.m@example.com"),
        ("Carol White",   27, "Female", "B+",  "Aspirin, Pollen", "carol.w@example.com"),
        ("David Chen",    45, "Male",   "AB+", "Sulfa drugs",     "david.c@example.com"),
    ]
    conn.executemany(
        "INSERT INTO patients (name, age, gender, blood_type, allergies, contact)"
        " VALUES (?,?,?,?,?,?)",
        patients,
    )

    # (patient_id, date, doctor_name, diagnosis, medications, notes)
    diagnoses = [
        # Alice (id 1)
        (1, "2025-08-14", "Dr. Emily Smith",
         "Type 2 Diabetes Mellitus",
         "Metformin 500mg twice daily",
         "HbA1c target < 7%. Monitor blood sugar daily. Follow-up in 3 months."),
        (1, "2026-01-10", "Dr. Emily Smith",
         "Essential Hypertension",
         "Lisinopril 10mg once daily",
         "DASH diet recommended. Sodium intake < 2 g/day. BP target < 130/80 mmHg."),
        # Bob (id 2)
        (2, "2025-07-22", "Dr. Raj Patel",
         "Chronic Lower Back Pain",
         "Ibuprofen 400mg as needed (max 3x daily), Cyclobenzaprine 5mg at bedtime",
         "Physical therapy 3x/week for 6 weeks. Avoid heavy lifting > 10 lbs."),
        (2, "2026-02-28", "Dr. Lisa Nguyen",
         "Hyperlipidemia",
         "Atorvastatin 20mg at bedtime",
         "Low-fat, high-fiber diet. Repeat lipid panel in 12 weeks."),
        # Carol (id 3)
        (3, "2026-01-05", "Dr. James Lee",
         "Seasonal Allergic Rhinitis",
         "Cetirizine 10mg once daily, Fluticasone nasal spray 2 sprays each nostril daily",
         "Reduce outdoor exposure on high-pollen days. Keep windows closed."),
        (3, "2026-03-01", "Dr. James Lee",
         "Vitamin D Deficiency",
         "Vitamin D3 2000 IU once daily with meals",
         "Recheck 25-OH Vitamin D in 3 months. Aim for 15-20 min of sunlight daily."),
        # David (id 4)
        (4, "2025-12-15", "Dr. Maria Torres",
         "Gastroesophageal Reflux Disease (GERD)",
         "Omeprazole 20mg 30 minutes before breakfast",
         "Avoid spicy foods, caffeine, alcohol, and meals within 3 hours of bedtime."),
        (4, "2026-02-20", "Dr. Maria Torres",
         "Mild Anxiety Disorder",
         "Escitalopram 10mg once daily",
         "Follow-up in 4 weeks. Referred to therapist for cognitive behavioural therapy (CBT)."),
    ]
    conn.executemany(
        "INSERT INTO diagnoses (patient_id, date, doctor_name, diagnosis, medications, notes)"
        " VALUES (?,?,?,?,?,?)",
        diagnoses,
    )


# ── Patients ───────────────────────────────────────────────────────────────────

def get_all_patients():
    with _db() as conn:
        return conn.execute("SELECT * FROM patients ORDER BY name").fetchall()


def get_patient(patient_id: int):
    with _db() as conn:
        return conn.execute(
            "SELECT * FROM patients WHERE id=?", (patient_id,)
        ).fetchone()


def add_patient(name: str, age: int, gender: str,
                blood_type: str, allergies: str, contact: str):
    with _db() as conn:
        conn.execute(
            "INSERT INTO patients (name, age, gender, blood_type, allergies, contact)"
            " VALUES (?,?,?,?,?,?)",
            (name, age, gender, blood_type, allergies, contact),
        )


# ── Diagnoses ──────────────────────────────────────────────────────────────────

def get_patient_diagnoses(patient_id: int):
    with _db() as conn:
        return conn.execute(
            "SELECT * FROM diagnoses WHERE patient_id=? ORDER BY date DESC",
            (patient_id,),
        ).fetchall()


def add_diagnosis(patient_id: int, date: str, doctor_name: str,
                  diagnosis: str, medications: str, notes: str):
    with _db() as conn:
        conn.execute(
            "INSERT INTO diagnoses"
            " (patient_id, date, doctor_name, diagnosis, medications, notes)"
            " VALUES (?,?,?,?,?,?)",
            (patient_id, date, doctor_name, diagnosis, medications, notes),
        )


# ── Consultations ──────────────────────────────────────────────────────────────

def get_patient_consultations(patient_id: int):
    with _db() as conn:
        return conn.execute(
            "SELECT * FROM consultations WHERE patient_id=? ORDER BY timestamp DESC",
            (patient_id,),
        ).fetchall()


def save_consultation(patient_id: int, query: str,
                      response: str, type_: str = "chat"):
    with _db() as conn:
        conn.execute(
            "INSERT INTO consultations (patient_id, type, query, response)"
            " VALUES (?,?,?,?)",
            (patient_id, type_, query, response),
        )


def patient_login(patient_email: str):
    with _db() as conn:
        return conn.execute(
            "SELECT id FROM patients WHERE contact=?", (patient_email,)
        ).fetchone()

# ── Stats ──────────────────────────────────────────────────────────────────────

def get_stats():
    """Return (total_patients, total_diagnoses, total_consultations)."""
    with _db() as conn:
        n_p = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        n_d = conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0]
        n_c = conn.execute("SELECT COUNT(*) FROM consultations").fetchone()[0]
        return n_p, n_d, n_c
