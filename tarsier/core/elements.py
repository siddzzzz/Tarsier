import json
import re
import sys
from typing import List, Dict, Any, Optional

ROLE_MAPPING = {
    # macOS
    "axstatictext": "text",
    "axtextfield": "textbox",
    "axtextarea": "textbox",
    "axbutton": "button",
    "axcheckbox": "checkbox",
    "axradiobutton": "radio",
    "axwindow": "window",
    "axmenuitem": "menuitem",
    "axmenubar": "menubar",
    "axgroup": "group",
    "aximage": "image",
    "axsheet": "window",
    "axdialog": "window",
    "axcombobox": "combobox",
    "axlink": "link",
    # Linux
    "push button": "button",
    "entry": "textbox",
    "text": "text",
    "label": "text",
    "check box": "checkbox",
    "radio button": "radio",
    "frame": "window",
    "combo box": "combobox",
    "hyperlink": "link",
}

class UIElementBackend:
    @property
    def name(self) -> str:
        raise NotImplementedError()
    @property
    def role(self) -> str:
        raise NotImplementedError()
    def click(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def double_click(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def right_click(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def hover(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def focus(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def drag_to(self, target: Any, move_speed: int = 1, wait_time: float = 0.5) -> 'UIElementBackend':
        raise NotImplementedError()
    def move(self, x: int, y: int) -> 'UIElementBackend':
        raise NotImplementedError()
    def resize(self, width: int, height: int) -> 'UIElementBackend':
        raise NotImplementedError()
    def maximize(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def minimize(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def restore(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def close(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def scroll_into_view(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def scroll_to_bottom(self) -> 'UIElementBackend':
        raise NotImplementedError()
    def type(self, text: str, waitTime: float = 0.05) -> 'UIElementBackend':
        raise NotImplementedError()
    def read(self) -> str:
        raise NotImplementedError()
    def find(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None) -> Any:
        raise NotImplementedError()
    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None, timeout: int = 10) -> Any:
        raise NotImplementedError()
    def wait_until_clickable(self, timeout: int = 10) -> 'UIElementBackend':
        raise NotImplementedError()
    def dump_ui(self, max_depth: int = 2) -> Dict[str, Any]:
        raise NotImplementedError()
    def to_yaml_snapshot(self, max_depth: int = 5) -> str:
        raise NotImplementedError()

class WindowsUIElement(UIElementBackend):
    def __init__(self, control, highlight_actions: bool = False):
        self._control = control
        self.highlight_actions = highlight_actions

    @property
    def name(self) -> str:
        return self._control.Name

    @property
    def role(self) -> str:
        return self._control.ControlTypeName

    def _highlight(self):
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
            pen = gdi32.CreatePen(0, 4, 0x0000FF)
            old_pen = gdi32.SelectObject(hdc, pen)
            brush = gdi32.GetStockObject(5)
            old_brush = gdi32.SelectObject(hdc, brush)
            
            for _ in range(3):
                gdi32.Rectangle(hdc, rect.left + 2, rect.top + 2, rect.right - 2, rect.bottom - 2)
                time.sleep(0.08)
                
            gdi32.SelectObject(hdc, old_pen)
            gdi32.SelectObject(hdc, old_brush)
            gdi32.DeleteObject(pen)
            user32.ReleaseDC(0, hdc)
            user32.InvalidateRect(None, None, True)
        except Exception:
            pass

    def click(self) -> 'WindowsUIElement':
        self._highlight()
        self._control.Click()
        return self
    
    def double_click(self) -> 'WindowsUIElement':
        self._highlight()
        self._control.DoubleClick()
        return self

    def right_click(self) -> 'WindowsUIElement':
        self._highlight()
        self._control.RightClick()
        return self

    def hover(self) -> 'WindowsUIElement':
        self._highlight()
        rect = self._control.BoundingRectangle
        x = (rect.left + rect.right) // 2
        y = (rect.top + rect.bottom) // 2
        import uiautomation as auto
        auto.MoveTo(x, y)
        return self

    def focus(self) -> 'WindowsUIElement':
        self._highlight()
        self._control.SetFocus()
        return self

    def drag_to(self, target: Any, move_speed: int = 1, wait_time: float = 0.5) -> 'WindowsUIElement':
        import uiautomation as auto
        import time
        start_rect = self._control.BoundingRectangle
        end_rect = target._backend._control.BoundingRectangle
        
        start_x = (start_rect.left + start_rect.right) // 2
        start_y = (start_rect.top + start_rect.bottom) // 2
        
        end_x = (end_rect.left + end_rect.right) // 2
        end_y = (end_rect.top + end_rect.bottom) // 2
        
        self._highlight()
        target._backend._highlight()
        
        auto.MoveTo(start_x, start_y)
        time.sleep(0.5)
        
        auto.DragDrop(start_x, start_y, end_x, end_y, moveSpeed=move_speed, waitTime=wait_time)
        return self

    def move(self, x: int, y: int) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetTransformPattern'):
            pattern = self._control.GetTransformPattern()
            if pattern and pattern.CanMove:
                pattern.Move(x, y)
        return self

    def resize(self, width: int, height: int) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetTransformPattern'):
            pattern = self._control.GetTransformPattern()
            if pattern and pattern.CanResize:
                pattern.Resize(width, height)
        return self

    def maximize(self) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(1)
        return self

    def minimize(self) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(2)
        return self

    def restore(self) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.SetWindowVisualState(0)
        return self

    def close(self) -> 'WindowsUIElement':
        if hasattr(self._control, 'GetWindowPattern'):
            pattern = self._control.GetWindowPattern()
            if pattern:
                pattern.Close()
        return self

    def scroll_into_view(self) -> 'WindowsUIElement':
        try:
            pattern = self._control.GetScrollItemPattern()
            if pattern:
                pattern.ScrollIntoView()
                return self
        except Exception:
            pass
        self.focus()
        return self

    def scroll_to_bottom(self) -> 'WindowsUIElement':
        self.focus()
        self._control.SendKeys('{Ctrl}{End}')
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'WindowsUIElement':
        import uiautomation as auto
        auto.SetClipboardText(text)
        self.focus()
        self._control.SendKeys('{Ctrl}v', waitTime=waitTime)
        return self

    def read(self) -> str:
        if hasattr(self._control, 'GetValuePattern'):
            pattern = self._control.GetValuePattern()
            if pattern:
                try:
                    return pattern.Value
                except Exception:
                    pass
                    
        if hasattr(self._control, 'GetTextPattern'):
            pattern = self._control.GetTextPattern()
            if pattern:
                try:
                    return pattern.DocumentRange.GetText(-1)
                except Exception:
                    pass
        
        text = self._control.GetWindowText()
        if not text:
            text = self.name
        return text

    def find(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None) -> Any:
        import uiautomation as auto
        for child, depth, _ in auto.WalkTree(self._control, getChildren=lambda c: c.GetChildren(), includeTop=False):
            match = True
            if name is not None and child.Name != name:
                match = False
            if regex_name is not None:
                if not child.Name or not re.match(regex_name, child.Name):
                    match = False
            if role is not None:
                r = role.lower()
                if r == "textbox":
                    if "edit" not in child.ControlTypeName.lower() and "document" not in child.ControlTypeName.lower():
                        match = False
                else:
                    if r not in child.ControlTypeName.lower():
                        match = False
            if match:
                return UIElement(child, highlight_actions=getattr(self, 'highlight_actions', False))
        
        raise ValueError(f"Element not found with name='{name}', regex_name='{regex_name}', role='{role}'")

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None, timeout: int = 10) -> Any:
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return self.find(role=role, name=name, regex_name=regex_name)
            except Exception:
                time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element with name='{name}', regex_name='{regex_name}', role='{role}' after {timeout} seconds")

    def wait_until_clickable(self, timeout: int = 10) -> 'WindowsUIElement':
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._control.IsEnabled:
                return self
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element to become clickable after {timeout} seconds")

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
        lines = []
        self._to_yaml_recursive(self._control, 0, max_depth, lines)
        return "\n".join(lines)
        
    def _to_yaml_recursive(self, control, depth: int, max_depth: int, lines: List[str]):
        role = control.ControlTypeName.replace("Control", "").lower() or "unknown"
        name = control.Name
        
        indent = "  " * depth
        line = f"{indent}- {role}"
        if name:
            safe_name = name.replace('"', '\\"')
            line += f' "{safe_name}"'
            
        children = control.GetChildren()
        if children and depth < max_depth:
            line += ":"
            lines.append(line)
            for child in children:
                self._to_yaml_recursive(child, depth + 1, max_depth, lines)
        else:
            lines.append(line)

class MacUIElement(UIElementBackend):
    def __init__(self, control, highlight_actions: bool = False):
        self._control = control
        self.highlight_actions = highlight_actions

    @property
    def name(self) -> str:
        return getattr(self._control, 'AXTitle', "") or getattr(self._control, 'AXDescription', "") or ""

    @property
    def role(self) -> str:
        el_role = getattr(self._control, 'AXRole', "unknown")
        return ROLE_MAPPING.get(el_role.lower(), el_role.replace("AX", "").lower())

    def click(self) -> 'MacUIElement':
        try:
            self._control.press()
        except Exception:
            self.hover()
            import pyautogui
            pyautogui.click()
        return self

    def double_click(self) -> 'MacUIElement':
        self.hover()
        import pyautogui
        pyautogui.doubleClick()
        return self

    def right_click(self) -> 'MacUIElement':
        self.hover()
        import pyautogui
        pyautogui.rightClick()
        return self

    def hover(self) -> 'MacUIElement':
        pos = self._control.AXPosition
        size = self._control.AXSize
        x = pos[0] + size[0] // 2
        y = pos[1] + size[1] // 2
        import pyautogui
        pyautogui.moveTo(x, y)
        return self

    def focus(self) -> 'MacUIElement':
        try:
            self._control.AXFocused = True
        except Exception:
            pass
        return self

    def drag_to(self, target: Any, move_speed: int = 1, wait_time: float = 0.5) -> 'MacUIElement':
        src_pos = self._control.AXPosition
        src_size = self._control.AXSize
        tgt_pos = target._backend._control.AXPosition
        tgt_size = target._backend._control.AXSize
        
        start_x = src_pos[0] + src_size[0] // 2
        start_y = src_pos[1] + src_size[1] // 2
        
        end_x = tgt_pos[0] + tgt_size[0] // 2
        end_y = tgt_pos[1] + tgt_size[1] // 2
        
        import pyautogui
        import time
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        time.sleep(0.2)
        pyautogui.dragTo(end_x, end_y, duration=move_speed, button='left')
        time.sleep(wait_time)
        return self

    def move(self, x: int, y: int) -> 'MacUIElement':
        try:
            self._control.AXPosition = (x, y)
        except Exception:
            pass
        return self

    def resize(self, width: int, height: int) -> 'MacUIElement':
        try:
            self._control.AXSize = (width, height)
        except Exception:
            pass
        return self

    def maximize(self) -> 'MacUIElement':
        try:
            self._control.AXZoomed = True
        except Exception:
            pass
        return self

    def minimize(self) -> 'MacUIElement':
        try:
            self._control.AXMinimized = True
        except Exception:
            pass
        return self

    def restore(self) -> 'MacUIElement':
        try:
            self._control.AXMinimized = False
        except Exception:
            pass
        return self

    def close(self) -> 'MacUIElement':
        try:
            # atomacos exposes a close action or property
            self._control.close()
        except Exception:
            self.focus()
            import pyautogui
            pyautogui.hotkey('command', 'w')
        return self

    def scroll_into_view(self) -> 'MacUIElement':
        self.focus()
        return self

    def scroll_to_bottom(self) -> 'MacUIElement':
        self.focus()
        import pyautogui
        pyautogui.hotkey('command', 'down')
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'MacUIElement':
        self.focus()
        try:
            self._control.AXValue = text
        except Exception:
            import pyperclip
            import pyautogui
            import time
            pyperclip.copy(text)
            pyautogui.hotkey('command', 'v')
            time.sleep(waitTime)
        return self

    def read(self) -> str:
        val = getattr(self._control, 'AXValue', None)
        if val is not None and isinstance(val, str):
            return val
        title = getattr(self._control, 'AXTitle', None)
        if title is not None and isinstance(title, str):
            return title
        return ""

    def _element_matches(self, element, role: Optional[str], name: Optional[str], regex_name: Optional[str]) -> bool:
        if role is not None:
            el_role = getattr(element, 'AXRole', "")
            mapped_role = ROLE_MAPPING.get(el_role.lower(), el_role.replace("AX", "").lower())
            if role.lower() not in mapped_role:
                return False
                
        el_name = getattr(element, 'AXTitle', "") or getattr(element, 'AXDescription', "") or getattr(element, 'AXValue', "")
        if not isinstance(el_name, str):
            el_name = str(el_name) if el_name is not None else ""
            
        if name is not None and el_name != name:
            return False
            
        if regex_name is not None:
            if not re.match(regex_name, el_name):
                return False
                
        return True

    def _find_recursive(self, element, role: Optional[str], name: Optional[str], regex_name: Optional[str]):
        if self._element_matches(element, role, name, regex_name):
            return element
        
        children = getattr(element, 'AXChildren', None)
        if children:
            for child in children:
                res = self._find_recursive(child, role, name, regex_name)
                if res:
                    return res
        return None

    def find(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None) -> Any:
        found = self._find_recursive(self._control, role, name, regex_name)
        if found:
            return UIElement(found, highlight_actions=self.highlight_actions)
        raise ValueError(f"Element not found with name='{name}', regex_name='{regex_name}', role='{role}'")

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None, timeout: int = 10) -> Any:
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return self.find(role=role, name=name, regex_name=regex_name)
            except Exception:
                time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element with name='{name}', regex_name='{regex_name}', role='{role}' after {timeout} seconds")

    def wait_until_clickable(self, timeout: int = 10) -> 'MacUIElement':
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            enabled = getattr(self._control, 'AXEnabled', True)
            if enabled:
                return self
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element to become clickable after {timeout} seconds")

    def dump_ui(self, max_depth: int = 2) -> Dict[str, Any]:
        return self._dump_recursive(self._control, 0, max_depth)
        
    def _dump_recursive(self, control, current_depth: int, max_depth: int) -> Dict[str, Any]:
        el_role = getattr(control, 'AXRole', "unknown")
        role = ROLE_MAPPING.get(el_role.lower(), el_role.replace("AX", "").lower())
        name = getattr(control, 'AXTitle', "") or getattr(control, 'AXDescription', "") or ""
        data = {
            "role": role,
            "name": str(name),
        }
        if current_depth < max_depth:
            children = getattr(control, 'AXChildren', None)
            if children:
                data["elements"] = [self._dump_recursive(c, current_depth + 1, max_depth) for c in children]
        return data

    def to_yaml_snapshot(self, max_depth: int = 5) -> str:
        lines = []
        self._to_yaml_recursive(self._control, 0, max_depth, lines)
        return "\n".join(lines)
        
    def _to_yaml_recursive(self, control, depth: int, max_depth: int, lines: List[str]):
        el_role = getattr(control, 'AXRole', "unknown")
        role = ROLE_MAPPING.get(el_role.lower(), el_role.replace("AX", "").lower())
        name = getattr(control, 'AXTitle', "") or getattr(control, 'AXDescription', "") or ""
        
        indent = "  " * depth
        line = f"{indent}- {role}"
        if name:
            safe_name = str(name).replace('"', '\\"')
            line += f' "{safe_name}"'
            
        children = getattr(control, 'AXChildren', None)
        if children and depth < max_depth:
            line += ":"
            lines.append(line)
            for child in children:
                self._to_yaml_recursive(child, depth + 1, max_depth, lines)
        else:
            lines.append(line)

class LinuxUIElement(UIElementBackend):
    def __init__(self, control, highlight_actions: bool = False):
        self._control = control
        self.highlight_actions = highlight_actions

    @property
    def name(self) -> str:
        return self._control.name or ""

    @property
    def role(self) -> str:
        role_name = self._control.getRoleName() or "unknown"
        return ROLE_MAPPING.get(role_name.lower(), role_name.replace(" ", "_").lower())

    def click(self) -> 'LinuxUIElement':
        try:
            act = self._control.queryAction()
            act.doAction(0)
        except Exception:
            self.hover()
            import pyautogui
            pyautogui.click()
        return self

    def double_click(self) -> 'LinuxUIElement':
        self.hover()
        import pyautogui
        pyautogui.doubleClick()
        return self

    def right_click(self) -> 'LinuxUIElement':
        self.hover()
        import pyautogui
        pyautogui.rightClick()
        return self

    def hover(self) -> 'LinuxUIElement':
        import pyatspi
        comp = self._control.queryComponent()
        box = comp.getExtents(pyatspi.XY_SCREEN)
        x = box.x + box.width // 2
        y = box.y + box.height // 2
        import pyautogui
        pyautogui.moveTo(x, y)
        return self

    def focus(self) -> 'LinuxUIElement':
        try:
            comp = self._control.queryComponent()
            comp.grabFocus()
        except Exception:
            pass
        return self

    def drag_to(self, target: Any, move_speed: int = 1, wait_time: float = 0.5) -> 'LinuxUIElement':
        import pyatspi
        src_comp = self._control.queryComponent()
        src_box = src_comp.getExtents(pyatspi.XY_SCREEN)
        
        tgt_comp = target._backend._control.queryComponent()
        tgt_box = tgt_comp.getExtents(pyatspi.XY_SCREEN)
        
        start_x = src_box.x + src_box.width // 2
        start_y = src_box.y + src_box.height // 2
        
        end_x = tgt_box.x + tgt_box.width // 2
        end_y = tgt_box.y + tgt_box.height // 2
        
        import pyautogui
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        pyautogui.dragTo(end_x, end_y, duration=move_speed, button='left')
        return self

    def move(self, x: int, y: int) -> 'LinuxUIElement':
        return self

    def resize(self, width: int, height: int) -> 'LinuxUIElement':
        return self

    def maximize(self) -> 'LinuxUIElement':
        return self

    def minimize(self) -> 'LinuxUIElement':
        return self

    def restore(self) -> 'LinuxUIElement':
        return self

    def close(self) -> 'LinuxUIElement':
        try:
            self.focus()
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
        except Exception:
            pass
        return self

    def scroll_into_view(self) -> 'LinuxUIElement':
        self.focus()
        return self

    def scroll_to_bottom(self) -> 'LinuxUIElement':
        self.focus()
        import pyautogui
        pyautogui.hotkey('ctrl', 'end')
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'LinuxUIElement':
        self.focus()
        try:
            edit = self._control.queryEditableText()
            edit.setTextContents(text)
        except Exception:
            import pyperclip
            import pyautogui
            import time
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(waitTime)
        return self

    def read(self) -> str:
        try:
            txt = self._control.queryText()
            return txt.getText(0, txt.characterCount)
        except Exception:
            return self.name

    def find(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None) -> Any:
        # Recursive traverse AT-SPI
        found = self._find_recursive(self._control, role, name, regex_name)
        if found:
            return UIElement(found, highlight_actions=self.highlight_actions)
        raise ValueError(f"Element not found with name='{name}', regex_name='{regex_name}', role='{role}'")

    def _element_matches(self, element, role: Optional[str], name: Optional[str], regex_name: Optional[str]) -> bool:
        if role is not None:
            role_name = element.getRoleName() or ""
            mapped_role = ROLE_MAPPING.get(role_name.lower(), role_name.replace(" ", "_").lower())
            if role.lower() not in mapped_role:
                return False
                
        el_name = element.name or ""
        if name is not None and el_name != name:
            return False
            
        if regex_name is not None:
            if not re.match(regex_name, el_name):
                return False
                
        return True

    def _find_recursive(self, element, role: Optional[str], name: Optional[str], regex_name: Optional[str]):
        if self._element_matches(element, role, name, regex_name):
            return element
            
        child_count = element.childCount
        if child_count > 0:
            for i in range(child_count):
                child = element.getChildAtIndex(i)
                res = self._find_recursive(child, role, name, regex_name)
                if res:
                    return res
        return None

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None, timeout: int = 10) -> Any:
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return self.find(role=role, name=name, regex_name=regex_name)
            except Exception:
                time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element with name='{name}', regex_name='{regex_name}', role='{role}' after {timeout} seconds")

    def wait_until_clickable(self, timeout: int = 10) -> 'LinuxUIElement':
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            state = self._control.getState()
            if state.contains(pyatspi.STATE_ENABLED) and state.contains(pyatspi.STATE_SENSITIVE):
                return self
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for element to become clickable after {timeout} seconds")

    def dump_ui(self, max_depth: int = 2) -> Dict[str, Any]:
        return self._dump_recursive(self._control, 0, max_depth)
        
    def _dump_recursive(self, control, current_depth: int, max_depth: int) -> Dict[str, Any]:
        role_name = control.getRoleName() or "unknown"
        role = ROLE_MAPPING.get(role_name.lower(), role_name.replace(" ", "_").lower())
        data = {
            "role": role,
            "name": control.name or "",
        }
        if current_depth < max_depth:
            child_count = control.childCount
            if child_count > 0:
                elements = []
                for i in range(child_count):
                    elements.append(self._dump_recursive(control.getChildAtIndex(i), current_depth + 1, max_depth))
                data["elements"] = elements
        return data

    def to_yaml_snapshot(self, max_depth: int = 5) -> str:
        lines = []
        self._to_yaml_recursive(self._control, 0, max_depth, lines)
        return "\n".join(lines)
        
    def _to_yaml_recursive(self, control, depth: int, max_depth: int, lines: List[str]):
        role_name = control.getRoleName() or "unknown"
        role = ROLE_MAPPING.get(role_name.lower(), role_name.replace(" ", "_").lower())
        name = control.name or ""
        
        indent = "  " * depth
        line = f"{indent}- {role}"
        if name:
            safe_name = name.replace('"', '\\"')
            line += f' "{safe_name}"'
            
        child_count = control.childCount
        if child_count > 0 and depth < max_depth:
            line += ":"
            lines.append(line)
            for i in range(child_count):
                self._to_yaml_recursive(control.getChildAtIndex(i), depth + 1, max_depth, lines)
        else:
            lines.append(line)

class UIElement:
    def __init__(self, control, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions
        if sys.platform == 'win32':
            self._backend = WindowsUIElement(control, highlight_actions)
        elif sys.platform == 'darwin':
            self._backend = MacUIElement(control, highlight_actions)
        elif sys.platform.startswith('linux'):
            self._backend = LinuxUIElement(control, highlight_actions)
        else:
            raise NotImplementedError(f"Platform {sys.platform} is not supported by Tarsier.")

    @property
    def _control(self):
        return self._backend._control

    @property
    def name(self) -> str:
        return self._backend.name

    @property
    def role(self) -> str:
        return self._backend.role

    def click(self) -> 'UIElement':
        self._backend.click()
        return self
    
    def double_click(self) -> 'UIElement':
        self._backend.double_click()
        return self

    def right_click(self) -> 'UIElement':
        self._backend.right_click()
        return self

    def hover(self) -> 'UIElement':
        self._backend.hover()
        return self

    def focus(self) -> 'UIElement':
        self._backend.focus()
        return self

    def drag_to(self, target: 'UIElement', move_speed: int = 1, wait_time: float = 0.5) -> 'UIElement':
        self._backend.drag_to(target, move_speed, wait_time)
        return self

    def move(self, x: int, y: int) -> 'UIElement':
        self._backend.move(x, y)
        return self

    def resize(self, width: int, height: int) -> 'UIElement':
        self._backend.resize(width, height)
        return self

    def maximize(self) -> 'UIElement':
        self._backend.maximize()
        return self

    def minimize(self) -> 'UIElement':
        self._backend.minimize()
        return self

    def restore(self) -> 'UIElement':
        self._backend.restore()
        return self

    def close(self) -> 'UIElement':
        self._backend.close()
        return self

    def scroll_into_view(self) -> 'UIElement':
        self._backend.scroll_into_view()
        return self

    def scroll_to_bottom(self) -> 'UIElement':
        self._backend.scroll_to_bottom()
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'UIElement':
        self._backend.type(text, waitTime)
        return self

    def read(self) -> str:
        return self._backend.read()

    def find(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None) -> 'UIElement':
        return self._backend.find(role, name, regex_name)

    def wait_for_element(self, role: Optional[str] = None, name: Optional[str] = None, regex_name: Optional[str] = None, timeout: int = 10) -> 'UIElement':
        return self._backend.wait_for_element(role, name, regex_name, timeout)

    def wait_until_clickable(self, timeout: int = 10) -> 'UIElement':
        self._backend.wait_until_clickable(timeout)
        return self

    def button(self, name: str) -> 'UIElement':
        return self.find(role="button", name=name)

    def textbox(self, name: Optional[str] = None) -> 'UIElement':
        try:
            return self.find(role="document", name=name)
        except ValueError:
            return self.find(role="textbox", name=name)
        
    def menu(self, name: str) -> 'UIElement':
        return self.find(role="menuitem", name=name)

    def dump_ui(self, max_depth: int = 2) -> Dict[str, Any]:
        return self._backend.dump_ui(max_depth)

    def to_yaml_snapshot(self, max_depth: int = 5) -> str:
        return self._backend.to_yaml_snapshot(max_depth)

    def to_json(self) -> str:
        return json.dumps(self.dump_ui(), indent=2)
