from facts import extract_facts, answer_from_facts

facts = extract_facts("สีโปรดของฉันคือสีม่วง", {})

assert facts.get("favorite_color") == "สีม่วง", facts
assert facts.get("likes") == "สีม่วง", facts
assert "name" not in facts, facts

reply = answer_from_facts("สีโปรดของฉันคือสีอะไร", facts)
assert reply and "สีม่วง" in reply, reply

print("favorite color fact regression ok")
