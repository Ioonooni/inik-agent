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

    # For factual / normal chat, never dump user state — it's irrelevant and confusing
    if query_type in ("FACTUAL_QUERY", "NORMAL_CHAT"):
        if "429" in error_message or "quota" in error_message.lower():
            return "รับรู้แล้วนะ ฉันยังตอบแบบโมเดลหลักไม่ได้เต็มที่ตอนนี้ แต่จะไม่เดาข้อมูลหรือดึงความจำมั่ว ๆ แทน"
        return "i nik ตอบไม่ได้ตอนนี้ ฉันจะไม่เดาข้อมูลแทนอีกทีนะ"

    if "429" in error_message or "quota" in error_message.lower() or "TooManyRequests" in error_message:
        return (
            f"ตอนนี้ประตูเวทของ โมเดลหลัก ติดขัดนิดหน่อยนะ {name}\n\n"
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
