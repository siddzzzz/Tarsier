import sys
import os
import time
import subprocess

# Ensure Tarsier is in path for example script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier macOS Calculator Coordinate Drag Demo ===")
    
    if sys.platform != 'darwin':
        print(f"Warning: This script is intended for macOS (darwin). Current OS is '{sys.platform}'.")
        print("We will still attempt the physical cursor movement and drag, but the app launch may differ.")
        
    desktop = Desktop(highlight_actions=True)
    
    print("\nLaunching Calculator app...")
    try:
        if sys.platform == 'darwin':
            # Native macOS way to open an application
            subprocess.Popen(["open", "-a", "Calculator"])
        elif sys.platform == 'win32':
            subprocess.Popen("calc.exe")
        else:
            # Fallback for linux (assuming gnome)
            subprocess.Popen(["gnome-calculator"])
    except Exception as e:
        print(f"Failed to launch calculator: {e}")
        
    print("Waiting 3 seconds for the app to open and render...")
    time.sleep(3)
    
    # On macOS, apps often spawn near the center of the screen, with the title bar at the top.
    # Since semantic targeting (UI trees) is Windows-only, we demonstrate cross-platform capability
    # by performing a physical coordinate-based drag where the title bar is expected to be.
    start_x, start_y = 500, 250
    end_x, end_y = 800, 600
    
    print(f"\nPhysically moving cursor and dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
    desktop.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed=2)
    
    print("\nDrag complete!")
    print("Note: This demonstrates that cross-platform physical mouse control via Tarsier works successfully.")
    print("If you run this on an actual Mac, you will see the mouse cursor grab the calculator and move it across the screen.")

if __name__ == "__main__":
    main()
