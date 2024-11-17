"""
A module containing key action classes
"""

import traceback
from concurrent.futures import ThreadPoolExecutor
import keyhac_console

logger = keyhac_console.getLogger("Action")

class ThreadedAction:

    """
    Base class for threaded actions.

    To define your own threaded action class, deribe the ThreadedAction and implement starting, run, and finished methods.
    run() is executed in a thread, and is for time consuming tasks.
    starting() and finished() are for light-weight tasks for before and after the time consuming task.
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
        pass

    def run(self):
        pass

    def finished(self, result):
        pass
