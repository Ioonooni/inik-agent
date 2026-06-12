from redemption import buy_reward_item, redeem_first_inventory_item
from rewards import get_reward_shop


class Session(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


shop = get_reward_shop()
assert shop, "reward shop must not be empty"

item = shop[0]
cost = int(item.get("cost", 0))

session = Session(
    user_id="test_user",
    points=cost,
    inventory=[],
    user_profile={},
)

purchase = buy_reward_item(session, item["id"])
assert purchase["ok"] is True, purchase
assert session["points"] == 0, session
assert len(session["inventory"]) == 1, session
assert purchase["record"]["status"] == "purchased", purchase
assert session["user_profile"]["redemption_count"] == 1, session

redeem = redeem_first_inventory_item(session)
assert redeem["ok"] is True, redeem
assert len(session["inventory"]) == 0, session
assert redeem["record"]["status"] == "redeemed", redeem
assert session["user_profile"]["redemption_count"] == 2, session

not_enough = Session(
    user_id="test_user",
    points=0,
    inventory=[],
    user_profile={},
)
fail = buy_reward_item(not_enough, item["id"])
assert fail["ok"] is False, fail
assert "Not enough points" in fail["error"], fail

print("REDEMPTION V1 TESTS PASSED")
