from typing import Any

class Hook:
    pass

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
    def write(s):
        pass
