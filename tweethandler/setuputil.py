import tweethandler

from tweepy import OAuthHandler

def run():
    print 'Input your application info.'
    consumer_key = raw_input('Consumer Key: ')
    consumer_secret = raw_input('Consumer Secret: ')

    auth = OAuthHandler(consumer_key,
                        consumer_secret)
    print "Visit the following url and allow TweetHandler to access."
    print '>>> %s' % auth.get_authorization_url()
    print ''
    vcode = raw_input('Enter verification code: ')
    token = auth.get_access_token(vcode)
    print 'OK. You can setup TweetHander with following code.'
    print """ ----
from tweethandler import TweetHandler
import logging
th = TweetHandler('%s',
                  '%s',
                  '%s',
                  '%s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
th.setLevel(logging.DEBUG)
logger.addHandler(th)
logger.info('Your log message')
""" % (consumer_key, consumer_secret,
       token.key, token.secret)
