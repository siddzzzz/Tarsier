import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
import uiautomation as auto

def main():
    print("=== Tarsier Advanced Interaction Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    print("\n1. Opening Calculator...")
    calc = desktop.open_app("calc.exe", window_name="Calculator")
    calc.focus()
    time.sleep(1.5)
    
    # Showcase Hover
    print("\n2. Testing Hover (Hovering over Calculator buttons)...")
    try:
        # Hover over the 'Seven' button
        btn_seven = calc.button("Seven")
        print("Hovering over '7' button...")
        btn_seven.hover()
        time.sleep(1)
        
        # Hover over the 'Equals' button
        btn_equals = calc.button("Equals")
        print("Hovering over '=' button...")
        btn_equals.hover()
        time.sleep(1)
    except Exception as e:
        print(f"Hover failed: {e}")
        
    # Showcase Right Click
    print("\n3. Testing Right Click (Opening context menu)...")
    try:
        # Let's type some number first to show context menu on display
        calc.button("Nine").click()
        time.sleep(0.5)
        
        # Find the calculator results display (often role='text' or class 'CalculatorResults' or group)
        # In Win 11 Calculator, the results screen has name starting with "Result" or "Display is"
        # Let's try to search for the results group/text control
        display_el = None
        for child, _, _ in auto.WalkTree(calc._control, getChildren=lambda c: c.GetChildren(), includeTop=False):
            if "Result" in child.Name or "Display is" in child.Name:
                from tarsier.core.elements import UIElement
                display_el = UIElement(child, highlight_actions=True)
                break
                
        if display_el:
            print(f"Right-clicking display: '{display_el.name}' to open Copy context menu...")
            display_el.right_click()
            time.sleep(1.5)
            # Dismiss the context menu by clicking Escape
            desktop.hotkey("{Esc}")
            time.sleep(1)
        else:
            # Fallback right click on a button
            print("Display element not found. Right-clicking the 'Clear' button...")
            calc.find(name="Clear", role="button").right_click()
            time.sleep(1.5)
            desktop.hotkey("{Esc}")
            time.sleep(1)
    except Exception as e:
        print(f"Right click failed: {e}")
        
    # Showcase coordinate drag & drop
    print("\n4. Testing Coordinate-based Drag and Drop...")
    try:
        # Get bounding box of the Calculator window
        rect = calc._control.BoundingRectangle
        start_x = (rect.left + rect.right) // 2
        start_y = rect.top + 20
        
        end_x = start_x + 300
        end_y = start_y + 150
        
        print(f"Dragging Calculator titlebar from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
        desktop.drag_and_drop_coordinates(start_x, start_y, end_x, end_y)
        time.sleep(1.5)
    except Exception as e:
        print(f"Coordinate Drag failed: {e}")
        
    # Showcase cross-window / element-based drag & drop
    print("\n5. Testing Cross-Window / Element-based Drag and Drop...")
    try:
        # Let's open a Notepad window to drag the Calculator to, or drag inside calc
        print("Opening Notepad...")
        notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
        notepad.focus()
        time.sleep(1.5)
        
        # Target Notepad's main edit box/document area
        notepad_textbox = notepad.textbox()
        
        # Drag Calculator's "Seven" button to Notepad's textbox
        btn_seven = calc.button("Seven")
        
        print("Dragging Calculator's 'Seven' button to Notepad's edit area...")
        desktop.drag_and_drop(btn_seven, notepad_textbox)
        time.sleep(1.5)
        
        # Clean up Notepad window
        print("Closing Notepad...")
        notepad.focus()
        desktop.hotkey("{Alt}{F4}")
        time.sleep(1)
        
        # If Notepad save warning pops up, dismiss it
        try:
            confirm = desktop.wait_for_window(regex_name="(?i).*(Save|Notepad).*", timeout=1)
            confirm.find(name="Don't Save", role="button").click()
        except Exception:
            pass
            
    except Exception as e:
        print(f"Element Drag failed: {e}")
        
    # Close calculator
    print("Closing Calculator...")
    calc.focus()
    desktop.hotkey("{Alt}{F4}")
    time.sleep(1)
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
