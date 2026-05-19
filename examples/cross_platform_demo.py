import sys
import os
import platform

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    print("=== Tarsier Cross-Platform Abstraction Demo ===")
    
    current_os = platform.system()
    print(f"Current Operating System detected: {current_os}")
    
    if current_os == "Windows":
        print("\nTarsier uses Windows UI Automation (UIA) as the underlying engine.")
        print("Initializing Desktop session...")
        from tarsier import Desktop
        desktop = Desktop()
        print("OK: Desktop initialized successfully on Windows.")
        
    elif current_os == "Darwin":
        print("\nTarsier macOS support utilizes the Apple Accessibility (AXAPI) layer.")
        print("[Note] macOS engine is currently in preview. Standard interface:")
        print("  - Desktop session uses PyObjC hooks.")
        
    elif current_os == "Linux":
        print("\nTarsier Linux support utilizes the AT-SPI layer.")
        print("[Note] Linux engine is currently in preview.")
        
    else:
        print(f"\nUnsupported operating system: {current_os}")

    print("\nTarsier's unified API abstracts all platform-specific controls:")
    print("  - Desktop.open_app()")
    print("  - UIElement.click()")
    print("  - UIElement.type()")
    print("  - UIElement.to_json()")
    print("Allows a single LLM prompt loop to control Windows, macOS, or Linux natively!")

if __name__ == "__main__":
    main()