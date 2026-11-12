import os
import re
import secrets
import sqlite3

from contextlib import closing
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session


# =====================================
# FLASK APPLICATION CONFIGURATION
# =====================================

app = Flask(__name__)

# Use an environment variable for deployment.
# A temporary random key is used when no environment key is configured.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true"
)

# Database location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "securecheck.db")

# Maximum accepted sample password length
MAX_PASSWORD_LENGTH = 256


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =====================================
# CREATE DATABASE TABLE
# =====================================

def init_db():

    with closing(get_db_connection()) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strength TEXT NOT NULL,
                percentage INTEGER NOT NULL,
                analyzed_at TEXT NOT NULL
            )
        """)

        connection.commit()


# Initialize database automatically
init_db()


# =====================================
# COMMON PASSWORD CHECK
# =====================================

COMMON_PASSWORDS = {
    "password",
    "password123",
    "123456",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "welcome",
    "letmein",
    "iloveyou",
    "abc123",
    "111111",
    "000000"
}


# =====================================
# PREDICTABLE PATTERN CHECK
# =====================================

def has_predictable_pattern(password):

    predictable_patterns = [
        "123456",
        "654321",
        "abcdef",
        "qwerty",
        "asdf",
        "password",
        "987654"
    ]

    password_lower = password.lower()

    return any(
        pattern in password_lower
        for pattern in predictable_patterns
    )


# =====================================
# PASSWORD ANALYSIS FUNCTION
# =====================================

def analyze_password(password):

    password_lower = password.lower()

    is_common = password_lower in COMMON_PASSWORDS

    has_repeated_characters = bool(
        re.search(r"(.)\1{2,}", password)
    )

    has_sequence = has_predictable_pattern(password)

    # Security checklist
    checks = {

        "At least 12 characters": len(password) >= 12,

        "At least 16 characters": len(password) >= 16,

        "Uppercase letter": any(
            character.isupper() for character in password
        ),

        "Lowercase letter": any(
            character.islower() for character in password
        ),

        "Number": any(
            character.isdigit() for character in password
        ),

        "Special character": any(
            not character.isalnum() for character in password
        ),

        "Not a common password": not is_common,

        "No predictable sequences": not has_sequence,

        "No character repeated 3 or more times consecutively":
            not has_repeated_characters

    }

    # Calculate score
    score = sum(checks.values())

    total_checks = len(checks)

    percentage = round(
        (score / total_checks) * 100
    )

    # Determine password strength
    if score <= 3:

        strength = "Weak"

    elif score <= 6:

        strength = "Moderate"

    else:

        strength = "Strong"

    # Generate improvement suggestions
    suggestions = [
        check
        for check, passed in checks.items()
        if not passed
    ]

    return strength, checks, suggestions, percentage


# =====================================
# SAVE ANALYSIS TO DATABASE
# =====================================

def save_analysis(strength, percentage):

    analyzed_at = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    # Only analysis metadata is saved.
    # The actual password is never inserted into SQLite.

    with closing(get_db_connection()) as connection:

        connection.execute("""
            INSERT INTO analysis_history
            (strength, percentage, analyzed_at)
            VALUES (?, ?, ?)
        """, (strength, percentage, analyzed_at))

        connection.commit()


# =====================================
# GET DASHBOARD STATISTICS
# =====================================

def get_dashboard_stats():

    with closing(get_db_connection()) as connection:

        total = connection.execute("""
            SELECT COUNT(*) AS total
            FROM analysis_history
        """).fetchone()["total"]

        weak = connection.execute("""
            SELECT COUNT(*) AS total
            FROM analysis_history
            WHERE strength = 'Weak'
        """).fetchone()["total"]

        moderate = connection.execute("""
            SELECT COUNT(*) AS total
            FROM analysis_history
            WHERE strength = 'Moderate'
        """).fetchone()["total"]

        strong = connection.execute("""
            SELECT COUNT(*) AS total
            FROM analysis_history
            WHERE strength = 'Strong'
        """).fetchone()["total"]

    return {
        "total": total,
        "weak": weak,
        "moderate": moderate,
        "strong": strong
    }


# =====================================
# GET RECENT ANALYSIS ACTIVITY
# =====================================

def get_recent_activity():

    with closing(get_db_connection()) as connection:

        records = connection.execute("""
            SELECT strength, percentage, analyzed_at
            FROM analysis_history
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

    recent_activity = []

    for record in records:

        recent_activity.append({
            "strength": record["strength"],
            "percentage": record["percentage"],
            "time": record["analyzed_at"]
        })

    return recent_activity


# =====================================
# HOME PAGE
# =====================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        password = request.form.get("password", "")

        # Accept non-empty sample passwords up to the limit.
        if password and len(password) <= MAX_PASSWORD_LENGTH:

            strength, checks, suggestions, percentage = (
                analyze_password(password)
            )

            # Save only the analysis result.
            # Never save the actual password.

            save_analysis(strength, percentage)

            # Store only the analysis result in the session.
            session["analysis_result"] = {
                "strength": strength,
                "checks": checks,
                "suggestions": suggestions,
                "percentage": percentage
            }

        return redirect(url_for("home"))

    # Display the result once
    result = session.pop("analysis_result", None)

    # Get dashboard information
    stats = get_dashboard_stats()

    recent_activity = get_recent_activity()

    return render_template(
        "index.html",
        result=result,
        stats=stats,
        recent_activity=recent_activity
    )


# =====================================
# CLEAR ANALYSIS HISTORY
# =====================================

@app.route("/clear-history", methods=["POST"])
def clear_history():

    with closing(get_db_connection()) as connection:

        connection.execute(
            "DELETE FROM analysis_history"
        )

        connection.commit()

    # Remove previous analysis result
    session.pop("analysis_result", None)

    return redirect(url_for("home"))


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1"
    )