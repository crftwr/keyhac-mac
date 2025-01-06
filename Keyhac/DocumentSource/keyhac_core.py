from typing import Any
from collections.abc import Callable


class Hook:

    """
    Keyhac core hook system.
    """

    @staticmethod
    def set_callback(name: str, func: Callable) -> None:
        """
        Set a callback to Keyhac's core hook system.

        Keyhac automatically sets callbacks to the core hook system.
        So you don't usually have to use this API directly.

        Args:
            name: name of the hook. Currently only "Keyboard" is supported.
            func: callback function
        """

    @staticmethod
    def send_keyboard_event(event_type: str, key: int) -> None:
        """
        Send a virtual key input event.

        Keyhac automatically handles virtual key inputs via InputContext class.
        So you don't usually have to use this API directly.

        Args:
            event_type: "keyDown" or "keyUp"
            key: keyCode
        """

    @staticmethod
    def get_keyboard_layout() -> str:
        """
        Get the current keyboard layout.

        Keyhac calls this function automatically and configure the key expression string table.

        Returns:
            "ansi" / "jis" / "iso" / "unknown"
        """

    @staticmethod
    def acquire_lock() -> str:
        """
        Acquire the lock for hooks.

        Acquire the internal recursive lock object to control exclusive execution with hook functions.
        Keyhac calls this function automatically to make InputContext thread-safe.
        """

    @staticmethod
    def release_lock() -> str:
        """
        Release the lock for hooks.

        Release the internal recursive lock object to control exclusive execution with hook functions.
        Keyhac calls this function automatically to make InputContext thread-safe.
        """

class UIElement:

    """
    UI element class

    UIElement represents multiple types of elements on your system like:

    - Application
    - Window
    - Button

    UIElement has attributes like "AXParent", "AXChildren", "AXRole", "AXPosition" and so on.
    You can get these attribute values by get_attribute_value().
    And you can also set some of these attribute values by set_attribute_value().

    You can also interact with UIElements using perform_action(). 
    For example, you can click buttons by `elm.perform_action("AXPress")`.

    It is a wrapper of macOS's accessibility object.
    """
    
    @staticmethod
    def get_focused_application():
        """
        Get current focused application as a UIElement object.
        """

    @staticmethod
    def get_running_applications():
        """
        Get currently running applications in a list of UIElements.
        """

    def get_attribute_names(self) -> [str]:
        """
        Get a list of attribute names this UI element has.

        Returns:
            A list of attribute names.
        """

    def get_attribute_value(self, name: str) -> Any:
        """
        Get the value of an attribute.

        Args:
            name: Name of the attribute

        Returns:
            Value of the attribute
        """

    def set_attribute_value(self, name: str, value: Any) -> None:
        """
        Set value of an attribute.

        Args:
            name: Name of the attribute
            value: Value of the attribute
        """

    def get_action_names(self) -> [str]:
        """
        Get a list of action names this UI element can perform.

        Returns:
            A list of action names.
        """

    def perform_action(self, name: str) -> None:
        """
        Perform an action on this UI element.

        Args:
            name: Name of the actiom
        """

class Console:
    
    @staticmethod
    def write(s: str, log_level: int = 100) -> None:
        """
        Write log to Keyhac Console.

        Keyhac automatically redirect sys.stdout / sys.stderr to the Keyhac Console.
        So you don't usually have to use this API directly.

        You can also use Logger object from getLogger() to write logs to the Keyhac Console.

        Args:
            s: Log message.
            log_level: Log level.
        """

    @staticmethod
    def set_text(name: str, text: str):
        """
        Set a text for special text field.

        Keyhac automatically use this API to update the "Last key" 
        and "Focus path" field in the Keyhac Console window.
        So you don't usually have to use this API directly.

        Args:
            name: "lastKey" or "focusPath"
            text: Contents of the special text field.
        """

class Chooser:

    """
    List window
    """

    def __init__(self, name: str, items: ((str,str)), on_selected, on_canceled ):
        """
        Initializes the Chooser object.

        Argumeng `items` is a sequence (list or tuple) of candidate items.
        Each candidate item is a tuple of (icon, label, ...).
        First two elements have to be strings. The tuple can contain any types of optional elements after the first two elements.

        Args:
            name: Name of the Chooser object
            items: List items. Sequence (list or tuple) of (icon string, label string, ...)
            on_selected: Callback function for when an item is selected and decided
            on_canceled: Callback function for when Chooser is canceled
        """

    def destroy(self) -> None:
        """
        Releases retained Python objects
        """

    def open(self, frame: (int,int,int,int)) -> None:
        """
        Open Chooser window

        Args:
            frame: Poistion and size in screen coordinates. Tuple of int (x,y,width,height). Chooser window will be centered within this rectangle.
        """

class Clipboard:

    """
    Clipboard data
    """
    
    def __init__(self):
        """
        Initializes the Clipboard object with empty content.
        """

    def destroy(self) -> None:
        """
        Releases clipboard data.
        """

    def get_string(self) -> str:
        """
        Get the string data from the Clipboard.
        """

    def set_string(self, s: str) -> None:
        """
        Set a string data in the Clipboard object.

        Args:
            s: String data to set
        """

    @staticmethod
    def get_current():
        """
        Get the current Clipboard object from the OS.

        Returns:
            Current Clipboard object
        """

    @staticmethod
    def set_current(clip) -> None:
        """
        Set a Clipboard object to the OS's clipboard.

        Args:
            clip: Clipboard object to set
        """
