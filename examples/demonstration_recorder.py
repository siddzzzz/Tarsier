import sys
import time
import queue

try:
    from pynput import mouse, keyboard
except ImportError:
    print("Error: pynput is required for the demonstration recorder.")
    print("Please install it with: pip install pynput")
    sys.exit(1)

def main():
    if sys.platform != 'win32':
        print("This demonstration recorder MVP is currently only supported on Windows.")
        sys.exit(1)

    import uiautomation as auto
    from tarsier.core.elements import ROLE_MAPPING

    def get_tarsier_role(control):
        raw_role = control.ControlTypeName.replace("Control", "").lower()
        return ROLE_MAPPING.get(raw_role, raw_role)

    last_focused_element = None
    typed_buffer = ""
    
    # Use a queue to pass events from pynput threads to the main thread
    # This avoids COM "CoInitialize has not been called" errors in uiautomation
    event_queue = queue.Queue()

    def on_click(x, y, button, pressed):
        if pressed:
            event_queue.put(('click', (x, y)))

    def on_press(key):
        if key == keyboard.Key.esc:
            event_queue.put(('stop', None))
            return False
        elif hasattr(key, 'char') and key.char is not None:
            event_queue.put(('type', key.char))
        elif key == keyboard.Key.space:
            event_queue.put(('type', ' '))
        elif key == keyboard.Key.backspace:
            event_queue.put(('backspace', None))
        elif key == keyboard.Key.enter:
            event_queue.put(('enter', None))

    print("Starting Demonstration Recorder...")
    print("Click around and type to record actions.")
    print("Press ESC to stop recording.")
    print("-" * 50)
    
    # Start listeners
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    # Main event loop (runs in main thread with COM initialized)
    running = True
    while running:
        try:
            event_type, event_data = event_queue.get(timeout=0.1)
            
            if event_type == 'stop':
                running = False
                break
                
            elif event_type == 'click':
                # Flush typed buffer if there is any
                if typed_buffer and last_focused_element:
                    print(f'[Agent] Tool Call -> desktop_type(role="{last_focused_element["role"]}", name="{last_focused_element["name"]}", text="{typed_buffer}")')
                    typed_buffer = ""
                    
                x, y = event_data
                try:
                    control = auto.ControlFromPoint(int(x), int(y))
                    role = get_tarsier_role(control)
                    name = control.Name
                    
                    last_focused_element = {"role": role, "name": name}
                    
                    name_str = f'"{name}"' if name else '""'
                    print(f'[Agent] Tool Call -> desktop_click(role="{role}", name={name_str})')
                except Exception as e:
                    pass # Ignore errors for untrackable elements
                    
            elif event_type == 'type':
                typed_buffer += event_data
                
            elif event_type == 'backspace':
                typed_buffer = typed_buffer[:-1]
                
            elif event_type == 'enter':
                if typed_buffer and last_focused_element:
                    print(f'[Agent] Tool Call -> desktop_type(role="{last_focused_element["role"]}", name="{last_focused_element["name"]}", text="{typed_buffer}")')
                    typed_buffer = ""
                print(f'[Agent] Tool Call -> desktop_press_key("enter")')
                
        except queue.Empty:
            pass
            
        except KeyboardInterrupt:
            running = False
    
    mouse_listener.stop()
    keyboard_listener.stop()
    
    # Flush remaining buffer
    if typed_buffer and last_focused_element:
        print(f'[Agent] Tool Call -> desktop_type(role="{last_focused_element["role"]}", name="{last_focused_element["name"]}", text="{typed_buffer}")')
        
    print("-" * 50)
    print("Recording stopped.")

if __name__ == "__main__":
    main()
