# <kbd>class</kbd> `Console`
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
[Static method] Get a string representation for the focused UI element. 
**Args:**
 - <b>`elm`</b>:  Focused UI element. 
**Returns:**
 Focus path string. 
# <kbd>class</kbd> `Hook`
# <kbd>class</kbd> `KeyCondition`
### <kbd>method</kbd> `KeyCondition.__init__`
```python
__init__(vk, mod=0, down=True, oneshot=False)
```
---
## <kbd>method</kbd> `KeyCondition.from_str`
```python
from_str(s)
```
---
## <kbd>method</kbd> `KeyCondition.init_vk_str_tables`
```python
init_vk_str_tables()
```
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
---
## <kbd>method</kbd> `KeyCondition.str_to_vk`
```python
str_to_vk(name)
```
---
## <kbd>method</kbd> `KeyCondition.vk_to_str`
```python
vk_to_str(vk)
```
# <kbd>class</kbd> `KeyTable`
### <kbd>method</kbd> `KeyTable.__init__`
```python
__init__(name=None)
```
# <kbd>class</kbd> `ThreadedAction`
Base class for threaded actions. 
To define your own threaded action class, deribe the ThreadedAction and implement starting, run, and finished methods. run() is executed in a thread, and is for time consuming tasks. starting() and finished() are for light-weight tasks for before and after the time consuming task. 
### <kbd>method</kbd> `ThreadedAction.__init__`
```python
__init__()
```
---
## <kbd>method</kbd> `ThreadedAction.finished`
```python
finished(result)
```
---
## <kbd>method</kbd> `ThreadedAction.run`
```python
run()
```
---
## <kbd>method</kbd> `ThreadedAction.starting`
```python
starting()
```
# <kbd>class</kbd> `UIElement`
# <kbd>function</kbd> `getLogger`
```python
getLogger(name)
```
