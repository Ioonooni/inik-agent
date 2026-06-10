import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from confidence import MemoryConfidence, score_fact_reliability


# Matched as substrings — explicit user intent to recall stored memory only
_EXPLICIT_MEMORY_PHRASES = (
    # Name
    "ชื่ออะไร", "ชื่อว่าอะไร", "รู้ชื่อฉัน", "ชื่อของฉัน",
    # Likes / dislikes
    "ฉันชอบอะไร", "ชอบอะไรบ้าง", "ฉันไม่ชอบอะไร",
    # Memory recall
    "จำได้ไหม", "จำอะไรได้", "จำเรื่องอะไร", "จำฉันได้",
    "รู้จักฉัน", "รู้อะไรเกี่ยวกับฉัน",
    # Past conversation
    "ฉันเคยพูดว่า", "ฉันเคยบอก", "เคยพูดถึง",
    "เราเคยคุย", "เราเคยพูด",
    "ฉันบอกว่า", "ฉันบอกไว้",
    # Stored data
    "ข้อมูลของฉัน", "บอกข้อมูลฉัน", "บอกสิ่งที่จำ",
    "จำข้อมูล",
)

# Requires real-time data — no tool exists to fetch it
_LIVE_DATA_WORDS = (
    "อากาศ", "weather",
    "พยากรณ์",
    "กี่โมง", "เวลาตอนนี้",
    "ราคาทอง", "ราคาหุ้น", "ราคาน้ำมัน",
    "ข่าวล่าสุด", "ข่าววันนี้",
    "อัตราแลกเปลี่ยน", "เรตแลกเปลี่ยน",
    "bitcoin", "crypto",
)

# Knowledge / factual questions — Gemini answers from training, no memory needed
_KNOWLEDGE_VERBS = (
    "คืออะไร", "อธิบาย", "เล่าเรื่อง",
    "หมายความว่า", "ความหมายของ",
    "ทำงานยังไง", "เกิดขึ้นยังไง",
    "เพราะอะไร",
    "เท่ากับ", "เท่าไหร่", "คำนวณ",
    "กลมไหม", "มีจริงไหม", "เป็นจริงไหม",
    "explain", "what is", "how does",
    "ประวัติของ", "ทฤษฎี", "สูตร",
)

# Game / state queries — answered by planner tools
_TOOL_WORDS = (
    "คะแนน", "แต้ม", "point", "points",
    "inventory", "ไอเท็ม", "ของใน inventory", "ดูของ",
    "ของรางวัล", "รางวัล",
    "stage", "เลเวล",
    "สถานะของฉัน",
)

# Relationship state queries
_RELATIONSHIP_WORDS = (
    "ความสนิท", "ความสัมพันธ์", "trust", "familiarity",
    "รู้สึกไงกับฉัน", "ชอบฉันไหม",
)

# Simple math expression — whole text is pure arithmetic
_MATH_RE = re.compile(r'^[\d\s\+\-\*\/\=\(\)\.]+$')

# Extract arithmetic sub-expression from text that may also contain Thai words
_MATH_EXPR_RE = re.compile(r'[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)+')

_MATH_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_ast_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _MATH_OPS:
        return _MATH_OPS[type(node.op)](_eval_ast_node(node.left), _eval_ast_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _MATH_OPS:
        return _MATH_OPS[type(node.op)](_eval_ast_node(node.operand))
    raise ValueError(f"unsupported node: {type(node)}")


def _try_eval_math(text: str) -> Optional[str]:
    """Extract and evaluate the first arithmetic expression in text.
    Uses AST — no eval() call. Returns string result or None."""
    stripped = text.strip()
    candidates = []

    # If the whole text is pure math, try it first
    if _MATH_RE.match(stripped):
        candidates.append(stripped)

    # Also try extracting a sub-expression (e.g. "2+2" from "2+2 เท่ากับเท่าไหร่")
    for m in _MATH_EXPR_RE.finditer(stripped):
        candidates.append(m.group(0).strip())

    for expr in candidates:
        if not expr:
            continue
        try:
            tree = ast.parse(expr, mode="eval")
            result = _eval_ast_node(tree.body)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            # Reject absurd or complex results
            if isinstance(result, (int, float)) and abs(result) <= 1e15:
                return str(result)
        except Exception:
            continue
    return None


class QueryType:
    MEMORY_QUERY = "MEMORY_QUERY"
    FACTUAL_QUERY = "FACTUAL_QUERY"
    NORMAL_CHAT = "NORMAL_CHAT"
    TOOL_QUERY = "TOOL_QUERY"
    RELATIONSHIP_QUERY = "RELATIONSHIP_QUERY"


@dataclass
class QueryClassification:
    query_type: str
    confidence: MemoryConfidence
    memory_key: Optional[str] = None
    requires_live_data: bool = False
    can_answer_directly: bool = False
    direct_answer: Optional[str] = None


def _detect_memory_key(text: str) -> Optional[str]:
    if "ชื่อ" in text or "name" in text:
        return "name"
    if "ชอบ" in text or "likes" in text:
        return "likes"
    return None


def classify(user_message: str, user_facts: Dict[str, Any]) -> QueryClassification:
    text = (user_message or "").lower().strip()

    # 1. Live data — real-time info unavailable without a tool
    if any(w in text for w in _LIVE_DATA_WORDS):
        return QueryClassification(
            query_type=QueryType.FACTUAL_QUERY,
            confidence=MemoryConfidence.UNKNOWN,
            requires_live_data=True,
            can_answer_directly=False,
        )

    # 2. Explicit memory question — user is asking about stored facts/history
    if any(phrase in text for phrase in _EXPLICIT_MEMORY_PHRASES):
        memory_key = _detect_memory_key(text)
        if memory_key and user_facts.get(memory_key):
            conf = score_fact_reliability(user_facts, memory_key)
        elif user_facts:
            conf = MemoryConfidence.MEDIUM
        else:
            conf = MemoryConfidence.UNKNOWN

        return QueryClassification(
            query_type=QueryType.MEMORY_QUERY,
            confidence=conf,
            memory_key=memory_key,
            requires_live_data=False,
            can_answer_directly=bool(memory_key and user_facts.get(memory_key)),
        )

    # 3. Tool / game-state queries
    if any(w in text for w in _TOOL_WORDS):
        return QueryClassification(
            query_type=QueryType.TOOL_QUERY,
            confidence=MemoryConfidence.HIGH,
            can_answer_directly=True,
        )

    # 4. Relationship state queries
    if any(w in text for w in _RELATIONSHIP_WORDS):
        return QueryClassification(
            query_type=QueryType.RELATIONSHIP_QUERY,
            confidence=MemoryConfidence.HIGH,
            can_answer_directly=True,
        )

    # 5. Knowledge / factual question — Gemini knows this from training
    if any(v in text for v in _KNOWLEDGE_VERBS) or _MATH_RE.match(text):
        math_result = _try_eval_math(text)
        return QueryClassification(
            query_type=QueryType.FACTUAL_QUERY,
            confidence=MemoryConfidence.HIGH,
            requires_live_data=False,
            can_answer_directly=math_result is not None,
            direct_answer=math_result,
        )

    # 6. Default — regular conversation
    return QueryClassification(
        query_type=QueryType.NORMAL_CHAT,
        confidence=MemoryConfidence.MEDIUM,
        can_answer_directly=False,
    )
