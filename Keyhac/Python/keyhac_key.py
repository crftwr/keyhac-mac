from keyhac_const import *
import keyhac_console

logger = keyhac_console.getLogger("Key")

class KeyCondition:

    """
    A key condition class.

    KeyCondition class is used to represent a single key stroke.
    It also provides ways to convert string expressions and internal key codes.
    """

    vk_str_table = {}
    str_vk_table = {}

    vk_str_table_common = {

        VK_A : "A",
        VK_B : "B",
        VK_C : "C",
        VK_D : "D",
        VK_E : "E",
        VK_F : "F",
        VK_G : "G",
        VK_H : "H",
        VK_I : "I",
        VK_J : "J",
        VK_K : "K",
        VK_L : "L",
        VK_M : "M",
        VK_N : "N",
        VK_O : "O",
        VK_P : "P",
        VK_Q : "Q",
        VK_R : "R",
        VK_S : "S",
        VK_T : "T",
        VK_U : "U",
        VK_V : "V",
        VK_W : "W",
        VK_X : "X",
        VK_Y : "Y",
        VK_Z : "Z",

        VK_0 : "0",
        VK_1 : "1",
        VK_2 : "2",
        VK_3 : "3",
        VK_4 : "4",
        VK_5 : "5",
        VK_6 : "6",
        VK_7 : "7",
        VK_8 : "8",
        VK_9 : "9",

        VK_MINUS  : "Minus",
        VK_PLUS   : "Plus",
        VK_COMMA  : "Comma",
        VK_PERIOD : "Period",

        VK_NUMPAD_CLEAR : "NumClear",
        VK_NUMPAD_ENTER : "NumEnter",
        VK_DIVIDE   : "Divide",
        VK_MULTIPLY : "Multiply",
        VK_SUBTRACT : "Subtract",
        VK_ADD      : "Add",
        VK_DECIMAL  : "Decimal",

        VK_NUMPAD0 : "Num0",
        VK_NUMPAD1 : "Num1",
        VK_NUMPAD2 : "Num2",
        VK_NUMPAD3 : "Num3",
        VK_NUMPAD4 : "Num4",
        VK_NUMPAD5 : "Num5",
        VK_NUMPAD6 : "Num6",
        VK_NUMPAD7 : "Num7",
        VK_NUMPAD8 : "Num8",
        VK_NUMPAD9 : "Num9",

        VK_F1  : "F1",
        VK_F2  : "F2",
        VK_F3  : "F3",
        VK_F4  : "F4",
        VK_F5  : "F5",
        VK_F6  : "F6",
        VK_F7  : "F7",
        VK_F8  : "F8",
        VK_F9  : "F9",
        VK_F10 : "F10",
        VK_F11 : "F11",
        VK_F12 : "F12",
        VK_F13 : "F13",
        VK_F14 : "F14",
        VK_F15 : "F15",
        VK_F16 : "F16",
        VK_F17 : "F17",
        VK_F18 : "F18",
        VK_F19 : "F19",
        VK_F20 : "F20",

        VK_LEFT     : "Left",
        VK_RIGHT    : "Right",
        VK_UP       : "Up",
        VK_DOWN     : "Down",
        VK_SPACE    : "Space",
        VK_TAB      : "Tab",
        VK_BACK     : "Back",
        VK_RETURN   : "Return",
        VK_ESCAPE   : "Escape",
        VK_CAPITAL  : "CapsLock",
        #VK_APPS     : "Apps", # FIXME : test on macOS

        #VK_INSERT   : "Insert", # FIXME : test on macOS
        VK_DELETE   : "Delete",
        VK_HOME     : "Home",
        VK_END      : "End",
        VK_NEXT     : "PageDown",
        VK_PRIOR    : "PageUp",

        VK_LALT     : "LAlt",
        VK_RALT     : "RAlt",
        VK_LCONTROL : "LCtrl",
        VK_RCONTROL : "RCtrl",
        VK_LSHIFT   : "LShift",
        VK_RSHIFT   : "RShift",
        VK_LCOMMAND : "LCmd",
        VK_RCOMMAND : "RCmd",
        VK_FUNCTION : "Fn",
    }

    vk_str_table_std = {
        VK_SEMICOLON    : "Semicolon",
        VK_SLASH        : "Slash",
        VK_GRAVE        : "BackQuote",
        VK_OPENBRACKET  : "OpenBracket",
        VK_BACKSLASH    : "BackSlash",
        VK_CLOSEBRACKET : "CloseBracket",
        VK_QUOTE        : "Quote",
    }

    vk_str_table_jpn = {
        #VK_OEM_1        : "Colon", # FIXME : test on macOS
        VK_SLASH        : "Slash",
        #VK_OEM_3        : "Atmark", # FIXME : test on macOS
        VK_OPENBRACKET  : "OpenBracket",
        #VK_OEM_5        : "Yen", # FIXME : test on macOS
        VK_CLOSEBRACKET : "CloseBracket",
        #VK_OEM_7        : "Caret", # FIXME : test on macOS
        VK_BACKSLASH    : "BackSlash",
    }

    str_vk_table_common = {

        "A" : VK_A,
        "B" : VK_B,
        "C" : VK_C,
        "D" : VK_D,
        "E" : VK_E,
        "F" : VK_F,
        "G" : VK_G,
        "H" : VK_H,
        "I" : VK_I,
        "J" : VK_J,
        "K" : VK_K,
        "L" : VK_L,
        "M" : VK_M,
        "N" : VK_N,
        "O" : VK_O,
        "P" : VK_P,
        "Q" : VK_Q,
        "R" : VK_R,
        "S" : VK_S,
        "T" : VK_T,
        "U" : VK_U,
        "V" : VK_V,
        "W" : VK_W,
        "X" : VK_X,
        "Y" : VK_Y,
        "Z" : VK_Z,

        "0" : VK_0,
        "1" : VK_1,
        "2" : VK_2,
        "3" : VK_3,
        "4" : VK_4,
        "5" : VK_5,
        "6" : VK_6,
        "7" : VK_7,
        "8" : VK_8,
        "9" : VK_9,

        "MINUS"  : VK_MINUS,
        "PLUS"   : VK_PLUS,
        "COMMA"  : VK_COMMA,
        "PERIOD" : VK_PERIOD,

        "NumClear" : VK_NUMPAD_CLEAR,
        "NumEnter" : VK_NUMPAD_ENTER,
        "DIVIDE"   : VK_DIVIDE,
        "MULTIPLY" : VK_MULTIPLY,
        "SUBTRACT" : VK_SUBTRACT,
        "ADD"      : VK_ADD,
        "DECIMAL"  : VK_DECIMAL,

        "NUM0" : VK_NUMPAD0,
        "NUM1" : VK_NUMPAD1,
        "NUM2" : VK_NUMPAD2,
        "NUM3" : VK_NUMPAD3,
        "NUM4" : VK_NUMPAD4,
        "NUM5" : VK_NUMPAD5,
        "NUM6" : VK_NUMPAD6,
        "NUM7" : VK_NUMPAD7,
        "NUM8" : VK_NUMPAD8,
        "NUM9" : VK_NUMPAD9,

        "F1"  : VK_F1,
        "F2"  : VK_F2,
        "F3"  : VK_F3,
        "F4"  : VK_F4,
        "F5"  : VK_F5,
        "F6"  : VK_F6,
        "F7"  : VK_F7,
        "F8"  : VK_F8,
        "F9"  : VK_F9,
        "F10" : VK_F10,
        "F11" : VK_F11,
        "F12" : VK_F12,
        "F13" : VK_F13,
        "F14" : VK_F14,
        "F15" : VK_F15,
        "F16" : VK_F16,
        "F17" : VK_F17,
        "F18" : VK_F18,
        "F19" : VK_F19,
        "F20" : VK_F20,

        "LEFT"     : VK_LEFT  ,
        "RIGHT"    : VK_RIGHT ,
        "UP"       : VK_UP    ,
        "DOWN"     : VK_DOWN  ,
        "SPACE"    : VK_SPACE ,
        "TAB"      : VK_TAB   ,
        "BACK"     : VK_BACK  ,
        "RETURN"   : VK_RETURN,
        "ENTER"    : VK_RETURN,
        "ESCAPE"   : VK_ESCAPE,
        "ESC"      : VK_ESCAPE,
        "CAPSLOCK" : VK_CAPITAL,
        "CAPS"     : VK_CAPITAL,
        "CAPITAL"  : VK_CAPITAL,
        #"APPS"     : VK_APPS, # FIXME : test on macOS

        #"INSERT"   : VK_INSERT, # FIXME : test on macOS
        "DELETE"   : VK_DELETE,
        "HOME"     : VK_HOME,
        "END"      : VK_END,
        "PAGEDOWN" : VK_NEXT,
        "PAGEUP"   : VK_PRIOR,

        "ALT"  : VK_LALT,
        "LALT" : VK_LALT,
        "RALT" : VK_RALT,
        "CTRL"  : VK_LCONTROL,
        "LCTRL" : VK_LCONTROL,
        "RCTRL" : VK_RCONTROL,
        "SHIFT"  : VK_LSHIFT,
        "LSHIFT" : VK_LSHIFT,
        "RSHIFT" : VK_RSHIFT,
        "CMD"  : VK_LCOMMAND,
        "LCMD" : VK_LCOMMAND,
        "RCMD" : VK_RCOMMAND,
        "FN" : VK_FUNCTION,
    }

    str_vk_table_std = {

        "SEMICOLON"     : VK_SEMICOLON,
        "COLON"         : VK_SEMICOLON,
        "SLASH"         : VK_SLASH,
        "BACKQUOTE"     : VK_GRAVE,
        #"TILDE"         : VK_OEM_3, # FIXME : test on macOS
        "OPENBRACKET"   : VK_OPENBRACKET,
        "BACKSLASH"     : VK_BACKSLASH,
        "YEN"           : VK_BACKSLASH,
        "CLOSEBRACKET"  : VK_CLOSEBRACKET,
        "QUOTE"         : VK_QUOTE,
        "DOUBLEQUOTE"   : VK_QUOTE,
        "UNDERSCORE"    : VK_MINUS,
        "ASTERISK"      : VK_8,
        "ATMARK"        : VK_2,
        "CARET"         : VK_6,
    }

    str_vk_table_jpn = {

        "SEMICOLON"     : VK_PLUS,
        #"COLON"         : VK_OEM_1, # FIXME : test on macOS
        "SLASH"         : VK_SLASH,
        "BACKQUOTE"     : VK_GRAVE,
        #"TILDE"         : VK_OEM_7, # FIXME : test on macOS
        "OPENBRACKET"   : VK_OPENBRACKET,
        "BACKSLASH"     : VK_BACKSLASH,
        "YEN"           : VK_YEN,
        "CLOSEBRACKET"  : VK_CLOSEBRACKET,
        "QUOTE"         : VK_7,
        "DOUBLEQUOTE"   : VK_2,
        "UNDERSCORE"    : VK_UNDERSCORE,
        #"ASTERISK"      : VK_OEM_1, # FIXME : test on macOS
        #"ATMARK"        : VK_OEM_3, # FIXME : test on macOS
        #"CARET"         : VK_OEM_7, # FIXME : test on macOS
    }

    str_mod_table = {

        "ALT"   :  MODKEY_ALT,
        "CTRL"  :  MODKEY_CTRL,
        "SHIFT" :  MODKEY_SHIFT,
        "WIN"   :  MODKEY_WIN,
        "CMD"   :  MODKEY_CMD,
        "FN"    :  MODKEY_FN,
        "USER0" :  MODKEY_USER0,
        "USER1" :  MODKEY_USER1,

        "LALT"   :  MODKEY_ALT_L,
        "LCTRL"  :  MODKEY_CTRL_L,
        "LSHIFT" :  MODKEY_SHIFT_L,
        "LWIN"   :  MODKEY_WIN_L,
        "LCMD"   :  MODKEY_CMD_L,
        "LUSER0" :  MODKEY_USER0_L,
        "LUSER1" :  MODKEY_USER1_L,

        "RALT"   :  MODKEY_ALT_R,
        "RCTRL"  :  MODKEY_CTRL_R,
        "RSHIFT" :  MODKEY_SHIFT_R,
        "RWIN"   :  MODKEY_WIN_R,
        "RCMD"   :  MODKEY_CMD_R,
        "RUSER0" :  MODKEY_USER0_R,
        "RUSER1" :  MODKEY_USER1_R,
    }

    def __init__( self, vk: int, mod: int = 0, down: bool = True, oneshot: bool = False ):

        """
        Initializes a key condition object.

        Args:
            vk: Key code.
            mod: Modifier key bits.
            down: Key down or up.
            oneshot: One-shot key.
        """

        self.vk = vk
        self.mod = mod
        self.down = down
        self.oneshot = oneshot

    def __hash__(self):
        return self.vk

    def __eq__(self, other):
        if self.vk!=other.vk: return False
        if not KeyCondition.mod_eq( self.mod, other.mod ): return False
        if self.down!=other.down: return False
        if self.oneshot!=other.oneshot: return False
        return True

    def __str__(self):

        s = ""

        if self.oneshot:
            s += "O-"
        elif self.down:
            s += "D-"
        else:
            s += "U-"

        if self.mod & MODKEY_ALT: s += "Alt-"
        elif self.mod & MODKEY_ALT_L: s += "LAlt-"
        elif self.mod & MODKEY_ALT_R: s += "RAlt-"

        if self.mod & MODKEY_CTRL: s += "Ctrl-"
        elif self.mod & MODKEY_CTRL_L: s += "LCtrl-"
        elif self.mod & MODKEY_CTRL_R: s += "RCtrl-"

        if self.mod & MODKEY_SHIFT: s += "Shift-"
        elif self.mod & MODKEY_SHIFT_L: s += "LShift-"
        elif self.mod & MODKEY_SHIFT_R: s += "RShift-"

        if self.mod & MODKEY_WIN: s += "Win-"
        elif self.mod & MODKEY_WIN_L: s += "LWin-"
        elif self.mod & MODKEY_WIN_R: s += "RWin-"

        if self.mod & MODKEY_CMD: s += "Cmd-"
        elif self.mod & MODKEY_CMD_L: s += "LCmd-"
        elif self.mod & MODKEY_CMD_R: s += "RCmd-"

        if self.mod & MODKEY_FN: s += "Fn-"
        elif self.mod & MODKEY_FN_L: s += "LFn-"
        elif self.mod & MODKEY_FN_R: s += "RFn-"

        if self.mod & MODKEY_USER0: s += "User0-"
        elif self.mod & MODKEY_USER0_L: s += "LUser0-"
        elif self.mod & MODKEY_USER0_R: s += "RUser0-"

        if self.mod & MODKEY_USER1: s += "User1-"
        elif self.mod & MODKEY_USER1_L: s += "LUser1-"
        elif self.mod & MODKEY_USER1_R: s += "RUser1-"

        s += KeyCondition.vk_to_str(self.vk)

        return s

    @staticmethod
    def from_str(s: str):

        """
        Create a key condition from a string expression

        Args:
            vk: Key code.
            mod: Modifier key bits.
            down: Key down or up.
            oneshot: One-shot key.

        Returns:
            KeyCondition object created
        """

        s = s.upper()

        vk = None
        mod=0
        down=True
        oneshot=False

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.str_to_mod(token)
            except ValueError:
                if token=="O":
                    oneshot = True
                elif token=="D":
                    down = True
                elif token=="U":
                    down = False
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.str_to_vk(token)

        return KeyCondition( vk, mod, down=down, oneshot=oneshot )

    @staticmethod
    def init_vk_str_tables() -> None:

        """
        Detect keyboard type and initialize internal key code translation tables.
        """

        # FIXME: detect keyboard type
        keyboard_type = 0

        KeyCondition.str_vk_table = KeyCondition.str_vk_table_common
        KeyCondition.vk_str_table = KeyCondition.vk_str_table_common

        if keyboard_type==7:
            KeyCondition.str_vk_table.update(KeyCondition.str_vk_table_jpn)
            KeyCondition.vk_str_table.update(KeyCondition.vk_str_table_jpn)
        else:
            KeyCondition.str_vk_table.update(KeyCondition.str_vk_table_std)
            KeyCondition.vk_str_table.update(KeyCondition.vk_str_table_std)

    @staticmethod
    def str_to_vk(name: str) -> int:

        """
        Convert a string expression of a key to key code

        Args:
            name: Name of the key.

        Returns:
            Key code of the key.
        """

        try:
            vk = KeyCondition.str_vk_table[name.upper()]
        except KeyError:
            try:
                vk = int(name.strip("()"))
            except:
                raise ValueError
        return vk

    @staticmethod
    def vk_to_str(vk: int) -> str:

        """
        Convert a key code to a string expression of the key

        Args:
            vk: Key code

        Returns:
            String expression of the key
        """

        try:
            name = KeyCondition.vk_str_table[vk]
        except KeyError:
            name = "(%d)" % vk
        return name

    @staticmethod
    def str_to_mod( name, force_LR=False ):

        """
        Convert a string expression of a modifier key to modifier bits

        Args:
            name: Name of the modifier key.
            force_LR: Whether distinguish left/right variations of the modifier keys

        Returns:
            Modifier bits.
        """
        
        try:
            mod = KeyCondition.str_mod_table[ name.upper() ]
        except KeyError:
            raise ValueError
        if force_LR and (mod & 0xff):
            mod <<= 8
        return mod

    @staticmethod
    def mod_eq( mod1, mod2 ):

        _mod1 = mod1 & 0xff
        _mod2 = mod2 & 0xff
        _mod1_L = (mod1 & 0xff00) >> 8
        _mod2_L = (mod2 & 0xff00) >> 8
        _mod1_R = (mod1 & 0xff0000) >> 16
        _mod2_R = (mod2 & 0xff0000) >> 16

        if _mod1 & ~( _mod2 | _mod2_L | _mod2_R ):
            return False
        if _mod1_L & ~( _mod2 | _mod2_L ):
            return False
        if _mod1_R & ~( _mod2 | _mod2_R ):
            return False
        if _mod2 & ~( _mod1 | _mod1_L | _mod1_R ):
            return False
        if _mod2_L & ~( _mod1 | _mod1_L ):
            return False
        if _mod2_R & ~( _mod1 | _mod1_R ):
            return False
        return True


class KeyTable:

    """
    A key table class

    KeyTable object can be used like a dictionary, to assign input key conditions to output key actions.
    """

    def __init__(self, name=None):
        self.name = name
        self.table = {}

    def __setitem__( self, key, value ):
        try:
            key = KeyCondition.from_str(key)
        except ValueError:
            logger.error(f"Invalid key expression: {key}")
            return

        self.table[key] = value

    def __getitem__( self, key ):
        try:
            key = KeyCondition.from_str(key)
        except ValueError:
            logger.error(f"Invalid key expression: {key}")
            return

        return self.table[key]

    def __delitem__( self, key ):
        try:
            key = KeyCondition.from_str(key)
        except ValueError:
            logger.error(f"Invalid key expression: {key}")
            return

        del self.table[key]

