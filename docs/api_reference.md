
## Keyhac API reference
---

### <kbd>class</kbd> `Keymap`
A keymap management class. Keymap class manages key-tables and executes key action translations. 

### <kbd>method</kbd> `Keymap.__init__`

```python
__init__()
```

Initializes keymap object. 


---

##### <kbd>property</kbd> Keymap.clipboard_history

ClipboardHistory object 

---

##### <kbd>property</kbd> Keymap.focus

Current focused UI element 



---

#### <kbd>method</kbd> `Keymap.configure`

```python
configure()
```

Reload configuration file and reconfigure the keymap. 

---

#### <kbd>method</kbd> `Keymap.define_keytable`

```python
define_keytable(
    name: str = None,
    focus_path_pattern: str = None,
    custom_condition_func: collections.abc.Callable = None
) → KeyTable
```

Define a key table. 

When focus_path_pattern and/or custom_condition_func were specified,  the key table is added to the Keymap object and it automatically activates when focus condtion met. 

When focus_path_pattern and custom_condition_func were not specified, the key table is not added to the Keymap object. The key table can be used to define multi-stroke key table. 



**Args:**
 
 - <b>`name`</b>:  Name of the key table. 
 - <b>`focus_path_pattern`</b>:  Focus path pattern with wildcards. 
 - <b>`custom_condition_func`</b>:  A function to define custom focus condition. 



**Returns:**
 KeyTable created 

---

#### <kbd>method</kbd> `Keymap.define_modifier`

```python
define_modifier(key: str | int, mod: str | int) → None
```

Define a user modifier key. 



**Args:**
 
 - <b>`key`</b>:  Key to use as the new modifier key 
 - <b>`mod`</b>:  Modifier key assigned to the key 

---

#### <kbd>method</kbd> `Keymap.get_input_context`

```python
get_input_context(replay=False) → InputContext
```

Get a key input context to send virtual key input sequence. 

Use this method to get a key input context object and to programmatically send virtual keys. 



**Args:**
 
 - <b>`replay`</b>:  Set `replay` mode to re-evaluate injected key events by the Keymap 



**Returns:**
 Key input context 

---

#### <kbd>method</kbd> `Keymap.get_instance`

```python
get_instance()
```

Get the Keymap singleton instance. 



**Returns:**
  Keymap singleton instance. 

---

#### <kbd>method</kbd> `Keymap.replace_key`

```python
replace_key(src: str | int, dst: str | int) → None
```

Replace a key with a different key. 



**Args:**
 
 - <b>`src`</b>:  Key to replace 
 - <b>`dst`</b>:  New meaning of the key 


---


### <kbd>class</kbd> `KeyTable`
A key table class 

KeyTable object can be used like a dictionary, to assign input key conditions to output key actions. 

### <kbd>method</kbd> `KeyTable.__init__`

```python
__init__(name=None)
```









---


### <kbd>class</kbd> `KeyCondition`
A key condition class. 

KeyCondition class is used to represent a single key stroke. It also provides ways to convert string expressions and internal key codes. 

### <kbd>method</kbd> `KeyCondition.__init__`

```python
__init__(vk: int, mod: int = 0, down: bool = True, oneshot: bool = False)
```

Initializes a key condition object. 



**Args:**
 
 - <b>`vk`</b>:  Key code. 
 - <b>`mod`</b>:  Modifier key bits. 
 - <b>`down`</b>:  Key down or up. 
 - <b>`oneshot`</b>:  One-shot key. 




---

#### <kbd>method</kbd> `KeyCondition.from_str`

```python
from_str(s: str)
```

Create a key condition from a string expression 



**Args:**
 
 - <b>`vk`</b>:  Key code. 
 - <b>`mod`</b>:  Modifier key bits. 
 - <b>`down`</b>:  Key down or up. 
 - <b>`oneshot`</b>:  One-shot key. 



**Returns:**
 KeyCondition object created 

---

#### <kbd>method</kbd> `KeyCondition.init_vk_str_tables`

```python
init_vk_str_tables() → None
```

Detect keyboard type and initialize internal key code translation tables. 

---

#### <kbd>method</kbd> `KeyCondition.mod_eq`

```python
mod_eq(mod1, mod2)
```





---

#### <kbd>method</kbd> `KeyCondition.str_to_mod`

```python
str_to_mod(name, force_LR=False)
```

Convert a string expression of a modifier key to modifier bits 



**Args:**
 
 - <b>`name`</b>:  Name of the modifier key. 
 - <b>`force_LR`</b>:  Whether distinguish left/right variations of the modifier keys 



**Returns:**
 Modifier bits. 

---

#### <kbd>method</kbd> `KeyCondition.str_to_vk`

```python
str_to_vk(name: str) → int
```

Convert a string expression of a key to key code 



**Args:**
 
 - <b>`name`</b>:  Name of the key. 



**Returns:**
 Key code of the key. 

---

#### <kbd>method</kbd> `KeyCondition.vk_to_str`

```python
vk_to_str(vk: int) → str
```

Convert a key code to a string expression of the key 



**Args:**
 
 - <b>`vk`</b>:  Key code 



**Returns:**
 String expression of the key 


---


### <kbd>class</kbd> `FocusCondition`
A class to define keyboard focus condition 

### <kbd>method</kbd> `FocusCondition.__init__`

```python
__init__(
    focus_path_pattern: str = None,
    custom_condition_func: collections.abc.Callable = None
)
```

Initialize the focus condition. 



**Args:**
 
 - <b>`focus_path_pattern`</b>:  Focus path pattern string with wildcards. 
 - <b>`custom_condition_func`</b>:  A function to define custom focus condition. 




---

#### <kbd>method</kbd> `FocusCondition.check`

```python
check(focus_path: str, focus_elm: keyhac_core.UIElement) → bool
```

Check if the current focus meets the condition. 



**Args:**
 
 - <b>`focus_path`</b>:  Focus path string 
 - <b>`focus_elm`</b>:  Focused UI element 



**Returns:**
 Boolean result whether the condition met. 

---

#### <kbd>method</kbd> `FocusCondition.get_focus_path`

```python
get_focus_path(elm: keyhac_core.UIElement) → str
```

Get a string representation for the focused UI element. 



**Args:**
 
 - <b>`elm`</b>:  Focused UI element. 



**Returns:**
 Focus path string. 


---


### <kbd>class</kbd> `InputContext`
A class to send multiple key strokes 

InputContext object sends virtual key events by managing current real key state and virtual key state. To create InputContext object, use Keymap.get_input_context(). Don't directly use InputContext.__init__(). 

Use with statement to call the Keymap.get_input_context(). Key events are accumerated in this object,  and sent at once when leaving the context. 

usage:  with keymap.get_input_context() as input_ctx:  input_ctx.send_key("Cmd-Left")  input_ctx.send_key("Cmd-Shift-Right") 

### <kbd>method</kbd> `InputContext.__init__`

```python
__init__(keymap, replay=False)
```

Initialize the input context. To create InputContext object, use Keymap.get_input_context(). Don't directly use InputContext.__init__(). 




---

#### <kbd>method</kbd> `InputContext.send_key`

```python
send_key(s: str) → None
```

Send a key stroke using a string expression. (e.g., "Cmd-Left") 



**Args:**
 
 - <b>`s`</b>:  Key expression string 

---

#### <kbd>method</kbd> `InputContext.send_key_by_vk`

```python
send_key_by_vk(vk: int, down: bool = True) → None
```

Send a key stroke with a key code and direction. 



**Args:**
 
 - <b>`vk`</b>:  Key code 
 - <b>`down`</b>:  True: key down, False: key up 

---

#### <kbd>method</kbd> `InputContext.send_modifier_keys`

```python
send_modifier_keys(mod: int)
```

Send modifier key events to match the target modifier state 



**Args:**
 
 - <b>`mod`</b>:  Target modifier state 


---


### <kbd>class</kbd> `MoveWindow`
A action class to move focused window 

### <kbd>method</kbd> `MoveWindow.__init__`

```python
__init__(
    x: int = None,
    y: int = None,
    direction: str = '',
    distance: float = inf,
    window_edge: bool = False
)
```

Initializes the action object. 



**Args:**
 
 - <b>`direction`</b>:  either of "left", "right", "up", "down" 
 - <b>`distance`</b>:  move amount 
 - <b>`window_edge`</b>:  whether window stops and fits to other window's edge 




---

#### <kbd>method</kbd> `MoveWindow.finished`

```python
finished(result: Any)
```





---

#### <kbd>method</kbd> `MoveWindow.run`

```python
run()
```





---

#### <kbd>method</kbd> `MoveWindow.starting`

```python
starting()
```

Virtual method called immediately when the action is triggered. 


---


### <kbd>class</kbd> `LaunchApplication`
A action class to launch an application. 

This action launches the application you specified if it is not running yet. If the application is already running, macOS automatically make it foreground. 

### <kbd>method</kbd> `LaunchApplication.__init__`

```python
__init__(app_name)
```

Initializes the action object. 



**Args:**
 
 - <b>`app_name`</b>:  Name of the application (e.g., "Terminal.app") 




---

#### <kbd>method</kbd> `LaunchApplication.finished`

```python
finished(result: Any) → None
```

Virtual method called after run() finished. 



**Args:**
 
 - <b>`result`</b>:  returned value from run(). 

---

#### <kbd>method</kbd> `LaunchApplication.run`

```python
run()
```





---

#### <kbd>method</kbd> `LaunchApplication.starting`

```python
starting()
```

Virtual method called immediately when the action is triggered. 


---


### <kbd>class</kbd> `ThreadedAction`
Base class for threaded actions. 

To run a time consuming task as an output key action, you need to use threads. ThreadedAction helps to define threaded action classes easily. 

To define your own threaded action class, derive the ThreadedAction class and implement starting(), run(), and finished() methods. The run() method is executed in a thread pool for time consuming tasks. The starting() and finished() methods are for light-weight tasks and they are executed before and after run() under exclusive control with keyboard hooks.  

### <kbd>method</kbd> `ThreadedAction.__init__`

```python
__init__()
```








---

#### <kbd>method</kbd> `ThreadedAction.finished`

```python
finished(result: Any) → None
```

Virtual method called after run() finished. 



**Args:**
 
 - <b>`result`</b>:  returned value from run(). 

---

#### <kbd>method</kbd> `ThreadedAction.run`

```python
run() → Any
```

Virtual method called in the thread pool. 

This method can include time consuming tasks. 



**Returns:**
  Any types of objects 

---

#### <kbd>method</kbd> `ThreadedAction.starting`

```python
starting()
```

Virtual method called immediately when the action is triggered. 


---


### <kbd>class</kbd> `ShowClipboardHistory`
Action class to show clipboard history with Chooser window. 

### <kbd>method</kbd> `ShowClipboardHistory.__init__`

```python
__init__()
```

Initializes the ShowClipboardHistory object. 




---

#### <kbd>method</kbd> `ShowClipboardHistory.list_items`

```python
list_items()
```





---

#### <kbd>method</kbd> `ShowClipboardHistory.on_chosen`

```python
on_chosen(item, modifier_flags: int)
```






---


### <kbd>class</kbd> `ShowClipboardSnippets`
Action class to show clipboard snippets with Chooser window. 

### <kbd>method</kbd> `ShowClipboardSnippets.__init__`

```python
__init__(snippets)
```

Initializes the ShowClipboardSnippets object. 




---

#### <kbd>method</kbd> `ShowClipboardSnippets.list_items`

```python
list_items()
```





---

#### <kbd>method</kbd> `ShowClipboardSnippets.on_chosen`

```python
on_chosen(item, modifier_flags: int)
```






---


### <kbd>class</kbd> `ShowClipboardTools`
Action class to show clipboard conversion tools with Chooser window. 

### <kbd>method</kbd> `ShowClipboardTools.__init__`

```python
__init__(tools)
```

Initializes the ShowClipboardTools object. 




---

#### <kbd>method</kbd> `ShowClipboardTools.list_items`

```python
list_items()
```





---

#### <kbd>method</kbd> `ShowClipboardTools.on_chosen`

```python
on_chosen(item, modifier_flags: int)
```





---

#### <kbd>method</kbd> `ShowClipboardTools.quote`

```python
quote(clip)
```

Convert clipboard to quoted string. 

---

#### <kbd>method</kbd> `ShowClipboardTools.to_full_width`

```python
to_full_width(clip)
```

Convert half width characters in clipboard to full width 

---

#### <kbd>method</kbd> `ShowClipboardTools.to_half_width`

```python
to_half_width(clip)
```

Convert full width characters in clipboard to half width 

---

#### <kbd>method</kbd> `ShowClipboardTools.to_plain`

```python
to_plain(clip)
```

Convert clipboard to plain-text. 

---

#### <kbd>method</kbd> `ShowClipboardTools.unindent`

```python
unindent(clip)
```

Remove common white space plex in the clipboard 


---


### <kbd>class</kbd> `StartRecordingKeys`
A action class to start recording keys in replay buffer 

### <kbd>method</kbd> `StartRecordingKeys.__init__`

```python
__init__()
```

Initializes the StartRecordingKeys object. 





---


### <kbd>class</kbd> `StopRecordingKeys`
A action class to stop recording keys in replay buffer 

### <kbd>method</kbd> `StopRecordingKeys.__init__`

```python
__init__()
```

Initializes the StopRecordingKeys object. 





---


### <kbd>class</kbd> `ToggleRecordingKeys`
A action class to start or stop recording keys in replay buffer 

### <kbd>method</kbd> `ToggleRecordingKeys.__init__`

```python
__init__()
```

Initializes the ToggleRecordingKeys object. 





---


### <kbd>class</kbd> `PlaybackRecordedKeys`
A action class to playback recorded keys in replay buffer 

### <kbd>method</kbd> `PlaybackRecordedKeys.__init__`

```python
__init__()
```

Initializes the PlaybackRecordedKeys object. 





---


### <kbd>class</kbd> `ChooserAction`
Base class for actions to use Chooser window. 

To define your own action class to use Chooser, derive the ChooserAction class and implement list_items() and on_chosen() methods. list_items() is executed when the Chooser opens to list items. on_chosen() is executed when an item is chosen and the Chooser closes. 

### <kbd>method</kbd> `ChooserAction.__init__`

```python
__init__()
```








---

#### <kbd>method</kbd> `ChooserAction.list_items`

```python
list_items()
```

Virtual method to list items. 



**Returns:**
  List of tuple (icon string, label string, ...) 

---

#### <kbd>method</kbd> `ChooserAction.on_chosen`

```python
on_chosen(item, modifier_flags: int) → None
```

Virtual method to handle chosen item. 



**Args:**
 
 - <b>`item`</b>:  Chosen item 
 - <b>`modifier_flags`</b>:  Combination of pressed modifier flags (MODKEY_SHIFT, etc) 


---


### <kbd>class</kbd> `UIElement`
UI element class 

UIElement represents multiple types of elements on your system like: 


- Application 
- Window 
- Button 

UIElement has attributes like "AXParent", "AXChildren", "AXRole", "AXPosition" and so on. You can get these attribute values by get_attribute_value(). And you can also set some of these attribute values by set_attribute_value(). 

You can also interact with UIElements using perform_action().  For example, you can click buttons by `elm.perform_action("AXPress")`. 

It is a wrapper of macOS's accessibility object. 




---

#### <kbd>method</kbd> `UIElement.get_action_names`

```python
get_action_names() → [<class 'str'>]
```

Get a list of action names this UI element can perform. 



**Returns:**
  A list of action names. 

---

#### <kbd>method</kbd> `UIElement.get_attribute_names`

```python
get_attribute_names() → [<class 'str'>]
```

Get a list of attribute names this UI element has. 



**Returns:**
  A list of attribute names. 

---

#### <kbd>method</kbd> `UIElement.get_attribute_value`

```python
get_attribute_value(name: str) → Any
```

Get the value of an attribute. 



**Args:**
 
 - <b>`name`</b>:  Name of the attribute 



**Returns:**
 Value of the attribute 

---

#### <kbd>method</kbd> `UIElement.get_focused_application`

```python
get_focused_application()
```

Get current focused application as a UIElement object. 

---

#### <kbd>method</kbd> `UIElement.get_running_applications`

```python
get_running_applications()
```

Get currently running applications in a list of UIElements. 

---

#### <kbd>method</kbd> `UIElement.get_screen_frames`

```python
get_screen_frames()
```

Get a list of position/size of screens (=displays) in [[x,y,width,height],...] format. 

---

#### <kbd>method</kbd> `UIElement.perform_action`

```python
perform_action(name: str) → None
```

Perform an action on this UI element. 



**Args:**
 
 - <b>`name`</b>:  Name of the actiom 

---

#### <kbd>method</kbd> `UIElement.set_attribute_value`

```python
set_attribute_value(name: str, value: Any) → None
```

Set value of an attribute. 



**Args:**
 
 - <b>`name`</b>:  Name of the attribute 
 - <b>`value`</b>:  Value of the attribute 


---


### <kbd>class</kbd> `ClipboardHistory`
Clipboard history 

ClipboardHistory object automatically captures historical clipboard contents. Currently this class only supports text data. 

ClipboardHistory class has following class variables to configure the maximum length and data size: 
- max_items: Maximum number of clipboard history item to keep (default: 1000 items) 
- max_label_length: Maximum length of label strings of clipboard items (default: 4096 bytes) 
- max_data_size: Maximum data size of single clipboard to keep (default: 10 * 1024 * 1024 = 10MB) 
- max_persist_data_size: Maximum data size of single clipboard to save in persistent file (default: 64 * 1024 = 64KB) 

### <kbd>method</kbd> `ClipboardHistory.__init__`

```python
__init__()
```

Initializes the ClipboardHistory object. 

Loads saved clipboard history data from file (`~/.keyhac/clipboard.json`), and installs clipboard hook to the OS. 




---

#### <kbd>method</kbd> `ClipboardHistory.add_item`

```python
add_item(clip: keyhac_core.Clipboard) → None
```

Add a Clipboard object to the history. 

Existing duplicate items are automatically deleted. 



**Args:**
 
 - <b>`clip`</b>:  Clipboard object to add 

---

#### <kbd>method</kbd> `ClipboardHistory.get_current`

```python
get_current() → Clipboard
```

Get the current Clipboard object from the clipboard history. 



**Returns:**
  Current Clipboard object  

---

#### <kbd>method</kbd> `ClipboardHistory.items`

```python
items()
```

Iterates the list of Clipboard objects. 

First item is the latest. 



**Returns:**
  Clipboard object and shortened label (Clipboard, str) 

---

#### <kbd>method</kbd> `ClipboardHistory.set_current`

```python
set_current(clip: keyhac_core.Clipboard) → None
```

Set a Clipboard object to the OS's clipboard and latest entry of the clipboard history 



**Args:**
 
 - <b>`clip`</b>:  Clipboard object to set 


---


### <kbd>class</kbd> `Console`







---

#### <kbd>method</kbd> `Console.set_text`

```python
set_text(name: str, text: str)
```

Set a text for special text field. 

Keyhac automatically use this API to update the "Last key"  and "Focus path" field in the Keyhac Console window. So you don't usually have to use this API directly. 



**Args:**
 
 - <b>`name`</b>:  "lastKey" or "focusPath" 
 - <b>`text`</b>:  Contents of the special text field. 

---

#### <kbd>method</kbd> `Console.write`

```python
write(s: str, log_level: int = 100) → None
```

Write log to Keyhac Console. 

Keyhac automatically redirect sys.stdout / sys.stderr to the Keyhac Console. So you don't usually have to use this API directly. 

You can also use Logger object from getLogger() to write logs to the Keyhac Console. 



**Args:**
 
 - <b>`s`</b>:  Log message. 
 - <b>`log_level`</b>:  Log level. 


---


### <kbd>class</kbd> `Hook`
Keyhac core hook system. 




---

#### <kbd>method</kbd> `Hook.acquire_lock`

```python
acquire_lock() → None
```

Acquire the lock for hooks. 

Acquire the internal recursive lock object to control exclusive execution with hook functions. Keyhac calls this function automatically to make InputContext thread-safe. 

---

#### <kbd>method</kbd> `Hook.get_keyboard_layout`

```python
get_keyboard_layout() → str
```

Get the current keyboard layout. 

Keyhac calls this function automatically and configure the key expression string table. 



**Returns:**
  "ansi" / "jis" / "iso" / "unknown" 

---

#### <kbd>method</kbd> `Hook.release_lock`

```python
release_lock() → None
```

Release the lock for hooks. 

Release the internal recursive lock object to control exclusive execution with hook functions. Keyhac calls this function automatically to make InputContext thread-safe. 

---

#### <kbd>method</kbd> `Hook.send_keyboard_event`

```python
send_keyboard_event(event_type: str, key: int) → None
```

Send a virtual key input event. 

Keyhac automatically handles virtual key inputs via InputContext class. So you don't usually have to use this API directly. 



**Args:**
 
 - <b>`event_type`</b>:  "keyDown" or "keyUp" 
 - <b>`key`</b>:  keyCode 

---

#### <kbd>method</kbd> `Hook.set_callback`

```python
set_callback(name: str, func: collections.abc.Callable) → None
```

Set a callback to Keyhac's core hook system. 

Keyhac automatically sets callbacks to the core hook system. So you don't usually have to use this API directly. 



**Args:**
 
 - <b>`name`</b>:  name of the hook. Currently only "Keyboard" is supported. 
 - <b>`func`</b>:  callback function 


---


### <kbd>class</kbd> `Clipboard`
Clipboard data 

### <kbd>method</kbd> `Clipboard.__init__`

```python
__init__()
```

Initializes the Clipboard object with empty content. 




---

#### <kbd>method</kbd> `Clipboard.destroy`

```python
destroy() → None
```

Releases clipboard data. 

---

#### <kbd>method</kbd> `Clipboard.get_current`

```python
get_current()
```

Get the current Clipboard object from the OS. 



**Returns:**
  Current Clipboard object 

---

#### <kbd>method</kbd> `Clipboard.get_string`

```python
get_string() → str
```

Get the string data from the Clipboard. 

---

#### <kbd>method</kbd> `Clipboard.set_current`

```python
set_current(clip) → None
```

Set a Clipboard object to the OS's clipboard. 



**Args:**
 
 - <b>`clip`</b>:  Clipboard object to set 

---

#### <kbd>method</kbd> `Clipboard.set_string`

```python
set_string(s: str) → None
```

Set a string data in the Clipboard object. 



**Args:**
 
 - <b>`s`</b>:  String data to set 


---


### <kbd>class</kbd> `Chooser`
List window 

### <kbd>method</kbd> `Chooser.__init__`

```python
__init__(
    name: str,
    items: (<class 'str'>, <class 'str'>),
    on_selected,
    on_canceled
)
```

Initializes the Chooser object. 

Argumeng `items` is a sequence (list or tuple) of candidate items. Each candidate item is a tuple of (icon, label, ...). First two elements have to be strings. The tuple can contain any types of optional elements after the first two elements. 



**Args:**
 
 - <b>`name`</b>:  Name of the Chooser object 
 - <b>`items`</b>:  List items. Sequence (list or tuple) of (icon string, label string, ...) 
 - <b>`on_selected`</b>:  Callback function for when an item is selected and decided 
 - <b>`on_canceled`</b>:  Callback function for when Chooser is canceled 




---

#### <kbd>method</kbd> `Chooser.destroy`

```python
destroy() → None
```

Releases retained Python objects 

---

#### <kbd>method</kbd> `Chooser.open`

```python
open(frame: (<class 'int'>, <class 'int'>, <class 'int'>, <class 'int'>)) → None
```

Open Chooser window 



**Args:**
 
 - <b>`frame`</b>:  Poistion and size in screen coordinates. Tuple of int (x,y,width,height). Chooser window will be centered within this rectangle. 


---


### <kbd>function</kbd> `getLogger`

```python
getLogger(name: str) → Logger
```

Create a logger configured for Keyhac Console. 

If there is an existing Logger with the same name, the existing logger returns. 



**Args:**
 
 - <b>`name`</b>:  name of the logger. 



**Returns:**
 Logger object. 

---


Copyright 2024 craftware@gmail.com. All rights reserved.
