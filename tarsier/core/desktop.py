import subprocess
import time
import sys
from typing import Optional
from tarsier.core.elements import UIElement

def _send_pyautogui_keys(keys: str, waitTime: float = 0.05):
    import pyautogui
    import re
    import time

    KEY_MAP = {
        'ctrl': 'ctrl',
        'control': 'ctrl',
        'shift': 'shift',
        'alt': 'alt',
        'option': 'option',
        'command': 'command',
        'cmd': 'command',
        'win': 'win',
        'lwin': 'win',
        'rwin': 'win',
        'enter': 'enter',
        'return': 'return',
        'tab': 'tab',
        'space': 'space',
        'backspace': 'backspace',
        'delete': 'delete',
        'esc': 'esc',
        'escape': 'escape',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'pgup': 'pageup',
        'pgdn': 'pagedown',
        'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5', 'f6': 'f6',
        'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
    }

    MODIFIERS = {'ctrl', 'shift', 'alt', 'option', 'command', 'win'}

    tokens = []
    pattern = r'\{([^}]+)\}|([a-zA-Z0-9]+)|(.)'
    for match in re.finditer(pattern, keys):
        braced, word, char = match.groups()
        if braced:
            k = braced.lower()
            tokens.append(KEY_MAP.get(k, k))
        elif word:
            k = word.lower()
            if k in KEY_MAP:
                tokens.append(KEY_MAP[k])
            else:
                tokens.extend(list(word))
        elif char:
            tokens.append(char)

    has_modifier = any(t in MODIFIERS for t in tokens)

    if has_modifier:
        pyautogui.hotkey(*tokens)
    else:
        for token in tokens:
            if token in KEY_MAP.values():
                pyautogui.press(token)
            else:
                pyautogui.write(token)

    time.sleep(waitTime)

class DesktopBackend:
    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
        raise NotImplementedError()
    def get_window(self, name: str) -> UIElement:
        raise NotImplementedError()
    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        raise NotImplementedError()
    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'DesktopBackend':
        raise NotImplementedError()
    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'DesktopBackend':
        raise NotImplementedError()
    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'DesktopBackend':
        raise NotImplementedError()

class WindowsDesktopBackend(DesktopBackend):
    def __init__(self, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    def _trigger_chrome_accessibility(self):
        """
        Programmatically triggers accessibility tree activation on all active
        Chromium-based windows (Chrome, Edge, Brave, Electron apps, etc.) on Windows
        by sending the WM_GETOBJECT message with OBJID_CLIENT to any Chrome_RenderWidgetHostHWND controls.
        This forces the browser renderer to turn on and expose its inner DOM tree.
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            WM_GETOBJECT = 0x003D
            OBJID_CLIENT = 0xFFFFFFFC # -4
            
            user32 = ctypes.windll.user32
            
            def enum_window_callback(hwnd, lParam):
                class_name = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_name, 256)
                if class_name.value == "Chrome_RenderWidgetHostHWND":
                    user32.SendMessageW(hwnd, WM_GETOBJECT, 0, OBJID_CLIENT)
                return True
                
            self._enum_callback = EnumChildProc(enum_window_callback)
            user32.EnumChildWindows(0, self._enum_callback, 0)
        except Exception:
            pass

    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
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
            self._trigger_chrome_accessibility()
            time.sleep(0.5)
            return UIElement(window, highlight_actions=self.highlight_actions)
            
        # If name or regex provided, use smart wait
        return self.wait_for_window(name=window_name, regex_name=regex_name)
        
    def get_window(self, name: str) -> UIElement:
        import uiautomation as auto
        window = auto.WindowControl(searchDepth=1, Name=name)
        if not window.Exists(3, 1):
            raise Exception(f"Could not find window with name: {name}")
        self._trigger_chrome_accessibility()
        time.sleep(0.5)
        return UIElement(window, highlight_actions=self.highlight_actions)
        
    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
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
            
        self._trigger_chrome_accessibility()
        time.sleep(0.5)
        return UIElement(window, highlight_actions=self.highlight_actions)

    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'WindowsDesktopBackend':
        import uiautomation as auto
        auto.SendKeys(keys, waitTime=waitTime)
        return self

    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'WindowsDesktopBackend':
        import uiautomation as auto
        auto.MoveTo(start_x, start_y)
        time.sleep(0.2)
        auto.DragDrop(start_x, start_y, end_x, end_y, moveSpeed=move_speed, waitTime=wait_time)
        return self

    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'WindowsDesktopBackend':
        start_rect = source_element._backend._control.BoundingRectangle
        end_rect = target_element._backend._control.BoundingRectangle
        
        start_x = (start_rect.left + start_rect.right) // 2
        start_y = (start_rect.top + start_rect.bottom) // 2
        
        end_x = (end_rect.left + end_rect.right) // 2
        end_y = (end_rect.top + end_rect.bottom) // 2
        
        if getattr(source_element, 'highlight_actions', False):
            source_element._backend._highlight()
            target_element._backend._highlight()
            
        return self.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed=move_speed, wait_time=wait_time)

class MacDesktopBackend(DesktopBackend):
    def __init__(self, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions

    def _find_running_app_info(self, executable: str):
        try:
            from Cocoa import NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            for app in workspace.runningApplications():
                localized_name = app.localizedName()
                bundle_id = app.bundleIdentifier()
                if (localized_name and localized_name.lower() == executable.lower()) or (bundle_id and bundle_id.lower() == executable.lower()):
                    return app.processIdentifier(), bundle_id
        except Exception:
            pass
        return None, None

    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
        import atomacos
        pid, bundle_id = self._find_running_app_info(executable)
        if pid is None:
            if executable.endswith('.app') or '/' in executable or '\\' in executable:
                subprocess.Popen(["open", executable])
            elif '.' in executable and len(executable.split('.')) >= 2:
                try:
                    atomacos.launchAppByBundleId(executable)
                except Exception:
                    subprocess.Popen(["open", "-b", executable])
            else:
                subprocess.Popen(["open", "-a", executable])
                
            start_time = time.time()
            while time.time() - start_time < 5:
                pid, bundle_id = self._find_running_app_info(executable)
                if pid is not None:
                    break
                time.sleep(0.5)
                
        if pid is None:
            time.sleep(2)
            try:
                from Cocoa import NSWorkspace
                pid = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']
            except Exception:
                raise Exception(f"Failed to launch or attach to application: {executable}")
                
        time.sleep(1)
        if window_name or regex_name:
            return self.wait_for_window(name=window_name, regex_name=regex_name)
            
        try:
            app_ref = atomacos.getAppRefByPid(pid)
            windows = app_ref.windows()
            if windows:
                return UIElement(windows[0], highlight_actions=self.highlight_actions)
            return UIElement(app_ref, highlight_actions=self.highlight_actions)
        except Exception as e:
            raise Exception(f"Error getting app accessibility reference for PID {pid}: {e}")

    def get_window(self, name: str) -> UIElement:
        import atomacos
        from Cocoa import NSWorkspace
        workspace = NSWorkspace.sharedWorkspace()
        for app in workspace.runningApplications():
            try:
                app_ref = atomacos.getAppRefByPid(app.processIdentifier())
                for window in app_ref.windows():
                    if window.AXTitle == name:
                        return UIElement(window, highlight_actions=self.highlight_actions)
            except Exception:
                pass
        raise Exception(f"Could not find window with title: {name}")

    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        import re
        import atomacos
        from Cocoa import NSWorkspace
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            workspace = NSWorkspace.sharedWorkspace()
            for app in workspace.runningApplications():
                try:
                    app_ref = atomacos.getAppRefByPid(app.processIdentifier())
                    for window in app_ref.windows():
                        title = window.AXTitle or ""
                        if name and title == name:
                            return UIElement(window, highlight_actions=self.highlight_actions)
                        if regex_name and re.match(regex_name, title):
                            return UIElement(window, highlight_actions=self.highlight_actions)
                except Exception:
                    pass
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for window with name='{name}' or regex_name='{regex_name}' after {timeout} seconds")

    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'MacDesktopBackend':
        _send_pyautogui_keys(keys, waitTime)
        return self

    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'MacDesktopBackend':
        import pyautogui
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        pyautogui.dragTo(end_x, end_y, duration=move_speed, button='left')
        time.sleep(wait_time)
        return self

    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'MacDesktopBackend':
        src_pos = source_element._backend._control.AXPosition
        src_size = source_element._backend._control.AXSize
        tgt_pos = target_element._backend._control.AXPosition
        tgt_size = target_element._backend._control.AXSize
        
        start_x = src_pos[0] + src_size[0] // 2
        start_y = src_pos[1] + src_size[1] // 2
        
        end_x = tgt_pos[0] + tgt_size[0] // 2
        end_y = tgt_pos[1] + tgt_size[1] // 2
        
        return self.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed, wait_time)

class LinuxDesktopBackend(DesktopBackend):
    def __init__(self, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions

    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
        subprocess.Popen(executable)
        time.sleep(2)
        if window_name or regex_name:
            return self.wait_for_window(name=window_name, regex_name=regex_name)
            
        import pyatspi
        registry = pyatspi.Registry
        desktop = registry.getDesktop(0)
        if desktop.childCount > 0:
            app = desktop.getChildAtIndex(desktop.childCount - 1)
            if app.childCount > 0:
                return UIElement(app.getChildAtIndex(0), highlight_actions=self.highlight_actions)
            return UIElement(app, highlight_actions=self.highlight_actions)
        raise Exception("Failed to get application reference on Linux.")

    def get_window(self, name: str) -> UIElement:
        import pyatspi
        registry = pyatspi.Registry
        desktop = registry.getDesktop(0)
        for app in desktop:
            for window in app:
                if window.name == name:
                    return UIElement(window, highlight_actions=self.highlight_actions)
        raise Exception(f"Could not find window with title: {name}")

    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        import re
        import pyatspi
        start_time = time.time()
        while time.time() - start_time < timeout:
            registry = pyatspi.Registry
            desktop = registry.getDesktop(0)
            for app in desktop:
                for window in app:
                    title = window.name or ""
                    if name and title == name:
                        return UIElement(window, highlight_actions=self.highlight_actions)
                    if regex_name and re.match(regex_name, title):
                        return UIElement(window, highlight_actions=self.highlight_actions)
            time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for window with name='{name}' or regex_name='{regex_name}' after {timeout} seconds")

    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'LinuxDesktopBackend':
        _send_pyautogui_keys(keys, waitTime)
        return self

    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'LinuxDesktopBackend':
        import pyautogui
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        pyautogui.dragTo(end_x, end_y, duration=move_speed, button='left')
        time.sleep(wait_time)
        return self

    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'LinuxDesktopBackend':
        import pyatspi
        src_comp = source_element._backend._control.queryComponent()
        src_box = src_comp.getExtents(pyatspi.XY_SCREEN)
        
        tgt_comp = target_element._backend._control.queryComponent()
        tgt_box = tgt_comp.getExtents(pyatspi.XY_SCREEN)
        
        start_x = src_box.x + src_box.width // 2
        start_y = src_box.y + src_box.height // 2
        
        end_x = tgt_box.x + tgt_box.width // 2
        end_y = tgt_box.y + tgt_box.height // 2
        
        return self.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed, wait_time)

class Desktop:
    def __init__(self, highlight_actions: bool = False):
        self.highlight_actions = highlight_actions
        if sys.platform == 'win32':
            self._backend = WindowsDesktopBackend(highlight_actions)
        elif sys.platform == 'darwin':
            self._backend = MacDesktopBackend(highlight_actions)
        elif sys.platform.startswith('linux'):
            self._backend = LinuxDesktopBackend(highlight_actions)
        else:
            raise NotImplementedError(f"Platform {sys.platform} is not supported by Tarsier.")

    def open_app(self, executable: str, window_name: str = None, regex_name: str = None) -> UIElement:
        return self._backend.open_app(executable, window_name, regex_name)

    def get_window(self, name: str) -> UIElement:
        return self._backend.get_window(name)

    def wait_for_window(self, name: str = None, regex_name: str = None, timeout: int = 10) -> UIElement:
        return self._backend.wait_for_window(name, regex_name, timeout)

    def hotkey(self, keys: str, waitTime: float = 0.05) -> 'Desktop':
        self._backend.hotkey(keys, waitTime)
        return self

    def drag_and_drop_coordinates(self, start_x: int, start_y: int, end_x: int, end_y: int, move_speed: int = 1, wait_time: float = 0.5) -> 'Desktop':
        self._backend.drag_and_drop_coordinates(start_x, start_y, end_x, end_y, move_speed, wait_time)
        return self

    def drag_and_drop(self, source_element: UIElement, target_element: UIElement, move_speed: int = 1, wait_time: float = 0.5) -> 'Desktop':
        self._backend.drag_and_drop(source_element, target_element, move_speed, wait_time)
        return self
