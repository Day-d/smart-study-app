import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY, title TEXT, due_date TEXT, status TEXT)"
    )

    cols = [r["name"] for r in conn.execute("PRAGMA table_info(tasks)")]
    if "subject" not in cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN subject TEXT DEFAULT 'General'")
        conn.execute("UPDATE tasks SET subject='General' WHERE subject IS NULL")
    conn.commit()
    conn.close()


init_db()  


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        due_date = request.form.get("due_date")
        subject = (request.form.get("subject") or "").strip() or "General"
        if title and due_date:
            conn.execute(
                "INSERT INTO tasks (title, due_date, status, subject) VALUES (?, ?, ?, ?)",
                (title, due_date, "Pending", subject),
            )
            conn.commit()
        conn.close()
        
        return redirect(url_for("index", subject=request.args.get("subject") or None))

    current_subject = request.args.get("subject")

    if current_subject:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE subject=? ORDER BY status DESC, due_date ASC",
            (current_subject,),
        ).fetchall()
    else:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY status DESC, due_date ASC"
        ).fetchall()

    subjects = conn.execute(
        "SELECT subject, COUNT(*) AS cnt FROM tasks GROUP BY subject ORDER BY subject"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    
    today = datetime.now().date()
    reminders = []
    for t in conn.execute("SELECT * FROM tasks WHERE status='Pending' ORDER BY due_date"):
        try:
            due = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        days_left = (due - today).days
        if days_left < 0:
            reminders.append(f"{t['title']}' ရက်လွန်နေတာ ({-days_left} ရက်)ရှိပါပြီ!")
        elif days_left <= 3:
            reminders.append(
                f"Rule-based reminder assistant: '{t['title']}' အတွက် {days_left} ရက်ပဲလိုတော့တယ်နော်။ စာလုပ်ဖို့ အချိန်တန်ပြီ!"
            )

    conn.close()
    return render_template(
        "index.html",
        tasks=tasks,
        reminders=reminders,
        subjects=subjects,
        total=total,
        current_subject=current_subject,
    )


@app.route("/done/<int:id>", methods=["POST"])
def mark_done(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))


@app.route("/undo/<int:id>", methods=["POST"])
def mark_pending(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Pending' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    conn = get_db()
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        due_date = request.form.get("due_date")
        subject = (request.form.get("subject") or "").strip() or "General"
        if title and due_date:
            conn.execute(
                "UPDATE tasks SET title=?, due_date=?, subject=? WHERE id=?",
                (title, due_date, subject, id),
            )
            conn.commit()
        conn.close()
        return redirect(url_for("index"))

    task = conn.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()
    subjects = conn.execute("SELECT DISTINCT subject FROM tasks").fetchall()
    conn.close()
    if task is None:
        return redirect(url_for("index"))
    return render_template("edit.html", task=task, subjects=subjects)


if __name__ == "__main__":
    app.run()