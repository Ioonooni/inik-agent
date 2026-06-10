from truth_engine import classify, QueryType
from response_router import route
from planner import build_plan


NO_GEMINI_CASES = [
    ("2+2 เท่ากับเท่าไร", "FACTUAL_DIRECT"),
    ("ตอนนี้กี่โมง", "LIVE_DIRECT"),
    ("วันนี้อากาศเป็นไง", "LIVE_DIRECT"),
    ("ราคาทองวันนี้เท่าไร", "LIVE_DIRECT"),
    ("ฉันชื่ออะไร", "MEMORY_QUERY"),
    ("ฉันชอบอะไร", "MEMORY_QUERY"),
    ("สถานะของฉัน", "TOOL_QUERY"),
    ("คะแนนของฉันเท่าไร", "TOOL_QUERY"),
    ("ความสัมพันธ์ตอนนี้เป็นไง", "RELATIONSHIP_QUERY"),
    ("ฉันชอบอะไรเกี่ยวกับหลุมดำ", "NOT_MEMORY_WRITE"),
    ("หลุมดำคืออะไร", "FACTUAL_NO_MEMORY"),
    ("ดาวเสาร์คืออะไร", "FACTUAL_NO_MEMORY"),
]


class DummyState(dict):
    pass


def _dummy_state(facts):
    s = DummyState()
    s.user_facts = facts
    s.relationship_state = {"trust": 0, "familiarity": 0, "curiosity": 0}
    s.inventory = []
    s.points = 0
    s.intimacy_score = 0
    return s


def run_acceptance_checks(session_state=None):
    facts = {}

    if session_state is not None:
        facts = dict(getattr(session_state, "user_facts", {}) or {})

    if not facts:
        facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

    results = []

    for message, expected in NO_GEMINI_CASES:
        c = classify(message, facts)
        d = route(c, facts, None, [])
        plan = build_plan(message, _dummy_state(facts))

        ok = True
        reason = "ok"

        if expected == "FACTUAL_DIRECT":
            ok = (
                c.query_type == QueryType.FACTUAL_QUERY
                and d.direct_reply == "4"
            )
            reason = f"type={c.query_type}, reply={d.direct_reply}"

        elif expected == "LIVE_DIRECT":
            ok = (
                c.query_type == QueryType.FACTUAL_QUERY
                and c.requires_live_data is True
                and d.direct_reply is not None
                and "ไม่ได้" in d.direct_reply
            )
            reason = f"live={c.requires_live_data}, reply={d.direct_reply}"

        elif expected == "MEMORY_QUERY":
            ok = c.query_type == QueryType.MEMORY_QUERY
            reason = f"type={c.query_type}"

        elif expected == "TOOL_QUERY":
            ok = c.query_type == QueryType.TOOL_QUERY or (plan and plan.get("tool"))
            reason = f"type={c.query_type}, plan={plan}"

        elif expected == "RELATIONSHIP_QUERY":
            ok = c.query_type == QueryType.RELATIONSHIP_QUERY or (plan and plan.get("tool"))
            reason = f"type={c.query_type}, plan={plan}"

        elif expected == "NOT_MEMORY_WRITE":
            ok = c.query_type != QueryType.MEMORY_QUERY
            reason = f"type={c.query_type}"

        elif expected == "FACTUAL_NO_MEMORY":
            ok = (
                c.query_type == QueryType.FACTUAL_QUERY
                and c.requires_live_data is False
            )
            reason = f"type={c.query_type}, live={c.requires_live_data}"

        results.append({
            "message": message,
            "expected": expected,
            "ok": ok,
            "detail": reason,
        })

    passed = sum(1 for r in results if r["ok"])
    failed = len(results) - passed

    return {
        "ok": failed == 0,
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    report = run_acceptance_checks()
    for r in report["results"]:
        mark = "PASS" if r["ok"] else "FAIL"
        print(f"{mark} | {r['message']} | {r['expected']} | {r['detail']}")
    print(f"\npassed={report['passed']} failed={report['failed']}")
    raise SystemExit(0 if report["ok"] else 1)
