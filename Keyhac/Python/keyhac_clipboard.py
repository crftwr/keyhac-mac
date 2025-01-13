import os
import re
import json
import collections

from keyhac_core import Hook, Clipboard

class ClipboardHistory:

    """
    Clipboard history

    ClipboardHistory object automatically captures historical clipboard contents.
    Currently this class only supports text data.

    ClipboardHistory class has following class variables to configure the maximum length and data size:
    - max_items: Maximum number of clipboard history item to keep (default: 1000 items)
    - max_label_length: Maximum length of label strings of clipboard items (default: 4096 bytes)
    - max_data_size: Maximum data size of single clipboard to keep (default: 10 * 1024 * 1024 = 10MB)
    - max_persist_data_size: Maximum data size of single clipboard to save in persistent file (default: 64 * 1024 = 64KB)
    """

    max_items = 1000
    max_label_length = 4096
    max_data_size = 10 * 1024 * 1024
    max_persist_data_size = 64 * 1024

    def __init__(self):

        """
        Initializes the ClipboardHistory object.

        Loads saved clipboard history data from file (`~/.keyhac/clipboard.json`), and installs clipboard hook to the OS.
        """

        self.filename = os.path.expanduser("~/.keyhac/clipboard.json")
        
        self._items = collections.OrderedDict()
        self.dirty = False

        self._load()

        Hook.set_callback("Clipboard", self._on_clipboard)

    def _on_clipboard(self, s):
        
        clip = Clipboard.get_current()

        self.add_item(clip)

        self.dirty = True

        # FIXME: reduce file I/O frequency
        self._save()

    def items(self):

        """
        Iterates the list of Clipboard objects.

        First item is the latest.

        Returns:
            Clipboard object and shortened label (Clipboard, str)
        """

        for item in reversed(self._items.values()):
            yield item

    def add_item(self, clip: Clipboard) -> None:

        """
        Add a Clipboard object to the history.

        Existing duplicate items are automatically deleted.

        Args:
            clip: Clipboard object to add
        """

        s = clip.get_string()
        if s:
            if len(s) > self.max_data_size:
                return

            label = self._shorten_string(s)

            if s in self._items:
                del self._items[s]

            self._items[s] = (clip, label)

        self._cap_num_items()

    def set_current(self, clip: Clipboard) -> None:

        """
        Set a Clipboard object to the OS's clipboard and latest entry of the clipboard history

        Args:
            clip: Clipboard object to set
        """

        self.add_item(clip)
        Clipboard.set_current(clip)

    def get_current(self) -> Clipboard:

        """
        Get the current Clipboard object from the clipboard history.

        Returns:
            Current Clipboard object 
        """

        for clip, label in self.items():
            return clip

    def _shorten_string(self, s):
        s = s[:self.max_label_length]
        return re.sub(r"\s+", " ", s).strip()

    def _save(self):

        d = {
            "clipboard_history" : [
            ]
        }

        for clip, label in self.items():
            s = clip.get_string()
            if s and len(s) <= self.max_persist_data_size:
                d["clipboard_history"].append(
                    {
                        "type": "string",
                        "data": s
                    }
                )

        os.makedirs( os.path.dirname(self.filename), exist_ok=True )
        with open(self.filename, "w") as fd:
            json.dump(d, fd)

        self.dirty = False

    def _load(self):

        self._items.clear()

        if os.path.exists(self.filename):
            with open(self.filename) as fd:
                d = json.load(fd)

                for item in reversed(d["clipboard_history"]):
                    if item["type"]=="string":
                        s = item["data"]

                        clip = Clipboard()
                        clip.set_string(s)

                        self.add_item(clip)

        self.dirty = False

    def _cap_num_items(self):

        total_data_size = 0
        while len(self._items) > self.max_items:
            s, (clip, label) = self._items.popitem(last=False)
            clip.destroy()
