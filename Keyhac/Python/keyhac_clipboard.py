import re
import collections

from keyhac_core import Hook, Clipboard

class ClipboardHistory:

    def __init__(self):
        self._items = collections.OrderedDict()
        self._max_items = 100
        Hook.set_callback("Clipboard", self._on_clipboard)

    def _on_clipboard(self, s):
        
        clip = Clipboard.get_current()
        s = clip.get_string()
        if s:
            # Prepare shortened list item
            label = re.sub(r"\s+", " ", s).strip()

            # Remove duplicate entry
            if s in self._items:
                del self._items[s]

            # Add as latest
            self._items[s] = (clip, label)
        
        # Remove oldest item if number of items exceeded
        while len(self._items) > self._max_items:
            s, clip, label = self._items.popitem(last=False)
            clip.destroy()
        
        self._dump()

    def items(self):

        for item in reversed(self._items.values()):
            yield item

    def _dump(self):

        print("------")
        for i, (_, label) in enumerate(reversed(self._items.values())):
            print(f"Clipboard[{i}]:", label)
