import json

import keyhac_core

class Keymap:
    def __init__(self):
        pass
        
    def onKey(self, type, keyCode):
        pass

def keyboardCallback(s):
    print("keyboardCallback", s)
    d = json.loads(s)
    return 0

def configure():

    # Test module level function
    keyhac_core.test1()
    
    hook = keyhac_core.Hook()
    
    hook.setCallback("Keyboard", keyboardCallback)
    #hook.setCallback("Keyboard", None)

#    inputs = [
#        keyhac_core.Input(),
#        keyhac_core.Input(),
#        keyhac_core.Input(),
#    ]
#    hook.sendInputs(inputs)
#
#    hook.destroy()

