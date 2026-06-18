diff --git a/README.md b/README.md
index 2bb55e5..4c449d7 100644
--- a/README.md
+++ b/README.md
@@ -179,18 +179,21 @@ Maintain continuity across sessions and reduce stateless chatbot behavior.
 Features:
 
 * Memory Gateway V2
-* Memory Quality Filtering
-* Fact Extraction
-* User Profile Extraction
-* Memory Ranking Engine
-* Retrieval-Augmented Context (RAG)
+* Memory Quality Filtering (importance scoring by category)
+* Memory Reinforcement (hit-count bonuses for recurring facts)
+* Memory Decay Engine (time-based importance decay by memory type)
+* Conflict Detection (7-category preference conflict analysis)
+* Soft Supersede (losers marked, never deleted)
+* Memory Ranking Engine (effective_importance + recency + relevance)
+* Retrieval-Augmented Context (RAG) — query-matched and time-ordered paths
+* Shared Memory Layer (memories_v2 table + local JSON fallback)
 * Context-Aware Recall
 
 Purpose:
 
 Improve memory precision, reduce low-value memory storage, and retrieve the most relevant information during conversations.
 
-This architecture moves beyond simple chat history storage toward a structured long-term memory system.
+This architecture moves beyond simple chat history storage toward a structured long-term memory system with quality gating, reinforcement, decay, and conflict resolution.
 
 ---
 
@@ -317,6 +320,7 @@ The project includes multiple layers of validation:
 * Memory Ranking Validation
 * Fact Extraction Testing
 * Profile Extraction Testing
+* Memory Intelligence Phase Tests (Phases 3.1–3.4, 4.1–4.6)
 
 ### Behavioral Validation
 
@@ -328,6 +332,10 @@ Current evaluation focuses on:
 * Character Continuity
 * Response Routing Correctness
 
+### Final Validation
+
+Roadmap v1 closure: 70 tests passed across all system, memory, and integration test suites.
+
 Future work includes formal LLM evaluation frameworks, automated character-consistency benchmarks, hallucination detection, and retrieval-quality scoring.
 
 ---
@@ -365,20 +373,26 @@ Future work includes formal LLM evaluation frameworks, automated character-consi
 
 ## Current Status
 
-i nik is currently deployed as a live MVP and serves as a reusable AI application framework for conversational AI products.
+Roadmap v1 is complete.
+
+i nik Platform v1 is a complete foundation for a memory-driven AI character platform. This is not an enterprise SaaS final form — it is a deliberate v1 scope that proves the core architecture and product hypothesis.
 
 The current version supports:
 
-* Persistent Memory
-* User Profiling
-* Relationship-State Tracking
-* Memory Ranking
-* RAG-Based Context Retrieval
-* Strategic Reasoning Modes
-* Personalized Conversations
-* Supabase Persistence
-* Event Logging
-* Deployment-Ready Architecture
+* Persistent Memory with Quality Scoring and Decay
+* Memory Conflict Detection and Soft Supersede
+* Memory V2 Shared Layer with Local Fallback
+* RAG-Based Context Retrieval (query-matched and time-ordered)
+* User Profiling and Fact Extraction
+* Relationship-State Tracking (Trust, Familiarity, Curiosity, Attachment)
+* Relationship Progression and Decay
+* Adaptive Personality System with Personality Matrix
+* Character Registry (i nik + Rick Royce)
+* Agent Routing between Character Modes
+* Reward Economy and Loyalty Progression
+* CRM Event Contract v1 (Supabase + n8n webhook)
+* Multi-User Architecture with Supabase Auth Foundation
+* Deployment-Ready Architecture (FastAPI + Streamlit)
 
 ---
 
@@ -402,62 +416,76 @@ The current version supports:
 
 ---
 
-## Future Roadmap
-
-### Phase 2
+### Phase 2 Completed
 
 Adaptive Personality System
 
-Goals:
+Delivered:
 
-* Personality State Machine
-* Behavioral Adaptation
+* Personality State Machine (Observer / Gremlin / Treasure)
+* Personality Matrix (mood, conversation style, user archetype signals)
+* Behavioral Adaptation per relationship stage
 * User-Specific Interaction Styles
-* Stronger Character Consistency
+* Tone Directive System
+* Re-engagement Awareness
 
 ---
 
-### Phase 3
+### Phase 3 Completed
 
-Advanced Relationship Progression
+Memory Intelligence
 
-Goals:
+Delivered:
 
-* Dynamic Familiarity Levels
-* Personalized Interaction Paths
-* Loyalty Progression
-* Long-Term User Modeling
+* Memory Quality Scoring v2 (importance by category: name, possession, preference, study, emotional, etc.)
+* Memory Reinforcement (hit-count bonuses, capped at 100)
+* Memory Decay Engine (type-based decay rates; high-frequency memories decay slower)
+* Conflict Detection (7 categories: name, dislike, preference, study, project, location, possession)
+* Soft Supersede (losing record marked superseded, never deleted; 0.25× ranking penalty)
+* Memory Ranking Engine (effective_importance + recency + relevance + hit-count)
 
 ---
 
-### Phase 4
+### Phase 4 Completed
 
-Multi-Agent Orchestration
+Shared Memory Layer and Agent Routing
 
-Goals:
+Delivered:
 
-* Hidden Specialist Agents
-* Shared Memory Layer
-* Shared User Identity
-* Agent Routing
-* Cognitive Mode Switching
-
-Users continue interacting with a unified system rather than multiple visible agents.
+* Memory V2 Write Path (save_message_memory_v2 with quality gating)
+* Memory Gateway V2 (Supabase primary + local JSON fallback)
+* Conflict Detection integrated into write path
+* RAG Ranking applied to all retrieval paths (search and list_recent)
+* list_recent_memories_v2 wired into runtime recall
+* app.py write path migrated from legacy to Memory V2
+* End-to-end integration test suite (Phase 4.6)
+* Agent Routing between i nik (Heart Layer) and Rick Royce (Mind Layer)
 
 ---
 
-### Phase 5
+### Phase 5 Completed
 
-AI Companion Platform
+Platform Foundation
 
-Goals:
+Delivered:
 
+* Character Registry (i nik + Rick Royce as distinct registered characters)
+* Character Ecosystem v1 (shared memory, shared user identity across characters)
 * Multi-User Architecture
-* Authentication
-* CRM Integration
-* Loyalty Systems
-* Commerce Integration
-* Character Ecosystem
+* Supabase Auth Foundation
+* CRM Event Contract v1 (structured event payloads, Supabase event table, n8n webhook)
+* Loyalty Progression and Reward Economy
+* Deployment-Ready Architecture (FastAPI API + Streamlit interface)
+
+---
+
+## Roadmap v1 Complete
+
+Phases 1–5 are complete.
+
+This represents a deliberate Platform v1 scope — not an enterprise SaaS final form, but a complete and tested foundation for memory-driven AI character products.
+
+Possible next directions include multi-character expansion, semantic memory search, formal LLM evaluation frameworks, and commerce or subscription integration. These are outside Roadmap v1 scope.
 
 ---
 
