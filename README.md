🕵️ Agentic Honeypot – AI Scam Detection System
📌 Project Overview

Agentic Honeypot is an AI-powered backend system that detects scam messages and
engages potential scammers using a conversational AI agent.
The system intelligently responds without revealing scam detection, allowing
the extraction of useful intelligence such as UPI IDs, bank numbers, and phishing URLs.

This project is built using FastAPI and integrates an LLM-based agent (Ollama).

🚀 Features

Scam message detection using keywords & regex

Multi-turn conversation memory

API key–based authentication

AI agent–driven automated replies

Intelligence extraction:

UPI IDs

Bank account numbers

Phishing URLs

Interactive Swagger UI for testing

🛠️ Technologies Used

Python

FastAPI

Uvicorn

Pydantic

Regex

Ollama (LLM)

📂 Project Structure
agentic-honeypot/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore

🔐 API Authentication

All API requests require an API Key.

Header Format
Authorization: Bearer honeypot_12345_secure


Swagger UI supports authentication via the Authorize 🔒 button.

📡 API Endpoint
POST /message
Request Headers
Authorization: Bearer honeypot_12345_secure

Request Body
{
  "conversation_id": "conv1",
  "message": "Your bank account is blocked. Share OTP immediately."
}

Response Body
{
  "conversation_id": "conv1",
  "scam_detected": true,
  "agent_engaged": true,
  "engagement_metrics": {
    "turns": 1,
    "duration_seconds": 2
  },
  "extracted_intelligence": {
    "upi_ids": [],
    "bank_accounts": [],
    "phishing_urls": []
  },
  "agent_response": "Could you please explain how this works?"
}

▶️ How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start the FastAPI server
uvicorn main:app --reload

3️⃣ Open Swagger UI
http://127.0.0.1:8000/docs

4️⃣ Authenticate

Click Authorize 🔒 and enter:

Bearer honeypot_12345_secure

🧠 How the System Works

User sends a message to the /message endpoint

Message is checked for scam indicators

If scam is detected:

Conversation memory is activated

Intelligence is extracted using regex

AI agent engages the scammer naturally

Conversation metrics are tracked per session

📈 Future Enhancements

Database integration (MongoDB / PostgreSQL)

Scam confidence scoring

Dashboard for intelligence visualization

Multi-language scam detection

Rate limiting & logging

👩‍💻 Author

Sri Harshitha
B.Tech – Computer Science & Engineering