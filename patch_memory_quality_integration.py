from pathlib import Path

app = Path("app.py")

text = app.read_text(encoding="utf-8")

# add import

if "from memory_quality import assess_memory_quality" not in text:
    text = text.replace(
        "from memory_verifier import verify as verify_memories",
        "from memory_verifier import verify as verify_memories\nfrom memory_quality import assess_memory_quality"
    )

# inject before save_memory_note

old = """save_memory_note("""
new = """quality = assess_memory_quality(user_message)

                if quality.should_store:

                    save_memory_note("""

if old in text and "quality = assess_memory_quality(user_message)" not in text:
    text = text.replace(old, new, 1)

# replace memory_type if present

text = text.replace(
    'memory_type="user_message"',
    'memory_type=quality.memory_type'
)

app.write_text(text, encoding="utf-8")

print("PATCHED app.py")
