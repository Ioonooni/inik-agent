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

## Technical Stack

Frontend

* Streamlit

AI

* Google Gemini API

Database

* Supabase

Workflow Automation

* n8n

Language

* Python

Deployment

* Streamlit Community Cloud

Development Environment

* GitHub Codespaces

Version Control

* Git
* GitHub

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

## Current Status

Prototype Status: Stable

Completed:

* Planner
* Tool Routing
* Memory V2
* Supabase Memory
* Autonomous Layer V1
* Reward Shop
* Redemption System
* Event Logging
* n8n Integration
* Smoke Test Suite

Repository State:

* All major Phase 1 milestones completed
* Smoke checks passing
* Git status clean

Current Focus:

Phase 2B — Dynamic Personality Evolution

Recently Completed:

* Adaptive Personality Matrix
* User Archetype Detection
* Shared Memory Prompting
* Relationship Decay
* Re-engagement Context
* Stronger stage-dependent behavior
