import sys
import os

# Ensure tarsier is in the python path if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Optional
from mcp.server.fastmcp import FastMCP
from tarsier import Desktop

# Initialize FastMCP Server
mcp = FastMCP("Tarsier Automation")
desktop = Desktop()
web_desktop = None

def get_web(headless: bool = False):
    """Lazy loads the WebDesktop so Chromium isn't started unless requested."""
    global web_desktop
    if not web_desktop:
        from tarsier import WebDesktop
        web_desktop = WebDesktop(headless=headless)
    return web_desktop

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
        return window.to_yaml_snapshot()
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
def desktop_right_click(window_name: str, role: str, name: str) -> str:
    """
    Semantically finds a UI element inside a window and right-clicks it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element (e.g. 'button', 'menuitem', 'tab').
        name: The exact semantic name of the element (e.g. 'Save', 'File').
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.right_click()
        return f"Successfully right-clicked the '{name}' {role}."
    except Exception as e:
        return f"Error right-clicking element: {e}"

@mcp.tool()
def desktop_hover(window_name: str, role: str, name: str) -> str:
    """
    Semantically finds a UI element inside a window and hovers the mouse cursor over it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element.
        name: The exact semantic name of the element.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.hover()
        return f"Successfully hovered over the '{name}' {role}."
    except Exception as e:
        return f"Error hovering element: {e}"

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

@mcp.tool()
def desktop_hotkey(keys: str) -> str:
    """
    Sends a global OS keyboard shortcut or hotkey.
    
    Args:
        keys: The hotkey string to send (e.g., '{Ctrl}c', '{Alt}{Tab}', '{LWin}r').
    """
    try:
        desktop.hotkey(keys)
        return f"Successfully sent hotkey: {keys}"
    except Exception as e:
        return f"Error sending hotkey: {e}"

@mcp.tool()
def desktop_drag_and_drop(window_name: str, source_role: str, source_name: str, target_role: str, target_name: str) -> str:
    """
    Semantically finds a source element and drags it to a target element.
    
    Args:
        window_name: The name of the window containing the elements.
        source_role: The role of the element to drag.
        source_name: The name of the element to drag.
        target_role: The role of the destination element.
        target_name: The name of the destination element.
    """
    try:
        window = desktop.get_window(window_name)
        source_element = window.find(role=source_role, name=source_name)
        target_element = window.find(role=target_role, name=target_name)
        desktop.drag_and_drop(source_element, target_element)
        return f"Successfully dragged '{source_name}' to '{target_name}'."
    except Exception as e:
        return f"Error dragging and dropping: {e}"

@mcp.tool()
def desktop_drag_and_drop_coordinates(start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> str:
    """
    Performs a drag-and-drop gesture from physical coordinates (start_x, start_y) to (end_x, end_y).
    
    Args:
        start_x: The starting X coordinate.
        start_y: The starting Y coordinate.
        end_x: The ending X coordinate.
        end_y: The ending Y coordinate.
        move_speed: Mouse movement speed (default is 1).
        wait_time: Delay in seconds after mouse up (default is 0.5).
    """
    try:
        desktop.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed=move_speed, wait_time=wait_time)
        return f"Successfully performed coordinate drag-and-drop from ({start_x}, {start_y}) to ({end_x}, {end_y})."
    except Exception as e:
        return f"Error performing coordinate drag-and-drop: {e}"

@mcp.tool()
def desktop_manage_window(window_name: str, action: str, x: int = None, y: int = None, width: int = None, height: int = None) -> str:
    """
    Manages and manipulates an entire Desktop window.
    
    Args:
        window_name: The name of the window to manage.
        action: The action to perform. Must be one of: 'maximize', 'minimize', 'restore', 'close', 'move', 'resize'.
        x: The X coordinate (required if action is 'move').
        y: The Y coordinate (required if action is 'move').
        width: The new width (required if action is 'resize').
        height: The new height (required if action is 'resize').
    """
    try:
        window = desktop.get_window(window_name)
        action = action.lower()
        if action == 'maximize':
            window.maximize()
        elif action == 'minimize':
            window.minimize()
        elif action == 'restore':
            window.restore()
        elif action == 'close':
            window.close()
        elif action == 'move':
            if x is None or y is None:
                return "Error: x and y must be provided for 'move' action."
            window.move(x, y)
        elif action == 'resize':
            if width is None or height is None:
                return "Error: width and height must be provided for 'resize' action."
            window.resize(width, height)
        else:
            return f"Error: Unknown action '{action}'"
            
        return f"Successfully performed '{action}' on window '{window_name}'."
    except Exception as e:
        return f"Error managing window: {e}"

# ==========================================
# WEB AUTOMATION TOOLS
# ==========================================

@mcp.tool()
def web_start_browser(headless: bool = False) -> str:
    """
    Starts the Playwright Chromium browser session.
    You usually don't need to call this manually unless you specifically want to start it in headless mode,
    as other web_ tools will auto-start it in non-headless mode if not already running.
    
    Args:
        headless: If True, the browser runs invisibly in the background. Defaults to False so the user can see.
    """
    try:
        get_web(headless=headless)
        mode = "headless" if headless else "visible"
        return f"Successfully started web browser in {mode} mode."
    except Exception as e:
        return f"Error starting browser: {e}"

@mcp.tool()
def web_goto(url: str) -> str:
    """
    Navigates the web browser to a specific URL.
    
    Args:
        url: The URL to navigate to (e.g., 'https://en.wikipedia.org/wiki/Main_Page')
    """
    try:
        web = get_web()
        page = web.goto(url)
        return f"Successfully navigated to {url}. Page title: '{page.name}'"
    except Exception as e:
        return f"Error navigating: {e}"

@mcp.tool()
def web_get_ui() -> str:
    """
    Retrieves the semantic UI tree (Web DOM) for the current web page.
    This returns a YAML string representing the accessibility tree (ARIA snapshot).
    """
    try:
        web = get_web()
        page = web.get_current_page()
        return page.to_json()
    except Exception as e:
        return f"Error getting Web UI: {e}"

@mcp.tool()
def web_click(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None) -> str:
    """
    Finds a UI element on the current web page (semantically or via CSS selector) and clicks it.
    
    Args:
        role: Optional semantic role of the element (e.g. 'button', 'link', 'checkbox').
        name: Optional exact semantic name of the element (e.g. 'Search', 'Submit').
        selector: Optional CSS/XPath selector fallback (e.g. '.shopping_cart_link') if element lacks clear semantic tags.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        element.click()
        return f"Successfully clicked the element (role={role}, name={name}, selector={selector})."
    except Exception as e:
        return f"Error clicking web element: {e}"

@mcp.tool()
def web_type(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None, text: str = "") -> str:
    """
    Finds a textbox or input field on the web page (semantically or via CSS selector) and types text into it.
    
    Args:
        role: Optional semantic role of the element (e.g. 'textbox', 'searchbox').
        name: Optional name of the element.
        selector: Optional CSS/XPath selector fallback (e.g. '#search-input') if element lacks clear semantic tags.
        text: The text to type.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        element.type(text)
        return f"Successfully typed text into the element (role={role}, name={name}, selector={selector})."
    except Exception as e:
        return f"Error typing web text: {e}"

@mcp.tool()
def web_read_text(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None) -> str:
    """
    Reads and returns the textual contents of a specific web element (like a paragraph, heading, or generic container).
    
    Args:
        role: Optional semantic role of the element (e.g. 'heading', 'main', 'article').
        name: Optional exact semantic name of the element.
        selector: Optional CSS/XPath selector fallback (e.g. '.product-price') if element lacks clear semantic tags.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        return element.read()
    except Exception as e:
        return f"Error reading web text: {e}"

def main():
    """Starts the stdio MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
