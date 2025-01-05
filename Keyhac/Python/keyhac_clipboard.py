import re

from keyhac_core import Hook, Clipboard

class ClipboardHistory:

    def __init__(self):
        self._items = []
        self._max_items = 100
        Hook.set_callback("Clipboard", self._on_clipboard)

    def _on_clipboard(self, s):
        clip = Clipboard.get_current()
        label = clip.get_string()
        if s:
            label = re.sub(r"\s+", " ", label).strip()
            self._items.insert(0, (clip, label) )
        
        while len(self._items) > self._max_items:
            oldest, _ = self._items.pop()
            oldest.destroy()
        
        self._dump()

    def pop_clipboard(self):

        if len(self._items)<=1:
            return

        latest, _ = self._items.pop(0)
        latest.destroy()
        
        Clipboard.set_current( self._items[0][0] )
        
        self._dump()

    def items(self):

        for item in self._items:
            yield item

    def _dump(self):

        print("------")
        for i, (_, label) in enumerate(self._items):
            print(f"Clipboard[{i}]:", label)

