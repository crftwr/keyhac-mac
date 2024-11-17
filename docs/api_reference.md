
# <kbd>class</kbd> `Keymap`
A keymap management class. Keymap class manages key-tables and executes key action translations. 

### <kbd>method</kbd> `Keymap.__init__`

```python
__init__()
```

Initializes keymap object. 


---

### <kbd>property</kbd> Keymap.focus

Current focused UI element 



---

## <kbd>method</kbd> `Keymap.configure`

```python
configure()
```

Reload configuration file and reconfigure the keymap. 

---

## <kbd>method</kbd> `Keymap.define_keytable`

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

## <kbd>method</kbd> `Keymap.define_modifier`

```python
define_modifier(key: str | int, mod: str | int) → None
```

Define a user modifier key. 



**Args:**
 
 - <b>`key`</b>:  Key to use as the new modifier key 
 - <b>`mod`</b>:  Modifier key assigned to the key 

---

## <kbd>method</kbd> `Keymap.getInstance`

```python
getInstance()
```

Get the Keymap singleton instance. 



**Returns:**
  Keymap singleton instance. 

---

## <kbd>method</kbd> `Keymap.get_input_context`

```python
get_input_context() → InputContext
```

Get a key input context to send virtual key input sequence. 



**Note:**

> Use this method to programmatically decide what virtual keys to send and avoid instantiating InputContext class directly. 
>Using get_input_context(), InputContext object is initialized correctly based on the current key status. 
>

**Returns:**
  Key input context 

---

## <kbd>method</kbd> `Keymap.replace_key`

```python
replace_key(src: str | int, dst: str | int) → None
```

Replace a key with a different key. 



**Args:**
 
 - <b>`src`</b>:  Key to replace 
 - <b>`dst`</b>:  New meaning of the key 


---


# <kbd>class</kbd> `KeyTable`
A key table class 

KeyTable object can be used like a dictionary, to assign input key conditions to output key actions. 

### <kbd>method</kbd> `KeyTable.__init__`

```python
__init__(name=None)
```









---


# <kbd>class</kbd> `KeyCondition`
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

## <kbd>method</kbd> `KeyCondition.from_str`

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

## <kbd>method</kbd> `KeyCondition.init_vk_str_tables`

```python
init_vk_str_tables() → None
```

Detect keyboard type and initialize internal key code translation tables. 

---

## <kbd>method</kbd> `KeyCondition.mod_eq`

```python
mod_eq(mod1, mod2)
```





---

## <kbd>method</kbd> `KeyCondition.str_to_mod`

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

## <kbd>method</kbd> `KeyCondition.str_to_vk`

```python
str_to_vk(name: str) → int
```

Convert a string expression of a key to key code 



**Args:**
 
 - <b>`name`</b>:  Name of the key. 



**Returns:**
 Key code of the key. 

---

## <kbd>method</kbd> `KeyCondition.vk_to_str`

```python
vk_to_str(vk: int) → str
```

Convert a key code to a string expression of the key 



**Args:**
 
 - <b>`vk`</b>:  Key code 



**Returns:**
 String expression of the key 


---


# <kbd>class</kbd> `FocusCondition`
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

## <kbd>method</kbd> `FocusCondition.check`

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

## <kbd>method</kbd> `FocusCondition.get_focus_path`

```python
get_focus_path(elm: keyhac_core.UIElement) → str
```

Get a string representation for the focused UI element. 



**Args:**
 
 - <b>`elm`</b>:  Focused UI element. 



**Returns:**
 Focus path string. 


---


# <kbd>class</kbd> `ThreadedAction`
Base class for threaded actions. 

To run a time consuming task as an output key action, you need to use threads. ThreadedAction helps to define threaded action classes easily. 

To define your own threaded action class, derive the ThreadedAction class and implement starting(), run(), and finished() methods. run() is executed in a thread pool for time consuming tasks. starting() and finished() are for light-weight tasks  and they are executed before and after run(). 

### <kbd>method</kbd> `ThreadedAction.__init__`

```python
__init__()
```








---

## <kbd>method</kbd> `ThreadedAction.finished`

```python
finished(result: Any) → None
```

Virtual method called after run() finished. 



**Args:**
 
 - <b>`result`</b>:  returned value from run(). 

---

## <kbd>method</kbd> `ThreadedAction.run`

```python
run() → Any
```

Virtual method called in the thread pool. 

This method can include time consuming tasks. 



**Returns:**
  Any types of objects 

---

## <kbd>method</kbd> `ThreadedAction.starting`

```python
starting()
```

Virtual method called immediately when the action is triggered. 


---


# <kbd>class</kbd> `UIElement`








---


# <kbd>class</kbd> `Console`







---

## <kbd>method</kbd> `Console.write`

```python
write(s)
```






---


# <kbd>class</kbd> `Hook`








---


# <kbd>function</kbd> `getLogger`

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

