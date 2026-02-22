# CoatiAssistant -- Project Summary

## 📦 Repository Overview

GitHub: https://github.com/Lord-Juice/CoatiAssistant

The project is structured as a multi-service Docker-based assistant
system written primarily in Python.\
It is designed to evolve in phases into a fully capable AI assistant
running locally 24/7.

------------------------------------------------------------------------

## ✅ What Already Exists

### 1️⃣ Agent Core (CLI Chat Interface)

**Status: ✅ Fully Functional**

-   Interactive CLI chat interface powered by local LLM (Ollama)
-   Built with LangChain agents framework
-   Rich terminal UI with live tool execution feedback
-   Modular tool system with multiple categories

**Available Tools:**

📅 **Calendar Tools**
-   `calendar_list_events` - List events in date range
-   `calendar_create_event` - Create new calendar entries
-   Mock calendar data (ready for service integration)

🕐 **Date/Time Tools**
-   `get_current_datetime` - Current ISO datetime
-   `get_current_weekday` - Current weekday name
-   `add_days_to_now` - Calculate future dates
-   `get_today_range` - Today's start/end timestamps
-   `get_tomorrow_range` - Tomorrow's start/end timestamps

💾 **Memory Tools**
-   `remember` - Store structured facts with entity/slot system
-   `recall` - Retrieve stored information
-   JSON-based persistent storage (`data/memory.json`)
-   Canonicalized entity names for consistent recall

🔢 **Math Tools**
-   `calculate` - Safe expression evaluation
-   `random_number` - Generate random integers
-   `generate_uuid` - Create unique identifiers

💬 **Discord Tools**
-   `discord_send_message` - Send messages (stub, ready for service integration)

🖥️ **System Tools**
-   `get_system_info` - Platform and system information
-   `read_text_file` - Read file contents

**Key Features:**
-   Intelligent tool chaining (automatically gathers missing arguments)
-   Never guesses time-sensitive or deterministic values
-   Conversational interface with memory persistence
-   Designed to prevent infinite loops and guess-based responses

**Tech Stack:**
-   LangChain + ChatOllama
-   Rich UI library
-   Python 3.14+

### 2️⃣ Discord Connector (Read-Only Listener)

-   A working Discord bot connects successfully to the Discord Gateway.
-   The bot **never sends messages** (loop-safe by design).
-   It listens to forwarded messages in a strict 4-line format:

```{=html}
<!-- -->
```
    <@UserID> or @Username
    Channel
    Server
    Message content...

-   Messages are parsed and converted into structured JSON events:

``` json
{
  "event_type": "discord.message_received",
  "source": "discord_service",
  "timestamp": "...",
  "data": {
    "is_dm": true,
    "author_username": "...",
    "author_id": "...",
    "channel_name": "DM",
    "channel_id": "...",
    "guild_name": null,
    "guild_id": null,
    "content": "..."
  }
}
```

-   Events are printed as clean one-line JSON to stdout.
-   Robust parsing supports:
    -   `@Username`
    -   `<@123456>`
    -   `<@!123456>`
-   Defensive error handling prevents crashes.

Current Role: The Discord service acts as a **read-only event emitter**.

------------------------------------------------------------------------

## 🚀 Quick Start

### Running Agent Core CLI

**Prerequisites:**
- Python 3.14+
- Ollama installed and running locally
- Required Python packages: `langchain`, `langchain-ollama`, `rich`

**Steps:**
```bash
cd services/agent_core
pip install -r requirements.txt
python app/cli_chat.py
```

The CLI provides:
- Interactive chat with local LLM
- Automatic tool usage for deterministic operations
- Memory persistence across sessions
- Rich terminal UI with live feedback

**Example interactions:**
- "What's 234 * 567?"
- "What day is it today?"
- "Remember that my dog's name is Max"
- "What is my dog's name?"
- "What's on my calendar today?"

### Running Discord Connector

**Prerequisites:**
- Discord bot token configured
- Python dependencies installed

**Steps:**
```bash
cd services/discord_connector
pip install -r requirements.txt
python app/bot.py
```

------------------------------------------------------------------------

## 🎯 Project Goals

------------------------------------------------------------------------

## Phase 1 -- Core Foundation (In Progress)

✅ Discord listener - **Complete**\
✅ Message parsing and structured JSON output - **Complete**\
✅ Agent Core CLI with tool system - **Complete**\
✅ Memory persistence (JSON-based) - **Complete**\
✅ Date/time, math, calendar, and system tools - **Complete**\
❌ Event forwarding from Discord to Agent Core (HTTP or message bus)\
❌ Agent Core HTTP API endpoint

**Next Steps:**
1. Create Agent Core REST API (`POST /events`, `POST /chat`)
2. Forward Discord JSON events to Agent Core endpoint
3. Connect calendar tools to actual Calendar Service
4. Connect Discord send tool to Discord Connector
5. Implement inter-service communication (HTTP or Redis pub/sub)

------------------------------------------------------------------------

## Phase 2 -- Intelligence & Persistence

### 🧠 Agent Core

**Status: ✅ CLI Complete | ❌ Service Mode Pending**

-   ✅ Central decision engine with LangChain agents
-   ✅ Tool-based architecture (15+ tools)
-   ✅ Memory system with structured fact storage
-   ✅ Interactive CLI interface
-   ❌ HTTP REST API for event ingestion
-   ❌ Service-to-service routing
-   ❌ Policies & permissions layer

**Needed:**
-   REST API wrapper around CLI agent
-   Service integration layer
-   Authentication/authorization

### 🗓 Calendar Service

**Status: ❌ Mock Data Only**

-   ❌ REST API:
    -   `GET /events?from=...&to=...`
    -   `POST /events`
-   ❌ Polling or event push for upcoming events
-   ❌ Emits structured calendar events

**Note:** Agent Core has calendar tool stubs ready for integration

### 💾 Memory / Database

**Status: ✅ Basic Implementation**

-   ✅ Persistent storage for facts and knowledge
-   ✅ JSON-based storage (`data/memory.json`)
-   ✅ Entity canonicalization for consistent recall
-   ✅ Structured entity/slot system
-   ❌ Database migration (PostgreSQL/SQLite)
-   ❌ Vector embeddings for semantic search
-   ❌ Advanced querying and indexing

### 🌐 Web Dashboard

**Status: ❌ Not Started**

-   Local status page
-   Shows:
    -   Current state (IDLE / THINKING / etc.)
    -   Last events
    -   Avatar visualization

### 🎤 Voice System

**Status: ❌ Not Started**

-   Wake word detection
-   Local speech-to-text (e.g., whisper.cpp)
-   Text-to-speech (e.g., piper)

------------------------------------------------------------------------

## Phase 3 -- Full Assistant Capabilities

### ✉ Write Capabilities

-   Discord message sending
-   Possibly WhatsApp integration
-   Permission layer to prevent misuse

### 🔋 Power Management

-   Sleep mode
-   Screen off
-   Reduced services when idle

### 🛡 Security & Policy Layer

-   Tool authorization
-   Action logging
-   Anti-loop protections
-   Rate limiting

------------------------------------------------------------------------

## 🏗 Target Architecture

                    ┌─────────────────────────┐
                    │    Agent Core ✅        │
                    │  - CLI Interface        │
                    │  - Tool System          │
                    │  - Memory Store         │
                    │  - LangChain Agent      │
                    │  [API Mode: Pending]    │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │ Discord ✅    │  │ Calendar ❌   │  │ Memory ✅     │
      │ Service       │  │ Service       │  │               │
      │ - Read only   │  │ - REST API    │  │ - JSON Store  │
      │ - Emits JSON  │  │ - Events      │  │ - Persistence │
      └───────────────┘  └───────────────┘  └───────────────┘

**Current Status:**
✅ Agent Core (CLI with 15+ tools)
✅ Discord Connector (read-only listener)
✅ Memory persistence (JSON-based)
❌ Service-to-service communication
❌ Calendar Service
❌ Web Dashboard
❌ Voice System

Communication model:

-   HTTP → Queries and Commands (planned)
-   Pub/Sub (Redis) → Event notifications (planned)
-   JSON → Standard event format across services

------------------------------------------------------------------------

## 🧭 Immediate Next Steps

### Priority 1: Service Integration
1.  **Agent Core REST API** - Wrap CLI agent in HTTP server (FastAPI/Flask)
2.  **Event forwarding** - Connect Discord service to Agent Core endpoint
3.  **Service discovery** - Define communication protocol between services

### Priority 2: Calendar Service
1.  Implement Calendar service with REST API
2.  Connect Agent Core calendar tools to real service
3.  Add event polling and notifications

### Priority 3: Enhanced Features
1.  Implement Web Dashboard for status monitoring
2.  Add database layer (migrate from JSON to PostgreSQL/SQLite)
3.  Improve memory system with semantic search
4.  Implement voice input/output system

### Priority 4: Security & Production
1.  Add policy and permission layer
2.  Implement rate limiting and anti-loop protections
3.  Action logging and audit trail
4.  Docker containerization and docker-compose orchestration

------------------------------------------------------------------------

## 🚀 Long-Term Vision

A fully local, modular AI assistant that:

-   ✅ Provides intelligent conversation with tool-based reasoning
-   ✅ Maintains persistent memory of facts and context
-   ✅ Performs deterministic operations (math, time, system info)
-   🔄 Listens via voice or Discord (Discord input ready)
-   🔄 Manages calendar and reminders (tools ready, service pending)
-   🔄 Stores structured knowledge (basic implementation complete)
-   🔄 Operates securely in Docker (containerization pending)
-   🔄 Runs 24/7 on dedicated hardware
-   🔄 Evolves into a powerful personal automation system

**Legend:** ✅ Complete | 🔄 In Progress | ❌ Not Started
