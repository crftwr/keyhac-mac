import fnmatch
import traceback

from keyhac_const import CONSOLE_STYLE_DEFAULT, CONSOLE_STYLE_ERROR

class FocusCondition:

    def __init__( self, focus_path_pattern=None, custom_condition_func=None ):
        self.focus_path_pattern = focus_path_pattern
        self.custom_condition_func = custom_condition_func

    def check( self, focus_path, focus_elm ):

        if self.focus_path_pattern and ( not focus_path or not fnmatch.fnmatch( focus_path, self.focus_path_pattern ) ):
            return False
        
        try:
            if self.custom_condition_func and ( not focus_elm or not self.custom_condition_func(focus_elm) ):
                return False
        except Exception as e:

            print(CONSOLE_STYLE_ERROR)
            print("ERROR: running custom focus condition function failed:")
            traceback.print_exc()
            print(CONSOLE_STYLE_DEFAULT)

            return False

        return True

    @staticmethod
    def get_focus_path(elm):

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
