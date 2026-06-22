from agent_router import classify_agent_route


def run():
    tests = [
        ("วันนี้เหนื่อยมาก อยากระบาย", "inik"),
        ("ควรซื้อหุ้น ASML ไหม", "rick_royce"),
        ("ฉันเครียดและกำลังคิดจะลาออก", "hybrid"),
        ("ฉันมีเงินเก็บ 5 แสน ควรลงทุนหรือเรียนต่อ", "rick_royce"),
    ]

    for msg, expected in tests:
        result = classify_agent_route(msg, "auto")
        assert result.agent_mode == expected, (
            f"{msg} -> {result.agent_mode} != {expected}"
        )

    print("runtime routing ok")


if __name__ == "__main__":
    run()
