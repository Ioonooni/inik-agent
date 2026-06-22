from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentHandoffSuggestion:
    suggested_agent: str
    confidence: float
    reason: str
    message: str


@dataclass
class AgentRouteDecision:
    agent_mode: str
    confidence: float
    reason: str


RICK_KEYWORDS = {
    "investment": [
        "หุ้น", "ลงทุน", "ซื้อหุ้น", "ขายหุ้น", "พอร์ต", "asset", "stock",
        "asml", "nvda", "tesla", "btc", "bitcoin", "กองทุน", "ผลตอบแทน",
        "capital", "moat", "valuation", "เงินลงทุน", "เงินเก็บ",
    ],
    "career": [
        "ลาออก", "เปลี่ยนงาน", "สมัครงาน", "career", "resume", "portfolio",
        "เงินเดือน", "งานไหนดี", "สายงาน", "ฝึกงาน", "internship", "เรียนต่อ",
    ],
    "business": [
        "ธุรกิจ", "startup", "สตาร์ทอัพ", "ลูกค้า", "รายได้", "กำไร",
        "business model", "pricing", "ตลาด", "คู่แข่ง", "product market fit",
    ],
    "strategy": [
        "กลยุทธ์", "คุ้มไหม", "ควรทำไหม", "เลือกทางไหนดี", "ตัดสินใจ",
        "tradeoff", "opportunity cost", "ความเสี่ยง", "risk", "แผนระยะยาว",
        "ทางเลือก", "จัดสรร", "prioritize", "priority",
    ],
}

EMOTIONAL_KEYWORDS = [
    "เหนื่อย", "เศร้า", "เครียด", "ร้องไห้", "ไม่ไหว", "พัง", "ท้อ",
    "เหงา", "กลัว", "กังวล", "เสียใจ", "หมดไฟ", "burnout", "อยากระบาย",
    "ปลอบ", "ฟังหน่อย",
]


def _score_keyword_groups(text: str, groups: dict[str, list[str]]) -> tuple[Optional[str], int]:
    matched_reason = None
    matched_count = 0

    for reason, keywords in groups.items():
        count = sum(1 for keyword in keywords if keyword.lower() in text)
        if count > matched_count:
            matched_count = count
            matched_reason = reason

    return matched_reason, matched_count


def classify_agent_route(user_message: str, requested_mode: str = "auto") -> AgentRouteDecision:
    text = (user_message or "").strip().lower()
    requested = (requested_mode or "auto").strip().lower()

    if requested in ("inik", "rick_royce", "hybrid"):
        return AgentRouteDecision(
            agent_mode=requested,
            confidence=1.0,
            reason="explicit_user_selected_mode",
        )

    if not text:
        return AgentRouteDecision(agent_mode="inik", confidence=0.5, reason="empty_message")

    rick_reason, rick_count = _score_keyword_groups(text, RICK_KEYWORDS)
    emotional_count = sum(1 for keyword in EMOTIONAL_KEYWORDS if keyword.lower() in text)

    if rick_count > 0 and emotional_count > 0:
        confidence = min(0.95, 0.76 + (rick_count * 0.05) + (emotional_count * 0.04))
        return AgentRouteDecision(
            agent_mode="hybrid",
            confidence=round(confidence, 2),
            reason=f"mixed_emotional_and_{rick_reason or 'strategic'}",
        )

    if rick_count > 0:
        confidence = min(0.95, 0.72 + (rick_count * 0.08))
        return AgentRouteDecision(
            agent_mode="rick_royce",
            confidence=round(confidence, 2),
            reason=rick_reason or "strategic",
        )

    return AgentRouteDecision(agent_mode="inik", confidence=0.72, reason="default_companion")


def detect_agent_handoff(user_message: str) -> Optional[AgentHandoffSuggestion]:
    decision = classify_agent_route(user_message, requested_mode="auto")

    if decision.agent_mode not in ("rick_royce", "hybrid"):
        return None

    reason_label = {
        "investment": "investment / capital allocation",
        "career": "career decision",
        "business": "business strategy",
        "strategy": "strategic decision",
    }.get(decision.reason.replace("mixed_emotional_and_", ""), decision.reason)

    if decision.agent_mode == "hybrid":
        message = (
            "เรื่องนี้มีทั้งน้ำหนักทางใจและการตัดสินใจเชิงกลยุทธ์ "
            "i nik จะช่วยจับอารมณ์ ส่วน Rick Royce จะช่วยดู tradeoffs ความเสี่ยง "
            "และต้นทุนทางเลือก"
        )
    else:
        message = (
            "เรื่องนี้ i nik คิดได้ระดับหนึ่งนะ แต่ถ้าเป็นเรื่อง "
            f"{reason_label} Rick Royce น่าจะมองความเสี่ยง ต้นทุนทางเลือก "
            "และผลลัพธ์ระยะยาวได้คมกว่า ไปคุยกับ Rick ไหม?"
        )

    return AgentHandoffSuggestion(
        suggested_agent=decision.agent_mode,
        confidence=decision.confidence,
        reason=decision.reason,
        message=message,
    )
