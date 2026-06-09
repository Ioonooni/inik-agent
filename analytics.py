def calculate_analytics(session_state):
    messages = session_state.get("messages", [])
    user_facts = session_state.get("user_facts", {})
    inventory = session_state.get("inventory", [])
    relationship_state = session_state.get("relationship_state", {})

    user_messages = [
        message for message in messages
        if message.get("role") == "user"
    ]

    assistant_messages = [
        message for message in messages
        if message.get("role") == "assistant"
    ]

    intimacy_score = session_state.get("intimacy_score", 0)
    points = session_state.get("points", 0)

    trust = relationship_state.get("trust", 0)
    familiarity = relationship_state.get("familiarity", 0)
    curiosity = relationship_state.get("curiosity", 0)

    memory_fact_count = len(user_facts)
    inventory_count = len(inventory)

    engagement_score = min(
        100,
        int(
            (intimacy_score * 0.35)
            + (points * 2)
            + (trust * 0.2)
            + (familiarity * 0.25)
            + (curiosity * 0.2)
            + (memory_fact_count * 5)
            + (inventory_count * 3)
        )
    )

    return {
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "memory_fact_count": memory_fact_count,
        "inventory_count": inventory_count,
        "engagement_score": engagement_score,
        "trust": trust,
        "familiarity": familiarity,
        "curiosity": curiosity,
        "intimacy_score": intimacy_score,
        "points": points,
    }


def get_engagement_label(score):
    if score < 25:
        return "Low Engagement"
    if score < 50:
        return "Developing Engagement"
    if score < 75:
        return "Strong Engagement"

    return "High Engagement"


def get_system_summary(analytics):
    return f"""
System Summary:
- Total Messages: {analytics["total_messages"]}
- User Messages: {analytics["user_messages"]}
- Assistant Messages: {analytics["assistant_messages"]}
- Memory Facts: {analytics["memory_fact_count"]}
- Inventory Items: {analytics["inventory_count"]}
- Engagement Score: {analytics["engagement_score"]}
- Engagement Label: {get_engagement_label(analytics["engagement_score"])}
"""