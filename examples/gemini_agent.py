import os
import sys
import time
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from tarsier import Desktop, WebDesktop

# Ensure tarsier is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Initialize Desktop Automation
desktop = Desktop(highlight_actions=True)
web_desktop = None

def get_web():
    """Lazy-load the WebDesktop instance."""
    global web_desktop
    if not web_desktop:
        web_desktop = WebDesktop(headless=False)
    return web_desktop

# =====================================================================
# Agent Tools Definitions
# =====================================================================

def desktop_open_app(executable: str, window_name: Optional[str] = None) -> str:
    """
    Opens a desktop application and attaches to it.
    
    Args:
        executable: The executable name (e.g., 'notepad.exe', 'calc.exe', 'code').
        window_name: (Optional) The title of the window to attach to. If omitted, grabs active window.
    """
    try:
        app = desktop.open_app(executable, window_name)
        return f"Successfully opened and attached to window: '{app.name}'"
    except Exception as e:
        return f"Error opening app: {e}"

def desktop_get_ui(window_name: str) -> str:
    """
    Retrieves the semantic YAML UI snapshot (Desktop DOM) for a specific window.
    Use this to see what buttons, textboxes, and lists are visible inside the window.
    
    Args:
        window_name: The name or title of the window to inspect.
    """
    try:
        window = desktop.get_window(window_name)
        return window.to_yaml_snapshot()
    except Exception as e:
        return f"Error getting UI tree for window '{window_name}': {e}"

def desktop_click(window_name: str, role: str, name: str) -> str:
    """
    Finds a UI element by role and name inside a window and clicks it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element (e.g., 'button', 'menuitem', 'tab').
        name: The exact name of the element (e.g., 'Save', 'File').
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.click()
        return f"Successfully clicked '{name}' {role}."
    except Exception as e:
        return f"Error clicking element: {e}"

def desktop_right_click(window_name: str, role: str, name: str) -> str:
    """
    Finds a UI element by role and name inside a window and right-clicks it.
    
    Args:
        window_name: The name of the window containing the element.
        role: The semantic role of the element.
        name: The exact name of the element.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.right_click()
        return f"Successfully right-clicked '{name}' {role}."
    except Exception as e:
        return f"Error right-clicking element: {e}"

def desktop_hover(window_name: str, role: str, name: str) -> str:
    """
    Finds a UI element inside a window and hovers the mouse cursor over it.
    
    Args:
        window_name: The name of the window.
        role: The semantic role of the element.
        name: The name of the element.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.hover()
        return f"Successfully hovered over '{name}' {role}."
    except Exception as e:
        return f"Error hovering over element: {e}"

def desktop_type(window_name: str, role: str, name: str, text: str) -> str:
    """
    Finds a textbox or editable document field inside a window and types text into it.
    
    Args:
        window_name: The name of the window.
        role: The semantic role of the input field (typically 'textbox' or 'document').
        name: The name of the field (can be empty if there's only one main area).
        text: The text string to type.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        element.type(text)
        return f"Successfully typed text into '{name}' {role}."
    except Exception as e:
        return f"Error typing into element: {e}"

def desktop_read_text(window_name: str, role: str, name: str) -> str:
    """
    Reads and returns the textual value of a specific element inside a window.
    
    Args:
        window_name: The name of the window.
        role: The semantic role of the element (e.g., 'textbox', 'document').
        name: The name of the element.
    """
    try:
        window = desktop.get_window(window_name)
        element = window.find(role=role, name=name)
        return element.read()
    except Exception as e:
        return f"Error reading text: {e}"

def desktop_hotkey(keys: str) -> str:
    """
    Sends a global OS keyboard hotkey or shortcut.
    
    Args:
        keys: The hotkey sequence (e.g., '{Ctrl}s', '{Alt}{Tab}', '{LWin}r', '{Enter}').
    """
    try:
        desktop.hotkey(keys)
        return f"Successfully sent global hotkey: {keys}"
    except Exception as e:
        return f"Error sending hotkey: {e}"

def desktop_drag_and_drop(window_name: str, source_role: str, source_name: str, target_role: str, target_name: str) -> str:
    """
    Drags a source element and drops it onto a target element inside a window.
    
    Args:
        window_name: The window name.
        source_role: Role of the element to drag.
        source_name: Name of the element to drag.
        target_role: Role of the element to drop onto.
        target_name: Name of the element to drop onto.
    """
    try:
        window = desktop.get_window(window_name)
        source = window.find(role=source_role, name=source_name)
        target = window.find(role=target_role, name=target_name)
        desktop.drag_and_drop(source, target)
        return f"Successfully dragged '{source_name}' to '{target_name}'."
    except Exception as e:
        return f"Error performing drag-and-drop: {e}"

def desktop_manage_window(window_name: str, action: str, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None) -> str:
    """
    Manages size, visibility, or coordinates of a window.
    
    Args:
        window_name: The title/name of the window.
        action: The action to perform. One of: 'maximize', 'minimize', 'restore', 'close', 'move', 'resize'.
        x: Required only for 'move'. The new X coordinate.
        y: Required only for 'move'. The new Y coordinate.
        width: Required only for 'resize'. New width.
        height: Required only for 'resize'. New height.
    """
    try:
        window = desktop.get_window(window_name)
        act = action.lower()
        if act == 'maximize':
            window.maximize()
        elif act == 'minimize':
            window.minimize()
        elif act == 'restore':
            window.restore()
        elif act == 'close':
            window.close()
        elif act == 'move':
            if x is None or y is None:
                return "Error: x and y must be provided for 'move' action."
            window.move(x, y)
        elif act == 'resize':
            if width is None or height is None:
                return "Error: width and height must be provided for 'resize' action."
            window.resize(width, height)
        else:
            return f"Error: Unknown action '{action}'"
        return f"Successfully executed '{action}' on window '{window_name}'."
    except Exception as e:
        return f"Error managing window: {e}"

def web_goto(url: str) -> str:
    """
    Navigates the web browser to a URL.
    
    Args:
        url: The website URL to visit.
    """
    try:
        web = get_web()
        page = web.goto(url)
        return f"Successfully navigated to {url}. Page title: '{page.name}'"
    except Exception as e:
        return f"Error navigating web browser: {e}"

def web_get_ui() -> str:
    """
    Retrieves the semantic YAML UI snapshot of the current web page.
    Use this to see textboxes, links, and buttons currently rendered in the browser.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        return page.to_yaml_snapshot()
    except Exception as e:
        return f"Error getting Web UI tree: {e}"

def web_click(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None) -> str:
    """
    Clicks an element on the current web page by its role and name, or CSS selector fallback.
    
    Args:
        role: Optional role of the element (e.g. 'button', 'link').
        name: Optional exact name of the element.
        selector: Optional CSS/XPath selector (e.g. '.btn-primary') if the element has no semantic tags.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        element.click()
        return f"Successfully clicked web element (role={role}, name={name}, selector={selector})."
    except Exception as e:
        return f"Error clicking web element: {e}"

def web_type(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None, text: str = "") -> str:
    """
    Types text into an input or search field on the web page.
    
    Args:
        role: Optional role of the input (e.g., 'textbox', 'searchbox').
        name: Optional name of the input.
        selector: Optional CSS/XPath selector fallback (e.g., '#username').
        text: The text value to input.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        element.type(text)
        return f"Successfully typed text into web element (role={role}, name={name}, selector={selector})."
    except Exception as e:
        return f"Error typing web element: {e}"

def web_read_text(role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None) -> str:
    """
    Reads the text content of a specific web element.
    
    Args:
        role: Optional role.
        name: Optional name.
        selector: Optional CSS selector.
    """
    try:
        web = get_web()
        page = web.get_current_page()
        element = page.wait_for_element(role=role, name=name, selector=selector, timeout=5)
        return element.read()
    except Exception as e:
        return f"Error reading web text: {e}"

def web_close_browser() -> str:
    """
    Closes the active web browser and Playwright browser process.
    """
    global web_desktop
    if web_desktop:
        try:
            web_desktop.close()
            web_desktop = None
            return "Successfully closed web browser."
        except Exception as e:
            return f"Error closing web browser: {e}"
    return "No web browser is currently running."

# =====================================================================
# Main Agent Loop
# =====================================================================

SYSTEM_INSTRUCTION = """
You are Tarsier-Agent, an autonomous AI computer control agent powered by the Tarsier library.
Your goal is to satisfy the user's request by manipulating the OS Desktop environment and the Web Browser.

You have access to a rich set of Python tools to open applications, manage windows, read states, click, hover, and type.

CRITICAL OPERATIONAL RULES:
1. EXPLORATION FIRST: You cannot interact with what you do not see. ALWAYS run `desktop_get_ui` (or `web_get_ui`) first to scan the screen when you focus on a new window or web page.
2. DYNAMIC WORKFLOWS: There is almost always more than one way to complete a task. If a direct semantic button click fails:
   - Try keyboard shortcuts via `desktop_hotkey`.
   - Use window transform actions via `desktop_manage_window`.
   - Right-click elements to open context menus.
   - Hover and try clicking.
3. ADAPT TO ENVIRONMENT: Tarsier automatically normalizes roles for you (e.g. mapping native 'edit' inputs to 'textbox'). Always refer to your YAML snapshot dumps for accurate element naming.
4. EXPLAIN & EXECUTE: Before each tool call, write a short explanation of what you are trying to do, then invoke the tool. Analyze the output and proceed to the next logical action.
5. FINALIZE: Once you are certain the task is finished, output a summary of what you did and conclude the run.
"""

def run_agent(task_prompt: str, api_key: str):
    print("\n[+] Configuring Gemini client...")
    genai.configure(api_key=api_key)
    
    # We use gemini-1.5-flash as it is extremely cheap, fast, and excellent at tool calling
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[
            desktop_open_app,
            desktop_get_ui,
            desktop_click,
            desktop_right_click,
            desktop_hover,
            desktop_type,
            desktop_read_text,
            desktop_hotkey,
            desktop_drag_and_drop,
            desktop_manage_window,
            web_goto,
            web_get_ui,
            web_click,
            web_type,
            web_read_text,
            web_close_browser
        ],
        system_instruction=SYSTEM_INSTRUCTION
    )

    print(f"\n[+] Starting agentic workflow for task:\n\"{task_prompt}\"")
    chat = model.start_chat()
    
    try:
        response = chat.send_message(task_prompt)
        
        while True:
            # Safely try to get text thought
            try:
                if response.text:
                    print(f"\n🧠 [Model Thought]:\n{response.text}")
            except Exception:
                pass
                
            # Check for function calls
            function_calls = []
            try:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_calls.append(part.function_call)
            except Exception:
                pass
                
            if not function_calls:
                break
                
            response_parts = []
            for call in function_calls:
                name = call.name
                args = call.args
                
                print(f"\n⚙️ [Model Action] Calling tool '{name}' with args:")
                for k, v in args.items():
                    val_str = str(v)
                    if len(val_str) > 100:
                        val_str = val_str[:100] + "..."
                    print(f"  - {k}: {val_str}")
                    
                # Execute tool
                result = "Unknown function"
                if name in globals():
                    try:
                        func_args = {k: v for k, v in args.items()}
                        result = globals()[name](**func_args)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                else:
                    result = f"Error: Tool '{name}' not found."
                    
                # Print output
                print(f"📊 [Tool Output]:")
                result_str = str(result)
                if len(result_str) > 500:
                    print(result_str[:500] + f"\n... (truncated {len(result_str)-500} characters)")
                else:
                    print(result_str)
                    
                # Build part
                part = genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=name,
                        response={'result': result}
                    )
                )
                response_parts.append(part)
                
            # Send back response
            response = chat.send_message(response_parts)
            
        print("\n=== Agent Finished Output ===")
        try:
            print(response.text)
        except Exception:
            print("(No final text output)")
            
    except Exception as e:
        print(f"\n[!] Execution error: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Get Gemini Key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        gemini_key = input("Please enter your GEMINI_API_KEY: ").strip()
        if not gemini_key:
            print("Error: GEMINI_API_KEY is required to run the agent.", file=sys.stderr)
            sys.exit(1)
            
    # Get Task Prompt
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("\nWhat task should the agent perform? (e.g. 'open notepad and type hello'): ").strip()
        if not task:
            print("Error: A task description must be provided.", file=sys.stderr)
            sys.exit(1)
            
    run_agent(task, gemini_key)
