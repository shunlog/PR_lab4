#!/usr/bin/env python3

import requests

host = 'http://127.0.0.1:8082'

for path in ['/', '/about', '/products', '/product/1']:
    url = host + path
    print("Requesting", url, "...")
    r = requests.get(url)
    print(r.text)
    print()
