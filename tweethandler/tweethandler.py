#
# TweetHandler
#
# author: yssk22
#
import logging
import Queue
import threading

from tweepy import OAuthHandler, API
from tweepy.error import TweepError


class TweetHandler(logging.Handler):
    """
    A handler class which writes logging records to twitter.com
    """

    def __init__(self,
                 ckey, csecret, akey, asecret,
                 dm_threshold = logging.ERROR,
                 dm_to = [],
                 compact_log = True,
                 ignore_twerror = True,
                 max_retries = 5, 
                 async = False):
        """
        Use OAuth access key and secret to initialize twitter client.
        """
        logging.Handler.__init__(self)
        self._auth = OAuthHandler(ckey, csecret)
        self._auth.set_access_token(akey, asecret)
        self._api = API(self._auth, retry_count = max_retries)

        # options
        self._dm_threshold = dm_threshold
        self._dm_to = dm_to
        self._compact_log = compact_log
        self._ignore_twerror = ignore_twerror
        self._pool = None
        if async:
            self._pool = _ExecPool()
            self._pool.start()

    def close(self):
        if self._pool:
            self._pool.stop()

    def emit(self, record):
        """
        Emit a record
        """
        try:
            if self._compact_log:
                self._compact_record(record)
            if record.levelno >= self._dm_threshold:
                self._send_dm(record)
            self._api_call(self._api.update_status,
                           self.format(record))
        except TweepError, e:
            if not self._ignore_twerror:
                raise e

    def _compact_record(self, record):
        formatted = self.format(record)
        if len(formatted) <= 140:
            # nothing to do
            return 
        compact_len = len(formatted) - 140
        record.msg = record.msg[:-compact_len]

    def _send_dm(self, record):
        msg = self.format(record)
        if type(self._dm_to) is list:
            for d in self._dm_to:
                self._api_call(self._api.send_direct_message,
                               d, text = msg)
        else:
            self._api_call(self._api.send_direct_message,
                           self._dm_to, text = msg)

    def _api_call(self, func, *args, **kwargs):
        if self._pool:
            self._pool.dispatch(func, *args, **kwargs)
        else:
            func(*args, **kwargs)


_StopWorker = object()
class _ExecPool:
    def __init__(self, numthreads = 10):
        self._numthreads = numthreads
        self._threads = []
        self._queue = Queue.Queue()
        self._started = False

    def start(self):
        if self._started:
            return # already started
        self._started = True
    
        for i in range(self._numthreads):
            name = "_ExecPool-%s-%s" % (id(self), i)
            newth = threading.Thread(target = self._worker,
                                     name = name)
            self._threads.append(newth)
            newth.start()

    def dispatch(self, func, *args, **kwargs):
        o = (func, args, kwargs)
        self._queue.put(o)
        if not self._started:
            self.start()

    def stop(self):
        if not self._started:
            return

        for i in range(self._numthreads):
            self._queue.put(_StopWorker)
        for th in self._threads:
            th.join()

        self._threads = []
        self._started = False

    def _worker(self):
        current = threading.currentThread()
        o = self._queue.get()
        while o is not _StopWorker:
            func, args, kwargs = o
            func(*args, **kwargs)
            o = self._queue.get()
        # ends of threads
