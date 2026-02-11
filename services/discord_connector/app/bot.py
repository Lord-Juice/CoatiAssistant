import os
import re
import sys
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

import discord
from dotenv import load_dotenv

# -----------------------------
# Config
# -----------------------------
def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN ist nicht gesetzt (Environment Variable).")

# Optional: wenn gesetzt, werden Nachrichten dieses Users/Bots ignoriert
IGNORE_AUTHOR_IDS = {
    s.strip()
    for s in (os.getenv("DISCORD_IGNORE_AUTHOR_IDS") or "").split(",")
    if s.strip()
}

MENTION_RE = re.compile(r"^<@!?(\d+)>$")

# Optional: Wenn true, werden nur DMs an diesen Bot verarbeitet (nicht in Servern)
ONLY_ACCEPT_DMS = env_bool("DISCORD_ONLY_ACCEPT_DMS", default=False)

# Optional: Debug-Logs
DEBUG = env_bool("DISCORD_DEBUG", default=False)

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger("discord_service")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# -----------------------------
# Helpers
# -----------------------------
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def safe_json_dumps(obj) -> str:
    # ensure_ascii=False für Umlaute; separators für kompakte one-line JSON logs
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

@dataclass(frozen=True)
class ForwardedParseResult:
    forwarded_author_username: str
    forwarded_channel_name: str
    forwarded_guild_name: Optional[str]
    forwarded_content: str
    is_dm: bool

def normalize_lines(raw: str) -> list[str]:
    # Normalisiert Windows CRLF etc. und entfernt nur LEADING/TRAILING Leerzeilen,
    # aber behält Leerzeilen innerhalb der Nachricht.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")

    # strip only outer empty lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    return lines

def parse_forwarded_message(raw: str) -> Optional[ForwardedParseResult]:
    """
    Erwartetes Forward-Format:
      1: @Username   ODER  <@1234567890> / <@!1234567890>
      2: Channel
      3: Server
      4+: Nachricht (kann mehrzeilig sein)

    Sonderfall DMs:
      Channel == "DM"
      Server  == "(DM)"
    """
    if not raw or not raw.strip():
        return None

    lines = normalize_lines(raw)
    if len(lines) < 4:
        return None

    author_line = lines[0].strip()
    channel_line = lines[1].strip()
    guild_line = lines[2].strip()

    forwarded_content = "\n".join(lines[3:]).strip()
    if not forwarded_content:
        return None

    # 1) Author normalisieren: @Name oder Mention <@id>/<@!id>
    forwarded_author_username: Optional[str] = None

    if author_line.startswith("@"):
        forwarded_author_username = author_line[1:].strip() or None
    else:
        m = MENTION_RE.match(author_line)
        if m:
            # Wir haben nur eine ID, keinen Username. Für dein JSON brauchst du aber "author_username".
            # Wir setzen ihn sinnvoll auf die ID als String (oder du lässt es auf None).
            forwarded_author_username = m.group(1)

    if not forwarded_author_username:
        return None

    is_dm = (channel_line == "DM") and (guild_line == "(DM)")

    if is_dm:
        forwarded_guild_name = None
    else:
        g = guild_line.strip()
        forwarded_guild_name = None if g in ("", "null", "(DM)") else g

    return ForwardedParseResult(
        forwarded_author_username=forwarded_author_username,
        forwarded_channel_name=channel_line,
        forwarded_guild_name=forwarded_guild_name,
        forwarded_content=forwarded_content,
        is_dm=is_dm,
    )

# -----------------------------
# Discord client
# -----------------------------
intents = discord.Intents.default()
# Wir parsen message.content -> dafür braucht man message_content
# Für DMs klappt es oft ohne, aber wir machen es stabil:
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info("✅ Eingeloggt als %s (id=%s)", client.user, getattr(client.user, "id", None))

@client.event
async def on_message(message: discord.Message):
    """
    WICHTIG: dieser Bot sendet NIE Nachrichten. Er liest nur und loggt Events als JSON.
    """
    try:
        # 0) Selbstnachrichten ignorieren
        if message.author == client.user:
            return

        # 1) Optional: Nur DMs verarbeiten (falls du das willst)
        is_actual_dm_to_bot = message.guild is None
        if ONLY_ACCEPT_DMS and not is_actual_dm_to_bot:
            return

        # 2) Optional: bestimmte Sender ignorieren (IDs als CSV in DISCORD_IGNORE_AUTHOR_IDS)
        author_id_str = str(message.author.id) if message.author and message.author.id else ""
        if author_id_str and author_id_str in IGNORE_AUTHOR_IDS:
            return

        # 3) Parsing des forwarded Formats
        parsed = parse_forwarded_message(message.content or "")
        if parsed is None:
            if DEBUG:
                logger.debug("Nicht parsebar. author_id=%s guild=%s channel=%s",
                             author_id_str,
                             getattr(message.guild, "name", None),
                             getattr(message.channel, "id", None))
            return

        # 4) Event bauen
        # Hinweis: author_id ist die ID des Senders an DIESEN Bot (z.B. Weiterleitungsbot),
        # nicht die Original-ID des forwarded_author_username (die kennen wir nicht).
        event = {
            "event_type": "discord.message_received",
            "source": "discord_service",
            "timestamp": iso_utc_now(),
            "data": {
                "is_dm": bool(parsed.is_dm),
                "author_username": parsed.forwarded_author_username,
                "author_id": author_id_str or None,
                "channel_name": parsed.forwarded_channel_name,
                "channel_id": str(message.channel.id) if getattr(message.channel, "id", None) else None,
                "guild_name": None if parsed.is_dm else parsed.forwarded_guild_name,
                "guild_id": None if parsed.is_dm else (str(message.guild.id) if message.guild else None),
                "content": parsed.forwarded_content,
            },
        }

        logger.info(safe_json_dumps(event))

    except Exception as e:
        # Niemals crashen, nur loggen
        logger.exception("Fehler in on_message: %s", e)

def main():
    try:
        client.run(TOKEN)
    except Exception as e:
        logger.exception("Bot konnte nicht starten: %s", e)
        raise

if __name__ == "__main__":
    main()
