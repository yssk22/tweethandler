#
# TweetHandler
#
# author: yssk22
#
from tweepy import OAuthHandler, API
from tweepy.error import TweepError
import logging


class TweetHandler(logging.Handler):
    """
    A handler class which writes logging records to twitter.com
    """

    def __init__(self,
                 ckey, csecret, 
                 akey, asecret):
        """
        Use OAuth access key and secret to initialize twitter client.
        """
        logging.Handler.__init__(self)
        self._auth = OAuthHandler(ckey, csecret)
        self._auth.set_access_token(akey, asecret)
        self._api = API(self._auth)

    def emit(self, record):
        """
        Emit a record
        """
        try:
            self._api.update_status(self.format(record))
        except TweepError, e:
            print e
