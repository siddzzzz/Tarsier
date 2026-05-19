import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import WebDesktop

def main():
    print("=== Tarsier Multi-Page / Tab Automation Demo ===")
    
    # Initialize headed browser
    print("Launching headed browser...")
    web = WebDesktop(headless=False, highlight_actions=True)
    
    try:
        # Tab 0: Wikipedia
        print("\n[Tab 0] Navigating to Wikipedia...")
        page0 = web.goto("https://www.wikipedia.org/")
        time.sleep(2)
        print(f"Tab 0 Title: {page0.page.title()}")
        
        # Open Tab 1: Hacker News
        print("\n[Tab 1] Opening new tab to Hacker News...")
        page1 = web.new_page("https://news.ycombinator.com/")
        time.sleep(2)
        print(f"Tab 1 Title: {page1.page.title()}")
        
        # Verify current active page is Hacker News
        current = web.get_current_page()
        print(f"Active Tab Title: {current.page.title()}")
        
        # Scraping some content from Hacker News
        print("\nScraping topmost article link from Hacker News (Tab 1)...")
        first_link = page1.find(role="link", selector=".titleline > a")
        print(f"Top HN Link Text: '{first_link.read()}'")
        
        # Switch back to Wikipedia (Tab 0)
        print("\nSwitching back to Tab 0 (Wikipedia)...")
        web.switch_to_page(0)
        time.sleep(1.5)
        
        # Interact with Wikipedia (Search)
        print("Searching for 'Open Source' on Wikipedia...")
        search_box = page0.textbox(name="Search Wikipedia")
        search_box.focus()
        search_box.type("Open source")
        time.sleep(1)
        
        search_btn = page0.button("Search")
        search_btn.click()
        time.sleep(2.5)
        
        # Verify we navigated
        page0_updated = web.get_current_page()
        print(f"Tab 0 New Title: {page0_updated.page.title()}")
        
        # Switch back to Hacker News (Tab 1)
        print("\nSwitching back to Tab 1 (Hacker News)...")
        web.switch_to_page(1)
        time.sleep(1.5)
        
        # Click on Hacker News New link
        print("Clicking 'new' stories link on Hacker News...")
        new_link = page1.find(role="link", name="new")
        new_link.click()
        time.sleep(2.5)
        
        page1_updated = web.get_current_page()
        print(f"Tab 1 New Title: {page1_updated.page.title()}")
        
        print("\nChecking all open pages:")
        for idx, page in enumerate(web.pages):
            print(f"  Tab [{idx}]: {page.page.title()}")
            
        print("\nAll multi-page/tab interactions completed successfully!")
    finally:
        print("\nClosing browser...")
        web.close()

if __name__ == "__main__":
    main()
