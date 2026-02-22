import platform
from langchain.tools import tool

@tool
def get_system_info() -> str:
    """Return basic system information."""
    return f"{platform.system()} {platform.release()} | Python {platform.python_version()}"

@tool
def read_text_file(path: str) -> str:
    """Read a text file and return its content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {e}"