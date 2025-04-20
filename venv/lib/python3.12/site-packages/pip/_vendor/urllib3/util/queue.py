import collections

from ..packages import six
from ..packages.six.moves import queue

if six.PY2:
    
    import Queue as _unused_module_Queue  


class LifoQueue(queue.Queue):
    def _init(self, _):
        self.queue = collections.deque()

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()
