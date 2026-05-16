import subprocess
import time
import uiautomation as auto
from tarsier.core.elements import UIElement

class Desktop:
    def __init__(self):
        pass

    def open_app(self, executable: str, window_name: str = None) -> UIElement:
        """
        Opens an application and returns the main window element.
        """
        subprocess.Popen(executable)
        
        # If no name given, we have to fall back to a short sleep and getting foreground window
        if not window_name:
            time.sleep(2)
            window = auto.GetForegroundControl()
            while window and window.GetParentControl() and window.GetParentControl().ControlTypeName != 'PaneControl':
                 parent = window.GetParentControl()
                 if parent.Name == 'Desktop 1':
                     break
                 window = parent
            return UIElement(window)
            
        # If name provided, use smart wait
        return self.wait_for_window(name=window_name)
        
    def get_window(self, name: str) -> UIElement:
        window = auto.WindowControl(searchDepth=1, Name=name)
        if not window.Exists(3, 1):
            raise Exception(f"Could not find window with name: {name}")
        return UIElement(window)
        
    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        """
        Blocks execution until the specified window appears.
        """
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
            
        return UIElement(window)
