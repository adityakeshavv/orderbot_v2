# OrderBot — AI-Powered Supply Chain Assistant

An intelligent order management chatbot built for **Tata Steel** as part of a KIIT University internship project.

Customers can place orders, track shipments, request expedited delivery, swap products, and cancel orders — all through natural conversation powered by **GPT-4o**.

---

## Demo

![OrderBot Chat](https://via.placeholder.com/800x400?text=OrderBot+Chat+Interface)

**Demo credentials**
| Email | Password |
|---|---|
| rajesh@tatasteel.in | Test1234 |
| anita@tatasteel.in | Test1234 |
| suresh@tatasteel.in | Test1234 |

---

## How It Works

User message
↓
FastAPI backend receives it
↓
LLM Agent (GPT-4o) reasons about what to do
↓
If info needed → asks user one question at a time
If ready       → calls a Tool (place_order, cancel_order, etc.)
↓
Tool executes against PostgreSQL database
↓
GPT-4o formats the result
↓
Response streams back word-by-word (like ChatGPT)

The LLM **never** touches the database directly.
Tools are the only way real actions happen — the LLM just decides which tool to call and when.

---

## Features

| Feature | Description |
|---|---|
| 🤖 LLM Agent | GPT-4o drives the conversation — understands natural language, asks for missing info, confirms before acting |
| ⚡ Streaming | Responses stream word-by-word using Server-Sent Events |
| 📦 Place Order | Collects product, quantity, delivery date — confirms before placing |
| 🔍 Track Order | Instant order status lookup |
| 📋 My Orders | Lists all customer orders |
| ❌ Cancel Order | Cancels with confirmation |
| 🚀 Speed Up | Submits expedite request + emails CAM |
| 🔄 Swap | Submits swap request + emails CAM |
| 💬 Chat History | All conversations saved, grouped by Today/Yesterday/Earlier |
| 🔐 Auth | JWT login/register with bcrypt passwords |
| 📱 React UI | Clean dark-mode three-panel layout |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| Migrations | Alembic |
| LLM | OpenAI GPT-4o |
| Auth | JWT + bcrypt |
| Streaming | Server-Sent Events (SSE) |
| Email | SMTP (Gmail) |

---

## Project Structure
orderbot/
├── app/
│   ├── main.py          ← FastAPI routes (auth, sessions, chat, orders)
│   ├── agent.py         ← LLM agent — GPT-4o + tool calling
│   ├── tools.py         ← Tools the agent can call (place_order, cancel, etc.)
│   ├── models.py        ← SQLAlchemy database models
│   ├── crud.py          ← All database operations
│   ├── auth.py          ← JWT + bcrypt authentication
│   ├── database.py      ← SQLAlchemy engine + session
│   ├── email_utils.py   ← SMTP email for CAM notifications
│   └── seed.py          ← Demo data seeder
├── alembic/             ← Database migrations
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── LoginPage.jsx
│       │   └── ChatPage.jsx
│       ├── hooks/
│       │   └── useAuth.jsx
│       └── utils/
│           └── api.js
├── .env.example
├── requirements.txt
└── README.md

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- OpenAI API key

---

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/orderbot.git
cd orderbot
```

### 2. Backend setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost/orderbot
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key-here
OPENAI_MODEL=gpt-4o
EMAIL_ENABLED=false
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Create database

In pgAdmin or psql:
```sql
CREATE DATABASE orderbot;
```

### 5. Run migrations and seed

```bash
alembic upgrade head
python -m app.seed
```

### 6. Start backend

```bash
uvicorn app.main:app --reload
```

API running at `http://localhost:8000`
Docs at `http://localhost:8000/docs`

### 7. Start frontend

```bash
cd frontend
npm install
npm run dev
```

App running at `http://localhost:5173`

---

## Email Setup (optional)

To enable CAM email notifications for speed-up and swap requests:

1. Enable 2-Step Verification on your Gmail account
2. Go to Google Account → Security → App passwords
3. Create an app password named "OrderBot"
4. Update `.env`:

```env
EMAIL_ENABLED=true
SMTP_USERNAME=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
CAM_EMAIL=cam@yourcompany.com
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register new account |
| POST | /auth/login | Login → JWT token |
| GET | /auth/me | Current user info |
| POST | /sessions | Create new chat session |
| GET | /sessions | List all sessions |
| GET | /sessions/{id} | Get session with messages |
| DELETE | /sessions/{id} | Delete session |
| PATCH | /sessions/{id} | Rename session |
| POST | /chat | Send message (SSE streaming) |
| GET | /orders | List my orders |
| GET | /health | Health check |

---

## Agent Architecture
┌─────────────────────────────────────────┐
│              GPT-4o Agent               │
│                                         │
│  Receives: message + conversation       │
│            history + tool definitions   │
│                                         │
│  Decides:  ask for more info            │
│         or call a tool                  │
│         or respond directly             │
└──────────────────┬──────────────────────┘
│ tool call
▼
┌─────────────────────────────────────────┐
│                 Tools                   │
│                                         │
│  place_order    → writes to database    │
│  track_order    → reads from database   │
│  list_orders    → reads from database   │
│  cancel_order   → updates database      │
│  speed_up_order → DB write + email      │
│  swap_order     → DB write + email      │
└──────────────────┬──────────────────────┘
│
▼
PostgreSQL Database

---

## Built By

**Aditya** — KIIT University (2306176@kiit.ac.in)
Internship Project — Tata Steel
