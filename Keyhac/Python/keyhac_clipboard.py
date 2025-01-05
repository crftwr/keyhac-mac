import os
import re
import json
import collections

from keyhac_core import Hook, Clipboard

class ClipboardHistory:

    def __init__(self):

        self.filename = os.path.expanduser("~/.keyhac/clipboard.json")
        
        self._items = collections.OrderedDict()
        self._max_items = 100
        self.dirty = False

        self.load()

        Hook.set_callback("Clipboard", self._on_clipboard)

    def _on_clipboard(self, s):
        
        clip = Clipboard.get_current()

        self.add_item(clip)

        self.dirty = True

        # FIXME: reduce file I/O frequency
        self.save()

    def items(self):

        for item in reversed(self._items.values()):
            yield item

    def add_item(self, clip):

        s = clip.get_string()
        if s:
            label = self.shorten_string(s)

            if s in self._items:
                del self._items[s]

            self._items[s] = (clip, label)

        self._cap_num_items()

    def set_current(self, clip):
        self.add_item(clip)
        Clipboard.set_current(clip)

    def get_current(self):
        for clip, label in self.items():
            return clip

    def shorten_string(self, s):
        return re.sub(r"\s+", " ", s).strip()

    def save(self):

        d = {
            "clipboard_history" : [
            ]
        }

        for clip, label in self.items():
            s = clip.get_string()
            if s:
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

    def load(self):

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

        while len(self._items) > self._max_items:
            s, (clip, label) = self._items.popitem(last=False)
            clip.destroy()
