from pathlib import Path


def run():
    text = Path("inik_api.py").read_text(encoding="utf-8")

    required = [
        "memory = load_memory(user_id=user_id)",
        "user_profile = normalize_user_profile",
        "user_facts = memory.get",
        "rag_context = build_safe_rag_context",
        "build_rick_prompt(",
        "build_main_prompt(",
        "elif agent_mode == \"hybrid\":",
        "save_memory(",
        "user_id=user_id",
    ]

    for item in required:
        assert item in text, f"missing shared API wiring: {item}"

    print("api shared context static ok")


if __name__ == "__main__":
    run()
