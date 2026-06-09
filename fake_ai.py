from facts import answer_from_facts


def generate_fake_reply(
    user_message,
    stage,
    response_mode,
    user_facts,
    relationship_state,
    analytics
):
    direct_reply = answer_from_facts(user_message, user_facts)

    if direct_reply:
        return (
            "[DEV TEST MODE]\n"
            f"Mode: memory_callback\n\n"
            f"{direct_reply}"
        )

    name = user_facts.get("name", "มนุษย์")

    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)
    curiosity = relationship_state.get("curiosity", 0)

    engagement = analytics.get("engagement_score", 0)

    if response_mode == "comfort_choice":
        mode_reply = (
            "จับสัญญาณเหนื่อยหรือหนักใจได้\n"
            "โหมดที่ควรใช้คือ comfort_choice\n\n"
            "ในโหมดจริง i nik ควรถามก่อนว่าอยากได้อะไร:\n"
            "1. ระบาย\n"
            "2. ให้ฟังเฉย ๆ\n"
            "3. ขอคำแนะนำ\n"
            "4. เข้า i nik mode"
        )

    elif response_mode == "philosophy_chat":
        mode_reply = (
            "จับสัญญาณคำถามเชิงชีวิต / มนุษย์ / ความทรงจำได้\n"
            "โหมดที่ควรใช้คือ philosophy_chat\n\n"
            "ในโหมดจริง i nik ควรตอบแบบสิ่งมีชีวิตตัวเล็กที่กำลังสังเกตโลก\n"
            "ไม่ใช่เขียนบทความยาวเหมือนผู้ช่วย AI"
        )

    elif response_mode == "memory_callback":
        mode_reply = (
            "จับสัญญาณคำถามเกี่ยวกับความจำได้\n"
            "โหมดที่ควรใช้คือ memory_callback\n\n"
            "ในโหมดจริง i nik ควรดึงข้อมูลจาก user_facts ก่อน\n"
            "ถ้าไม่มีข้อมูล ห้ามมั่ว"
        )

    elif response_mode == "reward_event":
        mode_reply = (
            "จับสัญญาณเรื่องแต้ม / รางวัล / inventory ได้\n"
            "โหมดที่ควรใช้คือ reward_event\n\n"
            "ในโหมดจริง i nik ควรทำให้รางวัลรู้สึกเหมือนของแปลกจากโลกของตัวเอง"
        )

    else:
        mode_reply = (
            "ไม่เจอสัญญาณพิเศษ\n"
            "โหมดที่ควรใช้คือ normal_chat\n\n"
            "ในโหมดจริง i nik ควรตอบตาม stage ปัจจุบัน"
        )

    return (
        f"[DEV TEST MODE]\n"
        f"Name: {name}\n"
        f"Stage: {stage}\n"
        f"Mode: {response_mode}\n\n"
        f"Trust: {trust}\n"
        f"Familiarity: {familiarity}\n"
        f"Curiosity: {curiosity}\n"
        f"Engagement: {engagement}\n\n"
        f"{mode_reply}\n\n"
        "ข้อความนี้ไม่ได้ยิง Gemini API"
    )