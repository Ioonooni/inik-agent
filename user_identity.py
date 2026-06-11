import streamlit as st


DEFAULT_DEMO_USER_ID = "demo_user"


def get_current_user_id(session_state=None) -> str:
    """
    Single source of truth for current user id.

    Priority:
    1. session_state.user_id
    2. st.session_state.user_id
    3. demo_user fallback
    """
    if session_state is not None:
        user_id = session_state.get("user_id")
        if user_id:
            return str(user_id)

    try:
        user_id = st.session_state.get("user_id")
        if user_id:
            return str(user_id)
    except Exception:
        pass

    return DEFAULT_DEMO_USER_ID
