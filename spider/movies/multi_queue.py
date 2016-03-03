import Queue
import multiprocessing
from multiprocessing import Process


class MultitaskQueue:
    def __init__(self, func):
        self.MAX_PROC = 8

        self.queue = multiprocessing.Queue()
        self.pool = []
        self.func = self.func_wrapper(func)
        self.process_cnt = 0

    def empty(self):
        return self.queue.empty()

    def count(self):
        return len(self.queue)

    def add(self, *args, **kwargs):
        self.queue.put((args, kwargs), block=True)
        if self.process_cnt < self.MAX_PROC:
            try:
                job = self.queue.get(block=True, timeout=1)
                process = Process(group=None, target=self.func, args=job[0], kwargs=job[1])
                self.process_cnt += 1
                process.start()
            except Queue.Empty, Queue.Full:
                pass

    def func_wrapper(self, func):
        class WrapClass:
            def __init__(self, _self, _func):
                self.multi = _self
                self.func = _func

            def __call__(self, *args, **kwargs):
                if len(args) > 0 or len(kwargs) > 0:
                    self.func(*args, **kwargs)
                while True:
                    try:
                        job = self.multi.queue.get(block=True, timeout=1)
                        self.func(*job[0], **job[1])
                    except Queue.Empty:
                        self.multi.process_cnt -= 1
                        return
                    except Queue.Full:
                        pass

        return WrapClass(self, func)
