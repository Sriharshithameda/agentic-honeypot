from fastapi import FastAPI, Header, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict
from fastapi import Depends
import re
import time
import ollama

app = FastAPI()

API_KEY = "honeypot_12345_secure"
api_key_header = APIKeyHeader(name="Authorization")


# -------- In-memory store --------
conversations: Dict[str, Dict] = {}

# -------- Scam indicators --------
SCAM_KEYWORDS = [
    "bank", "account", "blocked", "verify",
    "otp", "upi", "click", "link", "urgent"
]

UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
BANK_REGEX = r"\b\d{9,18}\b"
URL_REGEX = r"https?://[^\s]+"

# -------- Request Model --------
class ScamMessage(BaseModel):
    conversation_id: str
    message: str

# -------- Detection Logic --------
def detect_scam(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in SCAM_KEYWORDS)

def extract_intelligence(message: str, memory: Dict):
    memory["extracted"]["upi_ids"].extend(re.findall(UPI_REGEX, message))
    memory["extracted"]["bank_accounts"].extend(re.findall(BANK_REGEX, message))
    memory["extracted"]["phishing_urls"].extend(re.findall(URL_REGEX, message))

def agent_reply(conversation: list) -> str:
    system_prompt = """
You are a normal person chatting with a customer support agent.
You do NOT know this is a scam.
You are slightly confused but cooperative.
Never accuse or warn.
Keep replies short and natural.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation:
        messages.append({"role": "user", "content": msg})

    response = ollama.chat(
        model="llama3",
        messages=messages
    )

    return response["message"]["content"]

# -------- API Endpoint --------
@app.post("/message")
def receive_message(
    data: ScamMessage,
    authorization: str = Depends(api_key_header)
):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")


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
        reply = agent_reply(memory["messages"])
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
