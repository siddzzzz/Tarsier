import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier Window Management Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    # Let's open two apps: Notepad and Calculator
    print("Opening Notepad...")
    notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
    notepad.focus()
    time.sleep(1)
    
    print("Opening Calculator...")
    calc = desktop.open_app("calc.exe", window_name="Calculator")
    calc.focus()
    time.sleep(1)
    
    print("\nDemonstrating Window Management APIs...")
    
    # 1. Read window dimensions
    try:
        notepad_rect = notepad._control.BoundingRectangle
        calc_rect = calc._control.BoundingRectangle
        print(f"Notepad position: {notepad_rect}")
        print(f"Calculator position: {calc_rect}")
    except Exception as e:
        print(f"Could not read positions: {e}")
        
    # 2. Focus Switching
    print("\nSwitching focus to Notepad...")
    notepad.focus()
    time.sleep(1.5)
    
    print("Switching focus back to Calculator...")
    calc.focus()
    time.sleep(1.5)
    
    # 3. Closing windows semantically
    print("\nCleaning up (Closing windows)...")
    try:
        print("Closing Calculator...")
        calc.button("Close Calculator").click()
    except Exception:
        # Fallback to general window close gesture
        desktop.hotkey("{Alt}({F4})")
        
    time.sleep(1)
    
    try:
        print("Closing Notepad...")
        notepad.focus()
        desktop.hotkey("{Alt}({F4})")
        
        # If Notepad asks to save, cancel or don't save
        import uiautomation as auto
        cancel_dialog = auto.WindowControl(searchDepth=2, Name="Notepad")
        if cancel_dialog.Exists(1):
            auto.ButtonControl(searchFromControl=cancel_dialog, Name="Don't Save").Click()
    except Exception:
        pass
        
    print("\nDemo completed!")

if __name__ == "__main__":
    main()