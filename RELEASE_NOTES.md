# Release Notes — V3 Rick Mode Contract Restore + Frontend Wiring

**Date:** 2026-07-07
**Session scope:** Bug fixes, contract restoration, frontend wiring, deployment config

---

## Repositories Affected

| Repository | Branch | Status |
|---|---|---|
| `Ioonooni/inik-agent` | `main` | Merged — backend fixes live |
| `Ioonooni/inik-cafe` | `feat/rick-mode-active-state` | Pushed — awaiting PR merge + Vercel redeploy |

---

## Bugs Fixed

### Bug 1 — Memory write gate incorrectly stored recall questions as facts
**File:** `facts.py`
**Root cause:** The extraction patterns had no guard to distinguish "what is my name?" (recall intent) from "my name is X" (write intent). Recall questions were being parsed and stored as new facts, overwriting correct values.
**Fix:** Added `_has_recall_intent()` with two-tier logic — explicit update commands (`เรียกฉันว่า`, `ชื่อเล่นคือ`, `จำไว้ด้วย`) bypass the gate; recall markers (`จำได้ไหม`, `รู้ไหม`, terminal `ไหม/มั้ย/ปะ`) block writes. Applied to all write paths: name, favorite\_color, likes, interests, pet\_name.

### Bug 2 — Rick mode preference not persisting across requests
**File:** `inik_api.py`
**Root cause:** `ChatRequest.agent_mode` had default `"inik"`. Pydantic v2 cannot distinguish a client-omitted field from a client-sent `"inik"`. Every request therefore appeared to explicitly select inik, overwriting any saved `preferred_agent_mode` in the user profile.
**Fix:** Detected explicit sends using `model_fields_set`. Preference is now persisted only when the client explicitly includes `agent_mode` in the request body. Omitted fields restore the saved preference instead of overwriting it.

### Bug 3 — Relationship stage derived from flat counter instead of content-based state
**File:** `inik_api.py`
**Root cause:** The active `stage` variable was re-derived from `get_stage(intimacy_score)` — a flat per-message counter — rather than from `relationship_state["relationship_stage"]`, which is set by the content-based relationship logic (trust, familiarity, curiosity, attachment).
**Fix:** `stage` now reads from `relationship_state["relationship_stage"]`. `intimacy_score` increment reduced from +10 to +1 per message (display counter only; no longer drives stage).

### Bug 4 — ชื่อเล่น variants not captured by extraction patterns
**File:** `facts.py`
**Root cause:** `_EXPLICIT_UPDATE_RE` only matched `ชื่อเล่นคือ` but not `ชื่อเล่นฉันคือ` or `ชื่อเล่นเราคือ`. The name extraction pattern had the same gap. Users saying their nickname with a pronoun had writes silently blocked.
**Fix:** Extended `_EXPLICIT_UPDATE_RE` to `ชื่อเล่น(?:ฉัน|เรา)?คือ`. Added matching regex to `name_patterns`.

### Bug 5 — Rick suggestion UI missing from deployed frontend
**File:** `inik-cafe/src/App.tsx`, `inik-cafe/vercel.json`
**Root cause:** The frontend source (`Ioonooni/inik-cafe`) predated V3 Rick mode by 8 days. The Rick UI had never been built into the deployed frontend. Additionally, no `vercel.json` existed, so `/api/*` calls in production fell through without a rewrite target.
**Fix (additive on top of existing inline handoff card):**
- `activeMode` state variable — tracks current session mode persistently
- `send()` includes `agent_mode` only when `activeMode !== "inik"` (preserves backend `model_fields_set` detection)
- `send()` reads `d.agent_mode` from responses to stay in sync with backend routing
- "Talk to Rick Royce →" button (already present inline in message bubbles) now also sets `activeMode`
- Header bar mode indicator pill: **I NIK** / **RICK ROYCE** / **HYBRID**
- `← i nik` back button in input bar (visible only when `activeMode === "rick_royce"`)
- `vercel.json` with rewrite: `/api/:path*` → `https://inik-agent.onrender.com/api/:path*`

---

## Commits

### `Ioonooni/inik-agent` — `main`

| Hash | Description |
|---|---|
| `2b4018a` | Fix three root-cause bugs: memory write gate, Rick mode persistence, relationship stage |
| `ab69776` | Add ชื่อเล่น extraction pattern and close `_EXPLICIT_UPDATE_RE` gap |
| `7cd8a96` | Restore V3 frontend contract: inik default, explicit-only preference persistence |

### `Ioonooni/inik-cafe` — `feat/rick-mode-active-state`

| Hash | Description |
|---|---|
| `27f83c3` | Add persistent Rick mode state, header indicator, back button, vercel.json |

---

## Files Changed

### `Ioonooni/inik-agent`

| File | Type | Summary |
|---|---|---|
| `facts.py` | Modified | Write gate, nickname patterns, stop phrases |
| `inik_api.py` | Modified | `model_fields_set` detection, stage alignment, `agent_mode` default restored to `"inik"` |
| `test_v3_contract_restore.py` | New | 15 tests: default value, `model_fields_set`, persistence gate, routing, `suggested_agent` gate, preference restore |
| `test_nickname_extraction.py` | New | 13 tests: nickname variants, memory gate regression |

### `Ioonooni/inik-cafe`

| File | Type | Summary |
|---|---|---|
| `src/App.tsx` | Modified | `activeMode` state, `send()` conditional `agent_mode`, header pill, back button |
| `vercel.json` | New | Production API rewrite to Render backend |

---

## Test Results

```
28 passed, 0 failed
  test_v3_contract_restore.py   15 passed
  test_nickname_extraction.py   13 passed
```

Frontend build: `tsc -b && vite build` — zero TypeScript errors, 233 kB bundle.

---

## Deployment Status

| Layer | Service | Status |
|---|---|---|
| Backend | Render (`inik-agent.onrender.com`) | Live on `main` — all backend fixes active |
| Frontend | Vercel (`inik-cafe.vercel.app`) | NOT YET REDEPLOYED — `feat/rick-mode-active-state` pushed but not merged |
| Vercel project link | `Ioonooni/inik-cafe` | Reported "Project Link not found" — requires reconnection on Vercel dashboard |

**Blocking deployment steps (in order):**
1. Merge `feat/rick-mode-active-state` → `main` in `Ioonooni/inik-cafe`
2. On Vercel dashboard: reconnect project to `Ioonooni/inik-cafe`, Root Directory = *(repo root)*, branch = `main`
3. Build command: `npm run build` / Output: `dist`
4. Trigger redeploy

---

## Known Remaining Issues

1. **Vercel project link is broken.** Frontend is not auto-deploying. Manual reconnection on the Vercel dashboard is required before any frontend change reaches production.

2. **`vercel.json` rewrite not live yet.** Until the branch is merged and Vercel is reconnected, production `/api/chat` calls have no rewrite target. The current production frontend may be returning network errors or falling back to the Thai error message.

3. **`sendWithAgent()` does not update `activeMode` on its own response path.** When `sendWithAgent()` is called (via "Talk to Rick Royce →"), it does not read `d.agent_mode` from the response. The `activeMode` is set to `"rick_royce"` immediately on click, but if the backend returns a different `agent_mode` (e.g., `"hybrid"`), the state will not reflect it. Only the main `send()` path reads `d.agent_mode`.

4. **README example shows `agent_mode: "auto"` in curl sample.** The `README.md` (line 417) contains a curl example with `"agent_mode": "auto"`. After the V3 contract restoration, `"auto"` is no longer a valid named mode and will not save a preference. The README example should be updated to use `"rick_royce"` or `"inik"`.

5. **No end-to-end production verification performed.** The Render backend is live but could not be reached from this environment (proxy 403). The complete frontend → backend flow has not been tested in production this session.

---

## Recommended Next Milestone

**V3.1 — Production Verification + Reconnection**

1. Reconnect Vercel to `Ioonooni/inik-cafe` (unblocks all frontend deployments)
2. Merge `feat/rick-mode-active-state` → `main` in `inik-cafe`
3. Manual QA walkthrough against live URLs:
   - Default inik flow: confirm `agent_mode` absent from request body
   - Strategic message: confirm Rick suggestion card appears in message bubble
   - Click "Talk to Rick Royce →": confirm header pill changes to RICK ROYCE, subsequent messages include `agent_mode: "rick_royce"`
   - Click "← i nik": confirm mode resets, pill returns to I NIK
4. Fix `sendWithAgent()` to also read `d.agent_mode` from response (issue #3 above)
5. Update `README.md` curl example to remove `"agent_mode": "auto"` (issue #4 above)
