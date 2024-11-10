import traceback
from concurrent.futures import ThreadPoolExecutor

from keyhac_const import CONSOLE_STYLE_DEFAULT, CONSOLE_STYLE_ERROR

class ThreadedAction:

    thread_pool = ThreadPoolExecutor(max_workers=16)

    def __init__(self):
        pass

    def __call__(self):
        self.starting()
        future = ThreadedAction.thread_pool.submit(self.run)
        future.add_done_callback(self._done_callback)

    def _done_callback(self, future):
        try:
            self.finished(future.result())
        except Exception as e:
            print(CONSOLE_STYLE_ERROR)
            print("ERROR: running custom focus condition function failed:")
            traceback.print_exc()
            print(CONSOLE_STYLE_DEFAULT)

    def starting(self):
        pass

    def run(self):
        pass

    def finished(self, result):
        pass
