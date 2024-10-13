import json

import keyhac_core


hook = keyhac_core.Hook()

if 1:
    VK_A                    = 0x00
    VK_S                    = 0x01
    VK_D                    = 0x02
    VK_F                    = 0x03
    VK_H                    = 0x04
    VK_G                    = 0x05
    VK_Z                    = 0x06
    VK_X                    = 0x07
    VK_C                    = 0x08
    VK_V                    = 0x09
    VK_B                    = 0x0B
    VK_Q                    = 0x0C
    VK_W                    = 0x0D
    VK_E                    = 0x0E
    VK_R                    = 0x0F
    VK_Y                    = 0x10
    VK_T                    = 0x11
    VK_1                    = 0x12
    VK_2                    = 0x13
    VK_3                    = 0x14
    VK_4                    = 0x15
    VK_6                    = 0x16
    VK_5                    = 0x17
    VK_PLUS                 = 0x18
    VK_9                    = 0x19
    VK_7                    = 0x1A
    VK_MINUS                = 0x1B
    VK_8                    = 0x1C
    VK_0                    = 0x1D
    VK_CLOSEBRACKET         = 0x1E
    VK_O                    = 0x1F
    VK_U                    = 0x20
    VK_OPENBRACKET          = 0x21
    VK_I                    = 0x22
    VK_P                    = 0x23
    VK_L                    = 0x25
    VK_J                    = 0x26
    VK_QUOTE                = 0x27
    VK_K                    = 0x28
    VK_SEMICOLON            = 0x29
    VK_BACKSLASH            = 0x2A
    VK_COMMA                = 0x2B
    VK_SLASH                = 0x2C
    VK_N                    = 0x2D
    VK_M                    = 0x2E
    VK_PERIOD               = 0x2F
    VK_GRAVE                = 0x32

    VK_DECIMAL              = 0x41
    VK_MULTIPLY             = 0x43
    VK_ADD                  = 0x45
    #VK_KeypadClear          = 0x47
    VK_DIVIDE               = 0x4B
    #VK_KeypadEnter          = 0x4C
    VK_SUBTRACT             = 0x4E
    VK_NUMPADEQUAL          = 0x51
    VK_NUMPAD0              = 0x52
    VK_NUMPAD1              = 0x53
    VK_NUMPAD2              = 0x54
    VK_NUMPAD3              = 0x55
    VK_NUMPAD4              = 0x56
    VK_NUMPAD5              = 0x57
    VK_NUMPAD6              = 0x58
    VK_NUMPAD7              = 0x59
    VK_NUMPAD8              = 0x5B
    VK_NUMPAD9              = 0x5C

    VK_RETURN               = 0x24
    VK_TAB                  = 0x30
    VK_SPACE                = 0x31
    VK_BACK                 = 0x33
    VK_ESCAPE               = 0x35
    VK_RCOMMAND             = 0x36
    VK_LCOMMAND             = 0x37
    VK_LSHIFT               = 0x38
    VK_CAPITAL              = 0x39
    VK_LMENU                = 0x3A
    VK_LCONTROL             = 0x3B
    VK_RSHIFT               = 0x3C
    VK_RMENU                = 0x3D
    VK_RCONTROL             = 0x3E
    VK_FUNCTION             = 0x3F
    VK_F17                  = 0x40
    #VK_VolumeUp             = 0x48
    #VK_VolumeDown           = 0x49
    #VK_Mute                 = 0x4A
    VK_F18                  = 0x4F
    VK_F19                  = 0x50
    VK_F20                  = 0x5A
    VK_F5                   = 0x60
    VK_F6                   = 0x61
    VK_F7                   = 0x62
    VK_F3                   = 0x63
    VK_F8                   = 0x64
    VK_F9                   = 0x65
    VK_F11                  = 0x67
    VK_F13                  = 0x69
    VK_F16                  = 0x6A
    VK_F14                  = 0x6B
    VK_F10                  = 0x6D
    VK_F12                  = 0x6F
    VK_F15                  = 0x71
    VK_HELP                 = 0x72
    VK_HOME                 = 0x73
    VK_PRIOR                = 0x74
    VK_DELETE               = 0x75
    VK_F4                   = 0x76
    VK_END                  = 0x77
    VK_F2                   = 0x78
    VK_NEXT                 = 0x79
    VK_F1                   = 0x7A
    VK_LEFT                 = 0x7B
    VK_RIGHT                = 0x7C
    VK_DOWN                 = 0x7D
    VK_UP                   = 0x7E

    # ISO keyboards only
    VK_ISO_Section          = 0x0A

    # JIS keyboards only
    VK_YEN                  = 0x5D
    VK_UNDERSCORE           = 0x5E
    VK_KeypadComma          = 0x5F
    VK_Eisu                 = 0x66
    VK_Kana                 = 0x68


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
        
        if keyCode == VK_A:
            hook.sendKeyboardEvent("keyDown", VK_S)
            return True
        elif keyCode == VK_S:
            hook.sendKeyboardEvent("keyDown", VK_A)
            return True
        elif keyCode == VK_LEFT:
            hook.sendKeyboardEvent("keyDown", VK_RIGHT)
            return True
        elif keyCode == VK_RIGHT:
            hook.sendKeyboardEvent("keyDown", VK_LEFT)
            return True

        return False

    def onKeyUp(self, keyCode):
        print("Keymap.onKeyUp", keyCode)
        
        # FIXME: KeyUpを対応させないと、ApplePressAndHoldEnabled が有効な時に問題が起きる

        """
        if keyCode == VK_A:
            hook.sendKeyboardEvent("keyUp", VK_S)
            return True
        elif keyCode == VK_S:
            hook.sendKeyboardEvent("keyUp", VK_A)
            return True
        """

        return False


def configure():
    Keymap.getInstance().enableKeyboardHook()
