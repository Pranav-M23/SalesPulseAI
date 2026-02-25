# 🚀 SalesPlus AI – Agentic AI for Sales Optimization

SalesPlus AI is an autonomous, AI-powered sales follow-up platform that automates customer engagement across WhatsApp, SMS, Email, and Telegram.  
It uses Large Language Models (LLMs) to classify intent, generate personalized messages, and update lead status in real time.

Built for hackathons and MVP demos with a focus on speed, automation, and scalability.

👥 Team Name: 404 Not Found
Team Members: Pranav M Nair, Adithyan R, Deva Nandan J, Thejas Baiju
Project: SalesPlus AI

Built for  Raizen Hackathon 2026(Agentic AI) at CAPE Engineering College , Muttathara


## 📌 Features

- 🤖 Agentic AI Sales Assistant (Groq Llama 3.1)
- 📱 WhatsApp & SMS Integration (Twilio)
- 📧 Email Delivery (SendGrid)
- 💬 Telegram AI Bot 
- 📊 React Dashboard for Lead Tracking
- 🔄 Real-time Webhook Processing
- 🧠 Stage-Aware Prompt Engineering
- 📈 Funnel Automation (Cold → Closed)
- 📅 Automatic Booking Extraction
- 🗄 SQLite Database (MVP)

---

## 🏗 Tech Stack

### Backend
- FastAPI (Python)
- Groq API (Llama 3.1 – LPU Inference)
- SQLite + aiosqlite
- Twilio API
- SendGrid API

### Frontend
- React
- Tailwind CSS
- Axios

### Automation
- n8n
- Telegram Bot API

---

## 📁 Project Structure
salesplus-ai/
│
├── backend/
│ ├── main.py
│ ├── services/
│ ├── models/
│ ├── schemas/
│ └── api/
│
├── frontend/
│ ├── src/
│ └── public/
│
├── .env.example
└── README.md

⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/salesplus-ai.git
cd salesplus-ai
2️⃣ Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Run backend:

uvicorn main:app --reload
API Docs:

http://localhost:8000/docs
3️⃣ Frontend Setup
cd frontend
npm install
npm run dev
Frontend runs at:

http://localhost:5173
4️⃣ Expose Backend (For Webhooks)
Use ngrok:

ngrok http 8000
Set webhook URLs in Twilio / Telegram to the ngrok URL.

🔄 System Workflow
Lead is created via Dashboard / CSV

AI generates personalized message

Message sent via WhatsApp / Telegram / Email

User reply triggers webhook

AI analyzes intent

Lead status updated

Dashboard refreshed

Booking created (if applicable)

📊 Demo Flow
Open Dashboard

Select Lead

Trigger AI Follow-up

Send message to phone

Show AI reply

Book demo via chat

Status updates automatically

🧠 AI Architecture
Transformer-based LLM (Llama 3.1)

Stage-aware prompt injection

Intent classification

Structured data extraction

LPU-accelerated inference

🚀 Future Roadmap
Bulk CSV lead import

CRM integrations

Voice AI Agents

Revenue prediction

Multi-agent collaboration

Enterprise dashboard

⚠️ Disclaimer
This project was built as an MVP for a hackathon.

Not production hardened

Limited security features

Demo-focused implementation

👥 Team Name: 404 Not Found
Team Members: Pranav M Nair, Adithyan R, Deva Nandan J, Thejas baiju
Project: SalesPlus AI

Built for  Raizen Hackathon 2026 at CAPE Engineering College ,Muttathara


