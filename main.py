from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Dict, List
import re
import time
import requests

app = FastAPI(title="Agentic Honeypot – Scam Detection System")

# ================= API KEY =================
API_KEY = "honeypot_12345_secure"

# ================= MEMORY =================
conversations: Dict[str, Dict] = {}

# ================= SCAM RULES =================
SCAM_KEYWORDS = [
    "bank", "account", "blocked", "verify",
    "otp", "upi", "click", "link", "urgent",
    "suspended", "immediately"
]

UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
BANK_REGEX = r"\b\d{9,18}\b"
URL_REGEX = r"https?://[^\s]+"
PHONE_REGEX = r"\b[6-9]\d{9}\b"

# ================= REQUEST MODELS =================
class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

class RequestBody(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: List = []
    metadata: Dict = {}

# ================= CORE LOGIC =================
def detect_scam(message: str) -> bool:
    return any(word in message.lower() for word in SCAM_KEYWORDS)

def extract_intelligence(message: str, memory: Dict):
    memory["extracted"]["upiIds"].extend(re.findall(UPI_REGEX, message))
    memory["extracted"]["bankAccounts"].extend(re.findall(BANK_REGEX, message))
    memory["extracted"]["phishingLinks"].extend(re.findall(URL_REGEX, message))
    memory["extracted"]["phoneNumbers"].extend(re.findall(PHONE_REGEX, message))

    for word in SCAM_KEYWORDS:
        if word in message.lower():
            memory["extracted"]["suspiciousKeywords"].add(word)

def agent_reply(turns: int) -> str:
    # Simple multi-turn believable behavior
    replies = [
        "Why is my account being suspended?",
        "I didn’t receive any official message about this.",
        "What happens if I don’t do this now?",
        "Can you explain the process clearly?"
    ]
    return replies[min(turns, len(replies) - 1)]

# ================= GUVI FINAL CALLBACK =================
def send_final_callback(session_id: str, memory: Dict):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": len(memory["messages"]),
        "extractedIntelligence": {
            "bankAccounts": memory["extracted"]["bankAccounts"],
            "upiIds": memory["extracted"]["upiIds"],
            "phishingLinks": memory["extracted"]["phishingLinks"],
            "phoneNumbers": memory["extracted"]["phoneNumbers"],
            "suspiciousKeywords": list(memory["extracted"]["suspiciousKeywords"])
        },
        "agentNotes": "Scammer used urgency, account suspension and payment redirection tactics"
    }

    try:
        requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
    except Exception:
        pass  # Never break main API flow

# ================= ENDPOINT =================
@app.post("/")
@app.post("/message")
def receive_message(
    data: RequestBody,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        return {
            "status": "error",
            "reply": "Invalid API key"
        }

    session_id = data.sessionId
    text = data.message.text

    # Initialize session
    if session_id not in conversations:
        conversations[session_id] = {
            "messages": [],
            "scam_detected": False,
            "start_time": time.time(),
            "callback_sent": False,
            "extracted": {
                "upiIds": [],
                "bankAccounts": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": set()
            }
        }

    memory = conversations[session_id]
    memory["messages"].append(text)

    # Scam detection
    if not memory["scam_detected"]:
        memory["scam_detected"] = detect_scam(text)

    # If scam detected → engage + extract
    if memory["scam_detected"]:
        extract_intelligence(text, memory)
        reply = agent_reply(len(memory["messages"]))

        # Send final callback after enough engagement
        if len(memory["messages"]) >= 4 and not memory["callback_sent"]:
            send_final_callback(session_id, memory)
            memory["callback_sent"] = True
    else:
        reply = "Could you please explain?"

    # ⚠️ Return ONLY what evaluator expects
    return {
        "status": "success",
        "reply": reply
    }
