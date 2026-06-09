from datetime import datetime, timezone
from uuid import uuid4


def get_redemption_history(user_profile):
    if "redemption_history" not in user_profile:
        user_profile["redemption_history"] = []

    return user_profile["redemption_history"]


def redeem_first_inventory_item(session_state):
    inventory = session_state.get("inventory", [])
    user_profile = session_state.get("user_profile", {})

    if not inventory:
        return {
            "ok": False,
            "error": "No inventory item available to redeem",
            "record": None
        }

    redeemed_item = inventory.pop(0)

    record = {
        "redemption_id": str(uuid4()),
        "item": redeemed_item,
        "redeemed_at": datetime.now(timezone.utc).isoformat(),
        "user_id": "demo_user",
        "status": "redeemed"
    }

    redemption_history = get_redemption_history(user_profile)
    redemption_history.append(record)

    user_profile["redemption_history"] = redemption_history[-20:]
    user_profile["redemption_count"] = len(user_profile["redemption_history"])

    session_state.inventory = inventory
    session_state.user_profile = user_profile

    return {
        "ok": True,
        "error": None,
        "record": record
    }


def get_redemption_count(user_profile):
    return len(user_profile.get("redemption_history", []))


def get_latest_redemption(user_profile):
    history = user_profile.get("redemption_history", [])

    if not history:
        return None

    return history[-1]