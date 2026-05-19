import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def main():
    print("=== Tarsier Calculator Automation Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    print("Opening Calculator...")
    calc = desktop.open_app("calc.exe", window_name="Calculator")
    print(f"Attached to window: {calc.name}")
    calc.focus()
    time.sleep(1)
    
    print("Performing semantic calculation: 7 * 8 = ...")
    calc.button("Seven").click()
    calc.button("Multiply by").click()
    calc.button("Eight").click()
    calc.button("Equals").click()
    
    # Dump the UI state to show the result and the semantic tree
    try:
        print("Dumping UI State to see the semantic token-efficient YAML tree...")
        ui_state = calc.to_yaml_snapshot()
        print("\n--- Token-Efficient UI State (First 1000 chars) ---")
        safe_print_str = ui_state[:1000].encode('ascii', 'ignore').decode('ascii')
        print(safe_print_str + "\n...[truncated]...")
    except Exception as e:
        print(f"Error dumping UI state: {e}")

if __name__ == "__main__":
    main()