# 💊 Medication Management Tool (MMT)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas%2FLocal-green?logo=mongodb)](https://mongodb.com)

> Smart medication reminder system — reduces the 80M+ non-adherent patients in India by sending automated email reminders via Gmail SMTP at scheduled times.

**Research Paper**: VIT Vellore — Abhishek

---

## 📁 Project Structure

```
MMT/
├── app.py                   ← Flask backend (API + Email + Scheduler)
├── requirements.txt
├── .env                     ← Add your credentials here
├── templates/
│   └── index.html           ← Full frontend UI
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## ⚡ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure `.env`
```env
MONGO_URI=mongodb://localhost:27017/mmt_db
MAIL_USER=your_gmail@gmail.com
MAIL_PASS=your_16_char_app_password
```

> **Gmail App Password** (required — NOT your Gmail login password):
> `Gmail → Settings → Security → 2-Step Verification → App Passwords → Generate`

### 3. Start MongoDB
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas free cluster — paste the URI in .env
```

### 4. Run
```bash
python app.py
```
Open → **http://localhost:5000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`    | `/api/medications`               | List all medications |
| `POST`   | `/api/medications`               | Add new + send confirmation email |
| `PATCH`  | `/api/medications/<name>/taken`  | Mark as taken |
| `DELETE` | `/api/medications/<name>`        | Delete record |
| `GET`    | `/api/stats`                     | Adherence stats |

---

## 📬 How Reminders Work

1. **On add** → instant confirmation email with medication details
2. **APScheduler** → runs every 1 minute, checks `time == HH:MM now`
3. If match found and `taken == False` → sends reminder email via Gmail SMTP
4. User clicks **Mark taken** on dashboard → `taken = True`, stops further reminders

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS |
| Backend | Python 3, Flask |
| Database | MongoDB (PyMongo) |
| Email | Flask-Mail + Gmail SMTP |
| Scheduler | APScheduler (1-min interval) |
| API Testing | Postman |
