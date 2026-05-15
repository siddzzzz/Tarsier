<div align="center">
  <h1>🐒 Tarsier</h1>
  <p><b>Semantic Desktop Automation Framework for AI Agents</b></p>
  <p><i>The "Playwright" for Windows Desktop Apps.</i></p>
</div>

---

## 🎯 What is Tarsier?

Tarsier is an open-source **infrastructure layer** designed to provide robust, deterministic interaction with Windows desktop applications. 

Most "AI Computer Use" agents rely on taking screenshots, sending them to expensive vision models (like GPT-4V or Claude 3.5 Sonnet), and guessing X/Y pixel coordinates to click. 

**Tarsier takes a completely different approach.** 

Instead of screenshots, Tarsier hooks directly into the **Windows UI Automation (UIA) accessibility layer**. It extracts the exact structure of the application into a compact, semantic JSON tree (a "Desktop DOM") and allows interaction via semantic names and roles (e.g., "Click the Save button").

### ✨ Why use Tarsier over Vision Models?
* 🚀 **Zero Vision Models Needed:** Completely eliminates the need for multimodal vision models.
* 📉 **Extremely Low Token Usage:** An entire desktop UI JSON tree is often just a few hundred tokens, compared to the thousands of tokens required for an image.
* 🎯 **100% Deterministic:** No hallucinated XY coordinates or missed clicks if a window resizes or a button moves.
* 🧠 **LLM Friendly:** Large Language Models are fundamentally text-processing engines. Parsing a semantic JSON tree and returning text commands is what they do best!

> [!WARNING]
> **Important:** Tarsier is **NOT** an autonomous AI agent. It has no intelligence, no reasoning, and no ability to plan. It is purely the deterministic "hands and eyes" infrastructure designed to be controlled by *your* LLM systems, MCP servers, or automation scripts.

---

## 💻 Supported OS
Tarsier is currently built specifically for **Windows**. Support for macOS and Linux accessibility trees is planned for the future.

---

## 🚀 What Tarsier CAN Do
* ✅ **Extract UI State:** Recursively dump the semantic layout of an app (buttons, textboxes, tabs, menus) into LLM-friendly JSON.
* ✅ **Semantic Targeting:** Query elements by their semantic properties (e.g., `role="button"`, `name="Save"`).
* ✅ **Semantic Actions:** Perform clicks, double-clicks, and text input directly on the targeted elements.
* ✅ **Cross-App Support:** Works on standard Win32 apps (Notepad) and modern UWP apps (Calculator).
* ✅ **Electron Support:** Can interact with accessibility-enabled Electron apps (like VS Code).

## 🛑 What Tarsier CANNOT Do
* ❌ Understand raw coordinate-based clicking (e.g., "click pixel 300x500").
* ❌ Interact with video games or hardware-accelerated canvases that don't expose accessibility trees.
* ❌ Solve Captchas, parse raw images, or run OCR pipelines.
* ❌ Think for itself or plan autonomous agent workflows.

---

## 📦 Installation

You can install Tarsier directly from PyPI:

```bash
pip install tarsier
```

Alternatively, to install from source for development:

```bash
git clone https://github.com/siddzzzz/Tarsier.git
cd Tarsier
pip install -r requirements.txt
```

---

## 🛠️ Usage & Examples

### 1. Opening an App
Start by creating a Desktop session and launching an application.

```python
from tarsier import Desktop

desktop = Desktop()
notepad = desktop.open_app("notepad.exe", window_name="Notepad")
```

### 2. Dumping the "Desktop DOM" (Output Format)
Tarsier serializes the desktop state into a semantic JSON tree. This is exactly what you should feed to your LLM agent.

```python
ui_state_json = notepad.to_json()
print(ui_state_json)
```

**Example JSON Output:**
```json
{
  "role": "window",
  "name": "Untitled - Notepad",
  "elements": [
    {
      "role": "document",
      "name": "Text editor"
    },
    {
      "role": "menubar",
      "name": "System"
    },
    {
      "role": "button",
      "name": "Maximize"
    }
  ]
}
```

### 3. Finding Elements
You can query elements exactly like you would use query selectors in the browser.

```python
# Generic find by role and name
save_btn = notepad.find(role="button", name="Save")

# Convenience wrappers
my_button = notepad.button("Submit")
my_text_box = notepad.textbox("Username")
my_menu_item = notepad.menu("File")
```

### 4. Semantic Interaction
Once you have an element, you can interact with it deterministically. No coordinates required!

```python
# Click a button
notepad.button("Save").click()

# Double click
notepad.button("Folder").double_click()

# Type into a textbox instantly (uses clipboard injection to bypass OS racing)
editor = notepad.textbox()
editor.type("Hello from Tarsier!")

# Focus a specific element to ensure keystrokes land properly
editor.focus()
```

---

## 🎮 Included Demos
Check out the `examples/` directory for full working implementations:
* `notepad_demo.py`: Opens Notepad, writes text, saves the file semantically.
* `calculator_demo.py`: Operates the modern Windows Calculator app using pure semantic button queries.
* `vscode_demo.py`: Opens VS Code, navigates the Windows OS file explorer dialogs, creates a workspace, writes Python code, and runs it!

---

<div align="center">
  <p>Built with ❤️ for deterministic local AI.</p>
</div>