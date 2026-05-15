import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from tarsier import Desktop

def main():
    print("Initializing Tarsier Desktop...")
    desktop = Desktop()
    
    print("Opening Notepad...")
    # Open notepad. 'Untitled - Notepad' is typical, but varies by OS version (e.g. 'Untitled - Notepad' vs just 'Notepad')
    notepad = desktop.open_app("notepad.exe")
    
    print(f"Attached to window: {notepad.name}")
    
    print("Checking if it's a new file or an existing one...")
    time.sleep(1)
    
    # Simulate an LLM parsing the UI JSON state
    # In reality, an LLM would read `notepad.to_json()` here to make a decision
    ui_state_dict = notepad.dump_ui()
    window_name = ui_state_dict.get("name", "")
    
    print(f"Agent observed window name: '{window_name}'")
    
    # Make sure we focus the window before typing, in case the terminal stole focus
    notepad.focus()
    
    if "Untitled" not in window_name and window_name != "Notepad":
        print(f"Agent determined this is an existing file. Simulating decision to append...")
        try:
            editor = notepad.textbox()
            editor._control.SendKeys('{Ctrl}{End}', waitTime=0.1)
        except Exception as e:
            pass
    else:
        print("Agent determined this is a new file. Proceeding to type...")
    
    print("Typing text...")
    try:
        editor = notepad.textbox()
        # Ensure focus is on the editor itself
        editor.focus()
        editor.type("Hello from Tarsier\nThis is a semantic automation test.")
    except Exception as e:
        print(f"Could not find textbox, typing on main window. Error: {e}")
        notepad.type("Hello from Tarsier\nThis is a semantic automation test.")
        
    time.sleep(1)
    
    print("Dumping UI State...")
    ui_state = notepad.to_json()
    print("\n--- UI State ---")
    print(ui_state)
    print("----------------\n")
    
    print("Done! Notepad should remain open for inspection.")

if __name__ == "__main__":
    main()
