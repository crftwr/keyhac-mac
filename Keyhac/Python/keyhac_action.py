import json
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from keyhac_core import Chooser
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

class PasteClipboardHistory:

    def __init__(self):
        pass

    def __call__(self):

        keymap = Keymap.getInstance()

        items = []
        for clip, label in keymap.clipboard_history.items():
            items.append( ( "📋", label, clip) )

        # Get originally focused window and application
        elm = keymap.focus
        window = None
        app = None
        while elm:
            role = elm.get_attribute_value("AXRole")
            if role=="AXWindow":
                window = elm
            elif role=="AXApplication":
                app = elm
            elm = elm.get_attribute_value("AXParent")

        def focus_original_app():
            app.set_attribute_value("AXFrontmost", "bool", True)

        def on_selected(arg):
            print("onSelected", arg)
            arg = json.loads(arg)
            index = int(arg["index"])
            item = items[index]
            
            focus_original_app()

            keymap.clipboard_history.set_current(item[2])
            
            with keymap.get_input_context() as input_ctx:
                input_ctx.send_key("Cmd-V")

        def on_canceled(arg):
            focus_original_app()

        if window:
            window_frame = window.get_attribute_value("AXFrame")

            chooser = Chooser("clipboard", items, on_selected, on_canceled)
            chooser.open((int(window_frame[0]), int(window_frame[1]), int(window_frame[2]), int(window_frame[3])))

    def __repr__(self):
        return f"ShowClipboardHistory()"
