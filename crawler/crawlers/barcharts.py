from time import sleep
from random import randint
from selenium import webdriver
from pyvirtualdisplay import Display

class Barchart_Expiries():
        def __init__(self):
                self.url_to_crawl = "https://www.barchart.com/stocks/quotes/aapl/options"
                self.all_items = []

        # Open headless chromedriver
        def start_driver(self):
                print('starting driver...')
                #self.display = Display(visible=0, size=(800, 600))
                #self.display.start()
                self.driver = webdriver.Chrome("/home/paul/Paulthon/crawler/chromedriver235/chromedriver")
                #self.driver.get('https://www.barchart.com')
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
                #for div in self.driver.find_elements_by_xpath('//ul[@class="menu-items row"]//li'):
                #for div in self.driver.find_elements_by_xpath('.//*[@class="bc-dropdown filter in-the-money"]'):
                expiries_string = self.driver.find_elements_by_xpath('.//select[@class="ng-pristine ng-untouched ng-valid"]')[0].text
                print('----------------------')
                print(expiries_string)
                expiries = expiries_string.strip().split()
                #with open('expiries.txt', 'w') as f:
                #    f.write(expiries_string)
                return expiries

        def parse(self):
                self.start_driver()
                self.get_page(self.url_to_crawl)
                self.expiries = self.get_expiries()
                self.close_driver()

                if self.expiries:
                        return self.expiries
                else:
                        return False

                
# Run spider
expiries_list = Barchart_Expiries().parse()

# Print the expiries
for expiry in expiries_list:
    print(expiry)
