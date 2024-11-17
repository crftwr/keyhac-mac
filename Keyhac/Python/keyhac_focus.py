import fnmatch
import traceback
from collections.abc import Callable

from keyhac_core import UIElement
import keyhac_console

logger = keyhac_console.getLogger("Focus")

class FocusCondition:

    """
    A class to define keyboard focus condition
    """

    def __init__( self, focus_path_pattern: str = None, custom_condition_func: Callable = None ):

        """
        Initialize the focus condition.

        Args:
            focus_path_pattern: Focus path pattern string with wildcards.
            custom_condition_func: A function to define custom focus condition.
        """

        self.focus_path_pattern = focus_path_pattern
        self.custom_condition_func = custom_condition_func

    def check( self, focus_path: str, focus_elm: UIElement ) -> bool:

        """
        Check if the current focus meets the condition.

        Args:
            focus_path: Focus path string
            focus_elm: Focused UI element

        Returns:
            Boolean result whether the condition met.
        """

        if self.focus_path_pattern and ( not focus_path or not fnmatch.fnmatch( focus_path, self.focus_path_pattern ) ):
            return False
        
        try:
            if self.custom_condition_func and ( not focus_elm or not self.custom_condition_func(focus_elm) ):
                return False
        except Exception as e:
            print()
            logger.error(f"Running custom focus condition function failed:\n{traceback.format_exc()}")
            return False

        return True

    @staticmethod
    def get_focus_path(elm: UIElement) -> str:

        """
        Get a string representation for the focused UI element.

        Args:
            elm: Focused UI element.

        Returns:
            Focus path string.
        """

        focus_elms = []

        while elm:
            focus_elms.append(elm)
            elm = elm.getAttributeValue("AXParent")

        focus_path_components = [""]

        special_chars_trans_table = str.maketrans({
            "(":  r"<",
            ")":  r">",
            "/":  r"-",
            "*":  r"-",
            "?":  r"-",
            "[":  r"<",
            "]":  r">",
            ":":  r"-",
            "\n": r" ",
            "\t": r" ",
        })

        for elm in reversed(focus_elms):

            role = elm.getAttributeValue("AXRole")
            if role is None: role = ""
            role = role.translate(special_chars_trans_table)

            title = elm.getAttributeValue("AXTitle")
            if title is None: title = ""
            title = title.translate(special_chars_trans_table)

            focus_path_components.append( f"{role}({title})" )

        focus_path = "/".join(focus_path_components)

        return focus_path
