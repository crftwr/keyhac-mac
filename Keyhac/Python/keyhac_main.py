import sys
import os
import json
import fnmatch
import traceback

import keyhac_core
import keyhac_config
import keyhac_console
from keyhac_key import KeyCondition, KeyTable
from keyhac_focus import FocusCondition
from keyhac_const import *

# for Xcode console
sys.stdout.reconfigure(encoding='utf-8')

keyhac_console.StandardIo.installRedirection()

class Keymap:
    
    _instance = None
            
    @staticmethod
    def getInstance():
        if not Keymap._instance:
            Keymap._instance = Keymap()
        return Keymap._instance

    def __init__(self):

        self._debug = False                     # デバッグモード
        self._send_input_on_tru = False         # キーの置き換えが不要だった場合もsentInputするか

        self._focus_cond_keymap_list = []       # (FocusCondition, KeyTable) のリスト
        self._multi_stroke_keymap = None        # マルチストローク用の KeyTable
        self._current_map = {}                  # 現在フォーカスされているウインドウで有効なキーマップ
        self._vk_mod_map = {}                   # モディファイアキーの仮想キーコードとビットのテーブル
        self._vk_vk_map = {}                    # キーの置き換えテーブル
        self._focus_path = None                 # 現在フォーカスされているUI要素を表す文字列
        self._focus_elm = None                  # 現在フォーカスされているUI要素
        self._modifier = 0                      # 押されているモディファイアキーのビットの組み合わせ
        self._last_keydown = None               # 最後にKeyDownされた仮想キーコード
        self._oneshot_canceled = False          # ワンショットモディファイアをキャンセルするか
        self._input_seq = []                    # 仮想のキー入力シーケンス ( beginInput ～ endInput で使用 )
        self._virtual_modifier = 0              # 仮想のモディファイアキー状態 ( beginInput ～ endInput で使用 )
        self._record_status = None              # キーボードマクロの状態
        self._record_seq = None                 # キーボードマクロのシーケンス

        keyhac_core.Hook.setCallback("Keyboard", self._onKey)
        
        print("Welcome to Keyhac")

    def configure(self):

        self._releaseModifierAll()

        KeyCondition.initTables()

        self._focus_cond_keymap_list = []
        self._multi_stroke_keymap = None
        self._current_map = {}
        self._vk_mod_map = {}
        self._vk_vk_map = {}
        self._focus_path = None
        self._focus_elm = None
        self._modifier = 0

        self._vk_mod_map[VK_LSHIFT   ] = MODKEY_SHIFT_L
        self._vk_mod_map[VK_RSHIFT   ] = MODKEY_SHIFT_R
        self._vk_mod_map[VK_LCONTROL ] = MODKEY_CTRL_L
        self._vk_mod_map[VK_RCONTROL ] = MODKEY_CTRL_R
        self._vk_mod_map[VK_LMENU    ] = MODKEY_ALT_L
        self._vk_mod_map[VK_RMENU    ] = MODKEY_ALT_R
        self._vk_mod_map[VK_LCOMMAND ] = MODKEY_CMD_L
        self._vk_mod_map[VK_RCOMMAND ] = MODKEY_CMD_R
        self._vk_mod_map[VK_FUNCTION ] = MODKEY_FN_L

        # Load configuration file
        self.config = keyhac_config.Config(
            os.path.expanduser("~/.keyhac/config.py"),
            os.path.join(os.path.dirname(__file__), "_config.py")
        )
        self.config.call("configure", self)
        
        print("Keymap configuration succeeded.")

    def replace_key( self, src, dst ):
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

        self._vk_vk_map[src] = dst

    def define_modifier( self, vk, mod ):

        vk_org = vk
        try:
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

        self._vk_mod_map[vk] = mod

    # FIXME: naming convention
    def sendInput(self, seq):
        for event in seq:
            keyhac_core.Hook.sendKeyboardEvent(event[0], event[1])

    def _releaseModifierAll(self):
        input_seq = []
        for vk_mod in self._vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL:
                continue
            input_seq.append( ("keyUp", vk_mod[0]) )
        self.sendInput(input_seq)

    def define_keytable( self, name=None, focus_path_pattern=None, custom_condition_func=None ):
        keytable = KeyTable(name=name)
        if focus_path_pattern or custom_condition_func:
            focus_condition = FocusCondition( focus_path_pattern, custom_condition_func )
            self._focus_cond_keymap_list.append( (focus_condition, keytable) )
        return keytable

    # FIXME: naming convention
    def beginInput(self):
        self._input_seq = []
        self._virtual_modifier = self._modifier

    # FIXME: naming convention
    def endInput(self):
        self.setInput_Modifier(self._modifier)
        self.sendInput(self._input_seq)
        self._input_seq = []

    # FIXME: naming convention
    def setInput_Modifier( self, mod ):

        # モディファイア押す
        for vk_mod in self._vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if not ( vk_mod[1] & self._virtual_modifier ) and ( vk_mod[1] & mod ):
                self._input_seq.append( ("keyDown", vk_mod[0]) )
                self._virtual_modifier |= vk_mod[1]

        # モディファイア離す
        for vk_mod in self._vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if ( vk_mod[1] & self._virtual_modifier ) and not ( vk_mod[1] & mod ):
                self._input_seq.append( ("keyUp", vk_mod[0]) )
                self._virtual_modifier &= ~vk_mod[1]

    # FIXME: naming convention
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
            self._input_seq.append( ("keyUp", vk) )
        elif up==False:
            self._input_seq.append( ("keyDown", vk) )
        else:
            self._input_seq.append( ("keyDown", vk) )
            self._input_seq.append( ("keyUp", vk) )

    def _checkFocusChange(self):
    
        elm = keyhac_core.UIElement.getSystemWideElement()
        elm = elm.getAttributeValue("AXFocusedUIElement")

        self._focus_elm = elm
        new_focus_path = FocusCondition.get_focus_path(elm)

        if self._focus_path != new_focus_path:
            print("Focus path:", new_focus_path)
            self._focus_path = new_focus_path
            self._updateKeymap()

    def _onKey(self, s):
        d = json.loads(s)
        if d["type"]=="keyDown":
            return self._onKeyDown(d["keyCode"])
        elif d["type"]=="keyUp":
            return self._onKeyUp(d["keyCode"])

    def _onKeyDown( self, vk ):

        self._checkFocusChange()

        self._recordKey( vk, False )

        try:
            vk = self._vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        if self._last_keydown != vk:
            self._last_keydown = vk
            self._oneshot_canceled = False

        try:
            old_modifier = self._modifier
            if vk in self._vk_mod_map:
                self._modifier |= self._vk_mod_map[vk]
                if self._vk_mod_map[vk] & MODKEY_USER_ALL:
                    key = KeyCondition( vk, old_modifier, up=False )
                    self._keyAction(key)
                    return True

            key = KeyCondition( vk, old_modifier, up=False )

            if self._keyAction(key):
                return True
            elif replaced:
                key_seq = [ ("keyDown", vk) ]
                if self._debug : print( "REP :", key_seq )
                self.sendInput(key_seq)
                return True
            else:
                if self._send_input_on_tru:
                    # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                    # TRU でも Input.send すると問題が起きない
                    key_seq = [ ("keyDown", vk) ]
                    if self._debug : print( "TRU :", key_seq )
                    self.sendInput(key_seq)
                    return True
                else:
                    if self._debug : print( "TRU :", key )
                    return False

        except Exception as e:
            print( "ERROR : Unexpected error happened :" )
            print( e )
            traceback.print_exc()

    def _onKeyUp( self, vk ):

        self._checkFocusChange()

        self._recordKey( vk, True )

        try:
            vk = self._vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        oneshot = ( vk == self._last_keydown and not self._oneshot_canceled )
        self._last_keydown = None
        self._oneshot_canceled = False

        try: # for error
            try: # for oneshot
                if vk in self._vk_mod_map:

                    self._modifier &= ~self._vk_mod_map[vk]

                    if self._vk_mod_map[vk] & MODKEY_USER_ALL:
                        key = KeyCondition( vk, self._modifier, up=True )
                        self._keyAction(key)
                        return True

                key = KeyCondition( vk, self._modifier, up=True )

                if oneshot:
                    oneshot_key = KeyCondition( vk, self._modifier, up=False, oneshot=True )

                if self._keyAction(key):
                    return True
                elif replaced or ( oneshot and self._hasKeyAction(oneshot_key) ):
                    key_seq = [ ("keyUp", vk) ]
                    if self._debug : print( "REP :", key_seq )
                    self.sendInput(key_seq)
                    return True
                else:
                    if self._send_input_on_tru:
                        # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                        # TRU でも Input.send すると問題が起きない
                        key_seq = [ ("keyUp", vk) ]
                        if self._debug : print( "TRU :", key_seq )
                        self.sendInput(key_seq)
                        return True
                    else:
                        if self._debug : print( "TRU :", key )
                        return False

            finally:
                # ワンショットモディファイア は Up を処理した後に実行する
                # モディファイアキーの Up -> Down を偽装しなくてよいように。
                # Up を処理する前に Up -> Down を偽装すると、他のウインドウで
                # モディファイアが押しっぱなしになるなどの問題があるようだ。
                if oneshot:
                    key = KeyCondition( vk, self._modifier, up=False, oneshot=True )
                    self._keyAction(key)

        except Exception as e:
            print( "ERROR : Unexpected error happened :" )
            print( e )
            traceback.print_exc()

    def _recordKey( self, vk, up ):
        if self._record_status=="recording":
            if len(self._record_seq)>=1000:
                print( "ERROR : Keyboard macro is too long." )
                return
            self._record_seq.append( ( vk, up ) )

    def _hasKeyAction( self, key ):
        return key in self._current_map

    def _keyAction( self, key ):

        if self._debug : print( "IN  :", key )

        try:
            try:
                handler = self._current_map[key]
            except KeyError:
                if self._multi_stroke_keymap and not key.up and not key.oneshot and not key.vk in self._vk_mod_map:
                    winsound.MessageBeep()
                    return True
                else:
                    return False
        finally:
            if not key.up and not key.oneshot and not key.vk in self._vk_mod_map:
                self._leaveMultiStroke()

        if callable(handler):
            handler()

        elif isinstance(handler, KeyTable):
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

        self._multi_stroke_keymap = keymap
        self._updateKeymap()

        # FIXME : toast を使う
        #help_string = self._multi_stroke_keymap.helpString()
        #if help_string:
        #    self.popBalloon( "MultiStroke", help_string )

    def _leaveMultiStroke(self):

        if self._multi_stroke_keymap:
            self._multi_stroke_keymap = None
            self._updateKeymap()

            #self.closeBalloon( "MultiStroke" )

    def _updateKeymap(self):

        self._current_map = {}

        if self._multi_stroke_keymap:
            self._current_map.update(self._multi_stroke_keymap.table)
        else:
            for focus_condition, keytable in self._focus_cond_keymap_list:
                if focus_condition.check(self._focus_path, self._focus_elm):
                    self._current_map.update(keytable.table)

    @property
    def focus(self):
        return self._focus_elm

def configure():
    Keymap.getInstance().configure()
