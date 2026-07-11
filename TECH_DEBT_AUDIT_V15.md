# Technical Debt Audit — i nik V1.5

**Date:** 2026-07-11  
**Scope:** inik-agent (backend) · inik-cafe (frontend)  
**Auditor:** Senior-engineer review pass — inspect only, no edits  
**Baseline commits:** inik-agent `f46c402` · inik-cafe `6543a48`

---

## ARCH — Architecture Debt

---

### ARCH-01 · Parallel server implementations diverging

**Evidence:** `app.py:1` (`import streamlit as st`), `inik_api.py:1` (`from dotenv import load_dotenv`). Both files implement `/chat`-equivalent logic independently. Key divergences confirmed:

- Intimacy increment: `app.py:837` uses `+10`; `inik_api.py:83` uses `+1`
- Chat history: `app.py:876` calls `build_chat_history(st.session_state.messages, limit=10)` with no `active_agent_mode`; `inik_api.py:129` now passes `active_agent_mode=agent_mode`
- `app.py` has no Rick/hybrid routing — all memory saves are tagged `"agent_mode": "inik"` (line 828)
- `app.py` saves memory via `st.session_state` (Streamlit) + separate Supabase path; `inik_api.py` uses `load_memory`/`save_memory` from `memory_gateway.py`

**Root cause:** `app.py` was the original Streamlit prototype; `inik_api.py` is the production FastAPI server. No formal deprecation of `app.py`.

**Current impact:** Every bug fixed in `inik_api.py` is absent in `app.py`. The history isolation fix (`f46c402`) exists only in the FastAPI path. If `app.py` is still used by anyone, they get unfiltered mixed-mode history and incorrect intimacy counts.

**Failure probability:** 35% — low if nobody is using the Streamlit app, high if they are.

**Severity:** High  
**Fix effort:** L  
**Regression risk:** Medium  
**Fix when:** Before next milestone  
**Remediation:** Formally deprecate `app.py`: add a startup warning banner, move it to `legacy/app.py`, redirect any active Streamlit deployment to the FastAPI API. Do not delete until confirmed zero traffic.  
**If left 3–6 months:** Feature parity gap widens with every API fix. If Streamlit app is active, users on it experience increasingly incorrect behavior.

---

### ARCH-02 · `supabase_memory.py` imports `streamlit` at module level

**Evidence:** `supabase_memory.py:5` (`import streamlit as st`), `supabase_memory.py:24` (`return st.secrets.get(name)`). This module is imported by `memory_gateway.py:9` which is imported by `inik_api.py:21`. FastAPI boot imports Streamlit.

**Root cause:** `get_secret_value()` was written to work in both Streamlit and non-Streamlit contexts. The `st.secrets.get()` call is inside a `try/except`, so it silently returns `None` when Streamlit is not initialized. But the `import streamlit` at line 5 means streamlit must be importable.

**Current impact:** Streamlit is in `requirements.txt` so it installs. The `st.secrets` call returns `None` gracefully. Currently not user-visible but represents hidden coupling: removing streamlit from requirements would break the FastAPI path.

**Failure probability:** 20% on dependency change.

**Severity:** Medium  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Replace `get_secret_value()` with `os.getenv(name)` only. Remove the `import streamlit` and `st.secrets` fallback. FastAPI should never depend on `st.secrets`. Same applies to `event_logger.py:4` and `user_identity.py:1`.  
**If left 3–6 months:** A legitimate dependency cleanup that removes streamlit will silently break production.

---

### ARCH-03 · `event_logger.py` and `user_identity.py` import `streamlit`

**Evidence:** `event_logger.py:4` (`import streamlit as st`), `event_logger.py:56` (`st.secrets.get("N8N_EVENT_WEBHOOK_URL")`). `user_identity.py:1` (`import streamlit as st`), `user_identity.py:22` (`st.session_state.get("user_id")`).

**Root cause:** Same as ARCH-02 — these modules were written for Streamlit and re-imported in the FastAPI path.

**Current impact:** Same transitive coupling. `user_identity.py` reads `st.session_state` which is empty/missing in a FastAPI context. If called from FastAPI, it silently falls back (the code has a `try/except`).

**Failure probability:** 15%.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Same as ARCH-02: `os.getenv()` only. Note: `user_identity.py` is not currently imported by `inik_api.py` — verify before touching.  
**If left 3–6 months:** Same risk profile as ARCH-02.

---

### ARCH-04 · `app.py` `build_chat_history()` call lacks mode isolation

**Evidence:** `app.py:876` calls `build_chat_history(st.session_state.messages, limit=10)` — no `active_agent_mode`. After commit `f46c402`, `memory.py` supports the parameter but `app.py` was not updated.

**Root cause:** Two-server architecture means a fix to `inik_api.py` does not propagate to `app.py` automatically.

**Current impact:** If `app.py` is used, all assistant messages appear in the history regardless of mode, reverting the isolation fix.

**Failure probability:** 30% if Streamlit app has users.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone (or when ARCH-01 is addressed)  
**Remediation:** Pass `active_agent_mode="inik"` to the call in `app.py:876` (app.py only ever routes as inik).  
**If left 3–6 months:** Mode isolation only works for half the user population.

---

### ARCH-05 · `react-router-dom` installed but never used

**Evidence:** `inik-cafe/package.json` — `"react-router-dom": "^7.17.0"` in `dependencies`. `App.tsx` uses `useState<PageId>` for page state — no `<Router>`, `<Route>`, `useNavigate`, or `useParams` anywhere in the source.

**Root cause:** Dependency was likely added during scaffolding and never wired up.

**Current impact:** Adds to bundle size. Pages do not have URLs (no `/chat`, `/memories`, etc.) — navigation state is lost on refresh, and deep-linking is impossible.

**Failure probability:** 0% (no production failure, but bundle waste and missing browser Back/Forward support).

**Severity:** Low  
**Fix effort:** XS to remove; M to implement real routing  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Remove `react-router-dom` from `package.json` if not implementing URL routing in the next milestone. Implement routing later as a milestone feature.  
**If left 3–6 months:** Bundle grows. Users cannot bookmark pages or use Back button.

---

### ARCH-06 · `memory_gateway_v2.py` has no `active_agent_mode` on `retrieve_memories_v2`

**Evidence:** `memory_gateway_v2.py:103-117` — `retrieve_memories_v2` and `list_recent_memories_v2` fetch memories from Supabase without filtering by the agent context. RAG memories returned may contain cross-mode context.

**Root cause:** The V2 memory gateway was built before mode isolation was a requirement. The isolation fix only addressed `recent_messages`; the separate `memories_v2` Supabase table is not affected by the same mechanism but could surface cross-mode context.

**Current impact:** Low — RAG memories are general facts and conversation fragments, not conversation-flow entries. Less critical than `recent_messages`.

**Failure probability:** 10%.

**Severity:** Low  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Acceptable debt  
**Remediation:** Add optional `agent_mode` filter to `retrieve_memories_v2` for future use when memories are labeled.  
**If left 3–6 months:** Minor context noise in RAG results; unlikely to surface as a user-visible issue.

---

## DATA — Data and Memory Debt

---

### DATA-01 · Legacy `recent_messages` entries lack `agent_mode` — thin history for existing users

**Evidence:** `inik_api.py:230` (old): `recent_messages.append({"role": "assistant", "content": reply})` — all messages before commit `f46c402` lack `agent_mode`. `memory.py:12-20` now skips assistant entries where `message.get("agent_mode") != active_agent_mode`.

**Root cause:** The isolation fix was not retroactively applied to existing persisted data. The spec correctly states "skip legacy entries" — this is by design — but the transition cost is that existing users see no prior assistant context until new labeled messages accumulate.

**Current impact:** Existing users experience an effective history reset for the assistant side on their first request after the fix is deployed. They will see `"User: ..."` lines but no `"i nik: ..."` lines until new messages arrive.

**Failure probability:** 80% for existing users on next conversation.

**Severity:** Medium  
**Fix effort:** S (one-time Supabase migration to tag old rows `agent_mode: "inik"`) or XS (accept and document)  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Run a one-time Supabase UPDATE to set `agent_mode: "inik"` on all existing assistant entries in `recent_messages` JSON blobs where `agent_mode` is null. Alternatively, add a fallback in `build_chat_history()`: when `active_agent_mode == "inik"`, treat unlabeled entries as `"inik"` (legacy compat). The spec chose the skip approach but a compat fallback for inik-mode only is safe.  
**If left 3–6 months:** All users who chatted before the fix permanently lose their historical inik context. This is a silent quality degradation.

---

### DATA-02 · `preferred_agent_mode` field never pruned from `user_profile`

**Evidence:** `inik_api.py:127` writes `user_profile["preferred_agent_mode"] = agent_mode`. The `user_profile` dict is stored in the Supabase `user_profile` JSON column. This field is now never read for routing (by design) but accumulates in every user's record.

**Root cause:** The V1.5 mode fallback fix made `preferred_agent_mode` write-only. It is persisted but no code reads it for routing decisions.

**Current impact:** Dead data in Supabase. No functional impact. Could confuse future developers who find it in the database and assume it controls routing.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Acceptable debt  
**Remediation:** Add a comment at `inik_api.py:127` explaining the field is persisted for future analytics only and is not read for routing. Or stop writing it. Only if analytics use case is confirmed.  
**If left 3–6 months:** Confusing but harmless.

---

### DATA-03 · `recent_messages` unbounded in Supabase JSON blob

**Evidence:** `inik_api.py:231`: `recent_messages = recent_messages[-20:]` — Python correctly trims to 20 entries before saving. `supabase_memory.py:136`: `"user_profile": user_profile` — the entire user_profile dict (including `recent_messages`) is stored as a JSON blob in one Supabase column.

**Root cause:** The Supabase column has no structural enforcement of the 20-entry cap. The cap is enforced only in the Python layer. If the Python trim is bypassed, entries accumulate. Additionally, after the isolation fix, each entry is now larger (has `agent_mode` key).

**Current impact:** The Python trim is consistent, so in practice bounded. But the row size grows with each entry (each now contains `agent_mode`). Long messages can cause the row to approach Supabase row size limits.

**Failure probability:** 5% under normal use; 25% if a user sends very long messages.

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Acceptable debt  
**Remediation:** Current 20-entry cap is sufficient. No action needed unless Supabase row size errors appear.  
**If left 3–6 months:** Stable. Only a concern if message content size grows significantly.

---

### DATA-04 · `row_to_memory()` silent null fallback on `user_profile`

**Evidence:** `supabase_memory.py:85`: `memory["user_profile"] = row.get("user_profile") or memory["user_profile"]`. If `user_profile` is `null` or empty `{}` in Supabase, this silently substitutes a brand-new default profile, discarding all personality/adaptive state.

**Root cause:** Defensive default substitution without distinguishing "user has no profile yet" from "Supabase returned unexpected null."

**Current impact:** If a Supabase row corruption sets `user_profile` to null, the user silently loses their full profile. No error is raised. No logging.

**Failure probability:** 5%.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Log a warning when `user_profile` is null for an existing row. Keep the fallback but make the fallback visible.  
**If left 3–6 months:** Silent data loss in edge cases.

---

## TEST — Testing Debt

---

### TEST-01 · `test_v3_contract_restore.py` uses mirror model instead of production `ChatRequest`

**Evidence:** `test_v3_contract_restore.py:11` (docstring): "Uses a mirror model (`_Req`) instead of importing inik_api directly". `test_v3_contract_restore.py:25`: `class _Req(BaseModel)` redefines the request model independently.

**Root cause:** `inik_api.py` has `dotenv` / `google-generativeai` dependencies that fail to load in the bare pytest venv. The test author created a parallel model to avoid those imports.

**Current impact:** If `ChatRequest` in `inik_api.py` is modified (e.g., new field added, `agent_mode` default changed), `test_v3_contract_restore.py` continues to pass while production behavior diverges.

**Failure probability:** 30% of catching a real regression.

**Severity:** High  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add `requirements-test.txt` with `pydantic`, `fastapi`, `python-dotenv` — no `google-generativeai` needed. Import `ChatRequest` from a thin wrapper that avoids the Gemini initialization (mock `GEMINI_API_KEY`). Or refactor the Pydantic model into `models.py` that has no Gemini dependency.  
**If left 3–6 months:** The test provides false confidence in the contract — passes while production is broken.

---

### TEST-02 · No real endpoint test using FastAPI `TestClient`

**Evidence:** No `from starlette.testclient import TestClient` or `from fastapi.testclient import TestClient` found in any `test_*.py` file. All route logic in `inik_api.py` is untested at the HTTP layer.

**Root cause:** Test environment lacks full dependency stack for FastAPI startup.

**Current impact:** CORS headers, request parsing, `model_fields_set` behavior, HTTP status codes, response shape — none are tested. A syntax error in `inik_api.py` would not be caught by the test suite.

**Failure probability:** 40% of missing a real regression.

**Severity:** High  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Create `test_api_endpoints.py` using `TestClient` with mocked `model.generate_content` and mocked `load_memory`/`save_memory`. Test at minimum: `/health` returns 200, `/api/chat` with missing `user_id` returns 400, `/api/chat` returns `reply` key, `/api/chat` with `agent_mode: "rick_royce"` returns `agent_mode: "rick_royce"`.  
**If left 3–6 months:** Each API change ships without any endpoint-level safety net.

---

### TEST-03 · `test_v3_runtime_routing.py` uses `run()` function — not collected by pytest

**Evidence:** `test_v3_runtime_routing.py` — all logic is inside a `run()` function with no `def test_*` prefix. Pytest only collects functions prefixed `test_`. Running `pytest test_v3_runtime_routing.py` collects 0 items and reports success.

**Root cause:** The file was written as a script, not as a pytest test module.

**Current impact:** Routing tests appear to be covered but are silently not run by pytest. 5 routing assertions are dead.

**Failure probability:** 5% (logic tested elsewhere), but false coverage signal.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Rename `run()` to `test_routing_cases()` and add `if __name__ == "__main__": run()` as the script entry point.  
**If left 3–6 months:** Developers believe routing tests are passing when they are never executed.

---

### TEST-04 · `app.py` Streamlit logic is entirely untested

**Evidence:** `app.py` is 1098 lines. No `test_app.py` exists. All 52 test files target either pure functions or the FastAPI path. `app.py` imports from 30+ modules but its response pipeline, reward checks, planner calls, and memory saves are never exercised by tests.

**Root cause:** Streamlit UI logic is hard to unit test without a running Streamlit session.

**Current impact:** Regressions in `app.py` logic (including the ARCH-01 divergences) are invisible to CI.

**Failure probability:** 50% of missing a regression when changing shared modules.

**Severity:** Medium  
**Fix effort:** M  
**Regression risk:** Low  
**Fix when:** Later (or when app.py is deprecated)  
**Remediation:** Extract all business logic from `app.py` into pure functions importable without Streamlit. Test those functions. Leave only UI wiring in `app.py`.  
**If left 3–6 months:** Any change to a shared module could break `app.py` silently.

---

### TEST-05 · README states "109 checks passed" — stale count

**Evidence:** `README.md` under "Latest Regression Result": "**109 checks passed** / **0 checks failed**". Current test suite has 52 test files; counts are now different after V1.5 additions (`test_chat_history_isolation.py` adds 8, `test_v3_contract_restore.py` adds 15, etc.).

**Root cause:** README was written at a point in time and not updated after new tests were added.

**Current impact:** Misleading signal to reviewers. The actual count is higher, but a reader might believe coverage decreased if they count fewer than 109.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Update README to either reflect the current count or replace with "see CI for current count."  
**If left 3–6 months:** Cosmetic issue only.

---

### TEST-06 · No frontend tests

**Evidence:** `inik-cafe/package.json` — no test script, no `@testing-library/react`, no `vitest`, no `jest`. The frontend is entirely untested.

**Root cause:** Frontend was developed rapidly without test infrastructure.

**Current impact:** Every App.tsx change ships without any validation beyond TypeScript compilation.

**Failure probability:** 40% of shipping a logic regression.

**Severity:** Medium  
**Fix effort:** M  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Add `vitest` + `@testing-library/react`. Initial coverage: `getStableUserId()` returns consistent value, `send()` includes `agent_mode` when `activeMode !== 'inik'`, `setActiveMode` is called on Rick button click.  
**If left 3–6 months:** Frontend regressions are caught only by manual QA.

---

## DEPLOY — Deployment and Repository Debt

---

### DEPLOY-01 · `inik-cafe-source.zip` (351KB) permanently in backend git history

**Evidence:** `git show --stat 07621ad` — `A inik-cafe-source.zip` added at that commit. `git cat-file -s 07621ad:inik-cafe-source.zip` → 350999 bytes. The file is gitignored from the working tree but permanently stored in git object storage.

**Root cause:** The zip was committed and then the directory was gitignored, but git history is immutable without a force-push rewrite.

**Current impact:** Every `git clone` of `inik-agent` downloads an extra 351KB binary. The blob persists indefinitely. No security risk since the zip contains frontend source only.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** M (requires `git filter-branch` or BFG + force-push)  
**Regression risk:** High (force-push rewrites history for all collaborators)  
**Fix when:** Acceptable debt (cost of rewriting history outweighs benefit for a dev-only artifact)  
**Remediation:** If repo history cleanliness matters: use BFG Repo Cleaner to remove the blob and force-push. Otherwise accept it.  
**If left 3–6 months:** No functional impact. Slightly larger clones.

---

### DEPLOY-02 · 13 `.bak` files committed in `inik-cafe/src/`

**Evidence:** `ls /tmp/inik-cafe-repo/src/*.bak*` — 13 files including `App.tsx.bak_before_rick_handoff`, `App.tsx.broken_backup`, etc. Frontend `.gitignore` does not exclude `*.bak*`.

**Root cause:** Development-time backup practice of copying the file before editing, without adding `*.bak*` to `.gitignore`.

**Current impact:** Repository noise. Vite does not bundle `.bak` files. No runtime impact. But diff readability is reduced and the repo looks unprofessional.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add `*.bak*` and `*.broken_backup` to `inik-cafe/.gitignore`. Delete the committed files with `git rm`. One commit.  
**If left 3–6 months:** Repository continues to accumulate backup artifacts.

---

### DEPLOY-03 · `inik-dist.zip` and `memory_debug.txt` committed in frontend repo root

**Evidence:** `ls /tmp/inik-cafe-repo/` shows `inik-dist.zip` and `memory_debug.txt` in the repository root alongside production source.

**Root cause:** Development artifacts committed without `.gitignore` exclusion.

**Current impact:** No runtime impact. Repository noise. `memory_debug.txt` may contain user data or debug traces — needs review before publishing.

**Failure probability:** 0% user-visible. Potential privacy concern for `memory_debug.txt`.

**Severity:** Low (Medium if `memory_debug.txt` contains user data)  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone (check `memory_debug.txt` content first)  
**Remediation:** Add `*.zip`, `*_debug.txt` to `.gitignore`. Remove with `git rm`.  
**If left 3–6 months:** If `memory_debug.txt` contains real user data, it is exposed in a public repository.

---

### DEPLOY-04 · `requirements.txt` has no version pins

**Evidence:** `requirements.txt` lines 5-8: `fastapi`, `uvicorn`, `python-dotenv`, `requests`, `supabase==2.31.0` — only `supabase` is pinned. `google-generativeai`, `streamlit`, `fastapi`, `uvicorn` are unpinned.

**Root cause:** Pinning was not enforced during development.

**Current impact:** A `pip install` during a Render deploy could pull a breaking version of `fastapi`, `google-generativeai`, or `streamlit`. FastAPI and google-generativeai both have frequent breaking changes.

**Failure probability:** 30% over the next 3–6 months as new releases ship.

**Severity:** High  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Now  
**Remediation:** Pin every package: `pip freeze > requirements-frozen.txt` from the current working environment and use those pins. At minimum pin `fastapi`, `uvicorn`, `google-generativeai`, `streamlit`, `pydantic`.  
**If left 3–6 months:** Production deploys can break silently when upstream packages release breaking changes.

---

### DEPLOY-05 · No `render.yaml` or `Procfile` — Render config is dashboard-only

**Evidence:** No `render.yaml`, `Procfile`, or equivalent in `inik-agent/`. Deploy configuration exists only in the Render dashboard.

**Root cause:** Dashboard-configured deployment was sufficient for initial launch.

**Current impact:** Start command, environment variable names, health check path, port, and Python version are not in version control. If the Render service is deleted or recreated, configuration must be re-entered manually from memory.

**Failure probability:** 20% on service recreation or team hand-off.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add `render.yaml` to `inik-agent/` with service name, start command (`uvicorn inik_api:app --host 0.0.0.0 --port 10000`), environment variable names (not values), and health check path (`/health`).  
**If left 3–6 months:** One accidental service deletion causes a full manual configuration recovery.

---

### DEPLOY-06 · `vercel.json` hardcodes backend URL

**Evidence:** `inik-cafe/vercel.json:4`: `"destination": "https://inik-agent.onrender.com/api/:path*"`.

**Root cause:** URL was inlined during the initial vercel.json creation.

**Current impact:** If the backend is migrated to a different host or URL, the frontend rewrite breaks without a code change and redeploy.

**Failure probability:** 10% (only if backend URL changes).

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Acceptable debt  
**Remediation:** Use a Vercel environment variable: `VITE_API_BASE_URL` is already supported in `App.tsx:361`. The Vercel rewrite would need to support env var substitution, which Vercel does not natively support in `vercel.json`. Alternative: document this file as the single place to update if the backend URL changes.  
**If left 3–6 months:** No impact unless backend URL changes.

---

### DEPLOY-07 · Release tags `v1.5.0-backend` / `v1.5.0-frontend` exist locally only

**Evidence:** From QA checkpoint and session history: annotated tags were created locally but proxy returned 403 on `git push origin v1.5.0-backend`. Tags are not visible on GitHub.

**Root cause:** Proxy restriction on tag ref pushes during the session. Tags were never pushed from a non-proxied environment.

**Current impact:** No release tags exist on GitHub. Version tracking is commit-hash only.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** XS (push from local machine)  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Push tags from a non-proxied environment: `git push origin v1.5.0-backend v1.5.0-frontend`.  
**If left 3–6 months:** No semantic release history on GitHub.

---

## FE — Frontend Debt

---

### FE-01 · Single 891-line `App.tsx` monolith

**Evidence:** `App.tsx` — 891 lines containing: 5 global constants, 3 CSS animation blocks, `StarField` component, `TopNav` component, `NikCharacter` component, `HomePage` component, `ChatPage` component, `MemoriesPage` component, `JourneyPage` component, `ProfilePage` component, `AboutPage` component, all type definitions, all API calls, all state management.

**Root cause:** Single-file development style during rapid prototyping.

**Current impact:** Every edit requires navigating an 891-line file. Risk of accidental modification of unrelated components. Build is fast but developer experience degrades with size.

**Failure probability:** 20% of an accidental regression from a large-file edit.

**Severity:** Medium  
**Fix effort:** M  
**Regression risk:** Medium  
**Fix when:** Later  
**Remediation:** Extract one component at a time into `src/components/`. Priority order: `ChatPage` (most complex, most frequently changed), then page components. Keep `App.tsx` as the root router only.  
**If left 3–6 months:** Developer velocity decreases. Risk of merge conflicts increases with any team growth.

---

### FE-02 · No mobile/responsive layout — fixed pixel widths throughout

**Evidence:** `App.tsx:194`: `gridTemplateColumns:'1fr 1fr'` for HomePage. `App.tsx:471`: `width:248` for chat sidebar. `App.tsx:196`: `padding:'70px 50px 70px 72px'`. No `@media` queries. No `min-width: 0` guards. No viewport-relative units.

**Root cause:** Desktop-first design without responsive breakpoints during prototyping.

**Current impact:** Layout breaks on screens narrower than ~900px. Sidebar overlaps content. Chat area becomes unusable on mobile. The app is inaccessible to mobile users.

**Failure probability:** 85% on mobile devices.

**Severity:** High  
**Fix effort:** M  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add CSS media queries for breakpoints at 768px and 480px. At minimum: collapse sidebar on mobile (`display:none`), make grid single-column, ensure chat input is full-width and accessible. Use `min-width: 0` on flex children to prevent overflow.  
**If left 3–6 months:** Product is effectively desktop-only. Any mobile user sees a broken layout.

---

### FE-03 · `activeMode` not persisted across page reload

**Evidence:** `App.tsx:434`: `const [activeMode,setActiveMode]=useState<string>('inik')`. No `localStorage` read for `activeMode`. `localStorage` stores only `inik_user_id` (lines 313-322).

**Root cause:** Intentional design decision documented in session notes: mode is ephemeral per session.

**Current impact:** After page reload, user is always in inik mode even if they were in Rick mode. The backend state reflects the mode from the last successful request, but the frontend resets. On the next `send()`, no `agent_mode` is sent (since `activeMode === 'inik'`), so the backend also routes to inik.

**Failure probability:** 70% of users noticing the reset after a reload.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Persist `activeMode` to `localStorage` alongside `inik_user_id`. On init, read `localStorage.getItem("inik_agent_mode") || "inik"` as the initial `useState` value. Clear on "← i nik" button click.  
**If left 3–6 months:** Users in Rick mode regularly lose their mode context on page refresh, creating confusing conversation continuity.

---

### FE-04 · `fetchRuntimeState()` called independently on 4 page mounts

**Evidence:** `ChatPage` `useEffect` (line ~437), `MemoriesPage` `useEffect` (line ~627), `JourneyPage` `useEffect` (line ~720), `ProfilePage` `useEffect` (line ~798) — each independently fetches `/api/state`. No shared state, no deduplication, no cache.

**Root cause:** Each page is a self-contained component with no shared state context.

**Current impact:** Navigating between pages triggers unnecessary API calls. Each navigation fires a `/api/state` request against the Render backend. On the Render free tier, each call may trigger a cold start or add latency.

**Failure probability:** 0% user-visible failure; 40% of unnecessary latency.

**Severity:** Low  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Lift `runtimeState` to the `INikApp` root component with a shared `useState` + one `useEffect`. Pass as props or use a minimal React Context. Eliminates 3 of the 4 redundant fetches.  
**If left 3–6 months:** Render API call volume grows with user navigation patterns; no hard failure.

---

### FE-05 · Sidebar "Recent Fragments" is hardcoded static content

**Evidence:** `App.tsx:509-514`: `['First conversation','You mentioned stars','The broken universe','A quiet evening'].map(...)` — these four strings are hardcoded and never connected to real backend data.

**Root cause:** UI placeholder from initial scaffolding; backend data was never wired to this panel.

**Current impact:** Users see the same four static fragments regardless of their actual conversation history. Real memories appear only on the Memories page.

**Failure probability:** 0% failure; 100% incorrect content.

**Severity:** Low  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Use `state.recent_messages` (already fetched) to populate the sidebar with the last 4 user messages. Replace hardcoded array.  
**If left 3–6 months:** Feature appears broken/fake to users who notice.

---

### FE-06 · No `.env.example` in frontend; no documented environment setup

**Evidence:** No `.env.example` in `inik-cafe/`. `App.tsx:361` uses `import.meta.env.VITE_API_BASE_URL`. There is no documentation of what environment variables are needed for local development.

**Root cause:** Single-developer project; environment setup was known by the author.

**Current impact:** Any new developer cloning `inik-cafe` does not know about `VITE_API_BASE_URL`. They run with the production API URL by default, which may not be intended.

**Failure probability:** 0% user-visible.

**Severity:** Low  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add `inik-cafe/.env.example` with `VITE_API_BASE_URL=http://localhost:8000`.  
**If left 3–6 months:** Onboarding friction for any new contributor.

---

### FE-07 · `App.tsx.broken_backup` committed in `src/`

**Evidence:** `ls /tmp/inik-cafe-repo/src/` shows `App.tsx.broken_backup` alongside the 13 `.bak_*` files.

**Root cause:** Same as DEPLOY-02.

**Current impact:** Confusing name implies the current `App.tsx` had a broken state — could mislead developers. Same repository noise issue.

**Severity:** Low — addressed together with DEPLOY-02.

---

## BE — Backend Debt

---

### BE-01 · `app.py` and `inik_api.py` diverge on intimacy increment

**Evidence:** `app.py:837`: `st.session_state.intimacy_score + 10`; `inik_api.py:83`: `min(100, intimacy_score + 1)`. Ten-fold difference per message.

**Root cause:** `app.py` was never updated when `inik_api.py` changed the increment logic. These are two independently maintained implementations.

**Current impact:** Users on the Streamlit path level up 10× faster than users on the FastAPI path. Relationship stage progression is inconsistent across surfaces.

**Failure probability:** 35% if Streamlit users exist.

**Severity:** High  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone (as part of ARCH-01 remediation)  
**Remediation:** Align `app.py:837` to `+1` and cap at 100, matching `inik_api.py`. Or deprecate app.py.  
**If left 3–6 months:** State divergence increases. Streamlit users accumulate relationship stages faster than API users, creating inconsistent product behavior.

---

### BE-02 · `print(f"[memory_v2] save failed: {error}")` exposes exception string

**Evidence:** `inik_api.py:146`: `print(f"[memory_v2] save failed: {error}")`. Uses f-string with raw exception object, which may include Supabase endpoint URLs, internal error messages, or response payloads in the string representation.

**Root cause:** This line was not caught by the V1.5 security audit that established the `type(exc).__name__` rule.

**Current impact:** Exception detail is printed to Render logs (stdout). If Supabase SDK exceptions include API key fragments, URLs, or user data references in their string representation, they appear in logs. This violates the established security constraint.

**Failure probability:** 30% of a Supabase save failure exposing internal detail in logs.

**Severity:** High (security constraint violation)  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Now  
**Remediation:** Replace with `print(f"[memory_v2] save failed: {type(error).__name__}")`.  
**If left 3–6 months:** Every Supabase failure leaks internal detail to logs.

---

### BE-03 · `memory_gateway_v2.py` multiple `str(error)` in return dicts

**Evidence:** `memory_gateway_v2.py:41` (`errors.append(str(wb_error))`), `:49` (`str(exc)`), `:95` (`str(error)`), `:125` (`str(error)`), `:132` (`str(error)`), `:157` (`str(error)`), `:164` (`str(error)`).

**Root cause:** Return dicts include exception strings for internal debugging. Callers (`inik_api.py:145`) wrap the call in `try/except` and currently only print the top-level error, but the dicts themselves contain SDK exception strings.

**Current impact:** The return dict `supabase_error` fields contain raw SDK exception strings. If any caller logs or returns these dicts (e.g., in a future debug endpoint), Supabase URLs or credentials could be exposed. Currently these dicts are not returned to the API client, but the pattern is fragile.

**Failure probability:** 10% of exposure via future code path.

**Severity:** Medium  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Replace `str(error)` with `type(error).__name__` in return dicts. If the caller needs to know what failed, use the error class name, not the message.  
**If left 3–6 months:** Low current risk but grows as more callers use the return dicts.

---

### BE-04 · No request body size limit or rate limiting

**Evidence:** `inik_api.py` — no body size validation, no rate limiting middleware, no `limit_body_size` parameter. FastAPI defaults allow unlimited body size.

**Root cause:** Not implemented during MVP development.

**Current impact:** A single client can send arbitrarily large messages. On the free Gemini tier, very long prompts may cause quota to exhaust faster. A malicious client can send 1MB messages repeatedly.

**Failure probability:** 15% under adversarial conditions; 5% under normal use.

**Severity:** Medium  
**Fix effort:** S  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** Add `message: str = Field(..., max_length=4000)` to `ChatRequest`. Add SlowAPI or a simple per-IP counter as a rate limiter. At minimum, cap message length.  
**If left 3–6 months:** Quota exhaustion and potential denial-of-service via oversized payloads.

---

### BE-05 · `/api/state` returns full user data with no authentication

**Evidence:** `inik_api.py:272-297`: `GET /api/state?user_id=X` returns `user_facts`, `recent_messages`, `user_profile`, `relationship_state`, `intimacy_score`, `points` for any `user_id` string.

**Root cause:** Authentication was scoped out of the MVP. `user_id` is the only gate.

**Current impact:** Knowing any user's UUID (which is a localStorage value) gives read access to all their personal facts, conversation history, and relationship state. The UUID is not secret — it is sent in every POST request body and could be captured.

**Failure probability:** 20% of a user data exposure given an adversarial caller with a captured UUID.

**Severity:** High  
**Fix effort:** L (full auth) or S (read key / token on the state endpoint)  
**Regression risk:** Medium  
**Fix when:** Before next milestone  
**Remediation:** Near-term: require a simple `read_token` or signed session for `/api/state`. Long-term: implement full Supabase Auth. At minimum: add a server-side note in the response that this endpoint is read-only and document it as unauthenticated in the README.  
**If left 3–6 months:** User data is accessible to anyone with the UUID. As UUID distribution grows (frontend sends it in request logs), exposure risk increases.

---

### BE-06 · `prompt_builder.py` 457 lines — mixed concerns, hard to test sections

**Evidence:** `prompt_builder.py:1-458` — contains `_tone_from_relationship()`, `_reengagement_context()`, `_extract_profile_signal()`, `_personality_matrix()`, `_adaptive_personality_directive()`, `build_main_prompt()`. All personality, tone, re-engagement, and RAG assembly logic in one file.

**Root cause:** Incremental feature additions to a central prompt construction file.

**Current impact:** The file is testable (no Gemini dependency) but individual sections are not independently testable without constructing large argument objects. Changes to personality logic risk affecting prompt structure for all modes.

**Failure probability:** 20% of an unintended prompt change affecting unrelated paths.

**Severity:** Medium  
**Fix effort:** M  
**Regression risk:** Medium  
**Fix when:** Later  
**Remediation:** Split into `tone_directives.py`, `personality_matrix.py`, `prompt_assembly.py`. Each file is independently testable. `build_main_prompt()` becomes an assembler that calls each module.  
**If left 3–6 months:** File continues to grow with each new personality feature, increasing collision risk.

---

## SEC — Security and Reliability Debt

---

### SEC-01 · `user_id` is a client-controlled UUID with no server-side validation

**Evidence:** `inik_api.py:66-68`: `user_id = (req.user_id or "").strip()` — only validates non-empty. Any string is accepted. `memory_gateway.py:46`: `load_memory(user_id=user_id)` uses this string as the Supabase row key.

**Root cause:** Authentication is scoped out of the MVP.

**Current impact:** One user who discovers another user's UUID has full read/write access to their memory. Supabase has no Row Level Security enforced by the application layer. This is the most significant security gap for a multi-user system.

**Failure probability:** 15% given knowledge of another user's UUID.

**Severity:** Critical  
**Fix effort:** L  
**Regression risk:** Medium  
**Fix when:** Before next milestone  
**Remediation:** Implement Supabase Auth JWT verification in the FastAPI path. Short-term: add server-side session token verification before `load_memory`. The UUID alone should not be the only gate to a user's data.  
**If left 3–6 months:** Risk grows linearly with user count. Each new user is a potential target for any client that captures their UUID from network traffic.

---

### SEC-02 · CORS `allow_origin_regex` matches all GitHub Codespace subdomains

**Evidence:** `inik_api.py:32`: `allow_origin_regex=r"https://.*\.app\.github\.dev"`. This matches any `<anything>.app.github.dev` domain, including Codespace previews from any GitHub user, not just this project's collaborators.

**Root cause:** Added for development convenience (Codespace preview URLs are random subdomains).

**Current impact:** Any GitHub Codespace user can make authenticated cross-origin requests to the production API. Combined with SEC-01, an attacker with a Codespace can brute-force UUIDs from a browser context.

**Failure probability:** 5% of active exploitation.

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Before next milestone  
**Remediation:** If Codespace access is no longer needed for production, remove the `allow_origin_regex`. If still needed for development, scope it to a specific Codespace URL or use environment-based CORS config (strict in production, open in dev).  
**If left 3–6 months:** Low probability but non-zero attack surface.

---

### SEC-03 · Cold-start: `model = None` silently degrades without monitoring

**Evidence:** `inik_api.py:26`: `model = genai.GenerativeModel(MODEL_NAME) if API_KEY else None`. `inik_api.py:221`: `elif not API_KEY: reply = "สัญญาณ Gemini ยังไม่ได้ตั้งค่า GEMINI_API_KEY"`. On Render cold start with missing `GEMINI_API_KEY`, every chat returns the Thai "signal not configured" string instead of an error.

**Root cause:** Defensive design — returns a graceful message instead of 500. But no alerting fires.

**Current impact:** If `GEMINI_API_KEY` is removed from Render env vars, all users get the error string. No exception is raised, no alert fires, no 5xx response is returned to trigger uptime monitors. The `/health` endpoint correctly returns `"gemini_configured": false` but nothing watches it.

**Failure probability:** 5% (env var accidentally cleared during a Render service reset).

**Severity:** Medium  
**Fix effort:** XS  
**Regression risk:** Low  
**Fix when:** Later  
**Remediation:** Return HTTP 503 (Service Unavailable) when `model is None` at request time rather than a success response with an error string. This allows Render health checks or external monitors to detect the failure.  
**If left 3–6 months:** Potential invisible outage where all users receive the error string and no alert fires.

---

## Section A — Total Debt Count by Severity

| Severity | Count |
|---|---|
| Critical | 1 |
| High | 7 |
| Medium | 13 |
| Low | 18 |
| **Total** | **39** |

---

## Section B — Top 5 Debts by Risk-Adjusted Priority

PriorityScore = SeverityWeight × FailureProbability × UserImpact ÷ FixEffort

| Rank | ID | Title | Score | Severity | Effort |
|---|---|---|---|---|---|
| 1 | DEPLOY-04 | Unpinned `requirements.txt` | 2.70 | High | XS |
| 2 | SEC-01 | Client-controlled `user_id` — no server-side auth | 2.40 | Critical | L |
| 3 | BE-02 | `print(str(error))` in memory save — security constraint violation | 1.40 | High | XS |
| 4 | TEST-02 | No FastAPI endpoint test with `TestClient` | 1.20 | High | S |
| 5 | FE-02 | No mobile layout — fixed pixel widths | 1.13 | High | M |

---

## Section C — Fix Now (maximum 3 items)

**Rationale:** Items with XS effort, known security constraint violations, or high probability of an imminent production break.

1. **BE-02** — `inik_api.py:146`: Replace `print(f"[memory_v2] save failed: {error}")` with `print(f"[memory_v2] save failed: {type(error).__name__}")`. One-line fix. Violates the established security constraint today.

2. **DEPLOY-04** — Pin all packages in `requirements.txt`. Run `pip freeze` in the current env and replace unpinned entries. Prevents the next Render deploy from pulling a breaking dependency version. 30-minute task.

3. **TEST-03** — `test_v3_runtime_routing.py`: Rename `run()` to `test_routing_cases()`. 2-line change. Activates 5 currently dead test assertions.

---

## Section D — Before Next Milestone

| ID | Title | Effort |
|---|---|---|
| DATA-01 | Legacy `recent_messages` entries lack `agent_mode` — thin history | XS or S |
| TEST-01 | Mirror model in `test_v3_contract_restore.py` | S |
| TEST-04 (partial) | Add minimal `test_api_endpoints.py` with `TestClient` | S |
| ARCH-02 | Remove `streamlit` import from `supabase_memory.py` | S |
| ARCH-04 | Update `app.py:876` `build_chat_history()` call | XS |
| BE-01 | Align `app.py` intimacy increment to `+1` | XS |
| BE-03 | Replace `str(error)` in `memory_gateway_v2.py` return dicts | S |
| BE-04 | Add `max_length=4000` to `ChatRequest.message` | XS |
| BE-05 | Scope or document `/api/state` data exposure | S |
| DEPLOY-02 | Remove 13 `.bak` files from `inik-cafe/src/` | XS |
| DEPLOY-03 | Remove `inik-dist.zip` and check `memory_debug.txt` content | XS |
| DEPLOY-05 | Add `render.yaml` to `inik-agent/` | XS |
| DEPLOY-07 | Push release tags from non-proxied env | XS |
| FE-02 | Mobile responsive layout | M |
| FE-03 | Persist `activeMode` to `localStorage` | XS |
| FE-06 | Add `.env.example` to `inik-cafe/` | XS |
| SEC-02 | Scope CORS `allow_origin_regex` | XS |

---

## Section E — Do Not Fix Now

| ID | Title | Reason |
|---|---|---|
| ARCH-01 | Deprecate `app.py` | Large effort, needs product decision on Streamlit status |
| ARCH-05 | Remove `react-router-dom` or implement routing | Routing is a product feature decision |
| ARCH-06 | Mode filtering in `retrieve_memories_v2` | No user-visible issue; RAG memories are mode-agnostic |
| DATA-02 | Prune `preferred_agent_mode` | Dead but harmless; no urgency |
| DATA-03 | Supabase JSON blob unbounded | Python cap is working; no evidence of row size issues |
| DATA-04 | `row_to_memory()` silent fallback | Edge case; no current evidence of occurrence |
| DEPLOY-01 | Remove zip from git history | Force-push cost exceeds benefit |
| DEPLOY-06 | Parameterize `vercel.json` backend URL | No route to change backend URL imminently |
| FE-01 | Split `App.tsx` into components | Valid refactor but zero current failures |
| FE-04 | Shared `fetchRuntimeState()` | Latency issue, not a failure |
| FE-05 | Wire sidebar fragments to real data | UI enhancement, not debt |
| FE-07 | `App.tsx.broken_backup` | Covered by DEPLOY-02 |
| BE-06 | Split `prompt_builder.py` | Quality refactor; stable currently |
| SEC-03 | Return HTTP 503 on missing API key | Reliability improvement; low current risk |
| SEC-01 | Full auth implementation | Required but scope is L; not a "do not fix" — before milestone with scoping |
| TEST-04 | Full `app.py` test coverage | Only relevant if `app.py` is kept |
| TEST-05 | Update README test count | Trivial cosmetic |
| TEST-06 | Frontend tests with vitest | Good practice; no current failures |

---

## Section F — Estimated Cleanup Time

| ID | Effort | Est. Hours |
|---|---|---|
| BE-02 | XS | 0.25 |
| DEPLOY-04 | XS | 0.5 |
| TEST-03 | XS | 0.25 |
| DATA-01 | XS / S | 1–3 |
| TEST-01 | S | 2 |
| TEST-02 | S | 4 |
| ARCH-02/03 | S | 2 |
| ARCH-04 + BE-01 | XS | 0.5 |
| BE-03 | S | 1 |
| BE-04 | XS | 0.5 |
| BE-05 | S | 2–4 |
| DEPLOY-02/03/05/07 | XS | 1 |
| FE-02 (mobile) | M | 4–6 |
| FE-03 (persist mode) | XS | 0.5 |
| FE-06 | XS | 0.25 |
| SEC-02 | XS | 0.25 |
| **Fix Now total** | | **~1 hour** |
| **Before milestone total** | | **~20–26 hours** |

---

## Section G — Recommended Cleanup Milestone: V1.6 Stability Sprint

**Scope (strict):**

1. Pin requirements, fix BE-02 print, activate TEST-03 — same commit, 1 hour.
2. Mobile layout for ChatPage — isolated CSS, no logic changes.
3. Remove `.bak` files and add `.gitignore` entries in `inik-cafe`.
4. Add `render.yaml` and `.env.example`.
5. Add minimal `TestClient`-based endpoint tests.
6. Remove `streamlit` from `supabase_memory.py` and `event_logger.py` config paths.
7. Tag `v1.6.0` on both repos.

**Do not include in this milestone:** App.py deprecation, auth implementation, frontend component split, prompt_builder refactor.

**Definition of done:** All 39 items in C + D resolved or explicitly accepted. `tsc -b && vite build` passes. All pytest tests pass. Render deploy succeeds from the pinned requirements.

---

## Section H — Dependency Order

```
BE-02 (print fix)        — independent, fix first
DEPLOY-04 (pin reqs)     — independent, fix first
TEST-03 (activate test)  — independent, fix first

ARCH-02 (remove st from supabase_memory)
  └─ must precede: ARCH-01 (deprecate app.py) — removing app.py is safe only after decoupling

DATA-01 (legacy history migration)
  └─ must precede: any user-facing "history continuity" guarantee

TEST-01 (real ChatRequest import)
  └─ requires: DEPLOY-04 (test environment needs pinned pydantic/fastapi)
  └─ must precede: TEST-02 (endpoint tests extend the same test setup)

BE-04 (message max_length)
  └─ independent

BE-05 (/api/state scoping)
  └─ must precede: SEC-01 (full auth) — scope reduction is the first step

SEC-01 (full auth)
  └─ requires: BE-05 (partial state protection), Supabase RLS policy review

FE-02 (mobile layout)
  └─ independent

FE-03 (persist activeMode)
  └─ independent; cosmetically depends on FE-02 (mobile users need the back button to be visible)

ARCH-01 (deprecate app.py)
  └─ requires: ARCH-02, BE-01, ARCH-04 (eliminate divergences first)
  └─ requires: TEST-04 (confirm app.py logic is covered elsewhere before deleting)
```

---

## Section I — Items That Look Like Bugs But Are Expected Behavior

1. **Legacy `recent_messages` entries silently skipped (DATA-01):** This is intentional per the isolation spec: "Legacy assistant entries with no `agent_mode` must be skipped when mode filtering is active." It causes thin history for existing users but is the specified behavior, not a bug.

2. **`activeMode` resets to `'inik'` on page reload (FE-03):** Documented design decision from V1.5 session notes. The backend still routes based on explicit `agent_mode` in the request. The frontend state not persisting is a UX gap, not a routing bug.

3. **`preferred_agent_mode` is written but never read for routing (DATA-02):** After V1.5, this field is intentionally write-only. The V1.5 fix removed reading it for routing to prevent mode trapping. Writing it was retained for potential future analytics. Expected behavior.

4. **`/health` returns `gemini_configured: false` when `GEMINI_API_KEY` is missing (SEC-03):** This is the intended behavior of the health endpoint. The chat endpoint returning a graceful Thai string instead of HTTP 500 is also intentional — not a bug, but a reliability gap.

5. **`supabase_memory.py:st.secrets.get()` returns `None` silently in FastAPI context (ARCH-02):** This is defensive code working as designed. The `None` return causes the missing-env warning to fire once, which is the correct fallback behavior. Not a bug — a coupling smell.

---

## Section J — Concerning Items That Are NOT Technical Debt

1. **`LAST_MEMORY_STATUS` global dict in `memory_gateway.py`:** This mutable singleton looks dangerous but is used only as diagnostic state (logged, not branched on in production paths). Single-threaded FastAPI on Render means no concurrent write risk. Not debt — but worth a comment.

2. **`direct_fact_reply` bypasses agent mode in `inik_api.py:215`:** Facts are answered directly before Gemini is called. This means a user asking "what's my name?" in Rick mode gets the direct fact reply, not Rick's response. This is the correct, intentional behavior — deterministic fact recall should not depend on the model.

3. **RAG context not filtered by agent mode (`ARCH-06`):** RAG memories are general facts and conversation fragments. Unlike `recent_messages`, they don't carry conversational role assignments. Including cross-mode facts in both prompts is semantically correct — Rick and inik share the same user knowledge base.

4. **`supabase==2.31.0` is the only pinned package in `requirements.txt`:** This looks inconsistent with DEPLOY-04, but it was specifically pinned because the supabase SDK had a breaking API change at that version. This is the correct engineering decision and should be kept when other packages are pinned.

5. **`allow_credentials=False` on CORS (inik_api.py:45):** The CORS config explicitly disables credentials. This prevents cookie-based session attacks. Not a debt item — this is correct for a stateless API using bearer-like `user_id` in the request body.

---

*Audit complete. No source files were modified.*
