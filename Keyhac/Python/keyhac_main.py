import sys
import os
import json
import traceback

import keyhac_core
import keyhac_config
import keyhac_console
from keyhac_key import KeyCondition, KeyTable
from keyhac_focus import FocusCondition
from keyhac_input import InputContext
from keyhac_const import *

keyhac_console.initializeConsole()

logger = keyhac_console.getLogger("Keymap")

class Keymap:
    
    _instance = None
            
    @staticmethod
    def getInstance():
        if not Keymap._instance:
            Keymap._instance = Keymap()
        return Keymap._instance

    def __init__(self):

        # (Experimental) always send keys even for pass-through,
        # to ensure key events are not out of order
        self._passthru_by_send = False

        self._keytable_list = []            # List of (FocusCondition, KeyTable)
        self._multi_stroke_keytable = None  # KeyTable for multi-stroke mode
        self._unified_keytable = {}         # Key assignments aggregated from all active key tables
        self._vk_mod_map = {}               # Table of key code to modifier
        self._vk_vk_map = {}                # Table of key code to key code
        self._focus_path = None             # Focus path of the current focus
        self._focus_elm = None              # UIElement of the current focus
        self._modifier = 0                  # Flags of currently pressed modifier keys
        self._last_keydown = None           # Key code of the last key down, to detect one-shot event
        self._record_status = None          # Key recording status ("recording" or None)
        self._record_seq = None             # Recoreded key sequence

        keyhac_core.Hook.setCallback("Keyboard", self._on_key)
        
        print("\n" + CONSOLE_STYLE_TITLE + "Welcome to Keyhac" + CONSOLE_STYLE_DEFAULT + "\n")

    def configure(self):

        self._release_modifier_all()

        KeyCondition.init_vk_str_tables()

        self._keytable_list = []
        self._multi_stroke_keytable = None
        self._unified_keytable = {}
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
        
        logger.info("Loading configuration script.")

        # Create "~/.keyhac" and "extensions" directories
        os.makedirs(os.path.expanduser("~/.keyhac/extensions"), exist_ok=True)

        try:
            # Load configuration file
            self.config = keyhac_config.Config(
                os.path.expanduser("~/.keyhac/config.py"),
                os.path.join(os.path.dirname(__file__), "_config.py")
            )
            self.config.call("configure", self)
        except:
            print()
            logger.error(f"Loading configuration script failed:\n{traceback.format_exc()}")
            return

    def replace_key( self, src, dst ):
        try:
            if type(src)==str:
                src = KeyCondition.str_to_vk(src)
        except:
            logger.error(f"Invalid key expression for argument 'src': {src}")
            return

        try:
            if type(dst)==str:
                dst = KeyCondition.str_to_vk(dst)
        except:
            logger.error(f"Invalid key expression for argument 'dst': {dst}")
            return

        self._vk_vk_map[src] = dst

    def define_modifier( self, vk, mod ):

        vk_org = vk
        try:
            if type(vk)==str:
                vk = KeyCondition.str_to_vk(vk)
        except:
            logger.error(f"Invalid key expression for argument 'vk': {vk}")
            return

        try:
            if type(mod)==str:
                mod = KeyCondition.str_to_mod( mod, force_LR=True )
            else:
                raise TypeError
        except:
            logger.error(f"Invalid key expression for argument 'mod': {mod}")
            return

        self._vk_mod_map[vk] = mod

    def define_keytable( self, name=None, focus_path_pattern=None, custom_condition_func=None ):
        keytable = KeyTable(name=name)
        if focus_path_pattern or custom_condition_func:
            focus_condition = FocusCondition( focus_path_pattern, custom_condition_func )
            self._keytable_list.append( (focus_condition, keytable) )
        return keytable

    def _release_modifier_all(self):
        with self.get_input_context() as input_ctx:
            for vk_mod in self._vk_mod_map.items():
                if vk_mod[1] & MODKEY_USER_ALL:
                    continue
                input_ctx.send_key_by_vk(vk_mod[0], down=False)

    def get_input_context(self):
        return InputContext(self._modifier, self._vk_mod_map)

    def _get_focused_element(self):

        app = keyhac_core.UIElement.getFocusedApplication()
        if not app: return None

        focus = app.getAttributeValue("AXFocusedUIElement")
        if focus: return focus

        window = app.getAttributeValue("AXFocusedWindow")
        if window: return window
        
        return app

    def _check_focus_change(self):
        
        elm = self._get_focused_element()

        self._focus_elm = elm
        new_focus_path = FocusCondition.get_focus_path(elm)

        if self._focus_path != new_focus_path:
            logger.debug(f"Focus path: {new_focus_path}")
            keyhac_core.Console.setText("focusPath", new_focus_path)
            self._focus_path = new_focus_path
            self._update_unified_keytable()

    def _on_key(self, s):
        d = json.loads(s)
        if d["type"]=="keyDown":
            return self._on_key_down(d["keyCode"])
        elif d["type"]=="keyUp":
            return self._on_key_up(d["keyCode"])
        elif d["type"]=="hookRestored":
            return self._on_key_hook_restored()

    def _on_key_down( self, vk ):

        self._check_focus_change()

        self._record_key( vk, False )

        try:
            vk = self._vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        self._last_keydown = vk

        try:
            old_modifier = self._modifier
            if vk in self._vk_mod_map:
                self._modifier |= self._vk_mod_map[vk]
                if self._vk_mod_map[vk] & MODKEY_USER_ALL:
                    key = KeyCondition( vk, old_modifier, down=True )
                    self._setLastKeyText(key)
                    self._do_configured_key_action(key)
                    return True

            key = KeyCondition( vk, old_modifier, down=True )

            self._setLastKeyText(key)
            if self._do_configured_key_action(key):
                return True
            elif replaced:
                with self.get_input_context() as input_ctx:
                    input_ctx.send_key_by_vk( vk, down=True )
                    logger.debug(f"REPLACE  : {input_ctx}")
                return True
            else:
                if self._passthru_by_send:
                    with self.get_input_context() as input_ctx:
                        input_ctx.send_key_by_vk( vk, down=True )
                        logger.debug(f"PASSTHRU : {key}")
                    return True
                else:
                    logger.debug(f"PASSTHRU : {key}")
                    return False

        except Exception as e:
            print()
            logger.error(f"Unexpected error happened:\n{traceback.format_exc()}")

    def _on_key_up( self, vk ):

        self._check_focus_change()

        self._record_key( vk, True )

        try:
            vk = self._vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        oneshot = (vk == self._last_keydown)
        self._last_keydown = None

        try: # for error
            try: # for oneshot
                if vk in self._vk_mod_map:
                    self._modifier &= ~self._vk_mod_map[vk]
                    if self._vk_mod_map[vk] & MODKEY_USER_ALL:
                        key = KeyCondition( vk, self._modifier, down=False )
                        self._do_configured_key_action(key)
                        return True

                key = KeyCondition( vk, self._modifier, down=False )

                if oneshot:
                    oneshot_key = KeyCondition( vk, self._modifier, down=True, oneshot=True )

                if self._do_configured_key_action(key):
                    return True
                elif replaced or ( oneshot and self._is_key_configured(oneshot_key) ):
                    with self.get_input_context() as input_ctx:
                        input_ctx.send_key_by_vk( vk, down=False )
                        logger.debug(f"REPLACE  : {input_ctx}")
                    return True
                else:
                    if self._passthru_by_send:
                        with self.get_input_context() as input_ctx:
                            input_ctx.send_key_by_vk( vk, down=False )
                            logger.debug(f"PASSTHRU : {key}")
                        return True
                    else:
                        logger.debug(f"PASSTHRU : {key}")
                        return False

            finally:
                if oneshot:
                    key = KeyCondition( vk, self._modifier, down=True, oneshot=True )
                    self._do_configured_key_action(key)

        except Exception as e:
            print()
            logger.error(f"Unexpected error happened:\n{traceback.format_exc()}")

    def _setLastKeyText(self, key):
        s = str(key)
        if s.startswith("D-"): s = s[2:]
        keyhac_core.Console.setText("lastKey", s)

    def _on_key_hook_restored(self):
        logger.warning("Key hook timed out and has been restored.")

        # Modifier key state is not reliable anymore. Resetting.
        self._modifier = 0

    def _record_key( self, vk, up ):
        if self._record_status=="recording":
            if len(self._record_seq)>=1000:
                logger.error(f"Keyboard macro is too long.")
                return
            self._record_seq.append( ( vk, up ) )

    def _is_key_configured( self, key ):
        return key in self._unified_keytable

    def _do_configured_key_action( self, key ):

        logger.debug(f"INPUT    : {key}")
        
        action = None
        if key in self._unified_keytable:
            action = self._unified_keytable[key]

        left_multi_stroke = False
        if self._multi_stroke_keytable and not key.up and not key.oneshot and not key.vk in self._vk_mod_map:
            self._leave_multi_stroke()
            left_multi_stroke = True

        if action is None:
            return left_multi_stroke
        
        if callable(action):
            if hasattr(action, "__name__"):
                action_name = action.__name__
            else:
                action_name = repr(action)
            logger.debug(f"CALL     : {action_name}")
            action()

        elif isinstance(action, KeyTable):
            self._enter_multi_stroke(action)

        else:
            if type(action)!=list and type(action)!=tuple:
                action = [action]

            logger.debug(f"OUTPUT   : {action}")

            with self.get_input_context() as input_ctx:
                for item in action:
                    if type(item)==str:
                        input_ctx.send_key(item)
                    else:
                        raise TypeError;

        return True

    def _enter_multi_stroke( self, keytable ):

        logger.debug(f"Entering multi-stroke keytable - {keytable}")

        self._multi_stroke_keytable = keytable
        self._update_unified_keytable()

        # FIXME: show some UI to tell that multi stroke mode started
        #help_string = self._multi_stroke_keytable.helpString()
        #if help_string:
        #    self.popBalloon( "MultiStroke", help_string )

    def _leave_multi_stroke(self):

        if self._multi_stroke_keytable:
    
            logger.debug(f"Leaving multi-stroke keytable - {self._multi_stroke_keytable}")

            self._multi_stroke_keytable = None
            self._update_unified_keytable()

            #self.closeBalloon( "MultiStroke" )

    def _update_unified_keytable(self):

        self._unified_keytable = {}

        if self._multi_stroke_keytable:
            self._unified_keytable.update(self._multi_stroke_keytable.table)
        else:
            for focus_condition, keytable in self._keytable_list:
                if focus_condition.check(self._focus_path, self._focus_elm):
                    self._unified_keytable.update(keytable.table)

    @property
    def focus(self):
        return self._focus_elm

def configure():
    Keymap.getInstance().configure()
