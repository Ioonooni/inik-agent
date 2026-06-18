from agent_router import detect_agent_handoff


def test_investment_query_suggests_rick_royce():
    suggestion = detect_agent_handoff("ควรลงทุนใน NVDA หรือ ASML ดีไหม valuation แพงไปไหม")

    assert suggestion is not None
    assert suggestion.suggested_agent == "rick_royce"
    assert suggestion.confidence >= 0.75
    assert "investment" in suggestion.reason or "capital" in suggestion.message


def test_business_strategy_query_suggests_rick_royce():
    suggestion = detect_agent_handoff("ธุรกิจนี้คุ้มไหม market และ pricing ควรคิดยังไง")

    assert suggestion is not None
    assert suggestion.suggested_agent == "rick_royce"
    assert suggestion.confidence >= 0.75
    assert suggestion.reason == "business"


def test_career_decision_query_suggests_rick_royce():
    suggestion = detect_agent_handoff("ควรลาออกหรือเปลี่ยนงานดี career ตอนนี้ตันมาก")

    assert suggestion is not None
    assert suggestion.suggested_agent == "rick_royce"
    assert suggestion.confidence >= 0.75
    assert suggestion.reason == "career"


def test_normal_companion_chat_does_not_handoff():
    suggestion = detect_agent_handoff("วันนี้เหนื่อย อยากคุยเรื่องดาวกับขนมเฉย ๆ")

    assert suggestion is None


def test_empty_message_does_not_handoff():
    assert detect_agent_handoff("") is None
    assert detect_agent_handoff(None) is None
