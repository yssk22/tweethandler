import unittest
import logging
import os
import sys
import time
from tweepy import OAuthHandler, API
from tweepy.error import TweepError

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                "../tweethandler"))
from tweethandler import TweetHandler

LOG_FORMAT = "%(message)s"

# auth info from environment variables
ckey = os.environ['TH_CONSUMER_KEY']
csecret = os.environ['TH_CONSUMER_SECRET']
akey = os.environ['TH_ACCESS_KEY']
asecret = os.environ['TH_ACCESS_TOKEN']

class TestTweetHandler(unittest.TestCase):
    def setUp(self):
        # storage setup
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(akey, asecret)
        self.storage = API(auth)

        # logger setup
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter(LOG_FORMAT)
        self.logger.setLevel(logging.DEBUG)
        self.setUpHandler()

    def setUpHandler(self, 
                     compact_log = True,
                     ignore_duplication = True,
                     ignore_overchars = True,
                     max_retries = 5):
        self.handler = TweetHandler(ckey, csecret, akey, asecret,
                                    compact_log = compact_log,
                                    ignore_duplication = ignore_duplication,
                                    ignore_overchars = ignore_overchars,
                                    max_retries = max_retries)
        self.handler.setLevel(logging.DEBUG)
        self.handler.setFormatter(self.formatter)
        for h in self.logger.handlers:
            self.logger.removeHandler(h)
        self.logger.addHandler(self.handler)
    
    def tearDown(self):
        pass

    def testEmit(self):
        log = self.mklog('foo')
        self.logger.debug(log)
        self.assertEqual(log, self.getLastLog()[0])
        
    def testEmitDuplicate(self):
        log1 = self.mklog('foo')
        self.logger.debug(log1)   # starting point
        self.assertEqual(log1, self.getLastLog()[0])

        log2 = self.mklog('bar')
        self.logger.debug(log2) # emit without timestamp
        self.assertEqual(log2, self.getLastLog()[0])

        self.logger.debug(log2) # this will be discarded because of duplication.
        last_log = self.getLastLog()
        self.assertEqual(log1, last_log[1]) # assert not log2
        self.assertEqual(log2, last_log[0])

        self.setUpHandler(ignore_duplication = False)
        self.assertRaises(TweepError, 
                          lambda: self.logger.debug(log2))

    def testEmitOverChars(self):
        max_msg_len = 140 - 12

        # starting point
        log1 = self.mklog('foo')
        self.logger.debug(log1)   
        self.assertEqual(log1, self.getLastLog()[0])

        # log msg limitation
        log2 = self.mklog('a' * max_msg_len)
        self.logger.debug(log2)
        self.assertEqual(log2, self.getLastLog()[0])
        
        # over 140 chars log
        log3 = self.mklog('a' * (max_msg_len + 1))
        self.logger.debug(log3)

        # log3 should be compacted and emitted
        last_log = self.getLastLog()
        self.assertNotEqual(log3, last_log[0])
        self.assertEqual(log2, last_log[1])
        self.assertEqual(log1, last_log[2])

        # log3 should not be compacted and execption raised
        self.setUpHandler(ignore_overchars = False,
                          compact_log = False)
        self.assertRaises(TweepError, 
                          lambda: self.logger.debug(log3))


    def getLastLog(self, count=20):
        me = self.storage.me()
        tl = self.storage.user_timeline(me.id, count=count)
        return [st.text for st in tl]
    
    def mklog(self, str):
        ''' this returns "timestamp: str", 
        where 'timestamp' is int(time.time()), 10 chars.
        '''
        return "%s: %s" % (int(time.time()), str)

if __name__ == '__main__':
    unittest.main()
