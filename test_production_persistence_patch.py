"""
Tests for the production-safe persistence patch applied to origin/main.
Targets: supabase_memory.py, memory_gateway.py, requirements.txt
No live Supabase. No live Gemini. All external calls mocked.

API route tests (7, 8) load origin/main's inik_api.py from a temp path to avoid
testing the branch version which has different routes.
"""
import importlib
import importlib.util
import json
import logging
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Pre-stub unavailable modules at module load so cascading imports don't fail.
# Tests that need controlled mocks reload the specific module in setUp.
# ---------------------------------------------------------------------------
if "streamlit" not in sys.modules:
    _st_stub = MagicMock()
    _st_stub.secrets.get.return_value = None
    sys.modules["streamlit"] = _st_stub

# Ensure supabase stub has create_client (the real package is a stub here)
import supabase as _supabase_pkg
if not hasattr(_supabase_pkg, "create_client") or callable(getattr(_supabase_pkg, "create_client", None)) is False:
    _supabase_pkg.create_client = MagicMock(return_value=MagicMock())


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _clear_env():
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_KEY", None)


def _set_env():
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test-anon-key"


def _reload_sm(extra_patches=None):
    """Reload supabase_memory with clean state and mocked streamlit/supabase."""
    mock_st = MagicMock()
    mock_st.secrets.get.return_value = None
    patches = {
        "streamlit": mock_st,
        "supabase": MagicMock(create_client=MagicMock(return_value=MagicMock())),
    }
    if extra_patches:
        patches.update(extra_patches)
    with patch.dict("sys.modules", patches):
        sys.modules.pop("supabase_memory", None)
        import supabase_memory
        importlib.reload(supabase_memory)
        supabase_memory._missing_env_warned = False
    return supabase_memory


def _reload_sm_with_client(mock_client):
    mock_supabase = MagicMock()
    mock_supabase.create_client = MagicMock(return_value=mock_client)
    return _reload_sm(extra_patches={"supabase": mock_supabase})


_PROD_API_STUBS = {}


def _load_prod_inik_api():
    """Load origin/main's inik_api.py from temp path with all deps pre-stubbed."""
    # Stub every non-stdlib dep that would either crash or require live services.
    # These are only active during the exec; real sys.modules are restored after.
    genai_mock = MagicMock()
    genai_mock.GenerativeModel.return_value = MagicMock()

    stubs = {
        "dotenv": MagicMock(load_dotenv=MagicMock()),
        "google": MagicMock(),
        "google.generativeai": genai_mock,
        "behavior": MagicMock(get_stage=MagicMock(return_value="observer"),
                               get_stage_description=MagicMock(return_value="")),
        "memory": MagicMock(build_chat_history=MagicMock(return_value=[])),
        "memory_gateway_v2": MagicMock(),
        "relationship": MagicMock(
            create_relationship_state=MagicMock(return_value={"trust": 0, "familiarity": 0, "curiosity": 0}),
            update_relationship_state=MagicMock(return_value={"trust": 0, "familiarity": 0, "curiosity": 0}),
            describe_relationship_state=MagicMock(return_value=""),
        ),
        "user_profile": MagicMock(
            create_user_profile=MagicMock(return_value={"recent_messages": [], "adaptive_personality": None}),
            normalize_user_profile=MagicMock(side_effect=lambda x: x),
            update_user_profile=MagicMock(side_effect=lambda msg, prof: prof),
            describe_user_profile=MagicMock(return_value=""),
        ),
        "modes": MagicMock(
            detect_response_mode=MagicMock(return_value="normal_chat"),
            describe_response_mode=MagicMock(return_value=""),
        ),
        "facts": MagicMock(
            extract_facts=MagicMock(side_effect=lambda msg, facts: facts),
            answer_from_facts=MagicMock(return_value=None),
        ),
        "prompt_builder": MagicMock(build_main_prompt=MagicMock(return_value="prompt")),
        "agent_router": MagicMock(
            detect_agent_handoff=MagicMock(return_value=None),
            classify_agent_route=MagicMock(return_value=MagicMock(agent_mode="inik")),
        ),
        "rick_prompt": MagicMock(build_rick_prompt=MagicMock(return_value="rick")),
        "rag_prompt": MagicMock(build_safe_rag_context=MagicMock(return_value="")),
    }

    with patch.dict("sys.modules", stubs):
        sys.modules.pop("inik_api_prod", None)
        spec = importlib.util.spec_from_file_location("inik_api_prod", "/tmp/inik_api_prod.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    return mod


# ---------------------------------------------------------------------------
# Test 1: missing env logs warning once, no secrets in message
# ---------------------------------------------------------------------------

class TestMissingEnvWarnsOnce(unittest.TestCase):
    def test_missing_env_logs_warning_once(self):
        _clear_env()
        sm = _reload_sm()

        with self.assertLogs("inik.supabase", level="WARNING") as cm:
            try:
                sm.get_supabase_client()
            except ValueError:
                pass

        self.assertEqual(len(cm.output), 1)
        msg = cm.output[0]
        self.assertIn("disabled", msg)
        self.assertIn("environment variables", msg)
        self.assertNotIn("SUPABASE_URL", msg)
        self.assertNotIn("SUPABASE_KEY", msg)

    def test_missing_env_warning_fires_only_once(self):
        _clear_env()
        sm = _reload_sm()
        sm._missing_env_warned = False

        with self.assertLogs("inik.supabase", level="WARNING"):
            try:
                sm.get_supabase_client()
            except ValueError:
                pass

        with self.assertRaises(AssertionError):
            with self.assertLogs("inik.supabase", level="WARNING"):
                try:
                    sm.get_supabase_client()
                except ValueError:
                    pass

    def test_missing_env_still_raises_for_callers(self):
        _clear_env()
        sm = _reload_sm()
        sm._missing_env_warned = False
        with self.assertLogs("inik.supabase", level="WARNING"):
            with self.assertRaises(ValueError):
                sm.get_supabase_client()


# ---------------------------------------------------------------------------
# Test 2: valid env still creates client
# ---------------------------------------------------------------------------

class TestValidEnvCreatesClient(unittest.TestCase):
    def setUp(self):
        _set_env()

    def tearDown(self):
        _clear_env()

    def test_returns_client_with_valid_env(self):
        mock_client = MagicMock()
        mock_supabase = MagicMock(create_client=MagicMock(return_value=mock_client))
        sm = _reload_sm(extra_patches={"supabase": mock_supabase})

        result = sm.get_supabase_client()

        self.assertIsNotNone(result)
        mock_supabase.create_client.assert_called_once()


# ---------------------------------------------------------------------------
# Test 3: load failure logs only exception class
# ---------------------------------------------------------------------------

class TestLoadFailureLogsClassOnly(unittest.TestCase):
    def setUp(self):
        _set_env()

    def tearDown(self):
        _clear_env()

    def test_load_logs_class_not_message(self):
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value \
            .limit.return_value.execute.side_effect = RuntimeError("conn: secret://host")
        sm = _reload_sm_with_client(mock_client)

        with self.assertLogs("inik.supabase", level="WARNING") as cm:
            result = sm.load_memory_from_supabase("user_x")

        self.assertIsNotNone(result)
        self.assertEqual(len(cm.output), 1)
        msg = cm.output[0]
        self.assertIn("load", msg)
        self.assertIn("RuntimeError", msg)
        self.assertNotIn("secret://host", msg)
        self.assertNotIn("conn:", msg)
        self.assertNotIn("user_x", msg)
        self.assertNotIn("test-anon-key", msg)
        self.assertNotIn("supabase.co", msg)


# ---------------------------------------------------------------------------
# Test 4: save failure logs only exception class
# ---------------------------------------------------------------------------

class TestSaveFailureLogsClassOnly(unittest.TestCase):
    def setUp(self):
        _set_env()

    def tearDown(self):
        _clear_env()

    def test_save_logs_class_not_message(self):
        mock_client = MagicMock()
        mock_client.table.side_effect = ConnectionError("host=secret.supabase.co key=abc123")
        sm = _reload_sm_with_client(mock_client)

        with self.assertLogs("inik.supabase", level="WARNING") as cm:
            result = sm.save_memory_to_supabase(
                {}, {}, [], 0, 0, {}, user_id="uid_sensitive"
            )

        self.assertFalse(result)
        self.assertEqual(len(cm.output), 1)
        msg = cm.output[0]
        self.assertIn("save", msg)
        self.assertIn("ConnectionError", msg)
        self.assertNotIn("uid_sensitive", msg)
        self.assertNotIn("secret.supabase.co", msg)
        self.assertNotIn("abc123", msg)
        self.assertNotIn("key=", msg)


# ---------------------------------------------------------------------------
# Test 5: memory_gateway last_error is class name, not str(error)
# ---------------------------------------------------------------------------

class TestGatewayLoadErrorRedacted(unittest.TestCase):
    def _make_mock_sm(self, exc):
        mock_sm = MagicMock()
        mock_sm.get_supabase_client.side_effect = exc
        mock_sm.DEMO_USER_ID = "demo_user"
        mock_sm.TABLE_NAME = "i_nik_memory"
        mock_sm.row_to_memory = MagicMock()
        mock_sm.save_memory_to_supabase = MagicMock(return_value=False)
        return mock_sm

    def test_last_error_is_class_name_not_str(self):
        mock_sm = self._make_mock_sm(ValueError("url=https://secret.supabase.co"))

        with patch.dict("sys.modules", {"supabase_memory": mock_sm}):
            sys.modules.pop("memory_gateway", None)
            import memory_gateway
            importlib.reload(memory_gateway)

            with self.assertLogs("inik.supabase", level="WARNING") as cm:
                memory_gateway.load_memory("non_demo_user")

        last_error = memory_gateway.LAST_MEMORY_STATUS["last_error"]
        self.assertEqual(last_error, "ValueError")
        self.assertNotIn("secret.supabase.co", last_error)

        msgs = " ".join(cm.output)
        self.assertNotIn("secret.supabase.co", msgs)
        self.assertNotIn("non_demo_user", msgs)

    def test_demo_user_falls_back_to_json(self):
        mock_sm = self._make_mock_sm(ValueError("missing creds"))
        expected = {"user_facts": {"name": "demo"}, "intimacy_score": 5,
                    "points": 2, "inventory": [], "user_profile": {},
                    "relationship_state": {}}
        mock_json_load = MagicMock(return_value=expected)

        with patch.dict("sys.modules", {"supabase_memory": mock_sm}):
            sys.modules.pop("memory_gateway", None)
            import memory_gateway
            importlib.reload(memory_gateway)
            memory_gateway.load_memory_from_json = mock_json_load

            with self.assertLogs("inik.supabase", level="WARNING"):
                result = memory_gateway.load_memory("demo_user")

        mock_json_load.assert_called_once()
        self.assertEqual(result["user_facts"]["name"], "demo")
        self.assertEqual(memory_gateway.LAST_MEMORY_STATUS["source"], "json_fallback_demo_user")


# ---------------------------------------------------------------------------
# Test 6: non-demo user gets blank memory on Supabase failure
# ---------------------------------------------------------------------------

class TestNonDemoUserBlanksOnFailure(unittest.TestCase):
    def test_non_demo_user_returns_blank(self):
        mock_sm = MagicMock()
        mock_sm.get_supabase_client.side_effect = RuntimeError("network failure details")
        mock_sm.DEMO_USER_ID = "demo_user"
        mock_sm.TABLE_NAME = "i_nik_memory"
        mock_sm.row_to_memory = MagicMock()
        mock_sm.save_memory_to_supabase = MagicMock(return_value=False)

        with patch.dict("sys.modules", {"supabase_memory": mock_sm}):
            sys.modules.pop("memory_gateway", None)
            import memory_gateway
            importlib.reload(memory_gateway)

            with self.assertLogs("inik.supabase", level="WARNING"):
                result = memory_gateway.load_memory("real_user_456")

        self.assertIn("user_facts", result)
        self.assertEqual(memory_gateway.LAST_MEMORY_STATUS["source"],
                         "blank_memory_fallback_non_demo_user")
        self.assertEqual(memory_gateway.LAST_MEMORY_STATUS["last_error"], "RuntimeError")
        self.assertNotIn("network failure", memory_gateway.LAST_MEMORY_STATUS["last_error"])


# ---------------------------------------------------------------------------
# Test 7 & 8: POST /api/chat and GET /api/state via production inik_api.py
# Loaded from /tmp/inik_api_prod.py (git show origin/main:inik_api.py)
# ---------------------------------------------------------------------------

def _build_fake_memory():
    return {
        "user_facts": {},
        "user_profile": {
            "recent_mood": "neutral",
            "conversation_style": "unknown",
            "recurring_topics": [],
            "memorable_events": [],
            "recent_messages": [],
            "adaptive_personality": None,
        },
        "inventory": [],
        "intimacy_score": 0,
        "points": 0,
        "relationship_state": {"trust": 0, "familiarity": 0, "curiosity": 0},
    }


class TestProductionApiChat(unittest.TestCase):
    def setUp(self):
        self.mock_load = MagicMock(return_value=_build_fake_memory())
        self.mock_save = MagicMock(return_value=True)
        self.mock_save_v2 = MagicMock()

        # Mock all production inik_api.py dependencies before loading
        mock_mem_gw = MagicMock()
        mock_mem_gw.load_memory = self.mock_load
        mock_mem_gw.save_memory = self.mock_save

        mock_mem_gw_v2 = MagicMock()
        mock_mem_gw_v2.save_message_memory_v2 = self.mock_save_v2

        self._patches = {
            "memory_gateway": mock_mem_gw,
            "memory_gateway_v2": mock_mem_gw_v2,
            "dotenv": MagicMock(),
        }
        sys.modules.update(self._patches)

        # Remove cached prod module so it loads fresh
        sys.modules.pop("inik_api_prod", None)

        self.api = _load_prod_inik_api()
        self.api.model = None  # no Gemini

    def _make_req(self, user_id="u1", message="hello", agent_mode="inik"):
        req = MagicMock()
        req.user_id = user_id
        req.username = "tester"
        req.message = message
        req.agent_mode = agent_mode
        return req

    def test_chat_returns_reply_key(self):
        result = self.api.chat(self._make_req())
        self.assertIn("reply", result)
        self.assertIn("state", result)
        self.assertIn("agent_mode", result)
        self.assertEqual(result["user_id"], "u1")

    def test_chat_calls_load_and_save(self):
        self.api.chat(self._make_req())
        self.mock_load.assert_called_once()
        self.mock_save.assert_called_once()

    def test_chat_returns_400_on_missing_user_id(self):
        raised = None
        try:
            self.api.chat(self._make_req(user_id=""))
        except Exception as e:
            raised = e
        self.assertIsNotNone(raised, "Expected exception for empty user_id")
        self.assertEqual(getattr(raised, "status_code", None), 400)


class TestProductionApiState(unittest.TestCase):
    def _fake_mem_with_scores(self):
        m = _build_fake_memory()
        m["user_facts"] = {"name": "Tester"}
        m["intimacy_score"] = 25
        m["points"] = 3
        m["relationship_state"] = {"trust": 5, "familiarity": 3, "curiosity": 2}
        m["user_profile"]["recent_messages"] = [{"role": "user", "content": "hi"}]
        return m

    def setUp(self):
        self.mock_load = MagicMock(return_value=self._fake_mem_with_scores())
        mock_mem_gw = MagicMock()
        mock_mem_gw.load_memory = self.mock_load
        sys.modules["memory_gateway"] = mock_mem_gw
        sys.modules.pop("inik_api_prod", None)
        self.api = _load_prod_inik_api()

    def test_state_returns_correct_shape(self):
        result = self.api.get_state(user_id="test_user")
        for key in ("user_id", "stage", "intimacy_score", "points",
                    "relationship_state", "user_profile", "user_facts", "recent_messages"):
            self.assertIn(key, result, f"missing key: {key}")
        self.assertEqual(result["intimacy_score"], 25)
        self.assertEqual(result["points"], 3)
        self.assertEqual(result["user_facts"]["name"], "Tester")

    def test_state_raises_400_on_empty_user_id(self):
        raised = None
        try:
            self.api.get_state(user_id="")
        except Exception as e:
            raised = e
        self.assertIsNotNone(raised, "Expected exception for empty user_id")
        self.assertEqual(getattr(raised, "status_code", None), 400)


# ---------------------------------------------------------------------------
# Test 9: requirements.txt pinning
# ---------------------------------------------------------------------------

class TestRequirementsPinned(unittest.TestCase):
    def test_supabase_pinned(self):
        with open("requirements.txt") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertIn("supabase==2.31.0", lines)
        self.assertNotIn("supabase", [l for l in lines if l == "supabase"])

    def test_other_deps_unchanged(self):
        with open("requirements.txt") as f:
            lines = [l.strip() for l in f if l.strip()]
        for dep in ("streamlit", "google-generativeai", "requests",
                    "fastapi", "uvicorn", "python-dotenv"):
            self.assertIn(dep, lines, f"missing dep: {dep}")


if __name__ == "__main__":
    unittest.main()
