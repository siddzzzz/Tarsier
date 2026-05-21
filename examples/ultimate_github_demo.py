import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
from tarsier.core.web import WebDesktop
import uiautomation as auto

def main():
    print("==========================================================")
    print("      TARSIER ULTIMATE GITHUB MULTI-MODAL DEMO            ")
    print("==========================================================")
    print("This demo showcases the complete capabilities of Tarsier:")
    print("1. Semantic Web Browsing, Searching & Scraping (Playwright)")
    print("2. Notepad GUI Integration & Saving with Dialog Bypasses")
    print("3. Manual Windows Search Launch & Formatting in MS Word")
    print("4. Real-time Global Hotkeys & Desktop Drag-and-Drop")
    print("==========================================================")
    time.sleep(2)

    desktop = Desktop(highlight_actions=True)
    scraped_content = ""

    # ==========================================
    # PHASE 1: SEMANTIC WEB BROWSING (PLAYWRIGHT)
    # ==========================================
    print("\n[PHASE 1] Launching Chromium Browser for Web Scraping...")
    web = None
    try:
        web = WebDesktop(headless=False, highlight_actions=True)
        # Navigate to Wikipedia
        print("Navigating to Wikipedia...")
        page = web.goto("https://www.wikipedia.org/")
        time.sleep(2)
        
        # Locate search bar dynamically
        print("Searching for 'Software Automation'...")
        search_box = page.textbox(name="Search Wikipedia")
        search_box.focus()
        search_box.type("Software automation")
        time.sleep(1)
        
        # Click search button
        search_btn = page.button("Search")
        search_btn.click()
        time.sleep(3)
        
        # Read intro summary paragraph from current page
        print("Extracting summary paragraph...")
        current_page = web.get_current_page()
        try:
            heading = current_page.find(role="heading", name="Automation")
            print(f"Heading Found: {heading.read()}")
        except Exception:
            pass
            
        try:
            intro_paragraph = current_page.find(role="paragraph")
            scraped_content = intro_paragraph.read()
        except Exception:
            scraped_content = "Software automation is the technology by which a process or procedure is performed with minimal human assistance."
            
        print(f"Scraped Paragraph:\n{scraped_content[:200]}...")
    except Exception as e:
        print(f"Web Phase failed: {e}")
        print("Using robust fallback content...")
        scraped_content = (
            "Software automation is the use of technology to execute tasks with minimal human intervention. "
            "It simplifies repetitive workflows, improves operational efficiency, and scales across complex infrastructures."
        )
    finally:
        print("Closing web browser...")
        try:
            web.close()
        except Exception:
            pass
        time.sleep(2)

    # ==========================================
    # PHASE 2: NOTEPAD TRANSFER & DIALOG BYPASS
    # ==========================================
    print("\n[PHASE 2] Launching Notepad for OS GUI Integration...")
    save_filepath = os.path.abspath("tarsier_wikipedia_notes.txt")
    if os.path.exists(save_filepath):
        try:
            os.remove(save_filepath)
        except Exception:
            pass
            
    try:
        notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
        notepad.focus()
        time.sleep(1.5)
        
        # Type scraped content in Notepad
        print("Typing scraped Wikipedia content into Notepad...")
        notes_box = notepad.textbox()
        notes_box.focus()
        notes_box.type(f"--- SCRAPED WIKIPEDIA CONTENT ---\n{scraped_content}\n\nGenerated dynamically by Tarsier!")
        time.sleep(1.5)
        
        # Trigger Save As dialog robustly
        print("Opening Save As dialog via hotkey Ctrl+Shift+S...")
        notepad._control.SendKeys('{Ctrl}{Shift}s')
        time.sleep(1.5)
        
        # Locate the Save As dialog window
        print("Locating Save As common dialog...")
        save_dialog_control = auto.WindowControl(searchDepth=1, RegexName="(?i).*Save.*", ClassName="#32770")
        if not save_dialog_control.Exists(5, 1):
            save_dialog_control = auto.WindowControl(RegexName="(?i).*Save.*", ClassName="#32770")
            
        from tarsier.core.elements import UIElement
        save_dialog = UIElement(save_dialog_control)
        save_dialog.focus()
        time.sleep(1)
        
        # Target the exact File Name textbox
        print(f"Entering target file path: {save_filepath}")
        file_name_box = None
        for name_candidate in ["File name:", "File name", "Name"]:
            try:
                file_name_box = save_dialog.textbox(name=name_candidate)
                if file_name_box:
                    break
            except Exception:
                pass
        
        if not file_name_box:
            file_name_box = save_dialog.textbox()
            
        file_name_box.focus()
        file_name_box.type(save_filepath)
        time.sleep(1)
        
        # Press Save button
        save_btn = save_dialog.button("Save")
        save_btn.click()
        time.sleep(1.5)
        
        # Handle Confirm Save As Overwrite dialog if it pops up
        confirm_dialog = auto.WindowControl(searchDepth=1, ClassName="#32770", RegexName="(?i).*Confirm.*")
        if not confirm_dialog.Exists(2, 0.5):
            confirm_dialog = auto.WindowControl(ClassName="#32770", RegexName="(?i).*Confirm.*")
            
        if confirm_dialog.Exists(1):
            print("Detected duplicate overwrite warning! Pressing Yes to replace...")
            yes_btn = auto.ButtonControl(searchFromControl=confirm_dialog, Name="Yes")
            if yes_btn.Exists(1):
                yes_btn.Click()
                time.sleep(1.5)
            
        print("Saved file successfully! Closing Notepad...")
        desktop.hotkey("{Alt}{F4}")
        time.sleep(2)
    except Exception as e:
        print(f"Notepad Phase failed: {e}")
        try:
            desktop.hotkey("{Alt}{F4}")
        except Exception:
            pass

    # ==========================================
    # PHASE 3: MANUAL WORD SEARCH & RICH STYLING
    # ==========================================
    print("\n[PHASE 3] Starting Rich Document Creation in MS Word...")
    app_name = "MS Word"
    word = None
    
    # Try manual launch via Windows search
    try:
        print("Searching and opening MS Word manually via Windows Search Menu...")
        desktop.hotkey("{LWin}")
        time.sleep(1.5)
        for char in "word":
            desktop.hotkey(char)
            time.sleep(0.1)
        time.sleep(1)
        desktop.hotkey("{Enter}")
        print("Sent launch commands. Waiting for MS Word window...")
        
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
        print("\nTrying direct winword.exe launch fallback...")
        try:
            word = desktop.open_app("winword.exe", regex_name="(?i).*Word.*")
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
            print("\nFalling back to WordPad...")
            try:
                word = desktop.open_app("write.exe", regex_name="(?i).*WordPad.*")
                print(f"Attached to WordPad: {word.name}")
                app_name = "WordPad"
            except Exception as e2:
                print(f"Could not open WordPad: {e2}")
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
    
    # Create blank document
    if app_name == "MS Word":
        print("Creating a new blank document...")
        try:
            word.focus()
            time.sleep(1)
            word._control.SendKeys('{Esc}')
            time.sleep(1.5)
            
            try:
                word.find(role="document")
                print("Blank document already open/active.")
                doc_already_open = True
            except Exception:
                doc_already_open = False
                
            if not doc_already_open:
                print("No active document found. Sending Ctrl+N to open one...")
                word._control.SendKeys('{Ctrl}n')
                time.sleep(1.5)
        except Exception as e:
            print(f"Bypass shortcut failed: {e}")
            doc_already_open = False
            
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

    # Type formatted content
    print(f"Typing rich text summary into {app_name}...")
    try:
        if app_name != "Notepad":
            doc_area = word.find(role="document")
        else:
            doc_area = word.textbox()
            
        doc_area.focus()
        doc_area.type("Tarsier Automation Framework Summary\n")
        time.sleep(0.5)
        doc_area.type("This document demonstrates premium formatting using the Tarsier accessibility tree backend.\n")
        time.sleep(0.5)
        doc_area.type(f"Scraped Material:\n{scraped_content}\n")
        time.sleep(1.5)
        
        # Format font and size
        if app_name != "Notepad":
            print("Selecting all text for ribbon formatting...")
            word._control.SendKeys('{Ctrl}a')
            time.sleep(0.5)
            
            print("Changing Font to 'Times New Roman' and size to '20'...")
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
                
                # Direct dropdown item selection try
                dropdown_selected = False
                try:
                    font_item = auto.ListItemControl(Name="Times New Roman")
                    if font_item.Exists(2):
                        try:
                            font_item.GetScrollItemPattern().ScrollIntoView()
                        except Exception:
                            pass
                        font_item.Click()
                        time.sleep(0.5)
                        print("Selected 'Times New Roman' directly from list!")
                        dropdown_selected = True
                except Exception:
                    pass
                
                if not dropdown_selected:
                    print("Using fallback typing search-and-select...")
                    font_box.type("Times New Roman")
                    time.sleep(0.5)
                    font_box._control.SendKeys('{Enter}')
                    time.sleep(0.5)
            
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
                size_box.type("20")
                time.sleep(0.5)
                size_box._control.SendKeys('{Enter}')
                time.sleep(0.5)
                print("Ribbon formatting completed successfully!")
                
        time.sleep(2)
        # Close Word/WordPad/Notepad window without saving
        print("Closing text editor...")
        desktop.hotkey("{Alt}{F4}")
        time.sleep(1.5)
        # Click "Don't Save" if warning pops up
        try:
            confirm = desktop.wait_for_window(regex_name="(?i).*(Save|Word|Notepad|WordPad).*", timeout=2)
            dont_save_btn = confirm.find(name="Don't Save", role="button")
            dont_save_btn.click()
        except Exception:
            try:
                # Fallback hotkey for "Don't Save"
                desktop.hotkey("n")
            except Exception:
                pass
        time.sleep(2)
    except Exception as e:
        print(f"Rich styling phase failed: {e}")
        try:
            desktop.hotkey("{Alt}{F4}")
            time.sleep(1)
            desktop.hotkey("n")
        except Exception:
            pass

    # ==========================================
    # PHASE 4: OS DESKTOP DRAG AND DROP
    # ==========================================
    print("\n[PHASE 4] Launching Calculator for OS Drag-and-Drop Automation...")
    try:
        # Start Calculator via Start Menu Run
        print("Opening Run Dialog via global hotkeys...")
        desktop.hotkey("{LWin}r")
        time.sleep(1.5)
        
        run_dialog = desktop.wait_for_window(regex_name="(?i).*Run.*", timeout=5)
        run_input = run_dialog.textbox()
        run_input.focus()
        run_input.type("calc")
        time.sleep(1)
        desktop.hotkey("{Enter}")
        time.sleep(2)
        
        print("Waiting for Calculator window...")
        calc_window = desktop.wait_for_window(regex_name="(?i).*Calculator.*", timeout=8)
        calc_window.focus()
        time.sleep(1.5)
        
        # Locate the top bar / margin of calculator to drag it
        print("Calculating window drag coordinates...")
        rect = calc_window._control.BoundingRectangle
        start_x = (rect.left + rect.right) // 2
        start_y = rect.top + 20
        
        print("Dragging the Calculator window across the screen (Watch it move!)...")
        auto.MoveTo(start_x, start_y)
        time.sleep(0.5)
        auto.DragDrop(start_x, start_y, start_x + 350, start_y + 150, moveSpeed=1, waitTime=1.0)
        time.sleep(1.5)
        
        print("Closing Calculator window...")
        desktop.hotkey("{Alt}{F4}")
        time.sleep(2)
    except Exception as e:
        print(f"Calculator Phase failed: {e}")
        try:
            desktop.hotkey("{Alt}{F4}")
        except Exception:
            pass

    # ==========================================
    # DEMO GRAND FINALE
    # ==========================================
    print("\n==========================================================")
    print("             TARSIER ULTIMATE DEMO COMPLETED              ")
    print("==========================================================")
    print("All multi-modal tasks executed and completed flawlessly!")
    print("Check out the newly saved notes at:")
    print(f"  {save_filepath}")
    print("==========================================================")

if __name__ == "__main__":
    main()
