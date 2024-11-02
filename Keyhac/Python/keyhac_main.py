import sys
import os
import json
import time
import fnmatch
import traceback

import keyhac_core
import keyhac_config
import keyhac_console
from keyhac_const import *

# for Xcode console
sys.stdout.reconfigure(encoding='utf-8')

keyhac_console.StandardIo.installRedirection()

def checkModifier( mod1, mod2 ):

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


class KeyCondition:

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

        #VK_NUMLOCK  : "NumLock", # FIXME : Mac対応
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
        #VK_APPS     : "Apps", # FIXME : Mac対応

        #VK_INSERT   : "Insert", # FIXME : Mac対応
        VK_DELETE   : "Delete",
        VK_HOME     : "Home",
        VK_END      : "End",
        VK_NEXT     : "PageDown",
        VK_PRIOR    : "PageUp",

        #VK_MENU     : "Alt", # FIXME : Mac対応
        VK_LMENU    : "LAlt",
        VK_RMENU    : "RAlt",
        #VK_CONTROL  : "Ctrl", # FIXME : Mac対応
        VK_LCONTROL : "LCtrl",
        VK_RCONTROL : "RCtrl",
        #VK_SHIFT    : "Shift", # FIXME : Mac対応
        VK_LSHIFT   : "LShift",
        VK_RSHIFT   : "RShift",
        #VK_LWIN     : "LWin", # FIXME : Mac対応
        #VK_RWIN     : "RWin", # FIXME : Mac対応
        VK_LCOMMAND : "LCmd",
        VK_RCOMMAND : "RCmd",
        VK_FUNCTION : "Fn",

        #VK_SNAPSHOT : "PrintScreen", # FIXME : Mac対応
        #VK_SCROLL   : "ScrollLock", # FIXME : Mac対応
        #VK_PAUSE    : "Pause", # FIXME : Mac対応
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
        #VK_OEM_1        : "Colon", # FIXME : Mac対応
        VK_SLASH        : "Slash",
        #VK_OEM_3        : "Atmark", # FIXME : Mac対応
        VK_OPENBRACKET  : "OpenBracket",
        #VK_OEM_5        : "Yen", # FIXME : Mac対応
        VK_CLOSEBRACKET : "CloseBracket",
        #VK_OEM_7        : "Caret", # FIXME : Mac対応
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

        #"NUMLOCK"  : VK_NUMLOCK, # FIXME : Mac対応
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
        #"APPS"     : VK_APPS, # FIXME : Mac対応

        #"INSERT"   : VK_INSERT, # FIXME : Mac対応
        "DELETE"   : VK_DELETE,
        "HOME"     : VK_HOME,
        "END"      : VK_END,
        "PAGEDOWN" : VK_NEXT,
        "PAGEUP"   : VK_PRIOR,

        "ALT"  : VK_LMENU,
        "LALT" : VK_LMENU,
        "RALT" : VK_RMENU,
        "CTRL"  : VK_LCONTROL,
        "LCTRL" : VK_LCONTROL,
        "RCTRL" : VK_RCONTROL,
        "SHIFT"  : VK_LSHIFT,
        "LSHIFT" : VK_LSHIFT,
        "RSHIFT" : VK_RSHIFT,
        #"LWIN" : VK_LWIN, # FIXME : Mac対応
        #"RWIN" : VK_RWIN, # FIXME : Mac対応
        "CMD"  : VK_LCOMMAND,
        "LCMD" : VK_LCOMMAND,
        "RCMD" : VK_RCOMMAND,
        "FN" : VK_FUNCTION,

        #"PRINTSCREEN" : VK_SNAPSHOT, # FIXME : Mac対応
        #"SCROLLLOCK"  : VK_SCROLL, # FIXME : Mac対応
        #"PAUSE"       : VK_PAUSE, # FIXME : Mac対応
    }

    str_vk_table_std = {

        "SEMICOLON"     : VK_SEMICOLON,
        "COLON"         : VK_SEMICOLON,
        "SLASH"         : VK_SLASH,
        "BACKQUOTE"     : VK_GRAVE,
        #"TILDE"         : VK_OEM_3, # FIXME : Mac対応
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
        #"COLON"         : VK_OEM_1, # FIXME : Mac対応
        "SLASH"         : VK_SLASH,
        "BACKQUOTE"     : VK_GRAVE,
        #"TILDE"         : VK_OEM_7, # FIXME : Mac対応
        "OPENBRACKET"   : VK_OPENBRACKET,
        "BACKSLASH"     : VK_BACKSLASH,
        "YEN"           : VK_YEN,
        "CLOSEBRACKET"  : VK_CLOSEBRACKET,
        "QUOTE"         : VK_7,
        "DOUBLEQUOTE"   : VK_2,
        "UNDERSCORE"    : VK_UNDERSCORE,
        #"ASTERISK"      : VK_OEM_1, # FIXME : Mac対応
        #"ATMARK"        : VK_OEM_3, # FIXME : Mac対応
        #"CARET"         : VK_OEM_7, # FIXME : Mac対応
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

        #"A" :  MODKEY_ALT,
        #"C" :  MODKEY_CTRL,
        #"S" :  MODKEY_SHIFT,
        #"W" :  MODKEY_WIN,
        #"U0" : MODKEY_USER0,
        #"U1" : MODKEY_USER1,

        #"LA" :  MODKEY_ALT_L,
        #"LC" :  MODKEY_CTRL_L,
        #"LS" :  MODKEY_SHIFT_L,
        #"LW" :  MODKEY_WIN_L,
        #"LU0" : MODKEY_USER0_L,
        #"LU1" : MODKEY_USER1_L,

        #"RA" :  MODKEY_ALT_R,
        #"RC" :  MODKEY_CTRL_R,
        #"RS" :  MODKEY_SHIFT_R,
        #"RW" :  MODKEY_WIN_R,
        #"RU0" : MODKEY_USER0_R,
        #"RU1" : MODKEY_USER1_R,
    }

    def __init__( self, vk, mod=0, up=False, oneshot=False ):
        if type(vk)==str and len(vk)==1 : vk=ord(vk)
        self.vk = vk
        self.mod = mod
        self.up = up
        self.oneshot = oneshot

    def __hash__(self):
        return self.vk

    def __eq__(self,other):
        if self.vk!=other.vk : return False
        if not checkModifier( self.mod, other.mod ) : return False
        if self.up!=other.up : return False
        if self.oneshot!=other.oneshot : return False
        return True

    def __str__(self):

        s = ""

        if self.oneshot:
            s += "O-"
        elif self.up:
            s += "U-"
        else:
            s += "D-"

        if self.mod & MODKEY_ALT : s += "Alt-"
        elif self.mod & MODKEY_ALT_L : s += "LAlt-"
        elif self.mod & MODKEY_ALT_R : s += "RAlt-"

        if self.mod & MODKEY_CTRL : s += "Ctrl-"
        elif self.mod & MODKEY_CTRL_L : s += "LCtrl-"
        elif self.mod & MODKEY_CTRL_R : s += "RCtrl-"

        if self.mod & MODKEY_SHIFT : s += "Shift-"
        elif self.mod & MODKEY_SHIFT_L : s += "LShift-"
        elif self.mod & MODKEY_SHIFT_R : s += "RShift-"

        if self.mod & MODKEY_WIN : s += "Win-"
        elif self.mod & MODKEY_WIN_L : s += "LWin-"
        elif self.mod & MODKEY_WIN_R : s += "RWin-"

        if self.mod & MODKEY_CMD : s += "Cmd-"
        elif self.mod & MODKEY_CMD_L : s += "LCmd-"
        elif self.mod & MODKEY_CMD_R : s += "RCmd-"

        if self.mod & MODKEY_FN : s += "Fn-"
        elif self.mod & MODKEY_FN_L : s += "LFn-"
        elif self.mod & MODKEY_FN_R : s += "RFn-"

        if self.mod & MODKEY_USER0 : s += "User0-"
        elif self.mod & MODKEY_USER0_L : s += "LUser0-"
        elif self.mod & MODKEY_USER0_R : s += "RUser0-"

        if self.mod & MODKEY_USER1 : s += "User1-"
        elif self.mod & MODKEY_USER1_L : s += "LUser1-"
        elif self.mod & MODKEY_USER1_R : s += "RUser1-"

        s += KeyCondition.vkToStr(self.vk)

        return s

    @staticmethod
    def fromString(s):

        s = s.upper()

        vk = None
        mod=0
        up=False
        oneshot=False

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.strToMod(token)
            except ValueError:
                if token=="O":
                    oneshot = True
                elif token=="D":
                    up = False
                elif token=="U":
                    up = True
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.strToVk(token)

        return KeyCondition( vk, mod, up=up, oneshot=oneshot )

    @staticmethod
    def initTables():

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
    def strToVk(name):
        try:
            vk = KeyCondition.str_vk_table[name.upper()]
        except KeyError:
            try:
                vk = int(name.strip("()"))
            except:
                raise ValueError
        return vk

    @staticmethod
    def vkToStr(vk):
        try:
            name = KeyCondition.vk_str_table[vk]
        except KeyError:
            name = "(%d)" % vk
        return name

    @staticmethod
    def strToMod( name, force_LR=False ):
        try:
            mod = KeyCondition.str_mod_table[ name.upper() ]
        except KeyError:
            raise ValueError
        if force_LR and (mod & 0xff):
            mod <<= 8
        return mod


class WindowKeymap:

    def __init__( self, focus_path_pattern=None, check_func=None, help_string=None ):
        self.focus_path_pattern = focus_path_pattern
        self.check_func = check_func
        self.help_string = help_string
        self.keymap = {}

    def check( self, focus_path ):

        if self.focus_path_pattern and ( not focus_path or not fnmatch.fnmatch( focus_path, self.focus_path_pattern ) ) : return False
        
        try:
            if self.check_func and ( not self.focus_elm or not self.check_func(self.focus_elm) ) : return False
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False
        return True

    def helpString(self):
        return self.help_string

    def __setitem__( self, name, value ):

        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( "ERROR : Invalid key expression :", name )
            return

        self.keymap[key_cond] = value

    def __getitem__( self, name ):

        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( "ERROR : Invalid key expression :", name )
            return

        return self.keymap[key_cond]

    def __delitem__( self, name ):
        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( "ERROR : Invalid key expression :", name )
            return

        del self.keymap[key_cond]

class Keymap:
    
    _instance = None
            
    @staticmethod
    def getInstance():
        if not Keymap._instance:
            Keymap._instance = Keymap()
        return Keymap._instance

    def __init__(self):

        self.debug = False                      # デバッグモード
        self.send_input_on_tru = False          # キーの置き換えが不要だった場合もsentInputするか

        self.window_keymap_list = []            # WindowKeymapオブジェクトのリスト
        self.multi_stroke_keymap = None         # マルチストローク用のWindowKeymapオブジェクト
        self.current_map = {}                   # 現在フォーカスされているウインドウで有効なキーマップ
        self.vk_mod_map = {}                    # モディファイアキーの仮想キーコードとビットのテーブル
        self.vk_vk_map = {}                     # キーの置き換えテーブル
        self.focus_path = None                  # 現在フォーカスされているUI要素を表す文字列
        self.focus_elm = None                   # 現在フォーカスされているUI要素
        self.modifier = 0                       # 押されているモディファイアキーのビットの組み合わせ
        self.last_keydown = None                # 最後にKeyDownされた仮想キーコード
        self.oneshot_canceled = False           # ワンショットモディファイアをキャンセルするか
        self.input_seq = []                     # 仮想のキー入力シーケンス ( beginInput ～ endInput で使用 )
        self.virtual_modifier = 0               # 仮想のモディファイアキー状態 ( beginInput ～ endInput で使用 )
        self.record_status = None               # キーボードマクロの状態
        self.record_seq = None                  # キーボードマクロのシーケンス
        self.hook_call_list = []                # フック内呼び出し関数のリスト

        self.sanity_check_state = None
        self.sanity_check_count = 0
        self.last_input_send_time = 0
        
        print("Welcome to Keyhac")

    def configure(self):

        self._releaseModifierAll()

        KeyCondition.initTables()

        self.window_keymap_list = []
        self.multi_stroke_keymap = None
        self.current_map = {}
        self.vk_mod_map = {}
        self.vk_vk_map = {}
        self.focus_path = None
        self.focus_elm = None
        self.modifier = 0

        self.vk_mod_map[VK_LSHIFT   ] = MODKEY_SHIFT_L
        self.vk_mod_map[VK_RSHIFT   ] = MODKEY_SHIFT_R
        self.vk_mod_map[VK_LCONTROL ] = MODKEY_CTRL_L
        self.vk_mod_map[VK_RCONTROL ] = MODKEY_CTRL_R
        self.vk_mod_map[VK_LMENU    ] = MODKEY_ALT_L
        self.vk_mod_map[VK_RMENU    ] = MODKEY_ALT_R
        self.vk_mod_map[VK_LCOMMAND ] = MODKEY_CMD_L
        self.vk_mod_map[VK_RCOMMAND ] = MODKEY_CMD_R
        self.vk_mod_map[VK_FUNCTION ] = MODKEY_FN_L

        # Load configuration file
        self.config = keyhac_config.Config(
            os.path.expanduser("~/.keyhac/config.py"),
            os.path.join(os.path.dirname(__file__), "_config.py")
        )
        self.config.call("configure", self)
        
        print("Keymap configuration succeeded.")

    def enableKeyboardHook(self):
    
        def _onKey(s):
            d = json.loads(s)
            if d["type"]=="keyDown":
                return self._onKeyDown(d["keyCode"])
            elif d["type"]=="keyUp":
                return self._onKeyUp(d["keyCode"])

        keyhac_core.Hook.setCallback("Keyboard", _onKey)

    def replaceKey( self, src, dst ):
        try:
            if type(src)==str:
                src = KeyCondition.strToVk(src)
        except:
            print( f"ERROR : Invalid expression for argument 'src': {src}" )
            return

        try:
            if type(dst)==str:
                dst = KeyCondition.strToVk(dst)
        except:
            print( f"ERROR : Invalid expression for argument 'dst': {dst}" )
            return

        self.vk_vk_map[src] = dst

    def defineModifier( self, vk, mod ):

        try:
            vk_org = vk
            if type(vk)==str:
                vk = KeyCondition.strToVk(vk)
        except:
            print( f"ERROR : Invalid expression for argument 'vk': {vk}" )
            return

        try:
            if type(mod)==str:
                mod = KeyCondition.strToMod( mod, force_LR=True )
            else:
                raise TypeError
        except:
            print( f"ERROR : Invalid expression for argument 'mod': {mod}" )
            return

        try:
            if vk in self.vk_mod_map:
                raise ValueError
        except:
            print( f"ERROR : Already defined as a modifier: {vk_org}" )
            return

        self.vk_mod_map[vk] = mod

    def sendInput(self, seq):
        for event in seq:
            keyhac_core.Hook.sendKeyboardEvent(event[0], event[1])
        self.last_input_send_time = time.time()

    def _releaseModifierAll(self):
        input_seq = []
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL:
                continue
            input_seq.append( ("keyUp", vk_mod[0]) )
        self.sendInput(input_seq)

    def defineWindowKeymap( self, focus_path_pattern=None, check_func=None ):
        window_keymap = WindowKeymap( focus_path_pattern, check_func )
        self.window_keymap_list.append(window_keymap)
        return window_keymap

    ## マルチストローク用のキーマップを定義する
    def defineMultiStrokeKeymap( self, help_string=None ):
        keymap = WindowKeymap( help_string=help_string )
        return keymap

    def beginInput(self):
        self.input_seq = []
        self.virtual_modifier = self.modifier

    def endInput(self):
        self.setInput_Modifier(self.modifier)
        self.sendInput(self.input_seq)
        self.input_seq = []

    def setInput_Modifier( self, mod ):

        # Win と Alt の単体押しのキャンセルが必要かチェック
        # Win の単体押しは スタートメニューが開き、Alt の単体押しは メニューバーにフォーカスが移動してしまう。
        cancel_oneshot_win_alt = False
        if ( checkModifier( self.virtual_modifier, MODKEY_ALT ) or checkModifier( self.virtual_modifier, MODKEY_WIN ) ) and mod==0:
            cancel_oneshot_win_alt = True
        elif self.virtual_modifier==0 and ( checkModifier( mod, MODKEY_ALT ) or checkModifier( mod, MODKEY_WIN ) ):
            cancel_oneshot_win_alt = True

        # モディファイア押す
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if not ( vk_mod[1] & self.virtual_modifier ) and ( vk_mod[1] & mod ):
                self.input_seq.append( ("keyDown", vk_mod[0]) )
                self.virtual_modifier |= vk_mod[1]

        # Win と Alt の単体押しをキャンセル
        if cancel_oneshot_win_alt:
            self.input_seq.append( ("keyDown", VK_LCONTROL) )
            self.input_seq.append( ("keyUp", VK_LCONTROL) )

        # モディファイア離す
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if ( vk_mod[1] & self.virtual_modifier ) and not ( vk_mod[1] & mod ):
                self.input_seq.append( ("keyUp", vk_mod[0]) )
                self.virtual_modifier &= ~vk_mod[1]

    def setInput_FromString( self, s ):

        s = s.upper()

        vk = None
        mod = 0
        up = None

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.strToMod( token, force_LR=True )
            except ValueError:
                if token=="D":
                    up = False
                elif token=="U":
                    up = True
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.strToVk(token)

        self.setInput_Modifier(mod)

        if up==True:
            self.input_seq.append( ("keyUp", vk) )
        elif up==False:
            self.input_seq.append( ("keyDown", vk) )
        else:
            self.input_seq.append( ("keyDown", vk) )
            self.input_seq.append( ("keyUp", vk) )

    def _checkFocusChange(self):
    
        focus_elms = []

        elm = keyhac_core.UIElement.getSystemWideElement()
        elm = elm.getAttributeValue("AXFocusedUIElement")

        self.focus_elm = elm

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

        new_focus_path = "/".join(focus_path_components)
        if self.focus_path != new_focus_path:
            print("Focus path:", new_focus_path)
            self.focus_path = new_focus_path
            self._updateKeymap()

    # モディファイアのおかしな状態を修正する
    # たとえば Win-L を押して ロック画面に行ったときに Winキーが押されっぱなしになってしまうような現象を回避
    def _fixWierdModifierState(self):
        
        # 最後の Input.send() から 一定時間以上経ってなかったら、この処理をしない
        if time.time() - self.last_input_send_time < 1.0:
            return

        for vk_mod in self.vk_mod_map.items():

            if vk_mod[1] & MODKEY_USER_ALL:
                continue

            if self.modifier & vk_mod[1]:

                # FIXME: 実装
                #if not ckit.Input.isKeyPressed(vk_mod[0]):
                if False:
                    
                    self.modifier &= ~vk_mod[1]
                    
                    #keyhac_core.Hook.fixWierdModifierState()
    
                    #if self.debug:
                    if 0:
                        print( "" )
                        print( "FIX :", KeyCondition.vkToStr(vk_mod[0]) )
                        print( "" )


    def _onKeyDown( self, vk ):

        #if ckit.platform()=="win":
        if False:
            # FIXME : vk=0 は Macでは A キーなので特殊な用途には使えない
            if vk==0:
                for func in self.hook_call_list:
                    func()
                self.hook_call_list = []
                return True

        self._checkFocusChange()

        self._fixWierdModifierState()

        self._recordKey( vk, False )

        try:
            vk = self.vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        if self.last_keydown != vk:
            self.last_keydown = vk
            self.oneshot_canceled = False

        try:
            old_modifier = self.modifier
            if vk in self.vk_mod_map:
                self.modifier |= self.vk_mod_map[vk]
                if self.vk_mod_map[vk] & MODKEY_USER_ALL:
                    key = KeyCondition( vk, old_modifier, up=False )
                    self._keyAction(key)
                    return True

            key = KeyCondition( vk, old_modifier, up=False )

            if self._keyAction(key):
                return True
            elif replaced:
                key_seq = [ ("keyDown", vk) ]
                if self.debug : print( "REP :", key_seq )
                self.sendInput(key_seq)
                return True
            else:
                if self.send_input_on_tru:
                    # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                    # TRU でも Input.send すると問題が起きない
                    key_seq = [ ("keyDown", vk) ]
                    if self.debug : print( "TRU :", key_seq )
                    self.sendInput(key_seq)
                    return True
                else:
                    if self.debug : print( "TRU :", key )
                    return False

        except Exception as e:
            print( "ERROR : Unexpected error happened :" )
            print( e )
            traceback.print_exc()

    def _onKeyUp( self, vk ):

        self._checkFocusChange()

        self._fixWierdModifierState()

        self._recordKey( vk, True )

        try:
            vk = self.vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        oneshot = ( vk == self.last_keydown and not self.oneshot_canceled )
        self.last_keydown = None
        self.oneshot_canceled = False

        try: # for error
            try: # for oneshot
                if vk in self.vk_mod_map:

                    self.modifier &= ~self.vk_mod_map[vk]

                    if self.vk_mod_map[vk] & MODKEY_USER_ALL:
                        key = KeyCondition( vk, self.modifier, up=True )
                        self._keyAction(key)
                        return True

                key = KeyCondition( vk, self.modifier, up=True )

                if oneshot:
                    oneshot_key = KeyCondition( vk, self.modifier, up=False, oneshot=True )

                if self._keyAction(key):
                    return True
                elif replaced or ( oneshot and self._hasKeyAction(oneshot_key) ):
                    key_seq = [ ("keyUp", vk) ]
                    if self.debug : print( "REP :", key_seq )
                    self.sendInput(key_seq)
                    return True
                else:
                    if self.send_input_on_tru:
                        # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                        # TRU でも Input.send すると問題が起きない
                        key_seq = [ ("keyUp", vk) ]
                        if self.debug : print( "TRU :", key_seq )
                        self.sendInput(key_seq)
                        return True
                    else:
                        if self.debug : print( "TRU :", key )
                        return False

            finally:
                # ワンショットモディファイア は Up を処理した後に実行する
                # モディファイアキーの Up -> Down を偽装しなくてよいように。
                # Up を処理する前に Up -> Down を偽装すると、他のウインドウで
                # モディファイアが押しっぱなしになるなどの問題があるようだ。
                if oneshot:
                    key = KeyCondition( vk, self.modifier, up=False, oneshot=True )
                    self._keyAction(key)

        except Exception as e:
            print( "ERROR : Unexpected error happened :" )
            print( e )
            traceback.print_exc()

    def _recordKey( self, vk, up ):
        if self.record_status=="recording":
            if len(self.record_seq)>=1000:
                print( "ERROR : Keyboard macro is too long." )
                return
            self.record_seq.append( ( vk, up ) )

    def _hasKeyAction( self, key ):
        return key in self.current_map

    def _keyAction( self, key ):

        if self.debug : print( "IN  :", key )

        try:
            try:
                handler = self.current_map[key]
            except KeyError:
                if self.multi_stroke_keymap and not key.up and not key.oneshot and not key.vk in self.vk_mod_map:
                    winsound.MessageBeep()
                    return True
                else:
                    return False
        finally:
            if not key.up and not key.oneshot and not key.vk in self.vk_mod_map:
                self._leaveMultiStroke()

        if callable(handler):

            self._cancelOneshotWinAlt()

            handler()

        elif isinstance(handler,WindowKeymap):

            self._cancelOneshotWinAlt()

            self._enterMultiStroke(handler)

        else:
            if type(handler)!=list and type(handler)!=tuple:
                handler = [handler]

            self.beginInput()

            for item in handler:

                if type(item)==str:
                    self.setInput_FromString(item)
                else:
                    raise TypeError;

            self.endInput()

        return True

    def _enterMultiStroke( self, keymap ):

        self.multi_stroke_keymap = keymap
        self._updateKeymap()

        # FIXME : toast を使う
        #help_string = self.multi_stroke_keymap.helpString()
        #if help_string:
        #    self.popBalloon( "MultiStroke", help_string )

    def _leaveMultiStroke(self):

        if self.multi_stroke_keymap:
            self.multi_stroke_keymap = None
            self._updateKeymap()

            #self.closeBalloon( "MultiStroke" )

    def _updateKeymap(self):

        self.current_map = {}

        if self.multi_stroke_keymap:
            self.current_map.update(self.multi_stroke_keymap.keymap)
        else:
            for window_keymap in self.window_keymap_list:
                if window_keymap.check(self.focus_path):
                    self.current_map.update(window_keymap.keymap)


    # FIXME: MacOS で不要かも
    def _cancelOneshotWinAlt(self):
        if checkModifier( self.modifier, MODKEY_ALT ) or checkModifier( self.modifier, MODKEY_WIN ):
            self.beginInput()
            self.setInput_Modifier( self.modifier | MODKEY_CTRL_L )
            self.endInput()

    @property
    def focus(self):
        return self.focus_elm

def configure():
    Keymap.getInstance().enableKeyboardHook()
    Keymap.getInstance().configure()
