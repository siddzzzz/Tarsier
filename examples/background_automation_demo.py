import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    if sys.platform != 'win32':
        print("This demo is currently only supported on Windows.")
        sys.exit(0)

    print("=== Tarsier Background Automation Demo ===")
    print("This demo will show typing and clicking in Notepad without moving your mouse cursor.")
    print("Please keep your hands off the mouse during the demo to observe that it does not move!\n")
    
    desktop = Desktop(highlight_actions=True)
    
    print("[1/5] Opening Notepad...")
    notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
    print(f"Attached to window: '{notepad.name}'")
    time.sleep(1)
    
    print("\n[2/5] Typing text natively (via ValuePattern)...")
    try:
        editor = notepad.textbox()
        test_text = "Hello! This text was typed natively in the background without using keyboard emulation or clipboard copying."
        editor.type(test_text)
        print("Typing complete.")
    except Exception as e:
        print(f"Error typing: {e}")
        
    print("\n[3/5] Reading the typed text back natively...")
    try:
        read_text = editor.read()
        print(f"Successfully read back text from editor:\n--> \"{read_text}\"")
        if read_text == test_text:
            print("SUCCESS: Text matches perfectly!")
        else:
            print("WARNING: Text read back does not match typed text.")
    except Exception as e:
        print(f"Error reading: {e}")
        
    time.sleep(1.5)
    
    print("\n[4/5] Closing Notepad and handling the 'Save changes' dialog natively...")
    try:
        notepad.close()
        time.sleep(1)
        
        # Look for the Save confirmation dialog
        import uiautomation as auto
        confirm_dialog_control = auto.WindowControl(searchDepth=1, ClassName="#32770", RegexName="(?i).*Notepad.*")
        if not confirm_dialog_control.Exists(1, 0.5):
            confirm_dialog_control = auto.WindowControl(ClassName="#32770", RegexName="(?i).*Notepad.*")
            
        if confirm_dialog_control.Exists(1):
            print("Save dialog appeared. Clicking 'Don't Save' natively in background...")
            from tarsier.core.elements import UIElement
            confirm_dialog = UIElement(confirm_dialog_control)
            
            # Find the 'Don't Save' or 'No' button depending on Windows locale/version
            dont_save_btn = None
            try:
                dont_save_btn = confirm_dialog.button(name="Don't Save")
            except Exception:
                try:
                    dont_save_btn = confirm_dialog.button(name="No")
                except Exception:
                    dont_save_btn = confirm_dialog.button() # Fallback to first button
                    
            if dont_save_btn:
                dont_save_btn.click()
                print("Clicked 'Don't Save' natively.")
            else:
                print("Could not find 'Don't Save' button in the dialog.")
        else:
            print("No save dialog appeared.")
    except Exception as e:
        print(f"Error closing: {e}")
        
    print("\n[5/5] Done!")

if __name__ == "__main__":
    main()
