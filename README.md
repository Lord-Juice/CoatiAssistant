# CoatiAssistant -- Project Summary

## 📦 Repository Overview

GitHub: https://github.com/Lord-Juice/CoatiAssistant

The project is structured as a multi-service Docker-based assistant
system written primarily in Python.\
It is designed to evolve in phases into a fully capable AI assistant
running locally 24/7.

------------------------------------------------------------------------

## ✅ What Already Exists

### 1️⃣ Discord Connector (Read-Only Listener)

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

## 🎯 Project Goals

------------------------------------------------------------------------

## Phase 1 -- Core Foundation (Almost Complete)

✔ Discord listener\
✔ Message parsing and structured JSON output\
❌ Event forwarding to Agent Core (HTTP or message bus not yet
implemented)

Next step: - Define an Agent Core endpoint (e.g., `POST /events`) -
Forward JSON events instead of only printing them

------------------------------------------------------------------------

## Phase 2 -- Intelligence & Persistence

### 🧠 Agent Core

-   Central orchestration engine
-   Handles:
    -   Conversation logic
    -   Service routing
    -   Memory access
    -   Policies & permissions

### 🗓 Calendar Service

-   REST API:
    -   `GET /events?from=...&to=...`
    -   `POST /events`
-   Polling or event push for upcoming events
-   Emits structured calendar events

### 💾 Memory / Database

-   Persistent storage for:
    -   "Merk dir ..." statements
    -   Reminders
    -   Stored knowledge
-   Likely PostgreSQL or SQLite
-   Possibly vector embeddings later

### 🌐 Web Dashboard

-   Local status page
-   Shows:
    -   Current state (IDLE / THINKING / etc.)
    -   Last events
    -   Avatar visualization

### 🎤 Voice System

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
                    │       Agent Core        │
                    │  - Decision Engine      │
                    │  - Memory               │
                    │  - Service Router       │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │ Discord       │  │ Calendar      │  │ Memory / DB   │
      │ Service       │  │ Service       │  │               │
      │ - Read only   │  │ - REST API    │  │ - Persistence │
      │ - Emits JSON  │  │ - Emits Events│  │               │
      └───────────────┘  └───────────────┘  └───────────────┘

Communication model:

-   HTTP → Queries and Commands
-   Pub/Sub (Redis) → Event notifications
-   JSON → Standard event format across services

------------------------------------------------------------------------

## 🧭 Immediate Next Steps

1.  Implement Agent Core service.
2.  Add event forwarding from Discord service to Agent Core.
3.  Implement basic Calendar service.
4.  Add database layer.
5.  Expand to voice + UI.

------------------------------------------------------------------------

## 🚀 Long-Term Vision

A fully local, modular AI assistant that:

-   Listens via voice or Discord
-   Manages calendar and reminders
-   Stores memory
-   Operates securely in Docker
-   Runs 24/7 on dedicated hardware
-   Evolves into a powerful personal automation system
