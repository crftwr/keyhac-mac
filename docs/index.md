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

Global KeyTable is a KeyTable that is applied always, regardless of the current focused application. `keymap.define_keytable(focus_path_pattern="*")` can be used to create a global KeyTable. `*` is passed to the argument `focus_path_pattern`, so that this KeyTable matches any focus conditions.

KeyTable object can be used like a dictionary. You can associate input key conditions with 1) output keys, 2) output key sequences, 3) Python executable objects like functions and class instances.

``` python
keytable_global["Fn-J"] = "Left"
keytable_global["Fn-N"] = "1", "2", "3"
keytable_global["Fn-M"] = hello_world
```


## Define application/focus specific keytables




## Key -> Key


## Key -> functions/classes


## Multi-stroke key-table

## Replace keys


## Define modifiers


## One-shot modifiers


## Built-in Action classes


## 



