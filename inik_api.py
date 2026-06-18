import os
import re
from dotenv import load_dotenv
load_dotenv()
from google import genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from behavior import get_stage, get_stage_description
from memory import build_chat_history
from memory_gateway import load_memory, save_memory
from memory_gateway_v2 import save_message_memory_v2
from relationship import create_relationship_state, update_relationship_state, describe_relationship_state
from user_profile import create_user_profile, normalize_user_profile, update_user_profile, describe_user_profile
from modes import detect_response_mode, describe_response_mode
from facts import extract_facts
from prompt_builder import build_main_prompt
from agent_router import detect_agent_handoff
from rick_prompt import build_rick_prompt
from rag_prompt import build_safe_rag_context

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL_NAME = "gemini-2.0-flash"

app = FastAPI(title="i nik Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_origins=[
        "https://inik.lovable.app",
        "https://inik-cafe.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_USER_ID_RE = re.compile(r'^[A-Za-z0-9_\-]{1,64}$')
_DEFAULT_USER_ID = "web_demo_user"


def _validate_user_id(user_id: str) -> str:
    if not user_id or user_id == _DEFAULT_USER_ID:
        return _DEFAULT_USER_ID
    if not _USER_ID_RE.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id: use letters, numbers, _ or - (max 64 chars)")
    return user_id


STAGE_ORDER = {"Observer": 0, "Gremlin": 1, "Treasure": 2}


def _resolve_canonical_stage(intimacy_score: int, relationship_state: dict) -> str:
    intimacy_stage = get_stage(intimacy_score)
    rel_stage = (relationship_state or {}).get("relationship_stage", "Observer")
    intimacy_rank = STAGE_ORDER.get(intimacy_stage, 0)
    rel_rank = STAGE_ORDER.get(rel_stage, 0)
    return rel_stage if rel_rank > intimacy_rank else intimacy_stage


class ChatRequest(BaseModel):
    user_id: str = "web_demo_user"
    username: str = "traveler"
    message: str
    agent_mode: str = "inik"

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "i nik agent api",
        "gemini_configured": bool(API_KEY),
    }

@app.post("/api/chat")
def chat(req: ChatRequest):
    user_id = _validate_user_id(req.user_id or _DEFAULT_USER_ID)
    user_message = req.message.strip()

    memory = load_memory(user_id=user_id)

    user_facts = memory.get("user_facts", {})
    user_profile = normalize_user_profile(memory.get("user_profile", create_user_profile()))
    inventory = memory.get("inventory", [])
    intimacy_score = int(memory.get("intimacy_score", 0) or 0)
    points = int(memory.get("points", 0) or 0)
    relationship_state = memory.get("relationship_state", create_relationship_state())

    recent_messages = user_profile.get("recent_messages", [])
    recent_messages.append({"role": "user", "content": user_message})

    intimacy_score = min(100, intimacy_score + 10)
    points += 1

    if user_message.startswith(("ฉันชื่อ", "ชื่อฉันคือ", "ฉันชอบ", "ฉันไม่ชอบ")):
        user_facts = extract_facts(user_message, user_facts)

    user_profile = update_user_profile(user_message, user_profile)
    relationship_state = update_relationship_state(user_message, relationship_state)

    stage = _resolve_canonical_stage(intimacy_score, relationship_state)
    stage_description = get_stage_description(stage)
    relationship_description = describe_relationship_state(relationship_state)
    user_profile_description = describe_user_profile(user_profile)

    response_mode = detect_response_mode(user_message)
    response_mode_description = describe_response_mode(response_mode)

    chat_history = build_chat_history(recent_messages, limit=10)

    rag_context = build_safe_rag_context(
        user_id=user_id,
        user_message=user_message,
        limit=5,
    )

    agent_mode = (req.agent_mode or "inik").strip().lower()

    try:
        save_message_memory_v2(
            user_id=user_id,
            message=user_message,
            source="chat",
            metadata={
                "agent_mode": agent_mode,
                "route": "api_chat",
            },
        )
    except Exception as error:
        print(f"[memory_v2] save failed: {error}")

    handoff_suggestion = detect_agent_handoff(user_message)

    if agent_mode == "rick_royce":
        prompt = build_rick_prompt(
            user_profile_description=user_profile_description,
            chat_history=chat_history,
            user_facts=user_facts,
            rag_context=rag_context,
            user_message=user_message,
        )
    else:
        prompt = build_main_prompt(
            stage_description=stage_description,
            relationship_description=relationship_description,
            user_profile_description=user_profile_description,
            response_mode_description=response_mode_description,
            chat_history=chat_history,
            user_facts=user_facts,
            rag_context=rag_context,
            user_message=user_message,
            relationship_state=relationship_state,
            days_inactive=0,
            live_data_warning=None,
            user_profile=user_profile,
        )

    if agent_mode != "rick_royce" and handoff_suggestion:
        reply = handoff_suggestion.message
    elif not API_KEY:
        reply = "สัญญาณ Gemini ยังไม่ได้ตั้งค่า GEMINI_API_KEY"
    else:
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            reply = response.text
        except Exception as error:
            reply = f"สัญญาณจากจักรวาลสะดุด: {error}"

    recent_messages.append({"role": "assistant", "content": reply})
    recent_messages = recent_messages[-20:]
    user_profile["recent_messages"] = recent_messages

    save_memory(
        user_facts,
        user_profile,
        inventory,
        intimacy_score,
        points,
        relationship_state,
        user_id=user_id,
    )

    suggested_agent = None
    if agent_mode != "rick_royce" and handoff_suggestion:
        suggested_agent = {
            "agent": handoff_suggestion.suggested_agent,
            "confidence": handoff_suggestion.confidence,
            "reason": handoff_suggestion.reason,
            "message": handoff_suggestion.message,
        }

    return {
        "reply": reply,
        "user_id": user_id,
        "agent_mode": agent_mode,
        "suggested_agent": suggested_agent,
        "state": {
            "stage": stage,
            "intimacy_score": intimacy_score,
            "points": points,
            "relationship_state": relationship_state,
            "user_profile": user_profile,
            "user_facts": user_facts,
            "recent_messages": recent_messages,
        },
    }


@app.get("/api/state")
def get_state(user_id: str = "web_demo_user"):
    user_id = _validate_user_id(user_id)
    memory = load_memory(user_id=user_id)

    user_facts = memory.get("user_facts", {})
    user_profile = normalize_user_profile(memory.get("user_profile", create_user_profile()))
    intimacy_score = int(memory.get("intimacy_score", 0) or 0)
    points = int(memory.get("points", 0) or 0)
    relationship_state = memory.get("relationship_state", create_relationship_state())
    recent_messages = user_profile.get("recent_messages", [])

    stage = _resolve_canonical_stage(intimacy_score, relationship_state)

    return {
        "user_id": user_id,
        "stage": stage,
        "intimacy_score": intimacy_score,
        "points": points,
        "relationship_state": relationship_state,
        "user_profile": user_profile,
        "user_facts": user_facts,
        "recent_messages": recent_messages,
    }
