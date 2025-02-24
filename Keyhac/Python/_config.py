import time
import datetime
import urllib.parse
import json
import subprocess

from keyhac import *

logger = getLogger("Config")

def configure(keymap):

    # Replacing Right-Shift key with BackSpace
    #keymap.replace_key( "RShift", "Back" )

    # Defining user defined modifier keys
    keymap.define_modifier("RCmd", "RUser0")
    keymap.define_modifier("RAlt", "RUser1")

    # Configure clipboard history
    keymap.clipboard_history.max_items = 1000
    keymap.clipboard_history.max_data_size = 10 * 1024 * 1024
    

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
    # Fn-V: Show clipboard history by Chooser window
    keytable_global["Fn-V"] = ShowClipboardHistory()

    # -----------------------------------------------------
    # Fn-Shift-V: Show snippets by Chooser window
    class DateTimeString:
        def __init__(self, format):
            self.format = format
        def __call__(self):
            return datetime.datetime.now().strftime(self.format)

    keytable_global["Fn-Shift-V"] = ShowClipboardSnippets([
        ("👤", "myname@email.address"),
        ("👤", "01-2345-6789"),
        ("👤", "Mailing address", "400 Broad St, Seattle, WA 98109"),
        ("👤", "Zoom invitation",
            "\n".join((
                "John Doe is inviting you to a scheduled Zoom meeting.",
                "",
                "Topic: John Doe's Personal Meeting Room",
                "Join Zoom Meeting",
                "https://us04web.zoom.us/j/1234567890?pwd=abcdefgHIJKLMNopqrstuVWXYZ.1",
                "",
                "Meeting ID: 123 456 7890",
                "Passcode: ABCDEF",
            ))
        ),
        ("🕒", "YYYY-MM-DD HH:MM:SS", DateTimeString("%Y-%m-%d %H:%M:%S")),
        ("🕒", "YYYYMMDD_HHMMSS", DateTimeString("%Y%m%d_%H%M%S")),
    ])

    # -----------------------------------------------------
    # Cmd-Shift-V: Choose clipboard tool by Chooser window
    def uppercase(clip):
        s = clip.get_string()
        s = s.upper()
        clip = Clipboard()
        clip.set_string(s)
        return clip

    def lowercase(clip):
        s = clip.get_string()
        s = s.lower()
        clip = Clipboard()
        clip.set_string(s)
        return clip

    def pretty_json(clip):
        s = clip.get_string()
        try:
            d = json.loads(s)
        except json.JSONDecodeError as e:
            logger.error("Clipboard content is not a valid JSON string.")
            return clip
        s = json.dumps(d, indent=4)
        clip = Clipboard()
        clip.set_string(s)
        return clip

    keytable_global["Cmd-Shift-V"] = ShowClipboardTools([
        ("🔄", "Plain", ShowClipboardTools.to_plain),
        ("🔄", "Quote", ShowClipboardTools.quote),
        ("🔄", "Unindent", ShowClipboardTools.unindent),
        ("🔄", "Half Width", ShowClipboardTools.to_half_width),
        ("🔄", "Full Width", ShowClipboardTools.to_full_width),
        ("🔄", "Uppercase", uppercase),
        ("🔄", "Lowercase", lowercase),
        ("🔄", "Pretty JSON", pretty_json),
    ])

    # -----------------------------------------------------
    # User0-Z: Test of threaded action
    class ThreadedActionTest(ThreadedAction):
        def __init__(self):
            pass

        def starting(self):
            logger.info("ThreadedActionTest starting")

        def run(self):
            logger.info("ThreadedActionTest running")

            for c in "Hello Keyhac":
                time.sleep(0.3)
                with keymap.get_input_context() as input_ctx:
                    if "a" <= c <= "z":
                        key = f"{c}"
                    elif "A" <= c <= "Z":
                        key = f"Shift-{c}"
                    elif c == " ":
                        key = f"Space"
                    logger.info(f"Sending key input from sub-thread - {key}")
                    input_ctx.send_key(key)

            return True

        def finished(self, result):
            logger.info(f"ThreadedActionTest finished. result={result}")

        def __repr__(self):
            return "ThreadedActionTest()"

    keytable_global["User0-Z"] = ThreadedActionTest()

    # -----------------------------------------------------
    # Fn-T: Translate selected text English <-> Japanese
    def translate_en_ja():

        # Get selected text
        elm = keymap.focus
        if "AXSelectedText" not in elm.get_attribute_names():
            logger.warning("Cannot pick up selected text")
            return
        text = elm.get_attribute_value("AXSelectedText")

        # Detect source language
        src_lang = "en"
        for c in text:
            c = ord(c)
            if (0x3000 <= c <= 0x30ff) or (0x4e00 <= c <= 0x9faf) or (0xff00 <= c <= 0xffef):
                src_lang = "ja"
                break
        
        # Construct URL
        quoted_text = urllib.parse.quote_plus(text)
        if src_lang == "en":
            url = f"https://translate.google.co.jp/?sl=en&tl=ja&text={quoted_text}&op=translate"
        elif src_lang == "ja":
            url = f"https://translate.google.co.jp/?sl=ja&tl=en&text={quoted_text}&op=translate"

        # Open browser
        logger.info(f"Translate: {text}")
        cmd = ["open", url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: logger.info(r.stdout.strip())
        if r.stderr: logger.error(r.stderr.strip())

    keytable_global["Fn-T"] = translate_en_ja

    # -----------------------------------------------------
    # User0-D: Lookup selected words in the dictionary app
    def lookup_dictionary():

        # Get selected text
        elm = keymap.focus
        if "AXSelectedText" not in elm.get_attribute_names():
            logger.warning("Cannot pick up selected text")
            return
        text = elm.get_attribute_value("AXSelectedText")

        # Open dictionary app
        logger.info(f"Dictionary: {text}")
        quoted_text = urllib.parse.quote_plus(text)
        cmd = ["open", f"dict://{quoted_text}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: logger.info(r.stdout.strip())
        if r.stderr: logger.error(r.stderr.strip())

    keytable_global["User0-D"] = lookup_dictionary

    # -----------------------------------------------------
    # User0-G: Search selected words on Google
    def search_google():

        # Get selected text
        elm = keymap.focus
        if "AXSelectedText" not in elm.get_attribute_names():
            logger.warning("Cannot pick up selected text")
            return
        text = elm.get_attribute_value("AXSelectedText")

        # Open browser
        logger.info(f"Google: {text}")
        quoted_text = urllib.parse.quote_plus(text)
        cmd = ["open", f"https://www.google.com/search?q={quoted_text}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: logger.info(r.stdout.strip())
        if r.stderr: logger.error(r.stderr.strip())

    keytable_global["User0-G"] = search_google

    # -----------------------------------------------------
    # Fn-M: Zoom window (Test of UIElement.perform_action)
    def zoom_window():

        elm = keymap.focus

        while elm:
            role = elm.get_attribute_value("AXRole")
            if role=="AXWindow":
                break
            elm = elm.get_attribute_value("AXParent")

        if elm:
            names = elm.get_attribute_names()
            if "AXZoomButton" in names:
                elm = elm.get_attribute_value("AXZoomButton")
                if elm:
                    actions = elm.get_action_names()
                    elm.perform_action("AXPress")

    keytable_global["Fn-M"] = zoom_window

    # -----------------------------------------------------
    # Fn-Shift-Left/Right/Up/Down: Move current active window
    keytable_global["Fn-Shift-Home"] = MoveWindow(direction="left", distance=10)
    keytable_global["Fn-Shift-End"] = MoveWindow(direction="right", distance=10)
    keytable_global["Fn-Shift-PageUp"] = MoveWindow(direction="up", distance=10)
    keytable_global["Fn-Shift-PageDown"] = MoveWindow(direction="down", distance=10)

    # -----------------------------------------------------
    # Fn-Cmd-Left/Right/Up/Down: Move current active window quickly to window/screen edge
    keytable_global["Fn-Cmd-Home"] = MoveWindow(direction="left", window_edge=True)
    keytable_global["Fn-Cmd-End"] = MoveWindow(direction="right", window_edge=True)
    keytable_global["Fn-Cmd-PageUp"] = MoveWindow(direction="up", window_edge=True)
    keytable_global["Fn-Cmd-PageDown"] = MoveWindow(direction="down", window_edge=True)

    # -----------------------------------------------------
    # User0-T/F/C: Launch an applications
    keytable_global["User0-F"] = LaunchApplication("ForkLift.app")
    keytable_global["User0-C"] = LaunchApplication("Visual Studio Code.app")
    
    # -----------------------------------------------------
    # One-shot RCmd: Launch Terminal
    keytable_global["O-RCmd"] = LaunchApplication("Terminal.app")

    # -----------------------------------------------------
    # Fn-1/2/3: Start, Stop, and Toggle recoding keys
    # Fn-4: Playback recorded keys
    keytable_global["Fn-1"] = StartRecordingKeys()
    keytable_global["Fn-2"] = StopRecordingKeys()
    keytable_global["Fn-3"] = ToggleRecordingKeys()
    keytable_global["Fn-4"] = PlaybackRecordedKeys()

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
            window_elm = elm.get_attribute_value("AXWindow")
            if window_elm:
                app_elm = window_elm.get_attribute_value("AXParent")
                if app_elm:
                    app_title = app_elm.get_attribute_value("AXTitle")
                    return app_title in ("Terminal", "iTerm2")
            return False
        except KeyError:
            return False

    keytable_terminal = keymap.define_keytable(custom_condition_func = is_terminal_window)

    # -----------------------------------------------------
    # Fn-A: Overriding global keytable configuration
    def hello_terminal():
        print("Hello Terminal!")

    keytable_terminal["Fn-A"] = hello_terminal

    # -----------------------------------------------------
    # One-shot RCmd: Deactivate terminal
    keytable_terminal["O-RCmd"] = "Cmd-Tab"
