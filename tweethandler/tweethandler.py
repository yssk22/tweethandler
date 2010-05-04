#
# TweetHandler
#
# author: yssk22
#
from tweepy import OAuthHandler, API
from tweepy.error import TweepError
import logging

_EREASON_OVERCHARS = 'Status is over 140 characters.'
_EREASON_DUPLICATE = 'Status is a duplicate.'

def _prop(func):
    return property(**func())

class TweetHandler(logging.Handler):
    """
    A handler class which writes logging records to twitter.com
    """

    def __init__(self,
                 ckey, csecret, akey, asecret,
                 dm_threshold = logging.ERROR,
                 dm_to = [],
                 compact_log = True,
                 ignore_duplication = True,
                 ignore_overchars = True,
                 max_retries = 5):
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
        self._ignore_duplication = ignore_duplication
        self._ignore_overchars = ignore_overchars

    def emit(self, record):
        """
        Emit a record
        """
        try:
            if self._compact_log:
                self._compact_record(record)
            if record.levelno >= self._dm_threshold:
                self._send_dm(record)
            self._send_status(record)
        except TweepError, e:
            if e.reason == _EREASON_OVERCHARS:
                if not self._ignore_overchars:
                    raise e
            elif e.reason == _EREASON_DUPLICATE:
                if not self._ignore_duplication:
                    raise e
            else:
                raise e

    def _compact_record(self, record):
        formatted = self.format(record)
        if len(formatted) <= 140:
            # nothing to do
            return 
        compact_len = len(formatted) - 140
        record.msg = record.msg[:-compact_len]

    # TODO asynchronous logging.
    def _send_status(self, record):
        self._api.update_status(self.format(record))

    def _send_dm(self, record):
        msg = self.format(record)
        if type(self._dm_to) is list:
            for d in self._dm_to:
                self._api.send_direct_message(d, text = msg)
        else:
            self._api.send_direct_message(self._dm_to, text = msg)
