from bs4 import BeautifulSoup
import requests

source = requests.get('http://coreyms.com').text

soup = BeautifulSoup(source, 'lxml')
#print(soup.prettify())


article = soup.find('article')
#print(article.prettify())

headline = article.h2.a.text
summary = article.find('div', class_='entry-content').p.text
print(headline)
print(summary)
