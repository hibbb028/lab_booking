from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------- LOGIN PAGE --------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lab_booking.db")
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

    conn = sqlite3.connect("lab_booking.db")
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

    conn = sqlite3.connect("lab_booking.db")
    cur = conn.cursor()

    # Ensure booked_by column exists (safe if already added)
    try:
        cur.execute("ALTER TABLE labs ADD COLUMN booked_by TEXT")
    except:
        pass

    # Fetch current booking info
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

    # If booked by current user — allow cancellation
    elif booked_by == current_user:
        cur.execute("UPDATE labs SET is_booked=0, booked_by=NULL WHERE id=?", (lab_id,))
        conn.commit()
        flash("❌ Your booking has been cancelled.", "info")

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

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True)


















