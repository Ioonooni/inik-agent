import random


def check_reward(points):
    if points == 0:
        return None

    if points % 5 == 0:
        rewards = [
            "เศษดาวสีฟ้า",
            "ใบชาจากป่าลับ",
            "หินก้อนเล็กที่ดูเหมือนเมฆ",
            "เรื่องเล่าสั้น ๆ จากหลังร้าน",
            "ความลับเล็ก ๆ ของ i nik"
        ]

        return random.choice(rewards)

    return None