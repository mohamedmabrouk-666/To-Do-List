# app.py - Todo List Application
# Database: SQLite (creates todo.db automatically, zero setup)
# Notifications: Gmail SMTP email for overdue tasks
# Scheduler: Checks every 1 minute for overdue tasks

import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# ── App & Config ──────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"   # auto-created file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me-in-production"
app.config["SCHEDULER_API_ENABLED"] = False

# Read email settings from .env (app works without them, just no emails)
MAIL_USER = os.getenv("MAIL_USERNAME", "")
MAIL_PASS = os.getenv("MAIL_PASSWORD", "")
NOTIFY_TO = os.getenv("NOTIFY_EMAIL", "")

# ── Database Model ────────────────────────────────────────────────────────────

db = SQLAlchemy(app)

class Task(db.Model):
    """One row = one todo task."""
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    deadline   = db.Column(db.DateTime, nullable=True)    # optional
    notified   = db.Column(db.Boolean, default=False)     # True after email sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "title":      self.title,
            "deadline":   self.deadline.strftime("%Y-%m-%dT%H:%M") if self.deadline else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
        }

# Create tables on startup (safe to run multiple times)
with app.app_context():
    db.create_all()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "Title is required"}), 400

    deadline = None
    if data.get("deadline"):
        try:
            deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M")
        except ValueError:
            return jsonify({"error": "Invalid deadline format"}), 400

    task = Task(title=data["title"].strip(), deadline=deadline)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

# ── Email Helper ──────────────────────────────────────────────────────────────

def send_overdue_email(title, deadline):
    """Send a plain text email for one overdue task via Gmail."""
    msg = MIMEText(
        f'Your task "{title}" was due on '
        f'{deadline.strftime("%Y-%m-%d %H:%M")} and is still not done.\n\n'
        f'Open your todo list to take action.'
    )
    msg["Subject"] = f"Overdue Task: {title}"
    msg["From"]    = MAIL_USER
    msg["To"]      = NOTIFY_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(MAIL_USER, MAIL_PASS)
        s.sendmail(MAIL_USER, NOTIFY_TO, msg.as_string())

# ── Scheduler ─────────────────────────────────────────────────────────────────

def check_overdue_tasks():
    """Find overdue tasks and send one email per task (runs every 1 minute)."""
    with app.app_context():
        now     = datetime.utcnow()
        overdue = Task.query.filter(
            Task.deadline != None,
            Task.deadline < now,
            Task.notified == False
        ).all()

        for task in overdue:
            if MAIL_USER and NOTIFY_TO:
                try:
                    send_overdue_email(task.title, task.deadline)
                    print(f"[Notifier] Email sent for: {task.title}")
                except Exception as e:
                    print(f"[Notifier] Email error: {e}")

            task.notified = True   # mark done even if email failed
            db.session.commit()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job(
    id="check_overdue",
    func=check_overdue_tasks,
    trigger="interval",
    minutes=1
)
scheduler.start()

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)