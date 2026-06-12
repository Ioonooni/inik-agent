# i nik V2 Checkpoint

## Stable Tag
- v2-auth-memory-stable

## Completed
- Removed demo_user override from auth flow
- User ID now comes from login/session path
- Added auth flow static regression test
- Added auth regression into smoke_check.py
- Verified logout clears session state
- Fixed combined fact extraction:
  - "ฉันชื่ออุ่น และฉันชอบหลุมดำ"
  - name = อุ่น
  - likes = หลุมดำ
- Added regression test for combined fact extraction

## Verified
- python smoke_check.py passes
- acceptance_checks.py passes
- git status clean

## Next Safe V2 Task
Improve runtime reliability only when a real bug appears, or start the next planned V2 system explicitly.
