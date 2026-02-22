from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.text import Text

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage, HumanMessage

from tools import *

console = Console()

TOOLS = [
    calendar_list_events,
    calendar_create_event,
    get_current_datetime,
    get_current_weekday,
    add_days_to_now,
    discord_send_message,
    calculate,
    random_number,
    generate_uuid,
    remember,
    recall,
    clear_memory,
    get_system_info,
    read_text_file,
    get_today_range,
    get_tomorrow_range,
]

SYSTEM_PROMPT = (
    "You are CoatiAssistant Agent Core, a local AI assistant running on the user's machine. "
    "You can chat normally and provide helpful explanations.\n\n"
    "You have access to tools for deterministic or system-related tasks. "
    "Never guess values for time, dates, calculations, or system data.\n\n"
    "Decision procedure (must follow):\n"
    "1) Identify the user's goal.\n"
    "2) Identify which tool(s) are needed to fulfill the goal.\n"
    "3) Before calling the main tool, check whether any required arguments are missing or uncertain.\n"
    "4) If required arguments are missing/uncertain, call the appropriate helper tool(s) to gather them.\n"
    "5) Repeat step 3-4 until you have all required arguments.\n"
    "6) Call the main tool with the complete, correctly formatted arguments.\n"
    "7) Use the tool result to produce the final answer.\n\n"
    "Tool usage rules:\n"
    "- For 'today', 'tomorrow', 'this week', or relative time phrases: use date/time helper tools to compute ranges.\n"
    "- For math: use the calculator tool.\n"
    "- For Discord messages: use the Discord tool.\n"
    "- For calendar listing/creation: use calendar tools only with valid ISO datetimes.\n"
    "- For memory: use remember/recall/clear.\n"
    "- For file reading and system info: use the corresponding tools.\n\n"
    "Be concise. Do not mention internal tools by name unless asked. "
    "Do not ask the user for information you can obtain via tools."
    "For questions about previously stored personal facts (e.g. “Where is my wallet?”, “What is my dog’s name?”), ALWAYS try memory recall first before asking follow-up questions."
)


def _truncate(s: str, n: int = 500) -> str:
    s = str(s).strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def _clean_tool_output(output: Any) -> str:
    # LangChain gibt manchmal ToolMessage/Objekte zurück; wir wollen nur den content
    if hasattr(output, "content"):
        return str(output.content)
    return str(output)


@dataclass
class ToolLog:
    name: str
    input: str
    output: str = ""
    status: str = "Calling"  # Calling | Done | Error


class AgentLiveHandler(BaseCallbackHandler):
    """
    Debug UI:
    - Thinking/Tool spinner
    - Tool logs + inputs + outputs
    - Antwort wird NICHT im Debug-Panel gerendert (nur intern gesammelt)
    """

    def __init__(self) -> None:
        self.phase: str = "thinking"  # thinking | tool | answering
        self.answer_buffer: Text = Text()  # sammelt streaming tokens, wird später außerhalb gedruckt

        self.tool_logs: List[ToolLog] = []
        self._current_tool_index: Optional[int] = None

        self._live: Optional[Live] = None
        self.thinking_spinner = Spinner("dots", text="Thinking...", style="yellow")
        self.tool_spinner = Spinner("dots", text="Running tool...", style="magenta")

    def bind_live(self, live: Live) -> None:
        self._live = live
        self._refresh()

    def _refresh(self) -> None:
        if self._live:
            self._live.update(self.render())

    def render(self) -> Panel:
        renderables: List[Any] = []

        # Phase header
        if self.phase == "thinking":
            renderables.append(self.thinking_spinner)
        elif self.phase == "tool":
            renderables.append(self.tool_spinner)
        elif self.phase == "answering":
            # Wir streamen Tokens in den Buffer, aber zeigen hier nur einen Status
            renderables.append(Text("Streaming response...", style="bold green"))

        # Tool logs
        if self.tool_logs:
            tool_text = Text("\n[Tools]\n", style="bold magenta")
            for log in self.tool_logs:
                tool_text.append(f"• {log.status}: {log.name}\n", style="bold magenta")
                if log.input:
                    tool_text.append(f"  in:  {_truncate(log.input)}\n", style="dim")
                if log.output:
                    tool_text.append(f"  out: {_truncate(log.output)}\n", style="dim")
                tool_text.append("\n")
            renderables.append(tool_text)

        return Panel(Group(*renderables), title="CoatiAssistant Debug", border_style="cyan")

    # ---- LLM ----
    def on_llm_start(self, *args, **kwargs):
        self.phase = "thinking"
        self.answer_buffer = Text()
        self._refresh()

    def on_llm_new_token(self, token: str, **kwargs):
        if self.phase != "answering":
            self.phase = "answering"
        self.answer_buffer.append(token)
        self._refresh()

    # ---- Tool ----
    def on_tool_start(self, serialized: Dict[str, Any], input_str: Any = None, **kwargs):
        self.phase = "tool"
        name = serialized.get("name", "unknown_tool")

        # input_str kommt je nach LangChain-Version als dict/str
        inp = input_str if input_str is not None else {}
        self.tool_logs.append(ToolLog(name=name, input=str(inp), status="Calling"))
        self._current_tool_index = len(self.tool_logs) - 1
        self._refresh()

    def on_tool_end(self, output: Any, **kwargs):
        cleaned = _clean_tool_output(output)

        if self._current_tool_index is not None:
            self.tool_logs[self._current_tool_index].output = cleaned
            self.tool_logs[self._current_tool_index].status = "Done"

        self._current_tool_index = None
        self.phase = "thinking"
        self._refresh()

    def on_tool_error(self, error: BaseException, **kwargs):
        if self._current_tool_index is not None:
            self.tool_logs[self._current_tool_index].output = str(error)
            self.tool_logs[self._current_tool_index].status = "Error"

        self._current_tool_index = None
        self.phase = "thinking"
        self._refresh()


def main() -> None:
    model_name = "qwen2.5:3b"

    llm = ChatOllama(
        model=model_name,
        temperature=0,
        streaming=True,
    )

    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    messages: List[BaseMessage] = []

    debug_mode = False

    console.print("[bold green]CoatiAssistant Agent Core (CLI)[/bold green]")
    console.print("Commands: /exit, /reset, /debug\n")

    while True:
        user = Prompt.ask("[bold cyan]You[/bold cyan]").strip()

        if not user:
            continue

        if user == "/exit":
            break

        if user == "/reset":
            messages = []
            console.print("[yellow]Conversation reset.[/yellow]\n")
            continue

        if user == "/debug":
            debug_mode = not debug_mode
            console.print(f"[yellow]Debug mode: {'ON' if debug_mode else 'OFF'}[/yellow]\n")
            continue

        messages.append(HumanMessage(content=user))

        handler = AgentLiveHandler()

        # Debug OFF => transient=True (verschwindet)
        # Debug ON  => transient=False (bleibt)
        transient = not debug_mode

        with Live(handler.render(), console=console, refresh_per_second=20, transient=transient) as live:
            handler.bind_live(live)
            result = agent.invoke(
                {"messages": messages},
                config={"callbacks": [handler]},
            )

        new_messages = result.get("messages", [])
        if new_messages:
            messages = new_messages

        # Finale Antwort IMMER außerhalb vom Debug Panel ausgeben
        final_text = handler.answer_buffer.plain.strip()
        if not final_text and messages:
            final_text = getattr(messages[-1], "content", "").strip()

        console.print(f"Answer: {final_text}\n")


if __name__ == "__main__":
    main()