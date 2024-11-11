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


## Key -> functions/classes


## Multi-stroke key-table

## Replace keys


## Define modifiers


## One-shot modifiers


## Built-in Action classes


## 



