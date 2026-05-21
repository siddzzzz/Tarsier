import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier Notepad Automation Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    print("Opening Notepad...")
    notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
    print(f"Attached to window: {notepad.name}")
    
    notepad.focus()
    time.sleep(1)
    
    print("Typing text...")
    try:
        editor = notepad.textbox()
        editor.type("Hello from Tarsier!\nThis is a semantic automation test.")
    except Exception as e:
        print(f"Error typing: {e}")
        
    print("Saving the file...")
    try:
        notepad.focus()
        import uiautomation as auto
        notepad._control.SendKeys('{Ctrl}{Shift}s')
        time.sleep(1.5)
        
        save_dialog_control = auto.WindowControl(searchDepth=1, RegexName="(?i).*Save.*", ClassName="#32770")
        if not save_dialog_control.Exists(10, 1):
            save_dialog_control = auto.WindowControl(RegexName="(?i).*Save.*", ClassName="#32770")
            
        from tarsier.core.elements import UIElement
        save_dialog = UIElement(save_dialog_control)
        
        try:
            file_name_box = save_dialog.textbox(name="File name:")
        except Exception:
            try:
                file_name_box = save_dialog.textbox(name="File name")
            except Exception:
                file_name_box = save_dialog.textbox()
                
        file_name_box.type("tarsier_demo.txt")
        time.sleep(0.5)
        
        save_button = save_dialog.button("Save")
        save_button.click()
        time.sleep(1)
        
        # Check for standard overwrite confirm dialog box
        confirm_dialog = auto.WindowControl(searchDepth=1, ClassName="#32770", RegexName="(?i).*Confirm.*")
        if not confirm_dialog.Exists(2, 0.5):
            confirm_dialog = auto.WindowControl(ClassName="#32770", RegexName="(?i).*Confirm.*")
            
        if confirm_dialog.Exists(1):
            yes_btn = auto.ButtonControl(searchFromControl=confirm_dialog, Name="Yes")
            if yes_btn.Exists(1):
                yes_btn.Click()
                print("Overwrite confirmed.")
            
        print("Saved successfully!")
    except Exception as e:
        print(f"Error saving: {e}")
        
    print("Done!")

if __name__ == "__main__":
    main()