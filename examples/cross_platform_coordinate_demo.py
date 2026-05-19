import sys
import os
import time

# Ensure Tarsier is in path for example script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier Cross-Platform Coordinate Demo ===")
    print(f"Running on OS platform: {sys.platform}")
    
    desktop = Desktop(highlight_actions=True)
    
    print("\nDemonstrating hotkeys:")
    try:
        # Example: Open task manager or Spotlight/search
        if sys.platform == 'win32':
            print("  Pressing Ctrl+Shift+Esc (Windows Task Manager)...")
            desktop.hotkey("{Ctrl}{Shift}{Esc}")
        elif sys.platform == 'darwin': # macOS
            print("  Pressing Cmd+Space (macOS Spotlight)...")
            desktop.hotkey("{command}space")
        else: # linux
            print("  Pressing Alt+F2 (Linux Run Dialog)...")
            desktop.hotkey("{alt}f2")
            
        time.sleep(2)
        
        print("  Pressing Esc to close...")
        desktop.hotkey("{Esc}")
    except Exception as e:
        print(f"Hotkey demo failed: {e}")
        
    print("\nDemonstrating Coordinate Drag & Drop (Mouse Movement):")
    try:
        # Move mouse across screen
        start_x, start_y = 100, 100
        end_x, end_y = 400, 400
        print(f"  Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
        desktop.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed=2)
        print("  Drag complete!")
    except Exception as e:
        print(f"Coordinate drag failed: {e}")
        
    print("\nDemonstrating Semantic Tool Guard (Should fail gracefully on Mac/Linux):")
    if sys.platform != 'win32':
        try:
            desktop.open_app("calculator")
            print("  Warning: open_app succeeded? It should have failed on non-Windows!")
        except NotImplementedError as e:
            print(f"  Success: Semantic automation properly guarded: {e}")
    else:
        print("  Running on Windows. Semantic tool guard bypassed.")

if __name__ == "__main__":
    main()
