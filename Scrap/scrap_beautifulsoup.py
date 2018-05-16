import bs4 as bs
import urllib.request

sauce = urllib.request.urlopen('https://pythonprogramming.net/parsememcparseface/').read()

soup = bs.BeautifulSoup(sauce, 'lxml') # lxml is a parser
print(soup.title.string)

for paragraph in soup.find_all('p'):
    print(paragraph.string)

for url in soup.find_all('a')

