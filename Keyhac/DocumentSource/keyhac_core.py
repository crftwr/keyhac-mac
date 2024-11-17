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
