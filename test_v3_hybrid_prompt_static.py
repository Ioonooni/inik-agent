from pathlib import Path


def run():
    text = Path("inik_api.py").read_text(encoding="utf-8")

    required = [
        'elif agent_mode == "hybrid":',
        "HYBRID MODE: Heart + Mind response.",
        "=== HEART CONTEXT: i nik ===",
        "=== MIND CONTEXT: Rick Royce ===",
        "tradeoffs / risks / opportunity cost",
        "next practical step",
    ]

    for item in required:
        assert item in text, f"missing: {item}"

    print("hybrid prompt static ok")


if __name__ == "__main__":
    run()
