#!/usr/bin/env python3
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

host = 'http://127.0.0.1:8082'
save_dir = './downloaded/'
products_save_dir = save_dir + 'products/'

Path(save_dir).mkdir(parents=True, exist_ok=True)
Path(products_save_dir).mkdir(parents=True, exist_ok=True)

# scrap all regular pages
for path in ['/about', '/products', '/contacts']:
    url = host + path
    print("Requesting", url, "...")
    r = requests.get(url)

    fn = save_dir + path[1:] + '.html'
    with open(fn, 'w') as fp:
        fp.write(r.text)


# crawl all product listings
url = host + '/products'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')
product_pages = [a['href'] for a in soup.find_all('a')]
print("Found product pages:", product_pages)

for path in product_pages:
    url = host + path
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    data = {}
    for row in soup.find_all('tr'):
        name, val = [td.text for td in row.find_all('td')]
        data[name] = val

    i = int(path.split('/')[-1])
    save_path = products_save_dir + f'/{i}.json'

    with open(save_path, 'w') as fp:
        fp.write(json.dumps(data))
