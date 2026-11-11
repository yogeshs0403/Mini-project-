# Cybersecurity Awareness Portal

A beginner-friendly CSE mini project built with Python Flask, SQLite, HTML, CSS and JavaScript.

## Features
- User registration and login (passwords are hashed)
- Awareness lessons about phishing, passwords, MFA and safe browsing
- Interactive cybersecurity quiz with score and explanations
- User dashboard showing recent quiz results
- Admin dashboard showing registered users and quiz attempts

## Requirements
- Python 3.9+
- VS Code (recommended)

## Run on Windows / macOS / Linux
1. Extract the ZIP.
2. Open this folder in VS Code.
3. Open a terminal in the project folder.
4. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

   macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

   Windows:
   ```bash
   venv\\Scripts\\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python app.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

The SQLite database (`portal.db`) is created automatically on first run.

## Demo admin account
- Username: `admin`
- Password: `ChangeMe123!`

Change this demo password and the Flask `secret_key` before using the app beyond a local classroom demo. Do not deploy with Flask debug mode enabled.

## Suggested mini-project extensions
- Add email-based password reset
- Add categories and searchable awareness articles
- Add quiz question management in the admin panel
- Add charts for quiz performance
- Add CSRF protection and stronger production configuration

## Project note
This is an educational demonstration, not a production security product. Do not enter real or reused passwords.
