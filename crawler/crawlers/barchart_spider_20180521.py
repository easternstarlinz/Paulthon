from time import sleep
from random import randint
from selenium import webdriver
from pyvirtualdisplay import Display

class Barchart_Expiries():
        def __init__(self, symbol):
                self.url_to_crawl = "https://www.barchart.com/stocks/quotes/{}/options".format(symbol.lower())

        # Open headless chromedriver
        def start_driver(self):
                print('starting driver...')
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
                self.driver = webdriver.Chrome("/Users/paulwainer/Paulthon/crawler/chromedriver235/chromedriver")
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

        def get_expiries(self):
                print('grabbing list of items...')
                expiries_string = self.driver.find_elements_by_xpath('.//select[@class="ng-pristine ng-untouched ng-valid"]')[0].text
                expiries = expiries_string.strip().split()
                return expiries

        def parse_expiries(self):
                self.start_driver()
                self.get_page(self.url_to_crawl)
                self.expiries = self.get_expiries()
                self.close_driver()

                if self.expiries:
                        return self.expiries
                else:
                        return False

                
if __name__ = '__main__':
    # Run spider
    expiries = Barchart_Expiries('SPY').parse_expiries()

    # Print the expiries to the console
    for expiry in expiries:
        print(expiry)
