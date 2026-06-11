import random


REWARDS = [
    {
        "name": "เศษดาวสีฟ้า",
        "rarity": "common",
        "type": "material",
        "description": "เศษแสงเล็ก ๆ ที่เหมือนหลุดมาจากท้องฟ้า",
    },
    {
        "name": "หินก้อนเล็กที่ดูเหมือนเมฆ",
        "rarity": "common",
        "type": "material",
        "description": "เบามากจนไม่น่าไว้ใจ แต่ยังเป็นหินอยู่",
    },
    {
        "name": "ใบชาจากป่าลับ",
        "rarity": "rare",
        "type": "gift",
        "description": "ใบชาที่มีกลิ่นเหมือนความทรงจำที่ยังไม่เกิดขึ้น",
    },
    {
        "name": "เรื่องเล่าสั้น ๆ จากหลังร้าน",
        "rarity": "rare",
        "type": "story",
        "description": "เรื่องเล่าที่ i nik เก็บไว้ให้เฉพาะคนที่คุยกันมาสักพัก",
    },
    {
        "name": "ความลับเล็ก ๆ ของ i nik",
        "rarity": "epic",
        "type": "story",
        "description": "ไม่ใช่ความลับใหญ่ แต่ก็ไม่ใช่ของที่แจกมั่ว ๆ",
    },
]


def _legacy_item_name(item):
    if isinstance(item, dict):
        return item.get("name", "Unknown reward")
    return str(item)


def check_reward(points):
    if points == 0:
        return None

    if points % 5 == 0:
        reward = random.choice(REWARDS)
        return dict(reward)

    return None


def format_reward(item):
    if not item:
        return ""

    if isinstance(item, dict):
        name = item.get("name", "Unknown reward")
        rarity = item.get("rarity", "common")
        item_type = item.get("type", "item")
        description = item.get("description", "")
        return f"{name} [{rarity}/{item_type}] — {description}".strip()

    return _legacy_item_name(item)
