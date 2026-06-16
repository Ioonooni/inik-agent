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
* Memory Quality Filtering
* Fact Extraction
* User Profile Extraction
* Memory Ranking Engine
* Retrieval-Augmented Context (RAG)
* Context-Aware Recall

Purpose:

Improve memory precision, reduce low-value memory storage, and retrieve the most relevant information during conversations.

This architecture moves beyond simple chat history storage toward a structured long-term memory system.

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

### Behavioral Validation

Current evaluation focuses on:

* Memory Accuracy
* Recall Consistency
* Relationship-State Persistence
* Character Continuity
* Response Routing Correctness

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

i nik is currently deployed as a live MVP and serves as a reusable AI application framework for conversational AI products.

The current version supports:

* Persistent Memory
* User Profiling
* Relationship-State Tracking
* Memory Ranking
* RAG-Based Context Retrieval
* Strategic Reasoning Modes
* Personalized Conversations
* Supabase Persistence
* Event Logging
* Deployment-Ready Architecture

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

## Future Roadmap

### Phase 2

Adaptive Personality System

Goals:

* Personality State Machine
* Behavioral Adaptation
* User-Specific Interaction Styles
* Stronger Character Consistency

---

### Phase 3

Advanced Relationship Progression

Goals:

* Dynamic Familiarity Levels
* Personalized Interaction Paths
* Loyalty Progression
* Long-Term User Modeling

---

### Phase 4

Multi-Agent Orchestration

Goals:

* Hidden Specialist Agents
* Shared Memory Layer
* Shared User Identity
* Agent Routing
* Cognitive Mode Switching

Users continue interacting with a unified system rather than multiple visible agents.

---

### Phase 5

AI Companion Platform

Goals:

* Multi-User Architecture
* Authentication
* CRM Integration
* Loyalty Systems
* Commerce Integration
* Character Ecosystem

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
