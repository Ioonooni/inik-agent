from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="i nik Agent API")

class ChatRequest(BaseModel):
    user_id: str = "web_demo_user"
    username: str = "traveler"
    message: str

@app.get("/health")
def health():
    return {"ok": True, "service": "i nik api"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    return {
        "reply": f"i nik ได้ยินแล้ว: {req.message}",
        "user_id": req.user_id,
        "username": req.username,
    }
