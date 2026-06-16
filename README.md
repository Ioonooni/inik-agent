# i nik

AI Character Interaction System

i nik is a behavioral AI character prototype designed to explore how memory, relationship progression, gamification, and personality systems can create long-term engagement beyond traditional chatbots.

Instead of functioning as a simple assistant, i nik is designed as a persistent character that gradually develops familiarity with users through conversation history, memory systems, relationship signals, rewards, autonomous behaviors, and backend workflow automation.

This project serves as a prototype for future Character AI products, AI-native brand experiences, and relationship-driven digital companions.

---

## Live Demo

https://inik-ai-prototype-kqelfbrxvnbk3xtygziygn.streamlit.app/

---

## Vision

Most AI assistants are designed to answer questions.

i nik is designed to build familiarity.

The project explores a different hypothesis:

People rarely form emotional attachment to interfaces.

People form attachment to characters.

Instead of optimizing only for task completion, i nik is designed around:

* Memory
* Familiarity
* Relationship progression
* Character consistency
* Small rituals
* Variable rewards
* Long-term engagement

The long-term vision is not a chatbot.

The long-term vision is a persistent AI character capable of existing across products, communities, loyalty systems, games, physical stores, and future digital experiences.

---

## What Makes This Different

Most chatbot projects focus on:

* Question answering
* Information retrieval
* Productivity assistance

i nik focuses on:

* Character attachment
* Relationship development
* Personality progression
* Behavioral design
* User retention systems
* Memory persistence
* Gamified interaction loops

The goal is to explore Character AI as a product category rather than a traditional chatbot experience.

---

## Current Architecture

User

↓

Intent Classification

↓

Planner

↓

Tool Layer

├── Memory

├── Relationship

├── Inventory

├── Rewards

├── Analytics

└── Event Logging

↓

Response Router

↓

Character Response

↓

Persistence Layer

├── Supabase

└── JSON Fallback

↓

Workflow Layer

└── n8n

---

## Current Features

### Memory System

* Persistent memory
* Supabase-backed storage
* Memory ranking
* Context retrieval
* User profile memory
* Fact memory
* Conversation memory

Purpose:

Create continuity across interactions and reduce stateless chatbot behavior.

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

Improve memory precision, reduce low-value memory storage, prioritize meaningful user information, and retrieve the most relevant context during conversations.

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

* Observer / Gremlin / Treasure progression
* Relationship decay
* Re-engagement awareness

Purpose:

Allow the character to react differently depending on relationship history instead of treating every interaction equally.

---

### Response Mode Engine

Modes include:

* normal_chat
* philosophy_chat
* comfort_choice
* memory_callback
* reward_event

Purpose:

Improve emotional pacing and maintain personality consistency across different contexts.

---

### Reward System

Features:

* Point accumulation
* Variable rewards
* Inventory system
* Reward redemption

Purpose:

Introduce progression loops and create lightweight rituals between the user and the character.

---

### Autonomous Layer

Features:

* Relationship checkpoints
* Reward suggestions
* Memory prompts
* Cooldown protection

Purpose:

Allow the character to occasionally initiate interaction rather than remaining fully reactive.

---

### Event Logging

Features:

* Supabase event storage
* n8n webhook integration
* Structured event payloads

Purpose:

Create an automation-ready backend for future CRM, analytics, loyalty, and workflow systems.

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

Provide a dedicated strategic reasoning layer separate from the core character experience.

Rather than acting as a traditional chatbot, this layer is designed to help users evaluate decisions, challenge assumptions, and improve decision quality through structured reasoning.

---

## Technical Stack

Frontend

* React
* Vite

Backend

* FastAPI

AI

* Google Gemini API

Database

* Supabase

Workflow Automation

* n8n

Languages

* Python
* TypeScript

Development Environment

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
* Deployment-Ready Architecture

The architecture is designed to support future AI products, including companion systems, tutoring systems, strategic reflection agents, and multi-agent experiences.

The architecture is designed to support future AI products, including companion systems, tutoring systems, strategic reflection agents, and multi-agent experiences.
---
## Development Milestones

### Phase 1 Completed

* Character framework
* Memory persistence
* Relationship engine
* Planner system
* Response routing
* Reward shop
* Redemption system
* Event logging
* Autonomous behavior layer
* Supabase integration
* Smoke testing

---

## Character AI Roadmap

### Phase 2

Adaptive Personality System

Goals:

* Personality state machine
* Behavioral adaptation
* User-specific interaction styles
* Stronger character consistency

---

### Phase 3

Relationship Progression System

Goals:

* Multiple familiarity levels
* Dynamic interaction frequency
* Loyalty progression
* Personalized interaction paths

---

### Phase 4

Lore-Aware Character Memory

Goals:

* Worldbuilding integration
* Character history memory
* Story-aware interactions
* Narrative progression systems

---

### Phase 5

AI Character Platform

Goals:

* Multi-user architecture
* Authentication
* CRM integration
* Loyalty integration
* Commerce integration
* Character ecosystem

---

## Character Runtime Architecture

The current version of i nik uses a persistent runtime character architecture.

Core runtime systems:

* Conversation Persistence
* User Fact Extraction
* Relationship State Engine
* Profile State Tracking
* Supabase Memory Gateway
* Runtime State API
* Lore Bible System
* Character Identity Protection
* Reward and Inventory Systems

These systems allow the character to maintain continuity across refreshes and future sessions while preserving character consistency.

---

## Why This Project Matters

Most AI projects stop at conversation.

i nik explores whether AI characters can create meaningful long-term engagement through memory, familiarity, progression systems, behavioral design, and relationship building.

The project combines:

* AI Engineering
* Behavioral Psychology
* Memory Architecture
* Relationship Design
* Gamification Systems
* Workflow Automation
* Character Design
* Applied Product Thinking

Rather than building another chatbot, the project investigates how AI characters may become a new category of digital products.

The long-term vision is a persistent character capable of existing across conversations, communities, games, loyalty systems, and real-world experiences.

---

## Recent Milestone

A major milestone was completed by moving i nik from a partially mock-driven prototype into a persistent runtime character system.

Completed:

* Persistent conversation history
* Runtime relationship state persistence
* Supabase-backed user state
* Dynamic Profile page
* Dynamic Journey page
* Runtime Memory Shelf
* Fact extraction improvements
* Lore Bible V2 integration
* Identity protection rules
* Hidden lore-triggered dialogue events

Verified through end-to-end testing:

* Refresh persistence
* State persistence
* Memory recall
* Runtime API state loading
* Character consistency
* Lore identity locking
