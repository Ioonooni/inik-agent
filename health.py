def run_health_check(session_state):
    checks = []

    required_keys = [
        "messages",
        "user_facts",
        "user_profile",
        "inventory",
        "intimacy_score",
        "points",
        "relationship_state",
        "current_response_mode",
    ]

    for key in required_keys:
        checks.append({
            "name": f"session_state.{key}",
            "status": key in session_state,
            "detail": "OK" if key in session_state else "Missing"
        })

    relationship_state = session_state.get("relationship_state", {})

    for key in ["trust", "familiarity", "curiosity"]:
        checks.append({
            "name": f"relationship_state.{key}",
            "status": key in relationship_state,
            "detail": "OK" if key in relationship_state else "Missing"
        })

    user_profile = session_state.get("user_profile", {})

    for key in [
        "recent_mood",
        "conversation_style",
        "recurring_topics",
        "memorable_events",
        "total_messages",
        "total_visits",
        "last_interaction_date",
    ]:
        checks.append({
            "name": f"user_profile.{key}",
            "status": key in user_profile,
            "detail": "OK" if key in user_profile else "Missing"
        })

    passed = sum(1 for check in checks if check["status"])
    total = len(checks)

    return {
        "passed": passed,
        "total": total,
        "checks": checks,
        "healthy": passed == total
    }


def get_health_label(health_result):
    if health_result["healthy"]:
        return "Healthy"

    return f"{health_result['passed']}/{health_result['total']} checks passed"