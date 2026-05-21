import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tarsier import Desktop
from tarsier.core.web import WebDesktop

def main():
    print("=== Tarsier News Crawler & Notepad Sync Demo ===")
    
    # 1. Start browser to fetch news headlines (e.g. HN or similar public simple news site)
    print("\nLaunching browser to read news...")
    web = WebDesktop(headless=False, highlight_actions=True)
    
    headlines = []
    try:
        page = web.goto("https://news.ycombinator.com/")
        time.sleep(2)
        
        print("Scraping headlines from Hacker News...")
        # Get the titles
        for idx in range(1, 6):
            try:
                # Use robust Playwright nth selector matching the idx-th headline link
                title_el = page.find(selector=f"span.titleline > a >> nth={idx-1}")
                title_text = title_el.read()
                if title_text:
                    headlines.append(f"{idx}. {title_text}")
                    print(f"OK: Found: {title_text}")
            except Exception as e:
                print(f"Failed to read headline {idx}: {e}")
                
        print("Scrolling browser down...")
        page.scroll_to_bottom()
        time.sleep(1.5)
    except Exception as e:
        print(f"Browser navigation/scraping failed: {e}")
    finally:
        web.close()
        
    if not headlines:
        print("No headlines were found. Using mock headlines instead.")
        headlines = [
            "1. Tarsier: The open-source Playwright for Desktop Apps",
            "2. Semantic desktop automation reduces VLM token usage by 70%",
            "3. Autonomous agents learn to use accessibility trees as semantic IR"
        ]
        
    # 2. Open Notepad and type the headlines
    print("\n[Part 2] Syncing headlines to Notepad...")
    try:
        desktop = Desktop(highlight_actions=True)
        notepad = desktop.open_app("notepad.exe", regex_name="(?i).*Notepad.*")
        notepad.focus()
        time.sleep(1)
        
        editor = notepad.textbox()
        text_content = "=== Hacker News Top Stories ===\n" + "\n".join(headlines)
        editor.type(text_content)
        print("OK: Headlines successfully typed into Notepad!")
    except Exception as e:
        print(f"Failed to type in Notepad: {e}")
        
    print("\nDemo completed!")

if __name__ == "__main__":
    main()