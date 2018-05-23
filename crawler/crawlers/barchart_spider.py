from time import sleep
from random import randint
from selenium import webdriver
from pyvirtualdisplay import Display
import pandas as pd
import requests
from bs4 import BeautifulSoup

import sys
sys.path.append('/home/paul/Paulthon')
from utility.general import tprint

class Chrome_Crawler():
        def __init__(self):
            pass

        # Open headless chromedriver
        def start_driver(self, display=True):
            print('starting driver...')
            if display == False:
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            
            self.driver = webdriver.Chrome("/home/paul/Paulthon/crawler/chromedriver235/chromedriver")
            #self.driver.set_page_load_timeout(30)
            sleep(4)

        # Close chromedriver
        def close_driver(self):
            print('closing driver...')
            #self.display.stop()
            self.driver.quit()
            print('closed!')

        # Tell the browser to get a page
        def get_page(self, url):
                print('getting page...')
                self.driver.get(url)
                sleep(randint(2,3))

class Barchart_Crawler(Chrome_Crawler):
        def __init__(self, symbol):
            self.symbol = symbol
            self.base_url = "https://www.barchart.com/stocks/quotes/{}/options".format(symbol.lower())
            self.cache = {}
            self.reidx_cols = ['Midpoint', 'IV']

        def expiry_url(self, expiry):
            return self.base_url + "?expiration={}".format(expiry)

        def parse_expiries(self):
            self.start_driver()
            
            url_to_crawl = self.base_url
            self.get_page(url_to_crawl)
            expiries_string = self.driver.find_elements_by_xpath('.//select[@class="ng-pristine ng-untouched ng-valid"]')[0].text
            expiries = expiries_string.strip().split()
            
            self.close_driver()

            if expiries:
                    return expiries
            else:
                    return False

        def get_base_call_put_markup(self, expiry):
            try:
                print('Trying cache')
                return self.cache[self.symbol]
            except:
                self.start_driver(display=False)

                url_to_crawl = self.expiry_url(expiry)
                
                self.get_page(url_to_crawl)
                table_elements = self.driver.find_elements_by_class_name('barchart-content-block')
                markup = [elem.get_attribute('innerHTML') for elem in table_elements]
                
                self.cache[self.symbol] = markup
                return markup

        def create_base_call_df(self, expiry):
            markup = self.get_base_call_put_markup(expiry)
            soup = BeautifulSoup(markup[0], 'lxml')
            return pd.read_html(str(soup.find_all('table')))[0].set_index('Strike').loc[:, self.reidx_cols]
        
        def create_base_put_df(self, expiry):
            markup = self.get_base_call_put_markup(expiry)
            soup = BeautifulSoup(markup[1], 'lxml')
            return pd.read_html(str(soup.find_all('table')))[0].set_index('Strike').loc[:, self.reidx_cols]
                
if __name__ == '__main__':
    # Run spider
    spy = Barchart_Crawler('SPY')
    call_data = spy.create_base_call_df('2018-07-20')
    put_data = spy.create_base_put_df('2018-07-20')
    print(call_data)
    print(put_data)
    
    
    """
    expiries = Barchart_Crawler('SPY').parse_expiries()

    # Print the expiries to the console
    for expiry in expiries:
        print(expiry)
    """
