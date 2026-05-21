import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
import uiautomation as auto

def main():
    print("=== Tarsier MS Word Automation Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    print("Opening MS Word manually via Windows Search...")
    app_name = "MS Word"
    word = None
    
    # Phase 1: Try manual launch via Windows search
    try:
        desktop.hotkey("{LWin}")
        time.sleep(1.5)
        # Send characters to Start menu
        for char in "word":
            desktop.hotkey(char)
            time.sleep(0.1)
        time.sleep(1)
        desktop.hotkey("{Enter}")
        print("Sent launch commands. Waiting for MS Word window...")
        
        # Retry loop to robustly handle transient Windows 11 UIA COM lags/timeouts after Start Menu search
        word = None
        for attempt in range(3):
            try:
                word = desktop.wait_for_window(regex_name="(?i).*Word.*", timeout=8)
                break
            except Exception as wait_err:
                if attempt < 2:
                    print(f"Waiting for Word window lagged (attempt {attempt+1}/3). Retrying...")
                    time.sleep(2)
                else:
                    raise wait_err
        
        # Safely read window name to bypass splash transition races
        try:
            w_name = word.name
        except Exception:
            print("Word window busy or transitioning. Re-acquiring...")
            time.sleep(5)
            word = desktop.wait_for_window(regex_name="(?i).*Word.*", timeout=10)
            w_name = word.name
            
        if "opening" in w_name.lower():
            print("Caught splash screen. Waiting for main MS Word window to open...")
            time.sleep(6)
            for attempt in range(3):
                try:
                    word = desktop.wait_for_window(regex_name="(?i).*Word.*", timeout=10)
                    break
                except Exception:
                    time.sleep(2)
                    
        print(f"Attached to Word (Start Menu launch): {word.name}")
        app_name = "MS Word"
    except Exception as e:
        print(f"Start Menu launch failed: {e}")
        
        # Phase 2: Try direct winword.exe execution as direct fallback
        print("\nTrying direct winword.exe launch fallback...")
        try:
            word = desktop.open_app("winword.exe", regex_name="(?i).*Word.*")
            
            # Safely check splash screen for direct launch
            try:
                w_name = word.name
            except Exception:
                time.sleep(4)
                word = desktop.wait_for_window(regex_name="(?i).*Word.*", timeout=10)
                w_name = word.name
                
            if "opening" in w_name.lower():
                print("Caught splash screen. Waiting for main MS Word window to open...")
                time.sleep(6)
                word = desktop.wait_for_window(regex_name="(?i).*Word.*", timeout=10)
            print(f"Attached to Word (direct launch): {word.name}")
            app_name = "MS Word"
        except Exception as e_direct:
            print(f"Could not open MS Word directly: {e_direct}")
            
            # Phase 3: Try WordPad
            print("\nFalling back to WordPad...")
            try:
                word = desktop.open_app("write.exe", regex_name="(?i).*WordPad.*")
                print(f"Attached to WordPad: {word.name}")
                app_name = "WordPad"
            except Exception as e2:
                print(f"Could not open WordPad: {e2}")
                
                # Phase 4: Try Notepad
                print("\nFalling back to Notepad...")
                try:
                    word = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
                    print(f"Attached to Notepad: {word.name}")
                    app_name = "Notepad"
                except Exception as e3:
                    print(f"Could not open Notepad: {e3}")
                    print("All text processor fallbacks failed.")
                    return
                    
    word.focus()
    time.sleep(2)
    
    # Create a new document in MS Word
    if app_name == "MS Word":
        print("Creating a new blank document...")
        try:
            # Focus MS Word to receive keyboard events
            word.focus()
            time.sleep(1)
            
            # Escape the Start landing page or backstage view
            word._control.SendKeys('{Esc}')
            time.sleep(1.5)
            
            # Check if a document is already open/active (e.g. from the Escape key action)
            try:
                word.find(role="document")
                print("Blank document already open/active.")
                doc_already_open = True
            except Exception:
                doc_already_open = False
                
            if not doc_already_open:
                # Send Ctrl+N only if no blank document is open yet
                print("No active document found. Sending Ctrl+N to open a new one...")
                word._control.SendKeys('{Ctrl}n')
                time.sleep(1.5)
        except Exception as e:
            print(f"Bypass shortcut failed: {e}")
            doc_already_open = False
            
        # Supplementary UI click search (only if no blank document is open yet)
        if not doc_already_open:
            try:
                blank_doc = word.find(name="Blank document", role="button")
                blank_doc.click()
                time.sleep(2)
            except Exception:
                try:
                    blank_doc = word.find(name="Blank Document", role="button")
                    blank_doc.click()
                    time.sleep(2)
                except Exception:
                    pass
        
    print(f"Typing text into {app_name}...")
    try:
        # Enforce role="document" for MS Word & WordPad to completely avoid the top Search box (which has role="edit")
        if app_name != "Notepad":
            doc_area = word.find(role="document")
        else:
            doc_area = word.textbox()
            
        doc_area.focus()
        doc_area.type(f"Hello from Tarsier!\nThis is a semantically formatted document running inside {app_name}.")
        time.sleep(1)
        
        # Select all text to format it
        word._control.SendKeys('{Ctrl}a')
        time.sleep(0.5)
        
        if app_name != "Notepad":
            print("Changing Font to 'Times New Roman' and size to '20'...")
            # Try ribbon controls for Font and Font Size (supported in MS Word & WordPad)
            font_box = None
            for name_candidate in ["Font", "Font:", "Font Name", "Font name", "Font family", "Font Family", "Pick a font", "Pick a Font"]:
                try:
                    font_box = word.find(name=name_candidate, role="combobox")
                    if font_box:
                        break
                except Exception:
                    pass
            
            if font_box:
                font_box.click()
                time.sleep(1)
                
                # Robust listitem search and click directly from the dropdown popup
                dropdown_selected = False
                try:
                    import uiautomation as auto
                    # Search globally from Desktop root for the dropdown item
                    font_item = auto.ListItemControl(Name="Times New Roman")
                    if font_item.Exists(2):
                        # Scroll the item into view if it supports scrolling
                        try:
                            font_item.GetScrollItemPattern().ScrollIntoView()
                        except Exception:
                            pass
                        font_item.Click()
                        time.sleep(0.5)
                        print("Selected 'Times New Roman' directly from dropdown!")
                        dropdown_selected = True
                except Exception as select_err:
                    print(f"Direct dropdown selection failed: {select_err}")
                
                if not dropdown_selected:
                    # Scroll/typing fallback if UIA list selection fails
                    print("Using fallback typing search-and-select...")
                    font_box.type("Times New Roman")
                    time.sleep(0.5)
                    font_box._control.SendKeys('{Enter}')
                    time.sleep(0.5)
            else:
                print("Warning: Font family combobox not found in ribbon. Skipping.")
            
            size_box = None
            for name_candidate in ["Font size", "Font Size", "Size", "Size:", "Font size:", "Font Size:"]:
                try:
                    size_box = word.find(name=name_candidate, role="combobox")
                    if size_box:
                        break
                except Exception:
                    pass
            
            if size_box:
                size_box.click()
                time.sleep(0.5)
                # Type the font size "20"
                size_box.type("20")
                time.sleep(0.5)
                # Confirm font size change
                size_box._control.SendKeys('{Enter}')
                time.sleep(0.5)
                print("Formatting completed successfully!")
            else:
                print("Warning: Font size combobox not found in ribbon. Skipping.")
        else:
            print("Skipping font styling (Notepad fallback).")
            
        print("Demo completed successfully!")
    except Exception as e:
        print(f"Document interaction failed: {e}")

if __name__ == "__main__":
    main()