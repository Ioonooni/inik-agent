import os

def dump_context(filepath, search_term, lines_before=5, lines_after=10):
    if not os.path.exists(filepath):
        print(f"❌ ไม่พบไฟล์: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if search_term in line:
            found = True
            print(f"\n🔍 เจอ '{search_term}' ในไฟล์ {filepath} (บรรทัดที่ {i+1}):")
            start = max(0, i - lines_before)
            end = min(len(lines), i + lines_after + 1)
            print("-" * 50)
            for j in range(start, end):
                marker = ">> " if j == i else "   "
                print(f"{j+1:4d} {marker}{lines[j].rstrip()}")
            print("-" * 50)
    
    if not found:
        print(f"\n⚠️ ไม่เจอคำว่า '{search_term}' ใน {filepath}")

print("=== 🛠️ เริ่มดึงข้อมูลโค้ดปัจจุบัน (Read-Only) ===")
dump_context('app.py', 'route_decision.direct_reply', 5, 10)
dump_context('app.py', 'ขอโทษนะ ตอนนี้ i nik ตอบผ่านโมเดลหลักไม่ได้ชั่วคราว', 10, 5)
dump_context('memory_quality.py', 'def assess_memory_quality', 2, 12)
dump_context('truth_engine.py', 'topic_qualified_like_question', 2, 10)
print("=================================================")
