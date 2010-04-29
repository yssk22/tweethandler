from setuptools import setup, find_packages

setup(name='tweethandler',
      version='0.1',
      description='logging handler for twitter',
      license='MIT',
      author='Yohei Sasaki',
      url='http://github.com/yssk22/tweethandler',
      install_requires = [
        'setuptools>=0.6b1',
        'tweepy>=1.6'
        ],

      packages = find_packages(),
      keywords = 'twitter logging',
      zip_safe = False,
      entry_points="""
[console_scripts]
tweethandler_setup=tweethandler.setuputil:run
"""
)
