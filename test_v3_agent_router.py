from agent_router import classify_agent_route, detect_agent_handoff


def test_emotional_query_routes_to_inik():
    decision = classify_agent_route("วันนี้เหนื่อยมาก อยากระบาย", "auto")
    assert decision.agent_mode == "inik"


def test_investment_query_routes_to_rick():
    decision = classify_agent_route("ฉันมีเงินเก็บ 5 แสน ควรลงทุนอะไรดี", "auto")
    assert decision.agent_mode == "rick_royce"
    assert decision.confidence >= 0.75


def test_career_strategy_routes_to_rick():
    decision = classify_agent_route("ควรลาออกไปทำ startup หรือเรียนต่อดี", "auto")
    assert decision.agent_mode == "rick_royce"


def test_mixed_query_routes_to_hybrid():
    decision = classify_agent_route("ฉันเครียดมาก ควรลาออกไปทำธุรกิจไหม", "auto")
    assert decision.agent_mode == "hybrid"


def test_explicit_mode_overrides_auto():
    decision = classify_agent_route("วันนี้เหนื่อย", "rick_royce")
    assert decision.agent_mode == "rick_royce"
    assert decision.reason == "explicit_user_selected_mode"


def test_handoff_still_works_for_existing_api():
    suggestion = detect_agent_handoff("ควรซื้อหุ้น ASML ไหม")
    assert suggestion is not None
    assert suggestion.suggested_agent == "rick_royce"
