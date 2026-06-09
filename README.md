# i nik — AI Character Interaction System

i nik is an AI character interaction system designed as a behavioral character prototype for a beverage shop.

Instead of functioning as a traditional assistant, i nik is designed as a character that gradually develops familiarity with users through conversation, memory, relationship signals, reward mechanics, redemption behavior, and backend event logging.

This project demonstrates how an AI character can combine personality consistency, long-term memory, gamification, workflow automation, and applied AI product design.

---

## Live Demo

[Talk to i nik](https://inik-ai-prototype-kqelfbrxvnbk3xtygziygn.streamlit.app/)

---

## Project Goal

The objective of this project is to explore how AI characters can create stronger long-term user engagement through:

* Personality progression
* Memory systems
* Relationship modeling
* Response mode control
* Gamification loops
* Reward redemption
* Backend event logging
* Behavioral prompting
* Developer reliability tools

This project is built as a portfolio piece for AI Agent Development, Applied AI Product Design, and AI Workflow Automation.

---

## Core Features

### Behavioral Stage System

i nik changes its behavior according to an Intimacy Score.

Stages:

#### Observer

* Curious
* Polite
* Observant
* Asks questions
* Learning about the user

#### Gremlin

* More playful
* Teasing
* Uses inside jokes
* References previous conversations

#### Treasure

* Warm
* Familiar
* Emotionally attentive
* Values shared memories

---

### Response Mode Engine

i nik does not respond through stage alone. The system also detects the current interaction mode based on the user's message.

Response modes include:

* `normal_chat`
* `comfort_choice`
* `philosophy_chat`
* `memory_callback`
* `reward_event`

Purpose:

* Prevents generic responses
* Improves emotional pacing
* Allows the character to respond differently to emotional, philosophical, memory-related, and reward-related messages
* Keeps personality behavior more stable across different conversation contexts

---

### Memory System

The project contains multiple memory layers.

#### Recent Chat Memory

Stores recent conversation history and injects it into prompts.

Purpose:

* Context continuity
* Less repetitive conversations
* More natural follow-up responses

#### Fact Memory

Stores simple user facts extracted from conversation.

Examples:

* Name
* Preferences
* Interests

Purpose:

* Personalized interactions
* Character consistency
* Direct recall of important user information

#### User Profile Memory

Tracks broader user interaction patterns.

Stored data includes:

* Recent mood
* Conversation style
* Recurring topics
* Memorable events
* Total user messages
* Total visits
* Last interaction date
* Redemption history

Purpose:

* Long-term interaction continuity
* More meaningful personalization
* Better behavioral context for the AI character

#### Supabase Database Memory

The current version uses Supabase as the primary memory persistence layer.

Saved data includes:

* User facts
* User profile
* Intimacy score
* Points
* Relationship state
* Reward inventory
* Redemption history

Purpose:

* Prevents important prototype state from resetting
* Moves memory beyond local JSON storage
* Supports a more production-ready memory architecture
* Demonstrates a realistic path toward multi-user persistence

#### JSON Fallback Backup

The system also keeps JSON persistence as a backup layer.

Purpose:

* Local backup during development
* Debugging support
* Safer fallback if Supabase connection fails

---

### Relationship Engine

The system tracks three relationship dimensions.

#### Trust

How much personal or emotional information the user shares.

#### Familiarity

How often the user interacts with i nik.

#### Curiosity

How strongly the system responds to meaningful, unusual, or philosophical user input.

These values are exposed in the UI and injected into prompts to guide response behavior.

---

### Gamification System

The chatbot contains a lightweight reward loop.

Features:

* Point accumulation
* Variable rewards
* Inventory system
* Reward redemption

Examples of collectible items:

* Blue Star
* Forest Tea Leaf
* Ancient Note

Purpose:

* Retention
* Curiosity
* Progression
* Small ritual-building between the user and the character

---

### Reward Redemption v1

The system allows users to redeem items from their inventory.

Flow:

```text
Inventory item exists
↓
User clicks Redeem First Item
↓
Item is removed from Inventory
↓
Redemption record is stored in user profile
↓
Memory is saved to Supabase
↓
reward_redeemed event is sent to n8n
```

Purpose:

* Turns rewards from symbolic collectibles into actionable interaction events
* Demonstrates a path toward coupon, loyalty, or CRM integration
* Creates a working bridge between gamification and backend workflow automation

---

### Analytics Dashboard

The Streamlit sidebar includes lightweight analytics for the current user state.

Tracked metrics include:

* Engagement score
* Total messages
* Memory fact count
* Inventory item count
* Relationship values
* User profile activity

Purpose:

* Makes system state visible
* Supports debugging
* Shows how user engagement can be measured inside an AI character system

---

### Developer Tools

The system includes several developer-focused reliability tools.

#### Dev Test Mode

Allows the system to be tested without calling the Gemini API.

Purpose:

* Saves API quota
* Allows memory, reward, response mode, analytics, and backend event testing without relying on LLM availability

#### Data Control Panel

Allows memory state to be controlled from the UI.

Features:

* Download memory JSON
* Reset chat only
* Reset all memory

Purpose:

* Faster testing
* Safer debugging
* Easier state control during development

#### Quota Fallback

If Gemini quota is unavailable or the API fails, the system returns a fallback response instead of breaking.

Purpose:

* Prevents raw API errors from appearing to users
* Keeps the app usable during quota limits
* Preserves memory and state even when the LLM call fails

#### Health Check

Checks whether required system state exists.

Health check covers:

* Session state
* User facts
* User profile
* Relationship state
* Inventory
* Response mode
* Required profile fields

Purpose:

* Fast stability verification
* Easier debugging
* Safer final testing before deployment

---

## Backend Workflow Automation

The project uses n8n for backend event logging.

Logged events include:

* `user_message`
* `reward_redeemed`

Each event includes:

* Event type
* Timestamp
* User ID
* Current state
* Relationship values
* User profile summary
* Inventory count
* Extra event-specific data

Purpose:

* Demonstrates workflow automation beyond the chatbot UI
* Creates an automation-ready backend layer
* Supports future CRM, reward fulfillment, coupon generation, or analytics workflows

---

## Tech Stack

Frontend:

* Streamlit

AI:

* Google Gemini API

Database:

* Supabase

Backend Workflow Automation:

* n8n

Language:

* Python

Version Control:

* Git
* GitHub

Deployment:

* Streamlit Community Cloud

Development Environment:

* GitHub Codespaces

Persistence:

* Supabase database memory
* JSON fallback backup

---

## Project Structure

```text
app.py
Main Streamlit application

behavior.py
Behavior stage logic

character.py
Character Bible and personality rules

memory.py
Recent chat memory builder

facts.py
Fact extraction and direct memory recall

relationship.py
Trust / Familiarity / Curiosity engine

modes.py
Response mode detection and mode descriptions

profile.py
User profile memory and activity tracking

rewards.py
Variable reward system

redemption.py
Reward redemption logic

analytics.py
Engagement and system analytics

persistent_memory.py
JSON fallback memory persistence

supabase_memory.py
Supabase database adapter

memory_gateway.py
Supabase primary memory layer with JSON fallback

event_logger.py
n8n event logging sender

state_tools.py
Data export and reset tools

fallback.py
Gemini quota and API fallback handling

health.py
System health check

TESTING.md
Final test matrix

README.md
Project documentation
```

---

## System Architecture

```text
User
 ↓
Streamlit Frontend
 ↓
Session State Layer
 ├── Chat Messages
 ├── Intimacy Score
 ├── Points
 ├── User Facts
 ├── User Profile
 ├── Relationship State
 ├── Inventory
 ├── Redemption State
 └── Response Mode
 ↓
Behavior Engine
 ├── Stage Detection
 └── Observer / Gremlin / Treasure Progression
 ↓
Response Mode Engine
 ├── normal_chat
 ├── comfort_choice
 ├── philosophy_chat
 ├── memory_callback
 └── reward_event
 ↓
Memory System
 ├── Recent Chat Memory
 ├── Fact Memory
 ├── Direct Name Recall
 ├── User Profile Memory
 ├── Supabase Database Memory
 └── JSON Fallback Backup
 ↓
Relationship Engine
 ├── Trust
 ├── Familiarity
 └── Curiosity
 ↓
Prompt Assembly
 ├── Character Bible
 ├── Stage Rules
 ├── Relationship State
 ├── Response Mode
 ├── Recent Chat History
 ├── User Facts
 └── User Profile
 ↓
Gemini API / Dev Test Mode
 ↓
AI Response
 ↓
Reward System
 ├── Points
 ├── Variable Reward
 ├── Inventory Update
 └── Reward Redemption
 ↓
Persistence Layer
 ├── Supabase Save
 └── JSON Backup
 ↓
Backend Workflow
 ├── n8n user_message event
 └── n8n reward_redeemed event
 ↓
Reliability Layer
 ├── Quota Fallback
 ├── Data Control Panel
 └── Health Check
```

---

## Implemented Features

* Streamlit chatbot UI
* Gemini API integration
* Character Bible
* Behavioral stage progression
* Intimacy score system
* Recent chat memory
* Fact memory
* Direct name recall
* User profile memory
* Supabase database persistence
* JSON fallback backup
* Relationship engine
* Response mode engine
* Points system
* Variable reward system
* Reward inventory
* Reward redemption v1
* Engagement analytics
* n8n event logging
* Dev Test Mode
* Data Control Panel
* Quota fallback handling
* Health Check
* GitHub deployment
* Streamlit Cloud deployment
* Final end-to-end stability testing

---

## Testing

Core system tests are documented in:

[TESTING.md](TESTING.md)

The final end-to-end test covered:

* Character response
* Fact memory
* Name recall
* Supabase memory persistence
* Refresh persistence
* Relationship engine
* Response mode detection
* Stage progression
* Reward generation
* Inventory update
* Reward redemption
* n8n event logging
* Dev Test Mode
* Data Control Panel
* Quota fallback
* Health Check

---

## Key Passed Tests

* i nik can remember the user's name through direct fact recall
* User state persists through Supabase after refresh
* Intimacy, Points, Relationship metrics, and User Profile remain stable
* Response Mode changes correctly based on user message type
* Rewards are added to Inventory
* Redeemed items are removed from Inventory and recorded in redemption history
* n8n receives `user_message` events
* n8n receives `reward_redeemed` events
* Dev Test Mode allows testing without using Gemini quota
* Health Check confirms required session state and profile fields
* Data Control Panel can reset chat or full memory state

---

## Current Limitations

The current system is strong for a single-user applied AI prototype, but it is not yet a full multi-user production app.

Known limitations:

* The current version uses a fixed `demo_user` identity
* No authentication layer yet
* Relationship scoring is rule-based
* Fact extraction is pattern-based
* Reward redemption is symbolic and not connected to a real POS or coupon system yet
* n8n currently logs events but does not yet trigger CRM, coupon generation, or business actions
* The system is designed for prototype-scale testing, not high-traffic production use

---

## Technical Debt and Scaling Plan

This project intentionally separates prototype decisions from production requirements.

### Current Architecture Decisions

Supabase was added as the primary persistence layer because:

* It provides hosted database memory
* It supports structured user state storage
* It is easier to inspect and debug than a full custom backend
* It allows the prototype to move beyond local JSON memory
* It creates a clear path toward multi-user memory architecture

JSON persistence remains as a fallback because:

* It is useful during development
* It provides backup state during database issues
* It makes debugging easier

n8n was added for backend event logging because:

* It supports workflow automation without building a full backend first
* It can receive app events through webhooks
* It creates a path toward CRM, reward fulfillment, and business automation workflows

### Remaining Technical Debt

* No authentication or user-specific account system yet
* No production Row Level Security policy design yet
* No real coupon or POS integration yet
* No business analytics dashboard yet
* No multi-user memory separation yet
* No FastAPI backend layer yet

### Scaling Plan

If this prototype were expanded for real users, the architecture would be upgraded in phases.

#### Phase 1 — User Identity and Auth

Add user authentication and separate memory per user.

Possible options:

* Supabase Auth
* Streamlit authentication layer
* External identity provider

#### Phase 2 — Production Database Rules

Strengthen database security and access patterns.

Possible upgrades:

* Row Level Security policies
* User-specific memory rows
* Event history tables
* Reward redemption tables
* Audit logging

#### Phase 3 — Backend Workflow Automation

Expand n8n workflows for business operations.

Possible workflows:

* CRM logging
* Google Sheets logging
* Coupon generation
* Reward fulfillment
* Notification workflows
* Menu recommendation workflows
* Campaign automation

#### Phase 4 — Agent Logic Layer

Use Flowise or LangChain only if tool routing becomes necessary.

Possible use cases:

* Tool routing
* Retrieval routing
* Menu recommendation agents
* Reward decision agents
* Multi-step workflows

#### Phase 5 — Production Architecture

A production version could use:

* Streamlit or React frontend
* FastAPI backend
* Supabase or PostgreSQL database
* Redis caching
* n8n workflow automation
* LLM API layer
* Monitoring and analytics dashboard

---

## Future Roadmap

### Short-Term

* Improve fact extraction
* Add more structured preference tracking
* Add richer reward types
* Improve response mode classification

### Mid-Term

* Add user authentication
* Separate memory by user
* Add event history table
* Add reward redemption table
* Expand n8n workflow actions

### Long-Term

* Real coupon or POS integration
* CRM integration
* Advanced behavioral analytics
* Flowise or LangChain agent routing if needed
* Multi-user production deployment

---

## Why This Project Matters

Most chatbot projects stop at question-answer interactions.

i nik explores a different direction: building an AI character system that remembers, develops familiarity, creates small rituals, supports reward behavior, logs backend events, and maintains long-term engagement through behavioral design.

The project combines:

* Prompt Engineering
* Behavioral Design
* Memory Systems
* Relationship Modeling
* Gamification
* Workflow Automation
* Applied AI Product Design

This makes the project closer to an applied AI character system than a basic chatbot interface.
