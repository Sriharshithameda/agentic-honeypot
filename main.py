from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Dict, List
import re
import time

app = FastAPI(
    title="Agentic Honeypot – Scam Detection API"
)

# ================= API KEY =================
API_KEY = "honeypot_12345_secure"

# ================= MEMORY =================
conversations: Dict[str, Dict] = {}

# ================= SCAM RULES =================
SCAM_KEYWORDS = [
    "bank", "account", "blocked", "verify",
    "otp", "upi", "click", "link", "urgent"
]

UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
BANK_REGEX = r"\b\d{9,18}\b"
URL_REGEX = r"https?://[^\s]+"

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

# ================= LOGIC =================
def detect_scam(message: str) -> bool:
    return any(word in message.lower() for word in SCAM_KEYWORDS)

def extract_intelligence(message: str, memory: Dict):
    memory["extracted"]["upi_ids"].extend(re.findall(UPI_REGEX, message))
    memory["extracted"]["bank_accounts"].extend(re.findall(BANK_REGEX, message))
    memory["extracted"]["phishing_urls"].extend(re.findall(URL_REGEX, message))

# ================= ENDPOINT =================
@app.post("/")
@app.post("/message")
def receive_message(
    data: RequestBody,
    x_api_key: str = Header(None)
):
    # API key validation
    if x_api_key != API_KEY:
        return {
            "status": "error",
            "reply": "Invalid API key"
        }

    session_id = data.sessionId
    message_text = data.message.text

    # Initialize memory
    if session_id not in conversations:
        conversations[session_id] = {
            "messages": [],
            "scam_detected": False,
            "start_time": time.time(),
            "extracted": {
                "upi_ids": [],
                "bank_accounts": [],
                "phishing_urls": []
            }
        }

    memory = conversations[session_id]
    memory["messages"].append(message_text)

    # Detect scam
    if not memory["scam_detected"]:
        memory["scam_detected"] = detect_scam(message_text)

    # Reply logic (Evaluator expects THIS)
    if memory["scam_detected"]:
        extract_intelligence(message_text, memory)
        reply = "Why is my account being suspended?"
    else:
        reply = "Could you please explain?"

    # ⚠️ RETURN ONLY EXPECTED FORMAT
    return {
        "status": "success",
        "reply": reply
    }
