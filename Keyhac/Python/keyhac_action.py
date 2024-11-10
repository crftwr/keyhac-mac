import traceback
from concurrent.futures import ThreadPoolExecutor
import keyhac_console

logger = keyhac_console.getLogger("Action")

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
            print()
            logger.error(f"Threaded action failed:\n{traceback.format_exc()}")

    def starting(self):
        pass

    def run(self):
        pass

    def finished(self, result):
        pass
