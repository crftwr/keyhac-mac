from concurrent.futures import ThreadPoolExecutor

class ThreadedAction:

    thread_pool = ThreadPoolExecutor(max_workers=16)

    def __init__(self):
        pass

    def __call__(self):
        self.starting()
        future = ThreadedAction.thread_pool.submit(self.run)
        future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        self.finished()

    def starting(self):
        pass

    def run(self):
        pass

    def finished(self):
        pass
