from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentHandoffSuggestion:
    suggested_agent: str
    confidence: float
    reason: str
    message: str


RICK_KEYWORDS = {
    "investment": [
        "หุ้น", "ลงทุน", "ซื้อหุ้น", "ขายหุ้น", "พอร์ต", "asset", "stock",
        "asml", "nvda", "tesla", "btc", "bitcoin", "กองทุน", "ผลตอบแทน",
        "capital", "moat", "valuation", "เงินลงทุน",
    ],
    "career": [
        "ลาออก", "เปลี่ยนงาน", "สมัครงาน", "career", "resume", "portfolio",
        "เงินเดือน", "งานไหนดี", "สายงาน", "ฝึกงาน", "internship",
    ],
    "business": [
        "ธุรกิจ", "startup", "สตาร์ทอัพ", "ลูกค้า", "รายได้", "กำไร",
        "business model", "pricing", "ตลาด", "คู่แข่ง", "product market fit",
    ],
    "strategy": [
        "กลยุทธ์", "คุ้มไหม", "ควรทำไหม", "เลือกทางไหนดี", "ตัดสินใจ",
        "tradeoff", "opportunity cost", "ความเสี่ยง", "risk", "แผนระยะยาว",
    ],
}


def detect_agent_handoff(user_message: str) -> Optional[AgentHandoffSuggestion]:
    text = (user_message or "").strip().lower()
    if not text:
        return None

    matched_reason = None
    matched_count = 0

    for reason, keywords in RICK_KEYWORDS.items():
        count = sum(1 for keyword in keywords if keyword.lower() in text)
        if count > matched_count:
            matched_count = count
            matched_reason = reason

    if not matched_reason:
        return None

    confidence = min(0.95, 0.72 + (matched_count * 0.08))

    if confidence < 0.75:
        return None

    reason_label = {
        "investment": "investment / capital allocation",
        "career": "career decision",
        "business": "business strategy",
        "strategy": "strategic decision",
    }.get(matched_reason, matched_reason)

    return AgentHandoffSuggestion(
        suggested_agent="rick_royce",
        confidence=round(confidence, 2),
        reason=matched_reason,
        message=(
            "เรื่องนี้ i nik คิดได้ระดับหนึ่งนะ แต่ถ้าเป็นเรื่อง "
            f"{reason_label} Rick Royce น่าจะมองความเสี่ยง ต้นทุนทางเลือก "
            "และผลลัพธ์ระยะยาวได้คมกว่า ไปคุยกับ Rick ไหม?"
        ),
    )
