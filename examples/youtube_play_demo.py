import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import WebDesktop

def main():
    print("=== Tarsier YouTube Player Demo ===")
    
    # Initialize headed browser
    print("Launching Chromium browser...")
    web = WebDesktop(headless=False, highlight_actions=True)
    
    try:
        # Navigate to YouTube
        print("Navigating to YouTube...")
        page = web.goto("https://www.youtube.com/")
        time.sleep(3)
        
        # Check for cookie consent button if present
        print("Checking for cookie consent overlays...")
        try:
            # Common YouTube consent buttons in different regions
            consent_btn = None
            for name_candidate in ["Accept all", "Accept", "I agree", "Agree"]:
                try:
                    btn = page.find(role="button", name=name_candidate)
                    if btn._locator.first.count() > 0:
                        consent_btn = btn
                        break
                except Exception:
                    pass
            if consent_btn:
                print(f"Clicking cookie consent button: '{consent_btn.read()}'...")
                consent_btn.click()
                time.sleep(3)
        except Exception as e:
            print(f"No consent overlay detected or bypass failed: {e}")
            
        # Locate search bar using robust waiting
        print("Locating search box...")
        search_box = page.wait_for_element(selector="input[name='search_query']", timeout=15)
        
        print("Typing search query...")
        search_box.focus()
        search_box.type("Never Gonna Give You Up Rick Astley")
        time.sleep(1.5)
        
        # Press Enter to perform search
        print("Pressing Enter to search...")
        search_box._locator.first.press("Enter")
        time.sleep(4)
        
        # Locate the first video result
        print("Locating video in search results...")
        video_link = page.wait_for_element(selector="a#video-title", timeout=15)
        
        print(f"Clicking video link: '{video_link.read().strip()}'...")
        video_link.click()
        
        # Let the music play!
        print("\nPlaying 'Never Gonna Give You Up' for 20 seconds...")
        for seconds in range(20, 0, -5):
            print(f"  {seconds} seconds remaining...")
            time.sleep(5)
            
        print("\nFinished playing!")
        
    except Exception as e:
        print(f"Error during YouTube playback demo: {e}")
    finally:
        print("Closing browser...")
        web.close()

if __name__ == "__main__":
    main()
