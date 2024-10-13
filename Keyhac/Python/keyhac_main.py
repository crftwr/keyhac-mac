import json

import keyhac_core


hook = keyhac_core.Hook()

class Keymap:
    
    _instance = None
            
    @staticmethod
    def getInstance():
        if not Keymap._instance:
            Keymap._instance = Keymap()
        return Keymap._instance

    def __init__(self):
        pass

    def enableKeyboardHook(self):
    
        def _onKey(s):
            d = json.loads(s)
            if d["type"]=="keyDown":
                return self.onKeyDown(d["keyCode"])
            elif d["type"]=="keyUp":
                return self.onKeyUp(d["keyCode"])

        hook.setCallback("Keyboard", _onKey)

    def onKeyDown(self, keyCode):
        print("Keymap.onKeyDown", keyCode)
        return False

    def onKeyUp(self, keyCode):
        print("Keymap.onKeyUp", keyCode)
        return False


def configure():
    Keymap.getInstance().enableKeyboardHook()
