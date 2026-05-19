import subprocess
import time
import sys
from tarsier.core.elements import UIElement

class Desktop:
    def __init__(self, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions
        # Make the process DPI aware so that GDI coordinates match uiautomation coordinates!
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def _check_windows(self):
        if sys.platform != 'win32':
            raise NotImplementedError("Semantic desktop automation is currently supported only on Windows. For cross-platform automation, use WebDesktop or coordinate-based tools.")

    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
        """
        Opens an application and returns the main window element.
        """
        self._check_windows()
        import uiautomation as auto
        subprocess.Popen(executable)
        
        # If neither name nor regex_name given, we have to fall back to a short sleep and getting foreground window
        if not window_name and not regex_name:
            time.sleep(2)
            window = auto.GetForegroundControl()
            while window and window.GetParentControl() and window.GetParentControl().ControlTypeName != 'PaneControl':
                 parent = window.GetParentControl()
                 if parent.Name == 'Desktop 1':
                     break
                 window = parent
            return UIElement(window, highlight_actions=self.highlight_actions)
            
        # If name or regex provided, use smart wait
        return self.wait_for_window(name=window_name, regex_name=regex_name)
        
    def get_window(self, name: str) -> UIElement:
        self._check_windows()
        import uiautomation as auto
        window = auto.WindowControl(searchDepth=1, Name=name)
        if not window.Exists(3, 1):
            raise Exception(f"Could not find window with name: {name}")
        return UIElement(window, highlight_actions=self.highlight_actions)
        
    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        """
        Blocks execution until the specified window appears.
        """
        self._check_windows()
        import uiautomation as auto
        kwargs = {"searchDepth": 1}
        if regex_name:
            kwargs["RegexName"] = regex_name
        elif name:
            kwargs["Name"] = name
        else:
            raise ValueError("Must provide either name or regex_name")
            
        window = auto.WindowControl(**kwargs)
        if not window.Exists(timeout, 1):
            raise TimeoutError(f"Timed out waiting for window: {name or regex_name} after {timeout} seconds")
            
        return UIElement(window, highlight_actions=self.highlight_actions)

    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'Desktop':
        """
        Sends a global OS hotkey combination.
        Supports standard modifiers like {Ctrl}c, {Alt}{Tab}, {Win}d, etc.
        """
        if sys.platform == 'win32':
            import uiautomation as auto
            auto.SendKeys(keys, waitTime=waitTime)
        else:
            import pyautogui
            # Simple conversion of {Ctrl}c to pyautogui.hotkey('ctrl', 'c')
            import re
            modifiers = re.findall(r'{(.*?)}', keys)
            rest = re.sub(r'{.*?}', '', keys)
            keys_list = [m.lower() for m in modifiers]
            if rest:
                keys_list.extend(list(rest))
            pyautogui.hotkey(*keys_list)
        return self

    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'Desktop':
        """
        Drags from physical screen coordinates (start_x, start_y) to (end_x, end_y).
        """
        if sys.platform == 'win32':
            import uiautomation as auto
            auto.MoveTo(start_x, start_y)
            time.sleep(0.2)
            auto.DragDrop(start_x, start_y, end_x, end_y, moveSpeed=move_speed, waitTime=wait_time)
        else:
            import pyautogui
            pyautogui.moveTo(start_x, start_y, duration=0.2)
            pyautogui.dragTo(end_x, end_y, duration=move_speed, button='left')
        return self

    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'Desktop':
        """
        Drags from the center of source_element to the center of target_element.
        """
        self._check_windows()
        start_rect = source_element._control.BoundingRectangle
        end_rect = target_element._control.BoundingRectangle
        
        start_x = (start_rect.left + start_rect.right) // 2
        start_y = (start_rect.top + start_rect.bottom) // 2
        
        end_x = (end_rect.left + end_rect.right) // 2
        end_y = (end_rect.top + end_rect.bottom) // 2
        
        if getattr(source_element, 'highlight_actions', False):
            source_element._highlight()
            target_element._highlight()
            
        return self.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed=move_speed, wait_time=wait_time)
