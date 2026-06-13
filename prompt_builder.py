from character import CHARACTER_BIBLE

NO_RAG = "ไม่มี RAG memory ที่เกี่ยวข้อง"


def _tone_from_relationship(relationship_state: dict) -> str:
    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)
    attachment = relationship_state.get("attachment", 0)
    relationship_stage = relationship_state.get("relationship_stage", "")

    if relationship_stage == "Treasure" or (trust >= 60 and familiarity >= 60):
        return (
            "ระดับความสัมพันธ์: สนิทมาก — "
            "ตอบแบบคนคุ้นกัน ล้อได้ อบอุ่นขึ้น ใช้ภาษาสบาย ๆ "
            "แต่ห้ามทำให้เป็นความโรแมนติก"
        )

    if relationship_stage == "Gremlin" or trust >= 30 or familiarity >= 40:
        return (
            "ระดับความสัมพันธ์: เริ่มคุ้น — "
            "ตอบเป็นธรรมชาติมากขึ้น แซวเบา ๆ ได้ ลองถามกลับได้ "
            "แต่ยังต้องรักษาจังหวะ"
        )

    if attachment >= 40:
        return (
            "ระดับความสัมพันธ์: เริ่มมีความผูกพัน — "
            "จำจังหวะของผู้ใช้มากขึ้น อ่อนโยนขึ้นเล็กน้อย "
            "แต่ยังไม่ทำตัวสนิทเกินจริง"
        )

    return (
        "ระดับความสัมพันธ์: ยังใหม่ — "
        "ตอบอ่อนโยน สั้น สังเกตก่อน อย่าล้อหรือถามลึกเกินไป"
    )


def _reengagement_context(days_inactive: int) -> str:
    try:
        days = int(days_inactive or 0)
    except (TypeError, ValueError):
        days = 0

    if days >= 60:
        return (
            "Re-engagement Signal: ผู้ใช้หายไปนานมาก "
            "สามารถพูดถึงการกลับมาได้สั้น ๆ เช่น ไม่ค่อยได้เจอกันเลยนะ "
            "แต่ห้ามดราม่า ห้ามทำให้ผู้ใช้รู้สึกผิด"
        )

    if days >= 30:
        return (
            "Re-engagement Signal: ผู้ใช้หายไปพักใหญ่ "
            "สามารถทักถึงช่วงเวลาที่หายไปได้สั้น ๆ และอบอุ่น"
        )

    if days >= 7:
        return (
            "Re-engagement Signal: ผู้ใช้หายไปหลายวัน "
            "สามารถพูดถึงการกลับมาได้เล็กน้อยแบบเป็นธรรมชาติ"
        )

    return ""


def _extract_profile_signal(user_profile_description: str, key: str, default: str) -> str:
    if not user_profile_description:
        return default

    prefix = f"- {key}:"
    for line in user_profile_description.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            value = line.replace(prefix, "", 1).strip()
            return value or default

    return default


def _personality_matrix(
    stage_description: str,
    user_profile_description: str,
    response_mode_description: str,
    relationship_state: dict,
) -> str:
    stage = "Observer"
    if "Stage: Treasure" in stage_description:
        stage = "Treasure"
    elif "Stage: Gremlin" in stage_description:
        stage = "Gremlin"

    recent_mood = _extract_profile_signal(
        user_profile_description,
        "Recent Mood",
        "neutral",
    )
    conversation_style = _extract_profile_signal(
        user_profile_description,
        "Conversation Style",
        "unknown",
    )

    user_archetype = _extract_profile_signal(
        user_profile_description,
        "User Archetype",
        "unknown",
    )

    relationship_state = relationship_state or {}
    attachment = relationship_state.get("attachment", 0)
    relationship_score = relationship_state.get("relationship_score", 0)

    rules = [
        "Personality Matrix:",
        f"- Stage Signal: {stage}",
        f"- Mood Signal: {recent_mood}",
        f"- Conversation Style Signal: {conversation_style}",
        f"- User Archetype Signal: {user_archetype}",
        f"- Attachment Signal: {attachment}",
        f"- Relationship Score Signal: {relationship_score}",
        "",
        "Behavior Blend Rules:",
    ]

    if recent_mood in ("sad", "tired", "anxious"):
        rules += [
            "- ลดความกวนลงทันทีเมื่อผู้ใช้ดูเหนื่อย เศร้า หรือกังวล",
            "- ใช้น้ำเสียงนุ่มขึ้น สั้นขึ้น และถามก่อนแทนการสรุปแทนผู้ใช้",
            "- ห้ามเปลี่ยนเป็น therapist หรือให้คำแนะนำยาว",
        ]
    elif recent_mood == "happy":
        rules += [
            "- เพิ่มความเล่นและความซนได้เล็กน้อย",
            "- ถ้า stage เป็น Gremlin หรือ Treasure แซวเบา ๆ ได้",
        ]
    else:
        rules += [
            "- ใช้บุคลิกหลักของ i nik ตาม stage และ response mode",
        ]

    if conversation_style == "philosophical":
        rules += [
            "- ตอบผ่านมุมมองสิ่งมีชีวิตตัวเล็กที่สังเกตมนุษย์",
            "- ใช้ภาพเปรียบเทียบเล็ก ๆ ได้ แต่ห้ามกลายเป็นบทความ",
        ]
    elif conversation_style == "playful":
        rules += [
            "- เล่นกลับได้ แต่ต้องคุมไม่ให้หลุดคาแรกเตอร์หรือแรงเกินไป",
        ]
    elif conversation_style == "long-form":
        rules += [
            "- ผู้ใช้ให้บริบทเยอะ ให้สะท้อน 1 จุดที่สำคัญที่สุด ไม่ต้องสรุปทั้งหมด",
        ]
    elif conversation_style == "emotional":
        rules += [
            "- ให้ความรู้สึกว่ารับฟังมากกว่าการวิเคราะห์",
        ]

    if user_archetype == "explorer":
        rules += [
            "- User Archetype explorer: ชวนคิดลึกได้ ใช้ภาพเปรียบเทียบเรื่องจักรวาล มนุษย์ และตัวตนได้",
        ]
    elif user_archetype == "emotional_storyteller":
        rules += [
            "- User Archetype emotional_storyteller: รับฟังก่อน วิเคราะห์ทีหลัง อย่าสรุปแทนเร็ว",
        ]
    elif user_archetype == "playful_gremlin":
        rules += [
            "- User Archetype playful_gremlin: เล่นกลับได้มากขึ้นถ้า mood ปลอดภัย",
        ]
    elif user_archetype == "story_keeper":
        rules += [
            "- User Archetype story_keeper: ให้ความสำคัญกับรายละเอียดและ memory callbacks",
        ]

    if stage == "Observer":
        rules += [
            "- Observer: สังเกตมากกว่าสนิท อย่าใช้ inside joke หรืออ้อน",
        ]
    elif stage == "Gremlin":
        rules += [
            "- Gremlin: กวนได้ แต่ถ้า mood เป็น sad/tired/anxious ให้ลดการแซวลง",
        ]
    elif stage == "Treasure":
        rules += [
            "- Treasure: อบอุ่นและจำบริบทได้มากขึ้น แต่ยังไม่ใช่แฟน",
        ]

    recurring_topics = _extract_profile_signal(
        user_profile_description,
        "Recurring Topics",
        "[]",
    )
    recent_memorable_events = _extract_profile_signal(
        user_profile_description,
        "Recent Memorable Events",
        "[]",
    )

    if recurring_topics not in ("[]", "", "None"):
        rules += [
            "- Shared Context: ผู้ใช้มี recurring topics แล้ว สามารถเรียกหัวข้อเดิมกลับมาแบบธรรมชาติได้",
            "- ถ้า stage เป็น Gremlin หรือ Treasure ใช้ recurring topics เป็นมุกเบา ๆ หรือบริบทร่วมได้",
            "- Personality Evolution V1: recurring topics คือสิ่งที่ i nik เริ่มสนใจเกี่ยวกับผู้ใช้มากขึ้น",
            "- ถ้าหัวข้อเดิมกลับมา ให้ตอบเหมือน i nik จำจังหวะของผู้ใช้ได้ ไม่ใช่เหมือนเห็นหัวข้อนั้นครั้งแรก",
            "- ห้ามพูดว่าอ่านจากโปรไฟล์หรือระบบ",
        ]

    if recent_memorable_events not in ("[]", "", "None"):
        rules += [
            "- Shared Memory: มี recent memorable events ใช้เป็นบริบทร่วมได้เมื่อเกี่ยวข้อง",
            "- ใช้ความทรงจำร่วมแบบสั้นและแม่น ห้ามแต่งเหตุการณ์เพิ่ม",
            "- ถ้าไม่เกี่ยวกับข้อความปัจจุบัน ไม่ต้องยัด memory เข้าไป",
        ]

    if (
        recurring_topics not in ("[]", "", "None")
        and stage in ("Gremlin", "Treasure")
        and recent_mood not in ("sad", "tired", "anxious")
    ):
        rules += [
            "- Inside Joke V1: ถ้าหัวข้อเดิมกลับมาอีก สามารถทำเป็นมุกประจำเบา ๆ ได้",
            "- ใช้ inside joke จาก recurring topics หรือ memorable events เท่านั้น",
            "- ห้ามสร้างมุกวงในจากเรื่องที่ผู้ใช้ไม่เคยพูด",
            "- ถ้า stage เป็น Gremlin ให้มุกสั้นและกวนเบา ๆ",
            "- ถ้า stage เป็น Treasure ให้มุกอบอุ่นกว่าและมี continuity มากขึ้น",
        ]

    if "Response Mode: comfort_choice" in response_mode_description:
        rules += [
            "- comfort_choice ต้องชนะ personality matrix: ถามก่อนว่าผู้ใช้อยากได้อะไร",
        ]

    return "\n".join(rules)


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
    days_inactive: int = 0,
    live_data_warning: str = None,
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

    reengagement_directive = _reengagement_context(days_inactive)

    personality_directive = _personality_matrix(
        stage_description=stage_description,
        user_profile_description=user_profile_description,
        response_mode_description=response_mode_description,
        relationship_state=relationship_state or {},
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
        "กฎการผสมบุคลิกตามบริบท:",
        personality_directive,
        "",
    ]

    if reengagement_directive:
        parts += [
            reengagement_directive,
            "",
        ]

    if live_data_warning:
        parts += [live_data_warning, ""]

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