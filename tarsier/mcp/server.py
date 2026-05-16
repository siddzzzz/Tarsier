import sys
import os

# Ensure tarsier is in the python path if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp.server.fastmcp import FastMCP
from tarsier import Desktop

# Initialize FastMCP Server
mcp = FastMCP("Tarsier Desktop Automation")
desktop = Desktop()

@mcp.tool()
def desktop_open_app(executable: str, window_name: str = None) -> str:
    """
    Opens a desktop application and attaches to it.
    
    Args:
        executable: The name of the executable (e.g. 'notepad.exe', 'calc.exe', 'code')
        window_name: (Optional) The specific window title to attach to. If None, it grabs the active window.
    """
    try:
        app = desktop.open_app(executable, window_name)
        return f"Successfully opened app and attached to window: '{app.name}'"
    except Exception as e:
        return f"Error opening app: {e}"

@mcp.tool()
def desktop_get_ui(window_name: str) -> str:
    """
    Retrieves the entire semantic UI tree (Desktop DOM) for a specific window in JSON format.
    Use this to see what buttons, textboxes, and menus are currently on the screen.
    
    Args:
        window_name: The name of the window to inspect.
    """
    try:
        window = desktop.get_window(window_name)
        return window.to_json()
    except Exception as e:
        return f"Error getting UI: {e}"

@mcp.tool()
def desktop_click(window_name: str, role: str, name: str) -> str:
    """
    Semantically finds a UI element inside a window and clicks it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element (e.g. 'button', 'menuitem', 'tab').
        name: The exact semantic name of the element (e.g. 'Save', 'File').
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.click()
        return f"Successfully clicked the '{name}' {role}."
    except Exception as e:
        return f"Error clicking element: {e}"

@mcp.tool()
def desktop_type(window_name: str, role: str, name: str, text: str) -> str:
    """
    Semantically finds a textbox or input field and types text into it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element (e.g. 'document', 'edit').
        name: The name of the element (optional if there's only one main document, but best to provide).
        text: The text to inject.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.type(text)
        return f"Successfully typed text into the '{name}' {role}."
    except Exception as e:
        return f"Error typing text: {e}"

@mcp.tool()
def desktop_read_text(window_name: str, role: str, name: str) -> str:
    """
    Reads and returns the textual contents of a specific UI element (like a document or textbox).
    Use this to read the contents of an open file or field without dumping the entire UI tree.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element (e.g. 'document', 'edit').
        name: The exact semantic name of the element.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        content = element.read()
        return content
    except Exception as e:
        return f"Error reading text: {e}"

def main():
    """Starts the stdio MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
