import keyhac_core
from keyhac_const import *
from keyhac_key import KeyCondition

class InputContext:
    
    def __init__(self, real_modifier, vk_mod_map):
        self._real_modifier = real_modifier
        self._virtual_modifier = real_modifier
        self._vk_mod_map = vk_mod_map
        self._input_seq = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    def __str__(self):
        return str(self._input_seq)

    def send_modifier_keys(self, mod):

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

    def send_key(self, s):

        s = s.upper()

        vk = None
        mod = 0
        up = None

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.str_to_mod( token, force_LR=True )
            except ValueError:
                if token=="D":
                    up = False
                elif token=="U":
                    up = True
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.str_to_vk(token)

        self.send_modifier_keys(mod)

        if up==True:
            self._input_seq.append( ("keyUp", vk) )
        elif up==False:
            self._input_seq.append( ("keyDown", vk) )
        else:
            self._input_seq.append( ("keyDown", vk) )
            self._input_seq.append( ("keyUp", vk) )

    def send_key_by_vk(self, vk, down=True):

        if down:
            event_name = "keyDown"
        else:
            event_name = "keyUp"
        self._input_seq.append( (event_name, vk) )

    def flush(self):
        self.send_modifier_keys(self._real_modifier)
        for event in self._input_seq:
            keyhac_core.Hook.sendKeyboardEvent(event[0], event[1])
        self._input_seq = []
