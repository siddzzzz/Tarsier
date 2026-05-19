import time
import os
import sys

# Ensure tarsier is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier Hotkey & Drag-and-Drop Demo ===")
    
    # Initialize desktop with visual highlighting so you can see the magic!
    desktop = Desktop(highlight_actions=True)
    
    print("\n1. Testing Global Hotkeys...")
    print("Sending 'Win + R' to open the Run dialog...")
    desktop.hotkey("{LWin}r")
    time.sleep(1)
    
    # The Run dialog is a system window. We can grab it semantically!
    run_dialog = desktop.wait_for_window(name="Run", timeout=5)
    print("Found Run dialog!")
    
    print("Typing 'calc' and pressing Enter using hotkeys...")
    # Select all existing text and type calc
    desktop.hotkey("calc{Enter}")
    
    print("\n2. Waiting for Calculator to open...")
    calc = desktop.wait_for_window(regex_name="(?i).*Calculator.*", timeout=5)
    time.sleep(1) # Let animations finish
    
    print("\n3. Testing Semantic Drag and Drop...")
    print("Finding the top margin of the Calculator (Title Bar)...")
    # To move a window, we must grab its top margin. 
    rect = calc._control.BoundingRectangle
    start_x = (rect.left + rect.right) // 2
    start_y = rect.top + 20 # 20 pixels down from the top
    
    print("Dragging the Calculator window across the screen (Watch it move!)...")
    import uiautomation as auto
    auto.MoveTo(start_x, start_y)
    time.sleep(0.5)
    auto.DragDrop(start_x, start_y, start_x + 400, start_y + 200, moveSpeed=1, waitTime=1.0)
    
    print("\n4. Cleaning up...")
    print("Closing the Calculator using the 'Close Calculator' button...")
    calc.button("Close Calculator").click()
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()