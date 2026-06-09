def build_fallback_reply(
    error_message,
    user_message,
    stage,
    response_mode,
    user_facts,
    relationship_state
):
    name = user_facts.get("name", "มนุษย์")

    if "429" in error_message or "quota" in error_message.lower() or "TooManyRequests" in error_message:
        return (
            f"ตอนนี้ประตูเวทของ Gemini ติดขัดนิดหน่อยนะ {name}\n\n"
            "แต่ระบบของ i nik ยังจำสถานะเธออยู่\n"
            f"- Stage: {stage}\n"
            f"- Mode: {response_mode}\n"
            f"- Trust: {relationship_state.get('trust', 0)}\n"
            f"- Familiarity: {relationship_state.get('familiarity', 0)}\n"
            f"- Curiosity: {relationship_state.get('curiosity', 0)}\n\n"
            "ลองพักไว้ก่อน หรือใช้ Dev Test Mode เพื่อตรวจระบบ memory / reward / analytics ได้เลย"
        )

    return (
        f"มีบางอย่างสะดุดตอน i nik จะตอบนะ {name}\n\n"
        f"รายละเอียดระบบ: {error_message}\n\n"
        "แต่ memory กับ state ยังถูกบันทึกไว้ ไม่ได้หายไปไหน"
    )