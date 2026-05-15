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
    
    print("Saving the file...")
    try:
        # Use Ctrl+Shift+S to force "Save As" even on existing files
        notepad.focus()
        import uiautomation as auto
        notepad._control.SendKeys('{Ctrl}{Shift}s')
        time.sleep(1.5) # Wait for the dialog to open
        
        # Find the Save As dialog globally using Regex to handle "Save as" vs "Save As"
        save_dialog_control = auto.WindowControl(RegexName="(?i).*Save.*", ClassName="#32770")
        if not save_dialog_control.Exists(3, 1):
            raise Exception("Save dialog did not appear. (Tried Ctrl+Shift+S)")
            
        from tarsier.core.elements import UIElement
        save_dialog = UIElement(save_dialog_control)
        
        # Find the filename edit box. In standard Windows dialogs, it has Name="File name:" 
        try:
            file_name_box = save_dialog.find(role="edit", name="File name:")
        except ValueError:
            # Fallback if the exact name isn't found
            file_name_box = save_dialog.find(role="edit")
            
        file_name_box.type("tarsier_demo.txt")
        time.sleep(0.5)
        
        # Find and click the Save button
        save_button = save_dialog.button("Save")
        save_button.click()
        
        print("Successfully saved as 'tarsier_demo.txt'!")
        
        # In case the file already exists, a Confirm Save As dialog appears
        time.sleep(0.5)
        try:
            confirm_dialog = save_dialog.find(name="Confirm Save As")
            if confirm_dialog:
                yes_button = confirm_dialog.button("Yes")
                yes_button.click()
                print("Overwrote existing file.")
        except Exception:
            pass # No confirmation dialog appeared
            
    except Exception as e:
        print(f"Could not complete the save process: {e}")
        
    print("Done! Notepad should remain open for inspection.")

if __name__ == "__main__":
    main()
