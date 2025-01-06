import json
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from keyhac_core import Chooser, Clipboard
from keyhac_main import Keymap
import keyhac_console

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
    A key action class to move focused window
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
    A key action class to launch an application.

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


class ChoosingAction:

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
            item = items[index]
            
            _focus_original_app()

            self.on_chosen(item)

        def _on_canceled(arg):
            _focus_original_app()

        if window:
            window_frame = window.get_attribute_value("AXFrame")

            chooser = Chooser("clipboard", items, _on_selected, _on_canceled)
            chooser.open((int(window_frame[0]), int(window_frame[1]), int(window_frame[2]), int(window_frame[3])))

    def list_items(self):
        return []

    def paste(self, clip):

        keymap = Keymap.getInstance()

        keymap.clipboard_history.set_current(clip)
        
        with keymap.get_input_context() as input_ctx:
            input_ctx.send_key("Cmd-V")

    def __repr__(self):
        return f"ChoosingAction()"


class ChooseClipboardHistory(ChoosingAction):

    def __init__(self):
        super().__init__()

    def list_items(self):
        items = []
        for clip, label in Keymap.getInstance().clipboard_history.items():
            items.append( ( "📋", label, clip) )
        return items
    
    def on_chosen(self, item):
        self.paste(item[2])

    def __repr__(self):
        return f"ChooseClipboardHistory()"


class ChooseSnippet(ChoosingAction):

    def __init__(self, snippets):
        super().__init__()
        self.snippets = snippets

    def list_items(self):
        return self.snippets
    
    def on_chosen(self, item):

        s = None
        if len(item)==2:
            s = item[1]
        elif len(item)==3:
            if isinstance(item[2], str):
                s = item[2]
            elif callable(item[2]):
                s = item[2]()

        if isinstance(s, str):
            clip = Clipboard()
            clip.set_string(s)
            self.paste(clip)

    def __repr__(self):
        return f"ChooseSnippet({self.snippets})"
