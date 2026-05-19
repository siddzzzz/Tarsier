import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier.core.web import WebDesktop

def main():
    print("=== Tarsier E-commerce Web Automation Demo ===")
    
    # We will use a mock sandbox or a simple public demo site (e.g. letskodeit or internet-herokupp)
    # Let's use a standard public practice sandbox
    print("Launching Chromium browser...")
    web = WebDesktop(headless=False, highlight_actions=True)
    
    try:
        print("Navigating to Sandbox Store...")
        page = web.goto("https://the-internet.herokuapp.com/login")
        time.sleep(2)
        
        print("Locating Username textbox...")
        username = page.textbox(name="") # Or using general textbox finder
        # Since herokuapp login doesn't have ARIA label, let's find it by role or selector
        username = page.find(selector="#username")
        username.type("tomsmith")
        time.sleep(1)
        
        print("Locating Password textbox...")
        password = page.find(selector="#password")
        password.type("SuperSecretPassword!")
        time.sleep(1)
        
        print("Clicking Login button...")
        login_btn = page.find(selector="button[type='submit']")
        login_btn.click()
        time.sleep(3)
        
        current_page = web.get_current_page()
        print(f"Current page title: {current_page.name}")
        
        print("Verifying successful login...")
        flash_msg = current_page.find(selector="#flash")
        print(f"Flash Message: {flash_msg.read().strip()}")
        
        print("Done!")
    finally:
        print("Closing browser...")
        web.close()

if __name__ == "__main__":
    main()