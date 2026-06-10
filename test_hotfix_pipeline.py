
from truth_engine import classify, QueryType
from response_router import route
from memory_verifier import verify

facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

def assert_case(msg, expected_type=None, direct=None, live=None):
    c = classify(msg, dict(facts))
    d = route(c, dict(facts), None, [])
    print(msg, "=>", c.query_type, "direct=", c.direct_answer, "route=", d.route_type, "reply=", d.direct_reply)
    if expected_type:
        assert c.query_type == expected_type, (msg, c.query_type, expected_type)
    if direct is not None:
        assert c.direct_answer == direct or d.direct_reply == direct, (msg, c.direct_answer, d.direct_reply)
    if live is not None:
        assert c.requires_live_data is live, (msg, c.requires_live_data, live)

assert_case("2+2 เท่ากับเท่าไร", QueryType.FACTUAL_QUERY, direct="4")
assert_case("หลุมดำคืออะไร", QueryType.FACTUAL_QUERY)
assert_case("เล่าเรื่องหลุมดำ", QueryType.FACTUAL_QUERY)
assert_case("ดาวเสาร์คืออะไร", QueryType.FACTUAL_QUERY)
assert_case("ตอนนี้กี่โมง", QueryType.FACTUAL_QUERY, live=True)
assert_case("วันนี้อากาศเป็นไง", QueryType.FACTUAL_QUERY, live=True)
assert_case("ฉันชื่ออะไร", QueryType.MEMORY_QUERY)
assert_case("ฉันชอบอะไร", QueryType.MEMORY_QUERY)

from app import should_extract_structured_facts, should_save_rag_user_message

assert should_extract_structured_facts("ฉันชอบดาวเสาร์", classify("ฉันชอบดาวเสาร์", facts)) is True
assert should_extract_structured_facts("ฉันชอบอะไรเกี่ยวกับหลุมดำ", classify("ฉันชอบอะไรเกี่ยวกับหลุมดำ", facts)) is False
assert should_save_rag_user_message("หลุมดำคืออะไร", classify("หลุมดำคืออะไร", facts)) is False
assert should_save_rag_user_message("2+2 เท่ากับเท่าไร", classify("2+2 เท่ากับเท่าไร", facts)) is False

print("HOTFIX TESTS PASSED")
