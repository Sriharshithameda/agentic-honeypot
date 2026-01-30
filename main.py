from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict
import re
import time

app = FastAPI(
    title="Agentic Honeypot – AI Scam Detection System"
)

# ================= API KEY =================
API_KEY = "honeypot_12345_secure"
api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

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

# ================= MODEL =================
class ScamMessage(BaseModel):
    conversation_id: str
    message: str

# ================= LOGIC =================
def detect_scam(message: str) -> bool:
    return any(word in message.lower() for word in SCAM_KEYWORDS)

def extract_intelligence(message: str, memory: Dict):
    memory["extracted"]["upi_ids"].extend(re.findall(UPI_REGEX, message))
    memory["extracted"]["bank_accounts"].extend(re.findall(BANK_REGEX, message))
    memory["extracted"]["phishing_urls"].extend(re.findall(URL_REGEX, message))

def agent_reply():
    # SAFE fallback (Render-compatible)
    return "Could you please explain more about this offer?"

# ================= ENDPOINT =================
@app.post("/message", dependencies=[Depends(verify_api_key)])
def receive_message(data: ScamMessage):

    if data.conversation_id not in conversations:
        conversations[data.conversation_id] = {
            "messages": [],
            "scam_detected": False,
            "start_time": time.time(),
            "extracted": {
                "upi_ids": [],
                "bank_accounts": [],
                "phishing_urls": []
            }
        }

    memory = conversations[data.conversation_id]
    memory["messages"].append(data.message)

    if not memory["scam_detected"]:
        memory["scam_detected"] = detect_scam(data.message)

    if memory["scam_detected"]:
        extract_intelligence(data.message, memory)
        reply = agent_reply()
    else:
        reply = "Could you please explain?"

    return {
        "conversation_id": data.conversation_id,
        "scam_detected": memory["scam_detected"],
        "agent_engaged": memory["scam_detected"],
        "engagement_metrics": {
            "turns": len(memory["messages"]),
            "duration_seconds": int(time.time() - memory["start_time"])
        },
        "extracted_intelligence": memory["extracted"],
        "agent_response": reply
    }
