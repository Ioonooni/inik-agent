_QUOTA_MARKERS = ("429", "quota", "TooManyRequests", "rate limit", "Resource has been exhausted")

_CLEAN_QUERY_TYPES = (
    "FACTUAL_QUERY",
    "NORMAL_CHAT",
    "LIVE_DATA_QUERY",
    "MEMORY_QUERY",
    "TOOL_QUERY",
    "RELATIONSHIP_QUERY",
)


def _is_quota_error(error_message: str) -> bool:
    lower = error_message.lower()
    return any(m.lower() in lower for m in _QUOTA_MARKERS)


def build_fallback_reply(
    error_message,
    user_message,
    stage,
    response_mode,
    user_facts,
    relationship_state,
    query_type=None,
):
    name = user_facts.get("name", "มนุษย์")

    # For all classifiable query types, return a clean intent-appropriate message.
    # Never dump Stage/Trust/Familiarity unless the user explicitly asked for state.
    if query_type in _CLEAN_QUERY_TYPES:
        if _is_quota_error(error_message):
            return "ขอโทษนะ ตอนนี้ i nik เชื่อมต่อ Gemini ไม่ได้ชั่วคราว ลองถามใหม่สักครู่นะ"

        if query_type == "MEMORY_QUERY":
            return f"ตอนนี้ i nik เรียกข้อมูลความจำไม่ได้ {name} ลองถามใหม่อีกทีนะ"

        if query_type in ("TOOL_QUERY", "RELATIONSHIP_QUERY"):
            return "ระบบตรวจสอบข้อมูลไม่ได้ตอนนี้ ลองใหม่อีกสักครู่นะ"

        return "i nik ตอบไม่ได้ตอนนี้ ลองถามใหม่อีกทีนะ"

    # Unknown query type — surface a minimal error without dumping internal state
    if _is_quota_error(error_message):
        return f"Gemini ติดขัดชั่วคราวนะ {name} ลองใหม่สักครู่"

    return f"มีบางอย่างสะดุดตอน i nik จะตอบนะ {name} ลองใหม่อีกทีนะ"
