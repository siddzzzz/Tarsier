import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier.core.web import WebDesktop

def main():
    print("=== Tarsier Web Browser Automation Demo ===")
    
    # Initialize WebDesktop with headless=False so the user can see it
    # and highlight_actions=True for flashing visual boxes on page elements
    print("Launching Chromium browser...")
    web = WebDesktop(headless=False, highlight_actions=True)
    
    try:
        print("Navigating to Wikipedia...")
        page = web.goto("https://www.wikipedia.org/")
        time.sleep(2)
        
        print("Finding Wikipedia search box...")
        # We can semantically query elements!
        search_box = page.textbox(name="Search Wikipedia")
        
        print("Typing 'Tarsier' into search box...")
        search_box.type("Tarsier")
        time.sleep(1)
        
        print("Submitting search...")
        # Find search button and click it
        search_button = page.button("Search")
        search_button.click()
        time.sleep(3)
        
        # Read search results title
        current_page = web.get_current_page()
        print(f"Current page title: {current_page.name}")
        
        print("Reading the first heading of the page...")
        heading = current_page.find(role="heading", name="Tarsier")
        print(f"Heading Text: {heading.read()}")
        
        print("Scrolling the page to the bottom...")
        current_page.scroll_to_bottom()
        time.sleep(2)
        
        print("Done!")
    finally:
        print("Closing browser...")
        web.close()

if __name__ == "__main__":
    main()