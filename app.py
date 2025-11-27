from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "voice_of_vjm_secret"

# Admin password hash
ADMIN_PASS_HASH = generate_password_hash("prakash123@")


def db():
    conn = sqlite3.connect("data/reports.db")
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            status TEXT DEFAULT 'பெறப்பட்டது',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/report", methods=["GET","POST"])
def report():
    if request.method == "POST":
        cat = request.form["category"]
        desc = request.form["description"]

        conn = db()
        conn.execute("INSERT INTO reports(category, description) VALUES(?,?)",
                     (cat, desc))
        conn.commit()
        conn.close()
        return redirect("/thanks")
    return render_template("report.html")


@app.route("/thanks")
def thanks():
    return "<h2>🙏 நன்றி! உங்கள் தகவல் பதிவானது.</h2>"


## ADMIN ###########################

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form["password"]
        if check_password_hash(ADMIN_PASS_HASH, pwd):
            session["admin"] = True
            return redirect("/admin_panel")
        return "🔐 Wrong password"
    return render_template("admin_login.html")


@app.route("/admin_panel")
def admin_panel():
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return render_template("admin_panel.html", data=data)


@app.route("/update/<int:id>/<status>")
def update(id, status):
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    conn.execute("UPDATE reports SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    return redirect("/admin_panel")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


if __name__ == "__main__":
    init()
    app.run(debug=True)
