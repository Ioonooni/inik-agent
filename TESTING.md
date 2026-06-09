# i nik — Final Test Matrix

This file documents the core system tests for the i nik AI Character Interaction Prototype.

## Test 1 — Basic Character Response

Input:
สวัสดี

Expected:
- i nik responds in character
- Response does not sound like a generic AI assistant
- Tone feels curious, playful, or observant

Status:
Not tested / Passed / Failed

---

## Test 2 — Fact Memory

Input:
ฉันชื่อไออุ่น

Expected:
- The system extracts the user name
- Sidebar Memory shows: name: ไออุ่น

Status:
Passed

---

## Test 3 — Name Recall

Input:
ฉันชื่ออะไร

Expected:
- i nik answers using stored memory
- It should answer: ไออุ่น
- It should not say it does not know

Status:
Passed

---

## Test 4 — Relationship Engine

Input:
วันนี้ฉันรู้สึกเหนื่อยมาก

Expected:
- Trust increases
- Familiarity increases
- i nik responds with emotional awareness
- i nik does not over-comfort or act like a therapist

Status:
Not tested / Passed / Failed

---

## Test 5 — Curiosity Signal

Input:
ทำไมมนุษย์ต้องมีความทรงจำ

Expected:
- Curiosity increases
- i nik responds through its worldview
- Response should not become a formal essay

Status:
Not tested / Passed / Failed

---

## Test 6 — Stage Progression

Input:
Send multiple messages until Intimacy Score passes stage thresholds.

Expected:
- Observer: 0–34
- Gremlin: 35–74
- Treasure: 75–100
- Sidebar updates correctly

Status:
Not tested / Passed / Failed

---

## Test 7 — Reward System

Input:
Send messages until Points reach a reward trigger.

Expected:
- Reward message appears
- Reward item is added to Inventory
- Inventory persists after refresh

Status:
Not tested / Passed / Failed

---

## Test 8 — Persistent Memory

Input:
Refresh the page after storing user facts.

Expected:
- User name remains stored
- Inventory remains stored
- Intimacy and Points do not reset

Status:
Not tested / Passed / Failed

---

## Notes

Known limitations:
- Memory currently uses JSON-based persistence
- This is suitable for prototype demonstration
- Production version should use SQLite, Supabase, or PostgreSQL
- Gemini free-tier quota may limit testing