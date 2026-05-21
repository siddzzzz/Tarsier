import sys
import os
import time
import subprocess
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
from tarsier.core.elements import UIElement
import uiautomation as auto

def main():
    print("=== Tarsier VS Code Automation Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    print("Opening an empty VS Code window...")
    subprocess.Popen('code --new-window', shell=True)
    
    # Wait for VS Code to launch and find the window using Smart Waits
    try:
        vscode = desktop.wait_for_window(regex_name="(?i).*Visual Studio Code.*", timeout=15)
        print(f"Attached to VS Code window: {vscode.name}")
    except TimeoutError:
        print("Could not find VS Code window within timeout.")
        return
        
    # Wait for VS Code to be fully loaded before sending keys
    time.sleep(3)
    
    dialog_control = None
    for attempt in range(3):
        print(f"Triggering 'Open Folder' dialog via shortcut (attempt {attempt + 1})...")
        vscode.focus()
        time.sleep(0.5)
        vscode._control.SendKeys('{Ctrl}k{Ctrl}o')
        time.sleep(2)
        
        # Locate standard open dialog box by ClassName
        dialog_control = auto.WindowControl(searchDepth=1, ClassName="#32770")
        if not dialog_control.Exists(3, 0.5):
            dialog_control = auto.WindowControl(ClassName="#32770")
            
        if dialog_control.Exists(1):
            break
            
    if dialog_control and dialog_control.Exists(1):
        dialog = UIElement(dialog_control, highlight_actions=True)
        print("Folder dialog opened successfully.")
        
        # Create a new folder inside the dialog using hotkey
        folder_name = f"tarsier_test_{random.randint(100, 999)}"
        print(f"Creating new folder: {folder_name}")
        dialog_control.SendKeys('{Ctrl}{Shift}n')
        time.sleep(1)
        
        # Type folder name and hit Enter to select/rename it
        dialog_control.SendKeys(folder_name + '{Enter}')
        time.sleep(1)
        dialog_control.SendKeys('{Enter}') # Enter into folder
        time.sleep(1)
        
        # Click Select Folder
        try:
            dialog.button("Select Folder").click()
        except Exception:
            try:
                dialog.button("Select folder").click()
            except Exception:
                try:
                    dialog.button("Open").click()
                except Exception:
                    # Fallback: send Enter key to select active folder
                    dialog_control.SendKeys('{Enter}')
        print("Selected folder and loading workspace...")
        time.sleep(5) # Let VS Code reload
    else:
        print("Failed to locate Open Folder dialog.")
        return

    # Find the reloaded VS Code window
    try:
        vscode = desktop.wait_for_window(regex_name="(?i).*Visual Studio Code.*", timeout=15)
        vscode.focus()
    except TimeoutError:
        print("Could not find reloaded VS Code window.")
        return

    print("Creating a new Python file...")
    vscode._control.SendKeys('{Ctrl}n')
    time.sleep(1)
    
    print("Typing Python code...")
    vscode.type("print('Hello from Tarsier!')\nprint('This Python script was written and executed by a semantic desktop agent.')")
    time.sleep(1)
    
    print("Saving file...")
    vscode._control.SendKeys('{Ctrl}s')
    time.sleep(1.5)
    
    save_dialog_control = auto.WindowControl(searchDepth=1, RegexName="(?i).*Save.*", ClassName="#32770")
    if save_dialog_control.Exists(3):
        save_dialog = UIElement(save_dialog_control, highlight_actions=True)
        save_dialog.textbox().type("tarsier_test.py")
        save_dialog.button("Save").click()
        time.sleep(1)
        
    print("Opening VS Code integrated terminal...")
    vscode._control.SendKeys('{Ctrl}`')
    time.sleep(2)
    
    print("Running Python script in terminal...")
    vscode._control.SendKeys('python tarsier_test.py{Enter}')
    print("Done!")

if __name__ == "__main__":
    main()