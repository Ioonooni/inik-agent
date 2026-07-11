def build_chat_history(messages, limit=10, active_agent_mode=None):
    recent_messages = messages[-limit:]

    history_lines = []

    for message in recent_messages:
        role = message.get("role")
        content = message.get("content")

        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            if active_agent_mode is None:
                history_lines.append(f"i nik: {content}")
            else:
                if message.get("agent_mode") != active_agent_mode:
                    continue
                if active_agent_mode == "rick_royce":
                    label = "Rick Royce"
                elif active_agent_mode == "hybrid":
                    label = "Hybrid"
                else:
                    label = "i nik"
                history_lines.append(f"{label}: {content}")

    return "\n".join(history_lines)