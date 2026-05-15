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
        time.sleep(2) # Wait for it to open (MVP hack)
        
        # Try to find the window
        if window_name:
            window = auto.WindowControl(searchDepth=1, Name=window_name)
        else:
            # If no name given, just grab the active window after a short delay
            time.sleep(1)
            window = auto.GetForegroundControl()
            # find the top level window for this foreground control
            while window and window.GetParentControl() and window.GetParentControl().ControlTypeName != 'PaneControl':
                 # Usually the desktop is a PaneControl, so we go up until we hit the top level window
                 parent = window.GetParentControl()
                 if parent.Name == 'Desktop 1':
                     break
                 window = parent
            
        if not window.Exists(3, 1):
            raise Exception("Could not find the application window.")
            
        return UIElement(window)
        
    def get_window(self, name: str) -> UIElement:
        window = auto.WindowControl(searchDepth=1, Name=name)
        if not window.Exists(3, 1):
            raise Exception(f"Could not find window with name: {name}")
        return UIElement(window)
