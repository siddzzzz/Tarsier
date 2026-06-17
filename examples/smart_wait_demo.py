import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    if sys.platform != 'win32':
        print("This demo is currently only supported on Windows.")
        sys.exit(0)

    print("=== Tarsier Smart Wait and State Syncing Demo ===")
    desktop = Desktop(highlight_actions=True)
    
    # 1. Asynchronous App launch to demonstrate wait_for_window
    print("[1/4] Starting Notepad in a background thread to demonstrate async wait...")
    
    def launch_notepad_delayed():
        time.sleep(2) # Delay launch by 2 seconds
        import subprocess
        subprocess.Popen("notepad.exe")
        
    threading.Thread(target=launch_notepad_delayed, daemon=True).start()
    
    print("Main thread is waiting for Notepad window to appear (timeout=10s)...")
    start = time.time()
    notepad = desktop.wait_for_window(regex_name="(?i).*Notepad.*", timeout=10)
    duration = time.time() - start
    print(f"Notepad found in {duration:.2f} seconds! Attached to window: '{notepad.name}'")
    
    # 2. Typing and demonstrating wait_until_text_contains
    print("\n[2/4] Typing text into Notepad...")
    editor = notepad.textbox()
    editor.type("This text contains the keyword 'Tarsier-Smart-Wait'.")
    
    print("Waiting for editor to contain keyword 'Tarsier-Smart-Wait'...")
    start = time.time()
    # This should resolve instantly since the text is already there, but validates the API
    editor.wait_until_text_contains("Tarsier-Smart-Wait", timeout=5)
    print(f"Resolved wait_until_text_contains in {time.time() - start:.4f} seconds.")
    
    # 3. Demonstrate wait_until_gone (Element self-destruction check)
    print("\n[3/4] Closing Notepad and waiting for it to exit...")
    notepad.close()
    
    import uiautomation as auto
    confirm_dialog_control = auto.WindowControl(searchDepth=1, ClassName="#32770", RegexName="(?i).*Notepad.*")
    if confirm_dialog_control.Exists(1.5, 0.5):
        from tarsier.core.elements import UIElement
        confirm_dialog = UIElement(confirm_dialog_control)
        
        dont_save_btn = None
        try:
            dont_save_btn = confirm_dialog.button(name="Don't Save")
        except Exception:
            try:
                dont_save_btn = confirm_dialog.button(name="No")
            except Exception:
                dont_save_btn = confirm_dialog.button()
                
        dont_save_btn.click()
        print("Clicked 'Don't Save' to exit Notepad.")
    else:
        print("No save dialog appeared.")
        
    # Wait until the Notepad window is fully closed (gone)
    print("Waiting for Notepad window to be fully closed (wait_until_gone)...")
    start = time.time()
    notepad.wait_until_gone(timeout=5)
    print(f"Notepad window disappeared in {time.time() - start:.2f} seconds!")
        
    print("\n[4/4] Done! Smart wait checks successfully verified.")

if __name__ == "__main__":
    main()
