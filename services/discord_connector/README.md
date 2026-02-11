# Discord Connector Setup

This service reads Discord messages and logs them as JSON events.

## Quick Start

### Option 1: Automatic Setup (Windows)
```bash
cd services/discord_connector
setup.bat
start.bat
```

This will:
1. Create a dedicated virtual environment (`venv/`)
2. Install required dependencies
3. Start the bot

### Option 2: Manual Setup
```bash
cd services/discord_connector
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app/bot.py
```

## Configuration

Set the following environment variables:
- `DISCORD_TOKEN` - Your Discord bot token (required)
- `DISCORD_ONLY_ACCEPT_DMS` - Only process DMs (optional, default: false)
- `DISCORD_IGNORE_AUTHOR_IDS` - Comma-separated IDs to ignore (optional)
- `DISCORD_DEBUG` - Enable debug logging (optional, default: false)

Create a `.env` file in the `app/` directory:
```
DISCORD_TOKEN=your_token_here
```

## Note on Virtual Environments

**Important:** This service uses its own dedicated virtual environment (`services/discord_connector/venv/`) to avoid conflicts with other services that may use incompatible Discord packages (like `discord.py-self` in the self_bot).

Do **not** use the workspace-level `.venv` for this service.

## Message Format

The bot expects forwarded messages in this format:
```
@Username (or <@UserID>)
#channel
Server Name
Message content here
```

For DMs:
```
@Username
DM
(DM)
Message content here
```

## Output

Messages are logged as JSON events with the structure:
```json
{
  "event_type": "discord.message_received",
  "source": "discord_service",
  "timestamp": "2026-02-11T22:27:28Z",
  "data": {
    "is_dm": false,
    "author_username": "username",
    "author_id": "123456789",
    "channel_name": "#channel",
    "channel_id": "987654321",
    "guild_name": "Server Name",
    "guild_id": "555555555",
    "content": "Message content"
  }
}
```
