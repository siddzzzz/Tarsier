import json
from typing import List, Dict, Any, Optional

class UIElement:
    def __init__(self, control):
        # control is a uiautomation.Control
        self._control = control

    @property
    def name(self) -> str:
        return self._control.Name

    @property
    def role(self) -> str:
        return self._control.ControlTypeName

    def click(self) -> 'UIElement':
        self._control.Click()
        return self
    
    def double_click(self) -> 'UIElement':
        self._control.DoubleClick()
        return self

    def focus(self) -> 'UIElement':
        self._control.SetFocus()
        return self

    def type(self, text: str, waitTime: float = 0.05) -> 'UIElement':
        # SendKeys types character-by-character, which can race and garble in modern UI like Win 11 Notepad.
        # A much more reliable method for semantic automation is pasting via clipboard or ValuePattern.
        import uiautomation as auto
        auto.SetClipboardText(text)
        self.focus()
        self._control.SendKeys('{Ctrl}v', waitTime=waitTime)
        return self

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
                return UIElement(child)
        
        raise ValueError(f"Element not found with name='{name}', role='{role}'")

    def button(self, name: str) -> 'UIElement':
        return self.find(role="button", name=name)

    def textbox(self, name: Optional[str] = None) -> 'UIElement':
        return self.find(role="document", name=name) or self.find(role="edit", name=name)
        
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

    def to_json(self) -> str:
        return json.dumps(self.dump_ui(), indent=2)
