import sys
import os
import platform

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    print("=== Tarsier Cross-Platform Abstraction Demo ===")
    
    current_os = platform.system()
    print(f"Current Operating System detected: {current_os}")
    
    print("Initializing Desktop session...")
    from tarsier import Desktop
    try:
        desktop = Desktop(highlight_actions=True)
        print(f"OK: Desktop initialized successfully on {current_os}.")
    except Exception as e:
        print(f"Failed to initialize Desktop: {e}")

    print("\nTarsier's unified API abstracts all platform-specific controls:")
    print("  - Desktop.open_app()")
    print("  - UIElement.click()")
    print("  - UIElement.type()")
    print("  - UIElement.to_json()")
    print("Allows a single LLM prompt loop to control Windows, macOS, or Linux natively!")

if __name__ == "__main__":
    main()