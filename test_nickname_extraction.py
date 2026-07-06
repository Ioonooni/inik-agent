import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import facts as F


def _name(msg, initial=None):
    d = dict(initial or {})
    F.extract_facts(msg, d)
    return d.get("name")


# ── New: ชื่อเล่น extraction ─────────────────────────────────────────────────

def test_nickname_plain():
    assert _name("ชื่อเล่นคือไออุ่น") == "ไออุ่น"

def test_nickname_plain_with_space():
    assert _name("ชื่อเล่นคือ เลม่อน") == "เลม่อน"

def test_nickname_rao():
    assert _name("ชื่อเล่นเราคือเลม่อน") == "เลม่อน"

def test_nickname_chan():
    assert _name("ชื่อเล่นฉันคือไออุ่น") == "ไออุ่น"


# ── Previous 9 memory-gate tests (must all still hold) ───────────────────────

def test_recall_no_write_question_with_pa():
    assert _name("ฉันชื่อไรจำได้ปะ", {"name": "OLD"}) == "OLD"

def test_recall_no_write_complaint_thammai():
    assert _name("เราชื่อเลม่อนไง ทำไมจำไม่ได้", {"name": "OLD"}) == "OLD"

def test_recall_no_write_pure_recall():
    assert _name("จำชื่อฉันได้ไหม", {"name": "OLD"}) == "OLD"

def test_recall_no_write_yang_jam():
    assert _name("ยังจำชื่อเราไม่ได้อีกเหรอ", {"name": "OLD"}) == "OLD"

def test_recall_no_write_jam_dai_mai():
    assert _name("จำได้ไหมว่าเราชื่ออะไร", {"name": "OLD"}) == "OLD"

def test_write_simple_declaration():
    assert _name("ฉันชื่อไออุ่น") == "ไออุ่น"

def test_write_explicit_command():
    assert _name("เรียกฉันว่าไออุ่น") == "ไออุ่น"

def test_write_command_with_jam_wai():
    assert _name("เรียกฉันว่าเลม่อน จำไว้ด้วย") == "เลม่อน"

def test_write_toipai_riak():
    assert _name("ต่อไปเรียกเราว่าเลม่อนนะ") == "เลม่อน"
