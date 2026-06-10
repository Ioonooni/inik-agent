from character import CHARACTER_BIBLE

NO_RAG = "ไม่มี RAG memory ที่เกี่ยวข้อง"


def _tone_from_relationship(relationship_state: dict) -> str:
    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)

    if trust >= 60 and familiarity >= 60:
        return (
            "ระดับความสัมพันธ์: สนิทมาก — "
            "ตอบแบบเพื่อนเก่า ล้อได้ ถามลึกได้ ใช้ภาษาสบาย ๆ ไม่ต้องระวังมาก"
        )
    if trust >= 30 or familiarity >= 40:
        return (
            "ระดับความสัมพันธ์: เริ่มคุ้น — "
            "ตอบเป็นธรรมชาติมากขึ้น ลองถามกลับได้ ยังไม่ต้องล้อมากนัก"
        )
    return (
        "ระดับความสัมพันธ์: ยังใหม่ — "
        "ตอบอ่อนโยน สั้น สังเกตก่อน อย่าล้อหรือถามลึกเกินไป"
    )


def build_main_prompt(
    stage_description: str,
    relationship_description: str,
    user_profile_description: str,
    response_mode_description: str,
    chat_history: str,
    user_facts: dict,
    rag_context: str,
    user_message: str,
    relationship_state: dict = None,
) -> str:
    facts_text = (
        "\n".join(f"- {k}: {v}" for k, v in user_facts.items() if not k.startswith("_"))
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

    tone_directive = (
        _tone_from_relationship(relationship_state)
        if relationship_state
        else ""
    )

    parts = [
        CHARACTER_BIBLE,
        "",
        "กฎบุคลิกตามระดับความสนิท:",
        stage_description,
        "",
        "สถานะความสัมพันธ์:",
        relationship_description,
        "",
    ]

    if tone_directive:
        parts += [tone_directive, ""]

    parts += [
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
