import sys
import os
import time
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
import uiautomation as auto

def get_chrome_path():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"

def main():
    print("=== Tarsier Google Chrome Native YouTube Demo ===")
    
    chrome_path = get_chrome_path()
    if not os.path.exists(chrome_path):
        print(f"Warning: Chrome not found at standard path. Will try launching '{chrome_path}' directly...")
        
    # Use a custom user data directory to ensure we launch a fresh, independent Chrome process
    # with renderer accessibility enabled
    user_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chrome_temp"))
    os.makedirs(user_data_dir, exist_ok=True)
    print(f"Isolated User Data Directory: {user_data_dir}")
    
    # Initialize desktop automation
    desktop = Desktop(highlight_actions=True)
    
    # Launch Chrome
    print("Launching Google Chrome with accessibility enabled...")
    args = [
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        "--force-renderer-accessibility",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        "https://www.youtube.com"
    ]
    
    try:
        subprocess.Popen(args)
    except Exception as e:
        print(f"Failed to launch Chrome: {e}. Trying simple launch...")
        subprocess.Popen([chrome_path, "https://www.youtube.com"])
        
    print("Waiting for Google Chrome window to appear...")
    chrome = desktop.wait_for_window(regex_name="(?i).*Google Chrome.*", timeout=15)
    chrome.focus()
    
    # Maximize if not maximized already
    print("Maximizing Chrome window...")
    try:
        # Check visual state, if not maximized, maximize
        pattern = chrome._control.GetWindowPattern()
        if pattern and pattern.CurrentWindowVisualState != 1: # 1 = Maximized
            pattern.SetWindowVisualState(1)
    except Exception:
        pass
        
    print("Waiting 8 seconds for YouTube page to render...")
    time.sleep(8)
    
    try:
        # Check for cookie consent overlay inside Chrome window
        print("Checking for cookie consent buttons...")
        consent_btn = None
        for name_candidate in ["Accept all", "Accept", "I agree", "Agree"]:
            try:
                # Find inside the Chrome window tree
                btn = chrome.find(role="button", name=name_candidate)
                consent_btn = btn
                break
            except Exception:
                pass
                
        if consent_btn:
            print(f"Clicking cookie consent button: '{consent_btn.name}'...")
            consent_btn.click()
            time.sleep(3)
        else:
            print("No cookie consent button found or already accepted.")
            
        # Find the search box
        print("Locating search combobox...")
        search_box = chrome.wait_for_element(role="combobox", name="Search", timeout=15)
        
        # Click search box to focus and show cursor movement
        print("Moving cursor and clicking search box...")
        search_box.click()
        time.sleep(1)
        
        # Type the search term
        print("Typing search query...")
        search_box.type("Never Gonna Give You Up Rick Astley")
        time.sleep(1.5)
        
        # Submit the search via Enter key
        print("Pressing Enter to perform search...")
        desktop.hotkey("{Enter}")
        time.sleep(5)
        
        # Find the video link. Use regex to match the video title link
        print("Locating video link in search results...")
        video_link = chrome.wait_for_element(role="link", regex_name="(?i).*Never Gonna Give You Up.*", timeout=15)
        
        # Click the video link
        print(f"Moving cursor and clicking video: '{video_link.name}'...")
        video_link.click()
        
        print("\nPlaying music for 20 seconds...")
        for seconds in range(20, 0, -5):
            print(f"  {seconds} seconds remaining...")
            time.sleep(5)
            
        print("\nFinished playing! Closing Google Chrome...")
        chrome.focus()
        desktop.hotkey("{Alt}{F4}")
        time.sleep(1)
        
    except Exception as e:
        print(f"Error during Chrome YouTube playback: {e}")
        print("Closing Chrome...")
        try:
            chrome.focus()
            desktop.hotkey("{Alt}{F4}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
