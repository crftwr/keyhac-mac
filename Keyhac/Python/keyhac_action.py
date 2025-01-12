import json
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from keyhac_core import Chooser, Clipboard
from keyhac_main import Keymap
import keyhac_console
from keyhac_const import *

logger = keyhac_console.getLogger("Action")

class ThreadedAction:

    """
    Base class for threaded actions.

    To run a time consuming task as an output key action, you need to use threads.
    ThreadedAction helps to define threaded action classes easily.

    To define your own threaded action class, derive the ThreadedAction class
    and implement starting(), run(), and finished() methods.
    run() is executed in a thread pool for time consuming tasks.
    starting() and finished() are for light-weight tasks 
    and they are executed before and after run().
    """

    thread_pool = ThreadPoolExecutor(max_workers=16)

    def __init__(self):
        pass

    def __repr__(self):
        return f"ThreadedAction()"

    def __call__(self):
        self.starting()
        future = ThreadedAction.thread_pool.submit(self.run)
        future.add_done_callback(self._done_callback)

    def _done_callback(self, future):
        try:
            self.finished(future.result())
        except Exception as e:
            print()
            logger.error(f"Threaded action failed:\n{traceback.format_exc()}")

    def starting(self):
        """
        Virtual method called immediately when the action is triggered.
        """

    def run(self) -> Any:
        """
        Virtual method called in the thread pool.

        This method can include time consuming tasks.

        Returns:
            Any types of objects
        """

    def finished(self, result: Any) -> None:
        """
        Virtual method called after run() finished.

        Args:
            result: returned value from run().
        """

class MoveWindow:

    """
    A action class to move focused window
    """

    def __init__(self, x: int, y: int):

        """
        Initializes the action object.

        Args:
            x: horizontal distance to move
            y: vertical distance to move
        """

        self.x = x
        self.y = y

    def __call__(self):

        elm = Keymap.getInstance().focus

        while elm:
            role = elm.get_attribute_value("AXRole")
            if role=="AXWindow":
                break
            elm = elm.get_attribute_value("AXParent")

        if elm:
            names = elm.get_attribute_names()
            pos = elm.get_attribute_value("AXPosition")
            pos[0] += self.x
            pos[1] += self.y
            elm.set_attribute_value("AXPosition", "point", pos)

    def __repr__(self):
        return f"MoveWindow({self.x},{self.y})"


class LaunchApplication(ThreadedAction):

    """
    A action class to launch an application.

    This action launches the application you specified if it is not running yet.
    If the application is already running, macOS automatically make it foreground.
    """

    def __init__(self, app_name):

        """
        Initializes the action object.

        Args:
            app_name: Name of the application (e.g., "Terminal.app")
        """

        self.app_name = app_name

    def run(self):
        cmd = ["open", "-a", self.app_name]
        logger.info(f"Launching {self.app_name}")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: logger.info(r.stdout.strip())
        if r.stderr: logger.error(r.stderr.strip())

    def __repr__(self):
        return f'LaunchApplication("{self.app_name}")'


class ChooserAction:

    """
    Base class for actions to use Chooser window.

    To define your own action class to use Chooser, derive the ChooserAction class
    and implement list_items() and on_chosen() methods.
    list_items() is executed when the Chooser opens to list items.
    on_chosen() is executed when an item is chosen and the Chooser closes.
    """

    def __init__(self):
        pass

    def __call__(self):

        items = self.list_items()

        # Get originally focused window and application
        elm = Keymap.getInstance().focus
        window = None
        app = None
        while elm:
            role = elm.get_attribute_value("AXRole")
            if role=="AXWindow":
                window = elm
            elif role=="AXApplication":
                app = elm
            elm = elm.get_attribute_value("AXParent")

        def _focus_original_app():
            app.set_attribute_value("AXFrontmost", "bool", True)

        def _on_selected(arg):
            arg = json.loads(arg)
            index = int(arg["index"])
            modifier_flags = int(arg["modifierFlags"])

            item = items[index]
            
            _focus_original_app()

            self.on_chosen(item, modifier_flags)

        def _on_canceled(arg):
            _focus_original_app()

        if window:
            window_frame = window.get_attribute_value("AXFrame")

            chooser = Chooser("clipboard", items, _on_selected, _on_canceled)
            chooser.open((int(window_frame[0]), int(window_frame[1]), int(window_frame[2]), int(window_frame[3])))

    def list_items(self):
        
        """
        Virtual method to list items.

        Returns:
            List of tuple (icon string, label string, ...)
        """
        
        return []

    def on_chosen(self, item, modifier_flags: int) -> None:

        """
        Virtual method to handle chosen item.

        Args:
            item: Chosen item
            modifier_flags: Combination of pressed modifier flags (MODKEY_SHIFT, etc)
        """
        
        pass

    def __repr__(self):
        return f"ChooserAction()"

def _on_clipboard_chosen_common(clip, modifier_flags: int):

    keymap = Keymap.getInstance()

    # Add quote mark when alt key is pressed
    if modifier_flags & MODKEY_ALT:
        s = clip.get_string()
        lines = []
        for line in s.splitlines(keepends=True):
            lines.append("> " + line)
        s = "".join(lines)
        clip = Clipboard()
        clip.set_string(s)

    # Set current clipboard
    keymap.clipboard_history.set_current(clip)

    # Don't paste when shift key is pressed        
    if modifier_flags & MODKEY_SHIFT:
        return

    # Paste
    with keymap.get_input_context() as input_ctx:
        input_ctx.send_key("Cmd-V")

class ShowClipboardHistory(ChooserAction):

    """
    Action class to show clipboard history with Chooser window.
    """

    def __init__(self):

        """
        Initializes the ShowClipboardHistory object.
        """

        super().__init__()

    def list_items(self):

        items = []
        for clip, label in Keymap.getInstance().clipboard_history.items():
            items.append( ( "📋", label, clip) )
        return items
    
    def on_chosen(self, item, modifier_flags: int):
        _on_clipboard_chosen_common(item[2], modifier_flags)

    def __repr__(self):
        return f"ShowClipboardHistory()"


class ShowClipboardSnippets(ChooserAction):

    """
    Action class to show clipboard snippets with Chooser window.
    """

    def __init__(self, snippets):
        super().__init__()
        self.snippets = snippets

    def list_items(self):
        return self.snippets
    
    def on_chosen(self, item, modifier_flags: int):

        # Get snippet, 1) from 2nd element, 2) from 3rd element, 3) by calling 3rd element
        s = None
        if len(item)==2:
            s = item[1]
        elif len(item)==3:
            if isinstance(item[2], str):
                s = item[2]
            elif callable(item[2]):
                s = item[2]()
        
        if not isinstance(s, str):
            return

        clip = Clipboard()
        clip.set_string(s)

        _on_clipboard_chosen_common(clip, modifier_flags)

    def __repr__(self):
        return f"ShowClipboardSnippets({self.snippets})"


class StartRecordingKeys:

    """
    A action class to start recording keys in replay buffer
    """

    def __init__(self):
        """
        Initializes the StartRecordingKeys object.
        """
        pass

    def __call__(self):
        keymap = Keymap.getInstance()
        keymap.replay_buffer.start_recording()

    def __repr__(self):
        return f"StartRecordingKeys()"


class StopRecordingKeys:

    """
    A action class to stop recording keys in replay buffer
    """

    def __init__(self):
        """
        Initializes the StopRecordingKeys object.
        """
        pass

    def __call__(self):
        keymap = Keymap.getInstance()
        keymap.replay_buffer.stop_recording()

    def __repr__(self):
        return f"StopRecordingKeys()"


class ToggleRecordingKeys:

    """
    A action class to start or stop recording keys in replay buffer
    """

    def __init__(self):
        """
        Initializes the ToggleRecordingKeys object.
        """
        pass

    def __call__(self):
        keymap = Keymap.getInstance()
        keymap.replay_buffer.toggle_recording()

    def __repr__(self):
        return f"ToggleRecordingKeys()"


class PlaybackRecordedKeys:

    """
    A action class to playback recorded keys in replay buffer
    """

    def __init__(self):
        """
        Initializes the PlaybackRecordedKeys object.
        """
        pass

    def __call__(self):
        keymap = Keymap.getInstance()
        keymap.replay_buffer.playback()

    def __repr__(self):
        return f"PlaybackRecordedKeys()"

