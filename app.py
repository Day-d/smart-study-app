from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database Helper
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    # Task အသစ်ထည့်မယ်
    if request.method == "POST":
        title = request.form.get("title")
        due_date = request.form.get("due_date")
        if title and due_date:
            conn.execute("INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)", 
                         (title, due_date, 'Pending'))
            conn.commit()
    
    # Tasks တွေကို စီမယ်
    tasks = conn.execute("SELECT * FROM tasks ORDER BY due_date ASC").fetchall()
    
    # AI Assistant Reminder Logic (3 ရက်အတွင်း)
    today = datetime.now().date()
    reminders = []
    for task in tasks:
        if task['status'] == 'Pending':
            try:
                due = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                days_left = (due - today).days
                if 0 <= days_left <= 3:
                    reminders.append(f"AI Assistant: '{task['title']}' အတွက် {days_left} ရက်ပဲလိုတော့တယ်နော်။ စာလုပ်ဖို့ အချိန်တန်ပြီ!")
            except:
                continue
    
    conn.close()
    return render_template("index.html", tasks=tasks, reminders=reminders)

@app.route("/done/<int:id>")
def mark_done(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    conn = sqlite3.connect("database.db")
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, due_date TEXT, status TEXT)")
    conn.close()
    app.run(debug=True)