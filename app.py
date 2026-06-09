import streamlit as st
import google.generativeai as genai

from behavior import get_stage, get_stage_description
from character import CHARACTER_BIBLE
from memory import build_chat_history
from facts import extract_facts, answer_from_facts
from rewards import check_reward
from relationship import (
    create_relationship_state,
    update_relationship_state,
    describe_relationship_state
)
from memory_gateway import load_memory, save_memory, get_memory_status
from supabase_memory import get_redacted_supabase_url
from analytics import calculate_analytics, get_engagement_label, get_system_summary
from fake_ai import generate_fake_reply
from modes import detect_response_mode, describe_response_mode
from profile import (
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
from fallback import build_fallback_reply
from health import run_health_check, get_health_label
from event_logger import send_event_to_n8n
from redemption import (
    redeem_first_inventory_item,
    get_redemption_count,
    get_latest_redemption
)

st.set_page_config(
    page_title="i nik AI Prototype",
    page_icon="◧",
    layout="centered"
)


API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

USE_FAKE_AI = False


if "persistent_memory" not in st.session_state:
    st.session_state.persistent_memory = load_memory()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_facts" not in st.session_state:
    st.session_state.user_facts = st.session_state.persistent_memory.get(
        "user_facts",
        {}
    )

if "user_profile" not in st.session_state:
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

if "intimacy_score" not in st.session_state:
    st.session_state.intimacy_score = st.session_state.persistent_memory.get(
        "intimacy_score",
        0
    )

if "points" not in st.session_state:
    st.session_state.points = st.session_state.persistent_memory.get(
        "points",
        0
    )

if "relationship_state" not in st.session_state:
    st.session_state.relationship_state = st.session_state.persistent_memory.get(
        "relationship_state",
        create_relationship_state()
    )

if "inventory" not in st.session_state:
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

def persist_current_state():
    save_memory(
        st.session_state.user_facts,
        st.session_state.user_profile,
        st.session_state.inventory,
        st.session_state.intimacy_score,
        st.session_state.points,
        st.session_state.relationship_state
    )

    st.session_state.persistent_memory = {
        "user_facts": st.session_state.user_facts,
        "user_profile": st.session_state.user_profile,
        "inventory": st.session_state.inventory,
        "intimacy_score": st.session_state.intimacy_score,
        "points": st.session_state.points,
        "relationship_state": st.session_state.relationship_state
    }


stage = get_stage(st.session_state.intimacy_score)
stage_description = get_stage_description(stage)
analytics = calculate_analytics(st.session_state)


st.sidebar.header("User State")

st.sidebar.metric("Intimacy", st.session_state.intimacy_score)
st.sidebar.metric("Stage", stage)
st.sidebar.metric("Points", st.session_state.points)

st.sidebar.divider()

st.sidebar.subheader("Relationship")
st.sidebar.metric("Trust", st.session_state.relationship_state["trust"])
st.sidebar.metric("Familiarity", st.session_state.relationship_state["familiarity"])
st.sidebar.metric("Curiosity", st.session_state.relationship_state["curiosity"])

st.sidebar.divider()

st.sidebar.subheader("Response Mode")
st.sidebar.write(st.session_state.current_response_mode)

st.sidebar.divider()

st.sidebar.subheader("Memory")

if st.session_state.user_facts:
    for key, value in st.session_state.user_facts.items():
        st.sidebar.write(f"{key}: {value}")
else:
    st.sidebar.write("ยังไม่มีข้อมูลที่จำได้")

st.sidebar.divider()

st.sidebar.subheader("User Profile")

st.sidebar.write(
    f"Recent Mood: {st.session_state.user_profile.get('recent_mood', 'neutral')}"
)

st.sidebar.write(
    f"Conversation Style: {st.session_state.user_profile.get('conversation_style', 'unknown')}"
)

st.sidebar.write(
    f"Total User Messages: {st.session_state.user_profile.get('total_messages', 0)}"
)

st.sidebar.write(
    f"Total Visits: {st.session_state.user_profile.get('total_visits', 0)}"
)

st.sidebar.write(
    f"Last Interaction: {st.session_state.user_profile.get('last_interaction_date', 'None')}"
)

topics = st.session_state.user_profile.get("recurring_topics", [])

if topics:
    st.sidebar.write("Recurring Topics:")
    for topic in topics:
        st.sidebar.write(f"- {topic}")
else:
    st.sidebar.write("ยังไม่มี recurring topics")

st.sidebar.subheader("Inventory")

if st.session_state.inventory:
    for item in st.session_state.inventory:
        st.sidebar.write(f"🎁 {item}")

    if st.sidebar.button("Redeem First Item"):
        redemption_result = redeem_first_inventory_item(st.session_state)
        st.session_state.last_redemption_result = redemption_result

        if redemption_result["ok"]:
            persist_current_state()

            event_result = send_event_to_n8n(
                "reward_redeemed",
                st.session_state,
                extra={
                    "redemption": redemption_result["record"]
                }
            )

            st.session_state.last_event_log_result = event_result

        st.rerun()

else:
    st.sidebar.write("ยังไม่มีของแปลก")

redemption_count = get_redemption_count(st.session_state.user_profile)
latest_redemption = get_latest_redemption(st.session_state.user_profile)

st.sidebar.write(f"Redeemed Items: {redemption_count}")

if latest_redemption:
    st.sidebar.write(f"Latest Redeemed: {latest_redemption.get('item')}")

st.sidebar.divider()

st.sidebar.subheader("Analytics")

st.sidebar.metric(
    "Engagement",
    analytics["engagement_score"],
    get_engagement_label(analytics["engagement_score"])
)

st.sidebar.progress(
    analytics["engagement_score"] / 100
)

st.sidebar.metric(
    "Total Messages",
    analytics["total_messages"]
)

st.sidebar.metric(
    "Memory Facts",
    analytics["memory_fact_count"]
)

st.sidebar.metric(
    "Inventory Items",
    analytics["inventory_count"]
)

with st.sidebar.expander("System Summary"):
    st.text(get_system_summary(analytics))

st.sidebar.divider()

st.sidebar.subheader("Developer")

use_dev_test_mode = st.sidebar.checkbox(
    "Use Dev Test Mode",
    value=False
)

memory_status = get_memory_status()

st.sidebar.divider()
st.sidebar.subheader("Database Status")

st.sidebar.write(f"Source: {memory_status.get('source')}")
st.sidebar.write(f"Supabase Load: {memory_status.get('supabase_load')}")
st.sidebar.write(f"Supabase Save: {memory_status.get('supabase_save')}")
st.sidebar.write(f"URL: {get_redacted_supabase_url()}")

if memory_status.get("last_error"):
    st.sidebar.error(memory_status.get("last_error"))

st.sidebar.download_button(
    label="Download Memory JSON",
    data=export_memory_json(st.session_state),
    file_name="i_nik_memory_snapshot.json",
    mime="application/json"
)

if st.sidebar.button("Reset Chat Only"):
    reset_chat_only(st.session_state)
    st.rerun()

if st.sidebar.button("Reset All Memory"):
    reset_all_memory(st.session_state)
    st.rerun()

event_result = st.session_state.get("last_event_log_result")

st.sidebar.divider()
st.sidebar.subheader("Event Logging")

if event_result:
    st.sidebar.write(f"n8n OK: {event_result.get('ok')}")
    st.sidebar.write(f"Status: {event_result.get('status_code')}")

    if event_result.get("error"):
        st.sidebar.error(event_result.get("error"))
else:
    st.sidebar.write("ยังไม่มี event log")
redemption_result = st.session_state.get("last_redemption_result")

st.sidebar.divider()
st.sidebar.subheader("Redemption Status")

if redemption_result:
    st.sidebar.write(f"Redeem OK: {redemption_result.get('ok')}")

    if redemption_result.get("error"):
        st.sidebar.error(redemption_result.get("error"))

    if redemption_result.get("record"):
        st.sidebar.write(
            f"Item: {redemption_result['record'].get('item')}"
        )
else:
    st.sidebar.write("ยังไม่มี redemption")
health_result = run_health_check(st.session_state)

st.sidebar.divider()
st.sidebar.subheader("Health Check")

st.sidebar.write(get_health_label(health_result))

with st.sidebar.expander("Health Details"):
    for check in health_result["checks"]:
        icon = "✅" if check["status"] else "❌"
        st.write(f"{icon} {check['name']}: {check['detail']}")


st.title("i nik ◧")
st.caption("AI Character Loyalty Prototype")
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

    st.session_state.intimacy_score = min(
        100,
        st.session_state.intimacy_score + 10
    )

    st.session_state.points += 1

    reward = check_reward(st.session_state.points)

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

    direct_reply = answer_from_facts(
        user_message,
        st.session_state.user_facts
    )

    if direct_reply:
        reply = direct_reply

    else:
        prompt = f"""
{CHARACTER_BIBLE}

กฎบุคลิกตามระดับความสนิท:
{stage_description}

สถานะความสัมพันธ์:
{relationship_description}

โปรไฟล์ผู้ใช้:
{user_profile_description}

โหมดการตอบปัจจุบัน:
{response_mode_description}

ประวัติการคุยล่าสุด:
{chat_history}

ข้อมูลที่จำได้:
{st.session_state.user_facts}

กฎการใช้ความจำ:
- ถ้าข้อมูลที่จำได้มี name ให้ใช้ชื่อนั้นเมื่อตอบคำถามเกี่ยวกับชื่อผู้ใช้
- ห้ามตอบว่าไม่รู้ชื่อ ถ้าในข้อมูลที่จำได้มี name อยู่แล้ว
- ถ้าผู้ใช้ถามว่า "ฉันชื่ออะไร" ให้ตอบจากข้อมูลที่จำได้โดยตรง
- ใช้ความจำอย่างเป็นธรรมชาติ ไม่ต้องประกาศว่าอ่านจากระบบ

ผู้ใช้พูดว่า:
{user_message}
"""

        try:
            if USE_FAKE_AI or use_dev_test_mode:
                analytics = calculate_analytics(st.session_state)

                reply = generate_fake_reply(
                    user_message,
                    stage,
                    response_mode,
                    st.session_state.user_facts,
                    st.session_state.relationship_state,
                    analytics
                )
            else:
                response = model.generate_content(prompt)
                reply = response.text
        except Exception as e:
            reply = build_fallback_reply(
                str(e),
                user_message,
                stage,
                response_mode,
                st.session_state.user_facts,
                st.session_state.relationship_state
            )

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    if reward:
        st.session_state.inventory.append(reward)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"🎁 i nik เจอของแปลกให้เธอ: {reward}"
        })

    persist_current_state()

    event_result = send_event_to_n8n(
        "user_message",
        st.session_state,
        extra={
            "message": user_message,
            "reply": reply,
            "reward": reward
        }
    )

    st.session_state.last_event_log_result = event_result

    st.rerun()