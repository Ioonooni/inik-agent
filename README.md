# i nik

## Memory-Driven Conversational AI with Shared-Context Routing

i nik is a full-stack conversational AI application designed around persistent memory, user context, relationship state, and routing between two specialized response modes.

The system supports:

* **i nik — Heart Mode:** memory continuity, familiarity, emotional context, and relationship-aware responses
* **Rick Royce — Mind Mode:** strategic reasoning, trade-off analysis, risk assessment, and decision support

Both modes use the same user identity, facts, profile, relationship state, conversation history, and retrieved memory context.

This project uses shared-context response routing. It is not an autonomous multi-agent orchestration system: the modes do not independently delegate tasks, communicate through planner–executor loops, or operate autonomous tool-use cycles.

---

## Project Delivery

**Timeline:** 9 June 2026 – 24 June 2026
**Delivery Duration:** 16 days
**Role:** Applied AI Developer / Full-Stack AI Product Builder

### Delivery Scope

* Conversational AI product design
* React and TypeScript frontend
* FastAPI backend and REST APIs
* Persistent memory architecture
* Shared-context response routing
* Supabase persistence
* Local JSON fallback
* Relationship-state logic
* Structured fact extraction
* Regression testing
* Production deployment
* Technical documentation

---

## Live Links

**Live Demo**
https://inik-cafe.vercel.app

**Backend API**
https://inik-agent.onrender.com

**Backend Repository**
https://github.com/Ioonooni/inik-agent

**Frontend Repository**
https://github.com/Ioonooni/inik-cafe

> Gemini free-tier requests may temporarily return HTTP 429 when the external request quota is exhausted. This is a model-provider limitation rather than a failure of the memory, routing, persistence, or API layers.

---

## Problem

Many conversational AI applications rely primarily on the current prompt or recent chat history.

This can lead to:

* Loss of user context between sessions
* Repeated introductions
* Inconsistent personalization
* Generic emotional responses
* Weak long-term continuity
* Strategic and emotional requests being handled with the same response style

i nik explores whether a conversational system can provide more consistent long-term interaction by combining:

* Persistent memory
* Structured user facts
* Profile signals
* Relationship variables
* Retrieval-based context
* Specialized response modes
* Shared user state

---

## What the System Does

### Persistent User Context

The platform stores and retrieves:

* Conversation memories
* Structured user facts
* User profile signals
* Relationship state
* Recent messages
* Long-term memory records

### Specialized Response Routing

The router selects between:

* Heart Mode
* Mind Mode
* Hybrid Mode

Heart Mode is intended for personal continuity, emotional context, and relationship-aware conversation.

Mind Mode is intended for strategic questions involving:

* Decisions
* Trade-offs
* Opportunity costs
* Risk assessment
* Career planning
* Project planning

Hybrid Mode can combine both perspectives when the request requires personal context and structured reasoning.

### Shared Cognitive Context

All response paths receive the same underlying user context:

* Stable user identity
* Structured facts
* Profile state
* Relationship state
* Recent interaction history
* Retrieved long-term memory

The behavioral response mode changes, but the user state remains shared.

### Structured Fact Recall

Supported user facts can be answered through deterministic recall rather than requiring every response to depend on generative inference.

Examples include:

* Name
* Favorite color
* Interests
* Pet name
* Other supported profile facts

This allows known facts to remain available even when the external model quota is unavailable.

---

## Architecture

```text
User Input
    ↓
React + TypeScript Frontend
    ↓
FastAPI Backend
    ↓
Stable User Identity
    ↓
Response Router
    ├── i nik / Heart Mode
    ├── Rick Royce / Mind Mode
    └── Hybrid Mode
    ↓
Shared Cognitive Context
    ├── User Facts
    ├── User Profile
    ├── Relationship State
    ├── Recent Messages
    └── Retrieved Memories
    ↓
Prompt Construction
    ↓
Google Gemini API
    ↓
Response Generation
    ↓
State and Memory Persistence
    ├── Supabase
    └── Local JSON Fallback
    ↓
Frontend Rendering
```

Additional structured events can be stored in Supabase or sent to n8n through webhook integration.

---

## Memory Architecture

### Memory Sources

The memory layer supports:

* Structured user facts
* Recent conversation history
* Long-term conversation memories
* User profile information
* Relationship-state context
* Query-matched retrieval
* Time-ordered recent retrieval

### Memory Quality Scoring

Incoming memory candidates are evaluated before storage.

The system assigns different importance levels to categories such as:

* Name
* Preferences
* Possessions
* Study
* Projects
* Location
* Emotional context

The objective is to reduce low-value memory storage rather than treating every message as equally important.

### Reinforcement

Recurring facts can receive hit-count reinforcement.

Repeated information can become more significant within a capped scoring range.

### Time-Based Decay

Memory importance can decrease over time according to memory type.

High-value or frequently reinforced memories decay more slowly than low-value conversational details.

### Conflict Detection

The system checks supported fact categories for conflicts, including:

* Name
* Preference
* Dislike
* Study
* Project
* Location
* Possession

### Soft Superseding

When a newer memory conflicts with an older record, the older record can be marked as superseded rather than deleted.

This preserves historical traceability while lowering the older record’s retrieval priority.

### Lifecycle Filtering

Runtime retrieval excludes records that are:

* Archived
* Superseded
* Classified as low-value lifecycle candidates

Legacy memory records without newer lifecycle metadata remain eligible for retrieval for backward compatibility.

### Ranking

Memory candidates can be ranked using a combination of:

* Importance
* Query relevance
* Recency
* Reinforcement
* Supersede status
* Lifecycle status

The highest-ranked active records are selected for prompt context.

---

## Key Architecture Decisions

### Separate Behavior from User State

Heart and Mind modes have different behavioral instructions but share the same user context.

This avoids duplicating:

* Memory storage
* User profiles
* Relationship logic
* Retrieval infrastructure
* Stable identity

### Use Routing Instead of Autonomous Multi-Agent Orchestration

The current platform uses bounded response-mode routing.

It does not include:

* Inter-agent communication
* Autonomous delegation
* Planner–executor loops
* Independent tool-use agents
* Recursive agent collaboration

This choice reduces:

* Model-call cost
* Response latency
* Loop risk
* State-management complexity
* Debugging difficulty

### Keep Structured Recall Separate from Generation

Known user facts can be recalled directly.

This reduces unnecessary model calls and improves predictability for deterministic memory questions.

### Preserve Conflicting History

Conflicting records are soft-superseded instead of permanently deleted.

This provides safer historical tracking and reduces destructive overwrites.

### Use Supabase with Local Fallback

Supabase is the primary persistence layer.

A local JSON path provides fallback behavior during development or when remote storage is unavailable.

This is a prototype resilience mechanism, not a complete production disaster-recovery strategy.

---

## Relationship and Behavioral State

The system tracks rule-guided relationship variables such as:

* Trust
* Familiarity
* Curiosity
* Attachment
* Relationship score
* Relationship stage

Current stages include:

* Observer
* Gremlin
* Treasure

The user profile can also contain behavioral signals such as:

* Warmth
* Playfulness
* Curiosity
* Directness
* Formality
* Initiative
* Memory-callback tendency
* Conversation style
* Recurring topics
* Topic affinity

These values guide response construction.

They are product interaction variables, not validated psychological measurements.

---

## Event Logging

The backend includes infrastructure for structured events such as:

* User messages
* Memory-related events
* Relationship changes
* Reward events
* Redemption events

Events can be:

* Stored in Supabase
* Sent to an n8n webhook
* Used as a foundation for analytics or workflow automation

Potential future uses include:

* Product analytics
* CRM workflows
* Notifications
* Loyalty systems
* Reward fulfillment

---

## API Examples

### Health Check

```bash
curl https://inik-agent.onrender.com/health
```

Example response:

```json
{
  "ok": true,
  "service": "i nik agent api",
  "gemini_configured": true
}
```

### Send a Message

```bash
curl -X POST https://inik-agent.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "message": "ช่วยวิเคราะห์ข้อดีข้อเสียของทางเลือกนี้",
    "agent_mode": "auto"
  }'
```

### Retrieve User State

```bash
curl "https://inik-agent.onrender.com/api/state?user_id=demo_user"
```

The returned state may include:

* User facts
* User profile
* Relationship variables
* Recent messages
* Active response mode
* Runtime metadata

---

## Local Development

The frontend and backend are maintained in separate repositories.

### Backend

```bash
git clone https://github.com/Ioonooni/inik-agent.git
cd inik-agent

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
uvicorn inik_api:app --reload
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn inik_api:app --reload
```

Backend development URL:

```text
http://localhost:8000
```

### Frontend

```bash
git clone https://github.com/Ioonooni/inik-cafe.git
cd inik-cafe

npm install
npm run dev
```

Optional frontend environment variable:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The production fallback API is:

```text
https://inik-agent.onrender.com
```

---

## Environment Variables

Create a local `.env` file for backend configuration.

Typical values include:

```env
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Do not commit live API keys, database credentials, or production secrets.

---

## Testing

The repository includes checks covering:

* Memory scoring
* Memory reinforcement
* Memory decay
* Conflict detection
* Memory ranking
* Lifecycle filtering
* Structured fact extraction
* Direct fact recall
* Response routing
* Shared-context construction
* Persistence paths
* API integration
* Runtime behavior

### Latest Regression Result

* **109 checks passed**
* **0 checks failed**

### Production Verification

Production checks also confirmed:

* FastAPI health endpoint
* React/Vite production build
* Production API base configuration
* CORS configuration
* Frontend-to-backend connectivity
* Structured fact persistence
* Direct fact recall
* Memory lifecycle runtime integration
* Shared-context response paths
* Render backend deployment
* Vercel frontend deployment
* Clean and synchronized repositories

The test count shows that the implemented test conditions passed.

It does not measure:

* Retrieval precision
* Hallucination rate
* False-memory rate
* Conversational quality
* Production-scale reliability
* Security
* Latency
* Token cost
* User engagement

---

## Example Regression

Production verification identified a Thai fact-extraction bug.

The sentence:

```text
สีโปรดของฉันคือสีม่วง
```

was incorrectly matched by a broad name pattern and stored as:

```json
{
  "name": "สีม่วง"
}
```

The extraction logic was corrected so the system stores:

```json
{
  "favorite_color": "สีม่วง"
}
```

without overwriting the user’s name.

The fix was:

1. Reproduced locally
2. Covered by a targeted regression test
3. Checked against the broader response pipeline
4. Deployed
5. Verified again in production

---

## Technical Review Process

At the end of V1, I conducted a staged, context-limited technical review to reduce self-confirmation bias.

Instead of initially presenting the project as my own work, I evaluated it from the perspective of a company reviewing an internship candidate.

Project details were introduced gradually so the architecture and implementation could be assessed before personal context influenced the review.

The review identified issues including:

* Technical debt
* Incomplete runtime integration
* Weak persistence paths
* Deployment risk
* Overstated architecture terminology
* Missing production verification

The findings were treated as an adversarial checklist rather than ground truth.

Each issue was verified against:

* Source code
* Runtime behavior
* Tests
* API responses
* Deployment output
* Repository state

The remediation process influenced:

* Memory lifecycle runtime integration
* Structured fact-recall fixes
* Production verification
* Frontend/backend synchronization
* Repository cleanup
* More precise architecture terminology

---

## Milestones

| Version | Main Delivery                                                                                        |
| ------- | ---------------------------------------------------------------------------------------------------- |
| V1      | Persistent memory, relationship state, rewards, event logging, Supabase integration                  |
| V2      | Memory scoring, reinforcement, decay, conflict handling, ranking, shared context, routing foundation |
| V3      | Runtime lifecycle integration, regression fixes, production verification, deployment cleanup         |

---

## Current Limitations

* The relationship and behavioral variables are rule-guided.
* The system is not an autonomous multi-agent architecture.
* There is no independent inter-agent communication.
* There is no planner–executor delegation loop.
* There are no autonomous tool-use agents.
* Authentication is not yet a complete production user flow.
* Production Row Level Security has not been formally audited.
* Cross-user data isolation has not been independently security-tested.
* User-facing data export and deletion workflows are not implemented.
* Prompt-injection resistance for stored memory has not been formally evaluated.
* Retrieval precision has not been benchmarked.
* False-memory and hallucination rates have not been measured.
* Latency and token cost have not been formally reported.
* Production-scale load testing has not been performed.
* Observability and automated error monitoring remain limited.
* Rate limiting is not implemented as a complete production control layer.
* Schema migration and versioning require further work.
* Gemini requests depend on external API availability and quota.

---

## Evaluation Still Needed

Future evaluation should measure:

* Retrieval precision
* Retrieval hit rate
* False-memory rate
* Conflict-resolution accuracy
* Fact-extraction accuracy
* Routing accuracy
* Persistence reliability
* Long-context behavioral consistency
* End-to-end latency
* Token consumption
* Cost per conversation
* Cross-user data isolation

These metrics are not currently claimed.

---

## Possible Next Steps

Potential future work includes:

* Complete authentication flow
* Row Level Security policies
* Formal retrieval evaluation dataset
* Prompt-injection testing
* User data export and deletion
* Automated deployment monitoring
* Error and latency observability
* Model-provider fallback
* Semantic retrieval
* Rate limiting
* Schema migration tooling
* Production load testing
* A bounded coordinator–planner–reviewer flow for strategic tasks

A future multi-agent implementation would require explicit:

* Agent state
* Delegation rules
* Inter-agent messaging
* Tool permissions
* Stopping conditions
* Retry limits
* Loop protection
* Cost controls
* Observability
* Evaluation against the current routed architecture

---

## Technical Stack

### Frontend

* React
* TypeScript
* Vite

### Backend

* Python
* FastAPI
* REST APIs

### AI

* Google Gemini API
* Behavioral prompt construction
* Shared cognitive context
* Agent-style response routing

### Data and Memory

* Supabase
* Structured user facts
* RAG-based retrieval
* JSON fallback

### Automation

* n8n
* Webhook integration
* Structured event payloads

### Deployment

* Render
* Vercel
* GitHub
* GitHub Codespaces

---

## Important Backend Components

```text
inik_api.py             FastAPI application and API routes
facts.py                Structured fact extraction and recall
memory_gateway_v2.py    Supabase and local memory gateway
memory_lifecycle.py     Archive and lifecycle rules
memory_ranking.py       Memory ranking logic
rag_memory.py           Memory retrieval paths
rag_prompt.py           Shared-context construction
relationship.py         Relationship-state logic
event_logger.py         Event and webhook integration
```

---

## What This Project Demonstrates

This project demonstrates practical experience in:

* Applied AI product development
* Conversational AI architecture
* Persistent memory systems
* RAG-based retrieval
* Structured fact extraction
* Shared-context routing
* Behavioral system design
* FastAPI backend development
* React and TypeScript frontend development
* Supabase persistence
* Workflow automation
* Regression testing
* Production debugging
* Deployment verification
* Technical debt remediation
* Engineering documentation

The project focuses on application architecture, behavioral systems, product integration, and runtime reliability.

It does not claim expertise in model training, machine-learning research, or distributed AI infrastructure.
