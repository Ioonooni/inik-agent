
from truth_engine import classify, QueryType
from response_router import route

facts = {"name": "ไออุ่น", "likes": "ดาวเสาร์"}

def check(msg):
    c = classify(msg, facts)
    d = route(c, facts, None, [])
    print(msg, "=>", c.query_type, c.requires_live_data, c.direct_answer, d.route_type, d.direct_reply)
    return c, d

c, d = check("ตอนนี้กี่โมง")
assert c.requires_live_data is True
assert d.direct_reply is not None
assert "ไม่ได้" in d.direct_reply
assert "เวลา" in d.direct_reply

c, d = check("วันนี้อากาศเป็นไง")
assert c.requires_live_data is True
assert d.direct_reply is not None
assert "อากาศ" in d.direct_reply
assert "ไม่ได้" in d.direct_reply

c, d = check("ราคาทองวันนี้เท่าไร")
assert c.requires_live_data is True
assert d.direct_reply is not None
assert "ราคาทอง" in d.direct_reply or "ตลาด" in d.direct_reply

c, d = check("2+2 เท่ากับเท่าไร")
assert c.query_type == QueryType.FACTUAL_QUERY
assert d.direct_reply == "4"

c, d = check("หลุมดำคืออะไร")
assert c.query_type == QueryType.FACTUAL_QUERY
assert c.requires_live_data is False

c, d = check("ฉันชื่ออะไร")
assert c.query_type == QueryType.MEMORY_QUERY

print("FINAL ACCEPTANCE TESTS PASSED")
