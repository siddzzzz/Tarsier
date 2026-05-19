import sys
import os
import time

# Ensure Tarsier is in path for example script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop

def click_button_cross_platform(calc, name_win, name_mac):
    try:
        # Try Windows name
        calc.button(name_win).click()
        print(f"Clicked button: {name_win}")
    except ValueError:
        try:
            # Try macOS name
            calc.button(name_mac).click()
            print(f"Clicked button: {name_mac}")
        except ValueError:
            raise ValueError(f"Could not find button with name '{name_win}' or '{name_mac}'")

def main():
    print("=== Tarsier Cross-Platform Calculator Semantic Automation Demo ===")
    
    desktop = Desktop(highlight_actions=True)
    
    app_name = "calc.exe" if sys.platform == 'win32' else "Calculator"
    print(f"Opening {app_name}...")
    
    # open_app handles platform-specific launch and accessibility tree attachment
    calc = desktop.open_app(app_name, window_name="Calculator")
    print(f"Attached to window: {calc.name}")
    calc.focus()
    time.sleep(1)
    
    print("\nPerforming semantic calculation: 7 * 8 = ...")
    
    # Click 7
    click_button_cross_platform(calc, "Seven", "7")
    time.sleep(0.5)
    
    # Click Multiply
    click_button_cross_platform(calc, "Multiply by", "multiply")
    time.sleep(0.5)
    
    # Click 8
    click_button_cross_platform(calc, "Eight", "8")
    time.sleep(0.5)
    
    # Click Equals
    click_button_cross_platform(calc, "Equals", "equals")
    time.sleep(1)
    
    # Dump the UI state to show the result and the semantic tree
    try:
        print("\nDumping UI State to see the semantic token-efficient YAML tree...")
        ui_state = calc.to_yaml_snapshot(max_depth=3)
        print("\n--- Token-Efficient UI State (First 1000 chars) ---")
        safe_print_str = ui_state[:1000].encode('ascii', 'ignore').decode('ascii')
        print(safe_print_str + "\n...[truncated]...")
    except Exception as e:
        print(f"Error dumping UI state: {e}")

if __name__ == "__main__":
    main()