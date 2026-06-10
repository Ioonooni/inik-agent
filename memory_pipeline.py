from typing import Any, Dict, Optional

from memory_quality import assess_memory_quality
from memory_schema import build_memory_record, record_to_dict, should_promote_to_long_term


def build_memory_from_message(
    user_id: str,
    message: str,
    source: str = "chat",
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    quality = assess_memory_quality(message)

    if not quality.should_store:
        return None

    record = build_memory_record(
        user_id=user_id,
        content=message,
        memory_type=quality.memory_type,
        importance=quality.importance,
        source=source,
        metadata={
            **(metadata or {}),
            "quality_reason": quality.reason,
            "promote_to_long_term": False,
        },
    )

    data = record_to_dict(record)
    data["metadata"]["promote_to_long_term"] = should_promote_to_long_term(record)

    return data


def explain_memory_decision(message: str) -> Dict[str, Any]:
    quality = assess_memory_quality(message)
    return {
        "message": message,
        "should_store": quality.should_store,
        "memory_type": quality.memory_type,
        "importance": quality.importance,
        "reason": quality.reason,
    }
