from unittest.mock import patch

from memory_gateway_v2 import save_message_memory_v2
from rag_prompt import build_safe_rag_context


USER_ID = "v3-shared-user"


def fake_record(user_id, message, source="chat", metadata=None):
    return {
        "memory_id": f"{user_id}-shared-001",
        "user_id": user_id,
        "content": message,
        "memory_type": "user_fact",
        "importance": 85,
        "source": source,
        "metadata": metadata or {},
        "schema_version": "memory_v2",
        "hit_count": 1,
    }


def run():
    stored_records = []

    def capture_upsert(client, record):
        stored_records.append(record)
        return {"ok": True, "memory_id": record["memory_id"]}

    def fake_search_memory_notes(user_id, query, limit=5):
        results = [
            record for record in stored_records
            if record["user_id"] == user_id
        ][:limit]
        return {
            "ok": True,
            "backend": "fake_shared_memory",
            "results": results,
        }

    with patch("memory_gateway_v2.build_memory_from_message", side_effect=fake_record), \
         patch("memory_gateway_v2.get_supabase_client", return_value=object()), \
         patch("memory_gateway_v2._check_and_supersede_conflicts", return_value={"checked": True, "superseded": 0}), \
         patch("memory_gateway_v2.upsert_supabase_memory", side_effect=capture_upsert), \
         patch("rag_memory.search_memory_notes", side_effect=fake_search_memory_notes):

        save_result = save_message_memory_v2(
            user_id=USER_ID,
            message="ฉันกำลังสร้าง i nik V3 Heart Mind Architecture",
            source="chat",
            metadata={"agent_mode": "rick_royce", "route": "api_chat"},
        )

        assert save_result["stored"] is True
        assert stored_records[0]["metadata"]["agent_mode"] == "rick_royce"

        inik_context = build_safe_rag_context(
            user_id=USER_ID,
            user_message="จำได้ไหมว่าฉันกำลังสร้างอะไร",
            limit=5,
        )

        assert "i nik V3 Heart Mind Architecture" in inik_context

    print("shared cognitive layer ok")


if __name__ == "__main__":
    run()
