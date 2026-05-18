import json
from typing import List, Dict, Any, Optional

class WebElement:
    def __init__(self, page, locator=None, role="document", name="", highlight_actions: bool = False):
        self.page = page
        self._locator = locator or page.locator("body")
        self._role = role
        self._name = name
        self.highlight_actions = highlight_actions

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self._role

    def _highlight(self):
        """Visually flashes the element on screen to help humans debug automation."""
        if not getattr(self, 'highlight_actions', False):
            return
            
        try:
            # Inject a red box shadow temporarily using Playwright evaluate
            locator = self._locator.first
            locator.evaluate("""el => {
                const oldShadow = el.style.boxShadow;
                const oldTransition = el.style.transition;
                el.style.transition = 'box-shadow 0.1s';
                el.style.boxShadow = '0 0 0 5px rgba(255, 0, 0, 0.8)';
                setTimeout(() => {
                    el.style.boxShadow = oldShadow;
                    el.style.transition = oldTransition;
                }, 400);
            }""")
            import time
            time.sleep(0.1) # brief pause to let human see it before action
        except Exception:
            pass

    def click(self) -> 'WebElement':
        self._highlight()
        self._locator.first.click()
        return self
    
    def double_click(self) -> 'WebElement':
        self._highlight()
        self._locator.first.dblclick()
        return self

    def focus(self) -> 'WebElement':
        self._highlight()
        self._locator.first.focus()
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'WebElement':
        self._highlight()
        locator = self._locator.first
        locator.fill(text)
        return self

    def read(self) -> str:
        return self._locator.first.inner_text()

    def scroll_into_view(self) -> 'WebElement':
        """Scrolls the browser window until this element is visible."""
        self._locator.first.scroll_into_view_if_needed()
        return self

    def scroll_to_bottom(self) -> 'WebElement':
        """Scrolls the browser window to the absolute bottom of the page."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return self

    def find(self, role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None, exact: bool = False) -> 'WebElement':
        loc = self._locator
        if selector:
            loc = loc.locator(selector)
        elif role and name:
            loc = loc.get_by_role(role, name=name, exact=exact)
        elif role:
            loc = loc.get_by_role(role)
        elif name:
            loc = loc.get_by_text(name, exact=exact)
            
        return WebElement(self.page, loc, role, name or selector, highlight_actions=self.highlight_actions)

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, selector: Optional[str] = None, timeout: int = 10) -> 'WebElement':
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                el = self.find(role=role, name=name, selector=selector)
                # Ensure it actually exists in the DOM
                if el._locator.first.count() > 0:
                    return el
            except Exception:
                pass
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for web element with name='{name}', role='{role}', selector='{selector}' after {timeout} seconds")

    def wait_until_clickable(self, timeout: int = 10) -> 'WebElement':
        self._locator.first.wait_for(state="visible", timeout=timeout*1000)
        return self

    def button(self, name: str) -> 'WebElement':
        return self.find(role="button", name=name)

    def textbox(self, name: Optional[str] = None) -> 'WebElement':
        tb = self.find(role="textbox", name=name)
        try:
            if tb._locator.first.count() > 0:
                return tb
        except Exception:
            pass
        return self.find(role="searchbox", name=name)
        
    def menu(self, name: str) -> 'WebElement':
        return self.find(role="menuitem", name=name)

    def dump_ui(self, max_depth: int = 5) -> Dict[str, Any]:
        """
        Returns a JSON structure representing the page state using ARIA snapshot.
        This provides a semantic view similar to the Desktop DOM.
        """
        try:
            snapshot = self.page.locator("body").aria_snapshot()
        except Exception:
            snapshot = ""
            
        return {
            "role": "document",
            "name": self.page.title(),
            "aria_snapshot": snapshot
        }

    def to_json(self) -> str:
        return json.dumps(self.dump_ui(), indent=2)


class WebDesktop:
    def __init__(self, headless: bool = False, highlight_actions: bool = False):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.highlight_actions = highlight_actions

    def goto(self, url: str) -> WebElement:
        self.page.goto(url)
        try:
            self.page.wait_for_load_state('networkidle', timeout=5000)
        except Exception:
            pass
        return WebElement(self.page, highlight_actions=self.highlight_actions)
        
    def get_current_page(self) -> WebElement:
        return WebElement(self.page, highlight_actions=self.highlight_actions)

    def close(self):
        self.browser.close()
        self._pw.stop()
