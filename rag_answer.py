def clean_rag_line(line: str) -> str:
    text = (line or "").strip()

    prefixes = [
        "- [user_message]",
        "[user_message]",
        "- [conversation_fact]",
        "[conversation_fact]",
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    if "(" in text and text.endswith(")"):
        text = text[:text.rfind("(")].strip()

    return text.strip(" -")


def build_natural_rag_reply(user_message: str, rag_context: str) -> str | None:
    if not rag_context:
        return None

    if rag_context.strip() == "ไม่มี RAG memory ที่เกี่ยวข้อง":
        return None

    lines = [
        clean_rag_line(line)
        for line in rag_context.splitlines()
        if clean_rag_line(line)
    ]

    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)

    if not unique_lines:
        return None

    text = (user_message or "").strip().lower()

    if "ชอบอะไร" in text:
        for line in unique_lines:
            if "ชอบ" in line:
                liked = line.split("ชอบ", 1)[1].strip()
                if liked:
                    return f"เท่าที่ฉันจำได้ เธอชอบ{liked}นะ"

    if "ชื่ออะไร" in text:
        for line in unique_lines:
            if "ชื่อ" in line:
                name = line.split("ชื่อ", 1)[1].strip()
                if name:
                    return f"เธอชื่อ{name}ไง"

    if "จำอะไร" in text or "เคยพูด" in text or "เคยบอก" in text:
        memory_text = unique_lines[0]
        return f"เท่าที่ฉันจำได้ เธอเคยบอกว่า “{memory_text}”"

    memory_text = unique_lines[0]

    if len(memory_text) <= 80:
        return f"จำได้สิ เธอเคยพูดเรื่อง “{memory_text}”"

    return f"เท่าที่ฉันจำได้ เธอเคยพูดประมาณว่า “{memory_text[:80]}...”"