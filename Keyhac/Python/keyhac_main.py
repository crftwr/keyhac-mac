
import keyhac_core

def configure():
    keyhac_core.test1()
    
    hook = keyhac_core.Hook()
    print(hook)
    hook.destroy()
    
