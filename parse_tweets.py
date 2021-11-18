from bs4 import BeautifulSoup
from lxml import html
import requests
from selenium import webdriver

import random, time, os

from utils import *
from config import *

"Time to sleep"
MIN_RAND = 8
MAX_RAND = 14
SCROLL_PAUSE_TIME = 8


class Twitter:
    def __init__(self, url):
        path_chrome = './chromedriver'
        self.driver = webdriver.Chrome(path_chrome)

        print('Go to {}'.format(url))
        self.driver.get(url)
        time_sleep = random.randint(MIN_RAND, MAX_RAND)
        print('Waiting for %d seconds' %time_sleep)
        time.sleep(time_sleep)
        
        #Tweets counter
        self.cnt = 0

    def get_tweets_onpage(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")    
        tweets_section = soup.find('section', {'class': 'css-1dbjc4n'})
        if tweets_section is None:
            print('Error with getting tweets section')
            return False
        
        tweet_list = tweets_section.findChildren('article')
        if len(tweet_list) == 0:
            print('Error with getting tweets')
            return False
        
        for i, tweet in enumerate(tweet_list):
            print('{}/{} tweet'.format(i+1, len(tweet_list)))
            text_block_tweet = tweet.find('div', {'class': 'css-901oao r-1fmj7o5 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0'})
            if text_block_tweet:
                text_tweet = text_block_tweet.get_text()

                self.cnt += 1
                if not text_tofile(twitter_data_dir, self.cnt, text_tweet):
                    break
            else:
                continue
        print('\n')
            
        return True

    def parse(self):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        page = 1
        while True:
            print('Parsing page {}'.format(page))
            if not self.get_tweets_onpage():
                return
            
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            print('Waiting for %d seconds' %SCROLL_PAUSE_TIME)
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            page += 1
        