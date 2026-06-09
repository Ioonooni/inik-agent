from character import CHARACTER_BIBLE

NO_RAG = "ไม่มี RAG memory ที่เกี่ยวข้อง"


def build_main_prompt(
    stage_description: str,
    relationship_description: str,
    user_profile_description: str,
    response_mode_description: str,
    chat_history: str,
    user_facts: dict,
    rag_context: str,
    user_message: str,
) -> str:
    facts_text = (
        "\n".join(f"- {k}: {v}" for k, v in user_facts.items())
        if user_facts
        else "ยังไม่มีข้อมูลที่จำได้"
    )

    has_rag = rag_context and rag_context.strip() not in ("", NO_RAG)
    rag_section = (
        "\nประวัติสนทนาเก่าที่เกี่ยวข้อง"
        " (ใช้เป็น background เท่านั้น ห้ามพูดถึงโดยตรง):\n"
        + rag_context
        + "\n"
    ) if has_rag else ""

    parts = [
        CHARACTER_BIBLE,
        "",
        "กฎบุคลิกตามระดับความสนิท:",
        stage_description,
        "",
        "สถานะความสัมพันธ์:",
        relationship_description,
        "",
        "โปรไฟล์ผู้ใช้:",
        user_profile_description,
        "",
        "โหมดการตอบปัจจุบัน:",
        response_mode_description,
        "",
        "ประวัติการคุยล่าสุด:",
        chat_history,
        "",
        "ข้อมูลที่จำได้:",
        facts_text,
        rag_section,
        "กฎการใช้ความจำ:",
        "- ถ้าข้อมูลที่จำได้มี name ให้ใช้ชื่อนั้นเมื่อตอบคำถามเกี่ยวกับชื่อผู้ใช้",
        "- ห้ามตอบว่าไม่รู้ชื่อ ถ้าในข้อมูลที่จำได้มี name อยู่แล้ว",
        "- ถ้าผู้ใช้ถามว่า ฉันชื่ออะไร ให้ตอบจากข้อมูลที่จำได้โดยตรง",
        "- ถ้าผู้ใช้ถามว่า ฉันชอบอะไร ให้ตอบจากข้อมูลที่จำได้โดยตรง",
        "- ใช้ความจำอย่างเป็นธรรมชาติ ไม่ต้องประกาศว่าอ่านจากระบบ",
        "",
        "ผู้ใช้พูดว่า:",
        user_message,
    ]

    return "\n".join(parts)
