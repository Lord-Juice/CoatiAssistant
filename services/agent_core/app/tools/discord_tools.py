from langchain.tools import tool
from rich.console import Console

console = Console()

@tool
def discord_send_message(channel: str, content: str) -> str:
    """Send a Discord message to a channel. Use this to notify users via Discord."""
    console.print(f"[bold magenta][MOCK Discord][/bold magenta] -> #{channel}: {content}")
    return "OK (mock): message printed to console"
