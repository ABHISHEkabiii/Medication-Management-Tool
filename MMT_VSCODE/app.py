"""
Medication Management Tool — Flask Backend
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── MongoDB ──────────────────────────────────────────────
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mmt_db")
mongo = PyMongo(app)

# ── Flask-Mail (Gmail SMTP) ──────────────────────────────
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("MAIL_USER"),
    MAIL_PASSWORD=os.getenv("MAIL_PASS"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_USER"),
)
mail = Mail(app)

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def send_email(subject, recipient, html_body):
    try:
        msg = Message(subject=subject, recipients=[recipient], html=html_body)
        mail.send(msg)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


def confirmation_html(name, medicine, dosage, time, frequency):
    return f"""
    <div style="font-family:Georgia,serif;max-width:500px;margin:auto;background:#0f172a;
                color:#e2e8f0;padding:40px;border-radius:16px;border:1px solid #1e3a5f">
      <h2 style="color:#38bdf8;margin:0 0 8px;font-size:22px">Reminder Confirmed ✅</h2>
      <p style="color:#94a3b8;margin:0 0 24px;font-size:14px">Medication Management Tool</p>
      <p>Hi <strong>{name}</strong>, your reminder has been saved:</p>
      <table style="width:100%;margin:20px 0;border-collapse:collapse;font-size:14px">
        <tr><td style="padding:10px 12px;color:#94a3b8;border-bottom:1px solid #1e293b">Medicine</td>
            <td style="padding:10px 12px;color:#f1f5f9;border-bottom:1px solid #1e293b"><strong>{medicine}</strong></td></tr>
        <tr><td style="padding:10px 12px;color:#94a3b8;border-bottom:1px solid #1e293b">Dosage</td>
            <td style="padding:10px 12px;color:#f1f5f9;border-bottom:1px solid #1e293b">{dosage}</td></tr>
        <tr><td style="padding:10px 12px;color:#94a3b8;border-bottom:1px solid #1e293b">Time</td>
            <td style="padding:10px 12px;color:#38bdf8;border-bottom:1px solid #1e293b"><strong>{time}</strong></td></tr>
        <tr><td style="padding:10px 12px;color:#94a3b8">Frequency</td>
            <td style="padding:10px 12px;color:#f1f5f9">{frequency}</td></tr>
      </table>
      <p style="color:#64748b;font-size:12px;margin:0">You will receive reminders at your scheduled time. Stay healthy!</p>
    </div>"""


def reminder_html(name, medicine, dosage, time):
    return f"""
    <div style="font-family:Georgia,serif;max-width:500px;margin:auto;background:#0f172a;
                color:#e2e8f0;padding:40px;border-radius:16px;border:1px solid #78350f">
      <h2 style="color:#f59e0b;margin:0 0 8px;font-size:22px">⏰ Time for your medication</h2>
      <p style="color:#94a3b8;margin:0 0 24px;font-size:14px">Medication Management Tool</p>
      <p>Hi <strong>{name}</strong>,</p>
      <div style="background:#1e293b;border-left:4px solid #38bdf8;padding:16px 20px;
                  border-radius:8px;margin:20px 0">
        <p style="margin:0 0 4px;font-size:20px;color:#f1f5f9"><strong>{medicine}</strong></p>
        <p style="margin:0;color:#94a3b8;font-size:14px">{dosage} · Scheduled: {time}</p>
      </div>
      <p style="color:#64748b;font-size:12px;margin:0">Please take your medication and mark it as taken in the dashboard.</p>
    </div>"""


# ─────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hero")
def hero_landing():
    return render_template("hero-landing.html")


@app.route("/api/medications", methods=["GET"])
def get_medications():
    try:
        meds = list(mongo.db.medications.find({}, {"_id": 0}))
        return jsonify(meds)
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return jsonify({"error": "Database connection failed. Please check MongoDB."}), 503


@app.route("/api/medications", methods=["POST"])
def add_medication():
    d = request.json or {}
    required = ["name", "email", "medicine", "dosage", "time", "frequency"]
    if not all(k in d and d[k] for k in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        # Check duplicate
        if mongo.db.medications.find_one({"email": d["email"], "medicine": d["medicine"], "_id": {"$exists": True}}):
            pass  # allow duplicates with different times

        record = {**d, "taken": False, "taken_at": None,
                  "created_at": datetime.now().isoformat()}
        mongo.db.medications.insert_one(record)

        send_email(
            f"✅ Reminder Set — {d['medicine']}",
            d["email"],
            confirmation_html(d["name"], d["medicine"], d["dosage"], d["time"], d["frequency"])
        )

        return jsonify({"message": "Medication added & confirmation email sent"}), 201
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return jsonify({"error": "Database connection failed. Please check MongoDB."}), 503


@app.route("/api/medications/<path:medicine>/taken", methods=["PATCH"])
def mark_taken(medicine):
    try:
        res = mongo.db.medications.update_one(
            {"medicine": medicine, "taken": False},
            {"$set": {"taken": True, "taken_at": datetime.now().isoformat()}}
        )
        if res.modified_count:
            return jsonify({"message": "Marked as taken ✅"})
        return jsonify({"error": "Not found or already taken"}), 404
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return jsonify({"error": "Database connection failed. Please check MongoDB."}), 503


@app.route("/api/medications/<path:medicine>", methods=["DELETE"])
def delete_medication(medicine):
    try:
        mongo.db.medications.delete_one({"medicine": medicine})
        return jsonify({"message": "Deleted"})
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return jsonify({"error": "Database connection failed. Please check MongoDB."}), 503


@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        total  = mongo.db.medications.count_documents({})
        taken  = mongo.db.medications.count_documents({"taken": True})
        missed = total - taken
        rate   = round((taken / total * 100), 1) if total else 0
        return jsonify({"total": total, "taken": taken, "missed": missed, "adherence": rate})
    except Exception as e:
        print(f"[DB ERROR] {e}")
        # Return empty stats if DB unavailable
        return jsonify({"total": 0, "taken": 0, "missed": 0, "adherence": 0}), 200


# ─────────────────────────────────────────────────────────
# SCHEDULER — runs every minute, sends reminders
# ─────────────────────────────────────────────────────────

def send_reminders():
    now = datetime.now().strftime("%H:%M")
    with app.app_context():
        try:
            pending = mongo.db.medications.find({"time": now, "taken": False})
            for med in pending:
                send_email(
                    f"⏰ Time to take {med['medicine']} — MMT",
                    med["email"],
                    reminder_html(med["name"], med["medicine"], med["dosage"], med["time"])
                )
                print(f"[REMINDER] Sent to {med['email']} for {med['medicine']} at {now}")
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, "interval", minutes=1)
scheduler.start()

if __name__ == "__main__":
    print("🚀 MMT running at http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
