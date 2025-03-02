from keyhac_core import Hook
from keyhac_const import *
from keyhac_key import KeyCondition

class InputContext:
    
    """
    A class to send multiple key strokes

    InputContext object sends virtual key events by managing current real key state and virtual key state.
    To create InputContext object, use Keymap.get_input_context(). Don't directly use InputContext.__init__().

    Use with statement to call the Keymap.get_input_context(). Key events are accumerated in this object, 
    and sent at once when leaving the context.

    usage:
        with keymap.get_input_context() as input_ctx:
            input_ctx.send_key("Cmd-Left")
            input_ctx.send_key("Cmd-Shift-Right")
    """

    def __init__(self, keymap, replay=False):

        """
        Initialize the input context.
        To create InputContext object, use Keymap.get_input_context(). Don't directly use InputContext.__init__().
        """

        self._keymap = keymap
        self._replay = replay
        self._entered = False
        self._input_seq = []

    def __enter__(self):

        Hook.acquire_lock()

        self._entered = True

        # Need to get modifier state after locking hook
        self._real_modifier = self._keymap._modifier
        self._virtual_modifier = self._keymap._modifier
        self._vk_mod_map = self._keymap._vk_mod_map

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._flush()
        finally:
            self._entered = False
            Hook.release_lock()

    def __str__(self):
        return str(self._input_seq)

    def send_key(self, s: str) -> None:

        """
        Send a key stroke using a string expression. (e.g., "Cmd-Left")

        Args:
            s: Key expression string
        """

        if not self._entered:
            raise ValueError("Not in the context.")

        s = s.upper()

        vk = None
        mod = 0
        down = None

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.str_to_mod( token, force_LR=True )
            except ValueError:
                if token=="D":
                    down = True
                elif token=="U":
                    down = False
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.str_to_vk(token)

        self.send_modifier_keys(mod)

        if down==True:
            self._input_seq.append( ("keyDown", vk) )
        elif down==False:
            self._input_seq.append( ("keyUp", vk) )
        else:
            self._input_seq.append( ("keyDown", vk) )
            self._input_seq.append( ("keyUp", vk) )

    def send_key_by_vk(self, vk: int, down: bool = True) -> None:

        """
        Send a key stroke with a key code and direction.

        Args:
            vk: Key code
            down: True: key down, False: key up
        """

        if not self._entered:
            raise ValueError("Not in the context.")

        if down:
            event_name = "keyDown"
        else:
            event_name = "keyUp"
        self._input_seq.append( (event_name, vk) )

    def send_modifier_keys(self, mod: int):

        """
        Send modifier key events to match the target modifier state

        Args:
            mod: Target modifier state
        """

        # Key down modifier keys
        for vk_mod in self._vk_mod_map.items():
            # Ignore user modifier keys (when not replay mode), otherwise it causes key events of original meaning
            if (vk_mod[1] & MODKEY_USER_ALL) and (not self._replay):
                continue
            if not ( vk_mod[1] & self._virtual_modifier ) and ( vk_mod[1] & mod ):
                self._input_seq.append( ("keyDown", vk_mod[0]) )
                self._virtual_modifier |= vk_mod[1]

        # Key up modifier keys
        for vk_mod in self._vk_mod_map.items():
            # Ignore user modifier keys (when not replay mode), otherwise it causes key events of original meaning
            if (vk_mod[1] & MODKEY_USER_ALL) and (not self._replay):
                continue
            if ( vk_mod[1] & self._virtual_modifier ) and not ( vk_mod[1] & mod ):
                self._input_seq.append( ("keyUp", vk_mod[0]) )
                self._virtual_modifier &= ~vk_mod[1]

    def _flush(self):
        self.send_modifier_keys(self._real_modifier)
        for event in self._input_seq:
            Hook.send_keyboard_event(event[0], event[1], self._replay)
        self._input_seq = []

