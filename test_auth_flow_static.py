from pathlib import Path

app = Path("app.py").read_text(encoding="utf-8")

forbidden_patterns = [
    'st.session_state.user_id = "demo_user"',
    "st.session_state.user_id = 'demo_user'",
    'text_input(\n            "User ID"',
]

for pattern in forbidden_patterns:
    assert pattern not in app, f"Forbidden auth fallback found: {pattern}"

assert "def init_user_session():" in app
assert "if not user_id:" in app
assert "st.stop()" in app

print("AUTH FLOW STATIC TEST PASSED")
