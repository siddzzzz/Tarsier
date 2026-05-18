import json
from typing import List, Dict, Any, Optional

class UIElement:
    def __init__(self, control, highlight_actions: bool = False):
        # control is a uiautomation.Control
        self._control = control
        self.highlight_actions = highlight_actions

    @property
    def name(self) -> str:
        return self._control.Name

    @property
    def role(self) -> str:
        return self._control.ControlTypeName

    def _highlight(self):
        """Draws a temporary red rectangle around the control on screen using Windows GDI."""
        if not getattr(self, 'highlight_actions', False):
            return
        try:
            rect = self._control.BoundingRectangle
            if rect.left >= rect.right or rect.top >= rect.bottom:
                return
                
            import ctypes
            import time
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            
            hdc = user32.GetDC(0)
            pen = gdi32.CreatePen(0, 4, 0x0000FF) # Red border, width 4
            old_pen = gdi32.SelectObject(hdc, pen)
            brush = gdi32.GetStockObject(5) # NULL_BRUSH
            old_brush = gdi32.SelectObject(hdc, brush)
            
            # Flash it a few times
            for _ in range(3):
                # Draw slightly inset to avoid being clipped by invisible UWP window borders
                gdi32.Rectangle(hdc, rect.left + 2, rect.top + 2, rect.right - 2, rect.bottom - 2)
                time.sleep(0.08)
                
            gdi32.SelectObject(hdc, old_pen)
            gdi32.SelectObject(hdc, old_brush)
            gdi32.DeleteObject(pen)
            user32.ReleaseDC(0, hdc)
            
            # Force the OS to repaint the screen to erase the red rectangle
            user32.InvalidateRect(None, None, True)
        except Exception:
            pass

    def click(self) -> 'UIElement':
        self._highlight()
        self._control.Click()
        return self
    
    def double_click(self) -> 'UIElement':
        self._highlight()
        self._control.DoubleClick()
        return self

    def focus(self) -> 'UIElement':
        self._highlight()
        self._control.SetFocus()
        return self

    def drag_to(self, target: 'UIElement', move_speed: int = 1, wait_time: float = 0.5) -> 'UIElement':
        """Drags the current element to the center of the target element."""
        import uiautomation as auto
        start_rect = self._control.BoundingRectangle
        end_rect = target._control.BoundingRectangle
        
        start_x = (start_rect.left + start_rect.right) // 2
        start_y = (start_rect.top + start_rect.bottom) // 2
        
        end_x = (end_rect.left + end_rect.right) // 2
        end_y = (end_rect.top + end_rect.bottom) // 2
        
        self._highlight()
        target._highlight()
        
        # Explicitly move the mouse to the start position so it's visually clear
        auto.MoveTo(start_x, start_y)
        import time
        time.sleep(0.5)
        
        auto.DragDrop(start_x, start_y, end_x, end_y, moveSpeed=move_speed, waitTime=wait_time)
        return self

    def move(self, x: int, y: int) -> 'UIElement':
        """Moves the window or element to physical screen coordinates."""
        if hasattr(self._control, 'GetTransformPattern'):
            pattern = self._control.GetTransformPattern()
            if pattern and pattern.CanMove:
                pattern.Move(x, y)
        return self

    def resize(self, width: int, height: int) -> 'UIElement':
        """Resizes the window or element."""
        if hasattr(self._control, 'GetTransformPattern'):
            pattern = self._control.GetTransformPattern()
            if pattern and pattern.CanResize:
                pattern.Resize(width, height)
        return self

    def maximize(self) -> 'UIElement':
        """Maximizes the window."""
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(1) # 1 = Maximized
        return self

    def minimize(self) -> 'UIElement':
        """Minimizes the window."""
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(2) # 2 = Minimized
        return self

    def restore(self) -> 'UIElement':
        """Restores the window to its normal state."""
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(0) # 0 = Normal
        return self

    def close(self) -> 'UIElement':
        """Closes the window."""
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.Close()
        return self

    def scroll_into_view(self) -> 'UIElement':
        """Scrolls the native Windows parent container until this element is visible."""
        try:
            # Try native UI Automation ScrollItemPattern
            pattern = self._control.GetScrollItemPattern()
            if pattern:
                pattern.ScrollIntoView()
                return self
        except Exception:
            pass
        
        # Fallback: In Windows, focusing an element forces the UI shell to scroll it into view!
        self.focus()
        return self

    def scroll_to_bottom(self) -> 'UIElement':
        """Scrolls to the bottom of the active document, pane, or container."""
        self.focus()
        # Sending Ctrl+End is the standard Windows gesture to jump to the absolute bottom of any scrollable area
        self._control.SendKeys('{Ctrl}{End}')
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'UIElement':
        # SendKeys types character-by-character, which can race and garble in modern UI like Win 11 Notepad.
        # A much more reliable method for semantic automation is pasting via clipboard or ValuePattern.
        import uiautomation as auto
        auto.SetClipboardText(text)
        self.focus()
        self._control.SendKeys('{Ctrl}v', waitTime=waitTime)
        return self

    def read(self) -> str:
        """Reads the text content of the element."""
        # Try ValuePattern first (standard for edit boxes)
        if hasattr(self._control, 'GetValuePattern'):
            pattern = self._control.GetValuePattern()
            if pattern:
                try:
                    return pattern.Value
                except Exception:
                    pass
                    
        # Try TextPattern next (used by complex documents)
        if hasattr(self._control, 'GetTextPattern'):
            pattern = self._control.GetTextPattern()
            if pattern:
                try:
                    return pattern.DocumentRange.GetText(-1)
                except Exception:
                    pass
        
        # Fallback to Name or WindowText
        text = self._control.GetWindowText()
        if not text:
            text = self.name
        return text

    def find(self, role: Optional[str] = None, name: Optional[str] = None) -> 'UIElement':
        # Simple recursive search
        kwargs = {}
        if name is not None:
            kwargs["Name"] = name
        if role is not None:
            # Need to map to uiautomation ControlType or use generic search
            # uiautomation uses specific classes like ButtonControl, etc.
            # But we can also use Control.GetChildren() and filter
            pass
            
        import uiautomation as auto
        search_control = auto.Control(searchFromControl=self._control, searchDepth=0xFFFFFFFF, **kwargs)
        if role:
             # Just an MVP simplification, filtering by name and returning first match if role matches, 
             # uiautomation's search handles Name easily. 
             # For a robust MVP we use the built in search:
             pass
        
        # Proper MVP search
        for child, depth, _ in auto.WalkTree(self._control, getChildren=lambda c: c.GetChildren(), includeTop=False):
            match = True
            if name is not None and child.Name != name:
                match = False
            if role is not None:
                # Basic role matching based on ControlTypeName (e.g. 'ButtonControl' -> 'button')
                if role.lower() not in child.ControlTypeName.lower():
                    match = False
            if match:
                return UIElement(child, highlight_actions=getattr(self, 'highlight_actions', False))
        
        raise ValueError(f"Element not found with name='{name}', role='{role}'")

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, timeout: int = 10) -> 'UIElement':
        """Polls the DOM until the specified element appears."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return self.find(role=role, name=name)
            except Exception: # Catch COM errors, ElementNotAvailable, and ValueError
                time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element with name='{name}', role='{role}' after {timeout} seconds")

    def wait_until_clickable(self, timeout: int = 10) -> 'UIElement':
        """Blocks until the element is enabled by the OS."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._control.IsEnabled:
                return self
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element to become clickable after {timeout} seconds")

    def button(self, name: str) -> 'UIElement':
        return self.find(role="button", name=name)

    def textbox(self, name: Optional[str] = None) -> 'UIElement':
        try:
            return self.find(role="document", name=name)
        except ValueError:
            return self.find(role="edit", name=name)
        
    def menu(self, name: str) -> 'UIElement':
        return self.find(role="menuitem", name=name)

    def dump_ui(self, max_depth: int = 2) -> Dict[str, Any]:
        return self._dump_recursive(self._control, 0, max_depth)
        
    def _dump_recursive(self, control, current_depth: int, max_depth: int) -> Dict[str, Any]:
        data = {
            "role": control.ControlTypeName.replace("Control", "").lower() or "unknown",
            "name": control.Name,
        }
        
        if current_depth < max_depth:
            children = control.GetChildren()
            if children:
                data["elements"] = [self._dump_recursive(c, current_depth + 1, max_depth) for c in children]
                
        return data

    def to_yaml_snapshot(self, max_depth: int = 5) -> str:
        """
        Dumps the UI tree into a Playwright ARIA snapshot compatible YAML string.
        This provides a highly token-efficient, unified standard for LLM agents.
        """
        lines = []
        self._to_yaml_recursive(self._control, 0, max_depth, lines)
        return "\n".join(lines)
        
    def _to_yaml_recursive(self, control, depth: int, max_depth: int, lines: List[str]):
        role = control.ControlTypeName.replace("Control", "").lower() or "unknown"
        name = control.Name
        
        # Format like aria snapshot: - role "name":
        indent = "  " * depth
        line = f"{indent}- {role}"
        if name:
            # Safely escape quotes in name
            safe_name = name.replace('"', '\\"')
            line += f' "{safe_name}"'
            
        children = control.GetChildren()
        
        # Don't add colon if no children are being processed
        if children and depth < max_depth:
            line += ":"
            lines.append(line)
            for child in children:
                self._to_yaml_recursive(child, depth + 1, max_depth, lines)
        else:
            lines.append(line)

    def to_json(self) -> str:
        return json.dumps(self.dump_ui(), indent=2)
