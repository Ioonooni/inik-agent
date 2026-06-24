# i nik

## Memory-Driven AI Character Platform

i nik is a behavioral AI character platform designed to explore how memory, identity, relationship progression, and strategic reasoning can create long-term engagement beyond traditional chatbots.

Rather than functioning as a task-oriented assistant, i nik is designed as a persistent AI system that develops familiarity with users over time through memory retrieval, profile understanding, relationship-state awareness, and contextual reasoning.

The project explores a broader product hypothesis:

People rarely form attachment to interfaces.

People form attachment to personalities, continuity, and remembered experiences.

i nik serves as a prototype for future AI-native products including companion systems, tutoring systems, strategic advisors, language partners, and multi-agent experiences.

---

## Live Demo

https://inik-cafe.vercel.app

---

## Vision

Most AI products are optimized for question answering.

i nik is optimized for continuity.

The project explores whether AI systems can create stronger long-term engagement through:

* Memory
* Familiarity
* Identity
* Relationship progression
* Character consistency
* Personalized context
* Behavioral design
* Strategic reasoning
* Long-term interaction loops

The long-term vision is not a chatbot.

The long-term vision is a reusable AI platform capable of supporting multiple AI experiences through a shared memory, profile, and reasoning architecture.

---

## Product Philosophy

i nik is not designed as a single character application.

The architecture is intended to support multiple AI products while sharing the same core infrastructure:

* Memory Systems
* User Profiles
* Relationship Tracking
* Retrieval Systems
* Event Logging
* Analytics
* Workflow Automation

This allows future products to reuse the same foundation while changing behavior, personality, and reasoning layers.

---

## Heart and Mind Architecture

The platform currently explores two cognitive modes:

### i nik (Heart Layer)

Responsibilities:

* Memory Retrieval
* User Understanding
* Relationship Awareness
* Personal Continuity
* Emotional Context
* Long-Term Familiarity

i nik functions as the memory and continuity layer of the ecosystem.

---

### Rick Royce (Mind Layer)

Responsibilities:

* Strategic Reasoning
* Tradeoff Analysis
* Opportunity Cost Evaluation
* Risk Assessment
* Decision Support
* Long-Term Thinking

Rick Royce functions as a strategic reasoning layer rather than a separate product.

The goal is to allow users to move between emotional context and strategic thinking while maintaining a shared identity, memory system, and relationship history.

---

## Current Architecture

User

↓

React Frontend

↓

FastAPI Backend

↓

Memory Retrieval Layer

↓

Profile & Relationship State

↓

Prompt Construction

↓

Reasoning Layer

↓

Google Gemini

↓

Response Generation

↓

Persistence Layer

├── Supabase

└── JSON Fallback

↓

Event Logging

↓

n8n Automation Layer

---

## Core Systems

### Memory System

Features:

* Persistent Memory
* Supabase-backed Storage
* Conversation Memory
* Fact Memory
* User Profile Memory
* Context Retrieval
* Runtime Memory Loading

Purpose:

Maintain continuity across sessions and reduce stateless chatbot behavior.

---

### Advanced Memory Architecture

Features:

* Memory Gateway V2
* Memory Quality Filtering (importance scoring by category)
* Memory Reinforcement (hit-count bonuses for recurring facts)
* Memory Decay Engine (time-based importance decay by memory type)
* Conflict Detection (7-category preference conflict analysis)
* Soft Supersede (losers marked, never deleted)
* Memory Ranking Engine (effective_importance + recency + relevance)
* Retrieval-Augmented Context (RAG) — query-matched and time-ordered paths
* Shared Memory Layer (memories_v2 table + local JSON fallback)
* Context-Aware Recall

Purpose:

Improve memory precision, reduce low-value memory storage, and retrieve the most relevant information during conversations.

This architecture moves beyond simple chat history storage toward a structured long-term memory system with quality gating, reinforcement, decay, and conflict resolution.

---

### Relationship Engine

Tracks:

* Trust
* Familiarity
* Curiosity
* Attachment
* Relationship Score
* Relationship Stage

Features:

* Observer Progression
* Gremlin Progression
* Treasure Progression
* Relationship Decay
* Re-engagement Awareness

Purpose:

Allow the character to respond differently depending on relationship history rather than treating every conversation as a first interaction.

---

### Strategic Reasoning Layer

Features:

* Rick Royce Strategic Mode
* Tradeoff Analysis
* Assumption Checking
* Opportunity Cost Evaluation
* Decision Support Reasoning
* Strategic Reflection Framework

Purpose:

Provide a dedicated reasoning layer for decisions involving investment, career planning, business analysis, and long-term thinking.

---

### Response Mode Engine

Modes include:

* Normal Chat
* Philosophy Chat
* Comfort Choice
* Memory Callback
* Reward Event
* Strategic Reasoning

Purpose:

Maintain consistent behavior while adapting responses to different user needs and contexts.

---

### Reward System

Features:

* Point Accumulation
* Variable Rewards
* Inventory System
* Reward Redemption

Purpose:

Introduce lightweight progression systems and recurring interaction rituals.

---

### Autonomous Layer

Features:

* Relationship Checkpoints
* Reward Suggestions
* Memory Prompts
* Cooldown Protection

Purpose:

Allow the system to proactively support engagement rather than remaining entirely reactive.

---

### Event Logging

Features:

* Structured Event Tracking
* Supabase Event Storage
* n8n Webhook Integration
* Analytics-Ready Payloads

Purpose:

Provide infrastructure for future CRM, loyalty systems, analytics, and workflow automation.

---

## Evaluation and Testing

The project includes multiple layers of validation:

### System Validation

* Unit Testing
* Integration Testing
* End-to-End Testing
* Smoke Testing
* Runtime Persistence Testing

### Memory Validation

* Memory Recall Verification
* Retrieval Quality Testing
* Memory Ranking Validation
* Fact Extraction Testing
* Profile Extraction Testing
* Memory Intelligence Phase Tests (Phases 3.1–3.4, 4.1–4.6)

### Behavioral Validation

Current evaluation focuses on:

* Memory Accuracy
* Recall Consistency
* Relationship-State Persistence
* Character Continuity
* Response Routing Correctness

### Final Validation

Roadmap v1 closure: 70 tests passed across all system, memory, and integration test suites.

Future work includes formal LLM evaluation frameworks, automated character-consistency benchmarks, hallucination detection, and retrieval-quality scoring.

---

## Technical Stack

### Frontend

* React
* TypeScript
* Vite

### Backend

* FastAPI
* Python

### AI

* Google Gemini API

### Database

* Supabase

### Workflow Automation

* n8n

### Development Environment

* GitHub Codespaces

---

## Current Status

Roadmap v1 is complete.

i nik Platform v1 is a complete foundation for a memory-driven AI character platform. This is not an enterprise SaaS final form — it is a deliberate v1 scope that proves the core architecture and product hypothesis.

The current version supports:

* Persistent Memory with Quality Scoring and Decay
* Memory Conflict Detection and Soft Supersede
* Memory V2 Shared Layer with Local Fallback
* RAG-Based Context Retrieval (query-matched and time-ordered)
* User Profiling and Fact Extraction
* Relationship-State Tracking (Trust, Familiarity, Curiosity, Attachment)
* Relationship Progression and Decay
* Adaptive Personality System with Personality Matrix
* Character Registry (i nik + Rick Royce)
* Agent Routing between Character Modes
* Reward Economy and Loyalty Progression
* CRM Event Contract v1 (Supabase + n8n webhook)
* Multi-User Architecture with Supabase Auth Foundation
* Deployment-Ready Architecture (FastAPI backend + React/Vite frontend)

---

## V3 Runtime Integration Complete

V3 moves the platform's memory intelligence and shared cognitive architecture from isolated components into the production runtime.

Delivered:

* Memory Lifecycle filtering integrated into RAG retrieval
* Archived and superseded memories excluded from active context
* Backward compatibility retained for legacy memory records
* Shared Cognitive Layer used across i nik, Rick Royce, and hybrid response paths
* Shared user identity, profile, relationship state, and memory context across character modes
* Production agent routing between i nik (Heart) and Rick Royce (Mind)
* Thai structured-fact extraction and direct recall verification
* Favorite-color regression fixed without overwriting the user's name
* Backend regression suite verified with 109 passing checks and 0 failures
* FastAPI production deployment verified on Render
* React/Vite production build verified against the deployed backend
* Backend and frontend repositories synchronized with clean working trees

Production API:

`https://inik-agent.onrender.com`

Frontend:

`https://inik-cafe.vercel.app`

Current operational limitation:

Google Gemini free-tier requests may return HTTP 429 when the external quota is exhausted. This is an API quota limitation rather than a failure of the memory, routing, persistence, or retrieval architecture.

---

## Development Milestones

### Phase 1 Completed

* Character Framework
* Persistent Memory
* Relationship Engine
* Planner System
* Response Routing
* Reward Shop
* Redemption System
* Event Logging
* Autonomous Behaviors
* Supabase Integration
* Runtime Persistence
* Memory Retrieval
* User Profiling

---

### Phase 2 Completed

Adaptive Personality System

Delivered:

* Personality State Machine (Observer / Gremlin / Treasure)
* Personality Matrix (mood, conversation style, user archetype signals)
* Behavioral Adaptation per relationship stage
* User-Specific Interaction Styles
* Tone Directive System
* Re-engagement Awareness

---

### Phase 3 Completed

Memory Intelligence

Delivered:

* Memory Quality Scoring v2 (importance by category: name, possession, preference, study, emotional, etc.)
* Memory Reinforcement (hit-count bonuses, capped at 100)
* Memory Decay Engine (type-based decay rates; high-frequency memories decay slower)
* Conflict Detection (7 categories: name, dislike, preference, study, project, location, possession)
* Soft Supersede (losing record marked superseded, never deleted; 0.25× ranking penalty)
* Memory Ranking Engine (effective_importance + recency + relevance + hit-count)

---

### Phase 4 Completed

Shared Memory Layer and Agent Routing

Delivered:

* Memory V2 Write Path (save_message_memory_v2 with quality gating)
* Memory Gateway V2 (Supabase primary + local JSON fallback)
* Conflict Detection integrated into write path
* RAG Ranking applied to all retrieval paths (search and list_recent)
* list_recent_memories_v2 wired into runtime recall
* app.py write path migrated from legacy to Memory V2
* End-to-end integration test suite (Phase 4.6)
* Agent Routing between i nik (Heart Layer) and Rick Royce (Mind Layer)

---

### Phase 5 Completed

Platform Foundation

Delivered:

* Character Registry (i nik + Rick Royce as distinct registered characters)
* Character Ecosystem v1 (shared memory, shared user identity across characters)
* Multi-User Architecture
* Supabase Auth Foundation
* CRM Event Contract v1 (structured event payloads, Supabase event table, n8n webhook)
* Loyalty Progression and Reward Economy
* Deployment-Ready Architecture (FastAPI API + React/Vite interface)

---

## Roadmap v1 Complete

Phases 1–5 are complete.

This represents a deliberate Platform v1 scope — not an enterprise SaaS final form, but a complete and tested foundation for memory-driven AI character products.

Possible next directions include multi-character expansion, semantic memory search, formal LLM evaluation frameworks, and commerce or subscription integration. These are outside Roadmap v1 scope.

---

## Why This Project Matters

Most AI applications stop at generating responses.

i nik explores whether AI systems can build continuity through memory, relationship awareness, contextual understanding, and strategic reasoning.

The project combines:

* AI Engineering
* Memory Architecture
* Behavioral Design
* Relationship Systems
* Strategic Reasoning
* Workflow Automation
* Product Design
* Applied AI Product Thinking

Rather than building another chatbot, i nik investigates how persistent AI systems may evolve into a new category of digital products.
