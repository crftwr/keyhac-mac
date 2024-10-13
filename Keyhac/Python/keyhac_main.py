
import keyhac_core

def keyboardCallback():
    print("keyboardCallback")
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

