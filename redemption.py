from rewards import get_shop_item
from datetime import datetime, timezone
from uuid import uuid4

from user_identity import get_current_user_id


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
        "user_id": get_current_user_id(session_state),
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


def buy_reward_item(session_state, item_id):
    item = get_shop_item(item_id)

    if not item:
        return {
            "ok": False,
            "error": "Unknown shop item",
            "record": None,
        }

    cost = int(item.get("cost", 0))
    current_points = int(session_state.get("points", 0))

    if current_points < cost:
        return {
            "ok": False,
            "error": f"Not enough points. Need {cost}, have {current_points}",
            "record": None,
        }

    inventory = list(session_state.get("inventory", []))
    purchased_item = dict(item)
    inventory.append(purchased_item)

    session_state.points = current_points - cost
    session_state.inventory = inventory

    record = {
        "redemption_id": str(uuid4()),
        "item": purchased_item,
        "cost": cost,
        "redeemed_at": datetime.now(timezone.utc).isoformat(),
        "user_id": get_current_user_id(session_state),
        "status": "purchased",
    }

    user_profile = session_state.get("user_profile", {})
    redemption_history = get_redemption_history(user_profile)
    redemption_history.append(record)

    user_profile["redemption_history"] = redemption_history[-20:]
    user_profile["redemption_count"] = len(user_profile["redemption_history"])
    session_state.user_profile = user_profile

    return {
        "ok": True,
        "error": None,
        "record": record,
    }
