import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from behavior import get_stage, get_stage_description
from memory import build_chat_history
from memory_gateway import load_memory, save_memory
from relationship import create_relationship_state, update_relationship_state, describe_relationship_state
from user_profile import create_user_profile, normalize_user_profile, update_user_profile, describe_user_profile
from modes import detect_response_mode, describe_response_mode
from facts import extract_facts
from prompt_builder import build_main_prompt

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="i nik Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://inik.lovable.app", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str = "web_demo_user"
    username: str = "traveler"
    message: str

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "i nik agent api",
        "gemini_configured": bool(API_KEY),
    }

@app.post("/api/chat")
def chat(req: ChatRequest):
    user_id = req.user_id or "web_demo_user"
    user_message = req.message.strip()

    memory = load_memory(user_id=user_id)

    user_facts = memory.get("user_facts", {})
    user_profile = normalize_user_profile(memory.get("user_profile", create_user_profile()))
    inventory = memory.get("inventory", [])
    intimacy_score = int(memory.get("intimacy_score", 0) or 0)
    points = int(memory.get("points", 0) or 0)
    relationship_state = memory.get("relationship_state", create_relationship_state())

    messages = memory.get("messages", [])
    messages.append({"role": "user", "content": user_message})

    intimacy_score = min(100, intimacy_score + 10)
    points += 1

    if user_message.startswith(("ฉันชื่อ", "ชื่อฉันคือ", "ฉันชอบ", "ฉันไม่ชอบ")):
        user_facts = extract_facts(user_message, user_facts)

    user_profile = update_user_profile(user_message, user_profile)
    relationship_state = update_relationship_state(user_message, relationship_state)

    stage = get_stage(intimacy_score)
    stage_description = get_stage_description(stage)
    relationship_description = describe_relationship_state(relationship_state)
    user_profile_description = describe_user_profile(user_profile)

    response_mode = detect_response_mode(user_message)
    response_mode_description = describe_response_mode(response_mode)

    chat_history = build_chat_history(messages, limit=10)

    prompt = build_main_prompt(
        stage_description=stage_description,
        relationship_description=relationship_description,
        user_profile_description=user_profile_description,
        response_mode_description=response_mode_description,
        chat_history=chat_history,
        user_facts=user_facts,
        rag_context="",
        user_message=user_message,
        relationship_state=relationship_state,
        days_inactive=0,
        live_data_warning=None,
    )

    if not API_KEY:
        reply = "สัญญาณ Gemini ยังไม่ได้ตั้งค่า GEMINI_API_KEY"
    else:
        try:
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as error:
            reply = f"สัญญาณจากจักรวาลสะดุด: {error}"

    messages.append({"role": "assistant", "content": reply})

    save_memory(
        user_facts,
        user_profile,
        inventory,
        intimacy_score,
        points,
        relationship_state,
        user_id=user_id,
    )

    return {
        "reply": reply,
        "user_id": user_id,
        "state": {
            "stage": stage,
            "intimacy_score": intimacy_score,
            "points": points,
            "relationship_state": relationship_state,
            "user_profile": user_profile,
            "user_facts": user_facts,
        },
    }
