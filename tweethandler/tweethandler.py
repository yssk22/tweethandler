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
            self._api.update_status(self.format(record))
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
