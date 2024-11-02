import fnmatch
import traceback

class FocusCondition:

    def __init__( self, focus_path_pattern=None, custom_condition_func=None ):
        self.focus_path_pattern = focus_path_pattern
        self.custom_condition_func = custom_condition_func

    def check( self, focus_path, focus_elm ):

        if self.focus_path_pattern and ( not focus_path or not fnmatch.fnmatch( focus_path, self.focus_path_pattern ) ) : return False
        
        try:
            if self.custom_condition_func and ( not focus_elm or not self.custom_condition_func(focus_elm) ) : return False
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

        return True
