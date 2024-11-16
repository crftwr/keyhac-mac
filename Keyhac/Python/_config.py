import sys
import time
import urllib.parse
import subprocess
from keyhac import *

logger = getLogger("Config")

def configure(keymap):

    # Replacing Right-Shift key with BackSpace
    keymap.replace_key( "RShift", "Back" )

    # Defining user defined modifier keys
    keymap.define_modifier( "RCmd", "RUser0" )
    keymap.define_modifier( "RAlt", "RUser1" )

    # =====================================================
    # Global key table
    # =====================================================

    keytable_global = keymap.define_keytable(focus_path_pattern="*")

    # -----------------------------------------------------
    # Fn-A: Sample of assigning callable object to key
    def hello_world():

        print("Hello World!")

        logger.debug("Debug message via Console logger")
        logger.info("Information message via Console logger")
        logger.warning("Warning message via Console logger")
        logger.error("Error message via Console logger")
        logger.critical("Critical message via Console logger")

    keytable_global["Fn-A"] = hello_world

    # -----------------------------------------------------
    # User0-Z: Test of threaded action
    class ThreadedActionTest(ThreadedAction):
        def __init__(self):
            pass

        def starting(self):
            logger.info("ThreadedActionTest starting")

        def run(self):
            logger.info("ThreadedActionTest running")
            time.sleep(3)

        def finished(self, result):
            logger.info(f"ThreadedActionTest finished. result={result}")

    keytable_global["User0-Z"] = ThreadedActionTest()


    # -----------------------------------------------------
    # User0-D: Lookup selected words in the dictionary app
    def lookup_dictionary():

        elm = keymap.focus

        if "AXSelectedText" in elm.getAttributeNames():
            words = elm.getAttributeValue("AXSelectedText")
            words = urllib.parse.quote(words)
            cmd = ["open", f"dict://{words}"]
            subprocess.run(cmd)

    keytable_global["User0-D"] = lookup_dictionary

    # -----------------------------------------------------
    # User0-G: Search selected words on Google
    def search_google():

        elm = keymap.focus

        if "AXSelectedText" in elm.getAttributeNames():
            words = elm.getAttributeValue("AXSelectedText")
            logger.info(f"Searching on Google: {words}")
            words = urllib.parse.quote(words)
            cmd = ["open", f"https://www.google.com/search?q={words}"]
            subprocess.run(cmd)

    keytable_global["User0-G"] = search_google

    # -----------------------------------------------------
    # Fn-M: Zoom window (Test of UIElement.performAction)
    def zoom_window():

        elm = keymap.focus

        while elm:
            role = elm.getAttributeValue("AXRole")
            if role=="AXWindow":
                break
            elm = elm.getAttributeValue("AXParent")

        if elm:
            names = elm.getAttributeNames()
            if "AXZoomButton" in names:
                elm = elm.getAttributeValue("AXZoomButton")
                if elm:
                    actions = elm.getActionNames()
                    elm.performAction("AXPress")

    keytable_global["Fn-M"] = zoom_window

    # -----------------------------------------------------
    # User0-Left/Right/Up/Down: Move current active window
    class MoveWindow:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __call__(self):

            elm = keymap.focus

            while elm:
                role = elm.getAttributeValue("AXRole")
                if role=="AXWindow":
                    break
                elm = elm.getAttributeValue("AXParent")

            if elm:
                names = elm.getAttributeNames()
                pos = elm.getAttributeValue("AXPosition")
                pos[0] += self.x
                pos[1] += self.y
                elm.setAttributeValue("AXPosition", "point", pos)

    keytable_global["User0-Left"]  = MoveWindow(-10,0)
    keytable_global["User0-Right"] = MoveWindow(+10,0)
    keytable_global["User0-Up"]    = MoveWindow(0,-10)
    keytable_global["User0-Down"]  = MoveWindow(0,+10)

    # -----------------------------------------------------
    # User0-T/F/C: Launch an applications
    class LaunchApplication(ThreadedAction):
        def __init__(self, app_name):
            self.app_name = app_name

        def run(self):
            cmd = ["open", "-a", self.app_name]
            logger.info(f"Launching {self.app_name}")
            subprocess.run(cmd, check=True)

        def __repr__(self):
            return f'LaunchApplication("{self.app_name}")'

    keytable_global["User0-T"] = LaunchApplication("Terminal.app")
    keytable_global["User0-F"] = LaunchApplication("ForkLift.app")
    keytable_global["User0-C"] = LaunchApplication("Visual Studio Code.app")


    # =====================================================
    # Key table for Xcode
    # =====================================================

    keytable_xcode = keymap.define_keytable( focus_path_pattern="/AXApplication(Xcode)/*/AXTextArea()" )

    # -----------------------------------------------------
    # Fn-A: Overriding global keytable configuration
    def hello_xcode():
        print("Hello Xcode!")

    keytable_xcode["Fn-A"] = hello_xcode

    # -----------------------------------------------------
    # Fn-L: Select whole line
    keytable_xcode["Fn-L"] = "Cmd-Left", "Cmd-Left", "Shift-Cmd-Right"

    # -----------------------------------------------------
    # Test of Multi-stroke key binding
    keytable_xcode["Ctrl-X"] = keymap.define_keytable(name="Ctrl-X")
    keytable_xcode["Ctrl-X"]["Ctrl-O"] = "Cmd-O"


    # =====================================================
    # Custom focus condition
    # =====================================================

    # Use custom logic to detect terminal kind of applications
    def is_terminal_window(elm):
        try:
            window_elm = elm.getAttributeValue("AXWindow")
            if window_elm:
                app_elm = window_elm.getAttributeValue("AXParent")
                if app_elm:
                    app_title = app_elm.getAttributeValue("AXTitle")
                    return app_title in ("Terminal", "iTerm2")
            return False
        except KeyError:
            return False

    keytable_terminal = keymap.define_keytable( custom_condition_func = is_terminal_window )

    # -----------------------------------------------------
    # Fn-A: Overriding global keytable configuration
    def hello_terminal():
        print("Hello Terminal!")

    keytable_terminal["Fn-A"] = hello_terminal
