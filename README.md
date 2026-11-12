# SecureCheck – Password Strength Checker

## Project Overview

SecureCheck is a web-based password strength analysis application developed using Python and Flask. It evaluates sample passwords using educational security checks and provides immediate feedback through a live strength indicator.

The application includes a dashboard for viewing password analysis statistics and recent activity.

## Features

- **Password Strength Analysis:** Evaluates passwords using nine security checks.
- **Live Strength Indicator:** Displays strength and percentage while typing.
- **Show/Hide Password:** Allows users to toggle password visibility.
- **Security Checklist:** Shows which security criteria have passed or failed.
- **Improvement Suggestions:** Identifies areas where password security can be improved.
- **Dashboard:** Displays total, weak, moderate and strong analysis counts.
- **Strength Distribution:** Visualizes password analysis statistics.
- **Recent Activity:** Displays the latest five analysis records.
- **Clear History:** Allows users to clear saved analysis history.
- **About Page:** Provides project details and information.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive design |
| JavaScript | Interactive functionality |
| SQLite | Analysis history storage |

## Project Structure

```text
SecureCheck/
│
├── app.py
├── .gitignore
├── securecheck.db
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── js/
│       └── script.js
│
└── venv/
```

Note: The SQLite database and virtual environment are created locally and are excluded from the Git repository.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Fouziya02/SecureCheck.git
```

### 2. Open the project folder

```bash
cd SecureCheck
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows Command Prompt:

```bash
venv\Scripts\activate
```

### 5. Install Flask

```bash
pip install Flask
```

### 6. Run the application

```bash
python app.py
```

### 7. Open the application

Visit:

```text
http://127.0.0.1:5000
```

## Database and Privacy

SecureCheck uses SQLite to maintain password analysis history.

The application stores analysis metadata, including:
- Password strength
- Percentage score
- Analysis date and time

The actual password values are not inserted into the analysis history database.

## Project Purpose

This project was developed as an educational cybersecurity task to demonstrate password strength evaluation, web application development, database integration and interactive frontend functionality.

## Important Note

SecureCheck uses an educational scoring method. Its results are not a guarantee of password security and should not be treated as a replacement for a professional password security assessment.

---

**Project Name:** SecureCheck – Password Strength Checker  
**Repository:** https://github.com/Fouziya02/SecureCheck
