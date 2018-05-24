from time import sleep
from random import randint
from selenium import webdriver
from pyvirtualdisplay import Display
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append('/home/paul/Paulthon')
from utility.general import tprint, merge_dfs_horizontally, append_dfs_vertically, to_pickle_and_CSV
from decorators import profile

SLEEP_TOGGLE = True
GREEKS_PAGE_LOAD_TIMEOUT = 60


class Chrome_Crawler():
        def __init__(self):
            pass

        # Open headless chromedriver
        def start_driver(self, display=True):
            print('starting Chrome driver...')
            if display == False:
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
            
            self.driver = webdriver.Chrome("/home/paul/Paulthon/crawler/chromedriver235/chromedriver")
            if SLEEP_TOGGLE:
                sleep(4)

        # Close chromedriver
        def close_driver(self):
            print('closing Chrome driver...')
            #self.display.stop()
            self.driver.quit()
            print('closed!')

        # Tell the browser to get a page
        def get_page(self, url):
                print('getting page...', url)
                self.driver.get(url)
                if SLEEP_TOGGLE:
                    print('The sleep toggle is working')
                    sleep(randint(4,5))

class Barchart_Crawler(Chrome_Crawler):
        def __init__(self, symbol):
            self.symbol = symbol
            self.base_url = "https://www.barchart.com/stocks/quotes/{}".format(symbol.lower())
            self.base_reidx_cols = ['Bid', 'Midpoint', 'Ask']
            self.greeks_reidx_cols = ['IV', 'Delta']
            
            # Caches
            self.cache = {}
            self.greeks_cache = {}
            self.calls_and_puts_cache = {}

        def expiry_url(self, expiry):
            return self.base_url + "/options?expiration={}".format(expiry)
        
        def greeks_url(self, expiry):
            return self.base_url + "/volatility-greeks?expiration={}".format(expiry)

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

        def get_base_markup(self, expiry, display=False):
            try:
                print('Trying base cache')
                return self.cache[self.symbol]
            except:
                self.start_driver(display=display)

                url_to_crawl = self.expiry_url(expiry)
                
                self.get_page(url_to_crawl)
                table_elements = self.driver.find_elements_by_class_name('barchart-content-block')
                markup = [elem.get_attribute('innerHTML') for elem in table_elements]
                
                self.cache[self.symbol] = markup

                self.close_driver
                return markup
        
        def get_greeks_markup(self, expiry, display=False):
            try:
                print('Trying greeks cache')
                #print(self.greeks_cache)
                return self.greeks_cache[self.symbol]
            except:
                self.start_driver(display=display)
                self.driver.set_page_load_timeout(GREEKS_PAGE_LOAD_TIMEOUT)

                url_to_crawl = self.greeks_url(expiry)
                
                self.get_page(url_to_crawl)
                table_elements = self.driver.find_elements_by_class_name('barchart-content-block')
                markup = [elem.get_attribute('innerHTML') for elem in table_elements]
                print('There are {} tables'.format(len(markup)))     
                
                self.greeks_cache[self.symbol] = markup
                
                self.close_driver
                return markup


        def get_call_put_INDEX(option_type):
            if option_type == 'Call':
                return 0
            elif option_type == 'Put':
                return 1
            else:
                raise ValueError("'Call' and 'Put' are the only valid option_type inputs.")
        
        def create_base_df(self, expiry, option_type='Call', display=False):
            INDEX = Barchart_Crawler.get_call_put_INDEX(option_type)
            markup = self.get_base_markup(expiry, display=display)
            soup = BeautifulSoup(markup[INDEX], 'lxml')
            df = pd.read_html(str(soup.find_all('table')))[0].set_index('Strike').loc[:, self.base_reidx_cols]
            return df
        
        def create_greeks_df(self, expiry, option_type='Call', display=False):
            INDEX = Barchart_Crawler.get_call_put_INDEX(option_type)
            markup = self.get_greeks_markup(expiry, display=display)
            soup = BeautifulSoup(markup[INDEX], 'lxml')
            df = pd.read_html(str(soup.find_all('table')))[0].set_index('Strike').loc[:, self.greeks_reidx_cols]
            
            # Drop the bottom row
            df = df[:-1]

            # Transform 'Strike' values to floats
            index = df.index.tolist()
            index = [float(i) for i in index]
            df.index = index
            
            # Transform 'Delta' values to floats
            deltas = df['Delta'].tolist()
            deltas = [float(i) for i in deltas]
            df['Delta'] = deltas

            # Transform 'IV' values to floats
            vols = df['IV'].tolist()
            vols = [float(i[:-1]) for i in vols]
            df['IV'] = vols
            
            #cols = list(df)
            #cols_cleaned = [col.strip() for col in cols]
            #df.columns = cols_cleaned
            return df
        
        def create_combined_df(self, expiry, option_type='Call'):
            base_df = self.create_base_df(expiry, option_type)
            print(base_df.to_string())
            to_pickle_and_CSV(base_df, 'base')
            
            greeks_df = self.create_greeks_df(expiry, option_type)
            print(greeks_df.to_string())
            to_pickle_and_CSV(greeks_df, 'greeks')
            
            combined_df = merge_dfs_horizontally([base_df, greeks_df])
            print(combined_df.to_string())
            to_pickle_and_CSV(combined_df, 'combined')
            return combined_df
        
        def create_calls_and_puts_df(self, expiry):
            try:    
                print('Trying calls and puts cache')
                print(self.calls_and_puts_cache)
                return self.calls_and_puts_cache[self.symbol]
            
            except:
                calls_df = self.create_combined_df(expiry, 'Call')
                puts_df = self.create_combined_df(expiry, 'Put')
                
                to_pickle_and_CSV(calls_df, 'calls')
                to_pickle_and_CSV(puts_df, 'puts')
                
                calls_df = calls_df['Delta'] > .45
                puts_df = puts_df['Delta'] < -.55

                calls_and_puts_df = append_dfs_vertically([calls_df, puts_df])
                self.calls_and_puts_cache[self.symbol] = calls_and_puts_df
                return calls_and_puts_df
        
        def at_the_money_vol(self, expiry):
            calls_and_puts_df = self.create_calls_and_puts_df(expiry)
            #return calls_and_puts_df.iloc[[calls_and_puts_df.index.get_loc(1.00, method='nearest')], :]
            atm_df = calls_and_puts_df[calls_and_puts_df['Delta'].abs() - .5 < .1]
            print(vol_df)
            vol = atm_df['IV'].mean()
            return vol
        
        def put_vol(self, expiry):
            calls_and_puts_df = self.create_calls_and_puts_df(expiry)
            #return calls_and_puts_df.iloc[[calls_and_puts_df.index.get_loc(1.00, method='nearest')], :]
            put_df = calls_and_puts_df[(calls_and_puts_df['Delta'] - .25).abs() < .075]
            print(put_df)
            vol = put_df['IV'].mean()
            return vol


@profile        
def run_barchart_crawler():             
    if __name__ == '__main__':
        # Run spider
        stock = Barchart_Crawler('PEP')
        df = stock.create_greeks_df('2018-07-20', display=True)
        print(df)
        atm_vol = stock.at_the_money_vol('2018-07-20')
        put_vol = stock.put_vol('2018-07-20')
        print('ATM Vol: {:.2f}, Put Vol: {:.2f}'.format(atm_vol, put_vol))
        #greeks = spy.create_call_greeks_df('2018-07-20')
        #print(greeks)
        #call_data = spy.create_base_call_df('2018-07-20')
        #put_data = spy.create_base_put_df('2018-07-20')
        #print(call_data)
        #print(put_data)
        
        """
        expiries = Barchart_Crawler('SPY').parse_expiries()

        # Print the expiries to the console
        for expiry in expiries:
            print(expiry)
        """

run_barchart_crawler()
