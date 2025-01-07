import keyhac_console

logger = keyhac_console.getLogger("Replay")

class KeyReplayBuffer:

    def __init__(self):
        self.recording = False
        self.seq = []
        self.max_seq = 1000

    def record(self, vk: int, down: bool = True):
        if self.recording:
            if len(self.seq)>=self.max_seq:
                logger.error(f"Key replay buffer is full")
                return
            self.seq.append((vk,down))

    def start_recording(self):
        self.seq = []
        self.recording = True
        logger.info(f"Recording started")

    def stop_recording(self):

        if self.recording:

            key_table = [False] * 256
            normalized_seq = []

            for vk, down in self.seq:
                if down:
                    key_table[vk] = True
                    normalized_seq.append( [vk, down, False] ) # Not finalized until key up event comes
                else:
                    if key_table[vk]:
                        key_table[vk] = False

                        # Finalize preceeding key down records
                        for i in range(len(normalized_seq)-1,-1,-1):
                            if normalized_seq[i][0] == vk:
                                if normalized_seq[i][1]:
                                    if not normalized_seq[i][2]:
                                        normalized_seq[i][2] = True
                                    else:
                                        break
                                else:
                                    break

                        normalized_seq.append([vk, down, True])

            self.seq = []
            for vk, down, finalized in normalized_seq:
                if finalized:
                    self.seq.append((vk, down))

            self.recording=False

        logger.info(f"Recording stopped")

    def toggle_recording(self):
        if self.recording:
            return self.stop_recording()
        else:
            return self.start_recording()

    def clear(self):
        self.seq = []
        self.recording = False
        logger.info(f"Cleared buffer")

    def playback(self):

        # FIXME: find better solution
        # Avoid partial import error
        from keyhac_main import Keymap

        if self.recording:
            logger.warning(f"Still recording - canceling playback")
            return

        if not self.seq:
            logger.warning(f"Replay buffer is empty")
            return

        logger.info(f"Playing")

        keymap = Keymap.getInstance()
        for vk, down in self.seq:
            if down:
                if not keymap._on_key_down(vk):
                    with keymap.get_input_context() as input_ctx:
                        input_ctx.send_key_by_vk(vk,down)
            else:
                if not keymap._on_key_up(vk):
                    with keymap.get_input_context() as input_ctx:
                        input_ctx.send_key_by_vk(vk,down)
