from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB = "portal.db"

QUIZ = [
    {"q": "What should you do before clicking a link in an unexpected email?",
     "opts": ["Click quickly", "Check the sender and link destination", "Forward it to everyone", "Reply with your password"], "a": 1,
     "why": "Check the sender and destination carefully. Unexpected links may lead to phishing pages."},
    {"q": "Which password is generally strongest?",
     "opts": ["password123", "Your name", "A long, unique passphrase", "12345678"], "a": 2,
     "why": "Long, unique passwords or passphrases are harder to guess. Use a password manager."},
    {"q": "What does multi-factor authentication add?",
     "opts": ["A second verification step", "A faster internet connection", "More storage", "A public profile"], "a": 0,
     "why": "MFA requires an additional proof of identity beyond the password."},
    {"q": "You receive an unexpected attachment. What is safest?",
     "opts": ["Open it immediately", "Verify with the sender through another channel", "Disable antivirus", "Upload it publicly"], "a": 1,
     "why": "Verify unexpected attachments independently before opening them."},
    {"q": "What should you do if an account may be compromised?",
     "opts": ["Ignore it", "Share the password", "Change the password and report it", "Delete security alerts"], "a": 2,
     "why": "Use a trusted device to secure the account, enable MFA, and report the incident."}
]

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        # Demo admin: admin / ChangeMe123! (change after first login)
        exists = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            con.execute("INSERT INTO users(username,password_hash,is_admin) VALUES(?,?,1)",
                        ("admin", generate_password_hash("ChangeMe123!")))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8:
            flash("Username must be 3+ characters and password 8+ characters.", "danger")
        else:
            try:
                with db() as con:
                    con.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                                (username, generate_password_hash(password)))
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username is already taken.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        results = con.execute("SELECT score,total,created_at FROM results WHERE user_id=? ORDER BY id DESC LIMIT 5",
                              (session["user_id"],)).fetchall()
    return render_template("dashboard.html", results=results)

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        score = 0
        for i, item in enumerate(QUIZ):
            if request.form.get(f"q{i}") == str(item["a"]):
                score += 1
        with db() as con:
            con.execute("INSERT INTO results(user_id,score,total) VALUES(?,?,?)",
                        (session["user_id"], score, len(QUIZ)))
        return render_template("quiz_result.html", score=score, total=len(QUIZ), quiz=QUIZ)
    return render_template("quiz.html", quiz=QUIZ)

@app.route("/admin")
@login_required
def admin():
    if not session.get("is_admin"):
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    with db() as con:
        users = con.execute("SELECT id,username FROM users ORDER BY id DESC").fetchall()
        results = con.execute("""SELECT users.username, results.score, results.total, results.created_at
            FROM results JOIN users ON users.id=results.user_id ORDER BY results.id DESC LIMIT 20""").fetchall()
    return render_template("admin.html", users=users, results=results)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
