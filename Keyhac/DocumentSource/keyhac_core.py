from typing import Any
from collections.abc import Callable


class Hook:

    """
    Keyhac core hook system.
    """

    @staticmethod
    def setCallback(name: str, func: Callable) -> None:
        """
        Set a callback to Keyhac's core hook system.

        Keyhac automatically sets callbacks to the core hook system.
        So you don't usually have to use this API directly.

        Args:
            name: name of the hook. Currently only "Keyboard" is supported.
            func: callback function
        """

    @staticmethod
    def sendKeyboardEvent(event_type: str, key: int) -> None:
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
    You can get these attribute values by getAttributeValue().
    And you can also set some of these attribute values by setAttributeValue().

    You can also interact with UIElements using performAction(). 
    For example, you can click buttons by `elm.performAction("AXPress")`.

    It is a wrapper of macOS's accessibility object.
    """
    
    @staticmethod
    def getFocusedApplication():
        """
        Get current focused application as a UIElement object.
        """

    @staticmethod
    def getRunningApplications():
        """
        Get currently running applications in a list of UIElements.
        """

    def getAttributeNames(self) -> [str]:
        """
        Get a list of attribute names this UI element has.

        Returns:
            A list of attribute names.
        """

    def getAttributeValue(self, name: str) -> Any:
        """
        Get the value of an attribute.

        Args:
            name: Name of the attribute

        Returns:
            Value of the attribute
        """

    def setAttributeValue(self, name: str, value: Any) -> None:
        """
        Set value of an attribute.

        Args:
            name: Name of the attribute
            value: Value of the attribute
        """

    def getActionNames(self) -> [str]:
        """
        Get a list of action names this UI element can perform.

        Returns:
            A list of action names.
        """

    def performAction(self, name: str) -> None:
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
    def setText(name: str, text: str):
        """
        Set a text for special text field.

        Keyhac automatically use this API to update the "Last key" 
        and "Focus path" field in the Keyhac Console window.
        So you don't usually have to use this API directly.

        Args:
            name: "lastKey" or "focusPath"
            text: Contents of the special text field.
        """
