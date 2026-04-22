import math
import json
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from keyhac_core import UIElement, Hook, Chooser, Clipboard
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
    The run() method is executed in a thread pool for time consuming tasks.
    The starting() and finished() methods are for light-weight tasks
    and they are executed before and after run() under exclusive control with keyboard hooks. 
    """

    thread_pool = ThreadPoolExecutor(max_workers=1)

    def __init__(self):
        pass

    def __repr__(self):
        return f"ThreadedAction()"

    def __call__(self):

        try:
            Hook.acquire_lock()
            self.starting()
        finally:
            Hook.release_lock()

        future = ThreadedAction.thread_pool.submit(self.run)
        future.add_done_callback(self._done_callback)

    def _done_callback(self, future):
        try:
            result = future.result()
            try:
                Hook.acquire_lock()
                self.finished(result)
            finally:
                Hook.release_lock()

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

class MoveWindow(ThreadedAction):

    """
    A action class to move focused window.

    The window is clamped within the current screen bounds. When the window
    reaches a screen edge, it can cross to an adjacent monitor in the movement
    direction. The macOS menu bar gap between screens is accounted for.
    """

    # Tolerance for detecting adjacent screens across the menu bar gap (pixels)
    ADJACENT_SCREEN_TOLERANCE = 50

    # Tolerance for detecting if the window is at the screen edge.
    # For "up" direction, uses ADJACENT_SCREEN_TOLERANCE to account for the
    # macOS menu bar preventing windows from reaching y=0.
    EDGE_TOLERANCE = 2

    def __init__(self, x:int = None, y:int = None, direction:str = "", distance:float = 10, window_edge:bool = False, screen_edge:bool = True):

        """
        Initializes the action object.

        Args:
            direction: either of "left", "right", "up", "down"
            distance: move amount (default: 10)
            window_edge: whether window stops at other windows' edges (default: False)
            screen_edge: whether window stops at screen edges (default: True)
        """

        # FIXME: deprecated arguments from ver v1.64
        if x or y:
            logger.warning(f"MoveWindow's arguments x, y are deprecated. Use direction and distance instead.")
            if x < 0:
                self.direction = "left"
                self.distance = abs(x)
            elif x > 0:
                self.direction = "right"
                self.distance = abs(x)
            elif y < 0:
                self.direction = "up"
                self.distance = abs(y)
            elif y > 0:
                self.direction = "down"
                self.distance = abs(y)
            else:
                self.direction = ""
                self.distance = 0
        else:
            self.direction = direction
            self.distance = distance

        self.window_edge = window_edge
        self.screen_edge = screen_edge
        self.wnd = None

    def starting(self):
        
        elm = Keymap.get_instance().focus

        # Get focused window
        while elm:
            role = elm.get_attribute_value("AXRole")
            if role=="AXWindow":
                break
            elm = elm.get_attribute_value("AXParent")

        self.wnd = elm

    @staticmethod
    def _get_best_screen(wnd_frame, screen_frames):
        """Find the screen that has the most overlap with the window."""
        wx, wy, ww, wh = wnd_frame[0], wnd_frame[1], wnd_frame[2], wnd_frame[3]
        best_screen = screen_frames[0] if screen_frames else None
        best_overlap = -1
        for sf in screen_frames:
            sx, sy, sw, sh = sf[0], sf[1], sf[2], sf[3]
            ox = max(0, min(wx + ww, sx + sw) - max(wx, sx))
            oy = max(0, min(wy + wh, sy + sh) - max(wy, sy))
            overlap = ox * oy
            if overlap > best_overlap:
                best_overlap = overlap
                best_screen = sf
        return best_screen

    @classmethod
    def _is_adjacent_in_direction(cls, current_screen, other_screen, direction):
        """Check if other_screen is adjacent to current_screen in the given direction.

        Uses a tolerance to account for the menu bar gap between visible screen areas.
        """
        cx, cy, cw, ch = current_screen[0], current_screen[1], current_screen[2], current_screen[3]
        sx, sy, sw, sh = other_screen[0], other_screen[1], other_screen[2], other_screen[3]
        tol = cls.ADJACENT_SCREEN_TOLERANCE
        if direction == "left":
            if abs((sx + sw) - cx) <= tol:
                if not (sy + sh <= cy or sy >= cy + ch):
                    return True
        elif direction == "right":
            if abs(sx - (cx + cw)) <= tol:
                if not (sy + sh <= cy or sy >= cy + ch):
                    return True
        elif direction == "up":
            if abs((sy + sh) - cy) <= tol:
                if not (sx + sw <= cx or sx >= cx + cw):
                    return True
        elif direction == "down":
            if abs(sy - (cy + ch)) <= tol:
                if not (sx + sw <= cx or sx >= cx + cw):
                    return True
        return False

    @classmethod
    def _find_adjacent_screen(cls, current_screen, screen_frames, direction):
        """Find the adjacent screen in the given direction, or None."""
        for sf in screen_frames:
            if sf is current_screen:
                continue
            if cls._is_adjacent_in_direction(current_screen, sf, direction):
                return sf
        return None

    def run(self):

        if not self.wnd:
            return None

        # Get current window frame
        this_window_frame = self.wnd.get_attribute_value("AXFrame")

        # Get screens info
        screen_frames = UIElement.get_screen_frames()
        current_screen = self._get_best_screen(this_window_frame, screen_frames)

        if not current_screen:
            return None

        ww = this_window_frame[2]
        wh = this_window_frame[3]
        sx, sy, sw, sh = current_screen[0], current_screen[1], current_screen[2], current_screen[3]

        # Check if the window is already at (or stuck near) the screen edge
        # in the movement direction. macOS menu bar prevents windows from
        # reaching y=0, so use a generous tolerance for the "up" direction.
        menu_bar_tol = self.ADJACENT_SCREEN_TOLERANCE
        edge_tol = self.EDGE_TOLERANCE
        at_edge = False
        if self.direction == "left":
            at_edge = (this_window_frame[0] - sx) <= edge_tol
        elif self.direction == "right":
            at_edge = ((sx + sw) - (this_window_frame[0] + ww)) <= edge_tol
        elif self.direction == "up":
            at_edge = (this_window_frame[1] - sy) <= menu_bar_tol
        elif self.direction == "down":
            at_edge = ((sy + sh) - (this_window_frame[1] + wh)) <= edge_tol

        if at_edge:
            adj = self._find_adjacent_screen(current_screen, screen_frames, self.direction)
            if adj is not None:
                ax, ay, aw, ah = adj[0], adj[1], adj[2], adj[3]
                if self.direction == "left":
                    this_window_frame[0] = ax + aw - ww
                elif self.direction == "right":
                    this_window_frame[0] = ax
                elif self.direction == "up":
                    this_window_frame[0] = max(ax, min(this_window_frame[0], ax + aw - ww))
                    this_window_frame[1] = ay + ah - wh
                elif self.direction == "down":
                    this_window_frame[0] = max(ax, min(this_window_frame[0], ax + aw - ww))
                    this_window_frame[1] = ay
                return this_window_frame[:2]
            # No adjacent monitor — fall through to normal move (which will clamp)

        # Initial move distance
        distance = self.distance

        # Prepare window edge position
        if self.direction=="left":
            front_pos = this_window_frame[0]
            front_range = ( this_window_frame[1], this_window_frame[1] + this_window_frame[3] )
        elif self.direction=="right":
            front_pos = this_window_frame[0] + this_window_frame[2]
            front_range = ( this_window_frame[1], this_window_frame[1] + this_window_frame[3] )
        elif self.direction=="up":
            front_pos = this_window_frame[1]
            front_range = ( this_window_frame[0], this_window_frame[0] + this_window_frame[2] )
        elif self.direction=="down":
            front_pos = this_window_frame[1] + this_window_frame[3]
            front_range = ( this_window_frame[0], this_window_frame[0] + this_window_frame[2] )
        else:
            return None
        
        # Fit to current screen edge
        if self.screen_edge:
            if self.direction == "left":
                edge_dist = this_window_frame[0] - sx
            elif self.direction == "right":
                edge_dist = (sx + sw) - (this_window_frame[0] + ww)
            elif self.direction == "up":
                edge_dist = this_window_frame[1] - sy
            elif self.direction == "down":
                edge_dist = (sy + sh) - (this_window_frame[1] + wh)
            if edge_dist >= 0.1:
                distance = min(distance, edge_dist)

        # Fit to window edge
        if self.window_edge:

            def get_window_frames(app):
                windows = app.get_attribute_value("AXWindows")
                frames = []
                if windows:
                    for wnd in windows:
                        minimized = wnd.get_attribute_value("AXMinimized")
                        if minimized:
                            continue

                        title = wnd.get_attribute_value("AXTitle")
                        if not title:
                            continue

                        frame = wnd.get_attribute_value("AXFrame")
                        frames.append(frame)

                return frames

            # Get all window frames using parallel threads
            window_frames = []
            thread_pool = ThreadPoolExecutor(max_workers=16)
            for window_frames_from_single_app in thread_pool.map(get_window_frames, UIElement.get_running_applications()):
                window_frames += window_frames_from_single_app

            gap = 1

            for window_frame in window_frames:
                
                if self.direction=="left":
                    window_edge_pos = window_frame[0] + window_frame[2]
                    window_edge_range = (window_frame[1], window_frame[1] + window_frame[3])
                    sign = -1
                elif self.direction=="right":
                    window_edge_pos = window_frame[0]
                    window_edge_range = (window_frame[1], window_frame[1] + window_frame[3])
                    sign = 1
                elif self.direction=="up":
                    window_edge_pos = window_frame[1] + window_frame[3]
                    window_edge_range = (window_frame[0], window_frame[0] + window_frame[2])
                    sign = -1
                elif self.direction=="down":
                    window_edge_pos = window_frame[1]
                    window_edge_range = (window_frame[0], window_frame[0] + window_frame[2])
                    sign = 1
                
                if not( front_range[1] <= window_edge_range[0] or front_range[0] >= window_edge_range[1] ):
                    if (window_edge_pos - front_pos) * sign - gap >= 0.1:
                        distance = min(distance, (window_edge_pos - front_pos) * sign - gap)

        # Calculate target position
        if self.direction=="left":
            this_window_frame[0] -= distance
        elif self.direction=="right":
            this_window_frame[0] += distance
        elif self.direction=="up":
            this_window_frame[1] -= distance
        elif self.direction=="down":
            this_window_frame[1] += distance

        # Clamp to current screen bounds
        if this_window_frame[0] < sx:
            this_window_frame[0] = sx
        if this_window_frame[0] + ww > sx + sw:
            this_window_frame[0] = sx + sw - ww
        if this_window_frame[1] < sy:
            this_window_frame[1] = sy
        if this_window_frame[1] + wh > sy + sh:
            this_window_frame[1] = sy + sh - wh

        return this_window_frame[:2]

    def finished(self, result: Any):
        if self.wnd and result is not None:
            pos = result
            self.wnd.set_attribute_value("AXPosition", "point", pos)

    def __repr__(self):
        return f"MoveWindow(direction={self.direction},distance={self.distance},window_edge={self.window_edge})"


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
        elm = Keymap.get_instance().focus
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


class ClipboardChooserAction(ChooserAction):

    def __init__(self):
        super().__init__()

    def _on_chosen_common(self, clip, modifier_flags: int):

        keymap = Keymap.get_instance()

        # Set current clipboard
        keymap.clipboard_history.set_current(clip)

        # Don't paste when shift key is pressed
        if modifier_flags & MODKEY_SHIFT:
            return

        # Paste
        with keymap.get_input_context() as input_ctx:
            input_ctx.send_key("Cmd-V")

    def __repr__(self):
        return f"ClipboardChooserAction()"


class ShowClipboardHistory(ClipboardChooserAction):

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
        for clip, label in Keymap.get_instance().clipboard_history.items():
            items.append( ( "📋", label, clip) )
        return items
    
    def on_chosen(self, item, modifier_flags: int):
        self._on_chosen_common(item[2], modifier_flags)

    def __repr__(self):
        return f"ShowClipboardHistory()"


class ShowClipboardSnippets(ClipboardChooserAction):

    """
    Action class to show clipboard snippets with Chooser window.
    """

    def __init__(self, snippets):

        """
        Initializes the ShowClipboardSnippets object.
        """

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

        self._on_chosen_common(clip, modifier_flags)

    def __repr__(self):
        return f"ShowClipboardSnippets({self.snippets})"


class ShowClipboardTools(ClipboardChooserAction):

    """
    Action class to show clipboard conversion tools with Chooser window.
    """

    quote_mark = "> "

    _full_width_chars = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［＼］＾＿‘｛｜｝～０１２３４５６７８９　"
    _half_width_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}～0123456789 "

    def __init__(self, tools):

        """
        Initializes the ShowClipboardTools object.
        """

        super().__init__()
        self.tools = tools

    def list_items(self):
        return self.tools
    
    def on_chosen(self, item, modifier_flags: int):
        
        keymap = Keymap.get_instance()

        clip = keymap.clipboard_history.get_current()
        clip = item[2](clip)
        self._on_chosen_common(clip, modifier_flags)

    def __repr__(self):
        return f"ShowClipboardTools()"

    @staticmethod
    def to_plain(clip):

        """
        Convert clipboard to plain-text.
        """

        s = clip.get_string()
        clip = Clipboard()
        clip.set_string(s)
        return clip

    @staticmethod
    def quote(clip):

        """
        Convert clipboard to quoted string.
        """

        s = clip.get_string()
        lines = []
        for line in s.splitlines(keepends=True):
            lines.append(ShowClipboardTools.quote_mark + line)
        s = "".join(lines)
        clip = Clipboard()
        clip.set_string(s)
        return clip

    @staticmethod
    def unindent(clip):

        """
        Remove common white space plex in the clipboard
        """

        s = clip.get_string()

        def _get_common_white_space_prefix(s):
            lines = s.splitlines()
            for i, c in enumerate(lines[0]):
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    if (len(line) <= i) or (c not in " \t") or (line[i] != c):
                        return i
            return i+1

        indent_len = _get_common_white_space_prefix(s)

        lines = []
        for line in s.splitlines(keepends=True):
            unindented_line = line[indent_len:]
            if not unindented_line:
                if line[-1] == "\n":
                    unindented_line = "\n"
            lines.append(unindented_line)

        s = "".join(lines)
        clip = Clipboard()
        clip.set_string(s)

        return clip

    @staticmethod
    def to_half_width(clip):

        """
        Convert full width characters in clipboard to half width
        """

        s = clip.get_string()
        s = s.translate(str.maketrans(ShowClipboardTools._full_width_chars, ShowClipboardTools._half_width_chars))
        clip = Clipboard()
        clip.set_string(s)
        return clip

    @staticmethod
    def to_full_width(clip):

        """
        Convert half width characters in clipboard to full width
        """

        s = clip.get_string()
        s = s.translate(str.maketrans(ShowClipboardTools._half_width_chars, ShowClipboardTools._full_width_chars))
        clip = Clipboard()
        clip.set_string(s)
        return clip


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
        keymap = Keymap.get_instance()
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
        keymap = Keymap.get_instance()
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
        keymap = Keymap.get_instance()
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
        keymap = Keymap.get_instance()
        keymap.replay_buffer.playback()

    def __repr__(self):
        return f"PlaybackRecordedKeys()"

