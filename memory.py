def build_chat_history(messages, limit=10):
    recent_messages = messages[-limit:]

    history_lines = []

    for message in recent_messages:
        role = message.get("role")
        content = message.get("content")

        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            history_lines.append(f"i nik: {content}")

    return "\n".join(history_lines)