import os
import shutil
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ORIGINAL_DB = os.path.join(BASE_DIR, "lab_booking.db")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "secret123"

if os.name == 'nt':
    DB_PATH = ORIGINAL_DB
else:
    DB_PATH = "/tmp/lab_booking.db"

def init_db(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS labs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        hour INTEGER NOT NULL,
        lab_name TEXT NOT NULL,
        is_booked INTEGER DEFAULT 0,
        booked_by TEXT DEFAULT NULL
    )
    """)
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users_data = [
            ("student1", "pass123"),
            ("student2", "pass456")
        ]
        cur.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users_data)
        
        labs_data = [
            ("Monday", 3, "CCF"),
            ("Monday", 4, "CCF"),
            ("Monday", 5, "CCF"),
            ("Monday", 6, "CCF"),
            ("Monday", 1, "AI Programming Lab1"),
            ("Monday", 2, "AI Programming Lab1"),
            ("Monday", 1, "AI Programming Lab2"),
            ("Monday", 2, "AI Programming Lab2"),
            ("Monday", 3, "AI Programming Lab2"),
            ("Monday", 3, "System Lab1"),
            ("Monday", 4, "System Lab1"),
            ("Monday", 1, "System Lab2"),
            ("Monday", 2, "System Lab2"),
            ("Tuesday", 3, "CCF"),
            ("Wednesday", 1, "System Lab1"),
            ("Wednesday", 2, "System Lab1"),
            ("Wednesday", 3, "System Lab1"),
            ("Wednesday", 4, "System Lab1"),
            ("Wednesday", 1, "AI Programming Lab1"),
            ("Wednesday", 1, "AI Programming Lab2"),
            ("Wednesday", 5, "AI Programming Lab2"),
            ("Wednesday", 6, "AI Programming Lab2"),
            ("Wednesday", 1, "System Lab2"),
            ("Wednesday", 2, "System Lab2"),
            ("Thursday", 4, "AI Programming Lab1"),
            ("Thursday", 5, "AI Programming Lab1"),
            ("Thursday", 6, "AI Programming Lab1"),
            ("Thursday", 4, "AI Programming Lab2"),
            ("Friday", 3, "CCF"),
            ("Friday", 4, "AI Programming Lab1"),
            ("Friday", 5, "AI Programming Lab1"),
            ("Friday", 6, "AI Programming Lab1"),
            ("Friday", 1, "System Lab1"),
            ("Friday", 5, "System Lab1"),
            ("Friday", 6, "System Lab1"),
            ("Friday", 1, "System Lab2")
        ]
        cur.executemany("INSERT INTO labs (day, hour, lab_name, is_booked) VALUES (?, ?, ?, 0)", labs_data)
        conn.commit()
    conn.close()

def get_db():
    if DB_PATH != ORIGINAL_DB:
        if not os.path.exists(DB_PATH):
            if os.path.exists(ORIGINAL_DB):
                try:
                    shutil.copyfile(ORIGINAL_DB, DB_PATH)
                except Exception:
                    init_db(DB_PATH)
            else:
                init_db(DB_PATH)
    else:
        if not os.path.exists(ORIGINAL_DB):
            init_db(ORIGINAL_DB)
            
    conn = sqlite3.connect(DB_PATH)
    return conn

# -------------------- LOGIN PAGE --------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("select_time"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

# -------------------- SELECT DAY/TIME PAGE --------------------
@app.route("/select_time", methods=["GET", "POST"])
def select_time():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        day = request.form["day"]
        hour = request.form["hour"]
        return redirect(url_for("labs", day=day, hour=hour))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours = [1, 2, 3, 4, 5, 6]
    return render_template("select_time.html", days=days, hours=hours)

# -------------------- LABS DISPLAY PAGE --------------------
@app.route("/labs/<day>/<hour>")
def labs(day, hour):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM labs WHERE day=? AND hour=?", (day, hour))
    labs_data = cur.fetchall()
    conn.close()

    return render_template("labs.html", labs=labs_data, day=day, hour=hour, user=session["user"])

# -------------------- TOGGLE BOOKING --------------------
@app.route("/toggle_booking/<int:lab_id>/<day>/<hour>", methods=["POST"])
def toggle_booking(lab_id, day, hour):
    if "user" not in session:
        return redirect(url_for("login"))

    current_user = session["user"]

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE labs ADD COLUMN booked_by TEXT")
    except:
        pass

    cur.execute("SELECT is_booked, booked_by FROM labs WHERE id=?", (lab_id,))
    lab = cur.fetchone()

    if not lab:
        flash("Lab not found!", "error")
        conn.close()
        return redirect(url_for("labs", day=day, hour=hour))

    is_booked, booked_by = lab

    # If not booked — allow booking
    if is_booked == 0:
        cur.execute("UPDATE labs SET is_booked=1, booked_by=? WHERE id=?", (current_user, lab_id))
        conn.commit()
        flash("✅ You have successfully booked this lab.", "success")

    # If booked by current user OR if booked_by is missing/Unknown — allow cancellation
    elif booked_by == current_user or not booked_by or booked_by == 'Unknown':
        cur.execute("UPDATE labs SET is_booked=0, booked_by=NULL WHERE id=?", (lab_id,))
        conn.commit()
        flash("❌ Booking has been cancelled.", "info")

    # If booked by someone else — deny action
    else:
        flash("⚠️ You can’t cancel another user’s booking.", "error")

    conn.close()
    return redirect(url_for("labs", day=day, hour=hour))

# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
