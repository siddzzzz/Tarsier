import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
from tarsier.core.web import WebDesktop

def main():
    print("=== Tarsier Hybrid Desktop & Web Automation Demo ===")
    
    # 1. Desktop Automation (Calculator)
    print("\n[Part 1] Desktop Automation...")
    desktop = Desktop(highlight_actions=True)
    calc = desktop.open_app("calc.exe", window_name="Calculator")
    calc.focus()
    time.sleep(1)
    
    print("Performing semantic calculation: 5 * 5 = ...")
    calc.button("Five").click()
    calc.button("Multiply by").click()
    calc.button("Five").click()
    calc.button("Equals").click()
    time.sleep(1)
    
    # 2. Web Automation (Wikipedia)
    print("\n[Part 2] Web Automation...")
    web = WebDesktop(headless=False, highlight_actions=True)
    try:
        page = web.goto("https://www.wikipedia.org/")
        time.sleep(1)
        
        search_box = page.textbox(name="Search Wikipedia")
        search_box.type("Tarsier")
        time.sleep(1)
        
        search_button = page.button("Search")
        search_button.click()
        time.sleep(2)
        
        print("Tarsier search on Wikipedia finished successfully!")
    finally:
        web.close()
        
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()