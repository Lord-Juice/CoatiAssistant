# CoatiAssistant - Service Setup Guide

This project uses multiple services, each with its own virtual environment to prevent package conflicts.

## Services

### 1. Discord Connector (`services/discord_connector/`)
Reads Discord messages and logs them as JSON events. Uses `discord.py`.

**Setup:**
```bash
cd services/discord_connector
setup.bat
start.bat
```

### 2. Self Bot (`services/self_bot/`)
Discord self-bot with various features. Uses `discord.py-self`.

**Setup:**
```bash
cd services/self_bot
setup.bat
start.bat
```

## Important Notes

⚠️ **Each service has its own virtual environment:**
- `services/discord_connector/venv/` - Discord Connector
- `services/self_bot/venv/` - Self Bot

**Do NOT use the workspace-level `.venv` for individual services.** It will cause package conflicts since `discord.py` and `discord.py-self` cannot coexist.

## Cleanup (Optional)

If you previously used the workspace-level `.venv`, you can remove it:
```bash
rmdir /s /q .venv
```

This prevents accidental use of the old, conflicted environment.

## Running Services

❌ **Wrong:**
```bash
.venv\Scripts\python.exe services/discord_connector/app/bot.py
```

✅ **Correct:**
```bash
cd services/discord_connector
start.bat
```

Or manually:
```bash
cd services/discord_connector
.\venv\Scripts\activate.bat
python app\bot.py
```

## Troubleshooting

If you still get `AttributeError: module 'discord' has no attribute 'Intents'`:

1. Make sure you're in the correct service directory
2. Delete the service's `venv/` folder and re-run `setup.bat`
3. Verify you're using the service-specific venv, not `.venv`

## Future Services

When adding new services:
1. Create a `requirements.txt` in the service directory
2. Add `setup.bat` that creates a dedicated `venv/`
3. Add `start.bat` that activates the venv and runs the service
4. Document in the service's README.md
