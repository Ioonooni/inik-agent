import streamlit as st
from memory_direct_answer import answer_direct_memory_recall
import google.generativeai as genai

from behavior import get_stage, get_stage_description
from character import CHARACTER_BIBLE
from memory import build_chat_history
from rag_prompt import build_safe_rag_context, get_raw_memories
from rag_memory import save_memory_note
from memory_gateway_v2 import save_message_memory_v2
from truth_engine import classify as classify_query, QueryType
from memory_verifier import verify as verify_memories
from memory_quality import assess_memory_quality
from response_router import route as route_response, RouteType
from facts import extract_facts, answer_from_facts
from rewards import check_reward, format_reward, get_reward_shop
from relationship import (
    create_relationship_state,
    update_relationship_state,
    describe_relationship_state,
    apply_relationship_decay
)
from memory_gateway import load_memory, save_memory, get_memory_status
from supabase_memory import save_memory_to_supabase, get_redacted_supabase_url
from analytics import calculate_analytics, get_engagement_label, get_system_summary
from fake_ai import generate_fake_reply
from modes import detect_response_mode, describe_response_mode
from user_profile import (
    create_user_profile,
    normalize_user_profile,
    register_visit,
    update_user_profile,
    describe_user_profile
)
from state_tools import (
    export_memory_json,
    reset_chat_only,
    reset_all_memory
)
from runtime_fallback import build_runtime_fallback
from fallback import build_fallback_reply
from health import run_health_check, get_health_label
from event_logger import send_event_to_n8n
from redemption import (
    redeem_first_inventory_item,
    get_redemption_count,
    get_latest_redemption,
    buy_reward_item
)
from auth_manager import login_or_create_user
from planner import build_plan, explain_plan
from planner_guard import normalize_plan
from agent_tools import list_available_tools, run_tool
from prompt_builder import build_main_prompt
from autonomous import run_autonomous_check
from autonomous_scheduler import should_run_autonomous_check, mark_autonomous_run
from acceptance_checks import run_acceptance_checks


st.set_page_config(
    page_title="i nik AI Prototype",
    page_icon="◧",
    layout="centered"
)


API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

USE_FAKE_AI = False

QUESTION_MARKERS = (
    "อะไร", "ไหม", "หรือ", "เหรอ", "หรอ", "ยังไง", "อย่างไร",
    "เท่าไหร่", "เท่าไร", "กี่", "?", "คืออะไร", "เล่าเรื่อง",
    "อธิบาย", "ทำไม", "เพราะอะไร"
)

FACT_STORE_PREFIXES = (
    "ฉันชื่อ", "ชื่อฉันคือ", "เรา ชื่อ", "ผมชื่อ", "หนูชื่อ",
    "ฉันชอบ", "เราชอบ", "ผมชอบ", "หนูชอบ",
    "ฉันไม่ชอบ", "เราไม่ชอบ", "ผมไม่ชอบ", "หนูไม่ชอบ",
)

def is_question_like(text: str) -> bool:
    clean = (text or "").strip().lower()
    if not clean:
        return False
    return any(marker in clean for marker in QUESTION_MARKERS)

def should_extract_structured_facts(text: str, classification=None) -> bool:
    clean = (text or "").strip().lower()
    if not clean:
        return False

    # Never store facts from questions. Prevents:
    # "ฉันชอบอะไรเกี่ยวกับหลุมดำ" -> likes="อะไรเกี่ยวกับหลุมดำ"
    if is_question_like(clean):
        return False

    return any(clean.startswith(prefix) for prefix in FACT_STORE_PREFIXES)

def should_save_rag_user_message(text: str, classification=None) -> bool:
    clean = (text or "").strip().lower()
    if not clean:
        return False

    # Do not save query-like prompts into RAG as long-term memories.
    # They create echo contamination later.
    if is_question_like(clean):
        return False

    if classification and getattr(classification, "requires_live_data", False):
        return False

    if classification and getattr(classification, "query_type", None) in (
        QueryType.FACTUAL_QUERY,
        QueryType.TOOL_QUERY,
        QueryType.RELATIONSHIP_QUERY,
    ):
        return False

    return True



def show_login():
    st.title("🧚 i nik")
    st.caption("AI Character Loyalty Prototype")

    st.write("---")
    st.subheader("เข้าสู่ระบบ")

    auth_mode = st.radio(
        "เลือกโหมด",
        ["Login", "Sign up", "Username demo"],
        horizontal=True
    )

    if auth_mode in ["Login", "Sign up"]:
        with st.form(key="email_auth_form"):
            email = st.text_input(
                "Email",
                placeholder="you@example.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="อย่างน้อย 6 ตัวอักษร",
            )
            submitted = st.form_submit_button(
                auth_mode,
                type="primary",
                use_container_width=True,
            )

        if submitted:
            try:
                if auth_mode == "Login":
                    from auth_manager import login_with_email
                    user = login_with_email(email, password)
                else:
                    from auth_manager import sign_up_with_email
                    user = sign_up_with_email(email, password)

                st.session_state["current_user"] = user
                st.session_state["user_id"] = user["id"]
                st.session_state["username"] = user["username"]
                st.session_state["email"] = user.get("email")
                st.session_state["auth_mode"] = "supabase_auth"
                st.rerun()

            except Exception as e:
                st.error(f"{auth_mode} ไม่สำเร็จ: {e}")

    else:
        with st.form(key="username_demo_form"):
            username = st.text_input(
                "ชื่อผู้ใช้",
                placeholder="เช่น aiuun, nik_lover",
            )
            submitted = st.form_submit_button(
                "เข้าสู่ระบบแบบ demo",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not username or len(username.strip()) < 2:
                st.error("กรุณาใส่ชื่ออย่างน้อย 2 ตัวอักษร")
                return

            username = username.strip().lower()

            try:
                user = login_or_create_user(username)

                if not user or "id" not in user or "username" not in user:
                    st.error("ข้อมูลผู้ใช้ไม่สมบูรณ์จากระบบ login")
                    return

                st.session_state["current_user"] = user
                st.session_state["user_id"] = user["id"]
                st.session_state["username"] = user["username"]
                st.session_state["auth_mode"] = "username_demo"
                st.rerun()

            except Exception as e:
                st.error(f"เข้าสู่ระบบไม่สำเร็จ: {e}")


def clear_runtime_state_for_user_switch():
    keys_to_clear = [
        "persistent_memory",
        "messages",
        "user_facts",
        "user_profile",
        "visit_registered",
        "intimacy_score",
        "points",
        "relationship_state",
        "inventory",
        "current_response_mode",
        "last_event_log_result",
        "last_redemption_result",
        "last_agent_tool_result",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def init_user_session():
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("ไม่พบ user_id กรุณา login ใหม่")
        st.stop()

    previous_loaded_user = st.session_state.get("loaded_user_id")

    if previous_loaded_user != user_id:
        clear_runtime_state_for_user_switch()
        st.session_state.loaded_user_id = user_id

    if "persistent_memory" not in st.session_state:
        try:
            st.session_state.persistent_memory = load_memory(user_id=user_id)
        except Exception as e:
            st.error(f"โหลด memory จากฐานข้อมูลไม่สำเร็จ: {e}")
            st.session_state.persistent_memory = {
                "user_facts": {},
                "user_profile": create_user_profile(),
                "inventory": [],
                "intimacy_score": 0,
                "points": 0,
                "relationship_state": create_relationship_state(),
            }

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.user_facts = st.session_state.persistent_memory.get(
        "user_facts",
        {}
    )

    st.session_state.user_profile = normalize_user_profile(
        st.session_state.persistent_memory.get(
            "user_profile",
            create_user_profile()
        )
    )

    if "visit_registered" not in st.session_state:
        st.session_state.user_profile = register_visit(
            st.session_state.user_profile
        )
        st.session_state.visit_registered = True

    raw_intimacy = st.session_state.persistent_memory.get("intimacy_score", 0)

    last_date_str = st.session_state.persistent_memory.get(
        "user_profile", {}
    ).get("last_interaction_date")

    if last_date_str:
        try:
            from datetime import datetime, timezone as _tz
            last_date = datetime.fromisoformat(last_date_str)
            if last_date.tzinfo is None:
                last_date = last_date.replace(tzinfo=_tz.utc)
            days_inactive = (datetime.now(_tz.utc) - last_date).days
            if days_inactive > 7:
                decay = min(raw_intimacy, (days_inactive // 7) * 5)
                raw_intimacy = max(0, raw_intimacy - decay)
        except Exception:
            pass

    st.session_state.intimacy_score = raw_intimacy

    st.session_state.points = st.session_state.persistent_memory.get(
        "points",
        0
    )

    st.session_state.relationship_state = st.session_state.persistent_memory.get(
        "relationship_state",
        create_relationship_state()
    )

    if last_date_str:
        try:
            st.session_state.relationship_state = apply_relationship_decay(
                st.session_state.relationship_state,
                days_inactive,
            )
        except Exception:
            pass

    st.session_state.inventory = st.session_state.persistent_memory.get(
        "inventory",
        []
    )

    if "current_response_mode" not in st.session_state:
        st.session_state.current_response_mode = "normal_chat"

    if "last_event_log_result" not in st.session_state:
        st.session_state.last_event_log_result = None

    if "last_redemption_result" not in st.session_state:
        st.session_state.last_redemption_result = None

    if "last_agent_tool_result" not in st.session_state:
        st.session_state.last_agent_tool_result = None


def persist_current_state():
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("ไม่พบ user_id จึงบันทึก memory ไม่ได้")
        return

    save_memory(
        st.session_state.user_facts,
        st.session_state.user_profile,
        st.session_state.inventory,
        st.session_state.intimacy_score,
        st.session_state.points,
        st.session_state.relationship_state,
        user_id=user_id
    )

    st.session_state.persistent_memory = {
        "user_facts": st.session_state.user_facts,
        "user_profile": st.session_state.user_profile,
        "inventory": st.session_state.inventory,
        "intimacy_score": st.session_state.intimacy_score,
        "points": st.session_state.points,
        "relationship_state": st.session_state.relationship_state
    }


def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def render_agent_tools_panel():
    st.divider()
    st.subheader("🛠 Agent Tools")
    st.caption("Manual tool testing panel")

    tools = list_available_tools()
    tool_names = [tool["name"] for tool in tools]

    selected_tool = st.selectbox(
        "Select Tool",
        tool_names,
        key="agent_tool_select"
    )

    with st.expander("Tool Description"):
        selected_info = next(
            (tool for tool in tools if tool["name"] == selected_tool),
            None
        )

        if selected_info:
            st.write(selected_info["description"])

    arguments = {}

    if selected_tool == "check_memory":
        memory_key = st.text_input(
            "Memory key optional",
            placeholder="เช่น name, likes หรือปล่อยว่าง",
            key="tool_memory_key"
        )
        arguments["key"] = memory_key.strip() if memory_key.strip() else None

    elif selected_tool == "grant_points":
        amount = st.number_input(
            "Points amount",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
            key="tool_points_amount"
        )
        reason = st.text_input(
            "Reason",
            value="manual_tool_test",
            key="tool_points_reason"
        )
        arguments["amount"] = int(amount)
        arguments["reason"] = reason

    elif selected_tool == "update_relationship":
        user_message = st.text_area(
            "Test message",
            value="ฉันชอบ i nik",
            key="tool_relationship_message"
        )
        arguments["user_message"] = user_message

    elif selected_tool == "log_agent_event":
        event_type = st.text_input(
            "Event type",
            value="manual_agent_tool_test",
            key="tool_event_type"
        )
        arguments["event_type"] = event_type
        arguments["extra"] = {
            "source": "agent_tools_panel",
            "username": st.session_state.get("username"),
            "user_id": st.session_state.get("user_id"),
        }

    if st.button("Run Tool", key="run_agent_tool", use_container_width=True):
        result = run_tool(
            selected_tool,
            st.session_state,
            arguments
        )

        st.session_state.last_agent_tool_result = result

        if selected_tool in ["grant_points", "update_relationship"]:
            persist_current_state()

        if selected_tool == "log_agent_event":
            st.session_state.last_event_log_result = result.get("result")

        st.rerun()

    if st.session_state.get("last_agent_tool_result"):
        st.write("Last Tool Result")
        st.json(st.session_state.last_agent_tool_result)


def main_app():
    def save_current_memory():
        save_memory_to_supabase(
            st.session_state.user_facts,
            st.session_state.user_profile,
            st.session_state.inventory,
            st.session_state.intimacy_score,
            st.session_state.points,
            st.session_state.relationship_state,
            user_id=st.session_state.get("user_id", "demo_user"),
        )

    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")

    init_user_session()

    with st.sidebar:
        st.header("User State")
        st.write(f"**ผู้ใช้:** `{username}`")
        st.write(f"**ID:** `{str(user_id)[:8]}...`")

        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()

        st.divider()

        st.metric("Intimacy", st.session_state.intimacy_score)

        stage = get_stage(st.session_state.intimacy_score)
        stage_description = get_stage_description(stage)
        st.metric("Stage", stage)
        st.metric("Points", st.session_state.points)

        st.divider()

        st.subheader("Relationship")
        st.metric("Trust", st.session_state.relationship_state["trust"])
        st.metric("Familiarity", st.session_state.relationship_state["familiarity"])
        st.metric("Curiosity", st.session_state.relationship_state["curiosity"])

        st.divider()

        st.subheader("Response Mode")
        st.write(st.session_state.current_response_mode)

        st.divider()

        st.subheader("Memory")

        if st.session_state.user_facts:
            for key, value in st.session_state.user_facts.items():
                if not key.startswith("_"):
                    st.write(f"{key}: {value}")
        else:
            st.write("ยังไม่มีข้อมูลที่จำได้")

        st.divider()

        st.subheader("User Profile")

        st.write(
            f"Recent Mood: {st.session_state.user_profile.get('recent_mood', 'neutral')}"
        )
        st.write(
            f"Conversation Style: {st.session_state.user_profile.get('conversation_style', 'unknown')}"
        )
        st.write(
            f"Total User Messages: {st.session_state.user_profile.get('total_messages', 0)}"
        )
        st.write(
            f"Total Visits: {st.session_state.user_profile.get('total_visits', 0)}"
        )
        st.write(
            f"Last Interaction: {st.session_state.user_profile.get('last_interaction_date', 'None')}"
        )

        topics = st.session_state.user_profile.get("recurring_topics", [])

        if topics:
            st.write("Recurring Topics:")
            for topic in topics:
                st.write(f"- {topic}")
        else:
            st.write("ยังไม่มี recurring topics")


        st.subheader("Reward Shop")

        for shop_item in get_reward_shop():
            label = f"{format_reward(shop_item)} | Cost: {shop_item.get('cost', 0)} points"
            if st.button(f"Buy: {shop_item.get('name')}", key=f"buy_{shop_item.get('id')}"):
                purchase_result = buy_reward_item(st.session_state, shop_item.get("id"))
                st.session_state.last_redemption_result = purchase_result

                if purchase_result["ok"]:
                    record = purchase_result["record"]
                    st.success(
                        f"Purchased: {format_reward(record.get('item'))} | "
                        f"Cost: {record.get('cost')} points | "
                        f"Points: {record.get('points_before')} → {record.get('points_after')}"
                    )

                    event_result = send_event_to_n8n(
                        "reward_shop_purchase",
                        st.session_state,
                        extra={
                            "purchase": purchase_result["record"],
                        },
                    )
                    st.session_state.last_event_log_result = event_result

                    save_current_memory()
                    st.rerun()
                else:
                    st.error(purchase_result.get("error"))

            st.caption(label)

        st.subheader("Inventory")
        st.caption(f"Current points: {st.session_state.points}")
        st.caption(f"Inventory items: {len(st.session_state.inventory)}")

        if st.session_state.inventory:
            for item in st.session_state.inventory:
                st.write(f"🎁 {format_reward(item)}")

            if st.button("Redeem First Item"):
                redemption_result = redeem_first_inventory_item(st.session_state)
                st.session_state.last_redemption_result = redemption_result

                if redemption_result["ok"]:
                    record = redemption_result["record"]
                    st.success(record.get("effect_message", "Redeemed item"))

                    persist_current_state()

                    event_result = send_event_to_n8n(
                        "reward_redeemed",
                        st.session_state,
                        extra={
                            "redemption": redemption_result["record"],
                            "user_id": user_id
                        }
                    )

                    st.session_state.last_event_log_result = event_result
                else:
                    st.error(redemption_result.get("error", "Redeem failed"))

                st.rerun()

        else:
            st.write("ยังไม่มีของแปลก")

        redemption_count = get_redemption_count(st.session_state.user_profile)
        latest_redemption = get_latest_redemption(st.session_state.user_profile)

        st.write(f"Redeemed Items: {redemption_count}")

        if latest_redemption:
            st.write(f"Latest Redeemed: {format_reward(latest_redemption.get('item'))}")

        st.divider()

        st.subheader("Analytics")
        analytics = calculate_analytics(st.session_state)

        st.metric(
            "Engagement",
            analytics["engagement_score"],
            get_engagement_label(analytics["engagement_score"])
        )

        st.progress(analytics["engagement_score"] / 100)
        st.metric("Total Messages", analytics["total_messages"])
        st.metric("Memory Facts", analytics["memory_fact_count"])
        st.metric("Inventory Items", analytics["inventory_count"])

        with st.expander("System Summary"):
            st.text(get_system_summary(analytics))

        st.divider()

        st.subheader("Developer")

        use_dev_test_mode = st.checkbox(
            "Use Dev Test Mode",
            value=False
        )

        if use_dev_test_mode:
            debug = st.session_state.get("last_route_debug")
            if debug:
                st.caption("Last route (dev)")
                st.code(
                    f"query_type: {debug.get('query_type')}\n"
                    f"route_type: {debug.get('route_type')}\n"
                    f"live_data:  {debug.get('requires_live_data')}\n"
                    f"direct_ans: {debug.get('can_answer_directly')}\n"
                    f"answer:     {debug.get('direct_answer')}\n"
                    f"rag:        {debug.get('rag_preview')}",
                    language="yaml",
                )

            if st.button("Run Acceptance Checks", use_container_width=True):
                st.session_state.last_acceptance_report = run_acceptance_checks(st.session_state)

            report = st.session_state.get("last_acceptance_report")
            if report:
                st.caption(
                    f"Acceptance: {report['passed']} passed / {report['failed']} failed"
                )
                if report["ok"]:
                    st.success("Acceptance checks passed")
                else:
                    st.error("Acceptance checks failed")
                st.json(report["results"])

        memory_status = get_memory_status()

        st.divider()
        st.subheader("Database Status")

        st.write(f"Source: {memory_status.get('source')}")
        st.write(f"Supabase Load: {memory_status.get('supabase_load')}")
        st.write(f"Supabase Save: {memory_status.get('supabase_save')}")
        st.write(f"URL: {get_redacted_supabase_url()}")

        if memory_status.get("last_error"):
            st.error(memory_status.get("last_error"))

        st.download_button(
            label="Download Memory JSON",
            data=export_memory_json(st.session_state),
            file_name=f"i_nik_memory_{username}.json",
            mime="application/json"
        )

        if st.button("Reset Chat Only"):
            reset_chat_only(st.session_state)
            st.rerun()

        if st.button("Reset All Memory"):
            reset_all_memory(st.session_state)
            st.rerun()

        event_result = st.session_state.get("last_event_log_result")

        st.divider()
        st.subheader("Event Logging")

        if event_result:
            st.write(f"n8n OK: {event_result.get('ok')}")
            st.write(f"Status: {event_result.get('status_code')}")

            if event_result.get("error"):
                st.error(event_result.get("error"))
        else:
            st.write("ยังไม่มี event log")

        redemption_result = st.session_state.get("last_redemption_result")

        st.divider()
        st.subheader("Redemption Status")

        if redemption_result:
            st.write(f"Redeem OK: {redemption_result.get('ok')}")

            if redemption_result.get("error"):
                st.error(redemption_result.get("error"))

            if redemption_result.get("record"):
                st.write(
                    f"Item: {redemption_result['record'].get('item')}"
                )
        else:
            st.write("ยังไม่มี redemption")

        health_result = run_health_check(st.session_state)

        st.divider()
        st.subheader("Health Check")

        st.write(get_health_label(health_result))

        with st.expander("Health Details"):
            for check in health_result["checks"]:
                icon = "✅" if check["status"] else "❌"
                st.write(f"{icon} {check['name']}: {check['detail']}")

        render_agent_tools_panel()

    st.title("🧚 i nik ◧")
    st.caption(f"สวัสดี, {username}! i nik จำคุณได้...")
    st.write("### Talk to i nik")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_message = st.chat_input("พิมพ์คุยกับ i nik...")

    if user_message:
        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })

        # Classify before saving anything so questions do not poison memory/RAG.
        classification = classify_query(user_message, st.session_state.user_facts)

        if should_save_rag_user_message(user_message, classification):
            try:
                quality = assess_memory_quality(user_message)

                if quality.should_store:

                    save_memory_note(
                    user_id=user_id,
                    content=user_message,
                    memory_type=quality.memory_type
                )
            except Exception as error:
                print("[RAG SAVE ERROR]", error)

        st.session_state.intimacy_score = min(
            100,
            st.session_state.intimacy_score + 10
        )

        st.session_state.points += 1

        reward = check_reward(st.session_state.points)

        if should_extract_structured_facts(user_message, classification):
            st.session_state.user_facts = extract_facts(
                user_message,
                st.session_state.user_facts
            )

        st.session_state.user_profile = update_user_profile(
            user_message,
            st.session_state.user_profile
        )

        st.session_state.relationship_state = update_relationship_state(
            user_message,
            st.session_state.relationship_state
        )

        stage = get_stage(st.session_state.intimacy_score)
        stage_description = get_stage_description(stage)

        relationship_description = describe_relationship_state(
            st.session_state.relationship_state
        )

        user_profile_description = describe_user_profile(
            st.session_state.user_profile
        )

        response_mode = detect_response_mode(user_message)
        st.session_state.current_response_mode = response_mode

        response_mode_description = describe_response_mode(response_mode)

        chat_history = build_chat_history(
            st.session_state.messages,
            limit=10
        )

        # 1. Query intent was classified before memory writes.

        # 2. Fetch and verify RAG memories
        raw_memories = get_raw_memories(
            user_id=user_id,
            user_message=user_message,
            limit=5
        )
        verified = verify_memories(raw_memories or [])

        # 3. Run planner for tool-based intents
        raw_plan = build_plan(user_message, st.session_state)
        plan = normalize_plan(raw_plan)
        st.session_state.last_agent_plan = plan

        planner_result = None
        if plan.get("tool"):
            planner_result = run_tool(
                plan["tool"],
                st.session_state,
                plan.get("arguments", {})
            )

        # 4. Route to the correct response strategy
        route_decision = route_response(
            classification=classification,
            user_facts=st.session_state.user_facts,
            planner_result=planner_result,
            verified_memories=verified,
        )

        st.session_state.last_route_debug = {
            "query_type": classification.query_type,
            "route_type": route_decision.route_type,
            "requires_live_data": classification.requires_live_data,
            "can_answer_directly": classification.can_answer_directly,
            "direct_answer": classification.direct_answer,
            "rag_preview": route_decision.rag_context[:60],
        }

        
        recall_memories = list(raw_memories or [])
        try:
            broader_memories = get_raw_memories(
                user_id=user_id,
                user_message="",
                limit=50,
            )
            recall_memories.extend(broader_memories or [])
        except Exception:
            pass

        direct_memory_reply = answer_direct_memory_recall(
            user_message,
            st.session_state.user_facts,
            recall_memories,
        )
        if direct_memory_reply:
            route_decision.direct_reply = direct_memory_reply

        # 5. Execute routing decision
        # Direct deterministic / structured answers must win.
        # This prevents Gemini from overwriting answers like 2+2 -> 4.
        if route_decision.direct_reply is not None:
            reply = route_decision.direct_reply

        elif route_decision.route_type == RouteType.TOOL_ANSWER and planner_result and planner_result.get("ok"):
            tool_name = planner_result.get("tool")

            if tool_name == "check_memory":
                facts = planner_result.get("facts", {})
                value = planner_result.get("value")
                key = planner_result.get("key")

                if key and value:
                    if key == "name":
                        reply = f"เธอชื่อ {value} ไง"
                    elif key == "likes":
                        reply = f"เท่าที่ฉันจำได้ เธอชอบ {value}"
                    else:
                        reply = f"เท่าที่ฉันจำได้ {key} คือ {value}"
                elif facts:
                    clean_facts = {k: v for k, v in facts.items() if isinstance(facts, dict) and not k.startswith("_")}
                    facts_text = ", ".join(f"{k}: {v}" for k, v in clean_facts.items())
                    reply = f"เท่าที่ฉันจำได้เกี่ยวกับเธอ: {facts_text}" if facts_text else "ฉันยังจำข้อมูลนี้ไม่ได้เลย"
                else:
                    reply = "ฉันยังจำข้อมูลนี้ไม่ได้เลย"

            elif tool_name == "get_user_state":
                reply = (
                    f"ตอนนี้เธออยู่ Stage "
                    f"{planner_result.get('stage')} "
                    f"และมี {planner_result.get('points')} points"
                )

            elif tool_name == "get_inventory":
                inventory = planner_result.get("inventory", [])
                reply = f"ของที่เธอมีตอนนี้คือ {inventory}" if inventory else "ตอนนี้เธอยังไม่มีของใน inventory"

            elif tool_name == "get_relationship_state":
                reply = (
                    f"สถานะตอนนี้ trust={planner_result.get('trust')}, "
                    f"familiarity={planner_result.get('familiarity')}, "
                    f"curiosity={planner_result.get('curiosity')}"
                )

            elif tool_name == "get_visit_count":
                reply = (
                    f"เธอแวะมาทั้งหมด "
                    f"{planner_result.get('total_visits')} ครั้ง "
                    f"และส่งข้อความทั้งหมด "
                    f"{planner_result.get('total_messages')} ข้อความ"
                )

            else:
                reply = str(planner_result)

        else:
            prompt = build_main_prompt(
                stage_description=stage_description,
                relationship_description=relationship_description,
                user_profile_description=user_profile_description,
                response_mode_description=response_mode_description,
                chat_history=chat_history,
                user_facts=st.session_state.user_facts,
                rag_context=route_decision.rag_context,
                user_message=user_message,
                relationship_state=st.session_state.relationship_state,
                live_data_warning=route_decision.live_data_warning,
            )

            _bypass_gemini = bool(USE_FAKE_AI)

            try:
                if _bypass_gemini:
                    analytics = calculate_analytics(st.session_state)
                    reply = generate_fake_reply(
                        user_message,
                        stage,
                        response_mode,
                        st.session_state.user_facts,
                        st.session_state.relationship_state,
                        analytics,
                    )
                else:
                    response = model.generate_content(prompt)
                    reply = response.text

            except Exception as e:
                error_text = repr(e)
                print("GEMINI ERROR:", error_text)
                st.session_state.last_gemini_error = error_text
                st.sidebar.error(f"Gemini error: {error_text[:180]}")

                reply = build_fallback_reply(
                    str(e),
                    user_message,
                    stage,
                    response_mode,
                    st.session_state.user_facts,
                    st.session_state.relationship_state,
                    query_type=classification.query_type,
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

        if reward:
            st.session_state.inventory.append(reward)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"🎁 i nik เจอของแปลกให้เธอ: {format_reward(reward)}"
            })

        persist_current_state()

        if should_run_autonomous_check(st.session_state):
            try:
                auto_result = run_autonomous_check(st.session_state, model=model)
                auto_msg = auto_result.get("decision", {}).get("message")
                if auto_msg:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": auto_msg
                    })
            except Exception as error:
                st.session_state.last_autonomous_error = str(error)
            finally:
                mark_autonomous_run(st.session_state)

        event_result = send_event_to_n8n(
            "user_message",
            st.session_state,
            extra={
                "message": user_message,
                "reply": reply,
                "reward": reward,
                "user_id": user_id
            }
        )

        st.session_state.last_event_log_result = event_result

        st.rerun()


def main():
    if "current_user" not in st.session_state:
        show_login()
    else:
        main_app()


if __name__ == "__main__":
    main()
