## Keyhac for macOS - User Guide Document

(coming soon)

## Console Window features

![](images/console-window-features.png)


## Configuration script structure

Keyhac's configuration file is a Python script (`config.py`), and located under `~/.keyhac`.

``` python
from keyhac import *

def configure(keymap):
    keytable_global = keymap.define_keytable(focus_path_pattern="*")
    keytable_global["Fn-J"] = "Left"
    keytable_global["Fn-K"] = "Down"
    keytable_global["Fn-L"] = "Right"
    keytable_global["Fn-I"] = "Up"

    keytable_xcode = keymap.define_keytable( focus_path_pattern="/AXApplication(Xcode)/*/AXTextArea()" )
    keytable_xcode["Fn-A"] = "Cmd-Left", "Cmd-Left", "Shift-Cmd-Right"
```

The configuration script `config.py` has a function `configure()`. It is called by Keyhac when enabling keyboard hook. You can define key-tables in this function.

The function `configure()` receives a `Keymap` object as an argument. `Keymap` object manages key-tables and executes key action translations.


## Global KeyTable

``` python
keytable_global = keymap.define_keytable(focus_path_pattern="*")
```

Global KeyTable is a KeyTable that is applied always, regardless of the current focused application. `keymap.define_keytable(focus_path_pattern="*")` can be used to create a global KeyTable. `*` is passed to the argument `focus_path_pattern=`, so that this KeyTable matches any focus conditions.

KeyTable object can be used like a dictionary. You can associate input key conditions with 1) output keys, 2) output key sequences, 3) Python executable objects like functions and class instances.

``` python
keytable_global["Fn-J"] = "Left"
keytable_global["Fn-N"] = "1", "2", "3"
keytable_global["Fn-M"] = hello_world
```


## Define application/focus specific keytables

``` python
keytable_xcode = keymap.define_keytable( focus_path_pattern="/AXApplication(Xcode)/*/AXTextArea()" )
```

`keymap.define_keytable()` can be used to create application/focus specific key-tables as well. For the argument `focus_path_pattern=` specify focus path pattern.

Focus path is a Keyhac specific concept to represent the current focused application, window, and UI element.

```
/AXApplication(Mail)/AXWindow(Inbox – 118,569 messages, 4 unread)/AXSplitGroup()/AXSplitGroup()/AXScrollArea()/AXGroup()/AXScrollArea()/AXGroup()/AXGroup()/AXScrollArea()/AXWebArea()
```

When you specify `focus_path_pattern=` you can use wildcard patterns using `*`, `?`, `[]`. For the details of wildcard, see the [Python fnmatch document](https://docs.python.org/3/library/fnmatch.html).


If you need your own logic to check the focus condition, you can pass a function to `custom_condition_func=` as below:

``` python
def is_terminal_window(elm):
    try:
        window_elm = elm.getAttributeValue("AXWindow")
        if window_elm:
            app_elm = window_elm.getAttributeValue("AXParent")
            if app_elm:
                app_title = app_elm.getAttributeValue("AXTitle")
                return app_title in ("Terminal", "iTerm2")
        return False
    except KeyError:
        return False

keytable_terminal = keymap.define_keytable( custom_condition_func = is_terminal_window )
```

## Key -> Key

As the most basic usage of key-tables, you can associate input key condition to output key action.

``` python
keytable_global["Fn-J"] = "Left"
```

Both input key conditions and output key actions are expressed as strings formmated as below:

```
{Modifier1}-{Modifier2}-...{PrimaryKey}
```

Following are some examples:

``` python
"Cmd-X"       # Command + X
"Shift-Alt-Z" # Shift + Option + Z
"Fn-A"        # Fn + A
```

You can assign multiple key strokes using tuple of strings.

``` python
keytable_global["Fn-N"] = "Cmd-1", "Cmd-2", "Cmd-3"
```

## Key -> functions/classes

Keyhac allows you to run any custom actions by associating Python callable objects to key-tables. Below is an example of running a Python function as an output action.

``` python
def hello_world():
    print("Hello World!")

keytable_global["Fn-A"] = hello_world
```

You can use class instances as well by defining `__call__` method in the class and making it callable.

``` python
class MoveWindow:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __call__(self):

        elm = keymap.focus

        while elm:
            role = elm.getAttributeValue("AXRole")
            if role=="AXWindow":
                break
            elm = elm.getAttributeValue("AXParent")

        if elm:
            names = elm.getAttributeNames()
            pos = elm.getAttributeValue("AXPosition")
            pos[0] += self.x
            pos[1] += self.y
            elm.setAttributeValue("AXPosition", "point", pos)

keytable_global["User0-Left"]  = MoveWindow(-10,0)
keytable_global["User0-Right"] = MoveWindow(+10,0)
keytable_global["User0-Up"]    = MoveWindow(0,-10)
keytable_global["User0-Down"]  = MoveWindow(0,+10)
```

## Multi-stroke key-table

As an advanced feature, Keyhac supports multi-stroke key inputs, by creating a KeyTable by `keymap.define_keytable()` and associating it as an action in a different key-table.

``` python
keytable_xcode["Ctrl-X"] = keymap.define_keytable(name="Ctrl-X")
```

In the example above, `keytable_xcode`'s `Ctrl-X` is chained to the multi-stroke key-table. To associate second key stroke conditions, you can use following syntax.

``` python
keytable_xcode["Ctrl-X"]["Ctrl-O"] = "Cmd-O"
```


## Replace keys

Keymap has a key replacement table. `keymap.replace_key()` can be used to add a pair of source key and destination key.

``` python
keymap.replace_key( "RShift", "Back" )
```

The replacement happens before processing key-tables, so input key conditions for key-tables have to use the key after the replacement. 

In the example above, the meaning of Right Shift key is replaced with Back Space key. Right Shift key is not recognized as a Shift key anymore at the stage of processing key-tables.


## Define modifier keys

In addition to standard modifier keys (Shift, Control, Option, Command, and Fn), Keyhac allows you to define additional user modifier keys (User0, User1, for both Left and Right).

``` python
keymap.define_modifier( "RCmd", "RUser0" )
keymap.define_modifier( "RAlt", "RUser1" )
```

Once user modifier keys are defined, you can use `User0`, `User1` (and Left/Right specific variations `LUser0`, `LUser1`, `RUser0`, `RUser1`) in the key-table's key expressions.


## One-shot modifiers

"One-shot modifier" is a special key condition that is triggered when the modifier key is pressed and released without any other keys being pressed during the period.

This is useful especially when you defined user modifier keys, but you still want to use the key for different purpose when it is pressed and released alone.

`O-` prefix can be used to assign one-shot modifier to key-tables.

``` python
keytable_global["O-RAlt"] = "Space"
```

## Built-in action classes

Keyhac provides some built-in action classes for your convenience.

#### ThreadedAction

Keyhac uses keyboard hook to intercept all keystrokes across the system. Keyhac's keyboard hook handlers and user-defined actions are expected to complete their processings quickly to maintain system performance.

`ThreadedAction` can be used as a base class of time-consuming actions. When ThreadedAction (and its child classes) are used as a key action, it uses a thread pool internally to execute the main part of the action, allowing the keyboard hook to return immediately.

``` python
class SomeHeavyAction(ThreadedAction):
    def starting(self):
        # light-weight task when action is triggered

    def run(self):
        # time consuming task executed in thread-pool

    def finished(self, result):
        # light-weight task when the action is completed

keytable_global["User0-Z"] = SomeHeavyAction()
```


## UIElement class

`UIElement` class represents a user interface related object on the system, such as an application, a window, a button, a menu bar, or a text edit field. Keyhac uses the `UIElement` class for two purposes, 1) identify focused application and UI element, 2) operate graphical user interface programmatically by key actions.

`keymap.focus` is a read-only property of Keymap class, and it is a `UIElement` object that represents the current keyboard focus.

Following is an example how to find the Zoom button of the focused window, and click it.

``` python
def zoom_window():

    elm = keymap.focus

    while elm:
        role = elm.getAttributeValue("AXRole")
        if role=="AXWindow":
            break
        elm = elm.getAttributeValue("AXParent")

    if elm:
        names = elm.getAttributeNames()
        if "AXZoomButton" in names:
            elm = elm.getAttributeValue("AXZoomButton")
            if elm:
                actions = elm.getActionNames()
                elm.performAction("AXPress")

keytable_global["Fn-M"] = zoom_window
```

For more details about UIElement, see the Keyhac API reference(work in progress).


## Key expression reference

| Expression    | Key           |
| ------------- | ------------- |
| A - Z         |               |
| 0 - 9         |               |
| Minus         | -             |
| Plus          | +             |
| Comma         | ,             |
| Period        | .             |
| Semicolon     | ;             |
| Colon         | :             |
| Slash         | /             |
| BackQuote     | `             |
| Tilde         | ~             |
| OpenBracket   | [             |
| BackSlash     | \             |
| Yen           | ￥            |
| CloseBracket  | ]             |
| Quote         | '             |
| DoubleQuote   | "             |
| Underscore    | _             |
| Asterisk      | *             |
| Atmark        | @             |
| Caret         | ^             |
| NumLock       |               |
| Divide        | / (ten key)   |
| Multiply      | * (ten key)   |
| Subtract      | - (ten key)   |
| Add           | + (ten key)   |
| Decimal       | . (ten key)   |
| Num0 - Num9   | 0-9 (ten key) |
| F1 - F12      |               |
| Left, Right, Up, Down |       |
| Space         |               |
| Tab           |               |
| Back          | Delete        |
| Enter/Return  |               |
| Escape/Esc    |               |
| CapsLock/Caps/Capital |       |
| Delete        |               |
| Home          |               |
| End           |               |
| PageUp        |               |
| PageDown      |               |
| LAlt          | Left Option   |
| RAlt          | Right Option  |
| LCtrl         | Left Control  |
| RCtrl         | Right Control |
| LShift        | Left Shift    |
| RShift        | Right Shift   |
| LCmd          | Left Command  |
| RCmd          | Right Command |
| Fn            |               |
| (0) - (255)   | Virtual key code |
